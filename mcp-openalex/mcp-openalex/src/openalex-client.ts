export const OPENALEX_BASE_URL = "https://api.openalex.org";
export const DEFAULT_PER_PAGE = 25;
export const MAX_PER_PAGE = 100;

const ALLOWED_TOPIC_GROUP_BY = new Set(["domain.id", "field.id", "subfield.id", "id"]);

export type OpenAlexEnv = {
  apiKey: string;
  mailto?: string;
};

export type QueryValue = string | number | boolean | undefined;

export function clampPerPage(value?: number): number {
  if (value === undefined || Number.isNaN(value)) {
    return DEFAULT_PER_PAGE;
  }
  return Math.min(MAX_PER_PAGE, Math.max(1, Math.trunc(value)));
}

export function validateTopicGroupBy(groupBy: string): string {
  if (!ALLOWED_TOPIC_GROUP_BY.has(groupBy)) {
    throw new Error("group_by must be one of: domain.id, field.id, subfield.id, id");
  }
  return groupBy;
}

export function buildOpenAlexUrl(
  path: string,
  query: Record<string, QueryValue>,
  env: OpenAlexEnv
): URL {
  const apiKey = env.apiKey?.trim();
  if (!apiKey) {
    throw new Error("OPENALEX_API_KEY is required.");
  }

  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${OPENALEX_BASE_URL}${normalizedPath}`);
  const params = new URLSearchParams();

  params.set("api_key", apiKey);
  if (env.mailto?.trim()) {
    params.set("mailto", env.mailto.trim());
  }

  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }

    if (key === "per_page") {
      params.set("per_page", String(clampPerPage(Number(value))));
      continue;
    }

    params.set(key, String(value));
  }

  url.search = params.toString();
  return url;
}

export async function openAlexGetJson<T = unknown>(
  path: string,
  query: Record<string, QueryValue>,
  env: OpenAlexEnv,
  fetchImpl: typeof fetch = fetch
): Promise<T> {
  const url = buildOpenAlexUrl(path, query, env);
  const response = await fetchImpl(url, { method: "GET" });
  const bodyText = await response.text();

  if (!response.ok) {
    const snippet = bodyText.length > 500 ? `${bodyText.slice(0, 500)}...` : bodyText;
    throw new Error(`OpenAlex request failed (${response.status}): ${snippet}`);
  }

  try {
    return JSON.parse(bodyText) as T;
  } catch {
    throw new Error("OpenAlex response was not valid JSON.");
  }
}
