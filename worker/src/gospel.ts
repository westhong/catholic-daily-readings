import readings from "../../data/lectionary/readings.json";

export const DEFAULT_TIMEZONE = "America/Edmonton";
const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

export class InvalidDateError extends Error {
  constructor(message = "date must be YYYY-MM-DD") {
    super(message);
    this.name = "InvalidDateError";
  }
}

type ReadingItem = {
  citation: string;
  sources: string[];
};

type DayEntry = {
  feast: string;
  mass?: string;
  lectionary_number: number | null;
  readings: {
    gospel?: ReadingItem[];
  };
};

export type GospelRecord = {
  feast: string;
  mass: string;
  lectionary_number: number | null;
  gospels: ReadingItem[];
};

export type GospelPayload = {
  date: string;
  timezone: string;
  source: "catholic-daily-readings";
  records: GospelRecord[];
};

type GetGospelOptions = {
  timezone?: string;
  today?: string;
};

function todayInTimeZone(timezone: string): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: timezone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${values.year}-${values.month}-${values.day}`;
}

function resolveDate(date: string | undefined, timezone: string, today?: string): string {
  if (date === undefined || date === null || date === "") {
    return today ?? todayInTimeZone(timezone);
  }
  if (!DATE_RE.test(date)) {
    throw new InvalidDateError();
  }
  const parsed = new Date(`${date}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== date) {
    throw new InvalidDateError("date must be a real YYYY-MM-DD date");
  }
  return date;
}

export function getGospel(date?: string, options: GetGospelOptions = {}): GospelPayload | null {
  const timezone = options.timezone ?? DEFAULT_TIMEZONE;
  const dateKey = resolveDate(date, timezone, options.today);
  const entries = (readings as Record<string, DayEntry[]>)[dateKey];
  if (!entries) {
    return null;
  }

  return {
    date: dateKey,
    timezone,
    source: "catholic-daily-readings",
    records: entries.map((entry) => ({
      feast: entry.feast,
      mass: entry.mass ?? "default",
      lectionary_number: entry.lectionary_number,
      gospels: entry.readings.gospel ?? [],
    })),
  };
}
