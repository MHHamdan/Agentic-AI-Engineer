#!/usr/bin/env python3
"""Derive eval-gate thresholds from a baseline run (Lab 38, item 3).

Thresholds set by intuition drift or get gamed. Instead, measure a baseline and
set each threshold a defensible distance below it:

  - deterministic metric (routing accuracy): threshold = baseline - tolerance_band
  - noisy metric (judged faithfulness over N runs): threshold = mean - k * std

Writes gate_thresholds.json, which eval_gate.py reads via --thresholds.

Usage:
    python derive_thresholds.py                 # uses a recorded baseline (no network)
    python derive_thresholds.py --measure       # re-measure routing accuracy live
    python derive_thresholds.py --self-test     # derivation math only
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "gate_thresholds.json"


def derive_deterministic(baseline: float, tolerance: float = 0.06) -> float:
    """Allow normal wobble; fail only a clear regression below the band."""
    return round(baseline - tolerance, 3)


def derive_noisy(samples: list[float], k: float = 2.0) -> tuple[float, float, float]:
    """For a metric with run-to-run variance, threshold = mean - k*std. With k=2 a
    single run roughly within 2 sigma of the baseline mean does not trip the gate."""
    mean = statistics.mean(samples)
    std = statistics.stdev(samples) if len(samples) > 1 else 0.0
    return round(mean - k * std, 3), round(mean, 3), round(std, 3)


def measure_routing_baseline() -> float:
    """Live routing accuracy via the gate's own function (needs sklearn + embedder)."""
    sys.path.insert(0, str(HERE.parent / "37-rag-eval-gates"))
    from eval_gate import routing_accuracy  # type: ignore
    return routing_accuracy()["routing_accuracy"]


def build_config(routing_baseline: float, faith_samples: list[float],
                 tolerance: float = 0.06, k: float = 2.0) -> dict:
    rt = derive_deterministic(routing_baseline, tolerance)
    ft, fm, fs = derive_noisy(faith_samples, k)
    return {
        "routing_accuracy": rt,
        "judged_faithfulness": ft,
        "_meta": {
            "routing": {"baseline": round(routing_baseline, 3), "tolerance": tolerance,
                        "rule": "baseline - tolerance"},
            "faithfulness": {"mean": fm, "std": fs, "k": k, "rule": "mean - k*std",
                             "n_samples": len(faith_samples)},
            "note": "routing_accuracy is enforced by the blocking gate; judged_faithfulness "
                    "is enforced by the nightly job, not the PR gate.",
        },
    }


def _self_test() -> int:
    assert derive_deterministic(0.9375, 0.06) == 0.877
    ft, fm, fs = derive_noisy([0.81, 0.78, 0.83, 0.79, 0.80], 2.0)
    assert fm == 0.802 and 0 < ft < fm, (ft, fm, fs)
    cfg = build_config(0.9375, [0.81, 0.78, 0.83, 0.79, 0.80])
    assert cfg["routing_accuracy"] < 0.9375 and cfg["judged_faithfulness"] < 0.802
    assert all(not k.startswith("_") or k == "_meta" for k in cfg)
    print("self-test: threshold derivation OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Derive eval-gate thresholds from a baseline")
    ap.add_argument("--measure", action="store_true", help="re-measure routing accuracy live")
    ap.add_argument("--tolerance", type=float, default=0.06)
    ap.add_argument("--k", type=float, default=2.0)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()

    # A recorded baseline keeps this runnable offline; --measure refreshes routing live.
    routing_baseline = measure_routing_baseline() if args.measure else 0.9375
    # Judged-faithfulness samples come from prior nightly runs (see the nightly workflow).
    faith_samples = [0.81, 0.78, 0.83, 0.79, 0.80]

    cfg = build_config(routing_baseline, faith_samples, args.tolerance, args.k)
    OUT.write_text(json.dumps(cfg, indent=2) + "\n")
    print(f"wrote {OUT.name}:")
    print(json.dumps(cfg, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
