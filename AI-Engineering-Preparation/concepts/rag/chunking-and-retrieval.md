# Chunking and retrieval

> Concept note. ~9 min. Builds on [RAG end-to-end](./rag-end-to-end.md).

Two upstream choices decide how good a RAG system can be before the model writes a word: how documents are split into chunks, and how chunks are scored against a query. Retrieval can only return what a chunk contains, so these set the ceiling.

## Chunking

A **chunk** is the unit that gets embedded and retrieved. The size is a real tradeoff. Chunks that are too large dilute the embedding — one vector has to represent several topics, and the relevant sentence is buried with unrelated text. Chunks that are too small fragment an idea across several chunks, so no single retrieval carries the whole answer. Common practice is moderate, overlapping windows (a few hundred tokens, with overlap so a sentence split across a boundary still appears whole somewhere), or splitting on natural structure — paragraphs, sections, headings — so a chunk is a coherent unit of meaning. There is no universal size; it depends on the documents and the questions, and it is worth tuning because it caps everything downstream.

## Retrieval: three ways to score

- **Lexical** (sparse) — match on the words themselves, weighted by importance. TF-IDF and BM25 are the classics; the lab's retriever is TF-IDF. Strong on exact terms, names, and codes; blind to paraphrase ("car" will not match "automobile").
- **Dense** (semantic) — embed query and chunks with a model and compare vectors, so meaning matches even when words differ. A **bi-encoder** embeds the two sides independently, which is what makes precomputing chunk vectors possible. Strong on paraphrase; can miss an exact rare token a lexical match would catch.
- **Hybrid** — run both and combine the scores. In practice this is often the strongest, because the two methods fail on different queries: lexical catches the exact identifier, dense catches the paraphrase.

You then take the **top-k** chunks by score. Larger k raises the chance the right chunk is included (recall) but adds noise and cost to the generation step, and pushes material toward the middle of the context; k is a knob, not a constant.

## What to remember

- Chunking sets the ceiling: too large dilutes, too small fragments; overlap and natural boundaries help.
- Lexical matches words, dense matches meaning, hybrid combines them and is often best because they fail differently.
- Top-k trades recall against noise and cost — tune it, do not default it.

## References

- Karpukhin, V., et al. (2020). *Dense Passage Retrieval for Open-Domain QA.* arXiv:2004.04906.
- Robertson, S. & Zaragoza, H. (2009). *The Probabilistic Relevance Framework: BM25 and Beyond.* See [`../../references/references.md`](../../references/references.md).
