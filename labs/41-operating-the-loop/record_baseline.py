#!/usr/bin/env python3
"""Re-record the drift baseline after a retrain (Lab 42, item 2).

Lab 41's drift check compared live confidence against a hardcoded baseline. The moment
you promote a retrained router, that constant is stale - the new model has its own
confidence distribution. This recomputes the baseline (mean, std of router confidence
on a reference set) and writes confidence_baseline.json, which drift_check.py reads.
The promote phase calls this so the baseline can never drift out from under the check.

Usage:
    python record_baseline.py                 # measure on the prototype reference set
    python record_baseline.py --self-test      # stats only, offline
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "confidence_baseline.json"


def compute_baseline(confidences: list[float]) -> dict:
    """Pure: summarize a reference set's router confidences into a baseline band."""
    if len(confidences) < 2:
        raise ValueError("need at least 2 confidences for a std")
    return {"mean": round(statistics.mean(confidences), 3),
            "std": round(statistics.stdev(confidences), 3),
            "n": len(confidences)}


def measure_reference_confidences() -> list[float]:
    """Route a reference set with the current model and return confidences (needs embedder).
    Uses the prototype trainset as the reference 'clean' distribution."""
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    with open(HERE.parent / "36-training-the-router" / "router_trainset.jsonl") as f:
        train = [json.loads(line) for line in f]
    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    X = emb.encode([r["query"] for r in train], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    clf = LogisticRegression(max_iter=2000, C=10, class_weight="balanced").fit(X, [r["route"] for r in train])
    return clf.predict_proba(X).max(axis=1).tolist()


def write_baseline(stats: dict) -> pathlib.Path:
    stats = {**stats, "recorded_at": datetime.date.today().isoformat(),
             "note": "router-confidence baseline; re-recorded on promote (Lab 42)"}
    OUT.write_text(json.dumps(stats, indent=2) + "\n")
    return OUT


def _self_test() -> int:
    b = compute_baseline([0.80, 0.78, 0.82, 0.79, 0.81])
    assert b["n"] == 5 and 0.79 <= b["mean"] <= 0.81 and b["std"] > 0
    try:
        compute_baseline([0.8])
        raise AssertionError("compute_baseline should reject n < 2")
    except ValueError:
        pass
    print("self-test: compute_baseline() OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-record the drift baseline")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    stats = compute_baseline(measure_reference_confidences())
    path = write_baseline(stats)
    print(f"wrote {path.name}: {json.dumps(stats)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
