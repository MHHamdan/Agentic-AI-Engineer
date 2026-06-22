#!/usr/bin/env python3
"""Embeddings from counts (Lab 01).

An embedding turns a token into a vector so that "close in meaning" becomes "close in space." You do
not need a neural network to see the idea: the distributional hypothesis says words used in similar
contexts have similar meanings, so a word's co-occurrence counts already are an embedding. This
builds that from scratch, then fixes its obvious flaw - raw counts are dominated by frequent words
like "the" - with Positive Pointwise Mutual Information (PPMI), and shows cosine similarity then
ranks related words above unrelated ones.

This is the conceptual ancestor of modern dense embeddings (word2vec, and the encoders behind
retrieval); the geometry - cosine similarity over vectors - is identical. Deterministic, offline,
standard-library only.

References: Harris (1954), Distributional Structure; Mikolov et al. (2013), arXiv:1301.3781;
Levy & Goldberg (2014), Neural Word Embedding as Implicit Matrix Factorization.

Usage:
    python embeddings.py --self-test
"""
from __future__ import annotations

import argparse
import math
import sys

CORPUS = [
    "the cat ate the food", "the dog ate the food", "the cat is a pet",
    "the dog is a pet", "i drive the car", "the car is on the road",
    "the car needs fuel", "the pet ate food",
]


def cooccurrence(sentences: list[str], window: int = 2):
    toks = [s.split() for s in sentences]
    vocab = sorted({w for s in toks for w in s})
    idx = {w: i for i, w in enumerate(vocab)}
    n = len(vocab)
    co = [[0.0] * n for _ in range(n)]
    for s in toks:
        for i, w in enumerate(s):
            lo, hi = max(0, i - window), min(len(s), i + window + 1)
            for j in range(lo, hi):
                if j != i:
                    co[idx[w]][idx[s[j]]] += 1.0
    return co, idx


def ppmi(co: list[list[float]]) -> list[list[float]]:
    """Positive PMI re-weights counts: a pair matters when it co-occurs more than chance would
    predict, which suppresses ubiquitous words and surfaces meaningful associations."""
    n = len(co)
    total = sum(sum(r) for r in co) or 1.0
    row = [sum(r) for r in co]
    col = [sum(co[i][j] for i in range(n)) for j in range(n)]
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if co[i][j] > 0 and row[i] > 0 and col[j] > 0:
                p = co[i][j] / total
                pmi = math.log(p / ((row[i] / total) * (col[j] / total)))
                out[i][j] = max(pmi, 0.0)
    return out


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class Embeddings:
    def __init__(self, sentences=CORPUS, window=2, weighting="ppmi"):
        co, self.idx = cooccurrence(sentences, window)
        self.matrix = ppmi(co) if weighting == "ppmi" else co
        self.weighting = weighting

    def vector(self, word: str) -> list[float]:
        return self.matrix[self.idx[word]]

    def similarity(self, a: str, b: str) -> float:
        return cosine(self.vector(a), self.vector(b))

    def nearest(self, word: str, k: int = 3):
        sims = [(w, self.similarity(word, w)) for w in self.idx if w != word]
        return sorted(sims, key=lambda x: x[1], reverse=True)[:k]


def _self_test() -> int:
    raw = Embeddings(weighting="raw")
    weighted = Embeddings(weighting="ppmi")

    # the distributional signal: related words (shared contexts) beat unrelated ones, both weightings
    for emb in (raw, weighted):
        assert emb.similarity("cat", "dog") > emb.similarity("cat", "car"), emb.weighting

    # PPMI sharpens the contrast by suppressing frequent words like "the"
    raw_gap = raw.similarity("cat", "dog") - raw.similarity("cat", "car")
    ppmi_gap = weighted.similarity("cat", "dog") - weighted.similarity("cat", "car")
    assert ppmi_gap > raw_gap, (raw_gap, ppmi_gap)

    # cosine is bounded and symmetric
    s = weighted.similarity("cat", "dog")
    assert -1e-9 <= s <= 1 + 1e-9
    assert abs(weighted.similarity("car", "cat") - weighted.similarity("cat", "car")) < 1e-12

    # the nearest neighbor of "cat" is a fellow pet, not "car"
    top = weighted.nearest("cat", k=1)[0][0]
    assert top in {"dog", "pet"}, top

    print(f"self-test: related>unrelated for raw and PPMI; PPMI widens the gap "
          f"{raw_gap:.2f} -> {ppmi_gap:.2f} (suppresses 'the'); cos(cat,car) {raw.similarity('cat','car'):.2f}"
          f" -> {weighted.similarity('cat','car'):.2f}; nearest('cat')='{top}' OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Embeddings from co-occurrence counts")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--nearest", metavar="WORD")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    emb = Embeddings()
    if args.nearest:
        for w, s in emb.nearest(args.nearest):
            print(f"  {w:6} {s:.3f}")
    else:
        for a, b in [("cat", "dog"), ("cat", "car"), ("car", "road")]:
            print(f"  cos({a},{b}) = {emb.similarity(a, b):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
