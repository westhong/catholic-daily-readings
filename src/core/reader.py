"""
Core reader — assembles DailyReadingRecord from multiple sources.

Architecture:
  USCCB (metadata) → schema (reference) → FHL (bible text) → DailyReadingRecord
"""

import json
from datetime import date, datetime
from typing import Optional

from ..schema import (
    DailyReadingRecord,
    Reading,
    BibleReference,
    BibleTexts,
    Source,
    Translation,
    Metadata,
    usccb_to_fhl,
    usccb_to_full_zh,
)
from ..sources import usccb as usccb_source
from ..sources import fhl as fhl_source


# ─── Liturgical Year ─────────────────────────────────────────────────────────

LITURGICAL_PERIODS: list[tuple[str, str, list[tuple[int, int]]]] = [
    # (en_name, zh_name, [(month, day), ...])
    ("Advent", "將臨期", [
        (11, 30), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5),
        (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11),
        (12, 12), (12, 13), (12, 14), (12, 15), (12, 16), (12, 17),
        (12, 18), (12, 19), (12, 20), (12, 21), (12, 22), (12, 23),
        (12, 24),
    ]),
    ("Christmas Season", "聖誕期", [
        (12, 25), (12, 26), (12, 27), (12, 28), (12, 29),
        (12, 30), (12, 31), (1, 1), (1, 2), (1, 3), (1, 4),
        (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
        (1, 11), (1, 12), (1, 13),
    ]),
    ("Lent", "四旬期", [
        (2, 18), (2, 19), (2, 20), (2, 21), (2, 22), (2, 23),
        (2, 24), (2, 25), (2, 26), (2, 27), (2, 28), (3, 1),
        (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
        (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (3, 13),
        (3, 14), (3, 15), (3, 16), (3, 17), (3, 18), (3, 19),
        (3, 20), (3, 21), (3, 22), (3, 23), (3, 24), (3, 25),
        (3, 26), (3, 27), (3, 28), (3, 29), (3, 30), (3, 31),
        (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
    ]),
    ("Easter Season", "復活期", [
        (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (4, 12),
        (4, 13), (4, 14), (4, 15), (4, 16), (4, 17), (4, 18),
        (4, 19), (4, 20), (4, 21), (4, 22), (4, 23), (4, 24),
        (4, 25), (4, 26), (4, 27), (4, 28), (4, 29), (4, 30),
        (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
        (5, 7), (5, 8), (5, 9), (5, 10), (5, 11), (5, 12),
        (5, 13), (5, 14), (5, 15), (5, 16), (5, 17), (5, 18),
        (5, 19), (5, 20), (5, 21), (5, 22), (5, 23), (5, 24),
        (5, 25), (5, 26), (5, 27), (5, 28), (5, 29), (5, 30),
        (5, 31), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
        (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 11),
        (6, 12), (6, 13), (6, 14),
    ]),
    ("Ordinary Time", "常年 期", []),
]

FEAST_NAME_TRANSLATIONS: dict[str, str] = {
    "Easter Sunday": "復活節",
    "Palm Sunday of the Lord's Passion": "聖枝主日",
    "Good Friday": "耶穌受難日",
    "Holy Thursday": "聖週四",
    "Christmas": "聖誕節",
    "Immaculate Conception": "聖母始胎無染原罪瞻禮",
    "Assumption": "聖母升天瞻禮",
    "Nativity of the Lord": "耶穌聖誕",
    "Epiphany": "主顯節",
    "Baptism of the Lord": "耶穌受洗節",
    "Trinity Sunday": "天主聖三節",
    "Christ the King": "耶穌基督普世君王節",
    # Specific Easter season days
    "Saturday of the Second Week of Easter": "復活期第二周星期六",
    "Second Sunday of Easter": "復活期第二主日",
    "Monday of the Second Week of Easter": "復活期第二周星期一",
    "Tuesday of the Second Week of Easter": "復活期第二周星期二",
    "Wednesday of the Second Week of Easter": "復活期第二周星期三",
    "Thursday of the Second Week of Easter": "復活期第二周星期四",
    "Friday of the Second Week of Easter": "復活期第二周星期五",
}


def get_liturgical_period(d: date) -> tuple[str, str]:
    """Return (liturgical_period_en, liturgical_period_zh) for a given date."""
    key = (d.month, d.day)
    for en, zh, ranges in LITURGICAL_PERIODS:
        if key in ranges:
            return en, zh
    return "Ordinary Time", "常年 期"


def translate_feast_name(feast_en: str) -> str:
    """Translate feast name to Traditional Chinese."""
    # Check direct mapping first
    if feast_en in FEAST_NAME_TRANSLATIONS:
        return FEAST_NAME_TRANSLATIONS[feast_en]

    # Pattern-based fallback for "Week X of Easter" style names
    # e.g. "Saturday of the Second Week of Easter"
    import re
    m = re.match(r"(\w+) of the (\w+) Week of (\w+)", feast_en)
    if m:
        day, week_num, period = m.groups()
        day_zh = {"Sunday": "主日", "Monday": "星期一", "Tuesday": "星期二",
                  "Wednesday": "星期三", "Thursday": "星期四",
                  "Friday": "星期五", "Saturday": "星期六"}.get(day, day)
        week_zh = {"First": "第一", "Second": "第二", "Third": "第三",
                   "Fourth": "第四", "Fifth": "第五", "Sixth": "第六"}.get(week_num, week_num)
        period_zh = {"Easter": "復活期", "Lent": "四旬期",
                     "Advent": "將臨期", "Christmas": "聖誕期"}.get(period, period)
        return f"{period_zh}{week_zh}周{day_zh}"

    # Generic word replacement
    result = feast_en
    replacements = [
        ("Sunday", "主日"), ("Saturday", "星期六"), ("Monday", "星期一"),
        ("Tuesday", "星期二"), ("Wednesday", "星期三"), ("Thursday", "星期四"),
        ("Friday", "星期五"), ("Easter", "復活節"), ("Christmas", "聖誕節"),
        ("Lent", "四旬期"), ("Advent", "將臨期"), ("Week", "周"),
        ("Second", "第二"), ("Third", "第三"), ("Fourth", "第四"),
        ("First", "第一"), ("of the", ""), ("of", "的"), ("the", ""),
    ]
    for en_word, zh_word in replacements:
        result = result.replace(en_word, zh_word)
    return ' '.join(result.split())


def build_daily_record(target_date: Optional[date] = None) -> DailyReadingRecord:
    """
    Build a complete DailyReadingRecord for a given date.
    """
    if target_date is None:
        target_date = date.today()

    # Step 1: Scrape USCCB
    usccb_meta = usccb_source.scrape(target_date)

    # Step 2: Build readings with Bible text
    readings: list[Reading] = []
    for usccb_r in usccb_meta.readings:
        fhl_abbrev = usccb_to_fhl(usccb_r.book_en)
        book_full_zh = usccb_to_full_zh(usccb_r.book_en)

        # Fetch Bible text from FHL if we have a valid reference
        if fhl_abbrev and usccb_r.chapter > 0 and usccb_r.verse_range:
            zh_trad = fhl_source.fetch_verse(
                fhl_abbrev,
                usccb_r.chapter,
                usccb_r.verse_range
            )
        else:
            zh_trad = ""

        zh_simpl = fhl_source.zh_trad_to_simpl(zh_trad)

        ref = BibleReference(
            book_en=usccb_r.book_en,
            book_fhl=fhl_abbrev,
            book_full_zh=book_full_zh,
            chapter=usccb_r.chapter,
            verse_range=usccb_r.verse_range
        )
        texts = BibleTexts(zh_trad=zh_trad, zh_simpl=zh_simpl)
        readings.append(Reading(
            type=usccb_r.type,
            reference=ref,
            bible_texts=texts,
            alleluia_verse=None
        ))

    # Step 3: Liturgical period
    lit_en, lit_zh = get_liturgical_period(target_date)

    # Step 4: Feast name
    feast_zh = translate_feast_name(usccb_meta.feast_name)

    # Step 5: Metadata
    usccb_source_obj = Source(
        source_id="usccb",
        source_name_en="USCCB Daily Bible Reading",
        source_name_zh="美國主教團每日讀經",
        source_uri=usccb_source.USCCB_URL,
        license="private-use-only",
        license_detail=usccb_meta.license_detail,
        lectionary_ref=usccb_meta.lectionary_number,
        data={}
    )

    fhl_translation = Translation(
        translation_id="fhl_ofm",
        translation_name_en="Studium Biblicum Franciscanum (Sikong)",
        translation_name_zh="思高學會譯本",
        source_uri=fhl_source.FHL_URI,
        language="zh_trad",
        license="research-use",
        license_detail="Free for research use; commercial use requires permission."
    )

    metadata = Metadata(
        sources=[usccb_source_obj],
        translations=[fhl_translation],
        generated_at=datetime.utcnow().isoformat() + "Z",
        schema_version="1.0"
    )

    return DailyReadingRecord(
        date=target_date.isoformat(),
        weekday=usccb_meta.weekday,
        feast_name=usccb_meta.feast_name,
        feast_name_zh=feast_zh,
        lectionary_number=usccb_meta.lectionary_number,
        liturgical_year=lit_en,
        liturgical_year_zh=lit_zh,
        readings=readings,
        metadata=metadata
    )


def save_record(record: DailyReadingRecord, path: str) -> None:
    """Save a DailyReadingRecord to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)
