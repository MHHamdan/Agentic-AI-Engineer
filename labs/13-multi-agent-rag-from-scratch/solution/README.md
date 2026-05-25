# Lab 13 · Reference solution

The polished final implementation of [Lab 13: Multi-agent RAG from scratch](../README.md).

The integrative lab. Composes Path 02's retrieval pipeline (Labs 06-08: dense + BM25 + RRF + cross-encoder rerank, with optional Lab 08 contextual augmentation) with Lab 10's supervisor-worker pattern. The retriever-worker wraps the full pipeline as a single function; the supervisor decides when retrieval is needed; the synthesizer composes with chunk_id citations.

> 📖 The concept pages that frame this implementation:
> [`multi-agent-rag`](../../../concepts/multi-agent/multi-agent-rag.md),
> [`retriever-as-worker`](../../../concepts/multi-agent/retriever-as-worker.md).
> 🧠 Calibrate against the [multi-agent RAG quiz](../../../quizzes/multi-agent/multi-agent-rag.md).
> ⬅️ Builds on [Lab 10's solution](../../10-supervisor-worker-from-scratch/solution/README.md) and Path 02 Labs 06-08.

## What this solution implements

The headline path from the parent lab:

- Setup: locate Lab 06's corpus and (optionally) Lab 08's `context_cache.json`. Auto-detect v2 vs v3 pipeline based on cache availability with a 90% chunk-ID coverage check.
- Inline chunker: rebuild Lab 06's chunks with `TARGET_TOKENS=160`, `OVERLAP_TOKENS=32` — pinned for Lab 08 cache compatibility.
- Retrieval pipeline (inline): dense (MiniLM) + BM25 + RRF (k=60) + cross-encoder rerank (ms-marco-MiniLM-L-6-v2). When `context_cache.json` is available and ≥90% chunk-ID coverage, indexed text is `context + chunk_text` (Lab 08 v3); the retrieval result returns the original chunk text either way.
- Retriever-worker: `retriever_agent(query, top_k)` wraps the pipeline. Returns structured `{status, chunks: [{id, text, source, title, score}], query, pipeline}`. Relevance floor at `MIN_RERANK_SCORE = -2.0`.
- Synthesizer: cites by `[chunk_id]`, lists citations at the end. Refuses to paraphrase beyond what chunks support.
- Supervisor: Lab 10 pattern with `call_retriever` + `call_synthesizer` tools. System prompt encodes the four retrieval-decision rules + a corpus description. `SUPERVISOR_MAX_STEPS = 6` (headline path is short).
- One end-to-end demonstration run on a corpus-grounded query.

**Not in this solution** (deliberately): the retrieve/skip diagnostic (parent Step 8), the four-failure-mode walkthrough (parent Step 9), the Lab 11 critic-on-synthesis stretch (parent Step 10), the Lab 12 planner-driven-retrieval stretch (parent Step 11). Those are exploratory; the solution is the canonical mechanism.

## Implementation choices

### Six design decisions worth flagging

**1. The retriever is a function wrapper, not a class.** The retrieval pipeline has state (loaded models, indexed chunks) held in module-level closures. `retriever_agent(query, top_k)` reads that state but doesn't own it. This keeps the worker-as-function pattern from Lab 10 intact, and makes the retriever interchangeable with any other Lab-10-style worker.

**2. The supervisor never sees retrieval internals.** No BM25 scores, dense cosines, or rerank logits surface to the supervisor. The `score` field in the envelope is informational only. The supervisor's system prompt explicitly says not to reason about scores. Separation of concerns: retrieval quality is the retriever's job (it has the cross-encoder and the relevance floor); routing is the supervisor's job. Mixing them produces a supervisor "second-guessing" the retriever using a weaker signal.

**3. Chunks pass through the supervisor to the synthesizer VERBATIM.** `CallSynthesizerArgs.chunks: list[dict]` accepts the raw envelope. The supervisor doesn't paraphrase, filter, summarize, or re-number. This is the structural mitigation for citation drift — the canonical multi-agent-RAG bug. Anywhere the supervisor reformats chunks before passing them is where citations can drop.

**4. The synthesizer cites by `chunk_id`, not auto-numbered `[1]/[2]`.** System prompt explicit. Auto-numbering loses the chain of custody — the chunk_id maps back to a specific chunk in the corpus, [1] doesn't. Production systems sometimes rewrite chunk_ids to cleaner numeric form *after* the synthesizer runs, but the synthesizer must emit chunk_ids first.

**5. v2/v3 auto-detect with 90% coverage check.** If `context_cache.json` exists but the cached chunk IDs cover less than 90% of the rebuilt chunks (e.g., chunk parameters changed between Lab 08 and this lab), the auto-detect falls back to v2 with a *printed warning*. Silently using a stale cache would produce wrong context attached to chunks — correct-looking but corrupt retrieval. The 90% threshold catches parameter drift visibly.

**6. The relevance floor is `MIN_RERANK_SCORE = -2.0`.** Cross-encoder scores are unbounded logits; -2.0 is the empirical floor for this corpus where chunks become not-usefully-relevant. Tuned manually; for production you'd tune per-corpus. The floor lets the retriever return `status="empty"` cleanly — distinguishing "corpus has nothing relevant" from "the retriever crashed."

## Common variations that also work

**Pure v2 pipeline.** Skip the contextual augmentation entirely; always use Lab 07's pipeline. Simpler, less context-management, slightly lower precision on technical queries. Fine if you haven't completed Lab 08.

**Different relevance floors.** `MIN_RERANK_SCORE = -1.0 or -3.0`. The right value depends on the corpus and the cross-encoder model. Tighter floors produce more `empty` returns; looser floors produce more `ok` returns with low-relevance chunks. Default to slightly loose (more chunks reaching the synthesizer) since the synthesizer's prompt is strict about not over-relying on weak evidence.

**Different `top_k`.** Default 5. Production RAG systems often use 10-20 for the supervisor's first retrieval; this solution sticks with 5 to keep the synthesizer's prompt short and the trace readable. Higher `top_k` is rarely wrong; lower `top_k` (< 3) tends to miss relevant chunks the rerank would have caught.

## Bugs to watch for

Five things that pass syntax but fail eval:

**1. The supervisor retrieves on every query.** Symptom of either (a) the corpus description in the system prompt being too vague, or (b) the retrieval-decision rules being too weak. If you ask "what year was Marie Curie born?" and the supervisor retrieves, your retrieve-skip rule isn't firing. Fix: more specific corpus description + explicit examples of what doesn't warrant retrieval.

**2. The synthesizer cites by `[1], [2]` instead of by `chunk_id`.** The synthesizer's system prompt didn't enforce chunk_id citations, or the supervisor reformatted chunks before passing them. Verify: the synthesizer's output should contain literal chunk IDs like `[01-agent-loop_000]`. If it contains `[1]`, the chain of custody broke somewhere.

**3. The v2/v3 auto-detect mismatches.** If `context_cache.json` exists from a previous Lab 08 run but with different `TARGET_TOKENS`/`OVERLAP_TOKENS`, the chunk IDs in the cache don't match the rebuilt chunks. Without the coverage check, v3 silently attaches the wrong context to chunks. The 90% threshold catches this; suppress the warning at your peril.

**4. The synthesizer paraphrases beyond what chunks support.** The synthesizer "fills in" missing information from training data, producing claims with chunk_id citations that don't actually appear in those chunks. The Lab 11 critic-on-synthesis stretch catches this structurally; without it, the synthesizer's "do not paraphrase beyond what chunks support" prompt rule is best-effort. Verify by reading the chunks alongside the synthesized answer.

**5. The retriever's score floor is too high.** If `MIN_RERANK_SCORE = 5.0`, the retriever almost always returns `empty` even on corpus-grounded queries. The supervisor then falls back on training data with no signal that the corpus failed. Verify with a query you know is in the corpus; if the retriever returns `empty`, the floor needs tuning.

## Differences from naive implementations

Three things a learner might miss on first pass:

- **The retriever returns the ORIGINAL chunk text, not the indexed (contextualized) text.** When v3 is active, chunks are indexed as `context + chunk_text` — but the retriever's result contains only `chunk_text`. The synthesizer composes from the original text; the contextual augmentation is purely an indexing-time intervention to improve retrieval precision. This is the same discipline as Lab 08.

- **`SUPERVISOR_MAX_STEPS = 6` is enough for the headline path.** Trajectory: 1 call to retriever + 1 call to synthesizer + 1 finalization = 3 supervisor steps. The 6 budget gives headroom for retry on transient failures. Higher caps invite over-routing (retrieving multiple times when one retrieval is enough).

- **The retriever is run synchronously inside the supervisor's tool call.** Not asynchronously, not in a separate thread. The pipeline is fast (sub-second per query); threading it would add complexity for no benefit. The parent lab's Lab 12 stretch *does* parallelize retrievals (for compound queries), but that's a different pattern.

## Cost and timing

Per end-to-end run on the demo task:

- ~1-2 seconds to load the cross-encoder model (first kernel run only; cached afterward).
- ~10-30 seconds to build chunks + initialize the retrieval pipeline (one-time per kernel session).
- Per query: 1 supervisor call (routing) + 1 retrieval (local, ~0.5-1 second) + 1 synthesizer call.

Total: 2-3 LLM calls per query, ~$0.02-$0.04 at gpt-4o-mini rates. The retrieval pipeline itself is local and free. Typical end-to-end: 3-6 seconds per query after warm-up.

## Next

After completing this lab, you've finished Path 03's headline material (Modules 1-4). The next module (Module 5, future batch) is the framework bridge — re-implementing Labs 10-13 in LangGraph's multi-agent primitives (`Send`, `Command`, sub-graphs) and comparing line-by-line. The pedagogical payoff: now that you've built the patterns from scratch, you can evaluate whether the framework genuinely simplifies them or just hides complexity.

Module 6 (also future) extends Lab 09's evaluation harness for multi-agent: trajectory-level metrics, plan-quality scores, replan rate, citation preservation rate.
