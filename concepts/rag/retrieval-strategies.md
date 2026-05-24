# Retrieval strategies

> 🟢 Stable · ⏱ ~11 min read · 🏷 rag, retrieval, ranking

## TL;DR

A retriever has more knobs than it looks like — `top_k` is just the most visible one. This page covers the stable knobs that govern retrieval quality on *any* RAG system, regardless of which embedding model or vector store you're using: how many results to return, when to floor low-similarity hits, how to diversify the top-k, and how to phrase queries to retrieve well.

These are the decisions you make *before* reaching for reranking ([next concept page](./reranking.md)) or hybrid search ([the one after](./hybrid-search.md)). Tuning them well is usually higher-impact than swapping retrievers.

If you finished Lab 06, this page is the conceptual frame for what Lab 07 will exercise — Lab 06's `search_corpus` exposes exactly the knobs discussed here.

---

## The four knobs that matter most

In rough order of how often they're miscalibrated in production RAG:

1. **`top_k`** — how many chunks to return per query.
2. **Score floor** — minimum similarity to count as a real hit (vs. "nothing matched").
3. **Diversification** (MMR) — penalizing near-duplicate chunks in the top-k.
4. **Query construction** — what string the retriever sees.

Each is independently tunable; each has a defensible default that works for most workloads; each is something a learner builds intuition for by running a few targeted experiments. The rest of this page is those defaults plus the experiments that calibrate them.

## Knob 1 — `top_k`

The default in most RAG tutorials is `top_k=5`. It's a reasonable place to start, but the right value depends on two things:

- **What the agent does with the results.** If the agent reads every returned chunk in full (naive RAG), more chunks means more tokens stuffed into the prompt — recall improves but signal-to-noise degrades after about 5-10. If the agent triages (Lab 06's pattern — `search_corpus` returns snippets, agent picks 1-2 to `read_chunk`), you can afford higher `top_k` because the model isn't paying full chunk cost.
- **The size of your corpus.** Top-5 on a 10-chunk corpus is meaningless. Top-5 on a 100K-chunk corpus is barely scratching the surface for synthesis-heavy questions.

The honest rule:

| Use case | Reasonable `top_k` |
|---|---|
| Triage with agent loop (Lab 06 pattern) | 5-10 |
| Naive RAG (stuff and generate) | 3-5 |
| Synthesis across many docs | 10-20 |
| Reranking pipeline (this `top_k` is the *candidate set*) | 30-50 |
| Embedded in a re-ranker downstream | as many as the re-ranker can handle |

The biggest mistake is **leaving `top_k` at 5 when the pipeline includes a re-ranker**. Reranking is essentially "ask a more expensive model to pick from a larger candidate pool" — if you only give it 5 candidates, you've kept the bi-encoder's mistakes in the pool and made the re-ranker's job pointless. Pre-rerank, `top_k=30-50` is normal.

### Calibrating `top_k` on your corpus

You don't have to guess. For a small validation set of questions you know the right chunks for:

- Set `top_k=20`.
- Run the queries.
- Note the lowest *rank position* of a correct chunk across queries.

If the worst case is rank 8, you need `top_k>=8` to consistently surface the right chunks. If the worst case is rank 17, your retriever is missing things — increase `top_k` to 20+, *and* think harder about chunking or query construction.

This is one of the very few hyperparameters in RAG worth measuring rather than guessing.

## Knob 2 — score floors

A retriever always returns *something*. Cosine similarity is bounded in `[-1, 1]`; BM25 scores are bounded only by document length and term frequency. Either way, `top_k=5` will faithfully return five chunks — even when none of them matches the query.

**Score floors** address this. Below a configured similarity threshold, the retriever returns `status: empty` (or whatever your contract calls it) instead of low-quality results.

Lab 06's `search_corpus` uses `MIN_SIMILARITY = 0.30` against normalized MiniLM embeddings (so cosine ≈ dot product). When no chunk crosses the floor:

```python
{"status": "empty", "query": "...", "detail": "no chunks crossed similarity floor"}
```

The agent can recognize this and refine its query instead of synthesizing from noise.

### How to pick the floor

The defensible way is empirical:

- Run a batch of **off-corpus queries** (things you *know* aren't in the corpus). Note the score distribution of the top-1 chunks. These are your false positives.
- Run a batch of **on-corpus queries** with known good answers. Note the score distribution of the top-1 chunks. These are your true positives.
- Pick a floor between the two distributions. For Lab 06's MiniLM + 55-chunk corpus, off-corpus top-1 scores cluster around 0.10-0.18 and on-corpus top-1 around 0.40-0.75 — 0.30 is comfortably in the gap.

The floor is **model-specific and corpus-specific**. MiniLM cosines run lower than larger models. BGE-large cosines run higher. A floor calibrated for one combination won't transfer.

### When score floors hurt

Floors trade recall for precision. If your floor is too tight, you'll return `empty` on queries where a marginal-but-correct chunk would have answered. Symptoms: the agent says "I couldn't find this" on questions you *know* are in the corpus.

The fix is to lower the floor — but the better fix is usually to improve chunking or query construction, because those are the underlying recall problems.

## Knob 3 — MMR (Maximal Marginal Relevance)

**The problem MMR solves:** your `top_k=5` returns 5 chunks that are all near-duplicates of each other. You've spent the LLM's context budget on essentially the same passage repeated five times.

This happens when:

- Your chunker has overlap and the same content appears in adjacent chunks.
- Your corpus has duplicates (different docs cover the same topic).
- The query is broad and naturally maps to one cluster of similar chunks.

**MMR's idea:** when picking the next chunk to add to the top-k, balance *query relevance* against *dissimilarity from already-selected chunks*. Maximize a weighted combination of the two.

The algorithm (Carbonell & Goldstein, 1998):

```
selected = []
candidates = [all chunks ranked by similarity to query]

while len(selected) < top_k:
    for each candidate c:
        relevance       = sim(c, query)
        max_redundancy  = max(sim(c, s) for s in selected) if selected else 0
        mmr_score       = λ * relevance - (1 - λ) * max_redundancy
    selected.append(candidate with highest mmr_score)
    remove from candidates
```

`λ` is the relevance/diversity tradeoff:

- `λ = 1.0` — pure relevance, identical to standard top-k.
- `λ = 0.7` — gentle diversification. Reasonable default.
- `λ = 0.5` — equal weight; aggressive diversification.
- `λ = 0.0` — pure diversity, ignores the query entirely (useless).

For most RAG workloads, `λ = 0.5-0.7` is the practical range. Lab 07 implements MMR from scratch (~15 lines of numpy) and walks through what changes in the top-k.

### When MMR doesn't help

If your `top_k` results are *already* diverse (each chunk covers a different sub-topic), MMR is a no-op — it'll return roughly the same order. The overhead is small but real. If you've measured your retrieval and the top-k are already varied, skip MMR.

MMR also doesn't fix bad retrieval — it can only reorder chunks the retriever already returned. If the right chunk isn't in the top-50, MMR can't surface it.

## Knob 4 — query construction

This one's the most under-appreciated and the highest-leverage. The query you give the retriever isn't the user's question; it's whatever string you pass in.

In Lab 06, `search_corpus(query, top_k)` takes whatever the model decides to send. If the user asks *"Can you explain how the ReAct pattern's thought-action-observation cycle relates to the broader four-phase agent loop?"*, the model might send any of:

- The whole question, verbatim.
- "ReAct pattern agent loop"
- "thought action observation"
- "ReAct vs four-phase agent loop"

Each retrieves a different top-k. The shorter, keyword-heavy queries tend to do *better* than verbose questions on bi-encoder retrieval, because the embedding compresses noise (filler words) into a less distinctive vector.

### Tactics that work

- **Strip stop words and filler** in the agent's query before retrieval. "Can you tell me about" adds noise.
- **Front-load proper nouns and technical terms.** Embedding models weight earlier tokens slightly more, and proper nouns are usually the most distinguishing signal.
- **Decompose multi-part questions.** "What's X and how does Y compare to Z?" → two queries: `"X definition"` and `"Y vs Z"`. The agent loop already does this naturally — refining the query is one of its primary moves.
- **Don't over-engineer the system prompt** to dictate query format. Models follow loose guidance ("phrase queries as 3-8 specific words") better than rigid rules.

### Tactics that often look right but don't help

- **Adding metadata to the query** ("category: technical, urgency: high") — confuses the embedding model, doesn't filter. Use filtered retrieval instead (a separate metadata index plus dense ranking within the subset).
- **Rewriting the query as a hypothetical answer (HyDE)** — sometimes helps, sometimes hurts; it's worth measuring on your corpus before adopting. A topic for a later batch.
- **Translating the query** to a "more retrievable" form via a separate LLM call — adds latency, sometimes helps recall, often introduces drift. Not worth it for most workloads.

The honest summary: **the agent's query phrasing is the single biggest thing you can improve about a RAG system without changing infrastructure**. Spend time on it before reaching for fancier retrievers.

## What this page deliberately skips

These are real techniques, but they live in later concept pages or are out of scope for this batch:

- **Hybrid search** (BM25 + dense fusion) — [`hybrid-search.md`](./hybrid-search.md).
- **Reranking** with a cross-encoder — [`reranking.md`](./reranking.md).
- **Contextual retrieval** (Anthropic's chunk-augmentation technique) — future Path 02 batch.
- **Query expansion / HyDE / multi-query** — future batch.
- **Late-interaction models** (ColBERT, ColPali) — production-grade, off-the-shelf-difficult, out of scope.
- **Filtered retrieval** (metadata pre-filtering) — covered briefly in [`chunking-and-indexing.md § metadata`](./chunking-and-indexing.md#metadata-the-underused-lever); the lab pattern is straightforward.

The four knobs above plus hybrid search plus reranking handle ~90% of the retrieval-quality work most RAG systems do. The rest is corpus quality, which no retriever can fix.

## A practical sequence for improving retrieval

If you're staring at a RAG system that's "not finding the right chunks," here's the order to attack the problem:

1. **Audit the corpus.** Are the chunks even the right granularity? Are there obvious gaps? Is the right answer actually *in* the corpus, or did the user assume it would be?
2. **Audit the queries.** What strings is the agent sending? Are they specific enough? Are they hitting the words the chunks actually use?
3. **Increase `top_k`** and look at ranks 6-15. If the right chunk is in there, you have a precision problem (which reranking solves). If the right chunk is *not* in the top 50, you have a retrieval problem.
4. **Try BM25 alongside dense retrieval** for queries with proper nouns or specific terminology. If BM25 finds chunks dense retrieval misses, [hybrid search](./hybrid-search.md) is the next step.
5. **Add MMR** if you observe duplicate-cluster top-k results.
6. **Add a reranker** if step 3 showed the right chunk consistently ranks 6-15.
7. **Lower the score floor** *only after* steps 1-6, because lowering the floor admits more noise.

Lab 07 walks through steps 3-6 against the same corpus you used in Lab 06.

## See also

- 📖 [Hybrid search](./hybrid-search.md) — when keyword + dense retrieval beats either alone.
- 📖 [Reranking](./reranking.md) — adding a cross-encoder to improve precision.
- 📖 [Chunking and indexing](./chunking-and-indexing.md) — the upstream decisions that bound retrieval quality.
- 📖 [Retrieval as a tool](./retrieval-as-a-tool.md) — how the agent uses these knobs at inference.
- 🧪 [Lab 07: Retrieval strategies and reranking](../../labs/07-retrieval-strategies-and-reranking/) — exercises everything on this page.

## References

- Carbonell, J., & Goldstein, J. (1998). [*The use of MMR, diversity-based reranking for reordering documents and producing summaries*](https://dl.acm.org/doi/10.1145/290941.291025). SIGIR 1998. The MMR paper. The algorithm has barely changed in 27 years.
- Robertson, S., & Zaragoza, H. (2009). [*The Probabilistic Relevance Framework: BM25 and Beyond*](https://www.staff.city.ac.uk/~sb317/papers/foundations_bm25_review.pdf). Foundations and Trends in Information Retrieval. Comprehensive review of BM25's lineage and tuning.
- Gao, Y. et al. (2024). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997). §4 covers retrieval strategies in detail with citations.
- Lewis, P. et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. The paper that named the pattern; uses top-5 retrieval throughout.
- Karpukhin, V. et al. (2020). [*Dense Passage Retrieval for Open-Domain Question Answering*](https://arxiv.org/abs/2004.04906). EMNLP 2020. DPR established the bi-encoder retrieval pattern Lab 06 implements.
