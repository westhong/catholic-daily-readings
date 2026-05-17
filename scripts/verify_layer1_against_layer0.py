#!/usr/bin/env python3
"""Read-only full verification of Layer 1 readings.json against Layer 0 raw .cfm.

This verifier compares only USCCB-sourced citation metadata from Layer 1 against
locally archived USCCB .cfm files. It does not fetch live USCCB and does not
modify readings.json.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rebuild_layer1_from_layer0 import (
    BASE,
    READINGS_FILE,
    REPORT_DIR,
    normalize_citation,
    parse_citations_from_cfm,
    raw_path_for_entry,
)

DB_FILE = REPORT_DIR / "full-verification-db.json"
REPORT_FILE = REPORT_DIR / "full-verification-report.md"


def usccb_slots_from_entry(entry: dict[str, Any]) -> dict[str, list[str]]:
    slots: dict[str, list[str]] = {}
    for slot, value in entry.get("readings", {}).items():
        if isinstance(value, dict):
            items = [value]
        elif isinstance(value, list):
            items = value
        else:
            continue
        citations: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            if "USCCB" in item.get("sources", []) and item.get("citation"):
                citations.append(item["citation"])
        if citations:
            slots[slot] = citations
    return slots


def copyright_flags(entry: dict[str, Any]) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []
    allowed_entry_keys = {"date", "url", "lectionary_number", "feast", "mass", "readings"}
    extra_keys = sorted(set(entry) - allowed_entry_keys)
    if extra_keys:
        flags.append({"type": "unexpected_entry_keys", "detail": ", ".join(extra_keys)})

    sentence_like = re.compile(r"[.!?].+[.!?]")
    for slot, value in entry.get("readings", {}).items():
        items = value if isinstance(value, list) else [value]
        for item in items:
            if not isinstance(item, dict):
                flags.append({"type": "non_metadata_item", "detail": f"{slot}: {type(item).__name__}"})
                continue
            extra_item_keys = sorted(set(item) - {"citation", "sources"})
            if extra_item_keys:
                flags.append({"type": "unexpected_reading_keys", "detail": f"{slot}: {', '.join(extra_item_keys)}"})
            citation = item.get("citation", "")
            if not isinstance(citation, str):
                flags.append({"type": "bad_citation_type", "detail": slot})
            elif len(citation) > 180 or sentence_like.search(citation):
                flags.append({"type": "prose_like_citation", "detail": f"{slot}: {citation[:120]}"})
    return flags


def compare_slots(stored: dict[str, list[str]], parsed: dict[str, list[str]]) -> tuple[str, list[dict[str, Any]], list[str], list[str]]:
    mismatches: list[dict[str, Any]] = []
    all_slots = sorted(set(stored) | set(parsed))
    for slot in all_slots:
        stored_norm = [normalize_citation(c) for c in stored.get(slot, [])]
        parsed_norm = [normalize_citation(c) for c in parsed.get(slot, [])]
        if Counter(stored_norm) != Counter(parsed_norm):
            missing = sorted((Counter(parsed_norm) - Counter(stored_norm)).elements())
            extra = sorted((Counter(stored_norm) - Counter(parsed_norm)).elements())
            mismatches.append(
                {
                    "slot": slot,
                    "missing_from_stored": missing,
                    "extra_in_stored": extra,
                    "stored": stored.get(slot, []),
                    "raw": parsed.get(slot, []),
                }
            )

    stored_set = Counter(c for vals in stored.values() for c in map(normalize_citation, vals))
    parsed_set = Counter(c for vals in parsed.values() for c in map(normalize_citation, vals))
    missing_from_stored = sorted((parsed_set - stored_set).elements())
    extra_in_stored = sorted((stored_set - parsed_set).elements())

    if not mismatches:
        return "PASS", mismatches, missing_from_stored, extra_in_stored
    if not missing_from_stored and not extra_in_stored:
        return "SLOT_MISMATCH_ONLY", mismatches, missing_from_stored, extra_in_stored
    return "FAIL", mismatches, missing_from_stored, extra_in_stored


def verify_all() -> dict[str, Any]:
    readings = json.loads(READINGS_FILE.read_text())
    records: list[dict[str, Any]] = []

    for date_key in sorted(readings):
        entries = readings[date_key]
        if isinstance(entries, dict):
            entries = [entries]
        for mass_idx, entry in enumerate(entries):
            flags = copyright_flags(entry)
            raw_path = raw_path_for_entry(entry, date_key)
            record: dict[str, Any] = {
                "date": date_key,
                "mass_idx": mass_idx,
                "feast": entry.get("feast"),
                "mass": entry.get("mass"),
                "lectionary_number": entry.get("lectionary_number"),
                "url": entry.get("url"),
                "copyright_flags": flags,
            }
            if raw_path is None:
                record.update({"status": "MISSING_RAW", "raw_file": None, "mismatches": []})
                records.append(record)
                continue

            parsed = parse_citations_from_cfm(raw_path)
            stored = usccb_slots_from_entry(entry)
            status, mismatches, missing, extra = compare_slots(stored, parsed)
            if flags and status == "PASS":
                status = "COPYRIGHT_REVIEW"
            record.update(
                {
                    "status": status,
                    "raw_file": str(raw_path.relative_to(BASE)),
                    "parsed_slots": parsed,
                    "stored_usccb_slots": stored,
                    "citation_set_missing_from_stored": missing,
                    "citation_set_extra_in_stored": extra,
                    "mismatches": mismatches,
                }
            )
            records.append(record)

    summary = Counter(record["status"] for record in records)
    return {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "data/lectionary/readings.json ⇄ data/usccb-calendar/raw/*.cfm",
        "total_records": len(records),
        "summary": dict(sorted(summary.items())),
        "records": records,
    }


def render_report(db: dict[str, Any]) -> str:
    summary = db["summary"]
    accepted = summary.get("PASS", 0) + summary.get("ACCEPTED_EXCEPTION", 0)
    total = db["total_records"]
    pct = (accepted / total * 100) if total else 0
    lines = [
        "# Full Layer 1 Verification Report",
        "",
        f"- Run at: `{db['run_at']}`",
        "- Compared: `data/lectionary/readings.json` ⇄ `data/usccb-calendar/raw/*.cfm`",
        f"- Total records: **{total}**",
    ]
    for key in ["PASS", "ACCEPTED_EXCEPTION", "FAIL", "MISSING_RAW", "SLOT_MISMATCH_ONLY", "COPYRIGHT_REVIEW"]:
        if key in summary:
            lines.append(f"- {key}: **{summary[key]}**")
    lines.extend(
        [
            f"- Gate coverage (PASS + ACCEPTED_EXCEPTION): **{accepted}/{total} ({pct:.2f}%)**",
            "",
            "## Meaning",
            "- PASS: slot-level USCCB citations match local Layer 0 raw file.",
            "- SLOT_MISMATCH_ONLY: same citation set, but assigned to different slot/key.",
            "- FAIL: citation set differs from raw Layer 0.",
            "- MISSING_RAW: no local raw file could be matched.",
            "- COPYRIGHT_REVIEW: Layer 1 contains suspicious non-metadata fields or prose-like citation.",
            "",
            "## First 80 non-pass records",
            "",
        ]
    )

    non_pass = [record for record in db["records"] if record["status"] != "PASS"][:80]
    if not non_pass:
        lines.append("All records passed.")
    for record in non_pass:
        lines.append(f"### {record['status']} — {record['date']}[{record['mass_idx']}] — {record.get('feast') or ''}")
        lines.append(f"- URL: `{record.get('url')}`")
        lines.append(f"- Raw: `{record.get('raw_file')}`")
        if record.get("citation_set_missing_from_stored"):
            lines.append(f"- Missing from stored: `{record['citation_set_missing_from_stored']}`")
        if record.get("citation_set_extra_in_stored"):
            lines.append(f"- Extra in stored: `{record['citation_set_extra_in_stored']}`")
        for mismatch in record.get("mismatches", []):
            lines.append(
                f"  - {mismatch['slot']}: missing={mismatch['missing_from_stored']} extra={mismatch['extra_in_stored']}"
            )
        for flag in record.get("copyright_flags", []):
            lines.append(f"  - copyright flag: {flag['type']} — {flag['detail']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    db = verify_all()
    DB_FILE.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n")
    REPORT_FILE.write_text(render_report(db))
    print(json.dumps({"total_records": db["total_records"], "summary": db["summary"], "report": str(REPORT_FILE)}, indent=2))


if __name__ == "__main__":
    main()
