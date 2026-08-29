from __future__ import annotations
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import uuid4

def money(value: Any) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"

def new_person(name: str):
    return {"id": new_id("person"), "name": name.strip(), "created_at": now_iso()}

def new_group(name: str, member_ids: list[str]):
    return {"id": new_id("group"), "name": name.strip(), "members": list(dict.fromkeys(member_ids)), "archived": False, "created_at": now_iso()}

def new_expense(description, amount, paid_by, shares, date, group_id, category, notes="", installment_current=None, installment_total=None):
    item = {"id": new_id("expense"), "description": description.strip(), "amount": money(amount), "paid_by": paid_by, "shares": {k: money(v) for k,v in shares.items()}, "date": date, "group_id": group_id, "category": category.strip() or "Altro", "notes": notes.strip(), "created_at": now_iso()}
    if installment_current is not None and installment_total is not None:
        item["installment_current"] = int(installment_current)
        item["installment_total"] = int(installment_total)
    return item

def new_settlement(from_person, to_person, amount, date, group_id, notes=""):
    return {"id": new_id("settlement"), "from_person": from_person, "to_person": to_person, "amount": money(amount), "date": date, "group_id": group_id, "notes": notes.strip(), "created_at": now_iso()}

def new_recurring(description, amount, paid_by, shares, group_id, category, cadence, next_date, notes="", installments_total=None, installments_done=0):
    return {"id": new_id("recurring"), "description": description.strip(), "amount": money(amount), "paid_by": paid_by, "shares": {k: money(v) for k,v in shares.items()}, "group_id": group_id, "category": category.strip() or "Altro", "cadence": cadence, "start_date": next_date, "next_date": next_date, "active": True, "notes": notes.strip(), "installments_total": installments_total, "installments_done": installments_done, "created_at": now_iso()}
