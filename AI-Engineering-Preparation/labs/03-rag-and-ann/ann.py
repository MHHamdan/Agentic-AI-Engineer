#!/usr/bin/env python3
"""Exact vs. approximate nearest-neighbor search (Lab 03).

Retrieval finds the vectors closest to a query. Exact search compares the query against every stored
vector - correct, but linear in the size of the corpus, which does not scale. A vector database trades
a little accuracy for a large speedup with an approximate-nearest-neighbor (ANN) index. This builds the
inverted-file (IVF) idea from scratch: cluster the vectors, and at query time search only the few
clusters nearest the query instead of all of them. Then it measures the central tradeoff - recall vs.
how many vectors get scanned - as the number of probed clusters changes.

The result is the curve every vector-DB tuning knob rides: more probes means higher recall and more
work; fewer probes means faster and approximate. Deterministic (seeded), standard-library only.

References: Malkov & Yashunin (2016), HNSW, arXiv:1603.09320; Johnson et al. (2017), Billion-scale
similarity search (FAISS), arXiv:1702.08734; Jegou et al. (2011), Product Quantization.

Usage:
    python ann.py --self-test
    python ann.py --demo
"""
from __future__ import annotations

import argparse
import random
import sys

N, DIM, NLIST, K = 300, 16, 12, 5


def make_vectors(n: int, d: int, seed: int) -> list[list[float]]:
    """Clustered points, so nearest neighbors are local - the structure ANN indexes exploit."""
    rng = random.Random(seed)
    centers = [[rng.gauss(0, 3) for _ in range(d)] for _ in range(8)]
    pts = []
    for _ in range(n):
        c = rng.choice(centers)
        pts.append([c[i] + rng.gauss(0, 1) for i in range(d)])
    return pts


def _d2(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=False))


def exact_topk(q: list[float], pts: list[list[float]], k: int = K) -> list[int]:
    return [i for _, i in sorted((_d2(q, p), i) for i, p in enumerate(pts))[:k]]


def build_ivf(pts: list[list[float]], nlist: int = NLIST, seed: int = 0, iters: int = 10):
    """IVF training is k-means: learn nlist centroids, assign each vector to its nearest one. Seeded
    init and a fixed iteration count keep it reproducible."""
    rng = random.Random(seed)
    cent = [pts[i][:] for i in rng.sample(range(len(pts)), nlist)]
    for _ in range(iters):
        groups: list[list[list[float]]] = [[] for _ in range(nlist)]
        for p in pts:
            groups[min(range(nlist), key=lambda c: _d2(p, cent[c]))].append(p)
        for c in range(nlist):
            if groups[c]:
                cent[c] = [sum(col) / len(groups[c]) for col in zip(*groups[c], strict=False)]
    assign = [min(range(nlist), key=lambda c: _d2(p, cent[c])) for p in pts]
    return cent, assign


def ivf_search(q, pts, cent, assign, nprobe: int, k: int = K) -> tuple[list[int], int]:
    """Search only the nprobe clusters whose centroids are nearest the query."""
    probed = set(sorted(range(len(cent)), key=lambda c: _d2(q, cent[c]))[:nprobe])
    cand = [i for i, a in enumerate(assign) if a in probed]
    top = [i for _, i in sorted((_d2(q, pts[i]), i) for i in cand)[:k]]
    return top, len(cand)


def evaluate(nprobe: int, pts, cent, assign, queries, k: int = K) -> tuple[float, float]:
    recall = scanned = 0.0
    for q in queries:
        truth = set(exact_topk(q, pts, k))
        approx, n = ivf_search(q, pts, cent, assign, nprobe, k)
        recall += len(truth & set(approx)) / k
        scanned += n
    return recall / len(queries), scanned / len(queries)


def _self_test() -> int:
    pts = make_vectors(N, DIM, seed=0)
    cent, assign = build_ivf(pts, NLIST, seed=0)
    cent2, assign2 = build_ivf(pts, NLIST, seed=0)
    assert assign2 == assign and cent2 == cent  # deterministic index

    queries = make_vectors(40, DIM, seed=99)
    probes = [1, 2, 4, 8, NLIST]
    curve = [(p,) + evaluate(p, pts, cent, assign, queries) for p in probes]

    recalls = [r for _, r, _ in curve]
    assert all(recalls[i] <= recalls[i + 1] + 1e-9 for i in range(len(recalls) - 1))  # monotone in nprobe

    # probing every cluster reduces to exact search: perfect recall, all vectors scanned
    _, full_recall, full_scan = curve[-1]
    assert abs(full_recall - 1.0) < 1e-9 and abs(full_scan - N) < 1e-9

    # the payoff: one cluster already gives high recall while scanning a small fraction
    _, r1, s1 = curve[0]
    assert r1 >= 0.7 and s1 < N * 0.25, (r1, s1)

    print(f"self-test: deterministic IVF; recall monotone in nprobe; nprobe={NLIST} -> recall 1.00, "
          f"scans all {N}; nprobe=1 -> recall {r1:.2f} scanning only {s1:.0f}/{N} ({s1/N:.0%}) OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Exact vs. IVF approximate nearest-neighbor search")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    pts = make_vectors(N, DIM, seed=0)
    cent, assign = build_ivf(pts, NLIST, seed=0)
    queries = make_vectors(40, DIM, seed=99)
    print(f"IVF tradeoff (N={N}, nlist={NLIST}, k={K}):")
    print(f"  {'nprobe':>6}  {'recall@5':>9}  {'avg scanned':>12}")
    for p in [1, 2, 4, 8, NLIST]:
        r, s = evaluate(p, pts, cent, assign, queries)
        print(f"  {p:>6}  {r:>9.2f}  {s:>8.0f}/{N}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
