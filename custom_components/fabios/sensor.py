from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fabio's sensors."""
    store = hass.data[DOMAIN][entry.entry_id]["store"]
    async_add_entities(
        [
            FabiosSensor(store, entry.entry_id, "month_total", "mdi:cash-multiple"),
            FabiosSensor(store, entry.entry_id, "open_balances", "mdi:scale-balance"),
            FabiosSensor(store, entry.entry_id, "recurring_active", "mdi:calendar-sync"),
        ]
    )


class FabiosSensor(SensorEntity):
    """Expose a Fabio's summary value."""

    _attr_has_entity_name = True

    def __init__(self, store, entry_id: str, key: str, icon: str) -> None:
        self.store = store
        self.key = key
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_icon = icon

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "fabios")},
            "name": "Fabio's",
            "manufacturer": "Fabio Vittori",
            "model": "Shared Expense Manager",
        }

    @property
    def native_value(self):
        summary = self.store.summary(self.store.active_group_id())
        if self.key == "month_total":
            self._attr_native_unit_of_measurement = summary["currency"]
        return summary[self.key]

    @property
    def extra_state_attributes(self):
        if self.key == "open_balances":
            return {"balances": self.store.balances(self.store.active_group_id())}
        return {}
