#!/usr/bin/env python3
"""Per-session cost and latency observability (Lab 53).

Agent cost does not look like cloud cost. It accrues across three dimensions at once - input and
output tokens, session runtime, and tool calls - inside a single session, and the distribution is
heavy-tailed: most sessions are cheap and a few runaway loops dominate the bill. This module
accounts per-session cost, surfaces the tail (p90/p99, not the mean), detects runaway loops,
measures how much of the spend is re-sent context, and simulates model routing.

The rates are 2026 list prices (per million tokens) plus a session-runtime charge, used here to
make the arithmetic concrete; verify current prices before quoting them.

Usage:
    python cost.py --self-test
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

# (input_per_M, output_per_M) in USD, 2026 list prices
RATES = {"haiku": (1.0, 5.0), "sonnet": (3.0, 15.0), "opus": (5.0, 25.0)}
SESSION_HOUR = 0.08          # USD per session-hour of runtime
TOOL_CALL = 0.001            # USD per tool call (flat stand-in)
DATA = pathlib.Path(__file__).with_name("sessions.jsonl")


def step_token_cost(step: dict) -> float:
    rin, rout = RATES[step["model"]]
    return step["in_tok"] / 1e6 * rin + step["out_tok"] / 1e6 * rout


def session_cost(session: dict) -> float:
    tok = sum(step_token_cost(s) for s in session["steps"])
    runtime = sum(s["dur_s"] for s in session["steps"]) / 3600 * SESSION_HOUR
    tools = sum(1 for s in session["steps"] if s.get("tool")) * TOOL_CALL
    return tok + runtime + tools


def percentile(xs: list[float], p: float) -> float:
    """Linear-interpolated percentile (p in 0..100). Sorted copy; no numpy."""
    if not xs:
        return 0.0
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    rank = p / 100 * (len(s) - 1)
    lo = int(rank)
    frac = rank - lo
    return s[lo] if lo + 1 >= len(s) else s[lo] + frac * (s[lo + 1] - s[lo])


def cost_summary(sessions: list[dict]) -> dict:
    costs = [session_cost(s) for s in sessions]
    mean = sum(costs) / len(costs)
    return {"n": len(sessions), "mean": mean, "p50": percentile(costs, 50),
            "p90": percentile(costs, 90), "p99": percentile(costs, 99), "max": max(costs),
            "total": sum(costs)}


def detect_runaways(sessions: list[dict], loop_threshold: int = 10) -> list[str]:
    """Flag sessions that loop: the same tool-call signature repeated >= loop_threshold times.
    A repeated identical (tool, args) call is the signature of an agent stuck re-trying the same
    step - the pattern behind the weekend-long runaway sessions."""
    flagged = []
    for sess in sessions:
        sigs: dict[str, int] = {}
        for s in sess["steps"]:
            if s.get("tool"):
                sig = f"{s['tool']}:{s.get('args','')}"
                sigs[sig] = sigs.get(sig, 0) + 1
        if sigs and max(sigs.values()) >= loop_threshold:
            flagged.append(sess["id"])
    return flagged


def resent_context_fraction(sessions: list[dict]) -> float:
    """Fraction of all input tokens that are re-encoded history (each step re-sends the prior
    turns). This is the share of the bill spent re-reading what the model already saw."""
    total_in = sum(s["in_tok"] for sess in sessions for s in sess["steps"])
    resent = sum(s.get("history_tok", 0) for sess in sessions for s in sess["steps"])
    return resent / total_in if total_in else 0.0


def with_caching(sessions: list[dict], cache_frac: float = 0.8, cache_mult: float = 0.1) -> float:
    """Total cost if cache_frac of each step's history tokens bill at cache_mult of the input
    rate (prompt caching). Returns the new total cost."""
    total = 0.0
    for sess in sessions:
        for s in sess["steps"]:
            rin, rout = RATES[s["model"]]
            hist = s.get("history_tok", 0)
            cached = hist * cache_frac
            uncached_in = s["in_tok"] - cached
            total += (uncached_in / 1e6 * rin + cached / 1e6 * rin * cache_mult
                      + s["out_tok"] / 1e6 * rout)
        total += sum(s["dur_s"] for s in sess["steps"]) / 3600 * SESSION_HOUR
        total += sum(1 for s in sess["steps"] if s.get("tool")) * TOOL_CALL
    return total


def route_cheaper(sessions: list[dict], cheap_model: str = "haiku") -> float:
    """Total cost if every step flagged `simple` is routed to a cheaper model and only planning /
    judgment steps stay on the expensive one. Returns the new total cost."""
    total = 0.0
    for sess in sessions:
        for s in sess["steps"]:
            model = cheap_model if s.get("simple") else s["model"]
            rin, rout = RATES[model]
            total += s["in_tok"] / 1e6 * rin + s["out_tok"] / 1e6 * rout
        total += sum(s["dur_s"] for s in sess["steps"]) / 3600 * SESSION_HOUR
        total += sum(1 for s in sess["steps"] if s.get("tool")) * TOOL_CALL
    return total


def load_sessions(path: pathlib.Path = DATA) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _self_test() -> int:
    sessions = build_synthetic_sessions()
    summ = cost_summary(sessions)
    # 1) the tail dominates: p99 is many times the mean, so the mean hides the runaways
    assert summ["p99"] > 8 * summ["mean"], summ
    # 2) the runaway detector flags exactly the looping sessions
    flagged = detect_runaways(sessions)
    expected = [s["id"] for s in sessions if s.get("is_runaway")]
    assert set(flagged) == set(expected) and flagged, (flagged, expected)
    # 3) re-sent context is a large share of input tokens; on normal sessions it is the ~60%
    #    the literature reports, and the long runaway loops push the overall share even higher.
    normal = [s for s in sessions if not s.get("is_runaway")]
    resent_normal = resent_context_fraction(normal)
    resent_all = resent_context_fraction(sessions)
    assert 0.45 <= resent_normal <= 0.70, resent_normal
    assert resent_all > resent_normal, (resent_all, resent_normal)
    cached_total = with_caching(sessions)
    assert cached_total < summ["total"], (cached_total, summ["total"])
    # 4) routing routine steps to a cheaper model cuts the ROUTINE bill by >= 40%. (Routing does
    #    not help the runaways - those are expensive planning loops; loop detection is their fix.)
    normal_total = sum(session_cost(s) for s in normal)
    routed_normal = route_cheaper(normal)
    saving = 1 - routed_normal / normal_total
    assert saving >= 0.40, saving
    print(f"self-test: {summ['n']} sessions; mean ${summ['mean']:.2f} but p99 ${summ['p99']:.2f} "
          f"(tail {summ['p99']/summ['mean']:.0f}x); runaways {flagged}; re-sent context "
          f"{resent_normal:.0%} normal / {resent_all:.0%} overall; caching "
          f"${summ['total']:.0f}->${cached_total:.0f}; routing saves "
          f"{saving:.0%} OK")
    return 0


def build_synthetic_sessions() -> list[dict]:
    """Deterministic synthetic traces: 36 normal sessions and 4 runaway loops. Each step records
    model, input/output tokens, the re-sent history portion, a tool call, duration, and whether
    the step is `simple` (routable to a cheaper model)."""
    sessions = []
    for i in range(36):                                   # normal sessions
        n_steps = 4 + (i % 5)
        steps = []
        hist = 0
        for k in range(n_steps):
            base = 700                                    # fresh prompt tokens
            in_tok = base + hist
            simple = (k % 3 != 0)                         # ~2/3 of steps are routine lookups
            steps.append({"model": "opus",                # anti-pattern: everything on opus
                          "in_tok": in_tok, "out_tok": 180 + 20 * k, "history_tok": hist,
                          "tool": "search", "args": f"q{i}_{k}", "dur_s": 3 + k, "simple": simple})
            hist += 420                                   # history grows each turn
        sessions.append({"id": f"s{i:02d}", "steps": steps, "is_runaway": False})
    for j in range(4):                                    # runaway loops
        steps = []
        hist = 0
        for _k in range(45 + 5 * j):
            in_tok = 900 + hist
            steps.append({"model": "opus", "in_tok": in_tok, "out_tok": 300,
                          "history_tok": hist, "tool": "search", "args": "stuck_query",
                          "dur_s": 6, "simple": False})   # same (tool,args) every step = loop
            hist += 500
        sessions.append({"id": f"r{j:02d}", "steps": steps, "is_runaway": True})
    return sessions


def main() -> int:
    ap = argparse.ArgumentParser(description="Per-session cost and latency observability")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print(json.dumps(cost_summary(build_synthetic_sessions()), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
