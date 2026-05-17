import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.rebuild_layer1_from_layer0 import (  # noqa: E402
    parse_citations_from_cfm,
    rebuild_entry_from_raw,
)

RAW = ROOT / "data" / "usccb-calendar" / "raw"


def test_parse_full_citation_ranges_from_raw_cfm():
    raw = RAW / "2026-04-19-041926.cfm"

    parsed = parse_citations_from_cfm(raw)

    assert parsed["first_reading"] == ["Acts 2:14, 22-33"]
    assert parsed["responsorial_psalm"] == ["Psalm 16:1-2, 5, 7-8, 9-10, 11"]
    assert parsed["second_reading"] == ["1 Peter 1:17-21"]
    assert parsed["alleluia"] == ["Cf. Luke 24:32"]
    assert parsed["gospel"] == ["Luke 24:13-35"]


def test_rebuild_entry_replaces_usccb_citation_but_preserves_cross_source_sources():
    raw = RAW / "2026-04-02-040226-Supper.cfm"
    existing = {
        "date": "2026-04-02",
        "url": "https://bible.usccb.org/bible/readings/040226-Supper.cfm",
        "lectionary_number": 39,
        "feast": "Holy Thursday-Evening Mass of the Lord's Supper",
        "mass": "Supper",
        "readings": {
            "first_reading": [{"citation": "Exodus 12:1-8", "sources": ["USCCB"]}],
            "responsorial_psalm": [{"citation": "Psalm 116:12-13", "sources": ["USCCB"]}],
            "second_reading": [{"citation": "1 Corinthians 11:23-26", "sources": ["USCCB", "CatholicGallery", "CatholicOnline"]}],
            "gospel": [{"citation": "John 13:1-15", "sources": ["USCCB", "CatholicGallery", "CatholicOnline"]}],
        },
    }

    rebuilt = rebuild_entry_from_raw(existing, raw)

    assert rebuilt["readings"]["first_reading"] == [
        {"citation": "Exodus 12:1-8, 11-14", "sources": ["USCCB"]}
    ]
    assert rebuilt["readings"]["responsorial_psalm"] == [
        {"citation": "Psalm 116:12-13, 15-16bc, 17-18", "sources": ["USCCB"]}
    ]
    assert rebuilt["readings"]["second_reading"] == [
        {"citation": "1 Corinthians 11:23-26", "sources": ["USCCB", "CatholicGallery", "CatholicOnline"]}
    ]
    assert rebuilt["readings"]["gospel"] == [
        {"citation": "John 13:1-15", "sources": ["USCCB", "CatholicGallery", "CatholicOnline"]}
    ]


def test_parse_easter_vigil_numbered_readings_and_psalms():
    raw = RAW / "2025-04-19-041925.cfm"

    parsed = parse_citations_from_cfm(raw)

    assert parsed["first_reading"] == ["Genesis 1:1—2:2", "Genesis 1:1, 26-31a"]
    assert parsed["second_reading"] == ["Genesis 22:1-18", "Genesis 22:1-2, 9a, 10-13, 15-18"]
    assert parsed["third_reading"] == ["Exodus 14:15—15:1"]
    assert parsed["seventh_reading"] == ["Ezekiel 36:16-17a, 18-28"]
    assert parsed["epistle"] == ["Romans 6:3-11"]
    assert parsed["gospel"] == ["Luke 24:1-12"]
    assert parsed["responsorial_psalm_1"] == ["Psalm 104:1-2, 5-6, 10, 12, 13-14, 24, 35", "Psalm 33:4-5, 6-7, 12-13, 20 and 22"]
    assert parsed["responsorial_psalm_7"] == ["Psalm 42:3, 5; 43:3, 4", "Isaiah 12:2-3, 4bcd, 5-6", "Psalm 51:12-13, 14-15, 18-19"]
    assert parsed["responsorial_psalm"] == ["Psalm 118:1-2, 16-17, 22-23"]
