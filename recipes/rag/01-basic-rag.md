# Recipe: Basic RAG

> 🟡 Slow-moving · ⏱ ~5 min · Problem: get a working retrieve-then-generate loop running and measurable.

## Problem

You have a corpus and questions. You want a baseline RAG loop you can measure and improve, without standing up infrastructure.

## Solution

The canonical pipeline: embed the corpus once, embed the query, retrieve top-k by cosine similarity, stuff the chunks into the prompt, generate with a citation instruction.

```python
import numpy as np
from openai import OpenAI

client = OpenAI()

def embed(texts: list[str]) -> np.ndarray:
    """Batch-embed. Returns (n, d) array."""
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([d.embedding for d in resp.data])

# --- Index time (do once) ---
corpus = [
    "The mitochondrion is the powerhouse of the cell.",
    "Photosynthesis converts light energy into chemical energy in plants.",
    "The Krebs cycle produces ATP in aerobic respiration.",
    "Chlorophyll absorbs light most efficiently in the blue and red wavelengths.",
]
corpus_vecs = embed(corpus)                      # (4, 1536)

# --- Query time ---
def retrieve(query: str, k: int = 2) -> list[str]:
    q = embed([query])[0]                        # (1536,)
    # Cosine similarity; embeddings are pre-normalized so dot product suffices.
    sims = corpus_vecs @ q / (
        np.linalg.norm(corpus_vecs, axis=1) * np.linalg.norm(q)
    )
    top_k = np.argsort(-sims)[:k]
    return [corpus[i] for i in top_k]

def answer(query: str, k: int = 2) -> str:
    chunks = retrieve(query, k)
    evidence = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(chunks))
    prompt = (
        f"Answer using only the evidence. Cite sources as [n]. "
        f"If the evidence does not contain the answer, say so.\n\n"
        f"Evidence:\n{evidence}\n\nQuestion: {query}"
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content

print(answer("How do plants capture light?"))
# Expected: an answer grounded in the photosynthesis / chlorophyll chunks, with [n] citations.
```

## Why each piece is there

- **Pre-normalized embeddings** let you use the dot product directly; the explicit norm in the code is defensive in case your embedding source is not normalized.
- **The citation instruction** is load-bearing: without "cite as [n]" you lose the ability to check faithfulness later.
- **The abstention instruction** ("if the evidence does not contain the answer, say so") is what makes off-corpus queries fail safely instead of hallucinating.
- **temperature=0** makes the baseline reproducible so you can attribute changes to the pipeline, not to sampling noise.

## How to measure it

This baseline is only useful if you measure it. Build a small eval set and compute recall@k and faithfulness. See [`concepts/evaluation/rag-evaluation-framework.md`](../../concepts/evaluation/rag-evaluation-framework.md) for the framework and [`math-foundations/14-retrieval-ranking-metrics.md`](../../math-foundations/14-retrieval-ranking-metrics.md) for the metric code.

## When this is not enough

- Exact-term queries (codes, names) miss -> [Recipe 02: Hybrid + reranked](./02-hybrid-reranked-rag.md).
- Retrieval returns irrelevant chunks the model trusts -> [Recipe 03: Corrective RAG](./03-corrective-rag.md).
- Production scale -> swap the in-memory index for a vector store; the `retrieve` interface stays the same.

## References

- Lewis, P., et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS. The canonical formulation.
- [`concepts/rag/what-is-rag.md`](../../concepts/rag/what-is-rag.md) - the conceptual background.
- [`math-foundations/03-rag-formulation.md`](../../math-foundations/03-rag-formulation.md) - the marginalization math.
