#!/usr/bin/env python3
"""
Scrape USCCB daily reading references via .cfm URL format.
URL: https://bible.usccb.org/bible/readings/MMDDYY.cfm

Special days (Christmas Dec 25) have sub-pages: -Vigil, -Night, -Dawn, -Day
Output: data/lectionary/readings.json
"""

import os, re, json, time, urllib.request
from datetime import date, timedelta
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "lectionary")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(DATA_DIR, "readings.json")


def cfm_url(d: date, suffix: str = "") -> str:
    suffix_map = {"Vigil": "-Vigil", "Night": "-Night", "Dawn": "-Dawn", "Day": "-Day"}
    s = suffix_map.get(suffix, suffix)
    return f"https://bible.usccb.org/bible/readings/{d.strftime('%m%d%y')}{s}.cfm"


def first_ref_in_chunk(chunk: str) -> str:
    """Extract first chapter:verse reference with book name from text chunk.
    
    Chunk format: "BookName Chapter:VerseRange ..." e.g. "Is 62:1-5" or "Psalm 97:1, 2-3, 11-12."
    We return the book name + first chapter:verse.
    """
    # Find the chapter:verse pattern
    m = re.search(r'\d+:\d+(?:[\s–\-–,]\d+)*', chunk)
    if not m:
        # Fallback: just digits
        m2 = re.search(r'\d+', chunk)
        if m2:
            return chunk[:m2.end()+5].strip()[:40]
        return ""

    ref = m.group(0)
    before_ref = chunk[:m.start()].strip()
    words = before_ref.split()
    if words:
        # Take last 1-3 words as book name (handles "Is", "First John", "Song of Songs")
        book_words = words[-2:] if len(words) >= 2 else words
        return ' '.join(book_words) + ' ' + ref
    return ref


def parse_reading_refs(text: str) -> dict:
    """Extract reading references from plain text after Lectionary: number.

    Strategy: find each reading label at a word boundary, grab text until
    the next label, extract first chapter:verse reference with book name.
    """
    refs = {}

    # Chapter:verse pattern — handles optional space after colon (e.g., "96: 1-2")
    VERSE_REF = r'\d+:\s*\d+(?:[,\s\u2013\u2014\-]\s*\d+)*'

    # Labels with word boundary at the end (handles "Responsorial Psalm" vs "Psalm")
    label_specs = [
        ('first_reading',      re.compile(r'\bReading\s+(?:I|1)\s+')),
        ('second_reading',     re.compile(r'\bReading\s+(?:II|2)\s+')),
        ('responsorial_psalm', re.compile(r'\bResponsorial\s+Psalm\s+')),
        ('alleluia',           re.compile(r'\bAlle(?:lui)?a\s*\.?\s*', re.IGNORECASE)),
        ('gospel',             re.compile(r'\bGospel\s+')),
    ]

    # Collect all label positions in order
    all_matches = []
    for key, label_re in label_specs:
        for m in label_re.finditer(text):
            all_matches.append((m.start(), key, m.end()))
    all_matches.sort(key=lambda x: x[0])

    for i, (_, key, label_end) in enumerate(all_matches):
        next_start = all_matches[i + 1][0] if i + 1 < len(all_matches) else len(text)
        chunk = text[label_end:next_start].strip()

        ref_match = re.search(VERSE_REF, chunk)
        if ref_match:
            ref = ref_match.group(0)
            before_words = chunk[:ref_match.start()].strip().split()
            # Take last 1-2 words before the chapter:verse as book name
            book = ' '.join(before_words[-2:] if len(before_words) >= 2 else before_words)
            refs[key] = {"reference": (book + ' ' + ref).strip()}
        elif chunk:
            refs[key] = {"reference": chunk[:40].strip()}

    return refs


def fetch_reading_page(d: date, suffix: str = "") -> dict:
    url = cfm_url(d, suffix)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    result = {
        "date": d.isoformat(),
        "url": url,
        "lectionary_number": 0,
        "feast": "",
        "mass": suffix or "default",
        "readings": {}
    }

    # Lectionary number
    lec_match = re.search(r'Lectionary:\s*(\d+)', html)
    if lec_match:
        result["lectionary_number"] = int(lec_match.group(1))

    # Feast name: look for the h2 followed by "Lectionary:" paragraph
    # The USCCB pages have: <h2>Feast Name</h2><p class="...">Lectionary: N ...</p>
    feast_match = re.search(r'<h2[^>]*>([^<]+)</h2>\s*<p[^>]*>Lectionary:', html, re.DOTALL)
    if feast_match:
        result["feast"] = re.sub(r'\s+', ' ', feast_match.group(1).strip())
    else:
        # Fallback: find h2 that is NOT navigation/boilerplate
        h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
        NAV_H2s = {
            'Menu: Top Buttons', 'Menu: Top', 'Main navigation',
            'Get the Daily Readings', 'Get the Daily ReadingsEvery Morning',
            'Dive into God', "Dive into God's Word", 'Daily Readings',
        }
        for block in h2s:
            clean = re.sub(r'<[^>]+>', '', block).strip()
            clean = re.sub(r'\s+', ' ', clean)
            if clean and clean not in NAV_H2s and 3 < len(clean) < 120:
                result["feast"] = clean
                break

    # Extract reading references from plain text
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)

    # Look at a large chunk from Lectionary: to capture ALL readings on the page
    # (Christmas pages have Vigil/Night/Dawn/Day all on one page)
    WINDOW = 12000
    lec_idx = text.find('Lectionary:')
    if lec_idx >= 0:
        reading_text = text[lec_idx:lec_idx + WINDOW]
    else:
        reading_text = text[:WINDOW]

    refs = parse_reading_refs(reading_text)
    result["readings"] = refs

    return result


def fetch_date(d: date) -> list[dict]:
    """Fetch readings for a date. Returns list (one per mass)."""
    results = []

    if d.month == 12 and d.day == 25:
        # Christmas: fetch all 4 masses + default
        for suffix in ["Vigil", "Night", "Dawn", "Day"]:
            try:
                r = fetch_reading_page(d, suffix)
                if r.get("lectionary_number"):
                    results.append(r)
                time.sleep(0.5)
            except Exception:
                pass
        # Try default page too (in case it has readings)
        try:
            r = fetch_reading_page(d, "")
            if r.get("lectionary_number") and r.get("readings"):
                results.insert(0, r)
        except Exception:
            pass

    elif d.month == 4 and d.day in (17, 18, 19):
        # Holy Week: Apr 17 (Holy Thu), Apr 18 (Good Fri), Apr 19 (Holy Sat)
        if d.day == 17:
            # Holy Thursday: Chrism Mass + Evening Mass of the Lord's Supper
            for suffix in ["Chrism", "Supper"]:
                try:
                    r = fetch_reading_page(d, suffix)
                    if r.get("lectionary_number"):
                        results.append(r)
                    time.sleep(0.5)
                except Exception:
                    pass
        elif d.day == 18:
            # Good Friday: Celebration of the Lord's Passion
            try:
                r = fetch_reading_page(d, "")
                if r.get("lectionary_number"):
                    results.append(r)
            except Exception:
                pass
        elif d.day == 19:
            # Holy Saturday: Easter Vigil
            try:
                r = fetch_reading_page(d, "Vigil")
                if r.get("lectionary_number"):
                    results.append(r)
                time.sleep(0.5)
            except Exception:
                pass
            try:
                r = fetch_reading_page(d, "")
                if r.get("lectionary_number") and r.get("readings"):
                    results.insert(0, r)
            except Exception:
                pass

    else:
        try:
            r = fetch_reading_page(d, "")
            if r.get("lectionary_number"):
                results.append(r)
        except Exception:
            pass

    return results


def date_range(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def run_scrape():
    """Scrape all 3 liturgical years."""
    periods = [
        (date(2024, 12, 1), date(2025, 11, 29), "a"),
        (date(2025, 11, 30), date(2026, 11, 28), "b"),
        (date(2026, 11, 29), date(2027, 11, 27), "c"),
    ]

    all_data = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            all_data = json.load(f)
    fetched_dates = set(all_data.keys())

    total_new = 0
    errors = 0

    for start, end, label in periods:
        period_days = sum(1 for _ in date_range(start, end))
        print(f"\n=== Year {label.upper()}: {start} → {end} ({period_days} days) ===")
        period_new = 0

        for d in date_range(start, end):
            date_str = d.isoformat()
            if date_str in fetched_dates:
                continue

            try:
                results = fetch_date(d)
                if results:
                    all_data[date_str] = results
                    fetched_dates.add(date_str)
                    period_new += 1
                    total_new += 1

                    r0 = results[0]
                    lec = r0.get("lectionary_number", "?")
                    feast = r0.get("feast", "")[:35]
                    fr = r0["readings"].get("first_reading", {}).get("reference", "?")
                    g = r0["readings"].get("gospel", {}).get("reference", "?")
                    suffix = f" ({r0['mass']})" if len(results) > 1 else ""
                    print(f"  {date_str}: L{lec} | {feast} | FR={fr[:25]} | G={g[:20]}{suffix}")

                    if period_new % 10 == 0:
                        with open(OUTPUT_FILE, "w") as f:
                            json.dump(all_data, f, indent=2, ensure_ascii=False)
                else:
                    print(f"  {date_str}: NO DATA")

                time.sleep(0.8)

            except Exception as e:
                errors += 1
                print(f"  ERROR {date_str}: {e}")
                if errors >= 15:
                    print("Stopping. Run again to resume.")
                    with open(OUTPUT_FILE, "w") as f:
                        json.dump(all_data, f, indent=2, ensure_ascii=False)
                    return

        print(f"  Year {label.upper()}: {period_new} days done")
        with open(OUTPUT_FILE, "w") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\n=== DONE === Total: {len(all_data)}, new: {total_new}, errors: {errors}")


if __name__ == "__main__":
    run_scrape()
