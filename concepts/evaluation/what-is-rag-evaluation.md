# What is RAG evaluation?

> 🟢 Stable · ⏱ ~10 min read · 🏷 rag, evaluation, fundamentals

## TL;DR

You built a RAG system. Some queries work, some don't. How do you know if your latest change helped, hurt, or did nothing?

**RAG evaluation** is the discipline of measuring system quality with enough rigor to decide. It separates two questions that look identical from outside but require completely different measurement tools:

- **Retrieval evaluation:** did we find the right chunks?
- **Generation evaluation:** given chunks, did we produce the right answer?

The two are connected — you can't synthesize a right answer from wrong chunks — but they fail differently, get measured differently, and get fixed differently. Conflating them is the most common mistake in production RAG.

This page is the orientation. The next three pages cover [eval set construction](./eval-set-construction.md), [retrieval metrics](./retrieval-metrics.md), and [answer quality metrics](./answer-quality-metrics.md) in depth. [Lab 09](../../labs/09-evaluating-agentic-rag/) implements a from-scratch harness over Labs 06-08.

---

## What "evaluation" actually means here

Three different things hide under the word "evaluation" in RAG. Useful to separate them upfront because they need different tools:

1. **Offline evaluation** — you have a fixed set of test queries with expected answers; you run them through your system and compute metrics. Done in a notebook, in CI, or both. This is the topic of Path 02. **This is the rest of this page.**
2. **Online evaluation** — you observe real production traffic. You sample requests, score them, and watch trends. Done with observability tooling. Production concern; covered in Path 06.
3. **A/B testing** — you run two versions of your system against real traffic and compare metrics. Statistical concern; also Path 06.

Path 02 stops at (1). You can't responsibly do (2) or (3) without first doing (1) — without a fixed eval set, you have no idea what "better" means against real traffic.

## The two-part question

A RAG pipeline has two failure points that look identical from outside:

```text
   query
     │
     ▼
   ┌────────────────────┐
   │   RETRIEVAL        │  ← can fail here (wrong chunks)
   │   chunks selected  │
   └────────────────────┘
     │
     ▼
   ┌────────────────────┐
   │   GENERATION       │  ← can fail here (wrong synthesis)
   │   answer produced  │
   └────────────────────┘
     │
     ▼
   answer to user
```

A wrong final answer can come from either. From the outside they're indistinguishable — the user just sees a bad answer. From inside the system they're entirely different problems with different fixes.

**Retrieval went wrong** if:
- The chunks containing the answer weren't in the top-k.
- The chunks were in the top-k but the relevant one was buried.
- The chunks were from the wrong document.
- No chunks were relevant and the system tried to answer anyway.

**Generation went wrong** if:
- The right chunks were retrieved but the LLM ignored them.
- The right chunks were retrieved but the LLM contradicted them.
- The right chunks were retrieved but the LLM hallucinated additional facts not in the chunks.
- The right chunks were retrieved but the LLM cited the wrong ones.

These have separate metric families. Mixing them is the trap [failure mode 7](../rag/retrieval-failure-modes.md#failure-mode-7-the-agent-retrieves-something-but-synthesizes-the-wrong-answer) warns about — engineers throw more retrieval engineering at problems that are actually generation problems, and vice versa.

## Retrieval metrics

The retrieval question is "did the right chunks make it into the top-k?" — fundamentally a *ranking* question, well-studied in classical information retrieval.

The main metrics ([covered in depth on the next page](./retrieval-metrics.md)):

- **Recall@k** — what fraction of relevant chunks made the top-k?
- **Precision@k** — what fraction of the top-k chunks are relevant?
- **MRR** (Mean Reciprocal Rank) — how high up was the *first* relevant chunk?
- **nDCG@k** — a graded relevance score with position discounting.
- **Hits@k** — did *any* relevant chunk make the top-k? (Binary version of recall@k.)

These are computed against a known set of "right answer" labels. You need an [eval set](./eval-set-construction.md) — a list of queries with expected_doc/expected_chunks annotations — to compute any of them.

The good news: retrieval metrics are *cheap* and *reproducible*. No LLM call required. Run them in CI on every commit.

## Generation metrics

The generation question is "given the retrieved chunks, did the system produce a good answer?" — much harder to measure because the answer is free text.

Five concerns to separate, each with its own metric ([covered in depth on a later page](./answer-quality-metrics.md)):

- **Faithfulness** — does the answer say things the retrieved chunks support?
- **Groundedness** — does every claim in the answer trace to a specific chunk?
- **Citation accuracy** — do the cited chunks actually contain the cited claim?
- **Answer relevance** — does the answer address the query?
- **Refusal quality** — when the corpus can't answer, does the system refuse honestly?

The bad news: most of these are hard to compute mechanically. Rule-based checks (e.g., "does every numbered fact in the answer appear verbatim in some chunk?") work for narrow cases. **LLM-as-judge** — using a strong LLM to score answers against chunks — is the standard for the rest. Both have failure modes; [the answer-quality page covers them](./answer-quality-metrics.md).

## Correctness vs. groundedness — a critical distinction

These two get conflated constantly, and the difference matters:

- **Correctness** = "is the answer factually true?" — measured against external truth.
- **Groundedness** = "does the answer follow from the retrieved chunks?" — measured against the chunks.

These are different properties:

| | Grounded | Not grounded |
|---|---|---|
| **Correct** | ✓ Ideal — answer is true *and* supported by chunks. | ⚠ Lucky — answer is true but the model went outside the chunks to get there. The system can't be trusted to do this reliably. |
| **Incorrect** | ⚠ Garbage in, garbage out — chunks are wrong but the model faithfully relayed them. The retrieval system needs fixing, not the LLM. | ✗ Worst case — answer is wrong *and* fabricated. |

For RAG systems, **groundedness is what you actually want to measure**. The premise of RAG is "ground the answer in retrieved chunks instead of relying on parametric knowledge." If the answer isn't grounded, you don't have a RAG system — you have an LLM doing what it would do anyway.

Correctness depends on whether your corpus is correct, which is a content problem, not a RAG problem. If your corpus says the earth is flat and the system faithfully repeats that, RAG is doing its job; the *corpus* is the bug.

This is why production RAG evaluation focuses heavily on groundedness/faithfulness and relatively less on correctness. Correctness is usually measured separately, against external ground truth, for the queries that have it.

## What evaluation can't tell you

Important to flag upfront:

- **Evaluation doesn't fix anything.** It tells you what's broken. The fixes come from the [retrieval failure modes](../rag/retrieval-failure-modes.md) decision tree, the [contextual retrieval](../rag/contextual-retrieval.md) and [query rewriting](../rag/query-rewriting.md) interventions, or generation-side prompt engineering.
- **Single-number scores hide structure.** A 0.85 mean faithfulness score can mean (a) 85% of queries are great, 15% catastrophic, or (b) every query is mediocre. Always look at the distribution, not just the mean.
- **Eval set quality caps everything.** A poorly constructed eval set will rank your interventions in the wrong order. Garbage eval, garbage decisions. The next page is about how to avoid this.
- **Production traffic ≠ eval set.** Your eval set is a frozen snapshot of what you *thought* the queries would look like. Real users phrase questions in ways you didn't anticipate. Offline metrics correlate with online quality; they don't substitute for it.

## When you have evaluation infrastructure, you can…

The point of all this is decisions. Once you have an eval set and can compute metrics on it, you can:

- **A/B retrieval changes.** Does adding the cross-encoder reranker (Lab 07) actually help on *your* corpus, or just on Anthropic's benchmark?
- **Catch regressions.** You changed the embedding model. Did retrieval get worse on 30% of queries that used to work? CI will tell you.
- **Triage failures.** A user complaint comes in. Was it retrieval or generation? Run the query through your harness; look at which metric tanked.
- **Justify dependencies.** Is the cost of the contextual retrieval LLM calls worth the recall lift? Compute both numbers; decide on evidence.
- **Communicate with stakeholders.** "We're at 92% recall@5 on our 50-query eval set" is a fact. "RAG is working great" is a feeling.

Without evaluation, every retrieval engineering decision is faith-based. With it, decisions become evidence-based — even when the evidence is imperfect.

## The progression in this section

The four pages of this folder form a progression:

1. **This page** — orientation. Two-part question, correctness vs. groundedness.
2. **[Eval set construction](./eval-set-construction.md)** — building the foundation that everything else stands on.
3. **[Retrieval metrics](./retrieval-metrics.md)** — what to compute for the retrieval half.
4. **[Answer quality metrics](./answer-quality-metrics.md)** — what to compute for the generation half.

Then [Lab 09](../../labs/09-evaluating-agentic-rag/) puts it together: a from-scratch harness over Labs 06-08's retrieval pipeline, a 30-question eval set, and tables that let you compare every Lab 06-08 intervention head-to-head.

## A note on "evaluation frameworks"

You'll see RAGAS, TruLens, DeepEval, Phoenix, LangSmith, LangFuse, Weights & Biases mentioned everywhere in RAG content. These are real, mature, useful tools. They wrap the metrics this section covers and add production observability on top.

Path 02 deliberately doesn't use any of them. The reason is pedagogical: you should understand what the metrics *are*, and what they *do and don't measure*, before adopting a framework that hides those details behind nice APIs. Once you've built the harness from scratch in Lab 09, adopting RAGAS or DeepEval is a 30-minute swap; the conceptual leap is already done.

[Path 06](../../learning-paths/) — Evaluation & Observability — is where the framework treatment lives. It builds on this section.

## See also

- 📖 [Eval set construction](./eval-set-construction.md) — next page in this section.
- 📖 [Retrieval failure modes](../rag/retrieval-failure-modes.md) — the qualitative version of what evaluation quantifies.
- 🧪 [Lab 09](../../labs/09-evaluating-agentic-rag/) — the implementation.

## References

- Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). The paper that named and structured RAG evaluation as a discipline, even though Path 02 doesn't use the framework.
- Min, S., Krishna, K., Lyu, X., Lewis, M., Yih, W., Koh, P. W., Iyyer, M., Zettlemoyer, L., & Hajishirzi, H. (2023). [*FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation*](https://arxiv.org/abs/2305.14251). EMNLP 2023. Decomposes "is this factually correct" into atomic-claim verification — the conceptual basis for faithfulness checking.
- Zheng, L. et al. (2023). [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685). NeurIPS 2023 Datasets and Benchmarks. The canonical LLM-as-judge paper; documents agreement with human raters at >80% but also catalogues the position/verbosity/self-enhancement biases.
- Manning, C. D., Raghavan, P., & Schütze, H. (2008). [*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/). Cambridge University Press. The textbook source for retrieval metrics. Free online.
- Thakur, N. et al. (2021). [*BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*](https://arxiv.org/abs/2104.08663). NeurIPS 2021. The standard benchmark whose conventions (nDCG@10, recall@100) shape how retrieval gets evaluated.
