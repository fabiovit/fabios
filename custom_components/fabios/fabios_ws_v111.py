from __future__ import annotations

import calendar

from datetime import date
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .importer import parse_upload, convert_preview_rows


def _store(hass):
    entries = hass.data.get(DOMAIN, {})
    for key, value in entries.items():
        if isinstance(value, dict) and "store" in value:
            return value["store"]
    raise ValueError("Fabio's is not configured")


def _ok(connection, message, result):
    connection.send_result(message["id"], result)


def _err(connection, message, exc):
    connection.send_error(message["id"], "fabios_error", str(exc))


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/get_state",
    vol.Optional("group_id"): str,
    vol.Optional("month"): str,
})
@websocket_api.async_response
async def get_state(hass, connection, message):
    store = _store(hass)
    month = message.get("month")
    if month:
        try:
            year, mon = (int(x) for x in month.split("-", 1))
            last_day = calendar.monthrange(year, mon)[1]
            await store.materialize_due_recurring(f"{year:04d}-{mon:02d}-{last_day:02d}")
        except (ValueError, TypeError):
            pass
    _ok(connection, message, store.snapshot(message.get("group_id"), month))


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/add_person",
    vol.Required("name"): str,
})
@websocket_api.async_response
async def add_person(hass, connection, message):
    try:
        result = await _store(hass).add_person(message["name"])
        _ok(connection, message, result)
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/delete_person",
    vol.Required("person_id"): str,
})
@websocket_api.async_response
async def delete_person(hass, connection, message):
    try:
        await _store(hass).delete_person(message["person_id"])
        _ok(connection, message, {"success": True})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/add_group",
    vol.Required("name"): str,
    vol.Required("members"): [str],
})
@websocket_api.async_response
async def add_group(hass, connection, message):
    try:
        result = await _store(hass).add_group(message["name"], message["members"])
        _ok(connection, message, result)
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/archive_group",
    vol.Required("group_id"): str,
    vol.Required("archived"): bool,
})
@websocket_api.async_response
async def archive_group(hass, connection, message):
    try:
        await _store(hass).archive_group(message["group_id"], message["archived"])
        _ok(connection, message, {"success": True})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/add_expense",
    vol.Required("description"): str,
    vol.Required("amount"): vol.Coerce(float),
    vol.Required("paid_by"): str,
    vol.Required("shares"): dict,
    vol.Required("group_id"): str,
    vol.Optional("category", default="Altro"): str,
    vol.Optional("date", default=date.today().isoformat()): str,
    vol.Optional("notes", default=""): str,
    vol.Optional("installment_current"): vol.Any(None, vol.Coerce(int)),
    vol.Optional("installment_total"): vol.Any(None, vol.Coerce(int)),
})
@websocket_api.async_response
async def add_expense(hass, connection, message):
    try:
        result = await _store(hass).add_expense(
            message["description"],
            message["amount"],
            message["paid_by"],
            message["shares"],
            message["date"],
            message["group_id"],
            message["category"],
            message["notes"],
            message.get("installment_current"),
            message.get("installment_total"),
        )
        _ok(connection, message, result)
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/update_expense",
    vol.Required("expense_id"): str,
    vol.Required("description"): str,
    vol.Required("amount"): vol.Coerce(float),
    vol.Required("paid_by"): str,
    vol.Required("shares"): dict,
    vol.Required("date"): str,
    vol.Required("group_id"): str,
    vol.Required("category"): str,
    vol.Optional("notes", default=""): str,
    vol.Optional("installment_current"): vol.Any(None, vol.Coerce(int)),
    vol.Optional("installment_total"): vol.Any(None, vol.Coerce(int)),
})
@websocket_api.async_response
async def update_expense(hass, connection, message):
    try:
        item = await _store(hass).update_expense(
            message["expense_id"], message["description"], message["amount"],
            message["paid_by"], message["shares"], message["date"],
            message["group_id"], message["category"], message["notes"],
            message.get("installment_current"), message.get("installment_total"),
        )
        _ok(connection, message, item)
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/delete_expense",
    vol.Required("expense_id"): str,
})
@websocket_api.async_response
async def delete_expense(hass, connection, message):
    try:
        await _store(hass).delete_expense(message["expense_id"])
        _ok(connection, message, {"success": True})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/delete_expenses",
    vol.Required("expense_ids"): [str],
})
@websocket_api.async_response
async def delete_expenses(hass, connection, message):
    try:
        deleted = await _store(hass).delete_expenses(message["expense_ids"])
        _ok(connection, message, {"deleted": deleted})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/add_settlement",
    vol.Required("from_person"): str,
    vol.Required("to_person"): str,
    vol.Required("amount"): vol.Coerce(float),
    vol.Required("group_id"): str,
    vol.Optional("date", default=date.today().isoformat()): str,
    vol.Optional("notes", default=""): str,
})
@websocket_api.async_response
async def add_settlement(hass, connection, message):
    try:
        result = await _store(hass).add_settlement(
            message["from_person"],
            message["to_person"],
            message["amount"],
            message["date"],
            message["group_id"],
            message["notes"],
        )
        _ok(connection, message, result)
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/add_recurring",
    vol.Required("description"): str,
    vol.Required("amount"): vol.Coerce(float),
    vol.Required("paid_by"): str,
    vol.Required("shares"): dict,
    vol.Required("group_id"): str,
    vol.Optional("category", default="Altro"): str,
    vol.Required("cadence"): str,
    vol.Required("next_date"): str,
    vol.Optional("notes", default=""): str,
    vol.Optional("installments_total"): vol.Any(None, vol.Coerce(int)),
})
@websocket_api.async_response
async def add_recurring(hass, connection, message):
    try:
        result = await _store(hass).add_recurring(
            message["description"],
            message["amount"],
            message["paid_by"],
            message["shares"],
            message["group_id"],
            message["category"],
            message["cadence"],
            message["next_date"],
            message["notes"],
            message.get("installments_total"),
        )
        _ok(connection, message, result)
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/update_recurring",
    vol.Required("recurring_id"): str,
    vol.Required("description"): str,
    vol.Required("amount"): vol.Coerce(float),
    vol.Required("paid_by"): str,
    vol.Required("shares"): dict,
    vol.Required("group_id"): str,
    vol.Required("category"): str,
    vol.Required("cadence"): str,
    vol.Required("next_date"): str,
    vol.Optional("notes", default=""): str,
    vol.Optional("installments_total"): vol.Any(None, vol.Coerce(int)),
})
@websocket_api.async_response
async def update_recurring(hass, connection, message):
    try:
        item = await _store(hass).update_recurring(
            message["recurring_id"], message["description"], message["amount"],
            message["paid_by"], message["shares"], message["group_id"],
            message["category"], message["cadence"], message["next_date"],
            message["notes"], message.get("installments_total"),
        )
        _ok(connection, message, item)
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/delete_recurring",
    vol.Required("recurring_id"): str,
})
@websocket_api.async_response
async def delete_recurring(hass, connection, message):
    try:
        deleted = await _store(hass).delete_recurring(message["recurring_id"])
        _ok(connection, message, {"deleted": deleted})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/toggle_recurring",
    vol.Required("recurring_id"): str,
    vol.Required("active"): bool,
})
@websocket_api.async_response
async def toggle_recurring(hass, connection, message):
    try:
        await _store(hass).update_recurring_active(
            message["recurring_id"], message["active"]
        )
        _ok(connection, message, {"success": True})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/materialize_recurring",
    vol.Optional("through_date"): str,
})
@websocket_api.async_response
async def materialize_recurring(hass, connection, message):
    try:
        created = await _store(hass).materialize_due_recurring(
            message.get("through_date")
        )
        _ok(connection, message, {"created": created})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/add_category",
    vol.Required("name"): str,
})
@websocket_api.async_response
async def add_category(hass, connection, message):
    try:
        await _store(hass).add_category(message["name"])
        _ok(connection, message, {"success": True})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/set_currency",
    vol.Required("currency"): str,
})
@websocket_api.async_response
async def set_currency(hass, connection, message):
    try:
        await _store(hass).set_currency(message["currency"])
        _ok(connection, message, {"success": True})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/export",
})
@websocket_api.async_response
async def export_data(hass, connection, message):
    _ok(connection, message, _store(hass).export_data())


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/import",
    vol.Required("payload"): dict,
    vol.Optional("replace", default=False): bool,
})
@websocket_api.async_response
async def import_data(hass, connection, message):
    try:
        await _store(hass).import_data(message["payload"], message["replace"])
        _ok(connection, message, {"success": True})
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/import_preview",
    vol.Required("filename"): str,
    vol.Required("content_b64"): str,
})
@websocket_api.async_response
async def import_preview(hass, connection, message):
    try:
        result = parse_upload(message["filename"], message["content_b64"])
        _ok(connection, message, result)
    except Exception as exc:
        _err(connection, message, exc)


@websocket_api.websocket_command({
    vol.Required("type"): "fabios/import_commit",
    vol.Required("rows"): list,
    vol.Required("positive_payer"): str,
    vol.Required("negative_payer"): str,
    vol.Required("group_id"): str,
    vol.Optional("category", default="Altro"): str,
    vol.Optional("year_hint"): vol.Any(None, vol.Coerce(int)),
})
@websocket_api.async_response
async def import_commit(hass, connection, message):
    try:
        store = _store(hass)
        items = convert_preview_rows(
            message["rows"],
            message["positive_payer"],
            message["negative_payer"],
            message["group_id"],
            message["category"],
            message.get("year_hint"),
        )
        for item in items:
            await store.add_expense(
                item["description"],
                item["amount"],
                item["paid_by"],
                item["shares"],
                item["date"],
                item["group_id"],
                item["category"],
                item["notes"],
                item.get("installment_current"),
                item.get("installment_total"),
            )
        _ok(connection, message, {"created": len(items)})
    except Exception as exc:
        _err(connection, message, exc)


def async_register(hass: HomeAssistant) -> None:
    commands = (
        get_state,
        add_person,
        delete_person,
        add_group,
        archive_group,
        add_expense,
        update_expense,
        delete_expense,
        delete_expenses,
        add_settlement,
        add_recurring,
        update_recurring,
        delete_recurring,
        toggle_recurring,
        materialize_recurring,
        add_category,
        set_currency,
        export_data,
        import_data,
        import_preview,
        import_commit,
    )
    for command in commands:
        websocket_api.async_register_command(hass, command)
