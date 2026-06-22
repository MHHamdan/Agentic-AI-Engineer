# RAG end-to-end

> Concept note. ~9 min. Runnable companion: [`labs/03-rag-and-ann/`](../../labs/03-rag-and-ann/). Diagram: [`diagrams/rag-pipeline.md`](../../diagrams/rag-pipeline.md).

A base model answers from frozen parameters, so it cannot know recent or private facts and will [hallucinate](../llm/hallucination-and-cutoff.md) when it lacks the knowledge. **Retrieval-augmented generation (RAG)** fixes this without retraining: fetch relevant passages at query time and have the model answer from them, with a citation. It is the default way to put a model on top of a body of knowledge that changes or is private.

## The pattern: retrieve, then generate

RAG splits cleanly into two phases that run at different times.

**Indexing (offline, once per corpus change).** Documents are split into **chunks**, each chunk is turned into an embedding, and the embeddings are stored in a [vector index](../vector-db/) for fast similarity search.

**Query (online, per request).** The user's query is embedded, the index returns the most similar chunks, an optional [reranker](./reranking-and-citation.md) sharpens the order, and the model generates an answer **grounded** in those chunks, citing its sources.

```text
indexing:  documents → chunk → embed → vector index
query:     query → embed → retrieve (ANN) → rerank → generate + cite
```

The lab builds the query side end to end — retrieve, ground the answer in the best chunk, cite the source, and abstain when nothing is relevant.

## Why RAG over the alternatives

Compared with [fine-tuning](../llm/fine-tuning-vs-retrieval.md), RAG changes *knowledge* rather than *behavior*: update the documents and the next answer reflects them, with no retraining. It addresses the two structural limits of a frozen model directly — the knowledge cutoff (fetch current data) and hallucination (ground each claim in a retrieved source you can cite). And it keeps knowledge external, so it scales to corpora no context window could hold and stays auditable: every answer points back to a source.

## What can go wrong

RAG moves the problem from "does the model know this?" to "did retrieval find it?". The dominant failure is a **retrieval miss** — the right passage was never fetched, so the model answers from nothing or from the wrong chunk. Others follow from there: the answer drifts from the retrieved context (weak grounding), or the relevant chunk lands in the middle of a long context where the model attends least ([lost in the middle](../llm/context-window.md)). The discipline is to measure retrieval and grounding as separate things, and to make abstention — "I don't have evidence for that" — an acceptable output, as the lab does.

## What to remember

- RAG retrieves relevant chunks at query time and generates a grounded, cited answer from them.
- It changes knowledge, not behavior; it fixes the cutoff and curbs hallucination, and stays current by editing a store.
- Most RAG failures are retrieval failures — measure retrieval and grounding separately, and allow abstention.

## References

- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* arXiv:2005.11401. See [`../../references/references.md`](../../references/references.md).
