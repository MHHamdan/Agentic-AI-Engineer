#!/usr/bin/env python3
"""Comparing the optimism curve across embedders (Lab 59; extended in Batch 85).

The suggested-next item was to instantiate a real sentence-transformer and compare its optimism
curve to the stand-in's. The real model download needs network, so this ships:

  1. a real, offline, model-free dense embedder - the hashing trick (`hashing_embed`) - so the
     three-way comparison runs now with genuinely different geometry, and
  2. a `SentenceTransformerEmbedder` adapter (guarded) that drops straight into the same comparison
     once a model is available.

The lesson holds across all of them: a different embedding geometry separates reflows from edits
differently, so it overfits the threshold by a different amount at small n even though every
embedder converges to the same held-out accuracy. The label budget is embedder-specific.

Usage:
    python compare.py --self-test
    python compare.py --real-embedder MODEL_NAME   # if sentence-transformers + a model are present
"""
from __future__ import annotations

import argparse
import hashlib
import math
import sys

from retune import embed as trigram_embed
from retune import optimism_curve


def word_bag_embed(text: str) -> dict:
    v: dict[str, int] = {}
    for w in text.lower().split():
        v[w] = v.get(w, 0) + 1
    return v


def hashing_embed(text: str, dim: int = 256, ngram: int = 3) -> dict:
    """The hashing trick: map char n-grams into a fixed-dim dense vector with signed buckets. A
    real, model-free dense embedding - deterministic (blake2b), no training, no download."""
    t = " ".join(text.lower().split())
    vec = [0.0] * dim
    grams = [t[i:i + ngram] for i in range(max(len(t) - ngram + 1, 0))] or [t]
    for g in grams:
        h = int.from_bytes(hashlib.blake2b(g.encode(), digest_size=8).digest(), "big")
        vec[h % dim] += 1.0 if (h >> 1) & 1 else -1.0
    return {i: v for i, v in enumerate(vec) if v != 0.0}


class SentenceTransformerEmbedder:  # pragma: no cover - needs the model download
    """Adapter that makes a real sentence-transformer callable like the offline embedders. Lazy-
    loads the model on first call; raises a clear error if the dependency/model is unavailable."""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _ensure(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def __call__(self, text: str) -> dict:
        vec = self._ensure().encode(text, normalize_embeddings=True)
        return {i: float(x) for i, x in enumerate(vec)}

    @staticmethod
    def available() -> bool:
        try:
            import sentence_transformers  # noqa: F401
            return True
        except Exception:
            return False


def compare(embedders: dict) -> dict:
    """`embedders` maps name -> callable(text)->vector. Returns each one's optimism curve.
    Reuses Lab 59's pair construction via `optimism_curve` on rebuilt pairs."""
    return {name: optimism_curve(_pairs_with(fn)) for name, fn in embedders.items()}


def _cosine(u: dict, v: dict) -> float:
    dot = sum(u[k] * v.get(k, 0) for k in u)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0


def _pairs_with(embed_fn) -> list[tuple[float, int]]:
    templates = ["Dr. {p} leads the {org} and works on {topic}",
                 "The {org} funds the {proj} and the {cons}",
                 "Dr. {p} is the lead engineer on the {proj} at {org}",
                 "{org} funds the {proj} internally as an industry lab"]
    P = ["Aanya Rao", "Lena Fischer", "Priya Nair", "Tomas Vega", "Marco Ruiz", "Sofia Bianchi"]
    ORG = ["Helix Lab", "Meridian Institute", "Atlas Systems"]
    PROJ = ["Prism Project", "Lattice Project", "Sentinel Project"]
    TOPIC = ["retrieval systems", "graph indexing", "ranking models"]
    CONS = ["Cascade Consortium", "Northgate Alliance"]
    syn = {"leads": "heads", "works on": "focuses on", "lead engineer": "principal engineer",
           "funds": "finances", "internally": "in-house"}
    swap = {"Aanya": "Tomas", "Lena": "Marco", "Priya": "Sofia", "Helix": "Vortex",
            "Meridian": "Halcyon", "Atlas": "Orion", "Prism": "Quartz", "Lattice": "Trellis"}

    def rewrap(s):
        w = s.split()
        return "\n".join(" ".join(w[i:i + 4]) for i in range(0, len(w), 4))
    def paraphrase(s):
        for a, b in syn.items():
            s = s.replace(a, b)
        return s
    def edit(s):
        for a, b in swap.items():
            if a in s:
                return s.replace(a, b, 1)
        return s
    def negate(s):
        return s.replace("funds", "does not fund").replace("leads", "does not lead").replace("is the", "is not the")

    pairs = []
    i = 0
    for t in templates:
        for p in P:
            for org in ORG:
                s = t.format(
                    p=p,
                    org=org,
                    topic=TOPIC[i % 3],
                    proj=PROJ[i % 3],
                    cons=CONS[i % 2],
                )
                i += 1
                pairs += [(s, rewrap(s), 0), (s, edit(s), 1)]
                if i % 2 == 0:
                    pairs.append((s, paraphrase(rewrap(s)), 0))
                if i % 3 == 0 and any(k in s for k in ("funds", "leads", "is the")):
                    pairs.append((s, negate(s), 1))
    return [(_cosine(embed_fn(a), embed_fn(b)), lbl) for a, b, lbl in pairs]


_DEFAULT = {"char-trigram": trigram_embed, "word-bag": word_bag_embed, "hashing-dense": hashing_embed}


def _self_test() -> int:
    curves = compare(_DEFAULT)
    smalls = {}
    for name, curve in curves.items():
        sizes = sorted(curve)
        small, large = sizes[0], sizes[-1]
        assert curve[small]["optimism"] > curve[large]["optimism"], (name, curve)  # shrinks with n
        assert curve[large]["optimism"] < 0.01, (name, curve)                       # vanishes
        smalls[name] = curve[small]["optimism"]
    # three distinct geometries -> three distinct optimism magnitudes at the smallest n
    vals = sorted(smalls.values())
    assert vals[-1] - vals[0] > 0.01, smalls
    assert len({round(v, 3) for v in smalls.values()}) >= 2, smalls
    print("self-test: optimism at n=16 - " +
          ", ".join(f"{k} {v:+.3f}" for k, v in smalls.items()) +
          f"; all vanish by n={sorted(next(iter(curves.values())))[-1]}; ST adapter available: "
          f"{SentenceTransformerEmbedder.available()} OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare optimism curves across embedders")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--real-embedder", metavar="MODEL")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    embedders = dict(_DEFAULT)
    if args.real_embedder:
        if SentenceTransformerEmbedder.available():
            embedders[f"st:{args.real_embedder}"] = SentenceTransformerEmbedder(args.real_embedder)
        else:
            print("sentence-transformers not installed; running offline embedders only")
    for name, curve in compare(embedders).items():
        print(f"{name}:")
        for n, r in curve.items():
            print(f"  n={n:3d}  optimism {r['optimism']:+.3f}  held-out {r['held_out']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
