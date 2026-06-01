# Lab 31 · Reference solution

The complete implementation of [Lab 31: Corrective RAG (CRAG) from scratch](../README.md).

## What this is

CRAG layered on Lab 06's retrieval stack:

- **`grade_retrieval`** — the retrieval evaluator. One LLM call returns per-passage scores and an overall verdict in `{correct, ambiguous, incorrect}`.
- **`decompose_recompose`** — knowledge refinement. Keeps chunks scoring `>= keep_threshold`, splits them to sentences, recomposes with `[chunk_id]` provenance.
- **`rewrite_query` / `web_search_fallback`** — corrective actions. Rewrite-and-retry for ambiguous; fallback (stubbed) for incorrect.
- **`corrective_rag`** — the loop: retrieve → grade → route → generate, with a decision trace.

## Implementation choices

1. **The corpus path is `../06-agentic-rag-from-scratch/corpus`.** This lab reuses Lab 06's corpus rather than duplicating it; the chunker config (`TARGET_TOKENS=160`) matches so chunk IDs line up with Labs 07–09.
2. **The grader returns scores *and* a verdict.** One call does double duty: the verdict routes, the scores drive `decompose_recompose`'s keep-threshold.
3. **Three-way routing.** `correct` → refine and generate; `incorrect` → fallback; `ambiguous` → rewrite, re-retrieve, combine with fallback. The ambiguous path is where partial-relevance is salvaged.
4. **The web fallback is a stub** returning a sentinel string, so the notebook runs offline. Replace `web_search_fallback` with a real search tool for production; nothing else changes.
5. **Provenance survives refinement** because `decompose_recompose` keeps `[chunk_id]` prefixes — citations remain checkable after stripping.

## What's deliberately out of scope

- **A fine-tuned evaluator.** The paper trains a lightweight model; we use an LLM call. Logic identical, cost profile different.
- **Strip-level decomposition.** We refine at sentence granularity.
- **A real search API.** Stubbed; see choice 4.

## Running the solution

```bash
cd labs/31-corrective-rag-from-scratch/solution
jupyter notebook lab.ipynb
```

First run downloads `all-MiniLM-L6-v2` (~80 MB) to your HuggingFace cache.

## Next

- [Lab 32: Self-RAG from scratch](../../32-self-rag-from-scratch/) — the on-demand-retrieval sibling.
- [SOTA RAG patterns quiz](../../../quizzes/agentic-rag/sota-rag-patterns.md).
