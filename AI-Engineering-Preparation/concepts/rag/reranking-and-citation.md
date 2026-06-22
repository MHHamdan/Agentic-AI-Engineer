# Reranking and citation

> Concept note. ~8 min. Builds on [chunking and retrieval](./chunking-and-retrieval.md).

The first retrieval pass is built for speed over a whole corpus, so it is fast but imprecise. Two steps turn its rough shortlist into a trustworthy answer: reranking sharpens *what* the model sees, and citation makes the answer *checkable*.

## Reranking: precise, on a shortlist

First-stage retrieval uses a [bi-encoder](./chunking-and-retrieval.md) or lexical score — cheap, because chunk vectors are precomputed and the query is compared against an [index](../vector-db/), but only approximately right. A **reranker** re-scores the top handful (say, the top 50) with a slower, more accurate model, then keeps the best few for the generator. The usual reranker is a **cross-encoder**: it reads the query and a chunk *together*, so it can judge relevance directly instead of comparing two independent vectors. That joint reading is far more accurate and far too slow to run over a million chunks — which is exactly why it runs only on the shortlist. This two-stage shape, cheap-and-broad then expensive-and-narrow, is the standard retrieval pipeline.

## Citation: grounding you can verify

Retrieval makes grounding *possible*; citation makes it *checkable*. Having the model attribute each claim to the chunk it came from does two things: it lets a reader (or an automated check) verify that the claim is actually supported by the source, and it pushes the model to answer from the retrieved text rather than its parameters. The strong form is **sentence-level support**: every sentence in the answer should be traceable to a retrieved chunk, and any sentence that is not should be flagged or dropped. Recent evaluation work finds that getting models to cite is largely a solved problem; the harder, open part is **coverage** — whether the retrieved set actually contained the facts the question needed. That is a retrieval problem, which loops back to chunking and ranking.

## Failure modes to watch

- **Retrieval miss** — the answer was never in the shortlist; no amount of reranking or citing recovers it.
- **Unsupported sentences** — fluent claims with no backing chunk; the citation check exists to catch these.
- **Lost in the middle** — the supporting chunk is present but placed where the model attends least; ordering and a tight top-k help.

## What to remember

- Two-stage retrieval: cheap recall first, an expensive cross-encoder reranker on the shortlist.
- Citation turns grounding into something verifiable; aim for sentence-level support and flag unsupported claims.
- Citation is largely solved; coverage — did retrieval fetch the needed facts — is the harder, retrieval-side problem.

## References

- Nogueira, R. & Cho, K. (2019). *Passage Re-ranking with BERT.* See [`../../references/references.md`](../../references/references.md).
