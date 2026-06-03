#!/usr/bin/env python3
"""Swappable embedders for the semantic fingerprint (Lab 55, Batch 82).

Lab 55 tuned the change-detection threshold with a deterministic char-trigram embedder so the lab
runs offline. The threshold-tuning procedure is embedder-agnostic; this module makes the embedder a
swappable dependency so you can drop in a real sentence-transformer and re-tune on your own pairs.

`CharTrigramEmbedder` is the offline default (re-using Lab 55's `embed`/`cosine`).
`SentenceTransformerEmbedder` wraps a real model behind a guarded import; `tune_with` re-runs the
ROC/Youden threshold selection with whichever embedder you pass.

Usage:
    python embedders.py --self-test
"""
from __future__ import annotations

import argparse
import math
import sys
from typing import Protocol

from calibrate import cosine as _dict_cosine
from calibrate import embed as _trigram_embed
from calibrate import make_change_pairs, tune_threshold


class Embedder(Protocol):
    def encode(self, text: str): ...
    def similarity(self, a, b) -> float: ...


class CharTrigramEmbedder:
    """Deterministic offline embedder (Lab 55's char-trigram bag). Vectors are sparse dicts."""
    def encode(self, text: str) -> dict:
        return _trigram_embed(text)

    def similarity(self, a: dict, b: dict) -> float:
        return _dict_cosine(a, b)


class SentenceTransformerEmbedder:
    """Real dense embedder. Construction is guarded so importing this module never requires the
    dependency; you only pay for it when you actually instantiate the class."""
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # pragma: no cover - heavy dep
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str):
        return self.model.encode(text, normalize_embeddings=True)

    def similarity(self, a, b) -> float:
        return float(sum(x * y for x, y in zip(a, b, strict=False)))  # cosine on normalized vectors


def tune_with(embedder: Embedder, pairs=None) -> dict:
    """Re-run the ROC/Youden threshold selection with any embedder. The procedure is identical to
    Lab 55; only the embedding behind the cosine changes."""
    pairs = pairs or make_change_pairs()
    cos_labels = [(embedder.similarity(embedder.encode(a), embedder.encode(b)), lbl)
                  for a, b, lbl in pairs]
    return tune_threshold(cos_labels)


def _self_test() -> int:
    # the char-trigram embedder reproduces Lab 55's tuned result through the swappable interface
    res = tune_with(CharTrigramEmbedder())
    assert res["tuned"]["acc"] > res["fixed_0_98"]["acc"], res
    assert res["fixed_0_98"]["fpr"] > res["tuned"]["fpr"], res
    # the real embedder is importable and only pulls its dependency on instantiation
    assert hasattr(SentenceTransformerEmbedder, "encode")
    try:
        SentenceTransformerEmbedder()
        backend = "sentence-transformers available"
    except Exception:
        backend = "sentence-transformers not installed (guarded; offline default used)"
    print(f"self-test: swappable embedder - char-trigram tuned acc {res['tuned']['acc']:.2f} "
          f"vs fixed 0.98 {res['fixed_0_98']['acc']:.2f}; real embedder {backend} OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Swappable embedders for the semantic fingerprint")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("import CharTrigramEmbedder / SentenceTransformerEmbedder, or run --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
