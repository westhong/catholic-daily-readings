#!/usr/bin/env python3
"""
Fetch the daily liturgical scripture reference from Universalis,
then retrieve 和合本繁體 (cut) and World English Bible text
from api.getbible.net.

Usage: eval $(python3 fetch_daily_reading.py <session>)
  session: office | lauds | daytime | vespers | compline

Outputs shell variable assignments: REF, CHINESE, ENGLISH
"""

import re
import sys
from html import unescape

try:
    import requests
except ImportError:
    requests = None


FALLBACK_REF = "詩篇 23:1"
FALLBACK_ZH = "耶和華是我的牧者，我必不致缺乏。"
FALLBACK_EN = "The LORD is my shepherd; I shall not want."

BOOK_ZH = {
    "Psalm": "詩篇", "Psalms": "詩篇",
    "Genesis": "創世記", "Exodus": "出埃及記", "Leviticus": "利未記",
    "Numbers": "民數記", "Deuteronomy": "申命記", "Joshua": "約書亞記",
    "Judges": "士師記", "Ruth": "路得記", "1Samuel": "撒母耳記上",
    "2Samuel": "撒母耳記下", "1Kings": "列王紀上", "2Kings": "列王紀下",
    "1Chronicles": "歷代志上", "2Chronicles": "歷代志下", "Ezra": "以斯拉記",
    "Nehemiah": "尼希米記", "Esther": "以斯帖記", "Job": "約伯記",
    "Proverbs": "箴言", "Ecclesiastes": "傳道書", "SongofSolomon": "雅歌",
    "Isaiah": "以賽亞書", "Jeremiah": "耶利米書", "Lamentations": "耶利米哀歌",
    "Ezekiel": "以西結書", "Daniel": "但以理書", "Hosea": "何西阿書",
    "Joel": "約珥書", "Amos": "阿摩司書", "Obadiah": "俄巴底亞書",
    "Jonah": "約拿書", "Micah": "彌迦書", "Nahum": "那鴻書",
    "Habakkuk": "哈巴谷書", "Zephaniah": "西番雅書", "Haggai": "哈該書",
    "Zechariah": "撒迦利亞書", "Malachi": "瑪拉基書",
    "Matthew": "馬太福音", "Mark": "馬可福音", "Luke": "路加福音",
    "John": "約翰福音", "Acts": "使徒行傳", "Romans": "羅馬書",
    "1Corinthians": "哥林多前書", "2Corinthians": "哥林多後書",
    "Galatians": "加拉太書", "Ephesians": "以弗所書",
    "Philippians": "腓立比書", "Colossians": "歌羅西書",
    "1Thessalonians": "帖撒羅尼迦前書", "2Thessalonians": "帖撒羅尼迦後書",
    "1Timothy": "提摩太前書", "2Timothy": "提摩太後書",
    "Titus": "提多書", "Philemon": "腓利門書", "Hebrews": "希伯來書",
    "James": "雅各書", "1Peter": "彼得前書", "2Peter": "彼得後書",
    "1John": "約翰一書", "2John": "約翰二書", "3John": "約翰三書",
    "Jude": "猶大書", "Revelation": "啟示錄",
}

BOOK_MAP = {
    "Genesis": 1, "Exodus": 2, "Leviticus": 3, "Numbers": 4, "Deuteronomy": 5,
    "Joshua": 6, "Judges": 7, "Ruth": 8,
    "1Samuel": 9, "2Samuel": 10, "1Kings": 11, "2Kings": 12,
    "1Chronicles": 13, "2Chronicles": 14, "Ezra": 15, "Nehemiah": 16,
    "Tobit": 17, "Judith": 18, "Esther": 19,
    "1Maccabees": 20, "2Maccabees": 21,
    "Job": 22, "Psalm": 19, "Psalms": 19, "Proverbs": 20, "Ecclesiastes": 21,
    "SongofSolomon": 22, "Isaiah": 23, "Jeremiah": 24, "Lamentations": 25,
    "Ezekiel": 26, "Daniel": 27, "Hosea": 28, "Joel": 29, "Amos": 30,
    "Obadiah": 31, "Jonah": 32, "Micah": 33, "Nahum": 34, "Habakkuk": 35,
    "Zephaniah": 36, "Haggai": 37, "Zechariah": 38, "Malachi": 39,
    "Matthew": 40, "Mark": 41, "Luke": 42, "John": 43, "Acts": 44,
    "Romans": 45, "1Corinthians": 46, "2Corinthians": 47, "Galatians": 48,
    "Ephesians": 49, "Philippians": 50, "Colossians": 51,
    "1Thessalonians": 52, "2Thessalonians": 53,
    "1Timothy": 54, "2Timothy": 55, "Titus": 56, "Philemon": 57,
    "Hebrews": 58, "James": 59, "1Peter": 60, "2Peter": 61,
    "1John": 62, "2John": 63, "3John": 64, "Jude": 65, "Revelation": 66,
}


def ref_to_chinese(ref: str) -> str:
    parts = ref.strip().split()
    if not parts:
        return ref
    book_en = parts[0]
    rest = " ".join(parts[1:])
    book_zh = BOOK_ZH.get(book_en, book_en)
    return f"{book_zh} {rest}" if rest else book_zh


def lookup_book(name: str) -> int:
    key = name.replace(" ", "").replace(".", "")
    for k, v in BOOK_MAP.items():
        if k.lower() == key.lower():
            return v
    for k, v in BOOK_MAP.items():
        if key.lower() in k.lower() or k.lower() in key.lower():
            return v
    return 0


def fetch_page(url: str) -> str:
    if requests is None:
        return ""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception:
        return ""


def strip_html(html: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", html))


def parse_gospel(html: str):
    text = strip_html(html)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Gospel") and "Acclamation" not in line:
            parts = line.split()
            if len(parts) >= 3:
                book = parts[1]
                ref_part = parts[2]
                match = re.match(r"(\d+):(\d+)", ref_part)
                if match:
                    return f"{book} {match.group(1)}:{match.group(2)}"
    return None


def parse_responsorial_psalm(html: str):
    text = strip_html(html)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Responsorial Psalm"):
            match = re.search(r"Psalm\s+\d+\s*\((\d+)\)", line)
            if match:
                return f"Psalm {match.group(1)}:1"
            match = re.search(r"Psalm\s+(\d+)", line)
            if match:
                return f"Psalm {match.group(1)}:1"
    return None


def parse_first_psalm(html: str):
    text = strip_html(html)
    for line in text.splitlines():
        line = line.strip()
        match = re.match(r"Psalm\s+\d+\s*\((\d+)\)", line)
        if match:
            return f"Psalm {match.group(1)}:1"
        match = re.match(r"Psalm\s+(\d+)\b", line)
        if match:
            return f"Psalm {match.group(1)}:1"
    return None


def fetch_verse_getbible(ref: str, translation: str) -> str:
    if requests is None or not ref:
        return ""
    parts = ref.strip().split()
    if len(parts) < 2:
        return ""
    book_name = parts[0]
    cv = parts[1]
    cv_parts = cv.split(":")
    if len(cv_parts) < 2:
        return ""
    try:
        chapter = int(cv_parts[0])
        verse = int(cv_parts[1].split("-")[0])
    except ValueError:
        return ""

    book_num = lookup_book(book_name)
    if not book_num:
        return ""

    url = f"https://api.getbible.net/v2/{translation}/{book_num}/{chapter}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        verses = data.get("verses", [])
        for item in verses:
            if item.get("verse") == verse:
                text = item.get("text", "").strip()
                text = re.sub(r"^（[^）]*）\s*", "", text)
                return text.strip()
    except Exception:
        pass
    return ""


def main():
    session = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    ref = None

    if requests is not None:
        mass_html = fetch_page("https://universalis.com/mass.htm")

        if session == "lauds":
            ref = parse_gospel(mass_html)
        elif session == "daytime":
            ref = parse_responsorial_psalm(mass_html)
        elif session == "vespers":
            ref = parse_first_psalm(fetch_page("https://universalis.com/vespers.htm"))
        elif session == "compline":
            ref = parse_first_psalm(fetch_page("https://universalis.com/compline.htm"))
        elif session == "office":
            ref = parse_first_psalm(fetch_page("https://universalis.com/readings.htm"))

    if not ref:
        ref = FALLBACK_REF

    zh = fetch_verse_getbible(ref, "cut") or FALLBACK_ZH
    en = fetch_verse_getbible(ref, "web") or FALLBACK_EN
    zh = zh.replace("\n", " ").strip()
    en = en.replace("\n", " ").strip()
    ref_zh = ref_to_chinese(ref)

    def q(text: str) -> str:
        return text.replace("'", "'\\''")

    print(f"REF='{q(ref_zh)}'")
    print(f"CHINESE='{q(zh)}'")
    print(f"ENGLISH='{q(en)}'")


if __name__ == "__main__":
    main()
