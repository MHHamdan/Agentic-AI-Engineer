# Embeddings and vector similarity

> 🧮 Mathematical foundation · ⏱ ~7 min read · Anchor: [`concepts/rag/`](../concepts/rag/)

## The equation

An embedding model maps text $x$ to a dense vector $\mathbf{u} \in \mathbb{R}^d$:

$$
\mathbf{u} \;=\; f_\phi(x), \qquad \mathbf{u} \in \mathbb{R}^d.
$$

Where $f_\phi$ is the embedding model (parameters $\phi$) and $d$ is the embedding dimension — typically 768, 1024, 1536, or 3072 in production models.

**Cosine similarity** between two embeddings:

$$
\text{cos}(\mathbf{u}, \mathbf{v}) \;=\; \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \cdot \|\mathbf{v}\|}.
$$

Output range: $[-1, 1]$. Identical direction → $1$; orthogonal → $0$; opposite → $-1$. In practice, embedded text rarely scores below $0$ (semantic spaces are dominated by positive correlations).

For unit-norm embeddings, cosine similarity reduces to a dot product. Most production embedding APIs return pre-normalized vectors, so the divisor is $1$.

---

## Mathematical intuition

The training objective for modern embedding models is **contrastive**: pull semantically similar pairs together in vector space; push dissimilar pairs apart. After training, geometric distance in $\mathbb{R}^d$ approximates semantic distance — close vectors mean similar meanings.

Two properties worth internalizing:

**The embedding is a lossy projection.** A 1000-token document becomes a single 1024-dimensional vector. Information is necessarily discarded. The vector preserves the *gist* (topic, sentiment, key entities) but loses *details* (exact wording, specific numbers). This is why retrieval can return a document about the right topic but the wrong specific claim — the embedding never saw the difference.

**Cosine vs Euclidean distance.** For unit-norm vectors, the two are monotonically related: ranking by cosine ≡ ranking by negative Euclidean. The choice is conventional. Cosine is more interpretable (1 = same direction; 0 = orthogonal) and is what every vector store defaults to for text embeddings.

**Dimension matters less than you'd expect.** A well-trained 768-dim model often beats a poorly-trained 3072-dim model. Bigger $d$ helps at the margin once $d$ is "enough" (~768+ for English text). Cost scales linearly with $d$: storage, retrieval latency, and similarity computation all grow with the dimension.

---

## Why it matters for engineers

Four practical implications:

1. **Retrieval quality is upstream of generation quality.** If the embedding model can't tell "Q3 revenue" from "Q4 revenue" apart in vector space, no amount of LLM reasoning at the generation step recovers the distinction. Choose the embedding model first; tune the generator second.

2. **Embedding-space drift is measurable.** Track the distribution of query embeddings over time. If new queries land in regions far from your training data's coverage, retrieval will degrade silently. This is covered in [Path 06 Lab 23](../labs/23-embedding-space-drift-detection/).

3. **Domain-specific terminology is the canonical failure mode.** Generic embedding models (OpenAI, Cohere) cluster financial jargon, medical terminology, legal phrasing imperfectly. For domain-heavy retrieval, fine-tuning the embedding model on in-domain pairs is often higher-ROI than fine-tuning the LLM.

4. **Hybrid retrieval beats pure dense for many workloads.** BM25 (sparse, keyword-based) catches exact-match terms that dense embeddings smooth over (product codes, error message numbers, proper nouns). The 2026 production default is **hybrid search** — both, reranked.

---

## Where you'll see it in the code

From [Path 02 Lab 02](../labs/06-agentic-rag-from-scratch/), the embedding and similarity steps are explicit:

```python
import numpy as np
from openai import OpenAI

client = OpenAI()

def embed(text: str) -> np.ndarray:
    """f_phi(x) — produces a unit-norm 1536-dim vector."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return np.array(response.data[0].embedding)

def cosine_similarity(u: np.ndarray, v: np.ndarray) -> float:
    """cos(u, v) — for pre-normalized vectors, this is just u · v."""
    return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

# Retrieval: rank corpus by similarity to query
query_vec = embed(query)
scores = [cosine_similarity(query_vec, doc_vec) for doc_vec in corpus_vecs]
top_k = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
```

In production, the loop is replaced by a vector store (FAISS, Chroma, Pinecone, Qdrant, Weaviate) that indexes the corpus and serves nearest-neighbor queries in sublinear time.

---

## See also

- 📖 [Canonical RAG](../concepts/rag/what-is-rag.md) — where the embedding step sits in the seven-stage pipeline.
- 🧮 [RAG formulation as marginalization](./03-rag-formulation.md) — how retrieved chunks combine with the LLM to produce the final answer.
- 🧪 [Lab 02 — RAG from scratch](../labs/06-agentic-rag-from-scratch/) — implements this end-to-end.
- 📖 [Glossary — Embedding, Vector store, Hybrid search, BM25](../glossary/terms.md).

---

## Sources

- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). [*Efficient Estimation of Word Representations in Vector Space*](https://arxiv.org/abs/1301.3781). The word2vec paper — origin of dense distributional embeddings in NLP.
- Reimers, N., & Gurevych, I. (2019). [*Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*](https://arxiv.org/abs/1908.10084). EMNLP. Established the contrastive framework that production embedding models still use.
- Karpukhin, V., et al. (2020). [*Dense Passage Retrieval for Open-Domain Question Answering*](https://arxiv.org/abs/2004.04906). EMNLP. The DPR architecture — formalized dual-encoder retrieval at scale.
- Muennighoff, N., et al. (2023). [*MTEB: Massive Text Embedding Benchmark*](https://arxiv.org/abs/2210.07316). The canonical 2023+ benchmark for comparing embedding models across tasks.
