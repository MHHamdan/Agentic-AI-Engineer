# Lab 08 · Reference solution

The polished final implementation of [Lab 08: Contextual retrieval and query rewriting](../README.md).

## What this is

Lab 07's hybrid+rerank pipeline composed with two upstream layers:

1. **Contextual indexes** — Anthropic's verbatim `CONTEXT_PROMPT` generates a 1-2 sentence situating summary per chunk; the summary is prepended to the chunk before indexing. Cached on disk as `../context_cache.json`.
2. **Query rewriting** — three modes wired through the same composer: `hyde`, `multi`, `decompose`. Each generates one or more text strings that get fed through hybrid retrieval; results RRF-fused with the original.

The cross-encoder rerank uses the **original** query, not the rewrites — rewrites are for retrieval, the rerank should score against what the user actually asked. Results return the **original** chunk text — the augmentation was for retrieval only; the agent reads the chunk.

## How it differs from `../lab.ipynb`

| Lab notebook (46 cells) | Solution (26 cells) |
|---|---|
| Steps 4-6 introduce HyDE, multi-query, decompose separately with demos for each | Three modes composed in `search_corpus_v3` with a single `rewrite_mode` parameter |
| Step 9 stretch failure-mode walkthrough | Out of scope here |
| Step 7 "full pipeline" rebuilds the agent loop inline | Reuses Labs 06/07's loop with `search_corpus_v3` as the search tool |
| Walks index-size impact of augmentation | Mentioned briefly; lab is where the diagnostic walk lives |

## Implementation choices

1. **The cache lives at `../context_cache.json`**, one level up from the solution directory. The lab notebook writes to `./context_cache.json` relative to itself. The path adjustment is the only difference — both produce identical cache contents because the chunk IDs are stable (chunker config pinned). If you ran the lab first, this solution reuses the cache without re-calling.
2. **Anthropic's `CONTEXT_PROMPT` is reproduced verbatim.** Don't paraphrase. The exact wording was empirically validated by Anthropic for this use case; alternatives (longer, more elaborate, etc.) consistently underperform.
3. **`hyde_rewrite` returns a list**, not a string. Same return-type as `multi_query_rewrite` and `decompose_query`. Uniform API; the composer treats them identically.
4. **Reranking uses the original query.** Critical for HyDE — the hypothetical answer was useful for *retrieval* (it shares vocabulary with the corpus chunks) but is the *wrong* query for *scoring relevance* (it's a possible answer, not the question). The lab walks this distinction; the solution encodes it.
5. **Results return original chunk text, not augmented.** The augmentation was indexing-only. The agent reads the chunk as the human wrote it — the context summary was just a search-time helper.
6. **`rewrite_mode` is a `search_corpus_v3` parameter, not a tool-schema parameter the agent sees.** Production systems would either fix it (always multi-query, say), pick adaptively from query shape, or expose it as an internal A/B variable. Exposing it to the agent gives the LLM one more decision to get wrong without commensurate benefit.

## What's deliberately out of scope

- **Prompt caching of the document portion.** Anthropic's announcement claims ~90% cost reduction with prompt caching enabled on `CONTEXT_PROMPT`. Worth doing in production; the API call shape changes slightly. See [`concepts/rag/contextual-retrieval.md`](../../../concepts/rag/contextual-retrieval.md#the-cost-question) for the cost-question section.
- **Adaptive `rewrite_mode` selection.** A small classifier or heuristic picks the mode per query. Worth the engineering for production; demo simplicity here.
- **Batched contextualizer calls.** The current implementation iterates sequentially. Parallelizing reduces wall-clock time for large corpora.
- **Caching rewrite outputs.** Production caches `(query_hash, rewrite_mode)` → rewrite. Demo simplicity here.
- **Evaluation across modes.** "Does multi-query beat HyDE on referential queries?" That's Lab 09.

## Running the solution

```bash
cd labs/08-contextual-retrieval-and-query-rewriting/solution
jupyter notebook lab.ipynb
```

First run generates 55 context summaries (~$0.05 worth of LLM calls at gpt-4o-mini rates). Cache is written to `../context_cache.json`; subsequent runs are 0 calls.

You'll need both `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (for the contextualizer + query rewriting + agent loop) and the two models from Lab 07 cached locally (`all-MiniLM-L6-v2`, `ms-marco-MiniLM-L-6-v2`).

## Next

- Take the [contextual retrieval quiz](../../../quizzes/agentic-rag/contextual-retrieval-and-query-rewriting.md) if you haven't already.
- Continue to [Lab 09: Evaluating agentic RAG](../../09-evaluating-agentic-rag/) — measuring whether each of these layers actually helped.
