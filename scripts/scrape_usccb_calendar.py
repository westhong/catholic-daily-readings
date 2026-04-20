#!/usr/bin/env python3
"""
scrape_usccb_calendar.py

Download USCCB calendar data: all feast URLs per day, then download each .cfm file.
Saves to: data/usccb-calendar/
  - index/YYYY-MM.json    — daily index (date → list of feasts)
  - raw/YYYY-MM-DD[-variant].cfm  — raw HTML per feast

Usage:
  python3 scrape_usccb_calendar.py [--start YYYY-MM] [--end YYYY-MM]
"""

import os
import re
import json
import time
import logging
from datetime import date
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode

# ── config ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
DATA_DIR   = BASE_DIR / "data" / "usccb-calendar"
INDEX_DIR  = DATA_DIR / "index"
RAW_DIR    = DATA_DIR / "raw"
ROOT_URL   = "https://bible.usccb.org"
CAL_URL    = f"{ROOT_URL}/readings/calendar"
AJAX_URL   = f"{ROOT_URL}/views/ajax"
MONTHS     = list(range(202604, 202613)) + list(range(202701, 202713))
HEADERS    = {
    "User-Agent": "Mozilla/5.0 (compatible; CatholicAssistantBot/1.0)",
    "Accept": "application/x-www-form-urlencoded",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("usccb-cal")

# ── helpers ──────────────────────────────────────────────────────────────────

def fetch(url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=15) as r:
                ct = r.headers.get("Content-Type", "")
                # USCCB sometimes returns gzip
                raw = r.read()
                if ct.startswith("text/html") and raw[:2] in (b'\x1f\x8b', b'BZh'):
                    import gzip
                    raw = gzip.decompress(raw)
                return raw.decode("utf-8", errors="replace")
        except Exception as e:
            log.warning("  fetch %s failed (attempt %d): %s", url, attempt + 1, e)
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts")


def ajax_month(year_month: str) -> str:
    """Fetch one month calendar HTML via Drupal Views AJAX endpoint."""
    log.info("  AJAX fetch %s", year_month)
    data = urlencode({
        "view_name": "readings_calendar_base",
        "view_display_id": "page_month",
        "view_args": year_month,
    }).encode()
    req = Request(AJAX_URL, data=data, headers={
        "User-Agent": HEADERS["User-Agent"],
        "Content-Type": "application/x-www-form-urlencoded",
    })
    with urlopen(req, timeout=15) as r:
        raw = r.read()
        # AJAX response is JSON array; data field contains HTML
        import json as j
        responses = j.loads(raw.decode("utf-8"))
        # Find the insert/replaceWith command with calendar HTML
        for item in responses:
            if item.get("command") == "insert":
                html = item.get("data", "")
                if "calendar-calendar" in html:
                    return html
            elif item.get("command") == "settings":
                pass  # skip
        # fallback: return first response with HTML content
        for item in responses:
            if "calendar" in item.get("data", ""):
                return item["data"]
    return ""


def parse_month_html(html: str, year_month: str) -> dict[str, list[dict]]:
    """
    Given the calendar month HTML, return a dict:
        { "YYYY-MM-DD": [ {"feast": str, "href": str, "color": str}, ... ] }
    Only includes days that have feast entries.
    """
    results: dict[str, list[dict]] = {}

    # Each day cell: data-date="YYYY-MM-DD"
    # Inside .item, feast links are <a href="/bible/readings/..." data-colors="...">Feast Name</a>
    day_blocks = re.findall(
        r'<td[^>]+data-date="(\d{4}-\d{2}-\d{2})"[^>]*>(.*?)</td>',
        html, re.DOTALL
    )

    for day_str, cell_html in day_blocks:
        # Find all feast items within this cell
        items = re.findall(
            r'<a href="([^"]+)"[^>]*data-colors="([^"]*)"[^>]*>([^<]+)</a>',
            cell_html
        )
        if not items:
            continue
        day_feasts = []
        for href, color, name in items:
            href = href.strip()
            name = name.strip()
            # Fix URLs without .cfm suffix
            if href and not href.endswith(".cfm"):
                href = href.rstrip()
                # common cases
                if not href.endswith(".cfm"):
                    href = href + ".cfm"
            day_feasts.append({"feast": name, "href": href, "color": color})
        if day_feasts:
            results[day_str] = day_feasts

    return results


def normalize_url(href: str) -> str:
    """Ensure href has .cfm suffix, handling special cases."""
    href = href.strip()
    if not href:
        return ""
    # Already has .cfm
    if href.endswith(".cfm"):
        return href
    # Special named pages — map to standard .cfm form where known
    # pentecost-sunday → 052426-Day.cfm (approximation)
    special_map = {
        "pentecost-sunday": "pentecost-sunday",
        "pentecost-sunday-vigil": "pentecost-sunday",
    }
    if href in special_map:
        return href + ".cfm"
    # Anything else — just append .cfm
    return href + ".cfm"


def download_cfm(href: str, raw_dir: Path, date_str: str, feast_idx: int, original_href: str) -> str | None:
    """Download a single .cfm page. Returns local filename (relative) or None on failure."""
    # Build local filename
    safe_feast = re.sub(r'[^\w\-]', '_', original_href.split('/')[-1].replace(".cfm", ""))
    local_name = f"{date_str}-{safe_feast}.cfm"
    local_path = raw_dir / local_name

    if local_path.exists():
        log.info("  exists: %s", local_name)
        return local_name

    # Construct full URL
    if href.startswith("http"):
        url = href
    else:
        url = ROOT_URL + href if href.startswith("/") else f"{ROOT_URL}/{href}"

    try:
        content = fetch(url)
        local_path.write_text(content, encoding="utf-8")
        log.info("  saved: %s", local_name)
        return local_name
    except Exception as e:
        log.error("  FAILED %s → %s: %s", url, local_name, e)
        return None


def run(start: str = "2026-04", end: str = "2027-04"):
    """
    Run the full scrape from start_month (YYYY-MM) to end_month (inclusive).
    """
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Expand YYYY-MM → list of YYYYMM strings
    def month_iter(start_ym: str, end_ym: str):
        ym = int(start_ym.replace("-", ""))
        end = int(end_ym.replace("-", ""))
        while ym <= end:
            yield f"{ym:06d}"
            # bump to next month
            y, m = divmod(ym, 100)
            if m == 12:
                y += 1; m = 1
            else:
                m += 1
            ym = y * 100 + m

    for ym_str in month_iter(start, end):
        year_month = ym_str  # "202604"
        year = year_month[:4]
        month = year_month[4:]

        log.info("=== Month: %s ===", year_month)

        # Determine if this is the "current" month (April 2026) — use direct HTML
        if year_month == "202604":
            html = fetch(CAL_URL)
        else:
            html = ajax_month(year_month)

        if not html:
            log.error("  No HTML returned for %s, skipping", year_month)
            continue

        # Parse
        daily = parse_month_html(html, year_month)
        log.info("  Found %d days with feasts", len(daily))

        month_index: dict[str, list[dict]] = {}

        for day_str, feasts in sorted(daily.items()):
            log.info("  %s: %d feasts", day_str, len(feasts))
            feast_entries = []
            for idx, f in enumerate(feasts):
                original_href = f["href"]
                href = normalize_url(original_href)
                local_file = download_cfm(href, RAW_DIR, day_str, idx, original_href)
                feast_entries.append({
                    "feast": f["feast"],
                    "href": original_href,
                    "url": ROOT_URL + original_href if original_href.startswith("/") else original_href,
                    "color": f["color"],
                    "local_file": local_file,
                })
            month_index[day_str] = feast_entries

        # Write month index
        idx_path = INDEX_DIR / f"{year_month}.json"
        idx_path.write_text(json.dumps(month_index, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info("  Wrote index: %s", idx_path.name)

        time.sleep(1)  # polite delay between months

    log.info("Done. Data in %s", DATA_DIR)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape USCCB calendar")
    parser.add_argument("--start", default="2026-04")
    parser.add_argument("--end",   default="2027-04")
    args = parser.parse_args()
    run(args.start, args.end)
