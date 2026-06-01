# 02 · Agentic RAG

> 🟡 Intermediate · ⏱ 12–17 hours · 📍 Start here once you've completed Path 01 · ✅ Path 02 v1 complete

## Who this is for

You've finished Foundations: you can build an agent loop from scratch, design tools that work, and ship a research agent against the real web (Lab 03). Now you want to do the same thing with a *controlled corpus* instead of the open web — retrieval-augmented generation, the pattern most production agent systems converge on.

This path takes you from "I understand the search/retrieval distinction conceptually" to "I can build an agentic RAG system end-to-end with a production-grade retrieval pipeline, from chunking through reranking to chunk-level context augmentation to query-side rewriting, with a debugging mental model for production failure modes — *and* an evaluation harness that tells me whether my interventions actually helped." It does this from scratch in pure Python first — same discipline as the Foundations labs — so when you later reach for LangChain or LlamaIndex or RAGAS or TruLens or DeepEval, you'll know what those abstractions are hiding and when they help.

By the end of Path 02 v1 you should be able to:

- Explain what RAG is and why naive vs. agentic RAG are meaningfully different patterns.
- Implement chunking that respects document boundaries and stays under the embedding model's silent-truncation limit.
- Build a vector index from scratch in ~20 lines of numpy and explain what production vector stores add on top.
- Wire retrieval into the agent loop as a tool — the *same* loop you built in Labs 01/03.
- Track citations at chunk granularity, by the loop and not by the LLM.
- Calibrate top_k, score floors, MMR, and query construction for a specific corpus.
- Build BM25 + dense hybrid retrieval with reciprocal rank fusion from scratch.
- Wire a cross-encoder reranker into the retrieve-then-rerank pipeline and explain its precision/cost tradeoff.
- Implement contextual chunk augmentation (Anthropic's technique) with LLM-generated doc context, cached to disk.
- Implement HyDE, multi-query expansion, and query decomposition from scratch as query-rewriting interventions.
- Diagnose RAG failures against an 8-failure-mode taxonomy and pick the right intervention for each.
- Make an informed call between MiniLM-L6-v2 and OpenAI's `text-embedding-3-small` for a given workload.
- **Build a hand-curated eval set and a from-scratch evaluation harness** that produces comparison tables across every Path 02 intervention.
- Compute retrieval metrics (hits@k, recall@k, MRR, mean rank) and rule-based answer-quality metrics (groundedness, refusal quality) from scratch, plus an optional LLM-as-judge faithfulness check.
- Slice metrics by query category so the per-failure-mode picture is visible, not just the aggregate.

## Prerequisites

**Complete Path 01 — Foundations first.** This is non-negotiable. Lab 06 directly extends Lab 03's pattern, and the conceptual frame ("retrieval as a tool") only makes sense if you've internalized the search-vs-retrieval distinction from Foundations.

Minimum:

- Labs 01, 02, 03 finished.
- The [`search-tools`](../../concepts/tools/search-tools.md) concept page read and understood.
- All five Foundations quizzes passed at 6+/8.

If you've also done Lab 05 (LangGraph), great — but it's not required here. Labs 06-09 stay from-scratch on purpose, mirroring Lab 03's approach.

## How this path is structured

Path 02 v1 is the closed loop: *build* retrieval (Labs 06-08), *diagnose* what fails (failure modes), *measure* whether your interventions help (Lab 09). Five batches across the foundation, the retrieval-quality stack, the corpus and query-side interventions, the failure-modes synthesis, and the evaluation primer. Future batches will add the framework-bridge lab and conversational RAG.

```mermaid
flowchart TD
    subgraph Foundations["Phase 1 — RAG Foundations"]
        direction TB
        A["📖 What is RAG?"]
        B["📖 Retrieval as a tool"]
        C["📖 Chunking and indexing"]
        S1["⚙️ Embeddings snapshot"]
        S2["⚙️ Vector stores snapshot"]
        L6["🧪 Lab 06:<br/>Agentic RAG from scratch"]
        Q1["🧠 RAG fundamentals quiz"]

        A --> B
        B --> C
        C --> S1
        C --> S2
        S1 --> L6
        S2 --> L6
        L6 --> Q1
    end

    subgraph RetrievalStrategies["Phase 2 — Retrieval Strategies"]
        direction TB
        RS["📖 Retrieval strategies"]
        HS["📖 Hybrid search"]
        RR["📖 Reranking"]
        L7["🧪 Lab 07:<br/>Retrieval strategies and reranking"]
        Q2["🧠 Retrieval strategies quiz"]

        RS --> HS
        HS --> RR
        RR --> L7
        L7 --> Q2
    end

    subgraph ContextualRetrieval["Phase 3 — Contextual Retrieval"]
        direction TB
        CR["📖 Contextual retrieval"]
        QR["📖 Query rewriting"]
        FM["📖 Retrieval failure modes"]
        L8["🧪 Lab 08:<br/>Contextual retrieval and query rewriting"]
        Q3["🧠 Contextual retrieval<br/>and query rewriting quiz"]

        CR --> QR
        QR --> FM
        FM --> L8
        L8 --> Q3
    end

    subgraph Evaluation["Phase 4 — RAG Evaluation"]
        direction TB
        E1["📖 What is RAG evaluation?"]
        E2["📖 Eval set construction"]
        E3["📖 Retrieval metrics"]
        E4["📖 Answer quality metrics"]
        L9["🧪 Lab 09:<br/>Evaluating agentic RAG"]
        Q4["🧠 RAG evaluation quiz"]

        E1 --> E2
        E2 --> E3
        E3 --> E4
        E4 --> L9
        L9 --> Q4
    end

    N["🚀 Future batches"]

    Q1 --> RS
    Q2 --> CR
    Q3 --> E1
    Q4 --> N

    classDef concept fill:#E8F0FE,stroke:#1A73E8,stroke-width:2px,color:#0D47A1;
    classDef snapshot fill:#E0F7FA,stroke:#00838F,stroke-width:2px,color:#004D40;
    classDef lab fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px,color:#E65100;
    classDef quiz fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20;
    classDef future fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3px,color:#4A148C;

    classDef foundationGroup fill:#F8FBFF,stroke:#1565C0,stroke-width:2px,color:#0D47A1;
    classDef retrievalGroup fill:#FFF8E1,stroke:#F9A825,stroke-width:2px,color:#E65100;
    classDef contextualGroup fill:#F1F8E9,stroke:#388E3C,stroke-width:2px,color:#1B5E20;
    classDef evaluationGroup fill:#FCE4EC,stroke:#C2185B,stroke-width:2px,color:#880E4F;

    class A,B,C,RS,HS,RR,CR,QR,FM,E1,E2,E3,E4 concept;
    class S1,S2 snapshot;
    class L6,L7,L8,L9 lab;
    class Q1,Q2,Q3,Q4 quiz;
    class N future;
```

The arrows reflect the *recommended* order. Each concept-page set is designed to be read together; they cross-reference each other and converge on the matching lab.

## The reading list — Module 1: Conceptual frame

The conceptual prerequisites for Lab 06. Read these in order; the lab assumes their vocabulary.

1. 📖 **[What is RAG?](../../concepts/rag/what-is-rag.md)** *(~10 min)* — The pattern, naive vs. agentic, what RAG fixes and doesn't fix. Anchored to Lewis et al. (NeurIPS 2020).

2. 📖 **[Retrieval as a tool](../../concepts/rag/retrieval-as-a-tool.md)** *(~9 min)* — The agentic framing. How `search_corpus` and `read_chunk` map onto Lab 03's `web_search` and `fetch_page`. What transfers, what changes.

3. 📖 **[Chunking and indexing](../../concepts/rag/chunking-and-indexing.md)** *(~12 min)* — The stable decisions: chunk size, overlap, boundaries, metadata, what a vector index actually is mechanically. Includes the 256-wordpiece foot-gun.

> 💡 By the end of Module 1 you should be able to read any "RAG explained" article online and (a) follow it, (b) notice which decisions it skips, and (c) explain why search ≠ RAG one more time, in your sleep.

## Module 2: Reference snapshots

The pinned APIs and versions Lab 06 depends on. Reference material — skim once, refer back when you write your own code.

4. ⚙️ **[Embedding models snapshot](../../tools/embeddings/snapshot-v1.0.md)** *(~6 min reference)* — `sentence-transformers/all-MiniLM-L6-v2` as the default (no API key, CPU, 384-dim) and `text-embedding-3-small` as the production swap-in (1536-dim, $0.02/1M tokens). Pinned APIs, honest tradeoffs, the freshness-check protocol.

5. ⚙️ **[Vector stores snapshot](../../tools/vector-stores/snapshot-v1.0.md)** *(~8 min reference)* — A survey of Chroma, pgvector, Qdrant, Weaviate, Pinecone, plus FAISS. A decision aid, not a tutorial. Lab 06 doesn't use any of these; the page explains when you would.

## Module 3: The from-scratch lab

The practical exercise for the conceptual material. Build the whole stack: load the bundled corpus, chunk it, embed it, index it in numpy, wire it as agent tools, and run multi-step retrieval with citation tracking.

6. 🧪 **[Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/)** *(~100–130 min)* — The headline lab. Two tools (`search_corpus`, `read_chunk`), one loop, three test queries, an explicit failure-mode walkthrough, and a stretch section that swaps in OpenAI embeddings.

The lab corpus is bundled — 8 Markdown documents on agent/RAG topics, ~4,700 tokens total. Fully reproducible, no network downloads, you can inspect every document directly.

> 💡 If you can read Lab 03's agent code, you can read Lab 06's. The conceptual move is *only* "swap the I/O layer for retrieval over a local index." Most of the lab is the new I/O layer; the loop is unchanged.

## Module 4: First self-assessment

7. 🧠 **[RAG fundamentals quiz](../../quizzes/agentic-rag/rag-fundamentals.md)** *(~8 min)* — 8 single-select questions on the patterns, the 256-wordpiece foot-gun, citation tracking semantics, the search-vs-RAG distinction, and when to upgrade from numpy.

## Module 5: Retrieval quality

The retrieval-quality concept stack. Each of these reads in ~10–11 minutes and they share a worked example (the Lab 06 corpus). Read in order; Lab 07 assumes them.

8. 📖 **[Retrieval strategies](../../concepts/rag/retrieval-strategies.md)** *(~11 min)* — The four knobs every retriever exposes: `top_k`, score floors, MMR diversification, and query construction. The defensible defaults and how to calibrate them on your corpus.

9. 📖 **[Hybrid search](../../concepts/rag/hybrid-search.md)** *(~10 min)* — Why dense (semantic) and BM25 (lexical) have inverse failure modes. Reciprocal Rank Fusion from the Cormack 2009 paper, weighted combination, and the cascade pattern. When hybrid beats dense alone.

10. 📖 **[Reranking](../../concepts/rag/reranking.md)** *(~10 min)* — The bi-encoder limit; what a cross-encoder sees that a bi-encoder can't. The retrieve-then-rerank pipeline, the `candidate_k → final_k` ratio, model choices from MiniLM-L-6 to bge-reranker-large.

## Module 6: The retrieval-quality lab

11. 🧪 **[Lab 07: Retrieval strategies and reranking](../../labs/07-retrieval-strategies-and-reranking/)** *(~110–140 min)* — Extends Lab 06's `search_corpus` with BM25, RRF (from scratch), MMR (from scratch), and a cross-encoder reranker. Same corpus, same agent loop, measurably better retrieval. Step-by-step side-by-side comparison so every upgrade is visible.

The lab reuses Lab 06's corpus and chunker entirely. The only new dependency is `rank-bm25` for BM25; the `sentence-transformers` install from Lab 06 provides the cross-encoder via its `CrossEncoder` class.

## Module 7: Second self-assessment

12. 🧠 **[Retrieval strategies quiz](../../quizzes/agentic-rag/retrieval-strategies.md)** *(~9 min)* — 8 single-select questions on the four knobs, RRF mechanics, bi-encoder vs cross-encoder architecture, when each intervention helps, and the gotchas around score scales and `candidate_k`.

## Module 8: Quality interventions

The corpus-side and query-side interventions for the failure modes Module 5/6 couldn't fix from inside the retrieval stack. Each of these reads in ~10–11 minutes and they share the Lab 06 corpus as a worked example. Read in order; Lab 08 assumes them.

13. 📖 **[Contextual retrieval](../../concepts/rag/contextual-retrieval.md)** *(~11 min)* — Anthropic's chunk-augmentation technique (Sept 2024). One LLM call per chunk at index time produces a 50-100 token situating context summary; the augmented chunks feed both BM25 and the embedder. Cost optimization via prompt caching. Anthropic's measured 35-67% reduction in retrieval failure rate.

14. 📖 **[Query rewriting](../../concepts/rag/query-rewriting.md)** *(~10 min)* — Three patterns: HyDE (Gao et al. 2022), multi-query expansion (Query2doc; Wang et al. 2023), and query decomposition. When each helps, when each hurts, the cost/latency tradeoffs.

15. 📖 **[Retrieval failure modes](../../concepts/rag/retrieval-failure-modes.md)** *(~11 min)* — The synthesis. Eight failure modes covering all of Labs 06–08. Each has a symptom, a cause, a diagnostic experiment, and an intervention. Includes the decision tree for debugging production RAG. This page is the page to come back to when something breaks.

## Module 9: The quality-interventions lab

16. 🧪 **[Lab 08: Contextual retrieval and query rewriting](../../labs/08-contextual-retrieval-and-query-rewriting/)** *(~110–140 min)* — Extends Lab 07's hybrid+rerank pipeline with contextual chunk augmentation (cached to JSON for free re-runs) and three query-rewriting patterns (HyDE, multi-query, decomposition). Same corpus, same agent loop, more interventions to compose. The stretch section walks the failure-modes decision tree against deliberately-hard queries.

**No new dependencies** on top of Lab 07. The LLM that powers your agent loop also generates the context summaries.

> 💡 After Lab 08 you've built every standard retrieval intervention covered in mainstream RAG literature. The remaining ~5% requires fine-tuning, late-interaction models, or hosted reranker APIs — all real, all out of scope for this path.

## Module 10: Third self-assessment

17. 🧠 **[Contextual retrieval and query rewriting quiz](../../quizzes/agentic-rag/contextual-retrieval-and-query-rewriting.md)** *(~10 min)* — 8 single-select questions on Anthropic's technique mechanics, HyDE, the cost question, the failure-modes decision tree, and the canonical mis-diagnosis (failure mode 7).

## Module 11: RAG evaluation primer

After Lab 08, you've built every standard retrieval intervention. The honest question becomes: **did any of them actually help on your corpus?** Module 11 is the answer. Four concept pages in `concepts/evaluation/` covering what to measure, how to construct an eval set that surfaces the failures synthetic queries would miss, and what the metrics on each side of the retrieval/generation split actually reveal vs. hide. Read in order; Lab 09 assumes them.

18. 📖 **[What is RAG evaluation?](../../concepts/evaluation/what-is-rag-evaluation.md)** *(~10 min)* — Orientation: the retrieval/generation split, offline vs online, correctness vs groundedness (the distinction most teams conflate). Frames the rest of the section.

19. 📖 **[Eval set construction](../../concepts/evaluation/eval-set-construction.md)** *(~10 min)* — The foundation: why 30-50 hand-curated queries beat 1,000 synthetic ones, expected_doc vs expected_chunks tradeoffs, category and failure-label tagging, common pitfalls.

20. 📖 **[Retrieval metrics](../../concepts/evaluation/retrieval-metrics.md)** *(~11 min)* — Hits@k, recall@k, precision@k, MRR, nDCG@k, mean rank of expected chunk. Engineer-friendly Python formulas. What each reveals, what each hides, when each is the right metric.

21. 📖 **[Answer quality metrics](../../concepts/evaluation/answer-quality-metrics.md)** *(~11 min)* — Faithfulness, groundedness, citation accuracy, answer relevance, refusal quality. Rule-based vs LLM-as-judge tradeoffs. The Zheng et al. 2023 documented biases (position, verbosity, self-enhancement). RAGAS, TruLens, and DeepEval as future production tools — mentioned only.

> 🗺️ **Want the whole evaluation picture in one page?** [The RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) *(~16 min)* consolidates the four pages above into a six-layer A-Z map (eval set → component metrics → automated scoring → error taxonomy → CI gates → production monitoring), with the full metric taxonomy, the RAG error taxonomy, benchmarks (BEIR, MTEB), and a build order. Read it for the map; read the four pages above for depth.

## Module 12: The evaluation lab

22. 🧪 **[Lab 09: Evaluating agentic RAG](../../labs/09-evaluating-agentic-rag/)** *(~100–130 min)* — The synthesis lab. A from-scratch evaluation harness that runs your Labs 06-08 pipelines against a 30-question hand-curated eval set (shipped as `eval_set.jsonl`), produces comparison tables sliced by category, scores answer quality with rule-based metrics, and optionally runs LLM-as-judge faithfulness on a small subset.

**No new dependencies** on top of Lab 08. The harness is ~200 lines of pure Python; no RAGAS, no TruLens, no DeepEval — those are deliberately deferred to Path 06 so you understand what they *wrap* before adopting them.

> 💡 After Lab 09, Path 02 v1 closes. You can now build retrieval, diagnose failures, and measure interventions — the closed loop of production RAG work.

## Module 13: Fourth self-assessment

23. 🧠 **[RAG evaluation quiz](../../quizzes/agentic-rag/rag-evaluation.md)** *(~12 min)* — 8 single-select questions on the retrieval/generation split, eval set construction tradeoffs, MRR mechanics, the canonical correctness/groundedness distinction, Zheng et al.'s LLM-as-judge biases, and the rule-based vs LLM-as-judge tradeoff.

## Module 14: SOTA RAG patterns (2024-2026)

With the closed loop in hand — build, diagnose, measure — the last module maps the modern RAG landscape so you know what to add when your eval set shows static RAG failing.

24. 📖 **[SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md)** *(~15 min)* — Self-RAG, Corrective RAG (CRAG), Adaptive RAG, Agentic RAG, Graph RAG, long-context and multimodal RAG. What each pattern adds over static RAG, when it earns its added cost, and the real papers behind each. Ends with a decision guide keyed to the failure you measured in Module 12.

25. 🧠 **[SOTA RAG patterns quiz](../../quizzes/agentic-rag/sota-rag-patterns.md)** *(~10 min)* — 8 questions on matching patterns to failure modes, the cost/benefit of each control loop, and the citations.

### The SOTA pattern labs (build them from scratch)

Three from-scratch labs implement the patterns on top of Lab 06's retrieval stack. Each is self-contained and reuses the Lab 06 corpus, so the contrast with static RAG is direct.

26. 🧪 **[Lab 31: Corrective RAG (CRAG) from scratch](../../labs/31-corrective-rag-from-scratch/)** *(~90–120 min)* — add a retrieval evaluator, decompose-then-recompose refinement, and corrective actions (rewrite-and-retry, web-search fallback). See it route an off-corpus query away from fabrication.

27. 🧪 **[Lab 32: Self-RAG from scratch](../../labs/32-self-rag-from-scratch/)** *(~90–120 min)* — implement the reflection tokens (on-demand retrieve, ISREL, ISSUP, ISUSE) as constrained classification calls; generate one candidate per relevant passage and select by support + usefulness.

28. 🧪 **[Lab 33: Graph RAG from scratch](../../labs/33-graph-rag-from-scratch/)** *(~110–140 min)* — extract entities and relationships, build a `networkx` knowledge graph, detect and summarize communities, and answer global (map-reduce) vs local (traversal) questions. See the global-question win flat retrieval misses. Ships a dedicated entity-rich corpus so the technique's strengths are visible.

> 💡 The math behind the retrieval metrics in Module 11 now has its own page: [Math foundations page 14 — retrieval and ranking metrics](../../math-foundations/14-retrieval-ranking-metrics.md). Runnable (compact) recipes for these patterns are in [`recipes/rag/`](../../recipes/rag/); the labs above are the deeper, from-scratch versions.

## Module 15: Comparing and routing the patterns

Having built the patterns, the closing module measures them against each other and turns the result into a router — the synthesis of everything in Path 02.

29. 🧪 **[Lab 34: Head-to-head RAG pattern evaluation](../../labs/34-rag-pattern-head-to-head/)** *(~90–120 min)* — run static, CRAG, Self-RAG, and Graph RAG over one shared corpus and eval set, score them with the [evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md), and produce a pattern × category comparison table. The finding: each pattern wins the category it was built for, and none dominates.

30. 🧪 **[Lab 35: Adaptive RAG router](../../labs/35-adaptive-rag-router/)** *(~80–110 min)* — build a query classifier that routes each query to the category winner from Lab 34 (parametric → skip retrieval, global/multi-hop → graph, off-corpus-risk → CRAG, specific → flat). This is Adaptive-RAG ([Jeong et al. 2024](https://arxiv.org/abs/2403.14403)) and the synthesis of Labs 31–34.

> 💡 Labs 34 and 35 reuse Lab 33's entity-rich corpus and a shared 16-query eval set (`labs/34-rag-pattern-head-to-head/eval_set.jsonl`) spanning six query categories, so the comparison and the router are measured on the same footing.

## Module 16: Production-hardening the router

The router works — now make it deployable. Train its classifier, give it a fallback for uncertainty, score it with a real judge, and gate it in CI.

31. 🧪 **[Lab 36: Training and hardening the router](../../labs/36-training-the-router/)** *(~100–130 min)* — replace Lab 35's per-query LLM classification with a trained classifier (query embeddings + logistic regression on a labeled set), add a confidence gate from `predict_proba`, and route low-confidence queries to an agentic fallback that tries the top-2 strategies and verifies. An applied-ML lab: cross-validation on small data, trained-vs-prompt cost, and the calibration risk.

32. 🧪 **[Lab 37: Evaluation gates for RAG](../../labs/37-rag-eval-gates/)** *(~90–120 min)* — build an LLM-as-judge scorer that drops into Lab 34's harness in place of token-presence scoring, then wrap the router in an `eval_gate` ([`eval_gate.py`](../../labs/37-rag-eval-gates/eval_gate.py) + a [GitHub Actions workflow](../../.github/workflows/rag-eval-gate.yml)) that blocks CI on routing regressions. The design rule: block on cheap deterministic signals, monitor expensive noisy ones out of band.

> 💡 Module 16 turns the teaching router into a deployable one. Lab 36 is mostly a classification + calibration problem; Lab 37 is mostly evaluation-infrastructure and CI. Together they are the production tail of the RAG track.

## Module 17: Trusting and maintaining the system

A gate that emits numbers and a router trained on clean data are not enough — the numbers have to be calibrated against humans, the thresholds have to come from measurement, and the training data has to keep up with real queries.

33. 🧪 **[Lab 38: Calibrating the eval gate](../../labs/38-calibrating-the-eval-gate/)** *(~90–110 min)* — measure judge-vs-human agreement (Cohen's κ) before trusting judged metrics, derive gate thresholds from a baseline run plus a tolerance band, and operate judged faithfulness as a nightly monitor ([`rag-faithfulness-nightly.yml`](../../.github/workflows/rag-faithfulness-nightly.yml)) rather than a PR gate. Extends Lab 37's `eval_gate.py` with a `--thresholds` config.

34. 🧪 **[Lab 39: The router's query-data lifecycle](../../labs/39-router-data-lifecycle/)** *(~90–110 min)* — the prototype trainset underrepresents messy real-user phrasing (shown by a confidence drop). Capture messy queries, dedup, triage by confidence to a human-review queue, retrain, and measure whether the round helped before promoting — then re-derive the Lab 38 baseline.

> 💡 Module 17 is the operational layer: Lab 38 makes the gate's numbers trustworthy (validate the judge, derive thresholds); Lab 39 keeps the router's training data fresh (capture, triage, retrain, measure). The recurring discipline — validate before you trust, measure before you promote — is the point.

## What's *not* in this path yet

Anti-scope, kept explicit so you know what's coming and what isn't:

- ❌ **Production vector stores in the headline labs** (Chroma, Pinecone, Qdrant, Weaviate). Covered in the survey snapshot but not exercised in any lab.
- ❌ **RAG evaluation frameworks as dependencies** (RAGAS, TruLens, DeepEval, Phoenix). Mentioned by name in Module 11 only as future production tools. Path 06 covers them in depth.
- ❌ **LangChain / LlamaIndex RAG abstractions**. Reserved for a future framework-bridge lab analogous to Lab 05.
- ❌ **Multi-agent coordination** (researcher + synthesizer, etc.). That's Path 03.
- ❌ **Late-interaction retrieval** (ColBERT, PLAID, ColPali). Mentioned in `reranking.md` and `sota-rag-patterns.md` as a production path; hands-on lab treatment deferred.
- ❌ **Conversational query rewriting** (multi-turn rewriting against chat history). Future framework-bridge or conversational-RAG batch.
- ❌ **Fine-tuning** (rewriters, embedders, rerankers). Out of scope. (The Self-RAG lab approximates reflection tokens with prompting rather than fine-tuning, and says so.)
- ❌ **Production observability** (LangSmith, LangFuse, W&B). Different problem from offline eval; Path 06.
- ❌ **A/B testing and drift detection.** Path 06.
- ❌ **Synthetic eval set generation via LLM.** Briefly discussed in Module 11; recommended against for the first 30-50 queries.

> 📚 **Now shipped:** the SOTA patterns (Self-RAG, CRAG, Graph RAG) have conceptual coverage in [`sota-rag-patterns.md`](../../concepts/rag/sota-rag-patterns.md) (Module 14), compact recipes in [`recipes/rag/`](../../recipes/rag/), **from-scratch labs** ([31](../../labs/31-corrective-rag-from-scratch/), [32](../../labs/32-self-rag-from-scratch/), [33](../../labs/33-graph-rag-from-scratch/)), a **head-to-head evaluation** ([Lab 34](../../labs/34-rag-pattern-head-to-head/)), and an **adaptive router** ([Lab 35](../../labs/35-adaptive-rag-router/), which also realizes Adaptive RAG). Long-context and multimodal RAG remain concept-and-recipe only for now.

Each item above is meaningful enough to deserve its own focused treatment rather than a paragraph buried elsewhere.

## What comes in later batches

Path 02 v1 is now complete. Future Path 02 batches:

- **Module 15: Framework bridge** — same Lab 06–09 agent in LangChain/LangGraph, analogous to Lab 05 for Foundations.
- **Module 16: Conversational RAG** — multi-turn retrieval with chat history, query rewriting against context.

If you've finished Path 02 v1 and want more *now*, the natural next moves are:

- **Solutions batch.** Polished reference implementations for Labs 01-09 with production-grade choices. The forward-references in every lab's "Solution discussion" section finally resolve.
- **Path 03 — Multi-Agent Systems.** The patterns from Labs 06 + 07 + 08 transfer cleanly. A research agent + a synthesizer is just two of the loops you've built.
- **Path 06 — Evaluation & Observability.** Lab 09 was the *primer*. Path 06 is the production-grade treatment with RAGAS, TruLens, DeepEval, drift detection, A/B testing, and observability tracing.

## A note on time

The 12–17 hour estimate covers reading the thirteen concept pages, skimming the two snapshots, doing the four labs, and taking the four quizzes. Most of it is the four labs. If you're already comfortable with sentence-transformers, numpy, and async LLM calls, each lab takes 60–90 minutes; if you're learning the libraries for the first time, expect closer to two hours each. The conceptual material adds up to about two hours total.

---

## References

Foundational sources cited across this path's pages:

### RAG foundations

- Lewis, P. et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. The paper that named the pattern.
- Karpukhin, V. et al. (2020). [*Dense Passage Retrieval for Open-Domain Question Answering*](https://arxiv.org/abs/2004.04906). EMNLP 2020. The dense retrieval mechanism Lewis et al. built on.
- Gao, Y. et al. (2024). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997). The standard 2024 survey covering naive, advanced, and modular RAG.
- Reimers, N., & Gurevych, I. (2019). [*Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*](https://arxiv.org/abs/1908.10084). EMNLP 2019. The paper introducing the sentence-transformers approach our default embedding model uses; Section 5.3 establishes the cross-encoder as a distinct architecture.

### Retrieval mechanics

- Robertson, S., & Zaragoza, H. (2009). [*The Probabilistic Relevance Framework: BM25 and Beyond*](https://www.staff.city.ac.uk/~sb317/papers/foundations_bm25_review.pdf). The definitive BM25 review.
- Cormack, G. V., Clarke, C. L. A., & Büttcher, S. (2009). [*Reciprocal rank fusion outperforms Condorcet and individual rank learning methods*](https://dl.acm.org/doi/10.1145/1571941.1572114). SIGIR 2009. The RRF paper; introduces the `k=60` constant Lab 07 uses.
- Carbonell, J., & Goldstein, J. (1998). [*The use of MMR, diversity-based reranking for reordering documents and producing summaries*](https://dl.acm.org/doi/10.1145/290941.291025). SIGIR 1998. The MMR paper.
- Nogueira, R., & Cho, K. (2019). [*Passage Re-ranking with BERT*](https://arxiv.org/abs/1901.04085). The lineage of the `cross-encoder/ms-marco-MiniLM-L-6-v2` reranker Lab 07 uses.
- Malkov, Y. A., & Yashunin, D. A. (2018). [*Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs*](https://arxiv.org/abs/1603.09320). The HNSW paper — the basis for most ANN indexes used in production vector stores.

### Quality interventions

- Anthropic (2024). [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval). Published Sep 19, 2024. The primary source for Module 8's headline technique, including the published prompt template and the 35-67% retrieval-failure-rate reduction benchmarks.
- Gao, L., Ma, X., Lin, J., & Callan, J. (2022). [*Precise Zero-Shot Dense Retrieval without Relevance Labels*](https://arxiv.org/abs/2212.10496). ACL 2023. The HyDE paper.
- Wang, L., Yang, N., & Wei, F. (2023). [*Query2doc: Query Expansion with Large Language Models*](https://arxiv.org/abs/2303.07678). EMNLP 2023. The canonical reference for LLM-driven query expansion / multi-query.
- Ma, X., Gong, Y., He, P., Zhao, H., & Duan, N. (2023). [*Query Rewriting for Retrieval-Augmented Large Language Models*](https://arxiv.org/abs/2305.14283). The Rewrite-Retrieve-Read formalization.
- Barnett, S., Kurniawan, S., Thudumu, S., Brannelly, Z., & Abdelrazek, M. (2024). [*Seven Failure Points When Engineering a Retrieval Augmented Generation System*](https://arxiv.org/abs/2401.05856). Complementary taxonomy to Module 8's failure-modes page.

### Evaluation

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). [*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/). Cambridge University Press. Free online. Chapter 8 is the textbook source for retrieval metric definitions.
- Järvelin, K., & Kekäläinen, J. (2002). [*Cumulated gain-based evaluation of IR techniques*](https://dl.acm.org/doi/10.1145/582415.582418). ACM TOIS. The original DCG / nDCG paper.
- Craswell, N. (2009). [*Mean Reciprocal Rank*](https://link.springer.com/referenceworkentry/10.1007/978-0-387-39940-9_488). Encyclopedia of Database Systems. The formal definition of MRR.
- Thakur, N. et al. (2021). [*BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*](https://arxiv.org/abs/2104.08663). NeurIPS 2021. The standard reference benchmark; establishes nDCG@10 + recall@100 as the cross-corpus retrieval-eval convention.
- Bajaj, P. et al. (2018). [*MS MARCO: A Human Generated MAchine Reading COmprehension Dataset*](https://arxiv.org/abs/1611.09268). The reference real-query benchmark whose MRR@10 became the default retrieval metric in much dense-retrieval literature.
- Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). The framework paper; introduces `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall` as a standardized metric set. RAGAS is mentioned in Module 11 as a future tool; not used in Path 02.
- Min, S. et al. (2023). [*FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation*](https://arxiv.org/abs/2305.14251). EMNLP 2023. The atomic-claim-decomposition approach to faithfulness checking.
- Zheng, L. et al. (2023). [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685). NeurIPS 2023 Datasets and Benchmarks Track. The canonical LLM-as-judge paper; documents the position, verbosity, and self-enhancement biases that every LLM-as-judge user needs to design around.
- Saad-Falcon, J., Khattab, O., Potts, C., & Zaharia, M. (2023). [*ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems*](https://arxiv.org/abs/2311.09476). NAACL 2024. Argues for synthetic-question generation with human-validated subsets; honest about the limits.
- Liu, Y. et al. (2024). [*G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*](https://arxiv.org/abs/2303.16634). EMNLP 2023. The standard LLM-as-judge protocol for text generation; chain-of-thought scoring template that many frameworks adopted.
