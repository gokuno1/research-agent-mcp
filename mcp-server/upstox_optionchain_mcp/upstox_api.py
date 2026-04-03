"""HTTP client for Upstox v2 option chain."""

from __future__ import annotations

import os
from typing import Any
import json

import httpx

DEFAULT_BASE = "https://api.upstox.com/v2"
DEFAULT_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"

with open("path_to\\mcp.json") as f:
    data = json.load(f)

server = "upstox-optionchain"

def get_token() -> str:
    token = (
        data.get("mcpServers", {})
        .get(server, {})
        .get("env", {})
        .get("UPSTOX_ACCESS_TOKEN")
    ).strip()
    if not token:
        raise RuntimeError(
            "UPSTOX_ACCESS_TOKEN is not set. Add it to your MCP server env in Cursor settings (mcp.json)."
        )
    return token


def get_instrument_key() -> str:
    return (
        data.get("mcpServers", {})
        .get(server, {})
        .get("env", {})
        .get("UPSTOX_INSTRUMENT_KEY")
    ).strip() or DEFAULT_INSTRUMENT_KEY


def get_base_url() -> str:
    return (
        data.get("mcpServers", {})
        .get(server, {})
        .get("env", {})
        .get("UPSTOX_API_BASE")
    ).strip() or DEFAULT_BASE


def fetch_option_chain(expiry_date: str, instrument_key: str | None = None) -> dict[str, Any]:
    key = instrument_key or get_instrument_key()
    url = f"{get_base_url()}/option/chain"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
    }
    params = {"instrument_key": key, "expiry_date": expiry_date}
    with httpx.Client(timeout=60.0) as client:
        r = client.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()
