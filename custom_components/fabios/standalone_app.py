from __future__ import annotations

from pathlib import Path

from aiohttp import web
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN

_FRONTEND = Path(__file__).parent / "frontend"


class FabiosStandaloneAppView(HomeAssistantView):
    url = "/fabios-app/"
    name = "fabios:standalone_app"
    requires_auth = False

    async def get(self, request):
        return web.Response(
            text=(_FRONTEND / "fabios-app.html").read_text(encoding="utf-8"),
            content_type="text/html",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )


class FabiosStandaloneAppNoSlashView(HomeAssistantView):
    url = "/fabios-app"
    name = "fabios:standalone_app_redirect"
    requires_auth = False

    async def get(self, request):
        raise web.HTTPFound("/fabios-app/")


class FabiosStandaloneManifestView(HomeAssistantView):
    url = "/fabios-app/manifest.webmanifest"
    name = "fabios:standalone_manifest"
    requires_auth = False

    async def get(self, request):
        return web.Response(
            text=(_FRONTEND / "fabios-app.webmanifest").read_text(encoding="utf-8"),
            content_type="application/manifest+json",
            headers={"Cache-Control": "no-cache"},
        )


class FabiosStandaloneServiceWorkerView(HomeAssistantView):
    url = "/fabios-app/sw.js"
    name = "fabios:standalone_sw"
    requires_auth = False

    async def get(self, request):
        return web.Response(
            text=(_FRONTEND / "fabios-app-sw.js").read_text(encoding="utf-8"),
            content_type="application/javascript",
            headers={
                "Cache-Control": "no-cache",
                "Service-Worker-Allowed": "/fabios-app/",
            },
        )


class FabiosStandaloneIconView(HomeAssistantView):
    url = "/fabios-app/icon.svg"
    name = "fabios:standalone_icon"
    requires_auth = False

    async def get(self, request):
        return web.Response(
            text=(_FRONTEND / "fabios-app-icon.svg").read_text(encoding="utf-8"),
            content_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=86400"},
        )


def register_standalone_app(hass) -> None:
    """Register the public app shell once per HA process.

    The shell contains no Fabio's data. Actual data access is authenticated
    through Home Assistant OAuth + websocket.
    """
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("_standalone_app_registered"):
        return

    hass.http.register_view(FabiosStandaloneAppView)
    hass.http.register_view(FabiosStandaloneAppNoSlashView)
    hass.http.register_view(FabiosStandaloneManifestView)
    hass.http.register_view(FabiosStandaloneServiceWorkerView)
    hass.http.register_view(FabiosStandaloneIconView)
    domain_data["_standalone_app_registered"] = True
