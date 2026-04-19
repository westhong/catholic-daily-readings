"""
Catholic Liturgical Calendar Computation Engine.

Computes for any Gregorian date:
  - liturgical_year (A | B | C)
  - season (advent | christmas | lent | easter | ordinary)
  - week_of_season / day_of_week
  - feast_name
  - lectionary_number (US lectionary)
  - sunday_of_year (for Sundays)
  - readings for that day (from embedded US lectionary tables)

The 3-year cycle: Year A (瑪竇/Matthew), Year B (馬爾谷/Mark), Year C (路加/Luke).
Current cycle: 2024-2025=Year A, 2025-2026=Year B, 2026-2027=Year C.

US Lectionary numbering (main ranges):
  Sundays: 1-10 (Advent), 11-17 (Christmas), 18-25 (Lent), 29-39 (Easter),
           40-58 (Ordinary - Year A), 64-80 (Ordinary - Year B), 85-101 (Ordinary - Year C)
  Weekdays: separate numbering per season

Key dates by season (for reference):
  - Advent: 4 Sundays, Dec 25 ends
  - Christmas: Dec 25 to Jan 12 (then back to OT)
  - Lent: Ash Wednesday starts, 6 Sundays
  - Easter: Easter Sunday to Pentecost (7 weeks), then to Christ the King
  - Ordinary: Two blocks: after Christmas to Lent, after Easter to Christ the King
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional

import sys
import os

# ----------------------------------------------------------------------
# Data: Liturgical calendar rules
# ----------------------------------------------------------------------

class Season(Enum):
    ADVENT = "advent"
    CHRISTMAS = "christmas"
    LENT = "lent"
    EASTER = "easter"
    ORDINARY = "ordinary"


# ----------------------------------------------------------------------
# Helper: Find the first Sunday on or before a given date
# ----------------------------------------------------------------------

def first_sunday_on_or_before(d: date) -> date:
    """Return the Sunday of the week containing d (same day if d is Sunday)."""
    return d - timedelta(days=d.weekday())  # weekday(): Mon=0, Sun=6; subtract to get to Sunday


# ----------------------------------------------------------------------
# Helper: Find Advent start for a given liturgical year
# ----------------------------------------------------------------------

def advent_start(year: int) -> date:
    """
    Advent starts on the fourth Sunday before Christmas.
    Christmas is Dec 25. The Sunday on or before Dec 25 is:
      Dec 25 - (weekday(Dec 25) - 6) if weekday >= 6 else Dec 25 - weekday
    But simplified: find the Sunday exactly N days before Dec 25.
    The Sunday of the week containing Dec 25, then go back 3 weeks.
    """
    christmas = date(year, 12, 25)
    sunday_before_christmas = christmas - timedelta(days=christmas.weekday())
    # First Sunday of Advent = 4 weeks before that Sunday
    return sunday_before_christmas - timedelta(weeks=3)


def liturgical_year_for(c: date) -> int:
    """
    Catholic liturgical year number.
    Year 1 = Year A (Matthew), Year 2 = Year B (Mark), Year 3 = Year C (Luke).
    The 3-year cycle is based on the year of the liturgical year start.
    E.g., liturgical year starting Nov/Dec 2024 = Year 1 = Year A.
    """
    # Standard cycle: 2024-2025 liturgical year = Year A (1)
    # Pattern: Year A = odd-numbered liturgical years starting from 2024
    # Year A: starts in years 2024, 2027, 2030...
    # The cycle started with Year A in 2024 (Nov 30, 2024 = First Sunday of Advent 2024)
    # Cycle: Year A (2024-25), Year B (2025-26), Year C (2026-27), then repeat
    base_year = 2024
    base_cycle = 1  # Year A
    adv_start = advent_start(c.year)
    if c < adv_start:
        # Before Advent this year → still in previous liturgical year
        adv_start_prev = advent_start(c.year - 1)
        years_since_base = (adv_start_prev.year - base_year) // 3
        cycle_offset = (c.year - adv_start_prev.year) % 3
    else:
        years_since_base = (adv_start.year - base_year) // 3
        cycle_offset = (c.year - adv_start.year) % 3
    return ((base_cycle - 1 + cycle_offset) % 3) + 1


def year_label(c: date) -> str:
    """Return 'A', 'B', or 'C' for the liturgical year of date c."""
    cycle = liturgical_year_for(c)
    return ["A", "B", "C"][cycle - 1]


# ----------------------------------------------------------------------
# Compute liturgical date for any Gregorian date
# ----------------------------------------------------------------------

@dataclass
class LiturgicalDate:
    date: date
    liturgical_year: int  # 1=A, 2=B, 3=C
    year_label: str       # 'A' | 'B' | 'C'
    season: Season
    week_of_season: int   # 1-indexed within season
    day_of_week: int      # 0=Sun, 1=Mon, ... 6=Sat
    sunday_of_year: Optional[int] = None  # 1-35 for Sundays, None for weekdays
    feast: str = ""
    lectionary_number: int = 0
    readings: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "year": self.year_label,
            "season": self.season.value,
            "week_of_season": self.week_of_season,
            "day_of_week": self.day_of_week,
            "sunday_of_year": self.sunday_of_year,
            "feast": self.feast,
            "lectionary_number": self.lectionary_number,
            "readings": self.readings,
        }


def ash_wednesday_year(y: int) -> date:
    """Ash Wednesday = 46 days before Easter Sunday."""
    easter = easter_sunday(y)
    return easter - timedelta(days=46)


def easter_sunday(y: int) -> date:
    """
    Compute Easter Sunday for year y using Anonymous Gregorian algorithm.
    """
    a = y % 19
    b = y // 100
    c = y % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, month, day)


def season_and_week(c: date) -> tuple[Season, int, str]:
    """
    Return (season, week_of_season, feast_name) for date c.
    """
    ly = liturgical_year_for(c)
    adv_start = advent_start(c.year if c >= advent_start(c.year) else c.year - 1)
    if c < adv_start:
        adv_start = advent_start(c.year - 1)

    christmas = date(c.year, 12, 25)
    easter = easter_sunday(c.year if c >= ash_wednesday_year(c.year) or c.month < 6 else c.year - 1)
    if c < date(c.year, 1, 12) and c.month >= 9:
        # Might be in OT after Christmas
        pass

    # Determine actual liturgical year start
    adv_start_actual = adv_start
    if c < adv_start_actual:
        adv_start_actual = advent_start(c.year - 1)

    # Advent: starts 4 weeks before Dec 25, ends on Dec 24
    adv_start_actual = adv_start_actual  # already computed
    christmas_start = date(c.year, 12, 25)
    christmas_end = date(c.year, 1, 12)  # Jan 12

    # We need to handle the case where c is in Jan-early June
    # These belong to the liturgical year that started the previous Advent
    if c.month <= 6 and c.month >= 1:
        # These dates belong to the liturgical year that started prev Advent
        prev_adv = advent_start(c.year - 1)
        adv_start_actual = prev_adv

    # Recalculate based on actual liturgical year
    adv_start_actual = advent_start(c.year) if c >= advent_start(c.year) else advent_start(c.year - 1)
    christmas_day_date = date(c.year, 12, 25)

    # Check if in Advent
    if adv_start_actual <= c <= date(c.year, 12, 24):
        # Advent
        weeks_elapsed = (c - adv_start_actual).days // 7 + 1
        feast = f"{weeks_elapsed} Advent Sunday" if c.weekday() == 6 else weekday_feast_name(c, Season.ADVENT)
        season = Season.ADVENT
        return season, weeks_elapsed, feast

    # Christmas: Dec 25 - Jan 12 (Jan 6 = Epiphany usually, Jan 7-12 = after Epiphany)
    if date(c.year, 12, 25) <= c <= date(c.year, 12, 31):
        week_num = (c - date(c.year, 12, 25)).days // 7 + 1
        return Season.CHRISTMAS, week_num, christmas_feast_name(c)

    if date(c.year, 1, 1) <= c <= date(c.year, 1, 12):
        # Christmas season (Octave of Christmas)
        week_num = (c - date(c.year, 1, 1)).days // 7 + 1
        return Season.CHRISTMAS, week_num, christmas_feast_name(c)

    # Determine Easter and Lent dates for this liturgical year
    if c.month <= 6:
        # Use current calendar year for Easter calculation if we're in the first half
        easter_yr = c.year
    else:
        easter_yr = c.year

    ashWed = ash_wednesday_year(easter_yr)
    easter_dt = easter_sunday(easter_yr)

    # Lent: Ash Wednesday to Holy Saturday (the day before Easter)
    if ashWed <= c <= easter_dt - timedelta(days=1):
        weeks_elapsed = (c - ashWed).days // 7 + 1
        feast = f"{weeks_elapsed} Lent Sunday" if c.weekday() == 0 else lent_weekday_feast(c)
        return Season.LENT, weeks_elapsed, feast

    # Easter: Easter Sunday to Pentecost
    pentecost = easter_dt + timedelta(days=49)
    if easter_dt <= c <= pentecost:
        weeks_elapsed = (c - easter_dt).days // 7 + 1
        if weeks_elapsed == 1:
            feast = "Easter Sunday"
        elif c.weekday() == 0:
            feast = f"{weeks_elapsed} Easter Sunday"
        else:
            feast = easter_weekday_feast(c)
        return Season.EASTER, weeks_elapsed, feast

    # Pentecost to Christ the King (end of liturgical year)
    christ_king = pentecost + timedelta(days=27)  # Christ the King is 8th week after Pentecost
    # Actually Christ the King is the last Sunday, which is 33rd/34th Sunday after Pentecost
    # The last Sunday after Pentecost = Christ the King
    # For ordinary time after Pentecost:
    weeks_after_pentecost = (c - pentecost).days // 7 + 1
    if weeks_after_pentecost >= 27:  # Christ the King is 33rd/34th
        return Season.ORDINARY, weeks_after_pentecost, "Christ the King"

    feast = ordinary_time_feast(c, weeks_after_pentecost)
    return Season.ORDINARY, weeks_after_pentecost, feast


def christmas_feast_name(c: date) -> str:
    """Return feast name for Christmas season dates."""
    d = c.day
    m = c.month
    if m == 12:
        if d == 25: return "The Nativity of the Lord (Christmas)"
        if d == 26: return "St. Stephen, Martyr"
        if d == 27: return "St. John, Apostle"
        if d == 28: return "Holy Innocents"
        if d == 29: return "St. Thomas Becket"
        if d == 30: return "The Holy Family"
        if d == 31: return "St. Sylvester I, Pope"
    if m == 1:
        if d == 1: return "Solemnity of Mary, Mother of God"
        if d == 2: return "Sts. Basil the Great & Gregory Nazianzen"
        if d == 3: return "The Epiphany of the Lord"
        if d == 4: return "St. Elizabeth Ann Seton"
        if d == 5: return "St. John Neumann"
        if d == 6: return "The Epiphany of the Lord"
        if d >= 7 and d <= 12: return f"Days within the Octave of Epiphany"
    return "Christmas Season"


def lent_weekday_feast(c: date) -> str:
    """Return feast name for Lenten weekdays."""
    # Lenten weekdays are numbered: Week 1 (after Ash Wed), Week 2, etc.
    ashWed = ash_wednesday_year(c.year)
    days_since_ash = (c - ashWed).days
    week_num = days_since_ash // 7 + 1
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return f"{day_names[c.weekday()]} of Lent, Week {week_num}"


def easter_weekday_feast(c: date) -> str:
    """Return feast name for Easter season weekdays."""
    easter_dt = easter_sunday(c.year)
    days_since_easter = (c - easter_dt).days
    week_num = days_since_easter // 7 + 1
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return f"{day_names[c.weekday()]} of Easter, Week {week_num}"


def ordinary_time_feast(c: date, weeks_after_pentecost: int) -> str:
    """Return feast name for Ordinary Time dates."""
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    if c.weekday() == 0:
        return f"{weeks_after_pentecost} Sunday of Ordinary Time"
    return f"{day_names[c.weekday()]} of Ordinary Time, Week {weeks_after_pentecost}"


def weekday_feast_name(c: date, season: Season) -> str:
    """Return generic weekday feast name."""
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return f"{day_names[c.weekday()]}"


# ----------------------------------------------------------------------
# Lectionary number computation
# ----------------------------------------------------------------------

def lectionary_number_for(c: date, season: Season, week_of_season: int, sunday_of_year: Optional[int], ly_label: str) -> int:
    """
    Compute US lectionary number for a given date.
    This is based on the US Lectionary structure.
    """
    if sunday_of_year is not None:
        # Sunday lectionary numbers
        # Advent Sundays: 1-10
        # Christmas (first Sunday after Christmas if any): part of 11-17
        # Lent Sundays: 18-25
        # Easter Sundays: 26-29... actually Easter cycle uses 29-39
        # Actually the US lectionary numbers:
        # 1-4: Advent 1-4 (Year A/B/C vary)
        # 5-10: Advent varies
        # 11-17: Christmas / early January
        # 18-25: Lent 1-5 (Lent 6 is Passion/Palm)
        # 26: Palm Sunday
        # 27: Holy Thursday
        # 28: Good Friday
        # 29: Easter Vigil / Easter
        # 30-34: Easter 2-6
        # 35: Pentecost
        # 36-39: weeks after Pentecost (but there are more)
        # The Sunday lectionary after Pentecost continues to Christ the King
        # Year A: 40-58 (actually 40-58 = 19 Sundays)
        # Year B: 64-80 (17 Sundays)
        # Year C: 85-101 (17 Sundays)
        pass

    # For now, return 0 as a placeholder - actual numbers are complex
    # and depend on the specific day within the season
    return 0


# ----------------------------------------------------------------------
# US Lectionary data for Sundays
# ----------------------------------------------------------------------
# Format: (lectionary_num, year_a_refs, year_b_refs, year_c_refs)
# refs: (first_reading, responsorial_psalm, second_reading, gospel)
# All reading references are in the format "Book Chapter:Verse"

# Advent Sundays (1-4):
ADVENT_SUNDAYS = [
    # First Sunday of Advent (Dec 1-4 range)
    {
        "lectionary": 1,
        "year_a": ("Isaiah 2:1-5", "Psalm 122:1-2, 6-9", "Romans 13:11-14", "Matthew 24:37-44"),
        "year_b": ("Isaiah 63:16-17, 64:1-8", "Psalm 80:2-3, 15-16, 18-19", "1 Corinthians 1:3-9", "Mark 13:33-37"),
        "year_c": ("Jeremiah 33:14-16", "Psalm 25:4-5, 8-9, 10, 14", "1 Thessalonians 3:12—4:2", "Luke 21:25-28, 34-36"),
    },
    # Second Sunday of Advent
    {
        "lectionary": 5,
        "year_a": ("Isaiah 11:1-10", "Psalm 72:1-2, 7-8, 12-13, 17", "Romans 15:4-9", "Matthew 3:1-12"),
        "year_b": ("Isaiah 40:1-5, 9-11", "Psalm 85:9-14", "2 Peter 3:8-14", "Mark 1:1-8"),
        "year_c": ("Baruch 5:1-9", "Psalm 126:1-2, 2-3, 4-5, 6", "Philippians 1:4-6, 8-11", "Luke 3:1-6"),
    },
    # Third Sunday of Advent (Gaudete Sunday)
    {
        "lectionary": 7,
        "year_a": ("Isaiah 35:1-6, 10", "Psalm 146:6-7, 8-9, 9-10", "James 5:7-10", "Matthew 11:2-11"),
        "year_b": ("Isaiah 61:1-2, 10-11", "Luke 1:46-50, 53-54", "1 Thessalonians 5:16-24", "John 1:6-8, 19-28"),
        "year_c": ("Zephaniah 3:14-18", "Isaiah 12:2-3, 4, 5-6", "Philippians 4:4-7", "Luke 3:10-18"),
    },
    # Fourth Sunday of Advent
    {
        "lectionary": 9,
        "year_a": ("Isaiah 7:10-14", "Psalm 24:1-2, 3-4, 5-6", "Romans 1:1-7", "Matthew 1:18-24"),
        "year_b": ("2 Samuel 7:1-5, 8-12, 14, 16", "Psalm 89:2-3, 4-5, 21-22, 25, 27", "Romans 16:25-27", "Luke 1:26-38"),
        "year_c": ("Micah 5:1-4", "Psalm 80:2-3, 15-16, 18-19", "Hebrews 10:5-10", "Luke 1:39-45"),
    },
]

# Christmas Season:
CHRISTMAS_SUNDAYS = [
    # The Nativity of the Lord (Dec 25) - not a Sunday in standard calendar
    # Sunday after Christmas (if exists) or early January
    # First Sunday after Christmas (or Jan 1 if no Sunday)
    # The Epiphany (Jan 6) - typically celebrated on a Sunday Jan 2-8
]

# Lenten Sundays:
LENT_SUNDAYS = [
    # First Sunday of Lent
    {
        "lectionary": 18,
        "year_a": ("Genesis 2:7-9, 3:1-7", "Psalm 51:1-2, 3-4, 5-6", "Romans 5:12-19", "Matthew 4:1-11"),
        "year_b": ("Genesis 9:8-15", "Psalm 25:4-5, 6-7, 8-9", "1 Peter 3:18-22", "Mark 1:12-15"),
        "year_c": ("Deuteronomy 26:4-10", "Psalm 91:1-2, 10-11, 12-13, 14-15", "Romans 10:8-13", "Luke 4:1-13"),
    },
    # Second Sunday of Lent
    {
        "lectionary": 19,
        "year_a": ("Genesis 12:1-4", "Psalm 33:4-5, 18-19, 20, 22", "2 Timothy 1:8-10", "Matthew 17:1-9"),
        "year_b": ("Genesis 22:1-2, 9-13, 15-18", "Psalm 116:9, 15-16, 17-18", "Romans 8:31-34", "Mark 9:2-10"),
        "year_c": ("Genesis 15:1-6", "Psalm 27:1, 4, 7-8, 9-10, 13-14", "Philippians 3:17—4:1", "Luke 9:28-36"),
    },
    # Third Sunday of Lent
    {
        "lectionary": 20,
        "year_a": ("Exodus 17:1-7", "Psalm 95:1-2, 6-7, 8-9", "Romans 5:1-2, 5-8", "John 4:5-15, 19-26, 39-40, 43-44"),
        "year_b": ("Exodus 20:1-17", "Psalm 19:8, 9, 10, 11", "1 Corinthians 1:22-25", "John 2:13-25"),
        "year_c": ("Exodus 3:1-8, 13-15", "Psalm 103:1-2, 3-4, 6-7, 8, 11", "1 Corinthians 10:1-6, 10-12", "Luke 13:1-9"),
    },
    # Fourth Sunday of Lent (Laetare Sunday)
    {
        "lectionary": 21,
        "year_a": ("1 Samuel 16:1, 6-7, 10-13", "Psalm 23:1-3, 3-4, 5, 6", "Ephesians 5:8-14", "John 9:1-41"),
        "year_b": ("2 Chronicles 36:14-17, 19-23", "Psalm 137:1-2, 3, 4-5, 6", "Ephesians 2:4-10", "John 3:14-21"),
        "year_c": ("Joshua 5:9, 10-12", "Psalm 34:2-3, 4-5, 6-7", "2 Corinthians 5:17-21", "Luke 15:1-3, 11-32"),
    },
    # Fifth Sunday of Lent
    {
        "lectionary": 22,
        "year_a": ("Ezekiel 37:12-14", "Psalm 130:1-2, 3-4, 5-6, 7-8", "Romans 8:8-11", "John 11:1-45"),
        "year_b": ("Jeremiah 31:31-34", "Psalm 51:1-2, 10-12, 14", "Hebrews 5:7-9", "John 12:20-33"),
        "year_c": ("Isaiah 43:16-21", "Psalm 126:1-2, 2-3, 4-5, 6", "Philippians 3:8-14", "John 8:1-11"),
    },
    # Palm Sunday
    {
        "lectionary": 26,
        "year_a": ("Matthew 26:14-27:66", "Psalm 22:1, 7-8, 15-16, 17-18, 19-20, 25-27, 30-31", "Philippians 2:6-11", "Matthew 26:14-27:66"),
        "year_b": ("Mark 14:1-15:47", "Psalm 22:1, 7-8, 15-16, 17-18, 19-20, 25-27, 30-31", "Isaiah 52:13-53:12", "Mark 15:1-39"),
        "year_c": ("Luke 19:28-48", "Psalm 22:1, 7-8, 15-16, 17-18, 19-20, 25-27, 30-31", "Isaiah 50:4-7", "Luke 22:14-23:56"),
    },
]

# Easter Sundays:
EASTER_SUNDAYS = [
    # Easter Sunday
    {
        "lectionary": 29,
        "year_a": ("Acts 10:34, 37-43", "Psalm 118:1-2, 14-17, 22-23", "Colossians 3:1-4", "John 20:1-9"),
        "year_b": ("Acts 10:34, 37-43", "Psalm 118:1-2, 14-17, 22-23", "1 Corinthians 15:1-11", "Mark 16:1-7"),
        "year_c": ("Acts 10:34, 37-43", "Psalm 118:1-2, 14-17, 22-23", "1 Corinthians 15:19-26", "Luke 24:1-12"),
    },
    # Second Sunday of Easter (Divine Mercy)
    {
        "lectionary": 41,
        "year_a": ("Acts 2:42-47", "Psalm 118:2-4, 13-15, 22-24", "1 Peter 1:3-9", "John 20:19-31"),
        "year_b": ("Acts 4:32-37", "Psalm 118:2-4, 13-15, 22-24", "1 John 5:1-6", "John 20:19-31"),
        "year_c": ("Acts 5:12-16", "Psalm 118:2-4, 13-15, 22-24", "Revelation 1:9-11, 12-13, 17-19", "John 20:19-31"),
    },
    # Third Sunday of Easter
    {
        "lectionary": 46,
        "year_a": ("Acts 2:14, 22-33", "Psalm 16:1-2, 5, 7-8, 9-10, 11", "1 Peter 1:17-21", "Luke 24:13-35"),
        "year_b": ("Acts 3:12-19", "Psalm 4:2, 4, 7-8, 9", "1 John 2:1-5", "Luke 24:35-48"),
        "year_c": ("Acts 5:27-32, 36-40", "Psalm 30:2, 4, 5-6, 11-12, 13, 14", "Revelation 7:9, 14-17", "John 21:1-19"),
    },
    # Fourth Sunday of Easter (Good Shepherd)
    {
        "lectionary": 47,
        "year_a": ("Acts 2:14, 36-41", "Psalm 23:1-3, 3-4, 5, 6", "1 Peter 2:20-25", "John 10:1-10"),
        "year_b": ("Acts 4:8-12", "Psalm 118:8-9, 21-23, 25-27", "1 John 3:1-2", "John 10:11-18"),
        "year_c": ("Acts 13:14, 43-52", "Psalm 100:1-2, 3, 5", "Revelation 7:9, 14-17", "John 10:27-30"),
    },
    # Fifth Sunday of Easter
    {
        "lectionary": 48,
        "year_a": ("Acts 6:1-7", "Psalm 33:1-2, 4-5, 18-19", "1 Peter 2:4-9", "John 14:1-12"),
        "year_b": ("Acts 9:26-31", "Psalm 22:26-27, 28-29, 30-31", "1 John 3:18-24", "John 15:1-8"),
        "year_c": ("Acts 14:21-27", "Psalm 145:8-9, 10-11, 12-13", "Revelation 21:1-5", "John 13:31-35"),
    },
    # Sixth Sunday of Easter
    {
        "lectionary": 49,
        "year_a": ("Acts 8:5-8, 14-17", "Psalm 22:26-27, 28-29, 30-31", "1 Peter 3:15-18", "John 14:15-21"),
        "year_b": ("Acts 10:25-26, 34-35, 44-48", "Psalm 98:1, 2-3, 3-4", "1 John 4:7-11", "John 15:9-17"),
        "year_c": ("Acts 15:1-2, 22-29", "Psalm 67:2-3, 5, 6, 8", "Revelation 21:10-14, 22-23", "John 14:23-29"),
    },
    # Ascension of the Lord (7th Sunday of Easter in some years)
    # This falls on a Thursday 40 days after Easter, but celebrated on Sunday in most places
    # Seventh Sunday of Easter
    {
        "lectionary": 51,
        "year_a": ("Acts 1:1-11", "Psalm 47:2, 6-7, 8-9", "Ephesians 1:17-23", "Matthew 28:16-20"),
        "year_b": ("Acts 1:15-17, 20-26", "Psalm 103:1-2, 11-12, 19-20", "1 John 4:11-16", "John 17:11-19"),
        "year_c": ("Acts 7:55-60", "Psalm 97:1-2, 6, 11-12", "Revelation 22:12-14, 16-17, 20", "John 17:20-26"),
    },
    # Pentecost
    {
        "lectionary": 52,
        "year_a": ("Acts 2:1-11", "Psalm 104:1, 24, 29-30, 31, 33", "1 Corinthians 12:3-7, 12-13", "John 20:19-23"),
        "year_b": ("Acts 1:15-26", "Psalm 33:1-2, 4-5, 12-13, 20-21", "Romans 12:3-8", "John 17:1-11"),
        "year_c": ("Acts 2:1-11", "Psalm 104:1, 29-30, 31, 33, 35", "1 Corinthians 12:3-7, 12-13", "John 15:26-27; 16:4-15"),
    },
]

# ----------------------------------------------------------------------
# Christ the King (Last Sunday after Pentecost, Cycle C ends here)
CHRIST_THE_KING = {
    "lectionary": 58,
    "year_a": ("Ezekiel 34:11-12, 15-17", "Psalm 23:1-3, 3-4, 5, 6", "1 Corinthians 15:20-26, 28", "Matthew 25:31-46"),
    "year_b": ("Daniel 7:13-14", "Psalm 93:1, 1-2, 5", "Revelation 1:5-8", "John 18:33-37"),
    "year_c": ("2 Samuel 5:1-3", "Psalm 122:1-2, 4-5", "Colossians 1:12-20", "Luke 23:35-43"),
}


def build_full_year(date_start: date, date_end: date) -> list[dict]:
    """
    Build the full liturgical year data for all dates from date_start to date_end.
    Returns a list of LiturgicalDate objects.
    """
    results = []
    d = date_start
    while d <= date_end:
        ld = compute_liturgical_date(d)
        results.append(ld.to_dict())
        d += timedelta(days=1)
    return results


def compute_liturgical_date(c: date) -> LiturgicalDate:
    """
    Compute the full liturgical date for a given Gregorian date.
    Returns a LiturgicalDate with all fields populated.
    """
    ly = liturgical_year_for(c)
    ly_label = ["A", "B", "C"][ly - 1]
    season, week_of_season, feast = season_and_week(c)
    sunday_of_year = None
    if c.weekday() == 0:  # Sunday
        sunday_of_year = week_of_season  # Simplified - Sundays numbered within season
    day_of_week = c.weekday()

    ld = LiturgicalDate(
        date=c,
        liturgical_year=ly,
        year_label=ly_label,
        season=season,
        week_of_season=week_of_season,
        day_of_week=day_of_week,
        sunday_of_year=sunday_of_year,
        feast=feast,
        lectionary_number=0,  # TODO: compute from known tables
        readings={},
    )
    return ld


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Test: print liturgical date for a few sample dates
    test_dates = [
        date(2024, 11, 30),  # First Sunday of Advent 2024
        date(2024, 12, 25),  # Christmas
        date(2025, 3, 20),   # Lent
        date(2025, 4, 20),   # Easter season
        date(2026, 4, 19),   # Third Sunday of Easter Year C
        date(2026, 8, 15),   # Assumption
    ]

    for d in test_dates:
        ld = compute_liturgical_date(d)
        print(f"{d}: Year {ld.year_label}, {ld.season.value}, Week {ld.week_of_season}, {ld.feast}")
