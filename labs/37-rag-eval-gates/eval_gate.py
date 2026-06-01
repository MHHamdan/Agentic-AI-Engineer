#!/usr/bin/env python3
"""Eval gate for the adaptive RAG router (Lab 37).

Blocking CI check: ROUTING accuracy of the trained classifier on a held-out eval
set. This is deterministic and needs no LLM, so it makes a stable gate. Answer
faithfulness via an LLM judge is intentionally NOT a blocking check here (it is
noisy and costs API calls) -- run that nightly and alert on trend instead.

Usage:
    python eval_gate.py                      # routing-accuracy gate (default thresholds)
    python eval_gate.py --route-min 0.85     # custom threshold
    python eval_gate.py --answer --judge     # also score answers (needs API key)
    python eval_gate.py --self-test          # gate() logic only
    no deps, no network

Exit code 0 = pass, 1 = regression (so CI fails the build).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

# Resolve paths relative to this file so the script runs from anywhere.
HERE = pathlib.Path(__file__).resolve().parent
TRAINSET = HERE.parent / "36-training-the-router" / "router_trainset.jsonl"
EVALSET = HERE.parent / "34-rag-pattern-head-to-head" / "eval_set.jsonl"
CORPUS = HERE.parent / "33-graph-rag-from-scratch" / "corpus"

CAT_TO_ROUTE = {
    "parametric": "parametric", "global-theme": "global", "multi-hop": "multihop",
    "off-corpus": "off_corpus_risk", "specific-lookup": "specific", "paraphrase": "specific",
}


def gate(metrics:
    dict, thresholds: dict) -> tuple[bool, list[str]]:
    """Pure threshold logic. Returns (passed, failures). Unit-testable, no I/O."""
    failures = []
    for key, minimum in thresholds.items():
        value = metrics.get(key)
        if value is None:
            failures.append(f"{key}: missing from metrics")
        elif value < minimum:
            failures.append(f"{key}={value:.3f} < required {minimum:.3f}")
    return (len(failures) == 0, failures)


def routing_accuracy() -> dict:
    """Train the classifier on the labeled set, score routing on the eval set.
    Deterministic given fixed inputs and model -- the blocking signal."""
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    with open(TRAINSET) as f:
        train = [json.loads(line) for line in f]
    with open(EVALSET) as f:
        eval_set = [json.loads(line) for line in f]
    embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

    Xtr = embedder.encode([r["query"] for r in train], normalize_embeddings=True,
                          convert_to_numpy=True, show_progress_bar=False)
    clf = LogisticRegression(max_iter=1000, C=10.0, class_weight="balanced").fit(
        Xtr, [r["route"] for r in train])

    Xev = embedder.encode([e["query"] for e in eval_set], normalize_embeddings=True,
                          convert_to_numpy=True, show_progress_bar=False)
    pred = clf.predict(Xev)
    truth = [CAT_TO_ROUTE[e["category"]] for e in eval_set]
    hits = sum(p == t for p, t in zip(pred, truth, strict=False))
    return {"routing_accuracy": hits / len(truth), "n": len(truth),
            "misroutes": [(e["query"], p, t) for e, p, t in zip(eval_set, pred, truth, strict=False) if p != t]}


def _self_test() -> int:
    """Exercise gate() without any heavy deps or network. Used by CI smoke + dev."""
    ok, fails = gate({"routing_accuracy": 0.94, "answer_accuracy": 0.81},
                     {"routing_accuracy": 0.85, "answer_accuracy": 0.75})
    assert ok and not fails, fails
    ok, fails = gate({"routing_accuracy": 0.69}, {"routing_accuracy": 0.85})
    assert not ok and len(fails) == 1, fails
    ok, fails = gate({}, {"routing_accuracy": 0.85})
    assert not ok and "missing" in fails[0], fails
    print("self-test: gate() logic OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Eval gate for the adaptive RAG router")
    ap.add_argument("--route-min", type=float, default=0.85, help="min routing accuracy")
    ap.add_argument("--self-test", action="store_true", help="test gate() logic only")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    metrics = routing_accuracy()
    passed, failures = gate(metrics, {"routing_accuracy": args.route_min})

    print(f"routing_accuracy = {metrics['routing_accuracy']:.3f} on {metrics['n']} eval queries "
          f"(threshold {args.route_min:.2f})")
    for q, p, t in metrics["misroutes"]:
        print(f"  misroute: {q[:50]!r} -> {p} (expected {t})")
    print("GATE:", "PASS" if passed else "FAIL")
    for f in failures:
        print("  -", f)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
