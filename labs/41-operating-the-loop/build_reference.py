#!/usr/bin/env python3
"""Distill a larger clean held-out reference from real captured traffic (Lab 46, item 2).

Lab 44's reference was 16 curated queries - enough to teach, too few to trust. A 16-query
band has a wide confidence interval, so the drift check inherits that uncertainty. In
production you collect real traffic, filter it to clean held-out candidates (drop garbage,
near-duplicates, and anything verbatim in the trainset), verify them, and stratify by route.
A larger, representative sample gives a tighter band.

Usage:
    python build_reference.py            # distill captured_traffic.jsonl -> reference
    python build_reference.py --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAPTURED = HERE / "captured_traffic.jsonl"
TRAINSET = HERE.parent / "36-training-the-router" / "router_trainset.jsonl"
OUT = HERE / "reference_sample.jsonl"


def _norm(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip().lower())


def clean_candidates(captured: list[dict], trainset_queries: set[str], min_words: int = 2) -> list[dict]:
    """Filter raw traffic to clean held-out candidates: drop short/garbage, drop anything
    verbatim in the trainset (must be HELD OUT), and de-duplicate on normalized text."""
    train_norm = {_norm(q) for q in trainset_queries}
    seen, out = set(), []
    for r in captured:
        q = r.get("query", "")
        n = _norm(q)
        if len(n.split()) < min_words:      # too short / garbage
            continue
        if n in train_norm:                  # leaked from the trainset - not held out
            continue
        if n in seen:                        # duplicate
            continue
        seen.add(n)
        out.append(r)
    return out


def stratify(candidates: list[dict], per_route: int) -> list[dict]:
    """Balance the reference across routes so no route dominates the band."""
    by_route: dict[str, list[dict]] = {}
    for r in candidates:
        by_route.setdefault(r["route"], []).append(r)
    out = []
    for _route, rows in by_route.items():
        out.extend(rows[:per_route])
    return out


def band_ci(confidences: list[float], z: float = 1.96) -> dict:
    """Confidence interval for the band mean. SE = std / sqrt(n): a larger clean sample
    narrows the interval, which is the whole reason to collect more than 16."""
    n = len(confidences)
    mean = statistics.mean(confidences)
    sd = statistics.stdev(confidences) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": round(mean, 3), "ci_low": round(mean - z * se, 3),
            "ci_high": round(mean + z * se, 3), "ci_width": round(2 * z * se, 3)}


def _self_test() -> int:
    train = {"what does rag stand for"}     # pretend this one is in the trainset
    captured = [
        {"query": "who runs helix now", "route": "specific"},
        {"query": "Who Runs  Helix Now", "route": "specific"},   # near-dupe -> dropped
        {"query": "what does rag stand for", "route": "parametric"},  # trainset -> dropped
        {"query": "?", "route": "parametric"},                   # garbage -> dropped
        {"query": "summarize the structure", "route": "global"},
    ]
    cand = clean_candidates(captured, train)
    qs = [_norm(c["query"]) for c in cand]
    assert qs == ["who runs helix now", "summarize the structure"], qs
    # stratify caps per route
    strat = stratify([{"query": f"q{i}", "route": "specific"} for i in range(5)] +
                     [{"query": "g", "route": "global"}], per_route=3)
    assert sum(1 for r in strat if r["route"] == "specific") == 3
    # CI narrows as n grows (same spread, more samples)
    small = band_ci([0.80, 0.78, 0.83, 0.76] * 4)        # n=16
    big = band_ci([0.80, 0.78, 0.83, 0.76] * 20)         # n=80
    assert big["ci_width"] < small["ci_width"], (small, big)
    print(f"self-test: clean_candidates + stratify + band_ci (n16 width {small['ci_width']} "
          f"> n80 width {big['ci_width']}) OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Distill a clean held-out reference from traffic")
    ap.add_argument("--per-route", type=int, default=12)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    with open(CAPTURED) as f:
        captured = [json.loads(line) for line in f]
    with open(TRAINSET) as f:
        trainset = {json.loads(line)["query"] for line in f}
    cand = clean_candidates(captured, trainset)
    ref = stratify(cand, per_route=args.per_route)
    OUT.write_text("".join(json.dumps({"query": r["query"], "route": r["route"], "clean": True}) + "\n"
                           for r in ref))
    print(f"captured {len(captured)} -> cleaned {len(cand)} -> stratified reference {len(ref)} "
          f"(wrote {OUT.name})")
    print("verify these by hand (or with the live model) before trusting the band.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
