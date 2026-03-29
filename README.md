# Research Agent MCP: OpenAlex + Cursor Skill Setup

This project contains:

- A local OpenAlex MCP server (`mcp-openalex/mcp-openalex`)
- A project skill for structured research runs (`.cursor/skills/openalex-high-impact-research/SKILL.md`)
- MongoDB MCP integration for storing run outputs in `research_agent.research_runs`

Use this guide for first-time setup in Cursor IDE.

## 1) Prerequisites

- Cursor IDE with MCP support enabled
- Node.js 18+ (for the OpenAlex MCP server)
- MongoDB running locally (default: `mongodb://127.0.0.1:27017`)
- OpenAlex API key from [OpenAlex Settings](https://openalex.org/settings/api)

Optional but recommended:

- `OPENALEX_MAILTO` set to your email for OpenAlex request identification

## 2) Set up the OpenAlex MCP server

From the project folder:

```powershell
cd "D:\Projects\research-agent-mcp\mcp-openalex\mcp-openalex"
npm install
npm run build
```

This creates the server entrypoint:

- `D:/Projects/research-agent-mcp/mcp-openalex/mcp-openalex/dist/src/index.js`

## 3) Configure OpenAlex MCP in Cursor

In Cursor MCP settings, add an MCP server entry like:

```json
{
  "OpenAlex_Research_1_0_0": {
    "command": "node",
    "args": [
      "D:/Projects/research-agent-mcp/mcp-openalex/mcp-openalex/dist/src/index.js"
    ],
    "env": {
      "OPENALEX_API_KEY": "YOUR_OPENALEX_API_KEY",
      "OPENALEX_MAILTO": "you@example.com"
    }
  }
}
```

Then restart Cursor (or reload MCP servers).

## 4) Configure MongoDB MCP for local database

This project already has MongoDB plugin enabled in `.cursor/settings.json`.

To connect MongoDB MCP to local MongoDB, set MCP environment variable:

- `MDB_MCP_CONNECTION_STRING=mongodb://127.0.0.1:27017`

If your MongoDB uses auth, use:

- `mongodb://USERNAME:PASSWORD@127.0.0.1:27017/?authSource=admin`

Optional safety mode:

- `MDB_MCP_READ_ONLY=true` (prevents write operations)

Restart Cursor (or reload MCP servers) after changing env vars.

## 5) Verify MCP setup in Cursor chat

Quick verification prompts:

- `List all databases from local mongo db`
- `Search OpenAlex works for "event-driven architecture latency" with cited_by_count > 100`

Expected:

- MongoDB MCP can list your local databases
- OpenAlex MCP returns work records (title/id/year/citations)

## 6) Use the project research skill

Skill location:

- `.cursor/skills/openalex-high-impact-research/SKILL.md`

Reliable invocation prompts:

- `Run the openalex-high-impact-research skill for this question: <your question>`
- `Use the project research workflow: OpenAlex high-impact retrieve -> claims -> hypotheses -> contradictions -> score -> structural fixes -> save to research_agent.research_runs.`

What the skill does:

1. Retrieves high-impact OpenAlex papers (citation floor + topic filters)
2. Applies domain-intent filtering to reduce irrelevant domains
3. Builds claims, hypotheses, contradictions, and quality scores
4. Saves one run document to MongoDB:
   - database: `research_agent`
   - collection: `research_runs`

## 7) Troubleshooting

- **OpenAlex MCP not found in Cursor**
  - Recheck server name and absolute `args` path to `dist/src/index.js`
  - Ensure `npm run build` completed successfully

- **OpenAlex calls fail**
  - Verify `OPENALEX_API_KEY` is present in MCP env
  - Restart Cursor after env updates

- **MongoDB "connect first" errors**
  - Verify `MDB_MCP_CONNECTION_STRING` is set correctly
  - Confirm local MongoDB is running on the expected host/port

- **Skill does not trigger**
  - Name it explicitly in your first message: `openalex-high-impact-research`
  - Confirm the file exists at `.cursor/skills/openalex-high-impact-research/SKILL.md`

## 8) Notes

- Do not commit real API keys or database credentials.
- Keep credentials in local Cursor MCP env settings only.
