# Recipe: Hybrid + reranked RAG

> 🟡 Slow-moving · ⏱ ~7 min · Problem: dense retrieval misses exact-term queries; ranking quality is mediocre.

## Problem

Pure dense (embedding) retrieval smooths away exact terms: product codes, error numbers, rare proper nouns, API names. A query for "error E0423" retrieves semantically-similar-but-wrong chunks because the embedding does not privilege the exact token. Separately, even when the right chunk is retrieved, it may rank below distractors.

## Solution

Two independent improvements that compose:

1. **Hybrid retrieval** - run dense (embedding) and sparse (BM25-style keyword) retrieval, then fuse the rankings with Reciprocal Rank Fusion (RRF).
2. **Reranking** - take the fused top-N and rerank with a cross-encoder that scores each query-document pair directly.

```python
import re
import math
from collections import Counter
import numpy as np
from openai import OpenAI

client = OpenAI()

def embed(texts):
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([d.embedding for d in resp.data])

corpus = [
    "Reset the device by holding the power button for 10 seconds.",
    "Error E0423 indicates a failed firmware checksum; reflash the firmware.",
    "The warranty covers manufacturing defects for 24 months.",
    "Firmware updates are delivered over the air every quarter.",
]
corpus_vecs = embed(corpus)

# --- Sparse retrieval: a compact BM25 ---
def tokenize(s): return re.findall(r"\w+", s.lower())
tokenized = [tokenize(c) for c in corpus]
avgdl = sum(len(t) for t in tokenized) / len(tokenized)
df = Counter(tok for doc in tokenized for tok in set(doc))
N = len(corpus)

def bm25_scores(query, k1=1.5, b=0.75):
    q = tokenize(query)
    scores = []
    for doc in tokenized:
        tf = Counter(doc)
        s = 0.0
        for term in q:
            if term not in tf:
                continue
            idf = math.log(1 + (N - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + k1 * (1 - b + b * len(doc) / avgdl)
            s += idf * (tf[term] * (k1 + 1)) / denom
        scores.append(s)
    return np.array(scores)

# --- Dense retrieval ---
def dense_scores(query):
    q = embed([query])[0]
    return corpus_vecs @ q / (np.linalg.norm(corpus_vecs, axis=1) * np.linalg.norm(q))

# --- Reciprocal Rank Fusion ---
def rrf(score_lists, k=60):
    """Fuse rankings. score_lists: list of per-doc score arrays."""
    fused = np.zeros(N)
    for scores in score_lists:
        ranks = np.argsort(-scores)               # doc indices best-first
        for rank, doc_idx in enumerate(ranks, start=1):
            fused[doc_idx] += 1.0 / (k + rank)
    return fused

# --- Cross-encoder rerank (LLM-as-reranker stand-in) ---
def rerank(query, candidates):
    """Score each (query, doc) pair 0..10. A real system uses a cross-encoder
    model (e.g., Cohere rerank, bge-reranker); here an LLM stands in."""
    scored = []
    for doc in candidates:
        prompt = (
            f"Rate how well this passage answers the query, 0 to 10. "
            f"Reply with only the number.\nQuery: {query}\nPassage: {doc}"
        )
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0, max_tokens=3,
        )
        try:
            scored.append((float(r.choices[0].message.content.strip()), doc))
        except ValueError:
            scored.append((0.0, doc))
    scored.sort(reverse=True)
    return [doc for _, doc in scored]

def hybrid_reranked_retrieve(query, fuse_n=4, final_k=2):
    fused = rrf([dense_scores(query), bm25_scores(query)])
    top_n = [corpus[i] for i in np.argsort(-fused)[:fuse_n]]
    return rerank(query, top_n)[:final_k]

print(hybrid_reranked_retrieve("error E0423"))
# Expected: the firmware-checksum chunk ranks first - BM25 catches the exact code
# that dense retrieval alone would blur.
```

## Why each piece is there

- **BM25 catches exact terms** that embeddings blur. "E0423" is a near-meaningless token to an embedding model but a strong signal to BM25.
- **RRF fuses without tuning weights.** It combines rankings (not raw scores), so you do not need to calibrate dense scores against BM25 scores, which live on different scales. The constant $k=60$ is the common default.
- **Reranking fixes ordering.** The fused list has good recall but imperfect ranking; the cross-encoder, which sees the query and document together, reorders for precision at the top. In production use a real cross-encoder (Cohere rerank, `bge-reranker`), not an LLM, for latency and cost.

## How to measure it

Hybrid and reranking should move NDCG@k and MRR up (better ranking) and recall@k up (BM25 finds chunks dense missed). Measure all three against your eval set; if reranking helps NDCG but not recall, it is doing its job (reordering, not retrieving). See [`math-foundations/14-retrieval-ranking-metrics.md`](../../math-foundations/14-retrieval-ranking-metrics.md).

## References

- Robertson, S., and Zaragoza, H. (2009). [*The Probabilistic Relevance Framework: BM25 and Beyond*](https://www.nowpublishers.com/article/Details/INR-019). The BM25 scoring function.
- Cormack, G. V., Clarke, C. L. A., and Buettcher, S. (2009). [*Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods*](https://dl.acm.org/doi/10.1145/1571941.1572114). SIGIR. The RRF method.
- [`concepts/rag/hybrid-search.md`](../../concepts/rag/hybrid-search.md) and [`concepts/rag/reranking.md`](../../concepts/rag/reranking.md) - conceptual background.
- Thakur, N., et al. (2021). [*BEIR*](https://arxiv.org/abs/2104.08663). Evidence that reranking and late-interaction top zero-shot retrieval.
