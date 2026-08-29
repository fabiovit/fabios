from __future__ import annotations

from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PANEL_MODULE_URL, PANEL_URL, STATIC_URL, LITE_PANEL_MODULE_URL, LITE_PANEL_URL
from .store import FabiosStore
from .standalone_app import register_standalone_app
from .fabios_ws_v111 import async_register as async_register_websocket

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    register_standalone_app(hass)

    store = FabiosStore(hass)
    await store.async_load()
    await store.materialize_due_recurring()
    hass.data[DOMAIN][entry.entry_id] = {"store": store}

    frontend_dir = Path(__file__).parent / "frontend"
    if not hass.data[DOMAIN].get("_static_registered"):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(frontend_dir), False)]
        )
        hass.data[DOMAIN]["_static_registered"] = True

    
    if not hass.data[DOMAIN].get("_ws_registered"):
        async_register_websocket(hass)
        hass.data[DOMAIN]["_ws_registered"] = True

    # Register Fabio's and Fabio's Lite as two independent panels.
    # If the second registration fails, remove the first one before propagating
    # the exception so Home Assistant is never left with a half-registered setup.
    main_panel_registered = False
    lite_panel_registered = False
    try:
        await panel_custom.async_register_panel(
            hass,
            webcomponent_name="fabios-panel",
            frontend_url_path=PANEL_URL,
            module_url=PANEL_MODULE_URL,
            sidebar_title="Fabio's",
            sidebar_icon="mdi:cash-sync",
            require_admin=False,
            config={},
        )
        main_panel_registered = True

        await panel_custom.async_register_panel(
            hass,
            webcomponent_name="fabios-lite-panel",
            frontend_url_path=LITE_PANEL_URL,
            module_url=LITE_PANEL_MODULE_URL,
            sidebar_title="Fabio's Lite",
            sidebar_icon="mdi:account-cash",
            require_admin=False,
            config={},
        )
        lite_panel_registered = True
    except Exception:
        if lite_panel_registered:
            panel_custom.async_remove_panel(hass, LITE_PANEL_URL)
        if main_panel_registered:
            panel_custom.async_remove_panel(hass, PANEL_URL)
        raise

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        panel_custom.async_remove_panel(hass, LITE_PANEL_URL)
        panel_custom.async_remove_panel(hass, PANEL_URL)
    return unloaded
