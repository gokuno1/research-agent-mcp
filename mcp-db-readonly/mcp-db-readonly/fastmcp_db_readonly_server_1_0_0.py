#!/usr/bin/env python3
"""
FastMCP Read-only Database Server - MySQL
Connects to a non-production MySQL database with a read-only user.
Exposes tools to run SELECT queries (and SHOW/DESCRIBE/EXPLAIN) with validation.
Rejects INSERT, UPDATE, DELETE, CREATE, and any other write/DDL operations.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import sqlparse
from fastmcp import FastMCP
import pymysql

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Read-only Database Server (MySQL)")

# Allowed statement types (read-only only)
ALLOWED_STMT_TYPES = frozenset({"SELECT", "SHOW", "DESCRIBE", "EXPLAIN"})
# For "OTHER", we allow only if the first keyword is one of these (e.g. DESCRIBE/EXPLAIN may be OTHER)
ALLOWED_FIRST_KEYWORDS = frozenset({"SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "WITH"})

# Safe identifier: alphanumeric and underscore only (prevents SQL injection in DESCRIBE)
SAFE_IDENTIFIER_RE = re.compile(r"^[a-zA-Z0-9_]+$")


def _safe_identifier(name: Optional[str], field: str) -> Optional[str]:
    """Return name if it is a safe identifier, else None."""
    if not name or not name.strip():
        return None
    name = name.strip()
    if not SAFE_IDENTIFIER_RE.match(name):
        return None
    return name

DB_CONFIG: Dict[str, Any] = {
    "host": None,
    "port": 3306,
    "user": None,
    "password": None,
    "database": None,
    "charset": "utf8mb4",
}

# Max rows to return from db_select (safety cap)
MAX_SELECT_ROWS = 1000


def _parse_database_url(url: str) -> Optional[Dict[str, Any]]:
    """Parse DATABASE_URL (e.g. mysql://user:pass@host:3306/dbname)."""
    if not url or not url.strip():
        return None
    url = url.strip()
    # Support mysql:// and mysql+pymysql://
    if "mysql" not in url.split("://")[0].lower():
        return None
    try:
        # Simple regex parse to avoid extra dependency
        # mysql://user:password@host:port/database
        match = re.match(
            r"mysql(?:\+pymysql)?://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^?&#]*)",
            url,
            re.I,
        )
        if not match:
            return None
        user, password, host, port, database = match.groups()
        return {
            "host": host,
            "port": int(port) if port else 3306,
            "user": user,
            "password": password,
            "database": (database or "").strip("/") or None,
        }
    except Exception:
        return None


def _load_config_from_env() -> None:
    """Load DB config from DATABASE_URL or DB_* environment variables."""
    url = os.getenv("DATABASE_URL")
    if url:
        parsed = _parse_database_url(url)
        if parsed:
            DB_CONFIG.update(parsed)
            logger.info("Database configuration loaded from DATABASE_URL")
            return
    host = os.getenv("DB_HOST")
    if host:
        DB_CONFIG.update({
            "host": host,
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "charset": os.getenv("DB_CHARSET", "utf8mb4"),
        })
        logger.info("Database configuration loaded from DB_* environment variables")


def _get_connection():
    """Create and return a new connection. Caller must close it."""
    if not DB_CONFIG.get("host") or not DB_CONFIG.get("user"):
        raise ValueError("Database not configured. Set DATABASE_URL or DB_HOST, DB_USER, DB_PASSWORD, DB_NAME.")
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG.get("password") or "",
        database=DB_CONFIG.get("database"),
        charset=DB_CONFIG.get("charset", "utf8mb4"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def _get_first_keyword(sql: str) -> str:
    """Return the first SQL keyword (e.g. SELECT, SHOW) from the statement."""
    parsed = sqlparse.parse(sqlparse.format(sql, strip_comments=True))
    if not parsed:
        return ""
    stmt = parsed[0]
    for token in stmt.flatten():
        if token.ttype is sqlparse.tokens.Keyword.DML or token.ttype is sqlparse.tokens.Keyword.DDL:
            return (token.value or "").upper()
        if token.ttype is sqlparse.tokens.Keyword:
            return (token.value or "").upper()
    return ""


def is_readonly_query(query: str) -> Tuple[bool, str]:
    """
    Validate that the query is read-only. Returns (True, "") if allowed, (False, error_message) otherwise.
    """
    if not query or not query.strip():
        return False, "Empty query."
    normalized = " ".join(query.strip().split())
    parsed = sqlparse.parse(sqlparse.format(normalized, strip_comments=True))
    if not parsed:
        return False, "Could not parse query."
    stmt = parsed[0]
    stmt_type = (stmt.get_type() or "").upper()
    first_kw = _get_first_keyword(normalized)

    if stmt_type in ALLOWED_STMT_TYPES:
        if stmt_type == "OTHER":
            if first_kw not in ALLOWED_FIRST_KEYWORDS:
                return False, f"Query type not allowed: {first_kw or 'UNKNOWN'}. Only SELECT, SHOW, DESCRIBE, EXPLAIN are permitted."
        return True, ""
    if first_kw in ALLOWED_FIRST_KEYWORDS:
        return True, ""
    return False, f"Write or DDL operations are not allowed. Got: {stmt_type or first_kw or 'UNKNOWN'}. Only SELECT, SHOW, DESCRIBE, EXPLAIN are permitted."


@mcp.tool()
def db_test_connection() -> str:
    """Test connectivity to the configured non-production MySQL database. Returns success/failure and DB name/version."""
    _load_config_from_env()
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT VERSION() AS version, DATABASE() AS db")
                row = cur.fetchone()
            version = row.get("version", "Unknown") if row else "Unknown"
            db_name = row.get("db", "Unknown") if row else "Unknown"
            return json.dumps({
                "success": True,
                "message": "Connection successful.",
                "database": db_name,
                "version": version,
            }, indent=2)
        finally:
            conn.close()
    except ValueError as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)
    except pymysql.Error as e:
        errmsg = str(e).split("(")[0].strip() if "(" in str(e) else str(e)
        logger.exception("Database connection failed")
        return json.dumps({"success": False, "error": errmsg}, indent=2)
    except Exception as e:
        logger.exception("Unexpected error")
        return json.dumps({"success": False, "error": "Connection failed."}, indent=2)


@mcp.tool()
def db_list_tables(schema: Optional[str] = None) -> str:
    """List tables (and views) the read-only user can see. Optionally specify schema/database name."""
    _load_config_from_env()
    try:
        conn = _get_connection()
        try:
            db = schema or DB_CONFIG.get("database")
            if db:
                conn.select_db(db)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT TABLE_NAME, TABLE_TYPE FROM information_schema.TABLES "
                    "WHERE TABLE_SCHEMA = COALESCE(%s, DATABASE()) ORDER BY TABLE_NAME",
                    (db,),
                )
                rows = cur.fetchall()
            return json.dumps({"tables": [dict(r) for r in rows], "count": len(rows)}, indent=2, default=str)
        finally:
            conn.close()
    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)
    except pymysql.Error as e:
        errmsg = str(e).split("(")[0].strip() if "(" in str(e) else str(e)
        return json.dumps({"error": errmsg}, indent=2)
    except Exception:
        return json.dumps({"error": "Failed to list tables."}, indent=2)


@mcp.tool()
def db_describe_table(table_name: str, schema: Optional[str] = None) -> str:
    """Return column names and types for a given table (e.g. DESCRIBE table or INFORMATION_SCHEMA)."""
    _load_config_from_env()
    if not table_name or not table_name.strip():
        return json.dumps({"error": "table_name is required."}, indent=2)
    table_name = table_name.strip()
    if _safe_identifier(table_name, "table_name") is None:
        return json.dumps({"error": "table_name must contain only letters, numbers, and underscores."}, indent=2)
    safe_schema = _safe_identifier(schema, "schema") if schema else None
    if schema and safe_schema is None:
        return json.dumps({"error": "schema must contain only letters, numbers, and underscores."}, indent=2)
    schema = safe_schema
    try:
        conn = _get_connection()
        try:
            db = schema or DB_CONFIG.get("database")
            if db:
                conn.select_db(db)
            with conn.cursor() as cur:
                cur.execute("DESCRIBE `%s`" % table_name.replace("`", "``"))
                rows = cur.fetchall()
            return json.dumps({"table": table_name, "columns": [dict(r) for r in rows]}, indent=2, default=str)
        finally:
            conn.close()
    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)
    except pymysql.Error as e:
        errmsg = str(e).split("(")[0].strip() if "(" in str(e) else str(e)
        return json.dumps({"error": errmsg}, indent=2)
    except Exception:
        return json.dumps({"error": "Failed to describe table."}, indent=2)


@mcp.tool()
def db_select(query: str, limit: Optional[int] = None) -> str:
    """
    Run a validated read-only SELECT query and return rows. Only SELECT (and SHOW/DESCRIBE/EXPLAIN) are allowed.
    Optional limit caps the number of rows returned (default cap is 10000).
    """
    _load_config_from_env()
    if not query or not query.strip():
        return json.dumps({"error": "query is required."}, indent=2)
    allowed, err = is_readonly_query(query)
    if not allowed:
        return json.dumps({"error": err, "executed": False}, indent=2)
    max_rows = limit if limit is not None else MAX_SELECT_ROWS
    max_rows = min(max_rows, MAX_SELECT_ROWS)
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchmany(max_rows)
            return json.dumps({"rows": rows, "count": len(rows)}, indent=2, default=str)
        finally:
            conn.close()
    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)
    except pymysql.Error as e:
        errmsg = str(e).split("(")[0].strip() if "(" in str(e) else str(e)
        return json.dumps({"error": errmsg}, indent=2)
    except Exception:
        return json.dumps({"error": "Query execution failed."}, indent=2)


if __name__ == "__main__":
    mcp.run()
