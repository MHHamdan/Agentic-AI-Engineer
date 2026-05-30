# Embeddings and vector similarity

> Mathematical foundation. About 8 minutes to read. Anchor: [`concepts/rag/`](../concepts/rag/).

## Why this matters for agentic AI

RAG, semantic search, memory retrieval, and most "similar items" features all reduce to one operation: comparing two vectors. Get the embedding model wrong or score the similarity badly and the LLM downstream cannot recover what was missed. The math is small; the engineering consequences are not.

## The equation

An embedding model maps text $x$ to a dense vector $\mathbf{u}$ in $\mathbb{R}^d$:

$$
\mathbf{u} = f_\phi(x), \qquad \mathbf{u} \in \mathbb{R}^d.
$$

Where $f_\phi$ is the embedding model (parameters $\phi$) and $d$ is the embedding dimension (typically 384, 768, 1024, 1536, or 3072 in production models).

Cosine similarity between two embeddings:

$$
\text{sim}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\lVert \mathbf{u} \rVert \, \lVert \mathbf{v} \rVert}.
$$

**Symbols:**

- $f_\phi$ - the embedding model (a neural network).
- $\mathbf{u}, \mathbf{v}$ - dense vectors (bold to mark them as vectors, not scalars).
- $\mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^d u_i v_i$ - the dot product.
- $\lVert \mathbf{u} \rVert = \sqrt{\sum_i u_i^2}$ - the Euclidean (L2) norm.
- $d$ - the embedding dimension.

Output range of $\text{sim}$ is $[-1, 1]$. Identical direction gives $1$; orthogonal gives $0$; opposite gives $-1$. In practice, embedded text rarely scores below $0$ because semantic spaces are dominated by positive correlations.

## How to read this equation

The numerator measures alignment: how much the two vectors point in the same direction in $\mathbb{R}^d$. The denominator normalizes by their magnitudes so that two long vectors do not automatically score higher than two short ones. The result is an angle-only measure.

For unit-norm embeddings (where $\lVert \mathbf{u} \rVert = \lVert \mathbf{v} \rVert = 1$), cosine similarity reduces to a plain dot product. Most production embedding APIs return pre-normalized vectors, which is why you will see code that uses `np.dot` without the denominator.

## Mathematical intuition

The training objective for modern embedding models is **contrastive**: pull semantically similar pairs together in vector space; push dissimilar pairs apart. After training, geometric distance in $\mathbb{R}^d$ approximates semantic distance. Close vectors mean similar meanings.

Three properties worth internalizing:

**The embedding is a lossy projection.** A 1000-token document becomes a single 1024-dimensional vector. Information is necessarily discarded. The vector preserves the gist (topic, sentiment, key entities) but loses details (exact wording, specific numbers). This is why retrieval can return a document about the right topic but the wrong specific claim. The embedding never saw the difference.

**Cosine vs Euclidean distance.** For unit-norm vectors, the two are monotonically related. Ranking by cosine is the same as ranking by negative Euclidean distance. The choice between them is conventional. Cosine is more interpretable (1 means same direction; 0 means orthogonal) and is what every vector store defaults to for text embeddings.

**Dimension matters less than you would expect.** A well-trained 768-dim model often beats a poorly-trained 3072-dim model. Bigger $d$ helps at the margin once $d$ is large enough (around 768 or more for English text). Cost scales linearly with $d$: storage, retrieval latency, and similarity computation all grow with the dimension.

## Where this appears in agentic systems

- **RAG retrieval.** $p(z \mid x)$ in [page 03](./03-rag-formulation.md) is implemented as cosine similarity ranking.
- **Memory retrieval.** Agent long-term memory ([page 09](./09-memory-models.md)) uses the same operation over a per-user memory store.
- **Embedding-space drift detection.** Tracking the distribution of query embeddings over time catches retrieval degradation before answer quality drops.
- **Domain-specific terminology.** Generic embedding models cluster financial jargon, medical terminology, or legal phrasing imperfectly. For domain-heavy retrieval, fine-tuning the embedding model on in-domain pairs is often higher-ROI than fine-tuning the LLM.
- **Hybrid retrieval.** Cosine similarity (dense) gets combined with BM25 (sparse, keyword-based) for queries mixing semantic concepts with exact-match terms like product codes or error message numbers.

## Code example

Embed two strings and rank a small corpus by similarity to a query.

```python
import numpy as np
from openai import OpenAI

client = OpenAI()

def embed(text: str) -> np.ndarray:
    """f_phi(x). Returns a 1536-dim vector, pre-normalized by the API."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return np.array(response.data[0].embedding)

def cosine_similarity(u: np.ndarray, v: np.ndarray) -> float:
    """For pre-normalized vectors this is just the dot product."""
    return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

corpus = [
    "Vector databases store embeddings for nearest-neighbor search.",
    "The capital of France is Paris.",
    "Cosine similarity measures the angle between two vectors.",
    "Roast chicken at 425 degrees Fahrenheit for one hour.",
]
query = "How does semantic search work?"

corpus_vecs = [embed(text) for text in corpus]
query_vec = embed(query)

scores = [cosine_similarity(query_vec, v) for v in corpus_vecs]
ranked = sorted(zip(scores, corpus), reverse=True)

for score, text in ranked:
    print(f"{score:.3f}  {text}")
```

The first two corpus entries should score highest; the chicken recipe should score lowest. If the ranking is wrong on real data, the failure is upstream: either the embedding model is misaligned with your domain, or the chunks are too long or too short to carry meaning cleanly.

## Common mistakes

- **Comparing embeddings from different models.** A vector from `text-embedding-3-small` and a vector from `text-embedding-3-large` live in different spaces. Their cosine similarity is meaningless. Always check that all vectors in a similarity comparison came from the same model and version.
- **Forgetting to normalize.** If your embedding source returns un-normalized vectors, computing the dot product directly will rank longer documents higher just because they have larger magnitudes. Either normalize at write time or use the full cosine formula.
- **Chunking too large.** A 4000-token chunk has too much semantic content for a single vector to represent well. Aim for chunks in the 200 to 800 token range for retrieval-grade embedding.
- **Mixing strict-string-match queries with embedding retrieval.** "Order #12345" or "error code E0023" needs BM25 (sparse) or hybrid retrieval. Cosine over dense embeddings smooths these distinctions away.

## Repo cross-references

- [Lab 06 - Agentic RAG from scratch](../labs/06-agentic-rag-from-scratch/) - implements the embed + index + retrieve pipeline.
- [Lab 23 - Embedding-space drift detection](../labs/23-embedding-space-drift-detection/) - monitors query and result embedding distributions over time.
- [`concepts/rag/what-is-rag.md`](../concepts/rag/what-is-rag.md) - the engineering view of where embeddings sit in a RAG pipeline.
- [`concepts/rag/hybrid-search.md`](../concepts/rag/hybrid-search.md) - the dense + sparse combination.

## Related pages

- [03 - RAG formulation as marginalization](./03-rag-formulation.md) - how the retrieval step combines with generation.
- [09 - Memory models](./09-memory-models.md) - long-term memory as a per-user RAG store.
- [13 - Context-window optimization](./13-context-window-optimization.md) - how retrieved chunks fit into a bounded context.
- [Glossary: Embedding, Vector store, Hybrid search, BM25](../glossary/terms.md) - short definitions.

## References

- Mikolov, T., Chen, K., Corrado, G., and Dean, J. (2013). [*Efficient Estimation of Word Representations in Vector Space*](https://arxiv.org/abs/1301.3781). The word2vec paper. Origin of dense distributional embeddings in NLP.
- Reimers, N., and Gurevych, I. (2019). [*Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*](https://arxiv.org/abs/1908.10084). EMNLP. Established the contrastive framework that production embedding models still use.
- Karpukhin, V., et al. (2020). [*Dense Passage Retrieval for Open-Domain Question Answering*](https://arxiv.org/abs/2004.04906). EMNLP. The DPR architecture. Formalized dual-encoder retrieval at scale.
- Muennighoff, N., et al. (2023). [*MTEB: Massive Text Embedding Benchmark*](https://arxiv.org/abs/2210.07316). The canonical benchmark for comparing embedding models across tasks. Useful for picking a model.
- OpenAI. [*Embeddings API*](https://platform.openai.com/docs/guides/embeddings). Official documentation for `text-embedding-3-small` and related models used in the code example.
