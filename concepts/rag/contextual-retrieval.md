# Contextual retrieval

> 🟡 Evolving · ⏱ ~11 min read · 🏷 rag, retrieval, chunking, anthropic
>
> 🔴 **Technique snapshot:** Contextual Retrieval was introduced by Anthropic on September 19, 2024. Headline metrics quoted in this page come from Anthropic's published benchmarks; verify the [original post](https://www.anthropic.com/news/contextual-retrieval) for the most current numbers before citing.

## TL;DR

Chunks lose context when you cut them out of their document. A standalone sentence like *"The company's revenue grew by 3% over the previous quarter"* is meaningless without the doc it came from — but BM25 only sees the chunk, and your embedding model only embeds the chunk.

**Contextual retrieval** fixes this by using an LLM to generate a short situating sentence for each chunk *before* indexing. That sentence — usually 50-100 tokens — gets prepended to the chunk, and both the BM25 index and the embedding model see the augmented version. Retrieval improves because the chunk now carries enough context to be retrievable on its own.

Anthropic's published benchmarks (Sep 2024): contextual embeddings alone reduced the top-20 retrieval failure rate by **35%**; combined with contextual BM25, **49%**; further combined with reranking, **67%**.

This page covers the *mechanism* and the *operational tradeoffs*. [Lab 08](../../labs/08-contextual-retrieval-and-query-rewriting/) implements it from scratch on the Lab 06 corpus.

---

## The problem: context loss at chunk time

Consider a paragraph in the middle of an SEC 10-Q filing:

> The company's revenue grew by 3% over the previous quarter, driven by stronger international sales and modest improvement in legacy product lines. Cost of revenue increased disproportionately to 4%, however, reflecting input price pressure that management does not expect to reverse in the near term.

If you split this 10-Q into ~200-token chunks for retrieval, this paragraph becomes its own chunk. Now imagine a query: *"What was ACME Corp's Q2 2024 revenue growth?"*

The chunk contains the answer (3%). But:

- **BM25** doesn't see "ACME Corp" or "Q2 2024" anywhere in the chunk — those words are elsewhere in the document. The lexical signal is missing.
- **The embedding** captures "company revenue grew quarter" but the model has no way to know *which* company or *which* quarter. The dense signal is fuzzy.
- **The reranker** could maybe figure it out from the chunk + the doc filename — but only if you pass filename to the reranker (most pipelines don't) and even then it's a weak signal.

The chunk is *factually* the right one. But the retriever can't recognize it as such, because the retriever never sees the surrounding document.

This is the failure mode contextual retrieval exists to fix.

## The mechanism

For every chunk in your corpus, generate a short situating sentence using an LLM. The Anthropic-recommended prompt (verified at the source):

```text
<document>
{{WHOLE_DOCUMENT}}
</document>

Here is the chunk we want to situate within the whole document
<chunk>
{{CHUNK_CONTENT}}
</chunk>

Please give a short succinct context to situate this chunk within the
overall document for the purposes of improving search retrieval of the
chunk. Answer only with the succinct context and nothing else.
```

For the SEC example above, this returns something like:

> *This chunk is from ACME Corp's Q2 2024 10-Q filing on financial performance. The previous quarter's revenue was $314 million. The chunk discusses revenue growth and cost trends.*

Then you prepend that to the chunk and index the augmented version:

```text
[CONTEXT]
This chunk is from ACME Corp's Q2 2024 10-Q filing on financial performance.
The previous quarter's revenue was $314 million. The chunk discusses revenue
growth and cost trends.

[ORIGINAL CHUNK]
The company's revenue grew by 3% over the previous quarter...
```

Both your BM25 index and your embedding model now see "ACME Corp", "Q2 2024", and the topical framing. The chunk becomes retrievable on its own merits.

The augmented chunks are used for *retrieval only*. When the LLM eventually reads a candidate chunk in full (Lab 06's `read_chunk` pattern), it should read the original — the context summary is a retrieval aid, not part of the source of truth.

## Why it works

Three independent effects compound:

1. **Lexical signal restoration.** BM25 now has the proper nouns ("ACME Corp"), the time period ("Q2 2024"), and any doc-level terminology that wasn't in the chunk. Queries with exact terms find the right chunk.
2. **Semantic anchoring.** The embedding now compresses *both* the chunk's content *and* the document's topical position. Two similar-looking chunks from different documents now have *different* embeddings because their context summaries differ.
3. **Cross-chunk disambiguation.** If your corpus has multiple documents with similar content (e.g., multiple quarters of 10-Q filings), augmenting with the doc identity prevents the retriever from confusing them.

The technique sits **upstream of** retrieval strategies, hybrid search, and reranking. It changes what each chunk *looks like* to the retriever, not how the retriever ranks them. You still want hybrid + rerank on top.

## What the augmentation looks like in practice

Anthropic's benchmark targeted 800-token chunks with ~100-token context summaries — about a 12.5% token-overhead on the index size. The summaries the LLM produces are typically:

- 1-3 sentences.
- Name the document or document type.
- Mention any unique entities the chunk implies but doesn't state (company, quarter, person, project).
- Mention the topical role of the chunk within the doc (introduction, conclusion, methodology, example).

Examples:
- *"This chunk is from ACME Corp's Q2 2024 10-Q filing on financial performance."* — names entity + time.
- *"This chunk is from the Python documentation on dictionaries, in the section on dict comprehensions."* — names library + section.
- *"This chunk is from a customer support ticket about the iPhone 15 Pro Max camera. The customer is reporting blurry photos in low light."* — names product + issue type.

The 50-100 token target keeps overhead manageable while carrying the key disambiguating signal.

## The cost question

This technique is operationally meaningful: you're paying for one LLM call per chunk at index time. For a corpus of 100K chunks, that's 100K LLM calls. The math matters.

Anthropic's cited cost (with prompt caching, Claude Haiku) is **~$1.02 per million document tokens**. That assumes:

- 800-token chunks
- 8000-token documents (10 chunks per doc, on average)
- 50-token instruction prompt
- 100-token context output per chunk

This number isn't a guarantee for your corpus — it scales with doc length and chunk count — but it's a realistic order-of-magnitude. The technique is feasible at corpus scales of millions of chunks.

The key cost optimization is **prompt caching**. The naive implementation passes the whole document for *every chunk* in that document; with 10 chunks per doc, that's 10× redundant document tokens. With prompt caching, the document is loaded into the cache once and referenced cheaply across all chunks in that document.

As of late 2024, Anthropic's prompt-caching pricing (5-minute TTL):
- Cache write: 1.25× base input cost
- Cache read: 0.1× base input cost (90% discount)

Break-even: just *one* cache hit makes caching cheaper than re-paying. For a 10-chunk document, you save ~80% on document tokens.

OpenAI also offers prompt caching with automatic 50% discount on cached input (no per-message marking required). Gemini has implicit caching. The technique works with any provider; the economics shift slightly.

## When to use it

The honest cost-benefit framing:

**Strongly worth it when:**
- Documents are long enough that chunks lose disambiguating context (financial filings, legal cases, technical docs, codebases with multiple modules).
- Documents share structural similarity (multiple quarters of one company, multiple chapters of a book, multiple PRs from one repo).
- You're seeing retrieval failures of the "chunk is right but doesn't look it" kind — paraphrased queries that should hit but don't.

**Probably not worth it when:**
- Chunks are already self-contained (FAQ entries, recipe steps, glossary entries).
- Documents are short enough that chunks rarely need context (single-page Q&A, social posts, individual email messages).
- Corpus is small enough that the entire corpus fits in the LLM context window (<200K tokens) — Anthropic recommends just stuffing the whole corpus into the prompt instead.
- You can't afford the indexing cost or latency.

The decision is corpus-shape-specific. Run a small experiment: take 50 of your queries that retrieval gets wrong, contextualize the relevant 10-20 documents, re-test. If 10+ of the failed queries now succeed, the technique is paying off on your workload.

## Implementation considerations

The Anthropic post calls out four practical concerns:

1. **Chunk size and boundaries** still matter. Contextual retrieval doesn't fix bad chunking; it amplifies whatever your chunker produces. Read [chunking and indexing](./chunking-and-indexing.md) first.
2. **The contextualizer prompt may need domain tuning.** The generic prompt works well in most cases; for highly specialized domains (legal, medical, code), a custom prompt that mentions the domain vocabulary tends to help.
3. **Both BM25 and embeddings index the augmented chunks.** Skip either and you're leaving improvement on the table — and the result names "Contextual BM25" and "Contextual Embeddings" because both matter.
4. **Always evaluate on your corpus.** The 35-67% improvement numbers came from Anthropic's specific benchmarks (codebases, fiction, arXiv, science papers). Your workload may show more or less improvement; you have to measure.

Anthropic also notes that **passing the augmented chunk to the answer-generation step** (not just the original) sometimes improves response quality, because the model has more context to ground its response on. The lab leaves this as a tunable.

## What contextual retrieval is *not*

A few common misconceptions worth flagging directly:

- **It is not query expansion.** Contextual retrieval modifies the *chunks* (index-side). Query expansion modifies the *query* (query-side). Both are useful; they address different failure modes. See [query rewriting](./query-rewriting.md).
- **It is not RAG-summarization.** Summarization replaces the chunk with a summary; contextual retrieval *augments* the chunk with context. The chunk's content is preserved; the retrieval signal is enriched.
- **It is not "give the LLM the whole document."** That defeats the whole point of RAG — you'd be processing the full document on every query. Contextual retrieval pays the document-processing cost *once at index time*.
- **It is not a replacement for hybrid search or reranking.** It composes with them. The published 67% benchmark uses Contextual Embeddings + Contextual BM25 + Reranking *all together*. Skip any one and you lose ~⅓ of the lift.

## Adjacent techniques

Two ideas commonly conflated with contextual retrieval but distinct from it:

- **Document summary indexing** (LlamaIndex's `DocumentSummaryIndex`, 2023). Indexes one summary per *document*, retrieves at doc-level, then drills into chunks. Useful for some hierarchical corpora but solves a different problem (doc-level routing). Doesn't address chunk-level context loss the way contextual retrieval does. Anthropic notes they tested this approach and saw "low performance."
- **Sentence-window retrieval.** Retrieves chunks but returns the surrounding sentences as context. Helps the LLM read the chunk in context, doesn't help the *retriever* find the chunk. Complementary to contextual retrieval, not a substitute.
- **Parent-document retrieval.** Index small chunks for retrieval, but return the parent (larger) chunk for reading. Same comment: improves the read step, not the retrieve step.

These are all "context-aware retrieval" patterns but they differ in *which* step they enrich. Contextual retrieval is unique in enriching the indexed chunk itself.

## Where this leads

Contextual retrieval is a *corpus-side* intervention. The corollary is a *query-side* set of interventions — generating better queries before retrieval runs. That's the next concept page: [query rewriting](./query-rewriting.md), covering HyDE, multi-query, and decomposition.

Then [retrieval failure modes](./retrieval-failure-modes.md) ties Lab 06 + Lab 07 + Lab 08 together: a taxonomy of what goes wrong in RAG, with each failure mode mapped to the right intervention (chunking, strategy, hybrid, rerank, contextual, query rewrite).

## See also

- 📖 [Chunking and indexing](./chunking-and-indexing.md) — what contextual retrieval builds on.
- 📖 [Hybrid search](./hybrid-search.md) — contextual retrieval feeds both BM25 and dense indexes.
- 📖 [Reranking](./reranking.md) — composes with contextual retrieval for the 67% benchmark.
- 📖 [Query rewriting](./query-rewriting.md) — the query-side counterpart.
- 📖 [Retrieval failure modes](./retrieval-failure-modes.md) — when to reach for which intervention.
- 🧪 [Lab 08](../../labs/08-contextual-retrieval-and-query-rewriting/) — implements all three from scratch.

## References

- Anthropic (2024). [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval). The primary source; this page reflects its Sep 19, 2024 metrics and prompt template. Cookbook implementation: [platform.claude.com/cookbook/capabilities-contextual-embeddings-guide](https://platform.claude.com/cookbook/capabilities-contextual-embeddings-guide).
- Anthropic (2024). [*Prompt Caching documentation*](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching). Verify current pricing multipliers before computing your own cost estimates.
- LlamaIndex Team (2023). [*A New Document Summary Index for LLM-Powered QA Systems*](https://www.llamaindex.ai/blog/a-new-document-summary-index-for-llm-powered-qa-systems-9a32ece2f9ec). The document-summary-indexing approach Anthropic evaluated and found weaker.
- Gao, Y. et al. (2024). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997). §4.3 covers context-aware retrieval approaches.
- Pratt, S., Covert, I., Liu, R., & Farhadi, A. (2023). [*What does a platypus look like? Generating customized prompts for zero-shot image classification*](https://arxiv.org/abs/2209.03320). Conceptually adjacent — generating description prompts to enrich a retrieval target's representation.
