from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Query

from src.service.gospel import DEFAULT_TIMEZONE, GospelNotFoundError, InvalidDateError, get_gospel

app = FastAPI(
    title="Catholic Daily Readings API",
    description="Citation-only Catholic lectionary metadata API.",
    version="0.1.0",
)


def get_today(timezone: str = DEFAULT_TIMEZONE) -> str:
    return datetime.now(ZoneInfo(timezone)).date().isoformat()


@app.get("/api/v1/gospel")
def gospel_endpoint(
    date: str | None = Query(default=None, description="Date in YYYY-MM-DD format. Defaults to today in America/Edmonton."),
    today: str = Depends(get_today),
):
    try:
        return get_gospel(date, today=today)
    except InvalidDateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GospelNotFoundError as exc:
        missing_date = exc.args[0] if exc.args else date
        raise HTTPException(status_code=404, detail=f"No Gospel metadata found for {missing_date}") from exc
