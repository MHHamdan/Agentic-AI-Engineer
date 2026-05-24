# Retrieval failure modes

> 🟢 Stable · ⏱ ~11 min read · 🏷 rag, debugging, synthesis

## TL;DR

You shipped a RAG system. Some queries work. Some don't. What do you do about the ones that don't?

This page is the debugging mental model. Eight common failure modes, what each one *looks like*, how to *recognize* it, and which intervention from Labs 06–08 to reach for. It synthesizes the three batches that landed Path 02 so far — chunking, retrieval strategies, hybrid search, reranking, contextual retrieval, query rewriting — into a decision tree for production work.

This is the page to come back to when something breaks.

---

## How to read this page

Each failure mode has the same structure:

- **Symptom** — what you observe from outside the system.
- **Cause** — what's actually going wrong.
- **How to confirm** — the experiment that diagnoses it.
- **Intervention** — which technique fixes it.

The interventions are roughly ordered by effort. Cheap experiments first; expensive infrastructure last.

## Failure mode 1: The right chunk isn't in the top-50

**Symptom.** You manually verify the answer is in some specific chunk. You run retrieval with `top_k=50`. The chunk isn't there.

**Cause.** Retrieval recall is failing upstream. Either the chunk is *too different* from the query semantically and lexically (bad chunking, paraphrase mismatch), or the chunk *doesn't exist* in the form you expected (split across two chunks, embedded with bad context).

**How to confirm.** Find the chunk by manual search through your corpus (grep for distinctive terms). Inspect it. Note (a) what it actually says, (b) what your query says, (c) what context it has that the chunker stripped away.

**Intervention.**
- If the chunk's content lacks the query's terminology: **[contextual retrieval](./contextual-retrieval.md)** — augment with doc context so the retriever knows what the chunk is about.
- If the chunk is split awkwardly: revisit **[chunking](./chunking-and-indexing.md)** — increase chunk size, adjust boundaries, add overlap.
- If the query uses different vocabulary than the chunk: **[query rewriting](./query-rewriting.md)** (HyDE) — generate a hypothetical answer in the chunk's likely vocabulary.

Reranking won't help here. The reranker can only reorder candidates it's given.

## Failure mode 2: The right chunk is in top-50 but ranked too low

**Symptom.** Manual verification shows the chunk *is* in the top-30 or top-50, just ranked at position 12 or 24, well outside the agent's `top_k=5` window.

**Cause.** The bi-encoder is finding the chunk semantically but not ranking it #1 because other chunks have stronger surface similarity. A precision problem, not a recall problem.

**How to confirm.** Set `top_k=50` and look at where the right chunk lands. If it's consistently in positions 5-20, this is your failure mode.

**Intervention.**
- **[Reranking](./reranking.md)** — the textbook case. A cross-encoder rescores the candidate set with query-document interaction signal the bi-encoder didn't have. The right chunk reliably moves to position 1-3.
- Pair with **[hybrid search](./hybrid-search.md)** — gives the reranker access to BM25 candidates too, widening the recall before rerank narrows the precision.

## Failure mode 3: Exact-term queries don't match

**Symptom.** Queries with proper nouns, error codes, function names, or product SKUs return semantically-similar-but-wrong chunks. The exact match exists in the corpus but isn't surfaced.

**Cause.** Dense retrieval fuzzes exact terms into a semantic neighborhood. The model knows "ReAct" and "thought-action-observation" mean similar things, but it ranks both equally — the chunk with the exact "ReAct pattern" string doesn't dominate the chunk that describes the pattern without naming it.

**How to confirm.** Run the same query through BM25 alone. If BM25 surfaces the right chunk at rank 1-3 and dense retrieval ranks it at 5+, this is your failure mode.

**Intervention.**
- **[Hybrid search](./hybrid-search.md)** with RRF fusion. BM25 catches the exact match; dense catches the semantic match; RRF gives you both. This is the most common diagnosis for technical-domain corpora.

## Failure mode 4: Paraphrased queries don't match

**Symptom.** Inverse of failure mode 3. The user asks "how do I deal with long context" but the chunks say "context window exceeded" or "token limit reached." Dense retrieval is fuzzy on it; BM25 finds nothing.

**Cause.** Vocabulary mismatch in both directions: the query and the chunks describe the same concept with different words. Neither retriever has direct lexical or semantic anchor points.

**How to confirm.** Compare the query's keywords against the actual chunk text. If there's no token overlap and the semantic distance is large (rank > 30), this is the failure mode.

**Intervention.**
- **[Query rewriting with HyDE](./query-rewriting.md)** — generate a hypothetical answer in the *chunk's* vocabulary, retrieve against that.
- **[Contextual retrieval](./contextual-retrieval.md)** — augment chunks with topic-naming context that bridges the vocabulary gap.

## Failure mode 5: The top-k are redundant

**Symptom.** All five chunks in the top-5 are from the same document, near-duplicates of each other. The model has to read the same content five times to get five different angles.

**Cause.** The query maps cleanly to one cluster of similar chunks. Your chunker may have introduced overlap that creates near-duplicates, or your corpus may genuinely have repetitive content on this topic.

**How to confirm.** Look at the top-5 chunk IDs and their `doc_id`s. If 4-5 of them are from the same document or near-identical content, this is the failure mode.

**Intervention.**
- **[MMR diversification](./retrieval-strategies.md#knob-3--mmr-maximal-marginal-relevance)** with `λ=0.7` — balances relevance against redundancy in the top-k. Lab 07 implements this from scratch.

Contextual retrieval won't fix this; it only makes the redundant chunks each more retrievable in isolation. Reranking might mask it if the reranker accidentally diversifies, but MMR is the direct fix.

## Failure mode 6: Multi-part queries hit the wrong parts

**Symptom.** A user asks "What's X and how does Y compare to Z?" The retrieval surfaces chunks vaguely about all three but no chunk that answers any specific sub-question well.

**Cause.** Compound queries compress into a single fuzzy embedding. The dense vector is "about" X, Y, and Z mixed together but not specifically about any of them. The retriever ranks chunks by overall topical fit, not by sub-question coverage.

**How to confirm.** Pose each sub-question separately and rerun retrieval. If each individually surfaces the right chunk at rank 1-3, the compound version is the problem.

**Intervention.**
- **[Query decomposition](./query-rewriting.md#pattern-3-query-decomposition)** — break the compound query into atomic sub-queries; retrieve each.
- **Let the [agent loop](../agents/agent-loop.md) handle it** — agents naturally do this when given retrieval as a tool. Lab 06's pattern works fine here. The explicit-decomposition path matters more when latency requires parallel retrieval.

## Failure mode 7: The agent retrieves something but synthesizes the wrong answer

**Symptom.** Retrieval surfaces the right chunks. The agent reads them. The answer is still wrong, hallucinated, or contradicts the chunks.

**Cause.** This is *not a retrieval problem*. It's an answer-generation problem.

**How to confirm.** Inspect the chunks the agent retrieved (your citation log from Lab 06). If they contain the correct answer and the agent's response contradicts them, retrieval did its job.

**Intervention.**
- This is **faithfulness / groundedness**, which is a different concern from retrieval quality. RAG evaluation territory — Path 06.
- Short-term mitigations: (a) prompt-engineer the agent to ground in retrieved text only; (b) use a stronger answer-generation model; (c) reduce the number of chunks passed to generation so the model isn't distracted.
- Long-term: real evaluation with metrics like faithfulness, groundedness, citation accuracy. Out of scope for Path 02.

Don't waste retrieval-engineering effort on this failure mode. Build evaluation first.

## Failure mode 8: The corpus doesn't contain the answer

**Symptom.** The user asks something reasonable. Retrieval returns nothing useful — or returns chunks that aren't quite right. No combination of techniques helps.

**Cause.** The answer isn't in the corpus. The user is asking a question your knowledge base can't answer.

**How to confirm.** Manual corpus search. Grep for any document that *could* contain the answer. If nothing exists, the corpus is incomplete.

**Intervention.**
- **Expand the corpus.** No retrieval technique can find documents that aren't there.
- **Score floors** ([retrieval strategies §2](./retrieval-strategies.md#knob-2--score-floors)) help here — they let the retriever return `empty` instead of low-quality chunks, so the agent can refuse honestly instead of synthesizing nonsense.
- **Search-as-fallback** — for some workloads (Lab 03's research-agent pattern), agents combine corpus retrieval with web search and fall over to search when retrieval scores low. Useful pattern for production but a separate architecture.

This is the most common failure mode in real production RAG. It's also the easiest to misdiagnose as a retrieval problem and pour engineering effort into the wrong fix. Check corpus completeness first.

## The decision tree

When something's wrong with retrieval, walk through these in order:

```text
1. Manually find the right chunk. Does it exist in the corpus?
   ├── NO  → Expand corpus. (FM 8)
   └── YES → Continue.

2. Run retrieval with top_k=50. Is the right chunk in the top-50?
   ├── NO  → Either chunking, contextual retrieval, or HyDE.
   │         Diagnose by inspecting chunk vs query. (FM 1)
   └── YES → Continue.

3. Where in the ranking is it?
   ├── Position 6-50  → Reranking. (FM 2)
   └── Position 1-5   → Continue.

4. Is the top-k redundant (same doc / near-duplicates)?
   ├── YES → MMR. (FM 5)
   └── NO  → Continue.

5. Compare BM25 vs dense for this query. Which one finds it?
   ├── Only BM25  → Hybrid search needed; dense alone won't suffice.
   ├── Only dense → Hybrid still helps as insurance, plus contextual
   │                retrieval if the chunk vocabulary differs from
   │                the query. (FM 4)
   ├── Neither    → HyDE or contextual retrieval. (FM 4)
   └── Both       → Continue; retrieval is actually working.

6. Is the query compound?
   ├── YES → Decomposition or trust the agent loop. (FM 6)
   └── NO  → Continue.

7. The agent retrieved correctly but the answer is wrong.
   → Not a retrieval problem. Path 06 (evaluation). (FM 7)
```

For most real-world RAG debugging, step 1-3 catches 80% of failures. Steps 4-7 are the long tail.

## The failure-mode-to-intervention map

A reference table for the impatient:

| Failure mode | Diagnosis | Fix |
|---|---|---|
| Right chunk not in top-50 | Manual search; chunk vs query inspection | Contextual retrieval, better chunking, HyDE |
| Right chunk at rank 6-15 | top_k=50 reveals it | Reranking |
| Exact terms don't match | BM25 catches it, dense doesn't | Hybrid search |
| Paraphrased queries don't match | Vocabulary mismatch | HyDE, contextual retrieval |
| Top-k are redundant | Inspect chunk IDs | MMR (λ=0.7) |
| Multi-part query fails | Sub-queries each work alone | Decomposition, agent loop |
| Wrong synthesis after good retrieval | Inspect citations vs answer | Path 06 (evaluation) |
| Answer not in corpus | Manual corpus check | Expand corpus / score floor / search fallback |

## What's *not* a retrieval failure mode

Three things that look like retrieval problems but aren't:

- **The LLM is slow or expensive.** This is an *answer-generation* problem. Cheaper retrieval doesn't help. Optimize the generation step or the agent loop.
- **The user doesn't trust the output.** This is a *citations and transparency* problem. Retrieval got the right chunks; the UI just doesn't show them. Build citation surfaces (Lab 06's pattern).
- **Latency is too high.** Could be retrieval (rerank overhead) or generation (long context). Profile before optimizing. Reranking costs 30-300ms per query on CPU; if your latency budget is 100ms, drop it or move to GPU. If your latency budget is 5 seconds, retrieval is rarely the bottleneck.

These categories often get swept into "RAG is broken" complaints. Diagnose first.

## When to instrument before debugging

The interventions above all assume you can *see* what's happening. In a production system, you need logging:

- The query as received.
- Any rewrites (HyDE, multi-query, decomposition).
- The top-50 chunk_ids per retrieval.
- The rerank scores (if applicable).
- The chunks the agent actually read.
- The final citations.

Without this, you're guessing about which failure mode you're in. Build the instrumentation first; debug second.

Real evaluation tooling (Path 06) gets you there with built-in metrics. Until then, structured JSON logs of the above per query are sufficient.

## See also

- 📖 [What is RAG?](./what-is-rag.md) — the failures RAG fixes and the failures it doesn't (the orientation point).
- 📖 [Chunking and indexing](./chunking-and-indexing.md) — the upstream decisions; many "retrieval" failures trace here.
- 📖 [Retrieval strategies](./retrieval-strategies.md) — the four knobs.
- 📖 [Hybrid search](./hybrid-search.md) — when keyword + dense beats either alone.
- 📖 [Reranking](./reranking.md) — when the right chunk is in top-50 but ranked low.
- 📖 [Contextual retrieval](./contextual-retrieval.md) — when chunks lose context at chunk time.
- 📖 [Query rewriting](./query-rewriting.md) — when the query itself is the problem.
- 🧪 Labs [06](../../labs/06-agentic-rag-from-scratch/), [07](../../labs/07-retrieval-strategies-and-reranking/), [08](../../labs/08-contextual-retrieval-and-query-rewriting/) — the implementation foundation behind everything on this page.

## References

- Anthropic (2024). [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval). Documents one chunk-context failure mode and its fix.
- Barnett, S., Kurniawan, S., Thudumu, S., Brannelly, Z., & Abdelrazek, M. (2024). [*Seven Failure Points When Engineering a Retrieval Augmented Generation System*](https://arxiv.org/abs/2401.05856). A field study of real RAG failure modes; complementary taxonomy.
- Gao, Y. et al. (2024). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997). §5 (challenges and future directions) covers many of these failure modes.
- Karpukhin, V. et al. (2020). [*Dense Passage Retrieval for Open-Domain Question Answering*](https://arxiv.org/abs/2004.04906). EMNLP 2020. The bi-encoder pattern whose precision/recall properties drive most of this taxonomy.
- Pradeep, R. et al. (2023). [*Squeezing Water from a Stone: A Bag of Tricks for Further Improving Cross-Encoder Effectiveness for Reranking*](https://arxiv.org/abs/2208.01230). Practical engineering for the rank 6-50 failure mode.
