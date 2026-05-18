import { describe, expect, it } from "vitest";

import { InvalidDateError, getGospel } from "../src/gospel";


describe("getGospel", () => {
  it("returns citation-only Gospel metadata for a specific date", () => {
    expect(getGospel("2026-04-19")).toEqual({
      date: "2026-04-19",
      timezone: "America/Edmonton",
      source: "catholic-daily-readings",
      records: [
        {
          feast: "Third Sunday of Easter",
          mass: "default",
          lectionary_number: 44,
          gospels: [{ citation: "Luke 24:13-35", sources: ["USCCB"] }],
        },
      ],
    });
  });

  it("preserves multiple Mass records for one day", () => {
    const result = getGospel("2026-04-02");

    expect(result.records.map((record) => record.mass)).toEqual(["Chrism", "Supper"]);
    expect(result.records[1].gospels).toEqual([
      { citation: "John 13:1-15", sources: ["USCCB", "CatholicGallery", "CatholicOnline"] },
    ]);
  });

  it("uses injected today when date is omitted", () => {
    expect(getGospel(undefined, { today: "2026-04-19" }).date).toBe("2026-04-19");
  });

  it("rejects invalid date format", () => {
    expect(() => getGospel("04/19/2026")).toThrow(InvalidDateError);
  });

  it("returns null for unknown dates", () => {
    expect(getGospel("2099-01-01")).toBeNull();
  });
});
