import { describe, expect, it } from "vitest";

import { InvalidDateError, getReadings } from "../src/readings";


describe("getReadings", () => {
  it("returns citation-only full readings metadata for a specific date", () => {
    expect(getReadings("2026-05-17")).toEqual({
      date: "2026-05-17",
      timezone: "America/Edmonton",
      source: "catholic-daily-readings",
      records: [
        {
          feast: "Seventh Sunday of Easter",
          mass: "default",
          lectionary_number: 59,
          readings: {
            first_reading: [{ citation: "Acts 1:12-14", sources: ["USCCB"] }],
            responsorial_psalm: [{ citation: "Psalm 27:1, 4, 7-8", sources: ["USCCB"] }],
            second_reading: [{ citation: "1 Peter 4:13-16", sources: ["USCCB"] }],
            alleluia: [{ citation: "John 14:18", sources: ["USCCB"] }],
            gospel: [{ citation: "John 17:1-11a", sources: ["USCCB"] }],
          },
        },
        {
          feast: "The Ascension of the Lord (US celebration)",
          mass: "alternate",
          lectionary_number: 58,
          readings: {
            first_reading: [{ citation: "Acts 1:1-11", sources: ["USCCB"] }],
            responsorial_psalm: [{ citation: "Psalm 47:2-3, 6-7, 8-9", sources: ["USCCB"] }],
            second_reading: [{ citation: "Ephesians 1:17-23", sources: ["USCCB"] }],
            alleluia: [{ citation: "Matthew 28:19a, 20b", sources: ["USCCB"] }],
            gospel: [{ citation: "Matthew 28:16-20", sources: ["USCCB"] }],
          },
        },
      ],
    });
  });

  it("preserves multiple Mass records and sources for Holy Thursday", () => {
    const result = getReadings("2026-04-02");

    expect(result?.records.map((record) => record.mass)).toEqual(["Chrism", "Supper"]);
    expect(result?.records[1].readings.gospel).toEqual([
      { citation: "John 13:1-15", sources: ["USCCB", "CatholicGallery", "CatholicOnline"] },
    ]);
  });

  it("uses injected today when date is omitted", () => {
    expect(getReadings(undefined, { today: "2026-05-17" })?.date).toBe("2026-05-17");
  });

  it("rejects invalid date format", () => {
    expect(() => getReadings("05/17/2026")).toThrow(InvalidDateError);
  });

  it("returns null for unknown dates", () => {
    expect(getReadings("1900-01-01")).toBeNull();
  });
});
