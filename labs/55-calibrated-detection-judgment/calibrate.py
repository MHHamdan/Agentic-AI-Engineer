#!/usr/bin/env python3
"""Calibrated change-detection and judgment (Lab 55).

Two stand-ins from earlier labs, both replaced by calibration on held-out data:

  Part A (Lab 50): the semantic fingerprint used a fixed cosine threshold of 0.98. Real
  embeddings put reflows and meaning-changes on overlapping cosine ranges, so a fixed cutoff
  either misses edits or cries wolf on reflows. Tune the threshold on labeled reflow/edit pairs
  by maximizing Youden's J (TPR - FPR) on the ROC curve.

  Part B (Lab 51): the judge's bias was corrected with a single additive shift, and the gate was
  all-dimensions-pass. A real judge bias is monotone but not a constant offset (it compresses the
  scale), which an additive shift cannot fix; isotonic regression (pool-adjacent-violators) fits a
  monotone map judge -> gold and recovers more agreement. And a release decision is rarely
  all-or-nothing across dimensions; a weighted gate lets the product owner say which dimensions
  matter more.

The embedder here is a deterministic char-trigram stand-in so the lab runs offline; in production
pass a sentence-transformer. The math is in math-foundations/15-calibration-threshold-selection.md.

Usage:
    python calibrate.py --self-test
"""
from __future__ import annotations

import argparse
import math
import re
import sys

LEVELS = (0, 1, 2, 3)


# ============================ Part A: embeddings + threshold tuning ============================
def _trigrams(t: str) -> list[str]:
    t = re.sub(r"\s+", " ", t.strip().lower())
    return [t[i:i + 3] for i in range(len(t) - 2)]


def embed(text: str) -> dict:
    """Deterministic char-trigram embedding (offline stand-in). Production: a sentence-transformer."""
    v: dict[str, int] = {}
    for g in _trigrams(text):
        v[g] = v.get(g, 0) + 1
    return v


def cosine(u: dict, v: dict) -> float:
    if not u or not v:
        return 1.0 if u == v else 0.0
    dot = sum(u[k] * v.get(k, 0) for k in u)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0


def tune_threshold(cos_labels: list[tuple[float, int]]) -> dict:
    """Pick the cosine cutoff that maximizes Youden's J. `cos_labels` is [(cosine, label)] with
    label 1 = meaning changed. Predict 'changed' when cosine < threshold. Returns the threshold,
    its J, and accuracy, plus the same metrics at the fixed 0.98 baseline."""
    def metrics(th):
        tp = sum(1 for c, label in cos_labels if label == 1 and c < th)
        fp = sum(1 for c, label in cos_labels if label == 0 and c < th)
        tn = sum(1 for c, label in cos_labels if label == 0 and c >= th)
        fn = sum(1 for c, label in cos_labels if label == 1 and c >= th)
        tpr = tp / (tp + fn) if tp + fn else 0.0
        fpr = fp / (fp + tn) if fp + tn else 0.0
        acc = (tp + tn) / len(cos_labels)
        return {"tpr": tpr, "fpr": fpr, "acc": acc, "J": tpr - fpr}
    xs = sorted({c for c, _ in cos_labels})
    cands = [(xs[i] + xs[i + 1]) / 2 for i in range(len(xs) - 1)] or [0.98]
    best = max(cands, key=lambda th: metrics(th)["J"])
    return {"threshold": best, "tuned": metrics(best), "fixed_0_98": metrics(0.98)}


def make_change_pairs() -> list[tuple[str, str, int]]:
    """Labeled (textA, textB, label) pairs grounded in the corpus. label 0 = same meaning
    (reflow / reformat), 1 = meaning changed (entity swap)."""
    bases = [
        "Dr. Aanya Rao leads the Helix Lab and works on retrieval systems",
        "The Beacon Foundation funds the Lattice Project and the Cascade Consortium",
        "Dr. Lena Fischer is the lead engineer on the Lattice Project at Helix Lab",
        "Atlas Systems funds the Sentinel Project internally as an industry lab",
        "The Meridian Institute funds the Prism Project from its own endowment",
        "Dr. Priya Nair is a staff researcher at Atlas Systems an industry lab",
    ]
    swaps = {"Aanya": "Tomas", "Beacon": "Northgate", "Lena": "Marco", "Atlas": "Orion",
             "Meridian": "Halcyon", "Priya": "Sofia"}
    def rewrap(s):
        w = s.split()
        return "\n".join(" ".join(w[i:i + 4]) for i in range(0, len(w), 4))
    def edit(s):
        for a, b in swaps.items():
            if a in s:
                return s.replace(a, b, 1)
        return s + " (revised)"
    pairs = []
    for s in bases:
        pairs.append((s, rewrap(s), 0))                              # reflow
        pairs.append((s, s.replace(" and ", ", ").replace(".", ""), 0))  # reformat
        pairs.append((s, edit(s), 1))                                # entity swap
        pairs.append((s, edit(rewrap(s)), 1))                        # swap + reflow
    return pairs


# ============================ Part B: isotonic calibration + weighted gate =====================
def qwk(y1, y2, levels=LEVELS) -> float:
    level_count = len(levels)
    idx = {v: i for i, v in enumerate(levels)}
    observed = [[0] * level_count for _ in range(level_count)]

    for a, b in zip(y1, y2, strict=False):
        observed[idx[a]][idx[b]] += 1

    n_items = len(y1)
    row_totals = [sum(observed[i]) for i in range(level_count)]
    col_totals = [
        sum(observed[i][j] for i in range(level_count))
        for j in range(level_count)
    ]
    weights = [
        [((i - j) ** 2) / ((level_count - 1) ** 2) for j in range(level_count)]
        for i in range(level_count)
    ]

    numerator = sum(
        weights[i][j] * observed[i][j]
        for i in range(level_count)
        for j in range(level_count)
    )
    denominator = sum(
        weights[i][j] * row_totals[i] * col_totals[j] / n_items
        for i in range(level_count)
        for j in range(level_count)
    )

    return 1 - numerator / denominator if denominator else 1.0

def additive_shift(judge: list[int], gold: list[int]) -> int:
    return round(
        sum(g - j for g, j in zip(gold, judge, strict=False)) / len(judge)
    )

def isotonic_fit(x: list[float], y: list[int]) -> tuple[list[float], list[float]]:
    """Monotone non-decreasing fit via pool-adjacent-violators."""
    pts = sorted(zip(x, y, strict=False))
    xs = []
    ys = []
    ws = []

    for xi, yi in pts:
        if xs and xs[-1] == xi:
            ys[-1] = (ys[-1] * ws[-1] + yi) / (ws[-1] + 1)
            ws[-1] += 1
        else:
            xs.append(xi)
            ys.append(float(yi))
            ws.append(1.0)

    i = 0
    while i < len(ys) - 1:
        if ys[i] > ys[i + 1]:
            ys[i] = (ys[i] * ws[i] + ys[i + 1] * ws[i + 1]) / (ws[i] + ws[i + 1])
            ws[i] += ws[i + 1]
            del ys[i + 1]
            del ws[i + 1]
            del xs[i + 1]
            if i > 0:
                i -= 1
        else:
            i += 1

    return xs, ys

def isotonic_predict(xs: list[float], ys: list[float], q: float) -> int:
    best = ys[0]

    for xi, yi in zip(xs, ys, strict=False):
        if xi <= q:
            best = yi

    return max(0, min(3, round(best)))

def weighted_gate(scores_by_dim: dict, weights: dict, i: int, threshold: float) -> bool:
    """Pass release i if the weighted, max-normalized mean of its dimension scores clears the
    threshold. Lets the product owner trade dimensions off instead of requiring all to pass."""
    num = sum(weights[d] * scores_by_dim[d][i] for d in weights)
    return num / (3.0 * sum(weights.values())) >= threshold


def _self_test() -> int:
    # ---- Part A ----
    pairs = make_change_pairs()
    cos_labels = [(cosine(embed(a), embed(b)), lbl) for a, b, lbl in pairs]
    res = tune_threshold(cos_labels)
    assert res["tuned"]["acc"] > res["fixed_0_98"]["acc"], res
    assert res["fixed_0_98"]["fpr"] > res["tuned"]["fpr"], res   # fixed 0.98 cries wolf on reflows

    # ---- Part B: isotonic beats an additive shift on a non-additive monotone bias ----
    N = 24
    gold = [(i * 7) % 4 for i in range(N)]
    compress = {0: 0, 1: 0, 2: 1, 3: 2}            # judge compresses the low end (not a constant shift)
    judge = [compress[g] for g in gold]
    calib = list(range(12))
    test = list(range(12, 24))
    shift = additive_shift([judge[i] for i in calib], [gold[i] for i in calib])
    add_cal = [max(0, min(3, judge[i] + shift)) for i in range(N)]
    xs, ys = isotonic_fit([judge[i] for i in calib], [gold[i] for i in calib])
    iso_cal = [isotonic_predict(xs, ys, judge[i]) for i in range(N)]
    raw_q = qwk([judge[i] for i in test], [gold[i] for i in test])
    add_q = qwk([add_cal[i] for i in test], [gold[i] for i in test])
    iso_q = qwk([iso_cal[i] for i in test], [gold[i] for i in test])
    assert iso_q >= add_q > raw_q, (raw_q, add_q, iso_q)

    # ---- Part B: weighted gate is a different (product) decision than all-dimensions-pass ----
    F = [3, 3, 2, 1]
    R = [3, 2, 3, 1]
    C = [1, 2, 1, 3]
    sbd = {"f": F, "r": R, "c": C}
    W = {"f": 0.5, "r": 0.3, "c": 0.2}
    def all_dims(i):
        return F[i] >= 2 and R[i] >= 2 and C[i] >= 2
    def wgate(i):
        return weighted_gate(sbd, W, i, threshold=0.66)
    assert any(all_dims(i) != wgate(i) for i in range(4))

    print(f"self-test: Part A tuned threshold {res['threshold']:.3f} acc {res['tuned']['acc']:.2f} "
          f"vs fixed 0.98 acc {res['fixed_0_98']['acc']:.2f} (FPR {res['fixed_0_98']['fpr']:.2f}->"
          f"{res['tuned']['fpr']:.2f}); Part B completeness QWK raw {raw_q:.2f} -> additive {add_q:.2f} "
          f"-> isotonic {iso_q:.2f}; weighted gate differs from all-dims OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Calibrated change-detection and judgment")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("import this module, or run --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
