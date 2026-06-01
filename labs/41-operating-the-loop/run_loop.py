#!/usr/bin/env python3
"""Orchestrate the maintenance loop around its human gate (Lab 41, item 4).

You cannot fully automate a loop with a human-judgment step in the middle. So the
"loop on a cadence" is scheduled automation of the deterministic parts with an
explicit human gate:

  prepare  (scheduled)  -> capture window -> dedup -> confidence triage -> write a
                           review queue artifact + a promote plan; STOP for humans.
  -- humans label the review queue --
  promote  (manual)     -> merge reviewed labels -> retrain -> measure A vs B on a
                           held-out messy slice -> PROMOTE only on a real lift ->
                           re-derive the Lab 38 baseline.

This module holds the pure decisions (triage split, promotion gate, phase wiring);
the heavy embed/train steps live behind functions. --self-test covers the decisions.

Usage:
    python run_loop.py --phase prepare --window recent.jsonl
    python run_loop.py --phase promote --reviewed reviewed.jsonl
    python run_loop.py --self-test
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def triage_split(items_with_conf: list[tuple[dict, float]], threshold: float = 0.50):
    """Pure: split (item, confidence) pairs into auto-accept and human-review."""
    auto = [it for it, c in items_with_conf if c >= threshold]
    review = [it for it, c in items_with_conf if c < threshold]
    return auto, review


def should_promote(acc_baseline: float, acc_candidate: float, min_lift: float = 0.0) -> bool:
    """Pure promotion gate: ship the retrained model only on a measured lift above a
    margin. min_lift > 0 guards against promoting on noise."""
    return (acc_candidate - acc_baseline) > min_lift


def phase_prepare(window_path: str) -> dict:
    """Automatable front half: capture -> dedup -> triage -> emit review queue."""
    import re

    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    with open(HERE.parent / "36-training-the-router" / "router_trainset.jsonl") as f:
        train = [json.loads(line) for line in f]
    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    clf = LogisticRegression(max_iter=2000, C=10, class_weight="balanced").fit(
        emb.encode([r["query"] for r in train], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False),
        [r["route"] for r in train])
    with open(window_path) as f:
        raw = [json.loads(line) for line in f]
    # dedup by normalized string
    seen, uniq = set(), []
    for r in raw:
        key = re.sub(r"[^a-z0-9 ]", "", r["query"].lower()).strip()
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    conf = clf.predict_proba(emb.encode([r["query"] for r in uniq], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)).max(axis=1)
    auto, review = triage_split(list(zip(uniq, conf, strict=False)))
    (HERE / "review_queue.jsonl").write_text("".join(json.dumps(r) + "\n" for r in review))
    return {"captured": len(raw), "unique": len(uniq), "auto_accept": len(auto), "to_review": len(review)}


def _self_test() -> int:
    auto, review = triage_split([({"q": 1}, 0.9), ({"q": 2}, 0.3), ({"q": 3}, 0.5)])
    assert len(auto) == 2 and len(review) == 1, (auto, review)
    assert should_promote(0.80, 0.86, 0.02) and not should_promote(0.80, 0.81, 0.02)
    assert not should_promote(0.80, 0.78, 0.0)  # regression never promotes
    print("self-test: triage_split() + should_promote() OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Maintenance-loop orchestrator")
    ap.add_argument("--phase", choices=["prepare", "promote"])
    ap.add_argument("--window", help="recent queries (prepare)")
    ap.add_argument("--reviewed", help="human-labeled queue (promote)")
    ap.add_argument("--min-lift", type=float, default=0.02)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()

    if args.phase == "prepare":
        if not args.window:
            print("prepare needs --window")
            return 1
        report = phase_prepare(args.window)
        print(json.dumps(report, indent=2))
        print(f"\nwrote review_queue.jsonl ({report['to_review']} items). Humans label it, then:")
        print("  python run_loop.py --phase promote --reviewed review_queue.jsonl")
        return 0

    if args.phase == "promote":
        # The promote phase (retrain + measure) reuses Lab 39's notebook logic and is
        # gated by should_promote(); see the lab notebook for the worked measurement.
        # On a promote, two baselines must be refreshed so neither drifts out from under
        # its check: the eval-gate thresholds (Lab 38) and the drift baseline (Lab 42).
        print("promote: retrain on reviewed labels, measure A vs B, gate on should_promote().")
        print("On promotion, refresh BOTH baselines:")
        print("  python ../38-calibrating-the-eval-gate/derive_thresholds.py   # gate thresholds")
        print("  python record_baseline.py                                     # drift baseline")
        try:
            import record_baseline  # noqa: F401  (re-records confidence_baseline.json)
            print("(record_baseline importable: promote will refresh the drift baseline)")
        except Exception:
            pass
        return 0

    print("specify --phase prepare|promote (or --self-test)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
