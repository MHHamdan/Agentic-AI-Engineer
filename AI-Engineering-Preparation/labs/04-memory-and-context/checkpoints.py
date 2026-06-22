#!/usr/bin/env python3
"""State vs. memory, with checkpoint and rollback (Lab 04).

A long-running agent needs two different kinds of "remembering," and conflating them is a common bug.
State is the current task - the plan, what is done, what is next - and it must be cheap to rewind when
the user changes their mind mid-task. Memory is what carries across tasks - durable preferences and
facts - and it must survive a rewind. This builds both, plus the checkpoint/rollback that makes a
mid-task correction cheap: snapshot the state before each step, and when a correction lands, roll back
only to the affected step instead of restarting.

The scenario is a trip planner. It plans days against a per-day budget held in memory. Partway through,
the user raises the budget; the agent rolls back to before the affected day, keeping the earlier days,
and re-plans only the rest - while the new budget (memory) persists across the rollback. Deterministic,
standard-library only.

References: Packer et al. (2023), MemGPT, arXiv:2310.08560; LangGraph persistence (checkpointers),
official docs.

Usage:
    python checkpoints.py --self-test
    python checkpoints.py --demo
"""
from __future__ import annotations

import argparse
import copy
import sys


class Planner:
    """State is rewindable (the itinerary in progress); memory is durable (the budget preference).
    Checkpoints snapshot state, never memory."""

    def __init__(self) -> None:
        self.memory = {"budget_per_day": 200}             # carries across tasks and across rollbacks
        self.state = {"step": 0, "itinerary": []}          # the current task; rewindable
        self._checkpoints: dict[str, dict] = {}
        self.compute_calls = 0                             # to show only affected steps re-run

    def plan_day(self, day: int) -> None:
        self.compute_calls += 1
        spend = self.memory["budget_per_day"]
        self.state["itinerary"].append({"day": day, "plan_spend": spend})
        self.state["step"] = day

    def checkpoint(self, label: str) -> None:
        self._checkpoints[label] = copy.deepcopy(self.state)

    def rollback(self, label: str) -> None:
        self.state = copy.deepcopy(self._checkpoints[label])

    def spends(self) -> list[int]:
        return [d["plan_spend"] for d in self.state["itinerary"]]


def run_scenario(correction_budget: int | None = None):
    """Plan five days; optionally apply a mid-task budget correction after day 2."""
    p = Planner()
    for day in range(1, 6):
        p.checkpoint(f"before_day_{day}")
        p.plan_day(day)
    calls_after_initial = p.compute_calls
    if correction_budget is not None:
        p.memory["budget_per_day"] = correction_budget   # durable change
        p.rollback("before_day_3")                        # keep days 1-2, rewind the rest
        for day in range(3, 6):
            p.plan_day(day)
    return p, calls_after_initial


def _self_test() -> int:
    p0, _ = run_scenario()
    p1, _ = run_scenario()
    assert p0.spends() == p1.spends()  # deterministic

    # baseline: five days at the original budget
    base, calls_initial = run_scenario()
    assert base.spends() == [200, 200, 200, 200, 200]

    # mid-task correction: raise the budget after day 2
    p, calls_initial = run_scenario(correction_budget=350)

    # rollback kept days 1-2 unchanged; days 3-5 re-planned at the new budget
    assert p.spends() == [200, 200, 350, 350, 350], p.spends()

    # only the affected steps were recomputed (days 3, 4, 5), not the whole task
    recomputed = p.compute_calls - calls_initial
    assert recomputed == 3, recomputed

    # memory (the new budget) survived the rollback; state was rewound, memory was not
    assert p.memory["budget_per_day"] == 350

    print(f"self-test: deterministic; rollback kept days 1-2 and re-planned 3-5 at the new budget; "
          f"only {recomputed} steps recomputed; memory persisted across rollback OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="State vs. memory with checkpoint/rollback")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    base, _ = run_scenario()
    print("initial plan (budget 200/day):", base.spends())
    if args.demo:
        p, calls = run_scenario(correction_budget=350)
        print("user raises budget to 350 after day 2, agent rolls back to before day 3")
        print("corrected plan:                ", p.spends())
        print(f"steps recomputed: {p.compute_calls - calls} (only days 3-5); "
              f"memory budget now {p.memory['budget_per_day']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
