from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "America/Edmonton"
ROOT = Path(__file__).resolve().parents[2]
READINGS_FILE = ROOT / "data" / "lectionary" / "readings.json"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class InvalidDateError(ValueError):
    """Raised when date is not in YYYY-MM-DD format or is not a real date."""


class GospelNotFoundError(KeyError):
    """Raised when readings.json has no record for the requested date."""


def _resolve_date(date: str | None, timezone: str, today: str | None) -> str:
    if date is None:
        return today or datetime.now(ZoneInfo(timezone)).date().isoformat()
    if not DATE_RE.match(date):
        raise InvalidDateError("date must be YYYY-MM-DD")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError as exc:
        raise InvalidDateError("date must be a real YYYY-MM-DD date") from exc
    return date


def _load_readings(readings_file: Path = READINGS_FILE) -> dict:
    return json.loads(readings_file.read_text())


def get_gospel(
    date: str | None = None,
    *,
    timezone: str = DEFAULT_TIMEZONE,
    today: str | None = None,
    readings_file: Path = READINGS_FILE,
) -> dict:
    """Return citation-only Gospel metadata for a date.

    If date is omitted, today's date is calculated in the requested timezone.
    The returned payload intentionally contains no Bible text.
    """
    date_key = _resolve_date(date, timezone, today)
    readings = _load_readings(readings_file)
    entries = readings.get(date_key)
    if not entries:
        raise GospelNotFoundError(date_key)

    records = []
    for entry in entries:
        gospels = deepcopy(entry.get("readings", {}).get("gospel", []))
        records.append(
            {
                "feast": entry.get("feast"),
                "mass": entry.get("mass", "default"),
                "lectionary_number": entry.get("lectionary_number"),
                "gospels": gospels,
            }
        )

    return {
        "date": date_key,
        "timezone": timezone,
        "source": "catholic-daily-readings",
        "records": records,
    }
