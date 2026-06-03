# Lab 58: Measuring lost-in-the-middle

> 🟡 Intermediate · ⏱ ~60–75 min · 📚 Retrieval science · Module 26

## 🎯 Goal

Long-context models attend best to the start and end of the context and worst to the middle (Liu et al., 2023), so a RAG system can retrieve the right passage and still answer wrong if it places that passage in the middle. This lab builds the methodology for measuring that position bias: sweep the gold passage across positions, recover the U-shaped accuracy curve, and quantify mitigations.

By the end you should be able to:

- Run a position sweep and read accuracy by gold position instead of on average.
- Explain why mean accuracy hides the bias, and why the dead middle widens with k.
- Quantify rerank-to-top and shrink-k mitigations.

## 📋 Prerequisites

- 📖 [Lost in the middle](../../concepts/rag/lost-in-the-middle.md) — the phenomenon and the fixes.
- **Assumed background:** RAG retrieval/recall, and the idea that the generator reads an assembled prompt.

**Setup:** Python 3.11+; standard library only. The answerer is a deterministic stand-in for a model's position bias; swap in real model calls to measure your own stack.

## 🛠 Module

| Component | Notes |
|---|---|
| `lostmiddle.py` | `position_sweep`, `recall_prob`, `mean_accuracy_random_placement`, `rerank_to_top_accuracy` (`--self-test`) |

## What the numbers say

| | Result (k=20 stand-in) |
|---|---|
| Edge vs middle accuracy | ~0.95 vs ~0.50 (U-shaped) |
| Mean over random placement | ~0.64 (hides the bias) |
| Rerank gold to top | ~0.95 |
| Middle accuracy, k=40 → k=6 | 0.50 → 0.77 |

## Design choices and tradeoffs

- **Measure by position, not on average.** A single mean accuracy number can look healthy while the middle is failing. The sweep is the only way to see it, and it turns "use a reranker" from folklore into a measured decision.
- **Absolute edge window, not relative.** The dead middle is an absolute-distance effect — models attend to roughly the first/last few passages — so the middle *widens* with k. That's why shrinking the context, not just improving recall, raises accuracy.
- **A stand-in answerer, a real harness.** The lab's correctness model is a deterministic U-shaped stand-in; the deliverable is the sweep methodology, which you point at real model calls over your corpus.

## Common gotchas

- **Recall ≠ answer accuracy.** Retrieval metrics stop at "the passage was in the top-k"; they don't capture where it landed in the prompt.
- **More context can hurt.** Adding chunks improves recall but can lower answer accuracy by deepening the middle — measure before raising k.
- **The curve is model-specific.** Depth, window size, and end-vs-start symmetry vary by model and prompt; measure yours rather than copying these numbers.

## 🧮 Going deeper

- 📖 [Lost in the middle](../../concepts/rag/lost-in-the-middle.md) and [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md).
- Liu et al. (2023), *Lost in the Middle: How Language Models Use Long Contexts* (TACL).

## What comes next

Point `position_sweep` at real model calls over your own gold set, and add a reranking stage so the harness measures accuracy before and after reranking.
