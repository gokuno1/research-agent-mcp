# Read-only Database MCP Server (MySQL)

A FastMCP server that connects to a **non-production** MySQL database with a **read-only** user. It exposes tools to run SELECT queries (and SHOW/DESCRIBE/EXPLAIN) with validation. Any INSERT, UPDATE, DELETE, CREATE, or other write/DDL operation is **rejected**; no write operations are executed.

## Requirements

- Python 3.10+
- MySQL non-production database with a read-only user

## Installation

### Option A: Shell installer (recommended)

```bash
chmod +x installer.sh
./installer.sh
```

This creates a virtual environment, installs dependencies, and updates Cursor's MCP configuration with absolute paths.

### Option B: Manual

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Then add the server to Cursor's MCP config (`~/.cursor/mcp.json` or Cursor Settings > MCP) with `command` pointing to `.venv/bin/python` and `args` to the absolute path of `fastmcp_db_readonly_server_1_0_0.py`.

## Configuration

Set one of the following **before** using the tools (e.g. in Cursor MCP env or in your shell):

**Option 1 – Single URL (recommended)**

- `DATABASE_URL=mysql://readonly_user:password@host:3306/nonprod_db`  
  or  
  `DATABASE_URL=mysql+pymysql://readonly_user:password@host:3306/nonprod_db`

**Option 2 – Separate variables**

- `DB_HOST`, `DB_PORT` (default 3306), `DB_USER`, `DB_PASSWORD`, `DB_NAME`, optional `DB_CHARSET` (default utf8mb4)

Do **not** commit credentials. In `mcp-d.json` you can leave `env` empty and set `DATABASE_URL` or `DB_*` in Cursor’s MCP server settings.

## Tools

| Tool | Description |
|------|-------------|
| `db_test_connection` | Test connectivity; returns DB name and MySQL version. |
| `db_list_tables` | List tables (and views) the read-only user can see. Optional `schema` (database name). |
| `db_describe_table` | Return column names and types for a table. `table_name` required; optional `schema`. |
| `db_select` | Run a **validated** read-only query. Parameter: `query` (required). Optional `limit` (max rows returned; server cap 10,000). |

Only **read-only** SQL is allowed: SELECT, SHOW, DESCRIBE, EXPLAIN. INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, and similar are rejected and **not** executed.

## Flow

1. User asks in natural language (e.g. “Get users created last week from table1”).
2. Cursor’s AI turns that into a MySQL query and calls `db_select` (or uses `db_list_tables` / `db_describe_table` first to inspect schema).
3. The MCP server validates the query; if it is read-only, it runs it and returns results; otherwise it returns an error and does **not** run it.

## Security

- Use a MySQL user with **read-only** privileges (e.g. `GRANT SELECT ON nonprod_db.* TO 'readonly_user'@'%';`).
- Every query is validated before execution; do not rely on DB permissions alone.
- Do not log or expose passwords. Optional: enforce a row limit in `db_select` (default cap 10,000 rows).

## Version

1.0.0
