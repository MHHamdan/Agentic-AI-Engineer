# Query rewriting

> 🟢 Stable · ⏱ ~10 min read · 🏷 rag, retrieval, query-side

## TL;DR

Retrieval depends on the query you give it. If the query is vague, oddly phrased, or doesn't share vocabulary with the chunks, no retriever — not BM25, not dense, not hybrid, not reranked — will surface the right chunks.

**Query rewriting** addresses this from the query side. An LLM transforms the user's question into one or more retrieval-optimized strings before retrieval runs. The retrievers don't change; the input does.

Three patterns matter in practice:

- **HyDE** (Hypothetical Document Embeddings) — generate a fake answer, embed *that*, retrieve against it.
- **Multi-query expansion** — generate several rephrasings of the same question, retrieve each, fuse the results.
- **Query decomposition** — break a multi-part question into atomic sub-queries.

This page covers all three, when each helps, and the common failure modes. [Lab 08](../../labs/08-contextual-retrieval-and-query-rewriting/) implements them from scratch.

---

## Why the raw query is often the wrong query

Consider three real queries against a documentation corpus:

1. *"how do i fix my db"* (vague — what database? what's broken?)
2. *"Tell me about embeddings and rerankers, plus how they relate to vector indexes"* (multi-part — three sub-questions in one)
3. *"What does Claude do when the context is too long?"* (paraphrased — chunks say "context window exceeded" not "context is too long")

A bi-encoder retriever processes each as a single embedding. Query (1) has no specificity. Query (2) gets compressed into one vector that's "about" embeddings + rerankers + vector indexes mixed together. Query (3) has the wrong vocabulary.

Each of these is a retrieval problem you could try to fix on the retriever side — increase top_k, add hybrid search, add a reranker. None of those interventions help with the *root cause*: the query itself is the wrong input.

Query rewriting takes the LLM-already-in-your-loop and uses it to fix the query *before* retrieval runs. The retrievers stay the same; the queries get better.

## Pattern 1: HyDE — Hypothetical Document Embeddings

Gao, Ma, Lin & Callan (Dec 2022, ACL 2023) proposed an inversion: instead of retrieving documents that *match* the query, retrieve documents that match a *hypothetical answer* to the query.

The flow:

```text
1. User query: "What does Claude do when the context is too long?"
2. LLM generates a hypothetical answer:
   "When the context window is exceeded, Claude returns an error.
    Production usage should monitor for this and truncate or
    summarize the conversation history."
3. Embed THAT (not the original query).
4. Retrieve against the hypothetical-answer embedding.
```

The key insight: **answers share vocabulary with the chunks that contain them**. The hypothetical answer is more likely to retrieve the right chunks than the question itself, because chunks are statements and answers are statements; questions are not.

What HyDE handles well:
- **Paraphrased queries** where the chunk uses different vocabulary.
- **Zero-shot domains** where the retriever wasn't trained on this corpus's terminology — HyDE was designed for this case.
- **Underspecified queries** where the question implies an answer space the LLM can fill in.

What HyDE doesn't help with:
- **Exact-match queries** ("error code TS-999"). BM25 already handles these; HyDE may introduce noise.
- **Multi-part queries** where one hypothetical answer can't cover both parts. Use decomposition instead.
- **Domains where the LLM has no relevant knowledge** — the hypothetical answer is just made up, the embedding goes to a random place, retrieval gets worse.

The big tradeoff: **HyDE always adds an LLM call** before retrieval runs. Latency goes up; cost goes up. Whether the precision gain justifies the cost depends on your workload. For latency-critical or high-QPS production systems, it's often net negative; for analytical or research workloads where each query matters, it's often net positive.

A common variant in the original paper: generate **multiple** hypothetical answers (5 in the paper), embed each, average the embeddings. Reduces variance from any single hallucinated answer.

## Pattern 2: Multi-query expansion

Multi-query takes the original question and asks the LLM to **rephrase it several ways**. Each rephrasing becomes its own query; results are fused.

```text
User query: "How do I handle long context in Claude?"

LLM generates rephrasings:
1. "context window limits and overflow handling in Claude"
2. "what happens when a prompt exceeds Claude's max tokens"
3. "managing token budgets in long Anthropic conversations"

Retrieve each independently → RRF fusion → top-k
```

The bet: each rephrasing reaches a slightly different region of the embedding space and the lexical space. The union catches chunks any single phrasing would miss.

This is roughly the **Query2doc** pattern (Wang et al., EMNLP 2023, arXiv:2303.07678), which uses few-shot prompting to generate pseudo-documents and appends them to the query.

Multi-query helps most for:
- **Queries with terminology variants** — when chunks use synonyms or different domain dialects.
- **Conversational queries** that mix formal and informal vocabulary.

Cost concerns:
- N queries means N retrieval calls (and N× the BM25/embedding compute) plus the LLM call for generation. For a 5-rephrasing setup that's 5× retrieval cost.
- The fusion step matters: RRF (the Cormack k=60 formula) is a defensible default. Score averaging across retrievers tends to overweight queries that happen to produce high raw scores.

A practical compromise some teams use: generate just 2-3 rephrasings, not 5+. The diminishing returns are sharp; a handful of phrasings catches most of the lift.

## Pattern 3: Query decomposition

Some queries shouldn't be answered by retrieval against the original query at all. They're compound questions:

> "What's the difference between Claude's bi-encoder and cross-encoder retrieval, and which one does the Lab 06 corpus use?"

Three sub-questions here:
1. What is a bi-encoder?
2. What is a cross-encoder?
3. Which does Lab 06 use?

If you retrieve against the whole query, the embedding compresses all three concerns into one vector that's not specifically about any of them. The top-k will be vaguely relevant to "encoder retrieval" but probably won't have the chunk that answers (3).

**Decomposition** asks the LLM to split the query into sub-queries:

```text
User: "What's the difference between Claude's bi-encoder and
cross-encoder retrieval, and which one does the Lab 06 corpus use?"

LLM decomposition:
  sub_query_1: "bi-encoder retrieval architecture"
  sub_query_2: "cross-encoder retrieval architecture"
  sub_query_3: "Lab 06 corpus retrieval method"

Retrieve each → union (or RRF) → top-k
```

The agent then sees chunks specifically about each sub-question and can synthesize the comparative answer.

This is essentially **how the [agent loop](../agents/agent-loop.md) handles compound queries naturally**. If your agent has retrieval as a tool, it'll often decompose multi-part queries by calling retrieval multiple times. You can also do decomposition explicitly as a preprocessing step before the agent loop runs — useful when the agent's first-call latency matters.

When to use explicit decomposition vs. let-the-agent-do-it:
- **Explicit decomposition is faster** because the sub-queries run in parallel.
- **Agent-driven decomposition is more flexible** because the agent can react to what each sub-query returned and refine.
- For most production systems, **let the agent do it**. Decomposition-as-preprocessing is a useful pattern for high-throughput pipelines where parallelism beats flexibility.

## Composing query rewriting with other interventions

Query rewriting sits *upstream* of retrieval, so it composes freely with retrieval-side interventions:

```text
User query
   │
   ▼
[Query rewriting]   ◄── HyDE / multi-query / decomposition
   │
   ▼
[Dense retrieval]  ─┐
[BM25 retrieval]   ─┤
                    ├─→ [RRF fusion] → [MMR] → [Rerank] → top-k
                    │
[Contextual chunks indexed once at build time, used here]
```

The full stack (contextual retrieval + hybrid + RRF + MMR + rerank + query rewriting) is what production-grade RAG systems converge on. Most workloads don't need all of it; most workloads benefit from picking 2-3 of these based on which failure modes they actually see.

## When query rewriting hurts more than it helps

Query rewriting is not a free win. Three failure modes worth knowing:

1. **The LLM hallucinates the wrong topic.** If the user query is ambiguous and the LLM's hypothetical answer goes in the wrong direction, you've moved the retrieval target *away* from the correct chunks. HyDE in unfamiliar domains is the most susceptible.
2. **Latency stacks up.** Every rewrite is an LLM call. HyDE + multi-query (5×) + agent loop is 6 LLM calls before any answer is generated. For interactive UIs, this is often the wrong tradeoff.
3. **It hides upstream problems.** If retrieval is failing because your *corpus* is incomplete, query rewriting doesn't add documents that aren't there. It just makes you do more work for the same result.

The discipline: **measure first**. Pick 30-50 queries your retrieval gets wrong. Categorize *why* (paraphrase, multi-part, vague, off-corpus, etc.). If most failures are paraphrase-shaped, HyDE helps. If most are multi-part, decomposition helps. If most are off-corpus, no query rewriting will help — fix the corpus.

## Production patterns

A few real-world patterns:

- **Rewrite only when retrieval initially fails.** Run a fast bi-encoder retrieval; if the top-k similarity is below a threshold, run HyDE and retry. Saves cost on the easy cases. Lab 06's score floor enables this pattern naturally.
- **Cache rewrites.** A user reformulating the same question gets the same rewrite. Cache `query → rewrite` mappings, especially for HyDE (which is expensive).
- **Use a small model for rewrites.** Claude Haiku, GPT-4o-mini, or a similar tier is usually sufficient for query rewriting. The big model is for answer generation; the small model for query transformation.
- **Show the user the rewrites in research UIs.** When a user is doing analytical work, the rewrites are often more informative than the answer — they reveal *how the system understood the question*. This builds trust and gives the user a debug surface.

## Adjacent techniques worth knowing about

Mentioned for completeness; not covered in this batch:

- **Conversational query rewriting** — rewriting the latest query to be self-contained, given chat history. (E.g., "what about the second one?" → "tell me about Lab 02".) Important for multi-turn chat; covered in a future framework-bridge lab.
- **Query routing / classification** — deciding which retriever or which corpus to query for this question. A different problem; useful at multi-corpus scales.
- **Retrieve-and-edit (Rewrite-Retrieve-Read)** — Ma et al. (2023, arXiv:2305.14283) explicitly trains a small rewriter model. The pattern is the same; the training step is what makes it sharper. Out of scope for this lab.
- **Self-RAG / Corrective RAG** — agent patterns that judge retrieval quality and decide to rewrite or skip retrieval entirely. These are *agent-loop* patterns built on the primitives this page covers.

## See also

- 📖 [Retrieval as a tool](./retrieval-as-a-tool.md) — how agent-driven query refinement composes with these patterns.
- 📖 [Contextual retrieval](./contextual-retrieval.md) — the corpus-side counterpart.
- 📖 [Hybrid search](./hybrid-search.md) — query rewriting feeds both retrievers in a hybrid setup.
- 📖 [Retrieval failure modes](./retrieval-failure-modes.md) — when to reach for which intervention.
- 🧪 [Lab 08](../../labs/08-contextual-retrieval-and-query-rewriting/) — implements HyDE, multi-query, and decomposition from scratch.

## References

- Gao, L., Ma, X., Lin, J., & Callan, J. (2022). [*Precise Zero-Shot Dense Retrieval without Relevance Labels*](https://arxiv.org/abs/2212.10496). ACL 2023. The HyDE paper.
- Wang, L., Yang, N., & Wei, F. (2023). [*Query2doc: Query Expansion with Large Language Models*](https://arxiv.org/abs/2303.07678). EMNLP 2023. The Query2doc pattern; the canonical reference for LLM-driven query expansion.
- Ma, X., Gong, Y., He, P., Zhao, H., & Duan, N. (2023). [*Query Rewriting for Retrieval-Augmented Large Language Models*](https://arxiv.org/abs/2305.14283). The Rewrite-Retrieve-Read pipeline, which formalizes the pattern of training a rewriter for downstream RAG.
- Cormack, G. V., Clarke, C. L. A., & Büttcher, S. (2009). [*Reciprocal rank fusion outperforms Condorcet and individual rank learning methods*](https://dl.acm.org/doi/10.1145/1571941.1572114). SIGIR 2009. The RRF algorithm used to fuse multi-query results.
- Lewis, P. et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. The RAG paper; uses a single query throughout, motivating later query-rewriting work.
