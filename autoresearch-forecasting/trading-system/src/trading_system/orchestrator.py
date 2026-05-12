"""LangGraph orchestrator wiring agents into a single per-instrument pipeline.

  load_snapshots → microstructure → risk_agent → emit_card → persist_signal

Each node is a small adapter around the agent it calls. State flows through
the typed :class:`AgentState` Pydantic model. We keep nodes synchronous —
the deterministic core does no LLM calls, so async would only add complexity
without latency benefit.

Note: LangGraph's ``StateGraph`` natively supports Pydantic state. We only
re-export ``run_pipeline`` for the CLI to call without importing langgraph
directly elsewhere.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Callable, List

from langgraph.graph import END, StateGraph
import pytz

from .agents import microstructure_agent, risk_agent
from .agents.snapshot_io import load_literature, load_macro, load_micro
from .config import InstrumentConfig, SystemConfig
from .data.upstox import UpstoxClient
from .persistence.schemas import SignalSnapshot
from .persistence.store import Store
from .reporting.trade_card import format_trade_card
from .state import AgentState

IST = pytz.timezone("Asia/Kolkata")


def _node_load_snapshots(cfg: SystemConfig) -> Callable[[AgentState], AgentState]:
    def _node(state: AgentState) -> AgentState:
        state.macro = load_macro(cfg.paths.snapshots, cfg.cadences.macro_refresh_days)
        state.micro = load_micro(cfg.paths.snapshots, cfg.cadences.micro_refresh_days)
        state.literature = load_literature(cfg.paths.snapshots, cfg.cadences.literature_refresh_days)
        if state.macro is None:
            state.log("WARN: macro snapshot missing or stale — continuing with no-bias fallback.")
        return state

    return _node


def _node_microstructure(
    cfg: SystemConfig, instrument: InstrumentConfig, client: UpstoxClient
) -> Callable[[AgentState], AgentState]:
    def _node(state: AgentState) -> AgentState:
        try:
            score = microstructure_agent.run_microstructure(
                client=client,
                instrument_key=instrument.upstox_instrument_key,
                related_keys=instrument.related_keys,
                expected_volume_now=_expected_volume(instrument.symbol, state.now_ist),
                is_event_day=False,
                now_ist=state.now_ist,
                instrument_label=instrument.symbol,
            )
            state.microstructure = score
            state.log(
                f"Microstructure score: raw={score.raw_score:.2f} adjusted={score.adjusted_score:.2f} "
                f"direction={score.direction}"
            )
        except Exception as exc:  # pragma: no cover — surface live data errors
            state.fail(f"microstructure_failed: {exc}")
        return state

    return _node


def _node_risk(
    cfg: SystemConfig, instrument: InstrumentConfig, store: Store
) -> Callable[[AgentState], AgentState]:
    def _node(state: AgentState) -> AgentState:
        if state.microstructure is None:
            return state
        return risk_agent.evaluate(
            state=state,
            cfg=cfg,
            store=store,
            instrument_label=instrument.symbol,
            lot_size=instrument.lot_size,
        )

    return _node


def _node_persist_signal(store: Store) -> Callable[[AgentState], AgentState]:
    def _node(state: AgentState) -> AgentState:
        if state.microstructure is None:
            return state
        snap = SignalSnapshot(
            instrument=state.microstructure.instrument,
            timestamp=state.microstructure.timestamp,
            raw_score=state.microstructure.raw_score,
            adjusted_score=state.microstructure.adjusted_score,
            direction=state.microstructure.direction,
            layer_breakdown_json=json.dumps(state.microstructure.layer_notes),
            macro_regime=state.macro.regime if state.macro else None,
            macro_bias=(
                state.macro.nifty_directional_bias
                if state.macro and state.instrument.upper() == "NIFTY"
                else (state.macro.banknifty_directional_bias if state.macro else None)
            ),
        )
        store.insert_signal(snap)
        return state

    return _node


def _node_emit(cfg: SystemConfig) -> Callable[[AgentState], AgentState]:
    def _node(state: AgentState) -> AgentState:
        if state.trade_card is not None:
            rendered = format_trade_card(state.trade_card, state.microstructure)  # type: ignore[arg-type]
            (cfg.paths.reports / f"{datetime.utcnow():%Y-%m-%d-%H-%M}-{state.instrument}.txt").write_text(
                rendered
            )
            state.log(f"TradeCard emitted for {state.instrument}")
        elif state.risk_gate is not None and not state.risk_gate.passed:
            state.log(f"NoTrade {state.instrument}: {', '.join(state.risk_gate.reasons_rejected)}")
        return state

    return _node


def build_graph(
    cfg: SystemConfig, instrument: InstrumentConfig, client: UpstoxClient, store: Store
):
    """Compile a per-instrument LangGraph that returns a final :class:`AgentState`."""

    g = StateGraph(AgentState)
    g.add_node("load_snapshots", _node_load_snapshots(cfg))
    g.add_node("microstructure", _node_microstructure(cfg, instrument, client))
    g.add_node("risk", _node_risk(cfg, instrument, store))
    g.add_node("persist_signal", _node_persist_signal(store))
    g.add_node("emit", _node_emit(cfg))
    g.set_entry_point("load_snapshots")
    g.add_edge("load_snapshots", "microstructure")
    g.add_edge("microstructure", "risk")
    g.add_edge("risk", "persist_signal")
    g.add_edge("persist_signal", "emit")
    g.add_edge("emit", END)
    return g.compile()


def run_pipeline(
    cfg: SystemConfig, instrument: InstrumentConfig, client: UpstoxClient, store: Store
) -> AgentState:
    graph = build_graph(cfg, instrument, client, store)
    initial = AgentState(instrument=instrument.symbol, now_ist=datetime.now(IST).replace(tzinfo=None))
    final = graph.invoke(initial)
    if isinstance(final, dict):
        # LangGraph returns a dict view of the state in some versions
        final = AgentState(**final)
    return final


def _expected_volume(symbol: str, now_ist: datetime) -> float:
    """Coarse expected-volume baseline pro-rated by time of day.

    These numbers are deliberately rough — RVOL is used as a coarse filter,
    not a precision input. Operators should refine per their own data.
    """

    daily = {"NIFTY": 50_000_000, "BANKNIFTY": 25_000_000}.get(symbol, 10_000_000)
    t = now_ist.time()
    hour_pct = {
        "first": 0.30,
        "second": 0.15,
        "midday": 0.20,
        "fourth": 0.15,
        "last": 0.20,
    }
    if t.hour < 10:
        frac = hour_pct["first"]
    elif t.hour < 12:
        frac = hour_pct["first"] + hour_pct["second"]
    elif t.hour < 13:
        frac = hour_pct["first"] + hour_pct["second"] + hour_pct["midday"]
    elif t.hour < 14:
        frac = 0.80
    else:
        frac = 1.0
    return daily * frac
