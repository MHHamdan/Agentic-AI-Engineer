---
quiz_id: math-foundations-retrieval-ranking-metrics
title: "Retrieval and ranking metrics: precision@k, recall@k, MRR, MAP, NDCG"
source:
  - math-foundations/14-retrieval-ranking-metrics.md
  - concepts/evaluation/retrieval-metrics.md
  - concepts/evaluation/rag-evaluation-framework.md
length_minutes: 12
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "A retriever returns 5 documents in rank order with relevance labels [0, 1, 0, 1, 0] (1 = relevant). What is Precision@3?"
    options:
      A: "1/2"
      B: "1/3"
      C: "2/5"
      D: "2/2"
    answer: B
    explanation: |
      Precision@k is the fraction of the top-k that are relevant. The top-3 are
      [0, 1, 0], which contains 1 relevant document out of 3, so P@3 = 1/3 ≈ 0.333.
      Option A (1/2) would be P@2; C (2/5) is P@5; D is not a precision value here.
    review:
      page: math-foundations/14-retrieval-ranking-metrics.md
      section: "The equations"

  - id: q2
    difficulty: easy
    question: "For the same ranking [0, 1, 0, 1, 0], if the corpus contains exactly 2 relevant documents total, what is Recall@5?"
    options:
      A: "2/5"
      B: "1/2"
      C: "2/2 = 1.0"
      D: "1/5"
    answer: C
    explanation: |
      Recall@k is the fraction of all relevant documents that appear in the top-k.
      The top-5 contains both relevant documents (at ranks 2 and 4), and there are
      2 relevant documents total, so R@5 = 2/2 = 1.0. The common error is dividing
      by k (giving 2/5, option A) instead of by the total number of relevant docs.
    review:
      page: math-foundations/14-retrieval-ranking-metrics.md
      section: "Common mistakes"

  - id: q3
    difficulty: easy
    question: "What does Mean Reciprocal Rank (MRR) primarily reward?"
    options:
      A: "Retrieving every relevant document, regardless of order."
      B: "Ranking the first relevant document as high as possible."
      C: "Minimizing the number of documents retrieved."
      D: "Maximizing graded relevance scores across all ranks."
    answer: B
    explanation: |
      MRR averages 1/rank of the *first* relevant document across queries. It cares
      only about how high the first relevant result lands, which makes it the right
      metric when there is effectively one right answer (navigational or single-fact
      lookup). It ignores later relevant documents (so A is wrong), is not about
      count (C), and uses binary relevance, not graded (D — that is NDCG).
    review:
      page: math-foundations/14-retrieval-ranking-metrics.md
      section: "How to read these equations"

  - id: q4
    difficulty: medium
    question: "For the ranking [0, 1, 0, 1, 0] with 2 relevant documents, what is the Average Precision (AP)?"
    options:
      A: "0.500"
      B: "0.333"
      C: "1.000"
      D: "0.250"
    answer: A
    explanation: |
      AP averages the precision computed at each rank where a relevant document
      appears, divided by the total number of relevant docs. Relevant hits are at
      rank 2 (precision@2 = 1/2) and rank 4 (precision@4 = 2/4 = 1/2). AP =
      (1/2 + 1/2) / 2 = 0.500. This is verified by the worked code example on the
      page.
    review:
      page: math-foundations/14-retrieval-ranking-metrics.md
      section: "Code example"

  - id: q5
    difficulty: medium
    question: "Why is NDCG the headline metric for retrieval benchmarks like BEIR, rather than precision@k or recall@k?"
    options:
      A: "It is faster to compute than precision or recall."
      B: "It supports graded relevance and discounts gains by rank, and normalizing makes it comparable across queries with different numbers of relevant docs."
      C: "It does not require any relevance labels."
      D: "It only works for binary relevance, which is simpler."
    answer: B
    explanation: |
      NDCG handles graded relevance (a document can be perfectly, somewhat, or not
      relevant), applies a logarithmic rank discount so higher-ranked relevant
      results count more, and normalizes by the ideal DCG so scores fall in [0, 1]
      and are comparable across queries. That versatility is why BEIR reports
      NDCG@10. It is not faster (A), still needs labels (C), and is the metric that
      supports graded — not only binary — relevance (D is backwards).
    review:
      page: math-foundations/14-retrieval-ranking-metrics.md
      section: "How to read these equations"

  - id: q6
    difficulty: medium
    question: "A change to your retriever improves recall@10 but lowers MRR. What most likely happened?"
    options:
      A: "The change retrieved more relevant documents but pushed the first relevant result further down the ranking."
      B: "The change is strictly better and the metrics are contradictory."
      C: "Recall and MRR always move together, so this is a measurement bug."
      D: "The change reduced the total number of relevant documents in the corpus."
    answer: A
    explanation: |
      Recall@10 rising means more relevant docs are now in the top-10; MRR falling
      means the *first* relevant doc moved to a worse rank. Both can happen at once:
      you found more relevant material overall but degraded top-rank ordering. This
      is exactly the silent regression that rank-aware metrics catch and rank-unaware
      ones miss. The metrics are not contradictory (B) and do not always move
      together (C); the corpus relevant-doc count is fixed by the labels (D).
    review:
      page: math-foundations/14-retrieval-ranking-metrics.md
      section: "Where this appears in agentic systems"

  - id: q7
    difficulty: hard
    question: "How do the RAG-specific 'context precision' and 'context recall' relate to classical IR precision and recall?"
    options:
      A: "They are unrelated metrics invented for RAG with different math."
      B: "They are the same precision/recall ideas, computed per-query over the retrieved context the generator actually sees."
      C: "Context precision is recall renamed, and context recall is precision renamed."
      D: "They replace precision and recall because the classical metrics do not apply to RAG."
    answer: B
    explanation: |
      Context precision is precision computed over the retrieved context chunks for
      a query (signal-to-noise for the generator); context recall is recall of the
      information needed to answer (retrieval-gap detection). The underlying math is
      the classical IR math; the framing is per-query over the generator's actual
      context window. Knowing this means you are not learning two separate things.
      They are not unrelated (A), not swapped names (C), and do not replace the
      classical metrics (D).
    review:
      page: math-foundations/14-retrieval-ranking-metrics.md
      section: "Mathematical intuition"

  - id: q8
    difficulty: hard
    question: "When evaluating a reranker (which reorders an already-retrieved candidate set), which metric pattern indicates it is doing its job correctly?"
    options:
      A: "Recall@k rises sharply while NDCG and MRR stay flat."
      B: "NDCG and MRR improve (better ordering) while recall@k stays roughly flat (same candidates, reordered)."
      C: "All metrics including recall@k must increase, or the reranker failed."
      D: "Latency decreases while all quality metrics increase."
    answer: B
    explanation: |
      A reranker reorders candidates that retrieval already surfaced; it does not
      fetch new documents. So it should improve rank-aware metrics (NDCG, MRR) by
      putting relevant results higher, while recall@k stays roughly flat because the
      candidate set is unchanged. Expecting recall to rise (A, C) misunderstands what
      a reranker does — recall is set by the first-stage retriever. Rerankers
      typically add latency, not reduce it (D).
    review:
      page: math-foundations/14-retrieval-ranking-metrics.md
      section: "Where this appears in agentic systems"
---

# Retrieval and ranking metrics quiz

Eight questions on the IR metrics behind retrieval evaluation: precision@k, recall@k, MRR, MAP, and NDCG, plus the RAG-specific context precision/recall framing. Pass mark: 6 of 8.

This quiz assumes you have read [`math-foundations/14-retrieval-ranking-metrics.md`](../../math-foundations/14-retrieval-ranking-metrics.md). Several questions use the same worked example as the page (`rels = [0, 1, 0, 1, 0]`), so you can check your arithmetic against the verified code output there.

> The recurring trap this quiz tests: **rank-unaware metrics (precision@k, recall@k) hide ranking failures that rank-aware metrics (MRR, MAP, NDCG) catch.** For RAG, rank matters because of context-window position effects (lost in the middle).
