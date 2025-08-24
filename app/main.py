from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from . import __version__
import os
import platform
import time
from datetime import datetime, timezone
from typing import Optional
import logging

from .modules import historical_event_importer

logger = logging.getLogger(__name__)

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
                "ml_core": False,  # Devin tamamlayacak
                "db": False,       # opsiyonel
            },
            "notes": "SENKRON bootstrap sağlıklı. Çekirdek modüller iskelet halinde.",
        }
    )

@app.get("/patterns")
def get_patterns(
    min_weight: float = Query(0.0, description="Minimum event weight filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    csv_path: str = Query("data/historical_events.csv", description="CSV file path")
):
    """
    Historical event pattern analysis endpoint.
    
    Returns events filtered by weight, category, and date range.
    Results are split into window_a and window_b based on date ranges.
    """
    try:
        events = historical_event_importer.import_historical_events(
            csv_path=csv_path,
            min_weight=min_weight,
            category_filter=category
        )
        
        if start_date or end_date:
            filtered_events = []
            for event in events:
                event_date = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                
                if start_date:
                    start_dt = datetime.fromisoformat(start_date + 'T00:00:00+00:00')
                    if event_date < start_dt:
                        continue
                
                if end_date:
                    end_dt = datetime.fromisoformat(end_date + 'T23:59:59+00:00')
                    if event_date > end_dt:
                        continue
                
                filtered_events.append(event)
            
            events = filtered_events
        
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date + 'T00:00:00+00:00')
            end_dt = datetime.fromisoformat(end_date + 'T23:59:59+00:00')
            mid_dt = start_dt + (end_dt - start_dt) / 2
            
            window_a_events = []
            window_b_events = []
            
            for event in events:
                event_date = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                if event_date <= mid_dt:
                    window_a_events.append(event)
                else:
                    window_b_events.append(event)
        else:
            mid_point = len(events) // 2
            window_a_events = events[:mid_point]
            window_b_events = events[mid_point:]
        
        return {
            "total_events": len(events),
            "filters": {
                "min_weight": min_weight,
                "category": category,
                "start_date": start_date,
                "end_date": end_date
            },
            "window_a": {
                "events": window_a_events,
                "count": len(window_a_events)
            },
            "window_b": {
                "events": window_b_events,
                "count": len(window_b_events)
            }
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Patterns endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
