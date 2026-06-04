#!/usr/bin/env python3
"""A pluggable trace backend for the eval service (Lab 56; extended in Batch 85).

Batch 84 made the trace backend swappable behind a `TraceBackend` protocol with a `JsonlBackend`
and a guarded `TempoBackend`. This version makes the Tempo path concrete: `parse_tempo_search`
reads the real Grafana Tempo search response schema (traces -> spanSets -> spans -> OTLP-JSON
attributes), so the parsing is verified against the real wire format offline, against a recorded
fixture, even without a running Tempo. Pointing it at a live Tempo only changes where the JSON comes
from.

Usage:
    python trace_backend.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from typing import Protocol

from eval_service import export_to_store
from traces import _synthetic_sessions, token_cost


class TraceBackend(Protocol):
    def read_sessions(self) -> dict: ...


class JsonlBackend:
    """Reads GenAI spans from a JSONL trace store (the format `eval_service.export_to_store` writes)
    and groups them into per-session step lists from the span attributes alone."""
    def __init__(self, path: str):
        self.path = path

    def read_sessions(self) -> dict:
        by_session: dict[str, list[dict]] = {}
        with open(self.path) as f:
            for line in f:
                if not line.strip():
                    continue
                a = json.loads(line)["attributes"]
                by_session.setdefault(a["agent.session_id"], []).append({
                    "model": a["gen_ai.request.model"],
                    "in_tok": a["gen_ai.usage.input_tokens"],
                    "out_tok": a["gen_ai.usage.output_tokens"],
                })
        return by_session


def _otlp_value(value: dict):
    """Extract a scalar from an OTLP-JSON attribute value ({stringValue|intValue|doubleValue: ...}).
    intValue is encoded as a string in OTLP/JSON, hence the int() cast."""
    if "stringValue" in value:
        return value["stringValue"]
    if "intValue" in value:
        return int(value["intValue"])
    if "doubleValue" in value:
        return float(value["doubleValue"])
    if "boolValue" in value:
        return bool(value["boolValue"])
    return None


def parse_tempo_search(payload: dict) -> dict:
    """Parse a Grafana Tempo search response into per-session step lists. Pure function over the
    real response schema, so it is testable against a recorded fixture without a live backend."""
    by_session: dict[str, list[dict]] = {}
    for trace in payload.get("traces", []):
        for span_set in trace.get("spanSets", []):
            for span in span_set.get("spans", []):
                attrs = {kv["key"]: _otlp_value(kv["value"]) for kv in span.get("attributes", [])}
                sid = attrs.get("agent.session_id")
                if sid is None or span.get("name") != "gen_ai.chat":
                    continue
                by_session.setdefault(sid, []).append({
                    "model": attrs["gen_ai.request.model"],
                    "in_tok": attrs["gen_ai.usage.input_tokens"],
                    "out_tok": attrs["gen_ai.usage.output_tokens"],
                })
    return by_session


class TempoBackend:  # pragma: no cover - the HTTP path needs a running backend + requests
    """Queries a Grafana Tempo backend over HTTP and reconstructs per-session steps with
    `parse_tempo_search`. The reconstruction mirrors JsonlBackend, so the eval loop is identical;
    only the source of the JSON changes."""
    def __init__(self, endpoint: str, query: str = '{ name = "gen_ai.chat" }'):
        import requests  # noqa: F401
        self.endpoint = endpoint.rstrip("/")
        self.query = query

    def read_sessions(self) -> dict:
        import requests
        resp = requests.get(f"{self.endpoint}/api/search", params={"q": self.query}, timeout=30)
        resp.raise_for_status()
        return parse_tempo_search(resp.json())


def run_eval_loop(backend: TraceBackend) -> dict:
    sessions = backend.read_sessions()
    return {"sessions": len(sessions),
            "total_cost": sum(token_cost(steps) for steps in sessions.values())}


def _self_test() -> int:
    # 1) JsonlBackend reproduces the eval cost from the exported store
    sessions = _synthetic_sessions()
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "trace_store.jsonl")
        export_to_store(sessions, store)
        result = run_eval_loop(JsonlBackend(store))
        source_cost = sum(token_cost(s["steps"]) for s in sessions)
        assert result["sessions"] == len(sessions) and abs(result["total_cost"] - source_cost) < 1e-9

    # 2) the Tempo parser reads the real search-response schema (recorded fixture)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "tempo_search_fixture.json")) as f:
        payload = json.load(f)
    parsed = parse_tempo_search(payload)
    assert set(parsed) == {"sess-1", "sess-2"}, parsed
    assert len(parsed["sess-1"]) == 2 and len(parsed["sess-2"]) == 1
    assert sum(s["in_tok"] for s in parsed["sess-1"]) == 1500            # ints parsed from OTLP strings
    assert parsed["sess-2"][0]["model"] == "sonnet"
    tempo_cost = sum(token_cost(steps) for steps in parsed.values())

    print(f"self-test: JsonlBackend reproduced eval cost ${result['total_cost']:.2f}; Tempo parser "
          f"read {sum(len(v) for v in parsed.values())} spans -> {len(parsed)} sessions from the real "
          f"search schema (cost ${tempo_cost:.2f}) OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Pluggable trace backend (JSONL + real Tempo schema)")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("import JsonlBackend / TempoBackend / parse_tempo_search / run_eval_loop, or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
