# Lab 58 · Reference solution

The complete implementation of [Lab 58: Measuring lost-in-the-middle](../README.md).

## What this is

- **`position_sweep(k)`** — accuracy at each gold position 1..k over a fixed query set.
- **`recall_prob`** — a U-shaped stand-in using absolute distance from the nearest edge, so the dead middle widens with k.
- **`mean_accuracy_random_placement`**, **`rerank_to_top_accuracy`** — the bias the mean hides, and the rerank mitigation.

## Expected results

- k=20: edges ~0.95 vs middle ~0.50 (U-shaped); mean over random placement ~0.64.
- Rerank-to-top ~0.95; middle accuracy 0.50 → 0.77 as k shrinks 40 → 6.

## Implementation choices

1. **Report by position**, not on average.
2. **Absolute edge window** so shrinking k raises accuracy (the real mechanism).
3. **Pluggable answerer** — swap the stand-in for real model calls to measure your stack.

## What's out of scope

- Real model calls (deterministic stand-in here).
- A reranker implementation (the harness measures the effect of placing gold at the top).

## Running

```bash
cd labs/58-measuring-lost-in-the-middle
python lostmiddle.py --self-test
python lostmiddle.py --k 20      # print the position curve
```
