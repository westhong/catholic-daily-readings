"""
FHL Source — fetches Chinese Bible text from bible.fhl.net (思高譯本)

API endpoint:
  https://bible.fhl.net/json/qb.php?chineses={書名簡稱}&chap={章}&sec={節}&version=ofm&gb=0

License: research-use — Free for research use; commercial use requires permission.
URI: https://bible.fhl.net/
"""

import re
import urllib.request
import urllib.parse
from html import unescape

FHL_API = "https://bible.fhl.net/json/qb.php"
FHL_URI = "https://bible.fhl.net/"

# USCCB book name → FHL book abbreviation
USCCB_TO_FHL = {
    "psalm": "詩",
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
    "job": "約",
    "psalms": "詩",
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
    "obadiah": "鴻",
    "jonah": "納",
    "micah": "米",
    "nahum": "納",
    "habakkuk": "哈",
    "zephaniah": "索",
    "haggai": "蓋",
    "zechariah": "匝",
    "malachi": "瑪",
}

# FHL abbreviation → Full Traditional Chinese book name
FHL_TO_ZH = {
    "詩": "詩篇",
    "約": "若望福音",
    "徒": "宗徒大事錄",
    "太": "瑪竇福音",
    "可": "馬爾谷福音",
    "路": "路加福音",
    "羅": "羅馬書",
    "林前": "格林多前書",
    "林後": "格林多後書",
    "弗": "厄弗所書",
    "斐": "斐理伯書",
    "哥": "哥羅森書",
    "得前": "得撒洛尼前書",
    "得後": "得撒洛尼後書",
    "弟前": "弟茂德前書",
    "弟後": "弟茂德後書",
    "弟": "弟铎书",
    "費": "費肋孟書",
    "希": "希伯來書",
    "雅": "雅各伯書",
    "伯前": "伯多祿前書",
    "伯後": "伯多祿後書",
    "若一": "若望一書",
    "若二": "若望二書",
    "若三": "若望三書",
    "猶": "猶達書",
    "默": "若望默示錄",
    "創": "創世記",
    "出": "出谷紀",
    "肋": "肋未紀",
    "民": "戶籍紀",
    "申": "申命紀",
    "蘇": "若蘇厄書",
    "撒上": "撒慕爾紀上",
    "撒下": "撒慕爾紀下",
    "列上": "列王紀上",
    "列下": "列王紀下",
    "編上": "編年紀上",
    "編下": "編年紀下",
    "厄上": "厄斯德拉上",
    "厄下": "厄斯德拉下",
    "多": "多俾亞傳",
    "艾": "艾斯德爾傳",
    "約": "約伯傳",
    "箴": "箴言",
    "訓": "訓道篇",
    "歌": "雅歌",
    "依": "依撒意亞",
    "耶": "耶肋米亞",
    "哀": "哀歌",
    "則": "厄則克耳",
    "達": "達尼爾",
    "歐": "歐瑟亞",
    "岳": "岳厄爾",
    "亞": "亞毛斯",
    "鴻": "納崩",
    "納": "納鴻",
    "米": "米該亞",
    "哈": "哈巴谷",
    "索": "索福尼亞",
    "蓋": "哈蓋",
    "匝": "匝加利亞",
    "瑪": "瑪拉基亞",
}


def fetch_verse(fhl_abbrev: str, chapter: int, verse_range: str) -> str:
    """
    Fetch a verse range from FHL (思高譯本 ofm).

    Args:
        fhl_abbrev: FHL book abbreviation, e.g. "詩", "徒", "若"
        chapter: Chapter number
        verse_range: Verse range, e.g. "1-7", "1-2, 4-5, 18-19"

    Returns:
        Concatenated verse text in Traditional Chinese.
    """
    # Parse verse_range into individual parts
    parts = re.split(r',\s*', verse_range)
    all_texts: list[str] = []

    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = start.strip()
            end = end.strip()
            sec = f"{start}-{end}"
        else:
            sec = part

        params = urllib.parse.urlencode({
            "chineses": fhl_abbrev,
            "chap": str(chapter),
            "sec": sec,
            "version": "ofm",
            "gb": "0"
        })
        url = f"{FHL_API}?{params}"

        text = _fetch_single(url)
        if text:
            all_texts.append(text)

    return '\n'.join(all_texts)


def _fetch_single(url: str) -> str:
    """Fetch and parse a single verse/verse range from FHL API."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; CatholicAssistantBot/1.0)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            import json
            data = json.loads(resp.read().decode("utf-8", errors="replace"))

        records = data.get("record", [])
        if not records:
            return ""

        # Extract text from each record
        parts: list[str] = []
        for record in records:
            raw = record.get("bible_text", "")
            # Clean HTML per skill notes:
            # 1. Remove h2 block tags first
            raw = re.sub(r'<h2[^>]*>.*?</h2>', '', raw, flags=re.DOTALL)
            # 2. Strip all remaining tags
            raw = re.sub(r'<[^>]+>', '', raw)
            # 3. Unescape HTML entities
            raw = unescape(raw)
            # 4. Clean whitespace
            raw = re.sub(r' +\n', '\n', raw)
            raw = re.sub(r'\n+', '\n', raw).strip()
            if raw:
                parts.append(raw)

        return '\n'.join(parts)
    except Exception:
        return ""


def zh_trad_to_simpl(zh_trad: str) -> str:
    """
    Simple Traditional → Simplified Chinese converter.
    Uses opencc if available, falls back to basic character mapping.
    For production, install opencc: pip install opencc
    """
    try:
        import opencc
        converter = opencc.OpenCC('t2s')
        return converter.convert(zh_trad)
    except ImportError:
        pass

    # Basic fallback mapping for common TC → SC conversions
    mapping = {
        "義": "义", "們": "们", "應": "应", "踴": "踊", "躍": "跃",
        "歡": "欢", "稱": "称", "謝": "谢", "絃": "弦", "頌": "颂",
        "語": "语", "彈": "弹", "賢": "贤", "寶": "宝", "龍": "龙",
        "區": "区", "愛": "爱", "護": "护", "關": "关", "雙": "双",
        "請": "请", "這種": "这种", "個": "个", "這": "这", "為": "为",
        "們": "们", "經": "经", "常": "常", "聖": "圣", "神": "神",
        "主": "主", "耶穌": "耶稣", "基督": "基督", "教會": "教会",
        "恩典": "恩典", "救恩": "救恩", "祈禱": "祈祷", "阿們": "阿门",
        "的生命": "的生命", "我已經": "我已经", "你的": "你的",
    }
    result = zh_trad
    for tc, sc in mapping.items():
        result = result.replace(tc, sc)
    return result
