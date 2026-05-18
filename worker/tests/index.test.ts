import { describe, expect, it } from "vitest";

import worker from "../src/index";


describe("worker fetch", () => {
  it("serves /api/v1/gospel for a specific date", async () => {
    const response = await worker.fetch(new Request("https://example.com/api/v1/gospel?date=2026-04-19"));

    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.records[0].gospels).toEqual([{ citation: "Luke 24:13-35", sources: ["USCCB"] }]);
  });

  it("serves today when date is omitted", async () => {
    const response = await worker.fetch(new Request("https://example.com/api/v1/gospel"), {}, { today: "2026-04-19" });

    expect(response.status).toBe(200);
    expect((await response.json()).date).toBe("2026-04-19");
  });

  it("returns 400 for invalid dates", async () => {
    const response = await worker.fetch(new Request("https://example.com/api/v1/gospel?date=04/19/2026"));

    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ detail: "date must be YYYY-MM-DD" });
  });

  it("returns 404 for unknown dates", async () => {
    const response = await worker.fetch(new Request("https://example.com/api/v1/gospel?date=2099-01-01"));

    expect(response.status).toBe(404);
    expect(await response.json()).toEqual({ detail: "No Gospel metadata found for 2099-01-01" });
  });

  it("returns 404 for unknown routes", async () => {
    const response = await worker.fetch(new Request("https://example.com/nope"));

    expect(response.status).toBe(404);
  });
});
