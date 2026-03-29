import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import {
  clampPerPage,
  openAlexGetJson,
  validateTopicGroupBy,
  type OpenAlexEnv
} from "./openalex-client.js";

type OpenAlexResult = {
  meta?: unknown;
  results?: unknown;
  group_by?: unknown;
};

type GetWorkArgs = { work_id: string; select?: string };
type SearchWorksArgs = {
  filter?: string;
  search?: string;
  sort?: string;
  per_page?: number;
  page?: number;
  cursor?: string;
  select?: string;
};
type GetTopicArgs = { topic_id: string; select?: string };
type SearchTopicsArgs = SearchWorksArgs;
type GroupTopicsArgs = {
  group_by: string;
  filter?: string;
  search?: string;
  sort?: string;
  per_page?: number;
  page?: number;
  cursor?: string;
};

type NodeProcessLike = {
  env?: Record<string, string | undefined>;
  exit?: (code?: number) => void;
};

const nodeProcess = (globalThis as { process?: NodeProcessLike }).process;
const processEnv = nodeProcess?.env ?? {};

const env: OpenAlexEnv = {
  apiKey: processEnv.OPENALEX_API_KEY ?? "",
  mailto: processEnv.OPENALEX_MAILTO
};

const server = new McpServer({
  name: "openalex-research-server",
  version: "1.0.0"
});

function jsonResult(payload: unknown) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(payload, null, 2) }]
  };
}

function errorResult(error: unknown) {
  const message = error instanceof Error ? error.message : "Unexpected server error.";
  return jsonResult({ success: false, error: message });
}

server.tool(
  "openalex_get_work",
  "Fetch a single work by OpenAlex ID, DOI form, or supported external ID form.",
  {
    work_id: z.string().min(1).describe("Work identifier, for example W2741809807 or doi:10.xxxx/abcd"),
    select: z.string().optional().describe("Optional comma-separated field list")
  },
  async ({ work_id, select }: GetWorkArgs) => {
    try {
      const payload = await openAlexGetJson(`/works/${encodeURIComponent(work_id)}`, { select }, env);
      return jsonResult(payload);
    } catch (error) {
      return errorResult(error);
    }
  }
);

server.tool(
  "openalex_search_works",
  "Search or list works with OpenAlex query parameters (filter, search, sort, per_page, page, cursor, select).",
  {
    filter: z.string().optional(),
    search: z.string().optional(),
    sort: z.string().optional(),
    per_page: z.number().int().optional(),
    page: z.number().int().optional(),
    cursor: z.string().optional(),
    select: z.string().optional()
  },
  async ({ filter, search, sort, per_page, page, cursor, select }: SearchWorksArgs) => {
    try {
      const payload = await openAlexGetJson<OpenAlexResult>(
        "/works",
        {
          filter,
          search,
          sort,
          per_page: per_page === undefined ? undefined : clampPerPage(per_page),
          page,
          cursor,
          select
        },
        env
      );
      return jsonResult(payload);
    } catch (error) {
      return errorResult(error);
    }
  }
);

server.tool(
  "openalex_get_topic",
  "Fetch a single topic by OpenAlex topic ID.",
  {
    topic_id: z.string().min(1).describe("Topic identifier, for example T12345"),
    select: z.string().optional().describe("Optional comma-separated field list")
  },
  async ({ topic_id, select }: GetTopicArgs) => {
    try {
      const payload = await openAlexGetJson(`/topics/${encodeURIComponent(topic_id)}`, { select }, env);
      return jsonResult(payload);
    } catch (error) {
      return errorResult(error);
    }
  }
);

server.tool(
  "openalex_search_topics",
  "Search or list topics with OpenAlex query parameters (filter, search, sort, per_page, page, cursor, select).",
  {
    filter: z.string().optional(),
    search: z.string().optional(),
    sort: z.string().optional(),
    per_page: z.number().int().optional(),
    page: z.number().int().optional(),
    cursor: z.string().optional(),
    select: z.string().optional()
  },
  async ({ filter, search, sort, per_page, page, cursor, select }: SearchTopicsArgs) => {
    try {
      const payload = await openAlexGetJson<OpenAlexResult>(
        "/topics",
        {
          filter,
          search,
          sort,
          per_page: per_page === undefined ? undefined : clampPerPage(per_page),
          page,
          cursor,
          select
        },
        env
      );
      return jsonResult(payload);
    } catch (error) {
      return errorResult(error);
    }
  }
);

server.tool(
  "openalex_group_topics",
  "Group topics by hierarchy level. Allowed group_by: domain.id, field.id, subfield.id, id.",
  {
    group_by: z.string().describe("One of domain.id, field.id, subfield.id, id"),
    filter: z.string().optional(),
    search: z.string().optional(),
    sort: z.string().optional(),
    per_page: z.number().int().optional(),
    page: z.number().int().optional(),
    cursor: z.string().optional()
  },
  async ({ group_by, filter, search, sort, per_page, page, cursor }: GroupTopicsArgs) => {
    try {
      const validGroupBy = validateTopicGroupBy(group_by);
      const payload = await openAlexGetJson<OpenAlexResult>(
        "/topics",
        {
          group_by: validGroupBy,
          filter,
          search,
          sort,
          per_page: per_page === undefined ? undefined : clampPerPage(per_page),
          page,
          cursor
        },
        env
      );
      return jsonResult(payload);
    } catch (error) {
      return errorResult(error);
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Failed to start OpenAlex MCP server:", error);
  nodeProcess?.exit?.(1);
});
