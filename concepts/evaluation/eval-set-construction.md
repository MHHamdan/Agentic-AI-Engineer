# Eval set construction

> 🟢 Stable · ⏱ ~10 min read · 🏷 rag, evaluation, foundation

## TL;DR

The single highest-leverage thing you can do for RAG evaluation is **build a small honest eval set by hand**. 30 carefully curated questions beat 1,000 synthetic ones for early-stage work. Every metric in the next two pages — recall@k, MRR, faithfulness — is computed against this set. Garbage in, garbage out.

This page covers what an eval set is, what each entry needs, how to source the queries, why hand-curation beats synthetic generation early on, and the failure modes to watch for. It's the foundation [Lab 09](../../labs/09-evaluating-agentic-rag/) stands on.

---

## What an eval set is

An eval set is a list of queries with annotations. Each entry typically has:

```json
{
  "query": "What does the document on tool design say about errors?",
  "expected_doc": "02-tool-design.md",
  "expected_chunks": ["02-tool-design.md:1", "02-tool-design.md:2"],
  "reference_answer": "Tool errors should use a structured discriminated...",
  "category": "referential",
  "failure_label": null
}
```

The fields:

- **`query`** — what a user might ask. Exactly as they'd phrase it. No cleanup.
- **`expected_doc`** — the source document that contains the answer. Use `null` if the corpus shouldn't be able to answer this query (off-corpus test).
- **`expected_chunks`** — which chunk(s) the retriever should surface. Optional but powerful for retrieval metrics; needs to be re-annotated when the chunker changes.
- **`reference_answer`** — a human-written reference answer. Optional. Used for correctness metrics; if you don't have it, you can only score groundedness.
- **`category`** — what *kind* of query this is. Lets you slice metrics by query type. Common categories: `lexical`, `paraphrase`, `referential`, `compound`, `off-corpus`.
- **`failure_label`** — if this query is *known to fail* under specific conditions, label which [failure mode](../rag/retrieval-failure-modes.md) it tests. Useful for regression testing.

Different teams add different fields (timestamp, author, source, expected_refusal, etc.). The shape doesn't matter; the discipline of *labelling* matters.

## Why hand-curation beats synthetic generation

There's an obvious temptation: ask an LLM to generate 1,000 question/answer pairs from your corpus. RAGAS, DeepEval, and several other frameworks support this. It feels efficient.

**Don't do this first.** Here's why.

### Synthetic queries reflect the *generator's* assumptions, not your users'

An LLM asked to "generate questions answerable from this document" tends to produce:

- Questions that match the document's vocabulary closely (so retrieval looks artificially easy).
- Questions of the form "What is X?" or "Explain Y" (so the surface variety is low).
- Questions whose answers are extractive single chunks (so the system never gets credit for multi-chunk synthesis).
- Questions phrased with formal grammar (so the system never sees typos, fragments, or vernacular).

Your real users do none of those things. Their queries are messy, paraphrased, fragmentary, occasionally typo'd, often compound, sometimes off-topic. A synthetic eval set is a *biased sample* of the query distribution your system actually faces.

### Hand-curated queries catch the failure modes you didn't anticipate

When you write queries yourself — sitting in front of your corpus, trying to think like a user — you naturally produce:

- The compound questions you'd ask if you were impatient.
- The paraphrases that come out when you don't remember the exact terms.
- The vague queries that come from not knowing what's in the corpus.
- The "trick" questions where the obvious chunk isn't actually the right one.

These are exactly the queries that surface [failure modes 1, 4, 6, and 8](../rag/retrieval-failure-modes.md). They're the failures that matter.

### The numbers favor hand-curation early on

A rough heuristic: 30 hand-curated queries that cover your failure modes deliberately are worth ~300 synthetic queries that all look the same. As your system matures and you've fixed the obvious cases, the marginal value of more queries diminishes — but the value of *diverse* queries doesn't.

Most teams converge on a hybrid: hand-curate the first 30-50 queries (the *seed set*), use synthetic generation to expand later when you have specific gaps to fill. Path 02 stops at the seed-set stage.

## Sourcing queries

Where do you get the 30-50 queries? Five patterns work:

1. **Sit in front of your corpus and ask yourself questions.** What would a new hire ask? What would a customer? What would a skeptic? This catches the obvious queries.
2. **Mine your existing support tickets, search logs, or analytics.** If you have prior product data, the real questions are in there. Strip out PII before using them.
3. **Use the failure-modes taxonomy as a checklist.** For each of the [eight failure modes](../rag/retrieval-failure-modes.md), write 2-4 queries that test it. This guarantees coverage breadth.
4. **Ask domain experts to write 5-10 queries each.** They know the corner cases that engineers don't.
5. **Walk the corpus structurally.** For each document, write 1-2 queries that target it. Then write 1-2 queries that target *only* that document but use vocabulary the document doesn't contain (the paraphrase test).

A useful target distribution for a first eval set:

| Category | Count | What it tests |
|---|---|---|
| Direct lexical match | ~8 | Easy baseline; retrievers should ace these |
| Paraphrased | ~6 | Vocabulary-shift robustness |
| Referential | ~5 | Chunks lacking standalone context |
| Compound (multi-part) | ~3 | Decomposition / agent loop |
| Off-corpus | ~2-3 | Refusal / empty-result behavior |
| Total | ~25-30 | The seed set |

## Annotating expected chunks

For retrieval metrics, you need to know *which chunks* count as "relevant" for each query. Three approaches:

1. **Strict — exact chunk IDs.** Annotate `expected_chunks: ["02-tool-design.md:1"]`. Computes the cleanest metrics. Brittle: when the chunker changes (different size, different overlap), every chunk ID shifts and annotations break.
2. **Loose — expected document only.** Annotate `expected_doc: "02-tool-design.md"`, accept any chunk from that document as relevant. More robust to chunker changes; loses the "which specific chunk" information.
3. **Both.** Store both fields. Compute metrics either way; use the strict version when you trust your chunker, the loose version when you don't.

Lab 09 uses (3). Real production teams often pin chunks once a chunker is stable.

## The reference answer question

If your eval set has `reference_answer`, you can compute *correctness* — does the system's answer match the reference? This sounds appealing and is mostly a trap. Reasons:

- **There's rarely one right answer.** A query like "How does the agent loop work?" has many valid answers of differing levels of detail.
- **Exact-string matching against a reference is too brittle** (any rephrasing fails).
- **LLM-as-judge comparison against a reference** works but is expensive and noisy.
- **The reference itself can be wrong**, biased by what the author thought the answer was.

The pragmatic stance: write reference answers for a *subset* (10-30%) of queries where correctness genuinely matters and you can defend the reference. Use them sparingly. For the rest, score groundedness (does the answer follow from the chunks?) which doesn't need a reference.

Lab 09 ships reference answers for 5 of its 30 queries — the ones where there's a clear textbook answer in the corpus.

## Failure labels — making the eval set diagnostic

If your eval set just gives you one mean score per metric, you've thrown away most of its value. Slicing by category and failure label is where the diagnostic power comes from.

Tag each query with the failure mode it's designed to test (if any):

```json
{
  "query": "what does the document about chunking say about overlap",
  "category": "referential",
  "failure_label": "FM4_paraphrase"
}
```

Now your harness can answer questions like:

- "We added contextual retrieval. Did it improve the `FM4_paraphrase` queries specifically, or just the easy ones?"
- "Our recall dropped from 0.92 to 0.87. Which failure-mode bucket regressed?"
- "Refusal quality on `off-corpus` queries is 0.4 — the system isn't refusing when it should."

Without these labels, you only know the system got worse; with them, you know *where*.

## Maintaining the eval set over time

Eval sets aren't write-once artifacts. They evolve:

- **Add queries when you find new failure modes** in production. The first time you see a user query the system fumbles in a new way, add it to the eval set. The set becomes a living record of the failures you've encountered.
- **Re-annotate when the corpus changes.** New documents added? Re-check which `expected_doc` annotations are still right. Documents removed? Some queries may have become off-corpus.
- **Re-annotate when the chunker changes.** Chunk IDs shift; `expected_chunks` need to update. This is why pinning the chunker once it's stable matters.
- **Version the eval set.** Tag releases (`eval_set_v1.0.jsonl`) so you can rerun old experiments and reproduce metrics. Especially important for regression testing.
- **Don't grow it indefinitely.** Past ~100-200 queries, the maintenance cost dominates. Better to deliberately curate than to accrete.

## Common pitfalls

Three you'll see in real teams:

### "We tested it on the queries the team uses."

This is the most common mistake. You and your colleagues phrase queries using *your* vocabulary, which matches the corpus's vocabulary, which makes retrieval look great. Real users use different vocabulary. The eval set should over-represent users-unlike-you, not be dominated by users-like-you.

### "The eval set is just our happy-path queries."

If every query in the eval set has a clear right answer in the corpus, your evaluation will never catch failure modes 6 (compound) and 8 (off-corpus). The set needs *deliberate* coverage of cases the system *shouldn't* be able to answer.

### "We ran the eval; the scores are fine."

Aggregate scores hide failure modes. Always slice by category. A `lexical` recall of 0.95 alongside a `referential` recall of 0.4 is a *much* more useful signal than the overall recall of 0.78 the average gives you.

## What "good enough" looks like

For Path 02's purposes, a good first eval set has:

- 25-50 queries (manageable to maintain by hand).
- Coverage across categories (lexical, paraphrase, referential, compound, off-corpus).
- At least 2-3 off-corpus queries (refusal/empty behavior).
- `expected_doc` annotated for every on-corpus query.
- `expected_chunks` annotated for queries where you have a stable chunker.
- `failure_label` tags for queries that test specific failure modes.
- `reference_answer` for the 10-30% where it's clearly defensible.
- A `README.md` next to the eval set explaining how it was constructed and what categories mean.

Lab 09 ships an eval set that meets all of these for the Lab 06 corpus.

## What's *not* in this batch

Three eval-set practices Path 02 doesn't cover, deferred to Path 06:

- **Synthetic eval generation** (RAGAS's `TestsetGenerator`, DeepEval's `Synthesizer`). Useful once the seed set is mature and you have specific gaps.
- **Continuous evaluation** — re-annotating production traffic into eval entries on an ongoing basis. Standard practice in mature RAG systems but operationally heavy.
- **Multi-turn / conversational eval sets** — queries with chat history. Needs conversational RAG (future batch) first.

## See also

- 📖 [What is RAG evaluation?](./what-is-rag-evaluation.md) — the orientation that motivated this page.
- 📖 [Retrieval metrics](./retrieval-metrics.md) — what gets computed against the eval set's retrieval annotations.
- 📖 [Answer quality metrics](./answer-quality-metrics.md) — what gets computed against the eval set's answers.
- 📖 [Retrieval failure modes](../rag/retrieval-failure-modes.md) — the taxonomy that drives category and failure_label tagging.
- 🧪 [Lab 09](../../labs/09-evaluating-agentic-rag/) — the eval set you'll use lives here as `eval_set.jsonl`.

## References

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). [*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/). Chapter 8 covers evaluation set construction in classical IR; the principles transfer cleanly.
- Thakur, N. et al. (2021). [*BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*](https://arxiv.org/abs/2104.08663). NeurIPS 2021. The benchmark's curation methodology is worth reading — it's careful about exactly the failure modes synthetic eval sets miss.
- Bajaj, P. et al. (2018). [*MS MARCO: A Human Generated MAchine Reading COmprehension Dataset*](https://arxiv.org/abs/1611.09268). The reference benchmark for retrieval; built from real Bing query logs rather than synthetic generation.
- Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). RAGAS's reference-free eval approach is reasonable in production but Path 02 makes the case for hand-curation first.
- Saad-Falcon, J., Khattab, O., Potts, C., & Zaharia, M. (2023). [*ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems*](https://arxiv.org/abs/2311.09476). NAACL 2024. Argues for synthetic-question generation with human-validated subsets; honest about the limits.
