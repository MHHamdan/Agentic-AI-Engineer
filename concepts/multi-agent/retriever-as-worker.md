# The retriever-as-worker pattern

> ⏱ ~10 min · 🟡 Intermediate · Prerequisites: [multi-agent RAG](./multi-agent-rag.md), [supervisor-worker pattern](./supervisor-worker-pattern.md), Path 02 Labs 06-08

The specific pattern Lab 13 implements: Path 02's retrieval pipeline becomes a single worker the supervisor can invoke. The supervisor decides when retrieval is needed; the synthesizer composes from retrieved chunks with citation preservation. Concrete and prescriptive.

## The shape

```
        user query
            │
            ▼
    ┌───────────────┐
    │  supervisor   │ ← Lab 10's supervisor with two new tools
    │               │   (retrieve, synthesize)
    └───────────────┘
        │   ▲   │   ▲
        │   │   │   │
        ▼   │   ▼   │
    retriever  synthesizer
   (Lab 06-08    (writer
    pipeline)     with chunk
                  citations)
```

Three properties to internalize:

1. **The retriever wraps Path 02's pipeline unchanged.** Lab 06 chunking + Lab 07 four-stage retrieval (dense + BM25 + RRF + cross-encoder rerank) + Lab 08 contextual augmentation (when its cache is available, falling back to Lab 07's v2 pipeline when it isn't). The wrapper exposes one function and one structured envelope.

2. **The supervisor sees chunks, not retrieval internals.** The retriever's envelope returns `{status, chunks: [{id, text, source, score}, ...]}` — not BM25 scores, dense cosines, or rerank logits. The supervisor doesn't reason about retrieval quality; it reasons about which chunks to pass to the synthesizer.

3. **The synthesizer is told to cite by chunk id.** Citation rendering is `[<chunk_id>]` inline, with the citation list at the end mapping `[chunk_id] source — title`. The supervisor passes chunks through *verbatim* — no re-numbering, no summarizing, no filtering. This is the structural mitigation for citation drift.

## The retriever-worker contract

The retriever's API surface:

```python
def retriever_agent(query: str, top_k: int = 5) -> dict:
    """Run the retrieval pipeline.

    Returns:
      {
        "status": "ok" | "empty" | "off_corpus" | "error",
        "chunks": [
          {
            "id": str,        # stable chunk identifier
            "text": str,      # the chunk text
            "source": str,    # source document path/url
            "title": str,     # source title
            "score": float    # final rerank score (not for the supervisor to act on)
          },
          ...
        ],
        "query": str,         # the query as run (may differ from input if rewritten)
        "pipeline": str,      # which pipeline ran: "v2" or "v3-contextual"
      }
    """
```

Four `status` values:
- `ok` — retrieved chunks meet the relevance threshold
- `empty` — no chunks survived the floor; corpus doesn't have what was asked
- `off_corpus` — query was determined to be outside the corpus's scope (rare; usually surfaces via empty)
- `error` — pipeline failure (model load, embedding failure, etc.)

The `score` field is informational only. The supervisor must not reason about it ("this score is low, maybe retrieve again"). If the retriever returned ok, the chunks are good enough to use; if not, the retriever returned empty. The supervisor's job is to use the envelope, not second-guess it.

## The four retrieval-decision rules

These live in the supervisor's system prompt. Each prevents a specific failure mode.

### Rule 1: Retrieve when the query is grounded in the corpus

The supervisor's system prompt includes a 2-3 sentence description of the corpus ("This corpus covers Path 01 concepts: the agent loop, tool design, ReAct, search vs. retrieval, embeddings, vector indexes, chunking, citation tracking. Documents are markdown explanations, ~200-500 words each."). The supervisor reads the user query against this scope and decides whether retrieval is appropriate.

The rule prevents **retrieval skip** — the supervisor falling back on training-data answers for questions the corpus actually covers.

### Rule 2: Don't retrieve for definitional or stable-knowledge questions

Questions like "what is HTTP?" or "what year did France adopt the Napoleonic Code?" don't need corpus retrieval. The model handles them from training data. Even if the corpus *also* covers them, the retrieval cost is overhead.

The rule prevents **retrieval over-call** — retrieving for queries that don't benefit from it.

A useful test: if the user could find the answer in a general encyclopedia article, the corpus retrieval probably doesn't add value. If the user needs the specific framing your corpus provides, retrieve.

### Rule 3: One retrieval per distinct factual question

If a retrieval returned `empty`, the next move is to surface "couldn't find this in the corpus" — not to retry with a slightly reworded query hoping for better luck. The retrieval pipeline already does query rewriting internally (Lab 08); re-retrieving from the supervisor level is doing the same work twice with worse signal.

The rule prevents **retrieval thrash** — repeated near-duplicate retrievals on the same factual question. The action-hash dedup mechanism from Labs 03/10/11/12 enforces this at the supervisor's tool-dispatch level: identical retrieve args return a `repeated_action` envelope.

Compound questions are different. "Compare X and Y" is two distinct factual questions and should produce two retrievals (or one planner-driven multi-retrieval — see Lab 12's pattern).

### Rule 4: Pass retrieved chunks directly to the synthesizer without paraphrase

When the supervisor calls the synthesizer, it passes the chunks envelope through verbatim. No summarization. No filtering. No re-numbering. The synthesizer reads the chunks and composes the answer with citations.

The rule prevents **citation drift** — the supervisor's role is routing, not summarization. Summarization is the synthesizer's job, and the synthesizer is the only place that should see chunks rendered into prose.

If the chunks need filtering for relevance, that's the **critic's** job (Pattern 3 from the framing page; Lab 13's stretch section). Not the supervisor's.

## Citation preservation discipline

This is the canonical multi-agent-RAG bug, so it gets its own treatment.

The chain of custody for citations:

1. **Retrieval pipeline** assigns each chunk a stable `id` (from Lab 06's chunker) and tracks the source document.
2. **Retriever-worker** returns the chunks envelope with `id` and `source` for each chunk.
3. **Supervisor** passes the envelope to the synthesizer *without modification*. Specifically, the supervisor must not:
   - Re-number chunks (the `id` is the identifier, not a 1, 2, 3 index)
   - Filter chunks before passing them on
   - Summarize chunks into a "findings" string
   - Drop the `source` field
4. **Synthesizer** is told in its system prompt to cite inline by `[chunk_id]` and render the citation list at the end.
5. **The synthesizer's output** is the final answer with citations rendered.

The supervisor as a routing layer that doesn't touch payloads is the discipline. Every step where the supervisor "helpfully" reformats chunks is a place citations can drop.

This is the same handoff-hygiene discipline from Lab 10's `concepts/multi-agent/handoffs-and-shared-state.md`, applied specifically to retrieval chunks: **handoffs carry structured payloads, not paraphrased prose.**

## Choosing the retrieval pipeline

Lab 13 supports two pipelines:

- **v2** (Lab 07): dense + BM25 + RRF + cross-encoder rerank. Always available.
- **v3** (Lab 08): v2 + contextual augmentation (using cached chunk descriptions) + query rewriting (HyDE / multi-query / decompose).

The retriever-worker auto-detects: if a `context_cache.json` exists from a previous Lab 08 run, use v3; otherwise fall back to v2. The wrapper returns which pipeline ran in the `pipeline` field of its envelope.

In production you'd commit to one pipeline. The auto-detect is a pedagogical convenience: learners who haven't completed Lab 08 still get a working multi-agent RAG system; learners who have completed Lab 08 see the contextual augmentation in action.

## Composing with Lab 11's critic (optional)

Lab 13's stretch section adds Lab 11's critic worker — but applied to the synthesis, not the chunks. The critic reviews `(chunks, draft)` for groundedness: every claim in the draft must trace to a chunk.

```
retriever → chunks
            │
            ▼
        synthesizer → draft
            │
            ▼
          critic → ok or needs_revision
            │
            ▼
      synthesizer (revised, if needed)
```

Bounded refinement carries over from Lab 11 (`MAX_REFINEMENT_CYCLES = 3`). The critic-on-synthesis pattern is the standard placement; the critic-on-chunks variant (Pattern 3a from the framing page) is a different problem we don't tackle here.

When to add it: high-stakes synthesis where ungrounded claims have real cost. Cost: roughly 2x the synthesis cost. Worth it when wrong is worse than slow.

## Composing with Lab 12's planner (optional stretch)

For compound questions ("compare X, Y, Z"), Lab 13's second stretch section composes with Lab 12. The planner emits a plan with multiple `retrieve(query=...)` steps in the same `parallel_group`; the executor pool runs them concurrently; the synthesizer merges across all chunks.

The integration is straightforward: the retriever-worker is one of the tools in the planner's tool registry. The synthesizer becomes the final step in the plan. Everything from Lab 12 applies — `MAX_PLAN_STEPS = 8`, `MAX_PARALLEL_EXECUTORS = 3`, `MAX_REPLANS = 2`, bounded replanning on failure.

When to add it: clearly decomposable multi-aspect questions. Useless for single-fact questions where there's nothing to parallelize.

## When this pattern stops working

Three signals to look elsewhere:

- **The supervisor's retrieve/skip decisions are consistently wrong.** Either the corpus description in the system prompt is too vague, or the queries don't have a clean grounded/ungrounded distinction. Eval-time spot-check the supervisor's routing on a labeled set; if it's worse than always-retrieve, just use single-agent RAG.

- **The synthesizer's groundedness is poor enough that the critic is firing constantly.** Either the retrieval is poor (work on the retrieval pipeline first) or the synthesizer is paraphrasing too aggressively (tighten the synthesizer's prompt to require verbatim citation phrasing).

- **You need retrieval evaluators that trigger fallback** (e.g., to web search when corpus retrieval fails). That's CRAG territory. Different design problem; see the framing page.

## Related concepts

- The framing of when multi-agent RAG earns its place: [multi-agent RAG](./multi-agent-rag.md).
- The supervisor mechanics: [supervisor-worker pattern](./supervisor-worker-pattern.md).
- The critic mechanics: [generator-critic pattern](./generator-critic-pattern.md).
- The planner mechanics: [planner-executor pattern](./planner-executor-pattern.md).
- The handoff discipline that citation preservation follows: [handoffs and shared state](./handoffs-and-shared-state.md#rule-1-handoffs-carry-structured-payloads-not-free-text).

## References

- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — the orchestrator-workers pattern.
- Anthropic 2024, ["Introducing Contextual Retrieval"](https://www.anthropic.com/news/contextual-retrieval) — Lab 08's contextual augmentation, used in Lab 13's v3 pipeline.
- Reimers & Gurevych 2019, ["Sentence-BERT"](https://arxiv.org/abs/1908.10084) — the cross-encoder rerank model class Lab 07's pipeline uses.
- Cormack et al. 2009, ["Reciprocal Rank Fusion"](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) — the RRF combiner Lab 07 uses to merge dense and BM25 results.
