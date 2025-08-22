import os
import platform
import time
from datetime import datetime, timezone
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import __version__
from .modules.timeline_engine import build_window, discover_triggers
from .modules.unified_predictor import unified_score

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
            "services": {
                "api": True,
                "sbzet_quantum": True,
                "timeline_engine": True,
                "unified_predictor": True,
                "ephemeris_engine": True,
            },
            "notes": "SENKRON SBZET v2025.9 entegrasyonu aktif.",
        }
    )

class PredictRequest(BaseModel):
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format
    E: float         # Quantum enerji seviyesi
    delta_g: float   # Gravitasyonel değişim
    D: float         # Mesafe/gecikme faktörü
    weights: Optional[Tuple[float, float]] = (0.7, 0.3)  # (astro_weight, quantum_weight)

@app.post("/predict")
def predict(request: PredictRequest):
    """SBZET unified prediction endpoint"""
    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()

        result = unified_score(
            start_date=start_date,
            end_date=end_date,
            E=request.E,
            delta_g=request.delta_g,
            D=request.D,
            weights=request.weights or (0.7, 0.3)
        )

        result["version"] = __version__
        result["timestamp"] = datetime.now(timezone.utc).isoformat()
        result["sbzet_version"] = "v2025.9"

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Geçersiz parametre: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hesaplama hatası: {str(e)}") from e

@app.get("/patterns")
def patterns(start: str, end: str):
    """Timeline pattern discovery endpoint"""
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()

        mid_date = start_date + (end_date - start_date) / 2

        window_a = build_window(start_date, mid_date)
        window_b = build_window(mid_date, end_date)

        patterns = discover_triggers(window_a, window_b)

        result = {
            "period": {"start": start, "end": end},
            "windows": {
                "window_a": {"start": start_date.isoformat(), "end": mid_date.isoformat(), "events": len(window_a)},
                "window_b": {"start": mid_date.isoformat(), "end": end_date.isoformat(), "events": len(window_b)}
            },
            "patterns": [
                {
                    "name": p.name,
                    "score": p.score,
                    "description": p.description,
                    "nodes": p.nodes,
                    "links": p.links
                } for p in patterns
            ],
            "pattern_count": len(patterns),
            "version": __version__,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Geçersiz tarih formatı: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern keşif hatası: {str(e)}") from e
