#!/usr/bin/env python3
"""Context-budget assembly (Lab 04).

The context window is a finite budget shared by instructions, memory, history, tool schemas, and tool
output. When everything competes, you cannot just append - you have to choose. This builds a context
assembler that packs the window under a token budget using three of the standard moves: SELECT the
highest-priority items, COMPRESS the overflow into a short note, and keep durable knowledge in
WRITE-able memory rather than the prompt. The point it makes concrete: a bigger window is not a
substitute for selection, because models attend unevenly and degrade as context grows ("context rot").

Priority here is simple and explicit - memory by relevance, history by recency, instructions always
mandatory - so you can see what survives and what gets dropped. Token cost is approximated by word
count to keep the lab offline and deterministic; a real system counts tokens and the logic is the same.

References: Anthropic, Effective context engineering for AI agents (Sept 2025); Hong, Troynikov, Huber
(2025), Context Rot, Chroma technical report; Liu et al. (2023), Lost in the Middle, arXiv:2307.03172.

Usage:
    python context_budget.py --self-test
    python context_budget.py --demo
"""
from __future__ import annotations

import argparse
import sys


def _cost(text: str) -> int:
    """Approximate token cost by word count - offline and deterministic. Real systems count tokens."""
    return len(text.split())


def assemble(instructions: str, memory_items: list[dict], history: list[dict], budget: int) -> dict:
    """Pack the window to `budget`. Instructions are mandatory; the rest competes by priority
    (memory by relevance, history by recency). Overflow is compacted into a single note."""
    context = [{"kind": "instructions", "text": instructions}]
    used = _cost(instructions)

    pool = ([{"kind": "memory", "text": m["text"], "priority": m["relevance"]} for m in memory_items]
            + [{"kind": "history", "text": h["text"], "priority": h["recency"]} for h in history])
    # deterministic order: priority desc, then text as a tiebreak
    pool.sort(key=lambda x: (-x["priority"], x["text"]))

    dropped = []
    for item in pool:
        if used + _cost(item["text"]) <= budget:
            context.append({"kind": item["kind"], "text": item["text"]})
            used += _cost(item["text"])
        else:
            dropped.append(item)

    if dropped:  # compress: one short note stands in for what did not fit
        note = f"[compacted {len(dropped)} lower-priority item(s)]"
        if used + _cost(note) <= budget:
            context.append({"kind": "summary", "text": note})
            used += _cost(note)

    return {"context": context, "used": used, "dropped": dropped}


INSTRUCTIONS = "System: plan the trip and respect the user budget."
MEMORY = [
    {"text": "user prefers window seats and morning flights always", "relevance": 0.9},
    {"text": "user is vegetarian and avoids red eye flights", "relevance": 0.8},
    {"text": "user once mentioned liking jazz music in passing", "relevance": 0.2},
]
HISTORY = [
    {"text": "turn twelve user asked to add a museum on day three", "recency": 0.95},
    {"text": "turn two greeting and small talk about the weather", "recency": 0.1},
]


def _kinds(result) -> list[str]:
    return [c["kind"] for c in result["context"]]

def _texts(result) -> list[str]:
    return [c["text"] for c in result["context"]]


def _self_test() -> int:
    tight = assemble(INSTRUCTIONS, MEMORY, HISTORY, budget=40)
    assert assemble(INSTRUCTIONS, MEMORY, HISTORY, budget=40) == tight  # deterministic

    # never exceeds the budget
    assert tight["used"] <= 40

    # instructions are always present, regardless of pressure
    assert tight["context"][0]["kind"] == "instructions"

    # selection keeps the highest-priority items and drops the lowest
    assert MEMORY[0]["text"] in _texts(tight)            # top-relevance memory kept
    dropped_texts = [d["text"] for d in tight["dropped"]]
    assert MEMORY[2]["text"] in dropped_texts            # the low-relevance "jazz" memory dropped
    assert HISTORY[1]["text"] in dropped_texts           # the stale greeting dropped

    # compression leaves a marker that something was dropped
    assert "summary" in _kinds(tight)

    # a generous budget drops nothing
    loose = assemble(INSTRUCTIONS, MEMORY, HISTORY, budget=1000)
    assert loose["dropped"] == [] and "summary" not in _kinds(loose)

    print(f"self-test: deterministic; budget respected ({tight['used']}/40); instructions always kept; "
          f"top-relevance memory retained, {len(tight['dropped'])} stale/low items dropped + compacted; "
          f"loose budget drops nothing OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Context-budget assembly")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--budget", type=int, default=40)
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    res = assemble(INSTRUCTIONS, MEMORY, HISTORY, budget=args.budget)
    print(f"assembled context (budget {args.budget} words, used {res['used']}):")
    for c in res["context"]:
        print(f"  [{c['kind']:>12}] {c['text']}")
    if res["dropped"]:
        print("dropped:", [d["text"][:30] + "..." for d in res["dropped"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
