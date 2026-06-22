# Lab 03: RAG and ANN

> 🟢 Foundational · ⏱ ~70–90 min · 📚 Path 03 (Retrieval & memory)

## 🎯 Goal

Build the two halves of retrieval from scratch — a RAG pipeline that answers from grounded, cited context, and the approximate-nearest-neighbor index that makes retrieval scale — so the rest of the retrieval stack rests on something you have seen work.

By the end you should be able to:

- Build a retrieve → ground → cite → abstain pipeline and explain why each step matters.
- Explain why retrieval grounds answers and reduces hallucination.
- Implement an IVF approximate index and measure recall vs. vectors scanned.
- Reason about the recall / latency / memory tradeoff a vector database tunes.

## 🛠 Modules

| File | What it does |
|---|---|
| `rag.py` | minimal RAG: TF-IDF retrieval, grounded extractive answer, citation, abstention (`Retriever`, `--self-test`, `--query`) |
| `ann.py` | exact vs. IVF approximate nearest-neighbor search and the recall/scan tradeoff (`build_ivf`, `ivf_search`, `evaluate`, `--self-test`, `--demo`) |

## What the numbers say

- RAG: distinctive queries ground to the correct source and cite it; an out-of-corpus query scores ~0 and **abstains** rather than inventing an answer.
- IVF: probing 1 of 12 clusters already gives **0.79 recall@5 while scanning 13%** of the vectors; probing all clusters reduces to exact search (recall 1.00, 100% scanned).

## Design choices and tradeoffs

- **Grounding and abstention.** The answer is the retrieved chunk, not a free generation, and a similarity floor turns "nothing relevant" into a refusal — the two behaviors that separate RAG from a search box.
- **Lexical retrieval (TF-IDF).** IDF down-weights words common across the corpus so distinctive terms drive the match. It is the lexical half of hybrid search; dense embeddings are the other half.
- **IVF as clustering.** Searching only the nearest clusters trades a little recall for a large reduction in comparisons; `nprobe` is the knob that moves along that curve.

## Common gotchas

- **Lexical retrieval misses paraphrase.** "indexed" will not match "index" without stemming; this is exactly why dense or hybrid retrieval exists.
- **Recall is silent when it fails.** An ANN index that misses the true neighbor returns a plausible wrong one; measure recall against exact search, do not assume it.
- **Chunking decides the ceiling.** Retrieval can only return what a chunk contains; chunk too large and you bury the answer, too small and you fragment it.

## 🧮 Going deeper

- 📐 [math-foundations/03](../../math-foundations/03-nearest-neighbor-search.md) — exact vs. approximate search and the recall/latency tradeoff.
- 📖 [concepts/rag/rag-end-to-end.md](../../concepts/rag/rag-end-to-end.md) · [concepts/vector-db/similarity-and-ann.md](../../concepts/vector-db/similarity-and-ann.md) · [hnsw.md](../../concepts/vector-db/hnsw.md).

## References

- Lewis, P., et al. (2020). *Retrieval-Augmented Generation.* arXiv:2005.11401.
- Robertson, S. & Zaragoza, H. (2009). *BM25 / the probabilistic relevance framework.*
- Malkov, Yu. & Yashunin, D. (2016). *HNSW.* arXiv:1603.09320.
- Johnson, J., et al. (2017). *Billion-scale similarity search (FAISS).* arXiv:1702.08734.
