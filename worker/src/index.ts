import { getGospel } from "./gospel";
import { InvalidDateError, getReadings } from "./readings";

type TestContext = {
  today?: string;
};

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, OPTIONS",
  "access-control-allow-headers": "content-type",
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: JSON_HEADERS });
}

export default {
  async fetch(request: Request, _env?: unknown, ctx?: TestContext): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: JSON_HEADERS });
    }

    const date = url.searchParams.get("date") ?? undefined;

    try {
      if (url.pathname === "/api/v1/gospel") {
        const payload = getGospel(date, { today: ctx?.today });
        if (payload === null) {
          return jsonResponse({ detail: `No Gospel metadata found for ${date}` }, 404);
        }
        return jsonResponse(payload);
      }

      if (url.pathname === "/api/v1/readings") {
        const payload = getReadings(date, { today: ctx?.today });
        if (payload === null) {
          return jsonResponse({ detail: `No readings metadata found for ${date}` }, 404);
        }
        return jsonResponse(payload);
      }

      return jsonResponse({ detail: "Not found" }, 404);
    } catch (error) {
      if (error instanceof InvalidDateError) {
        return jsonResponse({ detail: error.message }, 400);
      }
      throw error;
    }
  },
};
