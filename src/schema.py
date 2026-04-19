"""
Schema: DailyReadingRecord — 每日讀經記錄標準格式

Core concept: Lectionary Number is the primary key.
All sources align by this number.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


# ─── Book Name Mappings ─────────────────────────────────────────────────────

# USCCB book name → FHL abbreviation
USCCB_BOOK_TO_FHL = {
    "psalm": "詩",
    "psalms": "詩",
    "john": "約",
    "acts": "徒",
    "matthew": "太",
    "mark": "可",
    "luke": "路",
    "romans": "羅",
    "1corinthians": "林前",
    "2corinthians": "林後",
    "ephesians": "弗",
    "philippians": "斐",
    "colossians": "哥",
    "1thessalonians": "得前",
    "2thessalonians": "得後",
    "1timothy": "弟前",
    "2timothy": "弟後",
    "titus": "弟",
    "philemon": "費",
    "hebrews": "希",
    "james": "雅",
    "1peter": "伯前",
    "2peter": "伯後",
    "1john": "若一",
    "2john": "若二",
    "3john": "若三",
    "jude": "猶",
    "revelation": "默",
    "genesis": "創",
    "exodus": "出",
    "leviticus": "肋",
    "numbers": "民",
    "deuteronomy": "申",
    "joshua": "蘇",
    "judges": "民",
    "ruth": "盧",
    "1samuel": "撒上",
    "2samuel": "撒下",
    "1kings": "列上",
    "2kings": "列下",
    "1chronicles": "編上",
    "2chronicles": "編下",
    "ezra": "厄上",
    "nehemiah": "厄下",
    "tobit": "多",
    "judith": "民",
    "esther": "艾",
    "job": "約伯",
    "proverbs": "箴",
    "ecclesiastes": "訓",
    "song of songs": "歌",
    "isaiah": "依",
    "jeremiah": "耶",
    "lamentations": "哀",
    "ezekiel": "則",
    "daniel": "達",
    "hosea": "歐",
    "joel": "岳",
    "amos": "亞",
    "obadiah": "納",
    "jonah": "納",
    "micah": "米",
    "nahum": "納",
    "habakkuk": "哈",
    "zephaniah": "索",
    "haggai": "蓋",
    "zechariah": "匝",
    "malachi": "瑪",
}

# USCCB book name → Full Chinese book name (Traditional)
USCCB_BOOK_TO_FULL_ZH = {
    "psalm": "聖詠",
    "psalms": "聖詠",
    "john": "若望福音",
    "acts": "宗徒大事錄",
    "matthew": "瑪竇福音",
    "mark": "馬爾谷福音",
    "luke": "路加福音",
    "romans": "羅馬書",
    "1corinthians": "格林多前書",
    "2corinthians": "格林多後書",
    "ephesians": "厄弗所書",
    "philippians": "斐理伯書",
    "colossians": "哥羅森書",
    "1thessalonians": "得撒洛尼前書",
    "2thessalonians": "得撒洛尼後書",
    "1timothy": "弟茂德前書",
    "2timothy": "弟茂德後書",
    "titus": "弟铎书",
    "philemon": "費肋孟書",
    "hebrews": "希伯來書",
    "james": "雅各伯書",
    "1peter": "伯多祿前書",
    "2peter": "伯多祿後書",
    "1john": "若望一書",
    "2john": "若望二書",
    "3john": "若望三書",
    "jude": "猶達書",
    "revelation": "若望默示錄",
    "genesis": "創世記",
    "exodus": "出谷紀",
    "leviticus": "肋未紀",
    "numbers": "戶籍紀",
    "deuteronomy": "申命紀",
    "joshua": "若蘇厄書",
    "judges": "民長紀",
    "ruth": "路得紀",
    "1samuel": "撒慕爾紀上",
    "2samuel": "撒慕爾紀下",
    "1kings": "列王紀上",
    "2kings": "列王紀下",
    "1chronicles": "編年紀上",
    "2chronicles": "編年紀下",
    "ezra": "厄斯德拉上",
    "nehemiah": "厄斯德拉下",
    "tobit": "多俾亞傳",
    "esther": "艾斯德爾傳",
    "job": "約伯傳",
    "proverbs": "箴言",
    "ecclesiastes": "訓道篇",
    "song of songs": "雅歌",
    "isaiah": "依撒意亞",
    "jeremiah": "耶肋米亞",
    "lamentations": "哀歌",
    "ezekiel": "厄則克耳",
    "daniel": "達尼爾",
    "hosea": "歐瑟亞",
    "joel": "岳厄爾",
    "amos": "亞毛斯",
    "obadiah": "約纳",
    "jonah": "约纳",
    "micah": "米該亞",
    "nahum": "納鴻",
    "habakkuk": "哈巴谷",
    "zephaniah": "索福尼亞",
    "haggai": "哈蓋",
    "zechariah": "匝加利亞",
    "malachi": "瑪拉基亞",
}


def usccb_to_fhl(book_en: str) -> str:
    """Convert USCCB English book name to FHL abbreviation."""
    return USCCB_BOOK_TO_FHL.get(book_en.lower(), "")


def usccb_to_full_zh(book_en: str) -> str:
    """Convert USCCB English book name to full Traditional Chinese name."""
    return USCCB_BOOK_TO_FULL_ZH.get(book_en.lower(), book_en)


# ─── Data Models ─────────────────────────────────────────────────────────────

@dataclass
class BibleReference:
    book_en: str       # "Acts"
    book_fhl: str      # "徒"
    book_full_zh: str  # "宗徒大事錄"
    chapter: int
    verse_range: str   # "1-7"


@dataclass
class BibleTexts:
    zh_trad: str   # 思高譯本 Traditional Chinese
    zh_simpl: str  # Simplified Chinese (converted)


@dataclass
class Reading:
    type: str            # "first_reading" | "psalm" | "alleluia" | "gospel"
    reference: BibleReference
    bible_texts: BibleTexts
    alleluia_verse: Optional[str]  # For alleluia type without reference


@dataclass
class Source:
    source_id: str
    source_name_en: str
    source_name_zh: str
    source_uri: str
    license: str
    license_detail: str
    lectionary_ref: int
    data: dict


@dataclass
class Translation:
    translation_id: str
    translation_name_en: str
    translation_name_zh: str
    source_uri: str
    language: str   # "zh_trad"
    license: str
    license_detail: str


@dataclass
class Metadata:
    sources: list[Source]
    translations: list[Translation]
    generated_at: str   # ISO8601 UTC
    schema_version: str


@dataclass
class DailyReadingRecord:
    date: str           # ISO8601 date: "2026-04-18"
    weekday: str         # "星期六"
    feast_name: str      # "Saturday of the Second Week of Easter"
    feast_name_zh: str  # "復活期第二周星期六"
    lectionary_number: int
    liturgical_year: str
    liturgical_year_zh: str
    readings: list[Reading]
    metadata: Metadata

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "weekday": self.weekday,
            "feast_name": self.feast_name,
            "feast_name_zh": self.feast_name_zh,
            "lectionary_number": self.lectionary_number,
            "liturgical_year": self.liturgical_year,
            "liturgical_year_zh": self.liturgical_year_zh,
            "readings": [
                {
                    "type": r.type,
                    "reference": {
                        "book_en": r.reference.book_en,
                        "book_fhl": r.reference.book_fhl,
                        "book_full_zh": r.reference.book_full_zh,
                        "chapter": r.reference.chapter,
                        "verse_range": r.reference.verse_range,
                    },
                    "bible_texts": {
                        "zh_trad": r.bible_texts.zh_trad,
                        "zh_simpl": r.bible_texts.zh_simpl,
                    },
                    "alleluia_verse": r.alleluia_verse,
                }
                for r in self.readings
            ],
            "metadata": {
                "sources": [
                    {
                        "source_id": s.source_id,
                        "source_name_en": s.source_name_en,
                        "source_name_zh": s.source_name_zh,
                        "source_uri": s.source_uri,
                        "license": s.license,
                        "license_detail": s.license_detail,
                        "lectionary_ref": s.lectionary_ref,
                        "data": s.data,
                    }
                    for s in self.metadata.sources
                ],
                "translations": [
                    {
                        "translation_id": t.translation_id,
                        "translation_name_en": t.translation_name_en,
                        "translation_name_zh": t.translation_name_zh,
                        "source_uri": t.source_uri,
                        "language": t.language,
                        "license": t.license,
                        "license_detail": t.license_detail,
                    }
                    for t in self.metadata.translations
                ],
                "generated_at": self.metadata.generated_at,
                "schema_version": self.metadata.schema_version,
            },
        }
