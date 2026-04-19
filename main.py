#!/usr/bin/env python3
"""
Catholic Assistant — Daily Reading Record Builder (MVP)

Usage:
    python3 main.py [date]
    python3 main.py 2026-04-18

Produces a DailyReadingRecord JSON for the given date (default: today).
"""

import json
import sys
from datetime import date

from src.core.reader import build_daily_record, save_record


def main():
    target = date.today()
    if len(sys.argv) > 1:
        target = date.fromisoformat(sys.argv[1])

    print(f"Building daily reading record for {target.isoformat()}...")

    record = build_daily_record(target)
    data = record.to_dict()

    # Print to stdout
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # Save to data/
    out_path = f"data/{target.isoformat()}.json"
    save_record(record, out_path)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
