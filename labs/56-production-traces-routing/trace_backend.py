#!/usr/bin/env python3
"""A pluggable trace backend for the eval service (Lab 56, Batch 84).

Batch 82's `eval_service.py` read spans from a JSONL stand-in. The suggested-next item was to query
a real trace backend instead. This module makes the backend a swappable dependency: the eval loop
calls `backend.read_sessions()` and does not care whether that is a JSONL file or a Tempo/Jaeger
HTTP query. `JsonlBackend` is the offline default; `TempoBackend` is guarded (it needs a running
backend and `requests`). Swapping one for the other does not change the eval loop.

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


class TempoBackend:  # pragma: no cover - needs a running backend + requests
    """Queries a Grafana Tempo (or any OTLP trace) backend over HTTP and reconstructs the same
    per-session step lists from the returned spans. The reconstruction mirrors JsonlBackend, so the
    eval loop is identical; only the source changes."""
    def __init__(self, endpoint: str, query: str = '{ name = "gen_ai.chat" }'):
        import requests  # noqa: F401
        self.endpoint = endpoint.rstrip("/")
        self.query = query

    def read_sessions(self) -> dict:
        import requests
        resp = requests.get(f"{self.endpoint}/api/search", params={"q": self.query}, timeout=30)
        resp.raise_for_status()
        by_session: dict[str, list[dict]] = {}
        for trace in resp.json().get("traces", []):
            for span in trace.get("spans", []):
                a = {kv["key"]: kv["value"] for kv in span.get("attributes", [])}
                sid = a.get("agent.session_id")
                if sid is None:
                    continue
                by_session.setdefault(sid, []).append({
                    "model": a["gen_ai.request.model"],
                    "in_tok": int(a["gen_ai.usage.input_tokens"]),
                    "out_tok": int(a["gen_ai.usage.output_tokens"]),
                })
        return by_session


def run_eval_loop(backend: TraceBackend) -> dict:
    """Backend-agnostic cost loop."""
    sessions = backend.read_sessions()
    return {"sessions": len(sessions),
            "total_cost": sum(token_cost(steps) for steps in sessions.values())}


def _self_test() -> int:
    sessions = _synthetic_sessions()
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "trace_store.jsonl")
        export_to_store(sessions, store)
        result = run_eval_loop(JsonlBackend(store))
        source_cost = sum(token_cost(s["steps"]) for s in sessions)
        assert result["sessions"] == len(sessions), result
        assert abs(result["total_cost"] - source_cost) < 1e-9, (result, source_cost)
    # TempoBackend is importable and presents the same interface (constructed lazily; not queried)
    assert hasattr(TempoBackend, "read_sessions")
    print(f"self-test: JsonlBackend ran the eval loop over the trace store and computed "
          f"${result['total_cost']:.2f} == source ${source_cost:.2f}; TempoBackend exposes the same "
          f"read_sessions interface (guarded) OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Pluggable trace backend for the eval service")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("import JsonlBackend / TempoBackend / run_eval_loop, or run --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
