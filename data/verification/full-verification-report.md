# Full Layer 1 Verification Report

- Run at: `2026-05-17T23:52:13+00:00`
- Compared: `data/lectionary/readings.json` ⇄ `data/usccb-calendar/raw/*.cfm`
- Total records: **1799**
- PASS: **1799**
- Gate coverage (PASS + ACCEPTED_EXCEPTION): **1799/1799 (100.00%)**

## Meaning
- PASS: slot-level USCCB citations match local Layer 0 raw file.
- SLOT_MISMATCH_ONLY: same citation set, but assigned to different slot/key.
- FAIL: citation set differs from raw Layer 0.
- MISSING_RAW: no local raw file could be matched.
- COPYRIGHT_REVIEW: Layer 1 contains suspicious non-metadata fields or prose-like citation.

## First 80 non-pass records

All records passed.
