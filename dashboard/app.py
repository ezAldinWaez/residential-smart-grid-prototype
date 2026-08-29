"""Web dashboard application and JSON control API."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from Pyro5.api import Proxy
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
TEMPLATE_DIR = PACKAGE_DIR / "templates"


class DashboardService:
    """Translate HTTP requests into short-lived Pyro remote-object calls."""

    def __init__(self) -> None:
        load_dotenv()
        host = os.getenv("RSGP_REMOTE_OBJECT_HOST", "0.0.0.0")
        port = int(os.getenv("RSGP_REMOTE_OBJECT_PORT", 41991))
        self._base_uri = f"PYRO:{{name}}@{host}:{port}"

    def _proxy(self, name: str) -> Proxy:
        return Proxy(self._base_uri.format(name=name))

    @staticmethod
    def _json_error(message: str, status_code: int = 503) -> JSONResponse:
        return JSONResponse({"ok": False, "error": message}, status_code=status_code)

    async def _run(self, operation: Callable[[], Any]) -> Any:
        """Run blocking Pyro work off the event loop."""
        return await asyncio.to_thread(operation)

    async def index(self, _request: Request) -> FileResponse:
        return FileResponse(TEMPLATE_DIR / "index.html")

    async def snapshot(self, _request: Request) -> JSONResponse:
        def collect() -> dict[str, Any]:
            with self._proxy("time_sim") as time_sim:
                timestamp = time_sim.get_timestamp()
            with self._proxy("houses_sim") as houses_sim:
                houses = houses_sim.get_dashboard_metrics()
            with self._proxy("solar_system_sim") as solar_sim:
                solar = solar_sim.get_dashboard_metrics()
            with self._proxy("power_manager") as power_manager:
                power = power_manager.get_dashboard_metrics()
            return {
                "ok": True,
                "timestamp": timestamp,
                "running": bool(houses["running"] or solar["running"] or power["running"]),
                "houses": houses,
                "solar": solar,
                "power": power,
            }

        try:
            return JSONResponse(await self._run(collect))
        except Exception:
            return self._json_error("The simulation services are unavailable. Retrying automatically.")

    async def set_simulation(self, request: Request) -> JSONResponse:
        action = request.path_params["action"]
        if action not in {"pause", "resume", "toggle"}:
            return self._json_error("Unknown simulation action.", 404)

        def update() -> dict[str, Any]:
            names = ("houses_sim", "solar_system_sim", "power_manager")
            if action == "toggle":
                with self._proxy("houses_sim") as houses_sim:
                    target = "pause" if houses_sim.is_running() else "resume"
            else:
                target = action
            with self._proxy("time_sim") as time_sim:
                getattr(time_sim, target)()
            for name in names:
                with self._proxy(name) as simulator:
                    getattr(simulator, target)()
            return {"ok": True, "running": target == "resume"}

        try:
            return JSONResponse(await self._run(update))
        except Exception:
            return self._json_error("Could not update the simulation state.")

    async def set_all_lines(self, request: Request) -> JSONResponse:
        line = request.path_params["line"]
        if line not in {"utility", "load"}:
            return self._json_error("Unknown line type.", 404)
        try:
            payload = await request.json()
        except Exception:
            return self._json_error("A JSON request body is required.", 400)
        state = payload.get("state")
        if not isinstance(state, bool):
            return self._json_error("The state field must be true or false.", 400)

        def update() -> dict[str, Any]:
            method = f"set_all_{line}_lines"
            with self._proxy("houses_sim") as houses_sim:
                getattr(houses_sim, method)(state)
            return {"ok": True, "line": line, "state": state}

        try:
            return JSONResponse(await self._run(update))
        except Exception:
            return self._json_error(f"Could not update the {line} lines.")

    async def toggle_house_line(self, request: Request) -> JSONResponse:
        house_idx = request.path_params["house_idx"]
        line = request.path_params["line"]
        if line not in {"utility", "load"}:
            return self._json_error("Unknown line type.", 404)

        def update() -> dict[str, Any]:
            method = f"toggle_house_{line}_line"
            with self._proxy("houses_sim") as houses_sim:
                state = getattr(houses_sim, method)(house_idx)
            return {"ok": True, "house_idx": house_idx, "line": line, "state": state}

        try:
            return JSONResponse(await self._run(update))
        except (IndexError, KeyError):
            return self._json_error("The requested house does not exist.", 404)
        except Exception:
            return self._json_error(f"Could not toggle the house {line} line.")

    async def house_devices(self, request: Request) -> JSONResponse:
        house_idx = request.path_params["house_idx"]

        def collect() -> dict[str, Any]:
            with self._proxy("houses_sim") as houses_sim:
                metrics = houses_sim.get_house_devices_metrics(house_idx)
            return {"ok": True, **metrics}

        try:
            return JSONResponse(await self._run(collect))
        except IndexError:
            return self._json_error("The requested house does not exist.", 404)
        except Exception:
            return self._json_error("Device telemetry is currently unavailable.")

    async def toggle_device(self, request: Request) -> JSONResponse:
        house_idx = request.path_params["house_idx"]
        device_name = request.path_params["device_name"]
        envelope_idx = request.path_params["envelope_idx"]

        def update() -> dict[str, Any]:
            with self._proxy("houses_sim") as houses_sim:
                state = houses_sim.toggle_house_device(
                    house_idx,
                    device_name,
                    envelope_idx,
                )
            return {
                "ok": True,
                "house_idx": house_idx,
                "device_name": device_name,
                "envelope_idx": envelope_idx,
                "state": state,
            }

        try:
            return JSONResponse(await self._run(update))
        except (IndexError, KeyError):
            return self._json_error("The requested device control does not exist.", 404)
        except Exception:
            return self._json_error("Could not update the device control.")


def create_app() -> Starlette:
    """Create the Starlette web dashboard."""
    service = DashboardService()
    routes = [
        Route("/", service.index, methods=["GET"]),
        Route("/api/snapshot", service.snapshot, methods=["GET"]),
        Route("/api/simulation/{action:str}", service.set_simulation, methods=["POST"]),
        Route("/api/houses/lines/{line:str}", service.set_all_lines, methods=["POST"]),
        Route(
            "/api/houses/{house_idx:int}/lines/{line:str}/toggle",
            service.toggle_house_line,
            methods=["POST"],
        ),
        Route(
            "/api/houses/{house_idx:int}/devices",
            service.house_devices,
            methods=["GET"],
        ),
        Route(
            "/api/houses/{house_idx:int}/devices/{device_name:str}/{envelope_idx:int}/toggle",
            service.toggle_device,
            methods=["POST"],
        ),
        Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
    ]
    return Starlette(debug=False, routes=routes)


app = create_app()
