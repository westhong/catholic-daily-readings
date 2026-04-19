#!/usr/bin/env python3
"""Fill missing dates by auto-discovering sub-pages from the main page."""
import os, sys, re, json, time, urllib.request
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
import scrape_usccb_readings as sr

OUTPUT_FILE = os.path.join(BASE_DIR, "data", "lectionary", "readings.json")

# dates that need special sub-page handling
MANUAL_DATES = {
    '2025-03-23': '032325',
    '2025-03-30': '033025',
    '2025-04-06': '040625',
    '2025-06-08': '060825',   # Pentecost
    '2025-08-15': '081525',
    '2025-06-24': '062425',
    '2025-06-29': '062925',
    '2025-05-29': '052925',   # Ascension
    '2025-04-17': '041725',   # Holy Thursday
    '2025-11-27': '112725',
    '2025-04-19': '041925',   # Easter Vigil
    '2027-02-28': '022827',
    '2027-03-07': '030727',
    '2027-03-14': '031427',
    '2027-05-16': '051627',
    '2027-08-15': '081527',
    '2027-06-24': '062427',
    '2027-06-29': '062927',
    '2027-05-06': '050627',
    '2027-03-25': '032527',
    '2027-03-29': '032927',
    '2026-11-21': '112126',   # Presentation
}


def discover_subpages(base_url, url_suffix):
    """Discover available sub-pages from the main page links."""
    req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='replace')

    links = re.findall(rf'href="(https://bible\.usccb\.org/bible/readings/{url_suffix}[^"]+)"', html)
    suffixes = set()
    for link in links:
        suffix = link.split(url_suffix)[1].split('.')[0]  # e.g. "-Vigil", "-YearA"
        if suffix and suffix not in ('.cfm', '-cfm', '/'):
            suffixes.add(suffix.lstrip('-'))
    return list(suffixes)


def fetch_page(url, dt_str, mass_label):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='replace')

    result = {'lectionary_number': 0, 'feast': '', 'readings': {}, 'url': url,
              'date': dt_str, 'mass': mass_label}

    lec_match = re.search(r'Lectionary:\s*(\d+)', html)
    if lec_match:
        result['lectionary_number'] = int(lec_match.group(1))

    # Feast
    feast_match = re.search(r'<h2[^>]*>([^<]+)</h2>\s*<p[^>]*>Lectionary:', html, re.DOTALL)
    if feast_match:
        result['feast'] = feast_match.group(1).strip()
    else:
        h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
        nav = {'Menu: Top Buttons', 'Menu: Top', 'Main navigation',
               'Get the Daily Readings', 'Get the Daily ReadingsEvery Morning',
               "Dive into God's Word", 'Daily Readings'}
        for block in h2s:
            clean = re.sub(r'<[^>]+>', '', block).strip()
            clean = re.sub(r'\s+', ' ', clean)
            if clean and clean not in nav and 3 < len(clean) < 120:
                result['feast'] = clean
                break

    # Readings
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)
    lec_idx = text.find('Lectionary:')
    reading_text = text[lec_idx:lec_idx + 12000] if lec_idx >= 0 else text[:12000]
    result['readings'] = sr.parse_reading_refs(reading_text)

    return result


def build_url(url_suffix, suffix):
    base = f'https://bible.usccb.org/bible/readings/{url_suffix}'
    return f'{base}{suffix}.cfm' if suffix else f'{base}.cfm'


def run():
    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    total_filled = 0
    skipped = 0

    for dt_str in sorted(MANUAL_DATES.keys()):
        url_suffix = MANUAL_DATES[dt_str]
        base_url = build_url(url_suffix, '')

        # Check if already has good data
        existing = data.get(dt_str, [])
        has_good = any(
            e.get('readings', {}).get('first_reading', {}).get('reference', '?') not in ['?', '', None, {}]
            for e in existing
        )
        if has_good:
            print(f'  SKIP {dt_str}: already has good data')
            skipped += 1
            continue

        print(f'  Processing {dt_str}...')
        try:
            suffixes = discover_subpages(base_url, url_suffix)
            print(f'    Discovered sub-pages: {suffixes}')
        except Exception as e:
            print(f'    ERROR discovering sub-pages: {e}')
            suffixes = ['']

        entries = []
        for suffix in suffixes:
            url = build_url(url_suffix, suffix)
            try:
                r = fetch_page(url, dt_str, suffix or 'default')
                if r.get('lectionary_number') and r.get('readings'):
                    entries.append(r)
                    fr = r['readings'].get('first_reading', {}).get('reference', '?')
                    g = r['readings'].get('gospel', {}).get('reference', '?')
                    print(f'    [{suffix or "default"}]: L{r["lectionary_number"]} | FR={fr[:25]} | G={g[:20]}')
                time.sleep(0.8)
            except Exception as e:
                print(f'    ERROR [{suffix}]: {e}')

        if entries:
            data[dt_str] = entries
            total_filled += 1

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'\nFilled {total_filled} dates, skipped {skipped}')


if __name__ == '__main__':
    run()
