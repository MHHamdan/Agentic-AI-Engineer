# Lab 32 · Reference solution

The complete implementation of [Lab 32: Self-RAG from scratch](../README.md).

## What this is

Self-RAG's reflection control flow on Lab 06's retrieval stack:

- **`decide_retrieve`** — the Retrieve token. Skips retrieval for parametric queries.
- **`grade_relevance` / `grade_support` / `grade_usefulness`** — ISREL / ISSUP / ISUSE, each a constrained categorical call via `chat_token`.
- **`generate_from_passage`** — one candidate answer per relevant passage.
- **`self_rag`** — the loop: decide → grade relevance → generate per relevant passage → score by `support_weight + usefulness/5` → select best.

## Implementation choices

1. **`chat_token` matches on word boundaries, not substrings.** `"relevant"` is a substring of `"irrelevant"`; naive `in` matching would grade every passage relevant. The helper uses `\bTOKEN\b` regex, which also handles the underscore tokens (`no_retrieve`). This is the single most important correctness detail in the lab.
2. **Conservative defaults.** When output is unparseable, `chat_token` returns the last (safest) option — `no_retrieve`, `no_support` — rather than the permissive one.
3. **Scoring is `support_weight + usefulness/5`.** `fully=1.0, partially=0.5, no_support=0.0` plus the 1–5 usefulness normalized to 0–1. Selects answers that are both grounded and on-target. The weighting is a tunable knob.
4. **Zero relevant passages → parametric fallback.** Forcing an answer from irrelevant passages invites fabrication; answering from parametric knowledge is safer and clearly labeled in the trace.

## What's deliberately out of scope

- **Fine-tuned reflection tokens.** The paper folds ISREL/ISSUP/ISUSE into one decoding pass via trained tokens. We approximate with separate calls — faithful to the logic, more expensive than the original.
- **Segment-level decoding.** We generate one candidate per passage rather than the paper's richer beam over reflection tokens.

## Running the solution

```bash
cd labs/32-self-rag-from-scratch/solution
jupyter notebook lab.ipynb
```

## Next

- [Lab 33: Graph RAG from scratch](../../33-graph-rag-from-scratch/).
- [SOTA RAG patterns quiz](../../../quizzes/agentic-rag/sota-rag-patterns.md) — question 4 covers reflection tokens.
