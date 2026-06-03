#!/usr/bin/env python3
"""Measuring lost-in-the-middle (Lab 58).

Liu et al. (2023) showed that long-context models attend best to information at the start and end
of the context and worst in the middle - accuracy as a function of the gold passage's position is
U-shaped. For RAG this means a *perfect* retriever can still produce wrong answers if it places the
right passage in the middle of a long context. Mean accuracy hides this; you have to measure
accuracy *by position*.

This is the measurement methodology, runnable offline. `answer_correct` is a deterministic stand-in
whose correctness follows a U-shaped position bias (simulating a real long-context model); in
production you swap it for real model calls over your own corpus. The harness sweeps the gold
position, recovers the curve, and quantifies three mitigations: rerank-to-top, reduce-k, and
reporting by position instead of the mean.

Usage:
    python lostmiddle.py --self-test
"""
from __future__ import annotations

import argparse
import sys

# A fixed set of queries, each with a difficulty in [0,1). A query is answered correctly at a given
# gold position iff its difficulty is below the position's recall probability (the U-shaped curve).
N_QUERIES = 200


def _difficulties(n: int = N_QUERIES) -> list[float]:
    # deterministic, evenly spread in [0,1)
    return [(i + 0.5) / n for i in range(n)]


def recall_prob(pos: int, k: int, hi: float = 0.95, lo: float = 0.50, window: int = 5) -> float:
    """U-shaped recall as a function of gold position (1..k): high within `window` passages of
    either edge, decaying to `lo` in the middle. Using ABSOLUTE distance from the nearest edge (not
    normalized) is what makes the dead middle widen with k - so shrinking the context raises
    accuracy. Stand-in for a real long-context model's positional bias."""
    edge_distance = min(pos - 1, k - pos)        # 0 at either edge
    frac = min(1.0, edge_distance / window)      # 0 at edge, 1 once past the window
    return hi - (hi - lo) * frac


def answer_correct(difficulty: float, pos: int, k: int) -> bool:
    """Deterministic stand-in: correct iff the query is easy enough for this position's recall."""
    return difficulty < recall_prob(pos, k)


def position_sweep(k: int, queries: list[float] | None = None) -> dict[int, float]:
    """Accuracy at each gold position 1..k, averaged over the query set."""
    queries = queries or _difficulties()
    return {pos: sum(answer_correct(d, pos, k) for d in queries) / len(queries)
            for pos in range(1, k + 1)}


def mean_accuracy_random_placement(k: int, queries: list[float] | None = None) -> float:
    """A retriever that puts the gold passage at a uniformly random position: its mean accuracy is
    dragged down by the middle."""
    curve = position_sweep(k, queries)
    return sum(curve.values()) / len(curve)


def rerank_to_top_accuracy(k: int, queries: list[float] | None = None) -> float:
    """Mitigation: a reranker that always places the gold passage first."""
    queries = queries or _difficulties()
    return sum(answer_correct(d, 1, k) for d in queries) / len(queries)


def _self_test() -> int:
    K = 20
    curve = position_sweep(K)
    edges = (curve[1] + curve[K]) / 2
    middle = curve[K // 2]
    # 1) the curve is U-shaped: edges clearly beat the middle
    assert edges - middle > 0.25, (edges, middle)
    assert curve[1] > curve[K // 2] < curve[K], curve   # both ends above the middle

    # 2) mean accuracy hides the position bias - it sits well below the edge accuracy
    mean = mean_accuracy_random_placement(K)
    assert mean < edges - 0.10, (mean, edges)

    # 3) rerank-to-top recovers accuracy to the edge level
    top = rerank_to_top_accuracy(K)
    assert top >= edges - 1e-9 and top - mean > 0.10, (top, mean)

    # 4) reducing k raises the middle accuracy (less context to get lost in)
    mid_long = position_sweep(40)[20]
    mid_short = position_sweep(6)[3]
    assert mid_short > mid_long, (mid_short, mid_long)

    print(f"self-test: k={K} position sweep - edges {edges:.2f} vs middle {middle:.2f} (U-shaped); "
          f"mean over random placement {mean:.2f} (hidden bias); rerank-to-top {top:.2f}; "
          f"middle accuracy rises {mid_long:.2f}->{mid_short:.2f} as k shrinks 40->6 OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure lost-in-the-middle position bias")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--k", type=int, default=20)
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    for pos, acc in position_sweep(args.k).items():
        print(f"  position {pos:2d}/{args.k}: {acc:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
