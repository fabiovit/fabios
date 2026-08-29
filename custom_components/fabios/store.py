from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from calendar import monthrange
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DEFAULT_CATEGORY, DEFAULT_CURRENCY, DEFAULT_GROUP_NAME, STORAGE_KEY, STORAGE_VERSION
from .models import money, new_expense, new_group, new_person, new_recurring, new_settlement

CADENCE_MONTHS = {"monthly": 1, "bimonthly": 2, "quarterly": 3, "four_months": 4, "semiannual": 6, "yearly": 12}


def add_months(date_str: str, months: int) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    day = min(d.day, monthrange(y, m)[1])
    return f"{y:04d}-{m:02d}-{day:02d}"


class FabiosStore:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.data: dict[str, Any] = {}

    async def async_load(self) -> None:
        self.data = self._migrate(await self._store.async_load() or {})

    def _migrate(self, data: dict[str, Any]) -> dict[str, Any]:
        data.setdefault("settings", {"currency": DEFAULT_CURRENCY})
        data["settings"].setdefault("currency", DEFAULT_CURRENCY)
        for key in ("people", "expenses", "settlements", "groups", "recurring", "carryovers"):
            data.setdefault(key, [])
        data.setdefault("categories", ["Casa", "Spesa", "Ristoranti", "Animali", "Auto", "Bollette", "Abbonamenti", "Salute", "Tempo libero", "Viaggi", "Altro"])
        if not data["groups"]:
            data["groups"].append(new_group(DEFAULT_GROUP_NAME, [p["id"] for p in data["people"]]))
        gid = data["groups"][0]["id"]
        for e in data["expenses"]:
            e.setdefault("group_id", gid)
            e.setdefault("category", DEFAULT_CATEGORY)
        for s in data["settlements"]:
            s.setdefault("group_id", gid)
        for r in data["recurring"]:
            r.setdefault("start_date", r.get("next_date"))
        return data

    async def async_save(self) -> None:
        await self._store.async_save(self.data)

    def person(self, person_id: str):
        return next((p for p in self.data["people"] if p["id"] == person_id), None)

    def group(self, group_id: str):
        return next((g for g in self.data["groups"] if g["id"] == group_id), None)

    def active_group_id(self) -> str | None:
        groups = [g for g in self.data["groups"] if not g.get("archived", False)]
        return groups[0]["id"] if groups else None

    def snapshot(self, group_id: str | None = None, month: str | None = None) -> dict[str, Any]:
        gid = group_id or self.active_group_id()
        selected_month = month or date.today().strftime("%Y-%m")
        return {**self.data, "active_group_id": gid, "selected_month": selected_month, "summary": self.summary(gid, selected_month), "balances": self.balances(gid, selected_month), "stats": self.stats(gid)}

    async def add_person(self, name: str):
        name = name.strip()
        if not name:
            raise ValueError("Name is required")
        if any(p["name"].casefold() == name.casefold() for p in self.data["people"]):
            raise ValueError("A person with this name already exists")
        p = new_person(name)
        self.data["people"].append(p)
        if len(self.data["groups"]) == 1 and self.data["groups"][0]["name"] == DEFAULT_GROUP_NAME:
            self.data["groups"][0]["members"].append(p["id"])
        await self.async_save()
        return p

    async def add_group(self, name: str, members: list[str]):
        if not name.strip() or len(members) < 2:
            raise ValueError("A group needs a name and at least two people")
        if any(not self.person(pid) for pid in members):
            raise ValueError("Unknown member")
        g = new_group(name, members)
        self.data["groups"].append(g)
        await self.async_save()
        return g

    async def archive_group(self, group_id: str, archived: bool):
        g = self.group(group_id)
        if not g:
            raise ValueError("Group not found")
        g["archived"] = archived
        await self.async_save()

    def _validate_shares(self, amount: float, paid_by: str, shares: dict[str, float], group_id: str) -> None:
        g = self.group(group_id)
        if not g or paid_by not in g["members"] or any(pid not in g["members"] for pid in shares):
            raise ValueError("People must belong to the selected group")
        if amount <= 0 or not shares:
            raise ValueError("Invalid amount or split")
        if money(sum(float(v) for v in shares.values())) != money(amount):
            raise ValueError("Shares must add up to the expense amount")

    async def add_expense(self, description, amount, paid_by, shares, expense_date, group_id, category, notes="", installment_current=None, installment_total=None):
        self._validate_shares(amount, paid_by, shares, group_id)
        e = new_expense(description, amount, paid_by, shares, expense_date, group_id, category, notes, installment_current, installment_total)
        self.data["expenses"].append(e)
        await self.async_save()
        return e

    async def update_expense(self, expense_id, description, amount, paid_by, shares, expense_date, group_id, category, notes="", installment_current=None, installment_total=None):
        self._validate_shares(amount, paid_by, shares, group_id)
        expense = next((e for e in self.data["expenses"] if e["id"] == expense_id), None)
        if not expense:
            raise ValueError("Spesa non trovata")
        updated = new_expense(description, amount, paid_by, shares, expense_date, group_id, category, notes, installment_current, installment_total)
        updated["id"] = expense_id
        updated["created_at"] = expense.get("created_at", updated["created_at"])
        expense.clear()
        expense.update(updated)
        await self.async_save()
        return expense

    async def delete_expense(self, expense_id: str):
        self.data["expenses"] = [e for e in self.data["expenses"] if e["id"] != expense_id]
        await self.async_save()

    async def delete_expenses(self, expense_ids):
        ids = set(expense_ids)
        before = len(self.data["expenses"])
        self.data["expenses"] = [e for e in self.data["expenses"] if e["id"] not in ids]
        deleted = before - len(self.data["expenses"])
        if deleted:
            await self.async_save()
        return deleted

    async def add_settlement(self, from_person, to_person, amount, settlement_date, group_id, notes=""):
        g = self.group(group_id)
        if not g or from_person not in g["members"] or to_person not in g["members"] or from_person == to_person or amount <= 0:
            raise ValueError("Invalid settlement")
        s = new_settlement(from_person, to_person, amount, settlement_date, group_id, notes)
        self.data["settlements"].append(s)
        await self.async_save()
        return s


    async def settle_month_balance(self, group_id: str, month: str):
        balances = self.balances(group_id, month)
        if not balances:
            return {"created": 0, "month": month, "balances": []}
        year, mon = (int(x) for x in month.split("-", 1))
        settlement_date = f"{year:04d}-{mon:02d}-{monthrange(year, mon)[1]:02d}"
        created = []
        for b in balances:
            s = new_settlement(
                b["from_person"], b["to_person"], b["amount"], settlement_date,
                group_id, f"Chiusura automatica mese {month}",
            )
            self.data["settlements"].append(s)
            created.append(s)
        await self.async_save()
        return {"created": len(created), "month": month, "balances": created}

    async def transfer_month_balance(self, group_id: str, month: str):
        balances = self.balances(group_id, month)
        if not balances:
            return {"created": 0, "source_month": month, "target_month": add_months(f"{month}-01", 1)[:7], "carryovers": []}
        target_month = add_months(f"{month}-01", 1)[:7]
        created = []
        for b in balances:
            item = {
                "id": f"carryover_{datetime.now().timestamp():.6f}_{len(created)}",
                "from_person": b["from_person"],
                "to_person": b["to_person"],
                "amount": money(b["amount"]),
                "group_id": group_id,
                "source_month": month,
                "target_month": target_month,
                "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
            self.data["carryovers"].append(item)
            created.append(item)
        await self.async_save()
        return {"created": len(created), "source_month": month, "target_month": target_month, "carryovers": created}

    async def add_recurring(self, description, amount, paid_by, shares, group_id, category, cadence, next_date, notes="", installments_total=None):
        self._validate_shares(amount, paid_by, shares, group_id)
        if cadence not in CADENCE_MONTHS:
            raise ValueError("Unsupported cadence")
        r = new_recurring(description, amount, paid_by, shares, group_id, category, cadence, next_date, notes, installments_total, 0)
        self.data["recurring"].append(r)
        await self.async_save()
        return r

    async def update_recurring(self, recurring_id, description, amount, paid_by, shares, group_id, category, cadence, next_date, notes="", installments_total=None):
        self._validate_shares(amount, paid_by, shares, group_id)
        if cadence not in CADENCE_MONTHS:
            raise ValueError("Unsupported cadence")
        r = next((x for x in self.data["recurring"] if x["id"] == recurring_id), None)
        if not r:
            raise ValueError("Ricorrente non trovata")

        start_date = r.get("start_date") or r.get("next_date")
        # Never allow the schedule to move before its original start.
        if next_date < start_date:
            raise ValueError(f"La prossima scadenza non può essere precedente alla data di partenza {start_date}")

        done = int(r.get("installments_done") or 0)
        if installments_total is not None:
            installments_total = int(installments_total)
            if installments_total < 1:
                raise ValueError("Numero rate non valido")
            if installments_total < done:
                raise ValueError("Il numero totale di rate non può essere inferiore alle rate già generate")

        r.update({
            "description": description.strip(),
            "amount": money(amount),
            "paid_by": paid_by,
            "shares": {k: money(v) for k, v in shares.items()},
            "group_id": group_id,
            "category": category.strip() or "Altro",
            "cadence": cadence,
            "next_date": next_date,
            "notes": notes.strip(),
            "installments_total": installments_total,
        })
        if installments_total is None or done < installments_total:
            r["active"] = True
        await self.async_save()
        return r

    async def delete_recurring(self, recurring_id):
        before = len(self.data["recurring"])
        self.data["recurring"] = [r for r in self.data["recurring"] if r["id"] != recurring_id]
        deleted = before - len(self.data["recurring"])
        if deleted:
            await self.async_save()
        return deleted

    async def toggle_recurring(self, recurring_id: str, active: bool):
        r = next((r for r in self.data["recurring"] if r["id"] == recurring_id), None)
        if not r:
            raise ValueError("Recurring expense not found")
        r["active"] = active
        await self.async_save()

    async def materialize_due_recurring(self, through_date: str | None = None) -> int:
        through = through_date or date.today().isoformat()
        created = 0
        for r in self.data["recurring"]:
            start_date = r.get("start_date") or r.get("next_date")
            if r.get("next_date") and r["next_date"] < start_date:
                r["next_date"] = start_date
            while r.get("active", True) and r["next_date"] <= through and r["next_date"] >= start_date:
                total = r.get("installments_total")
                done = int(r.get("installments_done") or 0)
                if total is not None and done >= int(total):
                    r["active"] = False
                    break
                installment_current = (done + 1) if total is not None else None
                installment_total = int(total) if total is not None else None
                e = new_expense(
                    r["description"], r["amount"], r["paid_by"], r["shares"],
                    r["next_date"], r["group_id"], r["category"], r.get("notes", ""),
                    installment_current, installment_total
                )
                e["recurring_id"] = r["id"]
                self.data["expenses"].append(e)
                created += 1
                r["installments_done"] = done + 1
                r["next_date"] = add_months(r["next_date"], CADENCE_MONTHS[r["cadence"]])
                if total is not None and r["installments_done"] >= int(total):
                    r["active"] = False
        if created:
            await self.async_save()
        return created

    async def set_currency(self, currency: str):
        currency = currency.strip().upper()
        if len(currency) != 3:
            raise ValueError("Use a 3-letter ISO currency code")
        self.data["settings"]["currency"] = currency
        await self.async_save()

    async def import_data(self, payload: dict[str, Any], replace: bool = False):
        if replace:
            self.data = self._migrate(payload)
        else:
            for key in ("people", "groups", "expenses", "settlements", "recurring", "carryovers"):
                ids = {x.get("id") for x in self.data[key]}
                self.data[key].extend(x for x in payload.get(key, []) if x.get("id") not in ids)
            for c in payload.get("categories", []):
                if c not in self.data["categories"]:
                    self.data["categories"].append(c)
        await self.async_save()

    def balances(self, group_id: str | None, month: str | None = None):
        if not group_id or not self.group(group_id):
            return []
        net = defaultdict(float)

        for e in self.data["expenses"]:
            if e.get("group_id") != group_id:
                continue
            if month and not str(e.get("date", "")).startswith(month):
                continue
            for pid, share in e.get("shares", {}).items():
                if pid != e["paid_by"]:
                    net[(pid, e["paid_by"])] += float(share)

        for s in self.data["settlements"]:
            if s.get("group_id") != group_id:
                continue
            if month and not str(s.get("date", "")).startswith(month):
                continue
            net[(s["from_person"], s["to_person"])] -= float(s["amount"])

        if month:
            for c in self.data.get("carryovers", []):
                if c.get("group_id") != group_id:
                    continue
                key = (c["from_person"], c["to_person"])
                if c.get("source_month") == month:
                    net[key] -= float(c["amount"])
                if c.get("target_month") == month:
                    net[key] += float(c["amount"])

        out=[];seen=set()
        members=self.group(group_id)["members"]
        for a in members:
            for b in members:
                if a==b:continue
                pair=frozenset((a,b))
                if pair in seen:continue
                seen.add(pair)
                diff=net[(a,b)]-net[(b,a)]
                if abs(diff)<.005:continue
                debtor,creditor,amount=(a,b,diff) if diff>0 else (b,a,-diff)
                out.append({"from_person":debtor,"to_person":creditor,"amount":money(amount)})
        return sorted(out,key=lambda x:x["amount"],reverse=True)

    def summary(self, group_id: str | None, month: str | None = None):
        selected_month=month or date.today().strftime("%Y-%m")
        expenses=[e for e in self.data["expenses"] if e.get("group_id")==group_id]
        month_expenses=[e for e in expenses if str(e.get("date","")).startswith(selected_month)]
        month_balances=self.balances(group_id,selected_month)
        return {
            "selected_month":selected_month,
            "month_total":money(sum(float(e["amount"]) for e in month_expenses)),
            "month_count":len(month_expenses),
            "all_time_total":money(sum(float(e["amount"]) for e in expenses)),
            "people_count":len(self.group(group_id)["members"]) if self.group(group_id) else 0,
            "open_balances":len(month_balances),
            "recurring_active":sum(1 for r in self.data["recurring"] if r.get("group_id")==group_id and r.get("active",True)),
            "currency":self.data["settings"].get("currency",DEFAULT_CURRENCY),
        }

    def stats(self, group_id: str | None):
        by_cat, by_month = defaultdict(float), defaultdict(float)
        for e in self.data["expenses"]:
            if e.get("group_id") != group_id:
                continue
            by_cat[e.get("category", DEFAULT_CATEGORY)] += float(e["amount"])
            by_month[str(e.get("date", ""))[:7]] += float(e["amount"])
        return {
            "by_category": [{"name": k, "amount": money(v)} for k, v in sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True)],
            "by_month": [{"month": k, "amount": money(v)} for k, v in sorted(by_month.items())[-12:]],
        }
