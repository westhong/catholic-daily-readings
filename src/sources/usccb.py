"""
USCCB Source — scrapes daily reading metadata from bible.usccb.org

What it scrapes:
- Date (from URL param), weekday (computed from date)
- Feast name (4th h2 on page)
- Lectionary number
- Reading references: Reading 1, Responsorial Psalm, Alleluia, Gospel

Alleluia note: USCCB HTML for Alleluia has a malformed <a> tag.
The anchor text is literally "'>" which is not a real verse reference.
We detect this and return "Alleluia" type without a reference.

License: private-use-only (USCCB/Coppervar)
URI: https://bible.usccb.org/daily-bible-reading
"""

import re
import urllib.request
from dataclasses import dataclass
from datetime import date
from typing import Optional


USCCB_URL = "https://bible.usccb.org/daily-bible-reading"
_USCCB_LECTNUMBER_RE = re.compile(r"Lectionary:\s*(\d+)")
_USCCB_H2_RE = re.compile(r"<h2[^>]*>([^<]+)</h2>")
_USCCB_SECTION_RE = re.compile(
    r'<h3 class="name">\s*([^<]+?)\s*</h3>\s*<div class="address">\s*(.*?)\s*</div>',
    re.DOTALL,
)
_USCCB_A_RE = re.compile(r'<a[^>]*>([^<]*)</a>')
_USCCB_HREF_RE = re.compile(r'<a[^>]*href="([^"]*)"')
# Malformed Alleluia anchor text marker
_INVALID_ALLHREF_RE = re.compile(r"orgroute\?|nolink", re.IGNORECASE)


# Book name to FHL abbreviation
USCCB_BOOK_TO_FHL: dict[str, str] = {
    "Genesis": "創",
    "Exodus": "出",
    "Leviticus": "肋",
    "Numbers": "戶",
    "Deuteronomy": "申",
    "Joshua": "蘇",
    "Judges": "民",
    "Ruth": "盧",
    "1 Samuel": "撒上",
    "2 Samuel": "撒下",
    "1 Kings": "列上",
    "2 Kings": "列下",
    "1 Chronicles": "編上",
    "2 Chronicles": "編下",
    "Ezra": "厄上",
    "Nehemiah": "厄下",
    "Tobit": "多",
    "Judith": "民",
    "Esther": "艾",
    "Job": "約",
    "Psalms": "詩",
    "Psalm": "詩",
    "Proverbs": "箴",
    "Ecclesiastes": "訓",
    "Song of Songs": "歌",
    "Isaiah": "依",
    "Jeremiah": "耶",
    "Lamentations": "哀",
    "Ezekiel": "則",
    "Daniel": "達",
    "Hosea": "歐",
    "Joel": "岳",
    "Amos": "亞",
    "Obadiah": "鴻",
    "Jonah": "納",
    "Micah": "米",
    "Nahum": "納",
    "Habakkuk": "哈",
    "Zephaniah": "索",
    "Haggai": "蓋",
    "Zechariah": "匝",
    "Malachi": "瑪",
    "Matthew": "瑪",
    "Mark": "谷",
    "Luke": "路",
    "John": "若",
    "Acts": "宗",
    "Romans": "羅",
    "1 Corinthians": "格前",
    "2 Corinthians": "格後",
    "Galatians": "迦",
    "Ephesians": "弗",
    "Philippians": "斐",
    "Colossians": "哥",
    "1 Thessalonians": "得前",
    "2 Thessalonians": "得後",
    "1 Timothy": "弟前",
    "2 Timothy": "弟後",
    "Titus": "弟",
    "Philemon": "費",
    "Hebrews": "希",
    "James": "雅",
    "1 Peter": "伯前",
    "2 Peter": "伯後",
    "1 John": "若一",
    "2 John": "若二",
    "3 John": "若三",
    "Jude": "猶",
    "Revelation": "默",
}


def scrape(target_date: date) -> "USCCBMeta":
    """
    Scrape USCCB daily reading page for a given date.
    Returns USCCBMeta with feast name, weekday, lectionary number, and readings.
    """
    url = f"{USCCB_URL}?date={target_date.isoformat()}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    # Lectionary number
    lec_match = _USCCB_LECTNUMBER_RE.search(html)
    lectionary_number = int(lec_match.group(1)) if lec_match else 0

    # Feast name — 4th h2 on page
    h2_titles = _USCCB_H2_RE.findall(html)
    feast_name = h2_titles[3].strip() if len(h2_titles) > 3 else ""

    # Weekday — compute from date
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekday_names[target_date.weekday()]

    # Reading sections
    sections = _USCCB_SECTION_RE.findall(html)
    readings: list[USCCBReading] = []

    for section_name_raw, address_html in sections:
        section_name = section_name_raw.strip()
        type_ = _section_type(section_name)

        # Extract anchor text and href
        link_texts = _USCCB_A_RE.findall(address_html)
        hrefs = _USCCB_HREF_RE.findall(address_html)

        if not link_texts or not hrefs:
            continue

        link_text = link_texts[0].strip()
        href = hrefs[0].strip()

        # Detect malformed Alleluia
        if _INVALID_ALLHREF_RE.search(href) or link_text in ("", "'>", " "):
            readings.append(USCCBReading(
                type=type_,
                book_en="",
                chapter=0,
                verse_range="",
                href="",
            ))
            continue

        # Parse reference string like "Acts 6:1-7"
        ref_text = link_text
        ref = _parse_ref(ref_text)
        if ref is None:
            continue

        readings.append(USCCBReading(
            type=type_,
            book_en=ref["book"],
            chapter=ref["chapter"],
            verse_range=ref["verse"],
            href=href,
        ))

    # License detail
    license_detail = (
        "Copyright © Confraternity of Christian Doctrine. "
        "Personal/parish use free; redistribution requires permission."
    )

    return USCCBMeta(
        date=target_date.isoformat(),
        weekday=weekday,
        feast_name=feast_name,
        lectionary_number=lectionary_number,
        readings=readings,
        license_detail=license_detail,
    )


def _section_type(name: str) -> str:
    """Map section name to reading type."""
    name = name.lower()
    if "reading 1" in name:
        return "first_reading"
    elif "responsorial psalm" in name or "psalm" in name:
        return "psalm"
    elif "alleluia" in name:
        return "alleluia"
    elif "gospel" in name:
        return "gospel"
    elif "second reading" in name:
        return "second_reading"
    else:
        return name


def _parse_ref(text: str) -> Optional[dict]:
    """
    Parse a reference string like "Acts 6:1-7" or "Psalm 33:1-2, 4-5, 18-19".
    Returns {"book": "Acts", "chapter": 6, "verse": "1-7"} or None.
    """
    # Pattern: Book Chapter:VerseRange
    m = re.match(r"(.+?)\s+(\d+):(.+)", text)
    if not m:
        return None
    return {
        "book": m.group(1).strip(),
        "chapter": int(m.group(2)),
        "verse": m.group(3).strip(),
    }


@dataclass
class USCCBReading:
    """A single reading scraped from USCCB."""
    type: str
    book_en: str
    chapter: int
    verse_range: str
    href: str


@dataclass
class USCCBMeta:
    """All metadata scraped from USCCB for one day."""
    date: str
    weekday: str
    feast_name: str
    lectionary_number: int
    readings: list[USCCBReading]
    license_detail: str
