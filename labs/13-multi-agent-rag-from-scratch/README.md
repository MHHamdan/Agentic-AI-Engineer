# Lab 13 — Multi-agent RAG from scratch

> ⏱ 130-160 min · 🟡 Intermediate · Prerequisites: Lab 10 (recommended: Labs 06-08, 11, 12)

Compose Path 02's retrieval pipeline with Path 03's coordination patterns. A **retriever-worker** wraps Lab 06-08's pipeline (auto-detecting v2 vs v3 based on whether the contextual cache exists); a **supervisor** decides when retrieval is needed; a **synthesizer** composes the final answer with citation preservation. Optional stretch sections add Lab 11's critic-on-synthesis and Lab 12's planner-driven parallel retrievals.

No new dependencies beyond what Labs 06-08 and Lab 10 already required.

## What you'll build

```
                    user query
                        │
                        ▼
                ┌───────────────┐
                │  supervisor   │ ← decides: retrieve? skip?
                │               │   (retrieval-decision rules in prompt)
                └───────────────┘
                  │            │
        retrieve  │            │  skip (stable-knowledge)
                  ▼            │
        ┌───────────────┐      │
        │  retriever    │      │
        │  (Lab 06-08   │      │
        │   pipeline)   │      │
        └───────────────┘      │
                  │            │
                  ▼            │
            chunks envelope    │
            {status, chunks:   │
             [{id, text,       │
               source,         │
               score}]}        │
                  │            │
                  └─────┬──────┘
                        ▼
                ┌───────────────┐
                │  synthesizer  │ ← cites by chunk id; passes chunks through verbatim
                └───────────────┘
                        │
                        ▼
                  final answer
                  with citations
```

Three agents in the headline path:

- **Supervisor** — Lab 10's supervisor pattern with two new tools (`retrieve`, `synthesize`). Reads the user query, decides whether to retrieve based on the four retrieval-decision rules in its system prompt, dispatches accordingly.
- **Retriever** — Wraps Lab 06-08's retrieval pipeline as a single function. Auto-detects v2 (Lab 07: dense + BM25 + RRF + cross-encoder rerank) vs v3 (Lab 08: + contextual augmentation) based on whether `../08-contextual-retrieval-and-query-rewriting/context_cache.json` is available. Returns structured `{status, chunks, query, pipeline}`.
- **Synthesizer** — Lab 10-style writer worker, with a system prompt that requires inline `[chunk_id]` citations and a citation list at the end. Reads chunks verbatim; the supervisor never paraphrases or filters before passing chunks on.

Two stretch sections compose with prior Labs:

- **Critic on synthesis** (composes with Lab 11) — Reads `(chunks, draft)` for groundedness. Same structured `{status, issues}` envelope as Lab 11; same bounded refinement (`MAX_REFINEMENT_CYCLES = 3`).
- **Planner-driven parallel retrieval** (composes with Lab 12) — For compound queries ("compare X, Y, Z"), the planner emits a Plan with multiple `retrieve` steps in the same `parallel_group`. Executor pool runs them concurrently. Synthesizer merges.

## Goal

By the end of the lab you should be able to:

- Wrap an existing retrieval pipeline as a single multi-agent worker, with a clean structured envelope and no leakage of retrieval internals to the supervisor.
- Apply the four retrieval-decision rules in a supervisor's system prompt and verify them with the retrieve/skip diagnostic.
- Preserve citations across the retrieval → supervisor → synthesis handoff using structural payload passing (not LLM-tracked).
- Diagnose the four multi-agent-RAG-specific failure modes (citation drift, retrieval skip, retrieval over-call, chunk drift) from a trace.
- Reason about when multi-agent RAG earns its place over single-agent RAG (the deciding-to-retrieve framing).
- Compose this with Lab 11's critic for groundedness and with Lab 12's planner for compound queries — both as optional integrations, not required additions.

## Prerequisites

- **Lab 10** — the supervisor-worker pattern. Lab 13's supervisor extends Lab 10's dispatcher with retrieve and synthesize tools.
- **Labs 06-08 (recommended)** — the retrieval pipeline. Lab 13 wraps this pipeline as a worker; if you haven't built it, you can still run Lab 13 (it rebuilds chunks inline from Lab 06's corpus), but the conceptual framing assumes you understand what's happening inside the retriever.
- **Lab 11 (for stretch 1)** — generator-critic with bounded refinement.
- **Lab 12 (for stretch 2)** — planner-executor with bounded parallel execution.
- **Concept pages** — at minimum [multi-agent RAG](../../concepts/multi-agent/multi-agent-rag.md) and [retriever-as-worker](../../concepts/multi-agent/retriever-as-worker.md). The lab references the four failure modes and the four retrieval-decision rules directly.

## Setup

No new dependencies. The lab uses what Labs 06-08 already installed:
- `sentence-transformers` (for the dense embedder and cross-encoder rerank model)
- `rank-bm25` (for BM25)
- Standard ML stack (numpy, sklearn-style imports if needed)

If you skipped Labs 06-08: run `pip install sentence-transformers rank-bm25` in your existing virtualenv.

Lab 06's corpus must exist at `../06-agentic-rag-from-scratch/corpus/`. If you didn't run Lab 06, the corpus files are still there (they're checked into the repo); the lab will build chunks from them inline.

## Structure

Roughly 35-40 cells, output-stripped, sample-output markdown cells throughout. The lab is structured so the deltas from Lab 10 and the integration with Labs 06-08 are visible at each turn.

- **Step 0**: Setup — environment check; warn if the corpus is missing; auto-detect whether Lab 08's `context_cache.json` is available.
- **Step 1**: Compact recap of Lab 10's machinery (chat client, structured envelopes, supervisor pattern) and Lab 06-08's retrieval pipeline. Not a re-derivation — one cell each.
- **Step 2**: Load Lab 06's corpus and build chunks inline. Same `TARGET_TOKENS=160` and `OVERLAP_TOKENS=32` as Lab 06 — pinned for compatibility with Lab 08's cache if present.
- **Step 3**: Build the retrieval pipeline inline. Dense + BM25 + RRF + cross-encoder rerank (Lab 07's v2 pipeline). If `context_cache.json` is available, add contextual augmentation (Lab 08's v3 pipeline) on top.
- **Step 4**: Build the retriever-worker. `retriever_agent(query, top_k)` wraps the pipeline; returns structured `{status, chunks, query, pipeline}` envelope. `RetrieveArgs` Pydantic schema for the supervisor's tool dispatch.
- **Step 5**: Build the synthesizer worker. System prompt requires inline `[chunk_id]` citations and a citation list at the end. Returns `{status, answer, citations}`.
- **Step 6**: Wire the supervisor. Lab 10 pattern with `call_retriever` and `call_synthesizer` tools. System prompt includes corpus description and the four retrieval-decision rules. `SUPERVISOR_MAX_STEPS = 6` (same as Lab 10; the multi-agent RAG headline path is short: retrieve → synthesize → finalize).
- **Step 7**: Run end-to-end on a corpus-grounded query.
- **Step 8**: The retrieve/skip diagnostic. Feed the supervisor a stable-knowledge query (something the model knows from training and the corpus doesn't cover) and verify it doesn't retrieve. Feed a corpus-grounded query and verify it does retrieve. If your supervisor retrieves on everything, the retrieval-decision rules in its prompt aren't working — re-read the four rules and tighten the corpus description.
- **Step 9**: Failure-mode walkthrough — each of the four multi-agent-RAG failure modes with the mitigation Lab 13 ships:
  - **Citation drift** → supervisor passes chunks envelope through verbatim; synthesizer cites by `chunk_id`; show the structural enforcement.
  - **Retrieval skip** → corpus description in the supervisor prompt; conservative "when in doubt, retrieve" guidance.
  - **Retrieval over-call** → the four retrieval-decision rules including "skip for stable-knowledge questions."
  - **Chunk drift** → demonstrated via Step 10's critic-on-synthesis (or, without it, via the synthesizer's "do not paraphrase beyond what the chunks support" rule).
- **Step 10** (stretch 1): Add Lab 11's critic on synthesis. Composes the generator-critic refinement loop with the multi-agent RAG headline path. The critic reads `(chunks, draft)` and flags ungrounded claims. Bounded refinement with `MAX_REFINEMENT_CYCLES = 3`.
- **Step 11** (stretch 2): Planner-driven research with parallel retrievals (composes with Lab 12). For compound queries, the planner emits a plan with multiple `retrieve(query=...)` steps in the same `parallel_group`; the executor pool runs them concurrently.

## What to watch for

Five practical issues:

1. **The supervisor retrieves on every query.** Symptom of either (a) the corpus description in the system prompt being too vague ("the corpus has documents about agents") so the LLM defaults to retrieval, or (b) the retrieval-decision rules being too weak. The fix is a more specific corpus description and explicit examples of what *doesn't* warrant retrieval. Step 8's diagnostic surfaces this before it pollutes real traces.

2. **The synthesizer cites by [1], [2] instead of by chunk id.** Sign the citation discipline isn't being enforced. The synthesizer's system prompt must say explicitly "cite by the chunk_id field from the chunks envelope; render the citation list at the end as [chunk_id] source — title." If you let it auto-number, the citations don't survive the supervisor → synthesizer handoff cleanly.

3. **Chunk IDs surface in the user-facing answer literally.** Sometimes the synthesizer outputs `[chunk_42]` instead of a clean `[42]` or a section-anchor reference. This is mostly cosmetic but worth a prompt tweak if it bothers you. Lab 13 leaves the chunk_id as-is for traceability; production systems usually rewrite to a cleaner numeric form *after* the synthesizer runs.

4. **The v2/v3 auto-detect fails.** If `context_cache.json` exists but was built with different chunk parameters (different `TARGET_TOKENS` or `OVERLAP_TOKENS`), v3 contextual augmentation will silently produce mismatches. Lab 13 verifies the chunk IDs in the cache match the rebuilt chunks; if not, it falls back to v2 with a printed warning. Don't suppress that warning in production.

5. **Cost.** A typical Lab 13 run does:
   - 1 supervisor call (routing decision)
   - 0-1 retriever calls (the retrieval pipeline itself doesn't use the LLM, except optionally for query rewriting in v3)
   - 1 synthesizer call
   - Total: 2-4 LLM calls per query, plus the cross-encoder rerank (local, cheap).
   With the Lab 11 critic stretch: 4-8 calls. With the Lab 12 planner stretch on a 3-fold compound query: 8-12 calls.

## Anti-scope

Deliberately out of scope, scoped for future batches:

- **CrewAI, AutoGen, LangGraph multi-agent helpers** — none of them. The lab is `chat_with_tools` + Lab 06-08's pipeline imports all the way down. Framework bridges come later.
- **New retrieval techniques.** Lab 13 *composes* the retrieval from Labs 06-08; it doesn't invent new retrieval. Distributed retrieval, vector DB integrations (Qdrant, Pinecone, Weaviate), and federated multi-corpus search are out of scope.
- **Self-RAG / CRAG / GraphRAG.** Different design problems; explained in the concept page but not implemented in this lab.
- **Production observability** — Path 06.
- **Multi-agent evaluation** — Module 6.
- **MCP / A2A** — Path 04.
- **Persistent retrieval state** — the corpus is loaded once per notebook run.
- **Multi-corpus federation** — one corpus per lab run.

## Run-time and cost

Per end-to-end run on the headline path:

- ~1-2 seconds to load the cross-encoder model (first run only; cached afterward).
- ~10-30 seconds to build chunks + initialize the retrieval pipeline (one-time per kernel session).
- ~3-6 seconds per query (1 supervisor call + 1 retrieval pipeline run + 1 synthesizer call).

At gpt-4o-mini rates, well under $0.05 per query. The retrieval pipeline itself is local and free. Stretch sections roughly double the cost per query.

## Solution

A reference implementation will land in `solution/lab.ipynb` in a follow-up solutions batch. Two implementation choices worth flagging up front:

- **The retriever is a function wrapper, not a class.** The retrieval pipeline has state (loaded models, indexed chunks) that lives in module-level closures. The `retriever_agent(query, top_k)` function reads that closure state but doesn't own it. This keeps the worker-as-function pattern from Lab 10 intact.
- **The supervisor never sees individual retrieval signals.** No BM25 scores, no dense cosines, no rerank logits. The `score` field in the chunks envelope is informational; the supervisor's system prompt explicitly says not to reason about it. If the chunks are present, they're usable; if not, the retriever returned `empty`.

## Next

- After completing the lab, take the [multi-agent RAG quiz](../../quizzes/multi-agent/multi-agent-rag.md).
- Path 03 continues with Module 5 (framework bridge — re-implementing Labs 10-13 in LangGraph's multi-agent primitives) in a future batch.
- A follow-up solutions batch will provide reference implementations for Labs 10/11/12/13 together.
