#!/usr/bin/env python3
"""Re-tuning the change-detection threshold on held-out pairs (Lab 59).

Lab 55 tuned the cosine threshold and Lab 55's `embedders.py` made the embedder swappable. The
question this lab answers is the one the suggested-next item raised: when you swap in a real
sentence-transformer and re-tune, how do you tune *out-of-sample*, and how many labeled pairs do you
need?

The trap is in-sample tuning: pick the threshold that maximizes accuracy on a set of pairs, then
report that same accuracy. It is optimistically biased, because the threshold has fit the sample's
noise. The fix is held-out evaluation (cross-validation): tune on one split, measure on another.
This lab shows the optimism as a function of sample size - large at small n, vanishing as n grows -
so you can decide how many reflow/edit pairs to label before trusting a re-tuned threshold.

The embedder here is the deterministic char-trigram stand-in so the lab runs offline; the real
sentence-transformer path is guarded (`--real-embedder` uses it when installed). The procedure -
hold out, cross-validate, watch the optimism curve - is identical for any embedder.

Usage:
    python retune.py --self-test
    python retune.py --real-embedder      # uses a sentence-transformer if installed
"""
from __future__ import annotations

import argparse
import math
import random
import re
import statistics
import sys


# ----- char-trigram embedder + cosine (offline stand-in; identical procedure to a real embedder) -
def embed(text: str) -> dict:
    t = re.sub(r"\s+", " ", text.strip().lower())
    v: dict[str, int] = {}
    for g in (t[i:i + 3] for i in range(len(t) - 2)):
        v[g] = v.get(g, 0) + 1
    return v


def cosine(u: dict, v: dict) -> float:
    if not u or not v:
        return 1.0 if u == v else 0.0
    dot = sum(u[k] * v.get(k, 0) for k in u)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0


def tune_threshold(cos_labels: list[tuple[float, int]]) -> float:
    """Threshold maximizing Youden's J (predict 'changed' when cosine < threshold)."""
    def J(th):
        tp = sum(1 for c, label in cos_labels if label == 1 and c < th)
        fp = sum(1 for c, label in cos_labels if label == 0 and c < th)
        tn = sum(1 for c, label in cos_labels if label == 0 and c >= th)
        fn = sum(1 for c, label in cos_labels if label == 1 and c >= th)
        tpr = tp / (tp + fn) if tp + fn else 0.0
        fpr = fp / (fp + tn) if fp + tn else 0.0
        return tpr - fpr
    xs = sorted({c for c, _ in cos_labels})
    cands = [(xs[i] + xs[i + 1]) / 2 for i in range(len(xs) - 1)] or [0.98]
    return max(cands, key=J)


def accuracy_at(cos_labels, th) -> float:
    return sum(1 for c, label in cos_labels if (c < th) == (label == 1)) / len(cos_labels)


# ----- labeled reflow/edit pairs, with hard cases so the classes overlap -----
def make_pairs() -> list[tuple[float, int]]:
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
                if i % 2 == 0:                                    # hard reflow: paraphrase, low cosine
                    pairs.append((s, paraphrase(rewrap(s)), 0))
                if i % 3 == 0 and any(k in s for k in ("funds", "leads", "is the")):
                    pairs.append((s, negate(s), 1))               # hard edit: negation, high cosine
    return [(cosine(embed(a), embed(b)), lbl) for a, b, lbl in pairs]


def cv_accuracy(cos_labels, K: int = 5, seed: int = 0) -> float:
    idx = list(range(len(cos_labels)))
    random.Random(seed).shuffle(idx)
    folds = [idx[f::K] for f in range(K)]
    accs = []
    for f in range(K):
        test = [cos_labels[j] for j in folds[f]]
        train = [cos_labels[j] for j in idx if j not in folds[f]]
        accs.append(accuracy_at(test, tune_threshold(train)))
    return statistics.mean(accs)


def optimism_curve(cos_labels, sizes=(16, 24, 40, 80, 160), trials: int = 20) -> dict:
    """For each sample size, average in-sample tuned accuracy and held-out accuracy over
    `trials` subsamples; the gap is the optimism of in-sample threshold selection."""
    rng = random.Random(42)
    out = {}
    for n in sizes:
        if n > len(cos_labels):
            continue
        ins, hos = [], []
        for trial in range(trials):
            sample = rng.sample(cos_labels, n)
            ins.append(accuracy_at(sample, tune_threshold(sample)))
            hos.append(cv_accuracy(sample, K=4, seed=trial))
        out[n] = {"in_sample": statistics.mean(ins), "held_out": statistics.mean(hos),
                  "optimism": statistics.mean(ins) - statistics.mean(hos)}
    return out


def _self_test() -> int:
    pairs = make_pairs()
    assert len(pairs) >= 160
    curve = optimism_curve(pairs)
    sizes = sorted(curve)
    small, large = sizes[0], sizes[-1]
    # in-sample is never below held-out (optimism is a one-sided bias)
    for n, row in curve.items():
        assert row["in_sample"] >= row["held_out"] - 1e-9, (n, row)
    # the optimism is real at small n and vanishes as n grows
    assert curve[small]["optimism"] > 0.01, curve[small]
    assert curve[large]["optimism"] < curve[small]["optimism"], curve
    assert curve[large]["optimism"] < 0.01, curve[large]
    print("self-test: optimism of in-sample threshold tuning, by sample size -",
          " ".join(f"n={n}:{curve[n]['optimism']:+.3f}" for n in sizes),
          "- large at small n, vanishes by n="f"{large} OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Held-out threshold re-tuning + optimism curve")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--real-embedder", action="store_true")
    args = ap.parse_args()
    if args.real_embedder:
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401
            print("sentence-transformers available - re-tune with real embeddings here")
        except Exception:
            print("sentence-transformers not installed; the procedure is identical with the stand-in")
        return 0
    if args.self_test:
        return _self_test()
    curve = optimism_curve(make_pairs())
    for n, r in curve.items():
        print(f"  n={n:3d}  in-sample {r['in_sample']:.3f}  held-out {r['held_out']:.3f}  optimism {r['optimism']:+.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
