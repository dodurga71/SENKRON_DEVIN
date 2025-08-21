import os
import platform
import time
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse

__version__ = "0.3.0"

app = FastAPI(title="SENKRONX_PLUS API", version=__version__)

@app.get("/version")
def version():
    started = float(os.environ.get("APP_STARTED_AT", time.time()))
    uptime = time.time() - started
    return {
        "version": __version__,
        "time": datetime.now(timezone.utc).isoformat(),
        "uptime_sec": uptime,
        "started_at": datetime.fromtimestamp(started, tz=timezone.utc).isoformat(),
        "name": "SENKRONX_PLUS API",
        "node": platform.node(),
        "python": platform.python_version(),
    }

@app.get("/healthz/details")
def healthz_details():
    return JSONResponse(
        {
            "status": "ok",
            "services": {"api": True, "ml_core": False, "db": False},
            "notes": "SENKRON bootstrap sağlıklı. Çekirdek modüller iskelet halinde.",
        }
    )