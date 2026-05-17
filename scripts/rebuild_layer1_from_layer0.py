#!/usr/bin/env python3
"""Rebuild Layer 1 readings.json from Layer 0 USCCB .cfm files.

This script is intentionally metadata-only: it reads citation links from local raw
USCCB HTML and rewrites the USCCB portion of Layer 1. It does not copy Bible
text or liturgical body text from the source pages.
"""

from __future__ import annotations

import argparse
import copy
import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parents[1]
READINGS_FILE = BASE / "data" / "lectionary" / "readings.json"
RAW_DIR = BASE / "data" / "usccb-calendar" / "raw"
REPORT_DIR = BASE / "data" / "verification"

ROMAN_NUMBERS = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7}
READING_SLOT = {
    1: "first_reading",
    2: "second_reading",
    3: "third_reading",
    4: "fourth_reading",
    5: "fifth_reading",
    6: "sixth_reading",
    7: "seventh_reading",
}


def clean_text(value: str) -> str:
    return " ".join(html.unescape(value or "").replace("\xa0", " ").strip().split())


def display_citation(value: str) -> str:
    return clean_text(value).strip(" ;,.").replace("–", "—")


def normalize_citation(value: str) -> str:
    value = display_citation(value).replace("—", "-")
    # Parenthetical Mass conditions describe when an alternative applies; they
    # should not block source preservation for the underlying citation.
    value = re.sub(r"\s*\((?:[^)]*mass|shorter form|optional)[^)]*\)\s*$", "", value, flags=re.I)
    value = re.sub(r"^(cf\.?|see)\s+", "", value, flags=re.I)
    value = re.sub(r"\s+", " ", value)
    return value.lower().strip(" .;,:")


def is_citation_like(value: str) -> bool:
    text = display_citation(value)
    return len(text) <= 160 and bool(re.search(r"\d+\s*[:：]\s*\d+", text))


def reading_number_from_label(label: str) -> int | None:
    label_norm = clean_text(label).lower().replace("–", "-").replace("—", "-")
    match = re.search(r"reading\s+(\d+)", label_norm)
    if match:
        return int(match.group(1))
    match = re.search(r"reading\s+([ivx]+)", label_norm)
    if match:
        return ROMAN_NUMBERS.get(match.group(1))
    if label_norm == "reading" or "reading i" in label_norm:
        return 1
    return None


def page_has_numbered_vigil_readings(soup: BeautifulSoup) -> bool:
    numbers = []
    for heading in soup.find_all(["h3", "h4"], class_="name"):
        number = reading_number_from_label(heading.get_text(" ", strip=True))
        if number is not None:
            numbers.append(number)
    return any(number >= 3 for number in numbers)


def slot_from_label(label: str, previous_slot: str | None, current_reading_number: int | None, multi_reading_page: bool) -> tuple[str | None, int | None]:
    label_clean = clean_text(label)
    label_norm = label_clean.lower().replace("–", "-").replace("—", "-")

    if label_norm in {"or", "or:", "or at afternoon or evening mass"}:
        return previous_slot, current_reading_number

    if "procession with palms" in label_norm and "gospel" in label_norm:
        return "gospel", current_reading_number

    number = reading_number_from_label(label_clean)
    if number is not None:
        return READING_SLOT.get(number, f"reading_{number}"), number

    if label_norm.startswith("responsorial") or label_norm == "psalm":
        if multi_reading_page and current_reading_number is not None:
            return f"responsorial_psalm_{current_reading_number}", current_reading_number
        return "responsorial_psalm", current_reading_number

    if label_norm.startswith("gospel") or label_norm == "gospel":
        return "gospel", current_reading_number

    if label_norm.startswith("epistle"):
        return "epistle", None

    if label_norm.startswith("alleluia"):
        return "alleluia", current_reading_number

    if label_norm.startswith("verse before the gospel") or label_norm.startswith("verse before gospel"):
        return "verse_before_gospel", current_reading_number

    if label_norm.startswith("sequence"):
        return "sequence", current_reading_number

    # A few malformed USCCB headings are themselves citation labels.
    if is_citation_like(label_clean):
        return previous_slot, current_reading_number

    return None, current_reading_number


def citation_texts_for_heading(heading) -> list[str]:
    header = heading.find_parent(class_="content-header") or heading.parent
    address = header.find(class_="address") if header else None
    citations: list[str] = []
    if address:
        for anchor in address.find_all("a"):
            text = display_citation(anchor.get_text(" ", strip=True))
            if is_citation_like(text):
                citations.append(text)
    label = clean_text(heading.get_text(" ", strip=True))
    if not citations and is_citation_like(label):
        citations.append(label)
    return citations


def parse_citations_from_cfm(path: Path) -> dict[str, list[str]]:
    soup = BeautifulSoup(path.read_text(errors="replace"), "html.parser")
    multi_reading_page = page_has_numbered_vigil_readings(soup)
    parsed: dict[str, list[str]] = defaultdict(list)
    previous_slot: str | None = None
    current_reading_number: int | None = None

    for heading in soup.find_all(["h3", "h4"], class_="name"):
        label = clean_text(heading.get_text(" ", strip=True))
        slot, current_reading_number = slot_from_label(
            label, previous_slot, current_reading_number, multi_reading_page
        )
        citations = citation_texts_for_heading(heading)
        if slot and citations:
            seen = {normalize_citation(citation) for citation in parsed[slot]}
            for citation in citations:
                key = normalize_citation(citation)
                if key not in seen:
                    parsed[slot].append(citation)
                    seen.add(key)
            previous_slot = slot
        elif slot and not label.lower().startswith("or"):
            previous_slot = slot

    return dict(parsed)


def slot_alias(slot: str) -> str:
    # Historical schema used both names; rebuild keeps only alleluia.
    return "alleluia" if slot == "alleluia_verse" else slot


def sources_for_matching_existing(existing_items: list[Any], citation: str) -> list[str]:
    wanted = normalize_citation(citation)
    sources: list[str] = ["USCCB"]
    for item in existing_items:
        if not isinstance(item, dict):
            continue
        if normalize_citation(item.get("citation", "")) == wanted:
            for source in item.get("sources", []):
                if source not in sources:
                    sources.append(source)
    return sources


def normalize_existing_by_slot(readings: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    normalized: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for slot, value in readings.items():
        target_slot = slot_alias(slot)
        if isinstance(value, dict):
            items = [value]
        elif isinstance(value, list):
            items = value
        else:
            continue
        for item in items:
            if isinstance(item, dict) and item.get("citation"):
                normalized[target_slot].append(copy.deepcopy(item))
    return dict(normalized)


def rebuild_entry_from_raw(entry: dict[str, Any], raw_path: Path) -> dict[str, Any]:
    rebuilt = copy.deepcopy(entry)
    existing_by_slot = normalize_existing_by_slot(entry.get("readings", {}))
    parsed_by_slot = parse_citations_from_cfm(raw_path)

    new_readings: dict[str, list[dict[str, Any]]] = {}
    slots = list(parsed_by_slot.keys())
    for slot in existing_by_slot:
        if slot not in slots and any("USCCB" not in item.get("sources", []) for item in existing_by_slot[slot]):
            slots.append(slot)

    for slot in slots:
        items: list[dict[str, Any]] = []
        existing_items = existing_by_slot.get(slot, [])
        for citation in parsed_by_slot.get(slot, []):
            items.append({"citation": citation, "sources": sources_for_matching_existing(existing_items, citation)})

        # Preserve non-USCCB cross-source citations that do not match raw USCCB citations.
        raw_keys = {normalize_citation(item["citation"]) for item in items}
        for existing in existing_items:
            existing_sources = existing.get("sources", [])
            existing_key = normalize_citation(existing.get("citation", ""))
            if existing_key and "USCCB" not in existing_sources and existing_key not in raw_keys:
                items.append(copy.deepcopy(existing))

        if items:
            new_readings[slot] = items

    rebuilt["readings"] = new_readings
    rebuilt.pop("mass_idx", None)
    return rebuilt


def raw_path_for_entry(entry: dict[str, Any], date_key: str) -> Path | None:
    url = entry.get("url") or ""
    slug = url.rstrip("/").split("/")[-1]
    if slug:
        candidates = [RAW_DIR / f"{date_key}-{slug}"]
        if not slug.endswith(".cfm"):
            candidates.append(RAW_DIR / f"{date_key}-{slug}.cfm")
        # Some early records stored malformed YYMMDD URLs (e.g. 230131.cfm).
        # Prefer the canonical MMDDYY filename derived from the date before falling back.
        yyyy, mm, dd = date_key.split("-")
        candidates.append(RAW_DIR / f"{date_key}-{mm}{dd}{yyyy[-2:]}.cfm")
        for candidate in candidates:
            if candidate.exists():
                return candidate
    files = list(RAW_DIR.glob(f"{date_key}-*.cfm"))
    if slug:
        slug_base = slug.lower().replace(".cfm", "")
        matches = [path for path in files if slug_base and slug_base in path.name.lower()]
        if len(matches) == 1:
            return matches[0]
    mass = (entry.get("mass") or "").lower()
    if mass and mass != "default":
        matches = [path for path in files if mass in path.name.lower()]
        if len(matches) == 1:
            return matches[0]
    if len(files) == 1:
        return files[0]
    return None


def rebuild_all(readings: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rebuilt: dict[str, Any] = {}
    report: list[dict[str, Any]] = []
    for date_key in sorted(readings):
        entries = readings[date_key]
        if isinstance(entries, dict):
            entries = [entries]
        rebuilt_entries = []
        for index, entry in enumerate(entries):
            raw_path = raw_path_for_entry(entry, date_key)
            if raw_path is None:
                rebuilt_entries.append(copy.deepcopy(entry))
                report.append({"date": date_key, "mass_idx": index, "status": "missing_raw", "url": entry.get("url")})
                continue
            new_entry = rebuild_entry_from_raw(entry, raw_path)
            rebuilt_entries.append(new_entry)
            report.append({
                "date": date_key,
                "mass_idx": index,
                "status": "rebuilt",
                "url": entry.get("url"),
                "raw_file": str(raw_path.relative_to(BASE)),
                "changed": new_entry != entry,
            })
        rebuilt[date_key] = rebuilt_entries
    return rebuilt, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Write rebuilt JSON to data/verification only")
    parser.add_argument("--output", type=Path, default=None, help="Optional output path")
    args = parser.parse_args()

    readings = json.loads(READINGS_FILE.read_text())
    rebuilt, report = rebuild_all(readings)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "rebuild-layer1-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))

    output = args.output
    if output is None:
        output = REPORT_DIR / "readings.rebuilt.json" if args.dry_run else READINGS_FILE
    output.write_text(json.dumps(rebuilt, ensure_ascii=False, indent=2) + "\n")

    total = len(report)
    changed = sum(1 for item in report if item.get("changed"))
    missing = sum(1 for item in report if item.get("status") == "missing_raw")
    print(json.dumps({"total": total, "changed": changed, "missing_raw": missing, "output": str(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
