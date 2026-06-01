#!/usr/bin/env python3
"""A fixed canary set the drift check and nightly job always include (Lab 42, item 4).

Volume-based signals go dark on a quiet day: if little traffic arrives, the drift
window is thin and the nightly eval set may be stale, so a sudden break slips through.
A small fixed canary set - known queries with known routes and reference answers -
gives both jobs a constant heartbeat. If a canary's route flips or its answer breaks,
something regressed regardless of traffic.

Usage:
    python canary.py --self-test
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CANARIES = HERE / "canary_queries.jsonl"


def load_canaries() -> list[dict]:
    with open(CANARIES) as f:
        return [json.loads(line) for line in f]


def augment_window(window: list[dict], canaries: list[dict]) -> list[dict]:
    """Prepend canaries so the drift window is never empty/quiet. Pure."""
    return [{"query": c["query"]} for c in canaries] + window


def canary_routing_failures(predicted: list[str], canaries: list[dict]) -> list[dict]:
    """Pure: canaries whose predicted route != gold. A non-empty list = a hard break,
    independent of any threshold - these should fail loudly."""
    out = []
    for pred, c in zip(predicted, canaries, strict=False):
        if pred != c["route"]:
            out.append({"query": c["query"], "expected": c["route"], "got": pred})
    return out


def predict_canary_routes() -> list[str]:
    """Route the canary queries with the current model (needs embedder)."""
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    with open(HERE.parent / "36-training-the-router" / "router_trainset.jsonl") as f:
        train = [json.loads(line) for line in f]
    cans = load_canaries()
    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    clf = LogisticRegression(max_iter=2000, C=10, class_weight="balanced").fit(
        emb.encode([r["query"] for r in train], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False),
        [r["route"] for r in train])
    return clf.predict(emb.encode([c["query"] for c in cans], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)).tolist()


def _self_test() -> int:
    cans = load_canaries()
    assert len(cans) >= 8 and all("route" in c and "reference" in c for c in cans)
    aug = augment_window([{"query": "live one"}], cans)
    assert len(aug) == len(cans) + 1 and aug[-1]["query"] == "live one"
    # routing-failure detection
    preds = [c["route"] for c in cans]
    preds[0] = "parametric"  # simulate one flip
    fails = canary_routing_failures(preds, cans)
    assert len(fails) == 1 and fails[0]["got"] == "parametric", fails
    assert canary_routing_failures([c["route"] for c in cans], cans) == []
    print("self-test: load + augment_window + canary_routing_failures OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Canary set helper")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    fails = canary_routing_failures(predict_canary_routes(), load_canaries())
    if fails:
        print(f"CANARY ROUTING FAILURES ({len(fails)}):")
        for f in fails:
            print(f"  {f['query']!r}: expected {f['expected']}, got {f['got']}")
        return 2
    print(f"all {len(load_canaries())} canaries route correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
