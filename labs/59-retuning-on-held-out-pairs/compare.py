#!/usr/bin/env python3
"""Comparing the optimism curve across embedders (Lab 59, Batch 84).

The suggested-next item was: instantiate a real sentence-transformer, re-tune, and compare the
optimism curve to the stand-in's. The real model is guarded (its download needs network), but the
comparison itself is the point and it works with any pair of embedders: a different embedding
geometry separates reflows from edits differently, so it overfits the threshold by a different
amount and needs a different label budget.

This compares the char-trigram embedder (Lab 59's default) against a word-bag embedder on the same
text pairs, and exposes a `compare(embedders)` you point at a real `SentenceTransformerEmbedder`.

Usage:
    python compare.py --self-test
"""
from __future__ import annotations

import argparse
import math
import sys

from retune import embed as trigram_embed
from retune import optimism_curve


def word_bag_embed(text: str) -> dict:
    v: dict[str, int] = {}
    for w in text.lower().split():
        v[w] = v.get(w, 0) + 1
    return v


def _cosine(u: dict, v: dict) -> float:
    dot = sum(u[k] * v.get(k, 0) for k in u)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0


def _pairs_with(embed_fn) -> list[tuple[float, int]]:
    """Rebuild Lab 59's overlapping reflow/edit pairs, but embedded with `embed_fn`."""
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


def compare(embedders: dict) -> dict:
    """`embedders` maps name -> callable(text)->vector. Returns each one's optimism curve."""
    return {name: optimism_curve(_pairs_with(fn)) for name, fn in embedders.items()}


def real_embedder_note() -> str:
    try:
        from sentence_transformers import SentenceTransformer  # noqa: F401
        return "sentence-transformers importable - add it to `embedders` to compare its curve"
    except Exception:
        return "sentence-transformers not installed; comparison runs on the offline stand-ins"


def _self_test() -> int:
    curves = compare({"char-trigram": trigram_embed, "word-bag": word_bag_embed})
    for name, curve in curves.items():
        sizes = sorted(curve)
        small, large = sizes[0], sizes[-1]
        assert curve[small]["optimism"] > curve[large]["optimism"], (name, curve)  # shrinks with n
        assert curve[large]["optimism"] < 0.01, (name, curve)                       # vanishes
    # the two embedders overfit the threshold by DIFFERENT amounts at small n
    t = curves["char-trigram"]
    w = curves["word-bag"]
    smallest = sorted(t)[0]
    assert abs(t[smallest]["optimism"] - w[smallest]["optimism"]) > 0.005, (t[smallest], w[smallest])
    print(f"self-test: optimism at n={smallest} - char-trigram {t[smallest]['optimism']:+.3f} vs "
          f"word-bag {w[smallest]['optimism']:+.3f} (different geometry, different overfit); both vanish "
          f"by n={sorted(t)[-1]}. {real_embedder_note()} OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare optimism curves across embedders")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    curves = compare({"char-trigram": trigram_embed, "word-bag": word_bag_embed})
    for name, curve in curves.items():
        print(f"{name}:")
        for n, r in curve.items():
            print(f"  n={n:3d}  optimism {r['optimism']:+.3f}  held-out {r['held_out']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
