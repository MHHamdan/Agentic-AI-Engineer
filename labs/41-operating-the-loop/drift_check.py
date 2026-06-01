#!/usr/bin/env python3
"""Confidence-drift check on live traffic (Lab 41, item 2).

Lab 39 showed router confidence collapses on phrasing the trainset never saw. That
drop needs no labels, so it can run on live queries continuously. This script reads a
window of recent queries, computes the router's mean confidence, and flags "retrain
due" when the window sits below a baseline band -- the trigger that starts the Lab 39
loop.

Usage:
    python drift_check.py --window recent_queries.jsonl   # live check (needs router)
    python drift_check.py --self-test                      # decision logic only, offline

Reads confidence_baseline.json when present (re-recorded on promote, Lab 42) so the
band tracks the current model; --canaries always-include a fixed heartbeat set.

Exit code 0 = within band, 2 = retrain due (a distinct code so the scheduler can branch).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import statistics
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
# Recorded clean-confidence baseline (mean, std) from a reference run on prototypes.
# Re-record this whenever you retrain the router (see the maintenance loop).
BASELINE_MEAN = 0.79
BASELINE_STD = 0.06


BASELINE_FILE = HERE / "confidence_baseline.json"


def load_baseline() -> tuple[float, float]:
    """Prefer the recorded baseline (refreshed on promote); fall back to the constants
    so the check still runs before the first record_baseline."""
    if BASELINE_FILE.exists():
        with open(BASELINE_FILE) as f:
            b = json.load(f)
        return float(b["mean"]), float(b["std"])
    return BASELINE_MEAN, BASELINE_STD


def drift_status(window_conf: list[float], baseline_mean: float = BASELINE_MEAN,
                 baseline_std: float = BASELINE_STD, k: float = 2.0) -> dict:
    """Pure decision. 'retrain_due' when the window mean falls more than k*std below
    the baseline mean. Returns status, the window mean, and the z-distance."""
    if not window_conf:
        return {"status": "no_data", "mean": None, "z": None}
    m = statistics.mean(window_conf)
    band = baseline_mean - k * baseline_std
    z = (m - baseline_mean) / baseline_std if baseline_std else 0.0
    return {"status": "retrain_due" if m < band else "ok", "mean": round(m, 3),
            "z": round(z, 2), "band": round(band, 3)}


def window_confidences(path: str) -> list[float]:
    """Route a window of recent queries and return their max-proba confidences."""
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    with open(HERE.parent / "36-training-the-router" / "router_trainset.jsonl") as f:
        train = [json.loads(line) for line in f]
    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    Xtr = emb.encode([r["query"] for r in train], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    clf = LogisticRegression(max_iter=2000, C=10, class_weight="balanced").fit(Xtr, [r["route"] for r in train])
    with open(path) as f:
        queries = [json.loads(line)["query"] for line in f]
    Xw = emb.encode(queries, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    return clf.predict_proba(Xw).max(axis=1).tolist()


def _self_test() -> int:
    # healthy window near baseline -> ok
    assert drift_status([0.80, 0.78, 0.82, 0.79])["status"] == "ok"
    # collapsed window (messy traffic) -> retrain_due
    d = drift_status([0.45, 0.40, 0.38, 0.50])
    assert d["status"] == "retrain_due" and d["mean"] < d["band"], d
    # empty -> no_data
    assert drift_status([])["status"] == "no_data"
    # load_baseline falls back to constants when no file is present
    m, s = load_baseline()
    assert m > 0 and s > 0
    print("self-test: drift_status() + load_baseline() OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Confidence-drift check on live traffic")
    ap.add_argument("--window", help="JSONL of recent queries ({'query': ...})")
    ap.add_argument("--k", type=float, default=2.0)
    ap.add_argument("--canaries", default=None, help="canary_queries.jsonl to always include")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.window:
        print("provide --window recent_queries.jsonl (or --self-test)")
        return 1

    base_mean, base_std = load_baseline()
    window_path = args.window
    if args.canaries:
        # Always include canaries so a quiet-traffic day still has a heartbeat.
        rows = []
        if args.window:
            with open(args.window) as f:
                rows = [json.loads(line) for line in f]
        with open(args.canaries) as f:
            cans = [{"query": json.loads(line)["query"]} for line in f]
        fd, window_path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        with open(window_path, "w") as f:
            for r in cans + rows:
                f.write(json.dumps(r) + "\n")
    d = drift_status(window_confidences(window_path), base_mean, base_std, k=args.k)
    print(f"window mean confidence = {d['mean']} (baseline {base_mean}, band {d['band']}, z={d['z']})")
    print(f"status: {d['status']}")
    return 2 if d["status"] == "retrain_due" else 0


if __name__ == "__main__":
    sys.exit(main())
