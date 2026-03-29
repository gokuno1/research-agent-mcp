# OpenAlex Research MCP Server (Node.js)

This MCP server uses OpenAlex APIs to fetch works and topic hierarchy data (domains, fields, subfields, topics). It uses `api_key` authentication and exposes focused tools for discovery workflows.

## Requirements

- Node.js 18+
- OpenAlex API key from [https://openalex.org/settings/api](https://openalex.org/settings/api)

## Install

```bash
npm install
npm run build
```

## Configuration

Set the following in MCP server environment:

- `OPENALEX_API_KEY` (recommended for higher practical usage limits)
- `OPENALEX_MAILTO` (optional)

OpenAlex docs:

- [Works API](https://developers.openalex.org/api-reference/works)
- [Topics API](https://developers.openalex.org/api-reference/topics)
- [LLM reference](https://developers.openalex.org/llms.txt)

## Tools

- `openalex_get_work`: fetch single work by OpenAlex ID, DOI, or supported external ID form
- `openalex_search_works`: search/list works with `filter`, `search`, `sort`, `per_page`, `page`, `cursor`, `select`
- `openalex_get_topic`: fetch single topic by ID
- `openalex_search_topics`: search/list topics with common query params
- `openalex_group_topics`: aggregate topics by `domain.id`, `field.id`, `subfield.id`, or `id`

## Local run

```bash
npm run build
npm start
```

For development:

```bash
npm run dev
```

## Cursor MCP config

Add this server into Cursor MCP with absolute paths. Example:

```json
{
  "OpenAlex_Research_1_0_0": {
    "command": "node",
    "args": ["D:/Projects/research-agent-mcp/mcp-openalex/mcp-openalex/dist/index.js"],
    "env": {
      "OPENALEX_API_KEY": "YOUR_KEY",
      "OPENALEX_MAILTO": "you@example.com"
    }
  }
}
```
