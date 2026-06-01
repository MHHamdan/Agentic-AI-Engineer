#!/usr/bin/env python3
"""Nightly judged-faithfulness monitor (Lab 38, item 2).

The blocking PR gate checks routing accuracy (cheap, deterministic). Judged
faithfulness is the opposite kind of signal: it needs LLM-judge calls, it is
noisy, and it costs money. So it does NOT belong on the PR path. This script runs
on a nightly schedule, scores faithfulness with the validated judge, writes a
trend line to the run summary, and flags (but does not block) a regression below
the baseline-derived threshold.

Usage:
    python nightly_faithfulness.py              # run (needs API key + judge from Lab 37)
    python nightly_faithfulness.py --self-test  # summary/threshold logic only, offline
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
THRESHOLDS = HERE / "gate_thresholds.json"
EVALSET = HERE.parent / "34-rag-pattern-head-to-head" / "eval_set.jsonl"


def load_threshold(name: str, default: float) -> float:
    if not THRESHOLDS.exists():
        return default
    with open(THRESHOLDS) as f:
        cfg = json.load(f)
    v = cfg.get(name)
    return float(v) if isinstance(v, (int, float)) else default


def summarize(faithfulness: float, threshold: float) -> tuple[str, bool]:
    """Pure: build the markdown trend line and decide whether it regressed.
    Returns (summary_markdown, regressed)."""
    regressed = faithfulness < threshold
    status = "🔴 BELOW threshold" if regressed else "🟢 within band"
    md = (f"### Nightly judged faithfulness\n\n"
          f"- faithfulness: **{faithfulness:.3f}**\n"
          f"- threshold (baseline-derived): {threshold:.3f}\n"
          f"- status: {status}\n")
    return md, regressed


def run_nightly() -> float:
    """Score faithfulness with the validated judge from Lab 37 over the eval set.
    Heavy (LLM calls); only the nightly schedule runs this."""
    sys.path.insert(0, str(HERE.parent / "37-rag-eval-gates"))
    from eval_gate import routing_accuracy  # noqa: F401  (ensures lab wiring is present)
    # In a real nightly you would: generate an answer per eval query with the router,
    # then call Lab 37's llm_judge(query, answer, reference) and average `faithful`.
    # That requires an API key and is intentionally not executed in CI smoke tests.
    raise RuntimeError("run_nightly needs an API key and Lab 37's judge; use the workflow")


def _self_test() -> int:
    md, reg = summarize(0.80, 0.764)
    assert not reg and "within band" in md, md
    md, reg = summarize(0.70, 0.764)
    assert reg and "BELOW" in md, md
    assert load_threshold("judged_faithfulness", 0.5) >= 0.0
    print("self-test: summarize() + load_threshold() OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Nightly judged-faithfulness monitor")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()

    threshold = load_threshold("judged_faithfulness", 0.75)
    faithfulness = run_nightly()
    md, regressed = summarize(faithfulness, threshold)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(md)
    print(md)
    # Non-blocking by design: exit 0 so a scheduled regression is visible in the
    # summary and via the workflow's regression step, without failing other work.
    return 0


if __name__ == "__main__":
    sys.exit(main())
