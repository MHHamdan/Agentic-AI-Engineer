# Multi-agent RAG

> ⏱ ~10 min · 🟡 Intermediate · Prerequisites: [supervisor-worker pattern](./supervisor-worker-pattern.md), [generator-critic pattern](./generator-critic-pattern.md), Path 02 Labs 06-08

This is the integrative page. Path 02 built retrieval (dense + BM25 + RRF + cross-encoder rerank + contextual augmentation + query rewriting) as a single agent's tool. Path 03 built coordination patterns (supervisor-worker, generator-critic, plan-and-execute) without retrieval. Multi-agent RAG is where the two finally meet.

The motivating shift: in single-agent RAG, the agent *always* retrieves before answering. That's wasteful when the question doesn't need retrieval, and brittle when one retrieval isn't enough. Multi-agent RAG turns retrieval into a *coordinated* concern — the supervisor decides when to retrieve, how many retrievals to issue, whether to critique results, and how to compose what comes back.

The next page, [retriever-as-worker](./retriever-as-worker.md), covers the specific pattern Lab 13 implements. This page covers the framing.

## What changes from single-agent RAG

Single-agent RAG (Lab 06-08):

```
query → retrieve → augment_prompt(chunks) → generate → answer
```

The retrieval is always-on. The generator sees retrieved chunks before producing the answer. The agent has no choice about whether to retrieve.

Multi-agent RAG:

```
query → supervisor decides → maybe retrieve → maybe critique → synthesize → answer
                       ↘  (or skip directly to synthesize for non-corpus queries)
```

Three properties that change:

1. **Retrieval is conditional.** The supervisor reasons about whether the query is corpus-grounded. Definitional questions, stable-knowledge questions, and questions about things outside the corpus's scope don't trigger retrieval.

2. **Retrieval is multi-step.** The supervisor can issue multiple retrievals for compound questions ("compare X and Y" might want one retrieval per entity), or chain retrievals where the second depends on the first.

3. **Retrieval is reviewable.** A critic can inspect retrieved chunks for relevance before synthesis, and review the synthesis for groundedness afterward. Single-agent RAG has no natural place to put either check.

These are not free. Each adds an LLM call and a failure surface. The honest framing: multi-agent RAG earns its place when *deciding* to retrieve is itself a non-trivial judgment, or when *multiple* retrievals must be composed. For queries where you always retrieve and always synthesize, single-agent RAG is simpler and cheaper.

## Three architectural patterns

There are three meaningfully different ways to compose retrieval with multi-agent patterns. Lab 13 implements the first as the headline; the other two appear as stretch sections.

### Pattern 1: Retriever-as-worker

The simplest composition. The retrieval pipeline (Lab 06-08) becomes a single tool the supervisor can call. The supervisor decides when and what to retrieve; the synthesizer composes from the retrieved chunks.

```
        user query
            │
            ▼
       supervisor   ← decides: retrieve? skip? how many times?
        ┌──┴──┐
        ▼     ▼
    retriever  (skip to synthesizer)
        │
        ▼
       chunks
        │
        ▼
    synthesizer  ← composes the final answer with citations
        │
        ▼
       answer
```

When this fits: most real workloads. Mix of corpus-grounded queries and stable-knowledge queries. Single retrievals usually suffice. The supervisor's main job is the retrieve/skip decision.

### Pattern 2: Planner-driven research

Composition with Lab 12's planner-executor. The planner emits a plan with multiple parallel retrievals; executors run them concurrently; the synthesizer merges.

```
        user query
            │
            ▼
       planner   ← emits plan: [retrieve(X), retrieve(Y), retrieve(Z), synthesize]
            │
            ▼
    Plan { steps with depends_on, parallel_group="retrievals" }
            │
            ▼
   executor pool   ← parallel retrievals (ThreadPoolExecutor, max 3)
            │
            ▼
       all chunks
            │
            ▼
    synthesizer
```

When this fits: questions that decompose cleanly into independent retrievals — comparisons ("compare X, Y, Z"), multi-aspect summaries, cross-referencing. The planner's parallel groups give you wall-clock savings; sequential single-agent RAG with multiple turns would be much slower.

When it doesn't fit: questions where each retrieval depends on the previous one's results. Plan-and-execute can't parallelize what isn't parallelizable.

### Pattern 3: Critic-on-retrieval

Composition with Lab 11's critic. A critic reviews either (a) the retrieved chunks before synthesis (filtering or requesting re-retrieval), or (b) the synthesized answer for groundedness (the standard Lab 11 placement).

```
        user query
            │
            ▼
       supervisor
            │
            ▼
        retriever
            │
            ▼
         chunks ─────┐
            │        │
            ▼        ▼
        synthesizer  critic (option a: review chunks)
            │
            ▼
         draft ─────┐
            │       │
            │       ▼
            │     critic (option b: review draft for groundedness)
            ▼
         final
```

Lab 13's stretch section adds option (b) — critic-on-synthesis — because it's the cleaner integration. Option (a) — critic-on-chunks — is harder to get right: the critic needs to know what "relevant" means for this query, which is roughly the same judgment the retriever's rerank already made.

When this fits: high-stakes synthesis where ungrounded claims have real cost (legal, medical, financial summaries). The critic is your last line of defense against the synthesizer paraphrasing the chunks into something they don't actually say.

## When multi-agent RAG earns its place

Three legitimate motivations:

**Deciding-to-retrieve is non-trivial.** If half your queries are stable-knowledge questions the model handles well, single-agent RAG wastes a retrieval call (and a fetch-or-search) on every one. The supervisor's retrieve/skip decision is the value-add. This is the most common motivation.

**Multiple retrievals must be composed.** "What were the financial results for Apple, Google, and Microsoft in Q4 2024?" is three retrievals merged. Single-agent RAG either issues one retrieval (and gets a mix), or runs three sequential turns (slow). Multi-agent RAG with a planner runs them in parallel.

**Retrieval precision matters enough to justify a critic.** The synthesizer can confidently produce ungrounded claims when chunks don't actually support what the user asked. A critic checking groundedness catches this. Cost: roughly 2x the synthesis cost. Worth it when wrong is worse than slow.

## When single-agent RAG is enough

Three signals to *not* reach for multi-agent RAG:

- **Every query needs retrieval.** Customer support over a product manual, legal-doc Q&A — the supervisor's retrieve/skip decision is a no-op. Single-agent RAG is simpler.
- **One retrieval per query is enough.** Standard FAQ-style use cases. The retrieval pipeline already handles complexity inside the single retrieval (query rewriting, multi-query, rerank).
- **Precision is acceptable from the retrieval pipeline.** If Lab 07's rerank + Lab 08's contextual augmentation give you the precision you need, adding a critic is pure overhead.

A useful heuristic: **if your retrieval pipeline already does the job, multi-agent RAG buys you the decision layer, not the retrieval improvement**. Reach for multi-agent RAG when you need the decision layer; stay with single-agent RAG when you don't.

## Four failure modes specific to multi-agent RAG

These don't appear in single-agent RAG or in the prior multi-agent patterns. They're emergent at the composition layer.

### Citation drift

The retriever returns chunks with `source` fields. The supervisor passes the chunks to the synthesizer. The synthesizer's prompt asks for cited output. Somewhere in this handoff, the source information gets lost — the synthesizer cites by chunk number ([1], [2]) but doesn't actually know which chunk number maps to which source, and the citations end up wrong or generic.

The mitigation is structural: the retriever's envelope carries `source` and `id` for each chunk; the supervisor passes the *entire envelope* through to the synthesizer (not just chunk text); the synthesizer's prompt is told to cite by `id` and to render the citation list at the end. The supervisor never re-numbers, summarizes, or filters chunks before passing them on — that's the canonical bug.

### Retrieval skip

The supervisor decides not to retrieve when it should have. The model "knows" the answer (or thinks it does) and confidently produces an answer that's wrong because the corpus had the right one. This is the supervisor falling back on its training data when retrieval was the right move.

Mitigations:
- The supervisor's system prompt includes a description of the corpus ("the corpus covers X, Y, Z topics with documents from W timeframe") so the LLM can decide whether a query falls inside that scope.
- Conservative default: when in doubt, retrieve. The cost of unnecessary retrieval is low; the cost of skipping a needed retrieval is wrong answers.
- Eval-time spot-check: feed queries you know are corpus-grounded and verify retrieval fires.

### Retrieval over-call

The opposite failure. The supervisor retrieves on every turn even for queries that obviously don't need it ("what is your name?"). Wasteful but rarely harmful — you pay for retrieval calls that surface chunks the synthesizer ignores.

This is mostly a cost concern, not a quality one. Mitigation is the same retrieval-decision rules: stable-knowledge questions, definitional questions, and meta-questions about the agent don't trigger retrieval.

### Chunk drift

The synthesizer "paraphrases" the chunks beyond what they actually say. The retrieval was correct; the synthesis loses fidelity. Citations still point at the right chunks, but the claims attached to those citations aren't what the chunks support.

This is where Lab 11's critic earns its place. The critic reads `(chunks, draft)` and checks every claim in the draft for a supporting sentence in some chunk. Unsupported claims get flagged; the synthesizer revises.

## When self-RAG / CRAG are the right pattern instead

A note for context, because the terms get mixed up.

**Self-RAG** (Asai et al. 2023) trains the model to emit special tokens that indicate when to retrieve, what to retrieve, and whether the retrieval was useful. It's a *training-time* intervention — you fine-tune the model to be retrieval-aware. Useful in production systems where you control the model; out of scope for an educational lab using off-the-shelf LLMs.

**CRAG** (Corrective RAG, Yan et al. 2024) adds a retrieval evaluator that scores retrieved documents and triggers a fallback (web search) when the corpus retrieval is poor. Architecturally similar to critic-on-retrieval (Pattern 3) but with the corrective web-search fallback as the distinctive feature.

Both are research patterns that overlap conceptually with multi-agent RAG but solve different problems. If you genuinely need them, you'll know — and you'll build them on top of the patterns Lab 13 covers, not instead of them.

## Related concepts

- The specific pattern Lab 13 implements: [retriever-as-worker](./retriever-as-worker.md).
- The supervisor mechanics this builds on: [supervisor-worker pattern](./supervisor-worker-pattern.md).
- The critic pattern that composes optionally: [generator-critic pattern](./generator-critic-pattern.md).
- The planner pattern that composes for stretch: [planner-executor pattern](./planner-executor-pattern.md).
- The retrieval pipeline this composes with: Path 02 Labs 06, 07, 08.

## References

- Lewis et al. 2020, ["Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"](https://arxiv.org/abs/2005.11401) — the original RAG paper. Useful for understanding what changed when retrieval-and-generation got tightly coupled.
- Asai et al. 2023, ["Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection"](https://arxiv.org/abs/2310.11511) — training-time approach to retrieval-aware models.
- Yan et al. 2024, ["Corrective Retrieval Augmented Generation"](https://arxiv.org/abs/2401.15884) — CRAG's retrieval evaluator + fallback design.
- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — the orchestrator-workers pattern applied to retrieval is the same shape as retriever-as-worker.
- Anthropic 2024, ["Introducing Contextual Retrieval"](https://www.anthropic.com/news/contextual-retrieval) — the contextual augmentation Lab 08 implements, which Lab 13 uses when its cache is available.
