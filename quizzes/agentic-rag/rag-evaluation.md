---
quiz_id: agentic-rag-rag-evaluation
title: "RAG evaluation: metrics, eval sets, and answer quality"
source:
  - concepts/evaluation/what-is-rag-evaluation.md
  - concepts/evaluation/eval-set-construction.md
  - concepts/evaluation/retrieval-metrics.md
  - concepts/evaluation/answer-quality-metrics.md
  - labs/09-evaluating-agentic-rag/
length_minutes: 12
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "A user complains the system gave a confidently wrong answer. The chunks containing the right answer were retrieved at rank 1. The LLM ignored them and made something up. Which property of the answer would you measure to catch this in evaluation?"
    options:
      A: "Recall@10."
      B: "Faithfulness (or groundedness)."
      C: "Citation count."
      D: "Mean Reciprocal Rank."
    answer: B
    explanation: |
      Retrieval succeeded — the right chunks were at rank 1 — so retrieval
      metrics like recall and MRR show no problem. The failure is on the
      generation side: the LLM produced claims the chunks don't support.
      That's what faithfulness/groundedness measures. The retrieval/generation
      split is the foundational distinction in RAG evaluation: wrong final
      answers can come from either half, and they need different metrics to
      diagnose. Citation count (C) is a shallow proxy — citing nothing or
      citing a lot says nothing about whether claims are supported.
    review:
      page: concepts/evaluation/what-is-rag-evaluation.md
      section: "The two-part question"

  - id: q2
    difficulty: easy
    question: "You're considering whether to build a 30-question hand-curated eval set or generate 1,000 synthetic questions with an LLM. Which is most accurate?"
    options:
      A: "The synthetic set is strictly better — more data is always more signal."
      B: "The hand-curated set tends to surface failure modes the synthetic set misses, because synthetic queries inherit the generator's vocabulary and structural biases."
      C: "They're equivalent for early-stage RAG work; pick whichever you can build faster."
      D: "The synthetic set is cheaper to maintain, which makes it the right default."
    answer: B
    explanation: |
      Synthetic queries reflect the *generator's* assumptions — they share
      vocabulary with the document, follow predictable forms ("What is X?"),
      rarely include compound or referential phrasings, and almost never
      include typos or fragments. A 30-question hand-curated set deliberately
      targeting failure modes is more diagnostic than 1,000 synthetic queries
      that all look like easy lexical matches. The "more data is more signal"
      intuition fails here because biased samples in volume are still biased.
      Most production teams converge on a hybrid (hand-curate the seed, expand
      synthetically later); Path 02 stops at the seed-set stage deliberately.
    review:
      page: concepts/evaluation/eval-set-construction.md
      section: "Why hand-curation beats synthetic generation"

  - id: q3
    difficulty: medium
    question: "A retrieval pipeline has overall recall@10 of 0.78. Sliced by category you see lexical recall = 0.95 and referential recall = 0.40. What's the right conclusion?"
    options:
      A: "The aggregate is what matters — 0.78 is the system's quality."
      B: "The aggregate is misleading; the system has a referential-query weakness that interventions should target."
      C: "Recall@10 isn't the right metric here; switch to MRR."
      D: "The eval set is broken since recall varies so much across categories."
    answer: B
    explanation: |
      The aggregate hides where the system is weak. A mean of 0.78 tells you
      nothing about whether to invest in better embeddings, hybrid retrieval,
      contextual augmentation, or query rewriting — but the per-category slice
      points directly at the referential failure mode. This is the single most
      important habit when working with retrieval metrics: read the
      per-category table, not the headline number. Variance across categories
      is exactly what a well-constructed eval set is *supposed* to show — it
      means the categories are doing diagnostic work, not that the set is
      broken. Switching metrics (C) doesn't help; the problem is the slicing
      discipline, not the metric.
    review:
      page: concepts/evaluation/retrieval-metrics.md
      section: "The discipline of looking at the distribution"

  - id: q4
    difficulty: medium
    question: "Which statement about MRR (Mean Reciprocal Rank) is correct?"
    options:
      A: "MRR measures how many relevant chunks were retrieved in the top-k."
      B: "MRR is the reciprocal of the rank of the *first* relevant chunk, averaged across queries — so a chunk at rank 1 contributes 1.0, rank 2 contributes 0.5, rank 5 contributes 0.2."
      C: "MRR penalizes pipelines that surface multiple relevant chunks below the first."
      D: "MRR is the right metric when the user reads the entire top-k as a batch."
    answer: B
    explanation: |
      For one query, reciprocal rank is `1 / rank_of_first_relevant_chunk`,
      or 0 if no relevant chunk made the top-k. MRR is the mean of those
      reciprocal ranks across queries. (A) confuses MRR with recall. (C) is
      wrong — MRR doesn't penalize *additional* relevant chunks below the
      first; it just ignores them. (D) is the opposite of what's true — MRR
      aligns with an agent that stops at the first useful chunk (Lab 06's
      pattern); it's a less natural fit for batch-consumption use cases
      where every chunk in the top-k gets read.
    review:
      page: concepts/evaluation/retrieval-metrics.md
      section: "MRR — Mean Reciprocal Rank"

  - id: q5
    difficulty: medium
    question: "The Zheng et al. 2023 LLM-as-judge paper (NeurIPS 2023 Datasets and Benchmarks) documents three biases. Which one says the LLM judge tends to prefer the answer it sees *first* when comparing two side-by-side?"
    options:
      A: "Self-enhancement bias."
      B: "Verbosity bias."
      C: "Position bias."
      D: "Anchoring bias."
    answer: C
    explanation: |
      Zheng et al. 2023 documents three LLM-as-judge biases: **position bias**
      (preference for whichever option is presented first), **verbosity bias**
      (preference for longer, more detailed answers even when they contain
      errors), and **self-enhancement bias** (preference for answers from the
      same model family as the judge). The standard mitigation for position
      bias is to present each pair in both orders and average the scores.
      Anchoring (D) is a real human-cognition bias but not one of the three
      this paper names. The paper's headline finding — >80% agreement with
      human raters — comes paired with these documented biases that you need
      to design around.
    review:
      page: concepts/evaluation/answer-quality-metrics.md
      section: "LLM-as-judge biases (Zheng et al. 2023)"

  - id: q6
    difficulty: medium
    question: "Which best describes the difference between *correctness* and *groundedness* in RAG evaluation?"
    options:
      A: "Correctness measures whether the chunks are correct; groundedness measures whether the answer is correct."
      B: "Correctness is whether the answer is factually true (measured against external truth); groundedness is whether the answer follows from the retrieved chunks (measured against the chunks)."
      C: "They're synonymous in RAG; the terms are used interchangeably across the literature."
      D: "Correctness applies to retrieval; groundedness applies to generation."
    answer: B
    explanation: |
      These are genuinely different properties. An answer can be correct but
      ungrounded (the model went outside the chunks to get the right answer —
      lucky, not reliable). An answer can be grounded but incorrect (the
      chunks were wrong; the model faithfully relayed them — that's a corpus
      problem, not a RAG problem). For RAG systems, groundedness is what you
      actually want to measure, because the entire premise of RAG is "ground
      the answer in retrieved chunks." If the answer isn't grounded, you
      don't have a RAG system — you have an LLM doing what it would do
      anyway. (A) inverts the relationship; (D) miscategorizes both metrics.
    review:
      page: concepts/evaluation/what-is-rag-evaluation.md
      section: "Correctness vs. groundedness — a critical distinction"

  - id: q7
    difficulty: hard
    question: "You're building an eval set. The strict approach annotates `expected_chunks: [\"02-tool-design.md:3\"]`. The loose approach annotates `expected_doc: \"02-tool-design.md\"`. What's the main tradeoff?"
    options:
      A: "Strict annotations produce cleaner metrics but break when the chunker changes; loose annotations are robust to chunker changes but lose chunk-specific information."
      B: "Loose annotations are strictly worse since they over-count irrelevant chunks from the same document."
      C: "Strict annotations are only correct for paraphrase queries; loose annotations are only correct for lexical queries."
      D: "Both produce identical metrics; the choice is purely stylistic."
    answer: A
    explanation: |
      Strict `expected_chunks` annotations let you measure exactly which chunk
      was retrieved at what rank — useful when the chunker is pinned. But the
      moment you change `TARGET_TOKENS`, the overlap, or the splitting logic,
      every chunk ID shifts and every annotation needs re-validation. Loose
      `expected_doc` annotations stay valid as the chunker evolves (a chunk
      is from the right doc or it isn't) but can't distinguish "the system
      found the exact paragraph" from "the system found some other chunk
      from the same document." Lab 09 ships loose annotations for this
      reason; production teams that have pinned their chunker often switch
      to strict once infrastructure is stable.
    review:
      page: concepts/evaluation/eval-set-construction.md
      section: "Annotating expected chunks"

  - id: q8
    difficulty: hard
    question: "When should you reach for rule-based answer-quality checks vs LLM-as-judge?"
    options:
      A: "LLM-as-judge is strictly better; rule-based checks are obsolete."
      B: "Rule-based checks are cheap, deterministic, and good for CI; LLM-as-judge handles substance-of-claim checks rule-based approaches can't reach (paraphrased answers, semantic implication). The pragmatic stance is to combine them."
      C: "Rule-based checks should only be used for refusal quality; everything else needs LLM-as-judge."
      D: "Both produce identical scores when configured correctly."
    answer: B
    explanation: |
      The pragmatic stance most teams converge on: rule-based for everything
      you can (string overlap, citation presence, refusal-language detection)
      because they're cheap, deterministic, and CI-friendly. LLM-as-judge is
      reserved for the cases where rules fail — paraphrased answers that
      don't share vocabulary with the chunks, substance-of-claim checks for
      compound questions, refusal detection where the rule misses subtle
      hedging. Lab 09 demonstrates the pattern: rule-based groundedness on
      every query, LLM-as-judge on a small subset. LLM-as-judge has its own
      failure modes (the Zheng et al. biases) that mean you shouldn't treat
      its scores as ground truth either — both are noisy signals that
      complement each other.
    review:
      page: concepts/evaluation/answer-quality-metrics.md
      section: "Rule-based vs LLM-as-judge"
---

# 🧠 Quiz: RAG evaluation

> 🟡 Intermediate · ⏱ ~12 min · 8 questions · Pass at 6/8

This quiz checks understanding of the four RAG-evaluation concept pages and the patterns from Lab 09. Read all four pages and complete at least steps 1-5 of the lab before attempting.

**Format.** Each question shows four options. Click the `<details>` block to reveal the answer and full explanation. Aim for 6/8 to feel solid; below that, the linked review section is the place to revisit.

---

## Q1 — Diagnosing the wrong-but-confident answer

A user complains the system gave a confidently wrong answer. The chunks containing the right answer were retrieved at rank 1. The LLM ignored them and made something up. Which property of the answer would you measure to catch this in evaluation?

A. Recall@10.  
B. Faithfulness (or groundedness).  
C. Citation count.  
D. Mean Reciprocal Rank.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

Retrieval succeeded — the right chunks were at rank 1 — so retrieval metrics like recall and MRR show no problem. The failure is on the generation side: the LLM produced claims the chunks don't support. That's what faithfulness/groundedness measures.

The retrieval/generation split is the foundational distinction in RAG evaluation: wrong final answers can come from either half, and they need different metrics to diagnose. Citation count (C) is a shallow proxy — citing nothing or citing a lot says nothing about whether claims are supported.

Review: [`concepts/evaluation/what-is-rag-evaluation.md` § The two-part question](../../concepts/evaluation/what-is-rag-evaluation.md#the-two-part-question)
</details>

---

## Q2 — Hand-curated vs synthetic eval sets

You're considering whether to build a 30-question hand-curated eval set or generate 1,000 synthetic questions with an LLM. Which is most accurate?

A. The synthetic set is strictly better — more data is always more signal.  
B. The hand-curated set tends to surface failure modes the synthetic set misses, because synthetic queries inherit the generator's vocabulary and structural biases.  
C. They're equivalent for early-stage RAG work; pick whichever you can build faster.  
D. The synthetic set is cheaper to maintain, which makes it the right default.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

Synthetic queries reflect the *generator's* assumptions — they share vocabulary with the document, follow predictable forms ("What is X?"), rarely include compound or referential phrasings, and almost never include typos or fragments. A 30-question hand-curated set deliberately targeting failure modes is more diagnostic than 1,000 synthetic queries that all look like easy lexical matches.

The "more data is more signal" intuition fails here because biased samples in volume are still biased. Most production teams converge on a hybrid (hand-curate the seed, expand synthetically later); Path 02 stops at the seed-set stage deliberately.

Review: [`concepts/evaluation/eval-set-construction.md` § Why hand-curation beats synthetic generation](../../concepts/evaluation/eval-set-construction.md#why-hand-curation-beats-synthetic-generation)
</details>

---

## Q3 — Reading per-category metrics

A retrieval pipeline has overall recall@10 of 0.78. Sliced by category you see lexical recall = 0.95 and referential recall = 0.40. What's the right conclusion?

A. The aggregate is what matters — 0.78 is the system's quality.  
B. The aggregate is misleading; the system has a referential-query weakness that interventions should target.  
C. Recall@10 isn't the right metric here; switch to MRR.  
D. The eval set is broken since recall varies so much across categories.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

The aggregate hides where the system is weak. A mean of 0.78 tells you nothing about whether to invest in better embeddings, hybrid retrieval, contextual augmentation, or query rewriting — but the per-category slice points directly at the referential failure mode. This is the single most important habit when working with retrieval metrics: read the per-category table, not the headline number.

Variance across categories is exactly what a well-constructed eval set is *supposed* to show — it means the categories are doing diagnostic work, not that the set is broken. Switching metrics (C) doesn't help; the problem is the slicing discipline, not the metric.

Review: [`concepts/evaluation/retrieval-metrics.md` § The discipline of looking at the distribution](../../concepts/evaluation/retrieval-metrics.md#the-discipline-of-looking-at-the-distribution)
</details>

---

## Q4 — MRR mechanics

Which statement about MRR (Mean Reciprocal Rank) is correct?

A. MRR measures how many relevant chunks were retrieved in the top-k.  
B. MRR is the reciprocal of the rank of the *first* relevant chunk, averaged across queries — so a chunk at rank 1 contributes 1.0, rank 2 contributes 0.5, rank 5 contributes 0.2.  
C. MRR penalizes pipelines that surface multiple relevant chunks below the first.  
D. MRR is the right metric when the user reads the entire top-k as a batch.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

For one query, reciprocal rank is `1 / rank_of_first_relevant_chunk`, or 0 if no relevant chunk made the top-k. MRR is the mean of those reciprocal ranks across queries.

(A) confuses MRR with recall. (C) is wrong — MRR doesn't penalize *additional* relevant chunks below the first; it just ignores them. (D) is the opposite of what's true — MRR aligns with an agent that stops at the first useful chunk (Lab 06's pattern); it's a less natural fit for batch-consumption use cases where every chunk in the top-k gets read.

Review: [`concepts/evaluation/retrieval-metrics.md` § MRR — Mean Reciprocal Rank](../../concepts/evaluation/retrieval-metrics.md#mrr-mean-reciprocal-rank)
</details>

---

## Q5 — The LLM-as-judge biases

The Zheng et al. 2023 LLM-as-judge paper (NeurIPS 2023 Datasets and Benchmarks) documents three biases. Which one says the LLM judge tends to prefer the answer it sees *first* when comparing two side-by-side?

A. Self-enhancement bias.  
B. Verbosity bias.  
C. Position bias.  
D. Anchoring bias.

<details>
<summary>Answer & explanation</summary>

**Answer: C.**

Zheng et al. 2023 documents three LLM-as-judge biases: **position bias** (preference for whichever option is presented first), **verbosity bias** (preference for longer, more detailed answers even when they contain errors), and **self-enhancement bias** (preference for answers from the same model family as the judge).

The standard mitigation for position bias is to present each pair in both orders and average the scores. Anchoring (D) is a real human-cognition bias but not one of the three this paper names. The paper's headline finding — >80% agreement with human raters — comes paired with these documented biases that you need to design around.

Review: [`concepts/evaluation/answer-quality-metrics.md` § LLM-as-judge biases (Zheng et al. 2023)](../../concepts/evaluation/answer-quality-metrics.md#llm-as-judge-biases-zheng-et-al-2023)
</details>

---

## Q6 — Correctness vs groundedness

Which best describes the difference between *correctness* and *groundedness* in RAG evaluation?

A. Correctness measures whether the chunks are correct; groundedness measures whether the answer is correct.  
B. Correctness is whether the answer is factually true (measured against external truth); groundedness is whether the answer follows from the retrieved chunks (measured against the chunks).  
C. They're synonymous in RAG; the terms are used interchangeably across the literature.  
D. Correctness applies to retrieval; groundedness applies to generation.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

These are genuinely different properties. An answer can be correct but ungrounded (the model went outside the chunks to get the right answer — lucky, not reliable). An answer can be grounded but incorrect (the chunks were wrong; the model faithfully relayed them — that's a corpus problem, not a RAG problem).

For RAG systems, groundedness is what you actually want to measure, because the entire premise of RAG is "ground the answer in retrieved chunks." If the answer isn't grounded, you don't have a RAG system — you have an LLM doing what it would do anyway. (A) inverts the relationship; (D) miscategorizes both metrics.

Review: [`concepts/evaluation/what-is-rag-evaluation.md` § Correctness vs. groundedness](../../concepts/evaluation/what-is-rag-evaluation.md#correctness-vs-groundedness-a-critical-distinction)
</details>

---

## Q7 — Strict vs loose chunk annotation

You're building an eval set. The strict approach annotates `expected_chunks: ["02-tool-design.md:3"]`. The loose approach annotates `expected_doc: "02-tool-design.md"`. What's the main tradeoff?

A. Strict annotations produce cleaner metrics but break when the chunker changes; loose annotations are robust to chunker changes but lose chunk-specific information.  
B. Loose annotations are strictly worse since they over-count irrelevant chunks from the same document.  
C. Strict annotations are only correct for paraphrase queries; loose annotations are only correct for lexical queries.  
D. Both produce identical metrics; the choice is purely stylistic.

<details>
<summary>Answer & explanation</summary>

**Answer: A.**

Strict `expected_chunks` annotations let you measure exactly which chunk was retrieved at what rank — useful when the chunker is pinned. But the moment you change `TARGET_TOKENS`, the overlap, or the splitting logic, every chunk ID shifts and every annotation needs re-validation.

Loose `expected_doc` annotations stay valid as the chunker evolves (a chunk is from the right doc or it isn't) but can't distinguish "the system found the exact paragraph" from "the system found some other chunk from the same document." Lab 09 ships loose annotations for this reason; production teams that have pinned their chunker often switch to strict once infrastructure is stable.

Review: [`concepts/evaluation/eval-set-construction.md` § Annotating expected chunks](../../concepts/evaluation/eval-set-construction.md#annotating-expected-chunks)
</details>

---

## Q8 — Rule-based vs LLM-as-judge

When should you reach for rule-based answer-quality checks vs LLM-as-judge?

A. LLM-as-judge is strictly better; rule-based checks are obsolete.  
B. Rule-based checks are cheap, deterministic, and good for CI; LLM-as-judge handles substance-of-claim checks rule-based approaches can't reach (paraphrased answers, semantic implication). The pragmatic stance is to combine them.  
C. Rule-based checks should only be used for refusal quality; everything else needs LLM-as-judge.  
D. Both produce identical scores when configured correctly.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

The pragmatic stance most teams converge on: rule-based for everything you can (string overlap, citation presence, refusal-language detection) because they're cheap, deterministic, and CI-friendly. LLM-as-judge is reserved for the cases where rules fail — paraphrased answers that don't share vocabulary with the chunks, substance-of-claim checks for compound questions, refusal detection where the rule misses subtle hedging.

Lab 09 demonstrates the pattern: rule-based groundedness on every query, LLM-as-judge on a small subset. LLM-as-judge has its own failure modes (the Zheng et al. biases) that mean you shouldn't treat its scores as ground truth either — both are noisy signals that complement each other.

Review: [`concepts/evaluation/answer-quality-metrics.md` § Rule-based vs LLM-as-judge](../../concepts/evaluation/answer-quality-metrics.md#rule-based-vs-llm-as-judge)
</details>

---

## What's next

You've finished the RAG-evaluation primer. Path 02 v1 is now complete — you can build retrieval (Labs 06-08), diagnose failures ([failure modes](../../concepts/rag/retrieval-failure-modes.md)), and measure interventions ([Lab 09](../../labs/09-evaluating-agentic-rag/)).

Next moves:

- A focused **solutions batch** that ships polished reference implementations for Labs 01-09.
- **Path 03 — Multi-Agent Systems.** The patterns from Labs 06-08 transfer cleanly.
- **Path 06 — Evaluation & Observability.** The production-grade version of Lab 09 with RAGAS, TruLens, DeepEval, drift detection, A/B testing.
