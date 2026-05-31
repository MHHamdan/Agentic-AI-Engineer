---
quiz_id: agentic-rag-sota-rag-patterns
title: "SOTA RAG patterns (2024-2026): matching patterns to failures"
source:
  - concepts/rag/sota-rag-patterns.md
  - concepts/evaluation/rag-evaluation-framework.md
  - recipes/rag/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "Your RAG system has no eval set yet, but the median query looks fine in spot checks. According to the decision guide, what is the correct next step before adopting any SOTA pattern?"
    options:
      A: "Adopt agentic RAG, since it is the most capable pattern."
      B: "Build the eval set first — you cannot tell which pattern you need without measured failures."
      C: "Add Graph RAG to be safe for future multi-hop queries."
      D: "Switch to a long-context model to avoid retrieval entirely."
    answer: B
    explanation: |
      The recurring theme of the SOTA patterns page is that every pattern above
      "hybrid + rerank" adds a control loop, and every control loop adds latency,
      cost, and a new failure surface. You adopt them in response to measured
      failures, not in anticipation. With no eval set, you cannot measure
      failures, so the eval set is step zero. Adopting a pattern blind (A, C, D)
      risks paying the cost of a loop that does not address your actual bottleneck.
    review:
      page: concepts/rag/sota-rag-patterns.md
      section: "Choosing a pattern"

  - id: q2
    difficulty: easy
    question: "Which SOTA pattern is described as among the cheapest to adopt because it adds a single classification step (a retrieval evaluator) rather than a full extra retrieval loop?"
    options:
      A: "Graph RAG."
      B: "Agentic RAG."
      C: "Corrective RAG (CRAG)."
      D: "Multimodal RAG."
    answer: C
    explanation: |
      CRAG inserts a lightweight retrieval evaluator between retrieval and
      generation that scores documents and routes correct / ambiguous / incorrect.
      It is one extra (cheap) model call, which is why it is often the most
      practical first step beyond static RAG. Graph RAG (A) has high index-time
      cost; agentic RAG (B) is the most expensive per query due to multiple model
      calls and retrievals; multimodal RAG (D) adds modality complexity and less
      mature tooling.
    review:
      page: concepts/rag/sota-rag-patterns.md
      section: "Pattern 2: Corrective RAG (CRAG)"

  - id: q3
    difficulty: medium
    question: "A workload has a wide spread of query difficulty: many trivial lookups and a few genuinely multi-hop questions. Applying multi-step retrieval to every query wastes budget; applying single-step to every query fails the hard ones. Which pattern targets exactly this?"
    options:
      A: "Adaptive RAG — a classifier routes by query complexity to the cheapest sufficient strategy."
      B: "Long-context RAG — stuff everything and let the model sort it out."
      C: "Self-RAG — emit reflection tokens on every token."
      D: "Hybrid search — fuse dense and sparse retrieval."
    answer: A
    explanation: |
      Adaptive RAG (Jeong et al., NAACL 2024) trains a classifier to assess query
      complexity and routes to no-retrieval, single-step, or multi-step accordingly,
      matching effort to difficulty. That is precisely the "wide difficulty spread"
      case. Long-context (B) does not address per-query routing. Self-RAG (C) is
      about on-demand retrieval and self-grading, not complexity routing. Hybrid
      search (D) is a retrieval-quality improvement, not a routing strategy.
    review:
      page: concepts/rag/sota-rag-patterns.md
      section: "Pattern 3: Adaptive RAG (query-complexity routing)"

  - id: q4
    difficulty: medium
    question: "Self-RAG introduces special tokens the model emits to make retrieval and quality decisions explicit. What do the IsREL, IsSUP, and IsUSE reflection tokens correspond to?"
    options:
      A: "Index size, embedding dimension, and chunk count."
      B: "Relevance of retrieved passages, support of the output by evidence, and usefulness of the output."
      C: "Three different reranker scores."
      D: "Retrieval latency, generation latency, and total cost."
    answer: B
    explanation: |
      In Self-RAG (Asai et al., ICLR 2024), the reflection tokens are IsREL
      (is the retrieved passage relevant?), IsSUP (is the generated output
      supported by the evidence?), and IsUSE (is the output useful?). They let
      the model decide when to retrieve and grade both passages and its own
      output. The other options describe unrelated system metrics.
    review:
      page: concepts/rag/sota-rag-patterns.md
      section: "Pattern 1: Self-RAG (self-reflective retrieval)"

  - id: q5
    difficulty: medium
    question: "For which query type is Graph RAG specifically strong, justifying its high index-time cost?"
    options:
      A: "Single-fact lookups over a small FAQ."
      B: "Global 'what are the main themes' questions and multi-hop questions that connect facts across documents."
      C: "Exact-term queries like product codes."
      D: "Low-latency autocomplete suggestions."
    answer: B
    explanation: |
      Graph RAG builds a knowledge graph, detects communities, and summarizes
      them, enabling map-reduce over community summaries for global questions and
      subgraph traversal for multi-hop questions — things flat vector RAG handles
      poorly. The cost is high index-time compute, justified only for corpora with
      rich entity structure and global/multi-hop queries. Single-fact lookup (A)
      and exact-term queries (C, better served by BM25/hybrid) do not justify the
      cost; autocomplete (D) needs low latency, the opposite of graph traversal.
    review:
      page: concepts/rag/sota-rag-patterns.md
      section: "Pattern 5: Graph RAG"

  - id: q6
    difficulty: hard
    question: "A teammate proposes switching to a 1M-token context model and dropping fine-grained retrieval, expecting strictly better answers because 'more context cannot hurt.' What is the most accurate caution from the long-context RAG material?"
    options:
      A: "Long contexts are always better; the teammate is correct."
      B: "More context costs more per call and exhibits the lost-in-the-middle effect — recall degrades for content in the middle of a long context."
      C: "Long-context models cannot do retrieval at all."
      D: "Context length has no measurable effect on cost or quality."
    answer: B
    explanation: |
      The lost-in-the-middle finding (Liu et al., TACL 2024) shows recall is
      weaker for content placed in the middle of a long context, so more context
      is neither free nor a reliable improvement. Long-context RAG is a real pattern,
      but the useful form is usually a hybrid (retrieve more coarsely, still bound
      what you send), not "stuff everything." A and D are wrong; C overstates —
      long-context and retrieval compose fine.
    review:
      page: concepts/rag/sota-rag-patterns.md
      section: "Pattern 6: Long-context RAG"

  - id: q7
    difficulty: hard
    question: "Multi-hop questions are failing: the evidence to answer is spread across several documents and a single retrieval never surfaces all of it. Which pattern is the targeted fix, and what is its main cost?"
    options:
      A: "Agentic RAG — iterative retrieve-reason-retrieve; main cost is multiple model calls and retrievals per query, plus harder reproducibility and debugging."
      B: "Reranking — reorder the single retrieval; main cost is a cross-encoder call."
      C: "Metadata filtering — restrict the corpus; main cost is maintaining metadata."
      D: "Chunk-size tuning — adjust overlap; main cost is re-indexing."
    answer: A
    explanation: |
      Multi-hop questions where the first retrieval reveals what to retrieve next
      are the canonical case for agentic RAG, where retrieval is a tool the agent
      can call repeatedly while reasoning. Its cost is the highest of the patterns:
      multiple model calls and retrievals, plus reproducibility and debugging
      difficulty, and the need for a max-iterations guard. Reranking (B) reorders a
      single retrieval and cannot gather new evidence; filtering (C) and chunk
      tuning (D) do not address the multi-step nature.
    review:
      page: concepts/rag/sota-rag-patterns.md
      section: "Pattern 4: Agentic RAG"

  - id: q8
    difficulty: medium
    question: "The page marks one pattern's tooling and benchmarks as still developing, advising you to verify model recommendations against current benchmarks and budget for manual validation. Which pattern is flagged this way?"
    options:
      A: "Hybrid search."
      B: "Corrective RAG."
      C: "Multimodal RAG (retrieval over images, tables, charts, audio)."
      D: "Reranking."
    answer: C
    explanation: |
      Multimodal RAG is explicitly labeled emerging: multimodal embedding models
      and benchmarks are developing quickly, production patterns are less settled
      than text RAG, and evaluation tooling is less mature — so the page advises
      treating specific model recommendations as fast-moving and budgeting for
      manual validation. This reflects the repo rule to mark areas as emerging or
      requiring further validation rather than overstating maturity. Hybrid search
      (A), CRAG (B), and reranking (D) are well-established.
    review:
      page: concepts/rag/sota-rag-patterns.md
      section: "Pattern 7: Multimodal RAG"
---

# SOTA RAG patterns quiz (2024-2026)

Eight questions on matching modern RAG patterns to the failures they fix, the cost each control loop adds, and the citations behind them. Pass mark: 6 of 8.

This quiz assumes you have read [`concepts/rag/sota-rag-patterns.md`](../../concepts/rag/sota-rag-patterns.md). It is Module 14's self-assessment in [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/). For the evaluation side, see the [RAG evaluation quiz](./rag-evaluation.md); for the metric math, see the [retrieval and ranking metrics quiz](../math-foundations/retrieval-ranking-metrics.md).

> The single most important idea this quiz tests: **adopt patterns in response to measured failures, not in anticipation.** Every control loop beyond hybrid + rerank adds latency, cost, and a new way to fail.
