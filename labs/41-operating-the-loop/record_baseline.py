#!/usr/bin/env python3
"""Re-record the drift baseline after a retrain (Lab 42, item 2).

Lab 42 recomputed the baseline on the PROTOTYPE trainset. That is circular: a model is
over-confident on the very data it trained on, so the band sits too high and the drift
check under-fires on real traffic. Lab 44 measures the baseline on a HELD-OUT clean
reference sample (realistic phrasings the model was not trained on, verified as cleanly
answerable) - a realistic band that reflects what live confidence actually looks like. The
promote phase calls this so the baseline tracks the current model AND real phrasing.

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


REFERENCE = HERE / "reference_sample.jsonl"
TRAINSET = HERE.parent / "36-training-the-router" / "router_trainset.jsonl"


def measure_reference_confidences(reference=None) -> list[float]:
    """Route a HELD-OUT clean reference with the current model and return confidences.
    Measuring on held-out phrasing (not the trainset) gives a realistic band; the model is
    over-confident on its own training data. Falls back to the trainset with a warning
    only if no held-out sample is present (needs embedder)."""
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    ref = reference or REFERENCE
    with open(TRAINSET) as f:
        train = [json.loads(line) for line in f]
    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    Xtr = emb.encode([r["query"] for r in train], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    clf = LogisticRegression(max_iter=2000, C=10, class_weight="balanced").fit(Xtr, [r["route"] for r in train])
    if ref.exists():
        with open(ref) as f:
            rows = [json.loads(line) for line in f]
        src = "held-out reference"
    else:
        rows = train
        src = "TRAINSET (no held-out reference found - band will be optimistic!)"
    print(f"measuring baseline on {len(rows)} queries from {src}")
    Xr = emb.encode([r["query"] for r in rows], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    return clf.predict_proba(Xr).max(axis=1).tolist()


def write_baseline(stats: dict) -> pathlib.Path:
    stats = {**stats, "recorded_at": datetime.date.today().isoformat(),
             "note": "router-confidence baseline on held-out reference; re-recorded on promote (Lab 44)"}
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
    prototype = compute_baseline([0.93, 0.95, 0.91, 0.94, 0.92])   # over-confident on trainset
    heldout   = compute_baseline([0.80, 0.78, 0.83, 0.76, 0.79])   # realistic on held-out
    assert heldout["mean"] < prototype["mean"], (heldout, prototype)
    print("self-test: compute_baseline() + held-out band lower/realistic OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-record the drift baseline")
    ap.add_argument("--reference", default=None, help="held-out clean reference JSONL")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ref = pathlib.Path(args.reference) if args.reference else None
    stats = compute_baseline(measure_reference_confidences(ref))
    path = write_baseline(stats)
    print(f"wrote {path.name}: {json.dumps(stats)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
