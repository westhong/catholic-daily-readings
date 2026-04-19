#!/usr/bin/env python3
"""
Weekly Sunday Readings Guide (中文導讀)
Fetches next Sunday's Mass readings from Universalis,
generates a Chinese commentary via xAI/Grok,
and sends text to Telegram.
"""

import re
import sys
from datetime import datetime, timedelta
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    import requests
except ImportError:
    print("ERROR: requests not installed", file=sys.stderr)
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai not installed", file=sys.stderr)
    sys.exit(1)

ENV_FILE = Path("/home/jarvis/.hermes/.env")
DEFAULT_CHAT_ID = "-1003336338866"
DEFAULT_TOPIC_ID = "17"
TZ = "America/Edmonton"


def read_env_value(key: str) -> str:
    if not ENV_FILE.exists():
        return ""
    for line in ENV_FILE.read_text().splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            return v.strip()
    return ""


BOT_TOKEN = read_env_value("TELEGRAM_BOT_TOKEN")
CHAT_ID = read_env_value("CATHOLIC_CHAT_ID") or DEFAULT_CHAT_ID
TOPIC_ID = read_env_value("CATHOLIC_TOPIC_ID") or DEFAULT_TOPIC_ID
GROK_KEY = read_env_value("XAI_API_KEY") or read_env_value("GROK_API_KEY")

BOOK_ZH = {
    "Genesis": "創世記", "Exodus": "出埃及記", "Leviticus": "利未記", "Numbers": "民數記",
    "Deuteronomy": "申命記", "Joshua": "約書亞記", "Judges": "士師記", "Ruth": "路得記",
    "1Samuel": "撒母耳記上", "2Samuel": "撒母耳記下", "1Kings": "列王紀上", "2Kings": "列王紀下",
    "1Chronicles": "歷代志上", "2Chronicles": "歷代志下", "Ezra": "以斯拉記", "Nehemiah": "尼希米記",
    "Esther": "以斯帖記", "Job": "約伯記", "Psalm": "詩篇", "Psalms": "詩篇",
    "Proverbs": "箴言", "Ecclesiastes": "傳道書", "SongofSolomon": "雅歌",
    "Isaiah": "以賽亞書", "Jeremiah": "耶利米書", "Lamentations": "耶利米哀歌",
    "Ezekiel": "以西結書", "Daniel": "但以理書", "Hosea": "何西阿書", "Joel": "約珥書",
    "Amos": "阿摩司書", "Obadiah": "俄巴底亞書", "Jonah": "約拿書", "Micah": "彌迦書",
    "Nahum": "那鴻書", "Habakkuk": "哈巴谷書", "Zephaniah": "西番雅書", "Haggai": "哈該書",
    "Zechariah": "撒迦利亞書", "Malachi": "瑪拉基書",
    "Matthew": "馬太福音", "Mark": "馬可福音", "Luke": "路加福音", "John": "約翰福音",
    "Acts": "使徒行傳", "Romans": "羅馬書", "1Corinthians": "哥林多前書",
    "2Corinthians": "哥林多後書", "Galatians": "加拉太書", "Ephesians": "以弗所書",
    "Philippians": "腓立比書", "Colossians": "歌羅西書", "1Thessalonians": "帖撒羅尼迦前書",
    "2Thessalonians": "帖撒羅尼迦後書", "1Timothy": "提摩太前書", "2Timothy": "提摩太後書",
    "Titus": "提多書", "Philemon": "腓利門書", "Hebrews": "希伯來書", "James": "雅各書",
    "1Peter": "彼得前書", "2Peter": "彼得後書", "1John": "約翰一書", "2John": "約翰二書",
    "3John": "約翰三書", "Jude": "猶大書", "Revelation": "啟示錄",
    "Tobit": "多俾亞傳", "Judith": "友弟德傳", "Sirach": "德訓篇", "Wisdom": "智慧篇",
    "Baruch": "巴路克書", "1Maccabees": "瑪加伯上", "2Maccabees": "瑪加伯下",
}


def book_zh(name: str) -> str:
    key = name.replace(" ", "").replace(".", "")
    for k, v in BOOK_ZH.items():
        if k.lower() == key.lower():
            return v
    for k, v in BOOK_ZH.items():
        if key.lower() in k.lower():
            return v
    return name


def fetch(url: str) -> str:
    try:
        response = requests.get(url, timeout=12)
        response.raise_for_status()
        return response.text
    except Exception as exc:
        print(f"WARN fetch {url}: {exc}", file=sys.stderr)
        return ""


def strip_html(html: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", html))


def next_sunday_date():
    now = datetime.now(ZoneInfo(TZ))
    days = (6 - now.weekday()) % 7
    if days == 0:
        days = 7
    return now + timedelta(days=days)


def parse_mass_readings(html: str):
    text = strip_html(html)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = {
        "sunday_name": "",
        "first_ref": "", "first_title": "", "first_text": "",
        "psalm_ref": "",
        "second_ref": "", "second_title": "", "second_text": "",
        "gospel_ref": "", "gospel_title": "", "gospel_text": "",
    }

    for line in lines:
        if "Sunday" in line and (
            "Lent" in line or "Advent" in line or "Easter" in line or
            "Ordinary" in line or "Christmas" in line or
            re.search(r"\d+(st|nd|rd|th)\s+Sunday", line)
        ):
            result["sunday_name"] = line[:80]
            break

    def extract_block(keyword, stop_keywords):
        capturing = False
        block = []
        for line in lines:
            if keyword.lower() in line.lower() and not capturing:
                capturing = True
            if capturing:
                if block and any(k.lower() in line.lower() for k in stop_keywords):
                    break
                block.append(line)
        return " ".join(block)

    for line in lines:
        match = re.match(r"First reading\s+(\S+)\s+([\d:,\-]+)\s+(.*)", line)
        if match:
            result["first_ref"] = f"{match.group(1)} {match.group(2)}"
            result["first_title"] = match.group(3)[:80]
            break
    result["first_text"] = extract_block("First reading", ["Responsorial", "Second reading", "Gospel"])[:600]

    for line in lines:
        match = re.search(r"Responsorial Psalm\s+Psalm\s+(\d+)\s*\((\d+)\)", line)
        if match:
            result["psalm_ref"] = f"詩篇 {match.group(2)}"
            break
        match = re.search(r"Responsorial Psalm\s+Psalm\s+(\d+)", line)
        if match:
            result["psalm_ref"] = f"詩篇 {match.group(1)}"
            break

    for line in lines:
        match = re.match(r"Second reading\s+(\S+)\s+([\d:,\-]+)\s+(.*)", line)
        if match:
            result["second_ref"] = f"{match.group(1)} {match.group(2)}"
            result["second_title"] = match.group(3)[:80]
            break
    result["second_text"] = extract_block("Second reading", ["Gospel Acclamation", "Gospel "])[:600]

    for line in lines:
        match = re.match(r"Gospel\s+(\S+)\s+([\d:,\-]+)\s+(.*)", line)
        if match and "Acclamation" not in line:
            result["gospel_ref"] = f"{match.group(1)} {match.group(2)}"
            result["gospel_title"] = match.group(3)[:80]
            break
    result["gospel_text"] = extract_block("Gospel ", ["Christian Art", "Dates", "Copyright"])[:800]
    return result


def ref_zh(ref: str) -> str:
    if not ref:
        return ref
    parts = ref.strip().split()
    if not parts:
        return ref
    return f"{book_zh(parts[0])} {' '.join(parts[1:])}"


def generate_commentary(readings, sunday_date_str: str) -> str:
    client = OpenAI(api_key=GROK_KEY, base_url="https://api.x.ai/v1")
    prompt = f"""你是一位天主教導師，風格類似 RCIA（基督徒入門禮儀）的教學方式。

請為以下主日讀經生成一份繁體中文導讀。聖經引文請用和合本繁體中文。

主日：{sunday_date_str}
禮儀主日名稱：{readings['sunday_name']}

讀經一：{ref_zh(readings['first_ref'])}（{readings['first_title']}）
內容摘錄：{readings['first_text'][:400]}

答唱詠：{readings['psalm_ref']}

讀經二：{ref_zh(readings['second_ref'])}（{readings['second_title']}）
內容摘錄：{readings['second_text'][:400]}

福音：{ref_zh(readings['gospel_ref'])}（{readings['gospel_title']}）
內容摘錄：{readings['gospel_text'][:600]}

請按以下格式生成導讀，篇幅約800-1000字：
1. 主題概覽（2-3句）
2. 讀經一解說（歷史背景、核心意象、與今日的連結）
3. 答唱詠簡介（引用和合本1-2節，說明在禮儀中的作用）
4. 讀經二解說（核心神學概念、與復活/信仰的連結）
5. 福音解說（背景人物、關鍵場景、核心金句的深層意涵）
6. 三段讀經的共同主題
7. 反思問題（3條，RCIA風格）
8. 本週靈修邀請（一句行動呼召）

語氣：溫暖、有深度、平易近人，像一位好老師在講解。"""
    response = client.chat.completions.create(
        model="grok-3",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def send_text(text: str) -> None:
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "message_thread_id": int(TOPIC_ID), "text": chunk},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram send failed: {data}")


def main() -> None:
    if not BOT_TOKEN:
        print(f"ERROR: TELEGRAM_BOT_TOKEN not found in {ENV_FILE}", file=sys.stderr)
        sys.exit(1)
    if not GROK_KEY:
        print(f"ERROR: XAI_API_KEY/GROK_API_KEY not found in {ENV_FILE}", file=sys.stderr)
        sys.exit(1)

    sunday = next_sunday_date()
    date_str = sunday.strftime("%Y%m%d")
    sunday_display = sunday.strftime("%Y年%-m月%-d日")

    print(f"Fetching readings for {sunday_display} ({date_str})...")
    html = fetch(f"https://universalis.com/{date_str}/mass.htm")
    if not html:
        print("ERROR: Could not fetch Universalis page", file=sys.stderr)
        sys.exit(1)

    readings = parse_mass_readings(html)
    print(f"Sunday: {readings['sunday_name']}")
    print(f"Readings: {readings['first_ref']} / {readings['psalm_ref']} / {readings['second_ref']} / {readings['gospel_ref']}")
    print("Generating commentary...")
    commentary = generate_commentary(readings, sunday_display)

    header = f"📖 主日讀經導讀\n{sunday_display} · {readings['sunday_name']}\n\n"
    header += f"讀經一：{ref_zh(readings['first_ref'])}\n"
    if readings["psalm_ref"]:
        header += f"答唱詠：{readings['psalm_ref']}\n"
    if readings["second_ref"]:
        header += f"讀經二：{ref_zh(readings['second_ref'])}\n"
    header += f"福音：{ref_zh(readings['gospel_ref'])}\n"
    header += "━━━━━━━━━━━━━━━\n\n"

    print("Sending text to Telegram...")
    send_text(header + commentary)
    print(f"✅ Weekly reading sent for {sunday_display} from Hermes")


if __name__ == "__main__":
    main()
