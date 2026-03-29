import assert from "node:assert/strict";
import test from "node:test";
import {
  buildOpenAlexUrl,
  clampPerPage,
  openAlexGetJson,
  validateTopicGroupBy
} from "../src/openalex-client.js";

test("clampPerPage uses defaults and bounds", () => {
  assert.equal(clampPerPage(undefined), 25);
  assert.equal(clampPerPage(0), 1);
  assert.equal(clampPerPage(101), 100);
  assert.equal(clampPerPage(50), 50);
});

test("validateTopicGroupBy allows supported values", () => {
  assert.equal(validateTopicGroupBy("domain.id"), "domain.id");
  assert.equal(validateTopicGroupBy("field.id"), "field.id");
  assert.equal(validateTopicGroupBy("subfield.id"), "subfield.id");
  assert.equal(validateTopicGroupBy("id"), "id");
});

test("validateTopicGroupBy rejects unsupported values", () => {
  assert.throws(
    () => validateTopicGroupBy("display_name"),
    /group_by must be one of/
  );
});

test("buildOpenAlexUrl adds api key, optional mailto, and clamps per_page", () => {
  const url = buildOpenAlexUrl("/works", { per_page: 250, search: "graph ai" }, {
    apiKey: "abc123",
    mailto: "you@example.com"
  });
  assert.equal(url.origin, "https://api.openalex.org");
  assert.equal(url.pathname, "/works");
  assert.equal(url.searchParams.get("api_key"), "abc123");
  assert.equal(url.searchParams.get("mailto"), "you@example.com");
  assert.equal(url.searchParams.get("per_page"), "100");
  assert.equal(url.searchParams.get("search"), "graph ai");
});

test("buildOpenAlexUrl throws when api key is missing", () => {
  assert.throws(
    () => buildOpenAlexUrl("/works", {}, { apiKey: "" }),
    /OPENALEX_API_KEY/
  );
});

test("openAlexGetJson returns parsed json for successful responses", async () => {
  const fetchMock = async () =>
    ({
      ok: true,
      status: 200,
      text: async () => JSON.stringify({ meta: { count: 1 }, results: [] })
    }) as Response;

  const payload = await openAlexGetJson(
    "/works",
    { per_page: 1 },
    { apiKey: "abc123" },
    fetchMock
  );
  assert.deepEqual(payload, { meta: { count: 1 }, results: [] });
});

test("openAlexGetJson throws with status and body details on error", async () => {
  const fetchMock = async () =>
    ({
      ok: false,
      status: 429,
      text: async () => JSON.stringify({ error: "rate limited" })
    }) as Response;

  await assert.rejects(
    async () =>
      openAlexGetJson("/works", {}, { apiKey: "abc123" }, fetchMock),
    /OpenAlex request failed \(429\):/
  );
});
