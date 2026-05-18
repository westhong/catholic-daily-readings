import { InvalidDateError, getReadings, type GetReadingsOptions, type ReadingItem } from "./readings";

export { InvalidDateError };

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

type GetGospelOptions = GetReadingsOptions;

export function getGospel(date?: string, options: GetGospelOptions = {}): GospelPayload | null {
  const payload = getReadings(date, options);
  if (payload === null) {
    return null;
  }

  return {
    date: payload.date,
    timezone: payload.timezone,
    source: payload.source,
    records: payload.records.map((record) => ({
      feast: record.feast,
      mass: record.mass,
      lectionary_number: record.lectionary_number,
      gospels: record.readings.gospel ?? [],
    })),
  };
}
