# RAG formulation as marginalization

> Mathematical foundation. About 9 minutes to read. Anchor: [`concepts/rag/`](../concepts/rag/).

## Why this matters for agentic AI

RAG is the dominant pattern for grounding LLM output in external knowledge. The marginalization formula tells you exactly what the retriever and generator each contribute, which means failure modes (hallucination vs missed evidence) map to specific parts of the equation. Understand the math and you can localize what is broken when answers go wrong.

## The equation

RAG generates an answer $y$ given a query $x$ by marginalizing over a latent retrieved document $z$:

$$
p(y \mid x) = \sum_{z \in \mathcal{Z}} p(y \mid x, z) \cdot p(z \mid x).
$$

**Symbols:**

- $x$ - the user query.
- $y$ - the generated answer.
- $z$ - a single retrieved document from the corpus.
- $\mathcal{Z}$ - the full corpus.
- $p(z \mid x)$ - the **retriever**. Scores each document by relevance to $x$. In practice: embed the query, compute cosine similarity against indexed embeddings, take top-$k$.
- $p(y \mid x, z)$ - the **generator**. Given query plus retrieved evidence, produces an answer. This is your LLM call.

The full RAG approximation, used in production (Lewis et al., 2020):

$$
p_{\text{RAG}}(y \mid x) \approx \sum_{z \in \text{top-}k\,(p(z \mid x))} p(y \mid x, z) \cdot p(z \mid x).
$$

The sum is truncated to the top-$k$ documents.

## How to read this equation

The probability of producing answer $y$ given query $x$ is a weighted average over all possible retrieved documents. Each document $z$ contributes its own answer probability $p(y \mid x, z)$, weighted by how likely the retriever thought that document was for this query.

In production we never enumerate the full corpus. We take the top-$k$ documents (say, $k = 5$) and either:

1. Feed all $k$ documents to a single LLM call (the prompt stuffs them all into the context); or
2. Generate one answer per document and combine them (rare; expensive).

Approach 1 is what almost every RAG system does. It is a coarse but practical approximation of the marginalization.

## Mathematical intuition

The marginalization framing is the whole conceptual contribution of RAG over "just generate." Three things to internalize.

**The retriever and the generator solve different problems.** $p(z \mid x)$ is a relevance problem: does this document address the question? $p(y \mid x, z)$ is a synthesis problem: given evidence, what is the answer? Conflating them is the most common architecture mistake. People try to make the generator do retrieval implicitly (in-context search) or make the retriever do synthesis (return answers, not documents).

**Top-$k$ is a budget decision, not a quality decision.** Larger $k$ raises the chance the right document is in the set, but also raises generation cost (more tokens in the prompt) and raises the risk of distractors (irrelevant documents that confuse the generator). The sweet spot is usually $k$ between 3 and 10 for production systems. Below 3 the recall hit is too sharp; above 10 the "lost in the middle" effect (see [page 13](./13-context-window-optimization.md)) dominates.

**The independence assumption is implicit.** The factorization assumes each candidate $z$ is conditionally independent given $x$. That retrieving document A is unrelated to whether document B was also retrieved. In practice this breaks when the corpus contains duplicates or near-duplicates (one fact in five places). Deduplication at retrieval time, or reranking with diversity, addresses this.

## Where this appears in agentic systems

- **Faithfulness debugging.** If the answer hallucinates facts that are not in the retrieved evidence, the generator is misbehaving (it is not conditioning on $z$ properly). If the right facts are not in retrieved $z$ in the first place, the retriever failed. Different fixes, different parts of the equation.
- **Hybrid retrieval.** $p(z \mid x)$ does not have to be cosine similarity. Modern production retrievers compute a weighted combination of dense (embedding) and sparse (BM25) scores, then rerank with a cross-encoder. Each stage approximates $p(z \mid x)$ better than the previous.
- **Agentic RAG.** Instead of "retrieve once, generate once," the agent decides when to retrieve, what to retrieve, and how many times. The math becomes a multi-step policy over the action space `{retrieve(query'), generate(answer)}`, formalized in [page 04](./04-agents-as-policies.md). See [`patterns/08-agentic-rag.md`](../patterns/08-agentic-rag.md).
- **The faithfulness metric.** Page 11 defines faithfulness as the fraction of claims in $y$ that are supported by $z$. It measures whether $p(y \mid x, z)$ is actually conditioning on $z$ or making things up.

## Code example

A minimal RAG implementation showing the marginalization explicitly.

```python
import numpy as np
from openai import OpenAI

client = OpenAI()

def embed(text: str) -> np.ndarray:
    r = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(r.data[0].embedding)

def cosine(u: np.ndarray, v: np.ndarray) -> float:
    return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

corpus = [
    "Paris is the capital of France.",
    "The Eiffel Tower was built between 1887 and 1889.",
    "France has 18 administrative regions.",
    "The Loire Valley is famous for its chateaux.",
]
corpus_vecs = [embed(text) for text in corpus]

def rag_answer(query: str, k: int = 2) -> str:
    # p(z | x): rank corpus by similarity to the query.
    q_vec = embed(query)
    scores = [cosine(q_vec, v) for v in corpus_vecs]
    top_k_idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
    retrieved = [corpus[i] for i in top_k_idx]

    # p(y | x, z): generate, conditioning on the retrieved evidence.
    evidence = "\n".join(f"[{i+1}] {doc}" for i, doc in enumerate(retrieved))
    prompt = (
        f"Use only the evidence to answer. Cite as [n].\n\n"
        f"Evidence:\n{evidence}\n\nQuestion: {query}\n"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content

print(rag_answer("What is the capital of France?"))
# Expected output: Paris [1].
```

Production extensions: hybrid retrieval (dense + BM25 + rerank), citation verification, deduplication of near-identical chunks, per-document quotas. The math is the same; the engineering gets richer.

## Common mistakes

- **Returning the documents instead of the answer.** A common RAG bug is the generator just dumping the retrieved text back at the user instead of synthesizing. Usually traces to a weak prompt or too much evidence; reduce $k$ or sharpen the instruction.
- **Setting $k$ by intuition.** Pick $k$ empirically by measuring recall@k on a labeled set. Default to 5 only if you have no data.
- **Trusting cosine similarity as a probability.** $p(z \mid x)$ is a *probability* in the equation; the cosine score is *unnormalized*. Some implementations softmax the scores; others just rank. Both work, but be aware they are different.
- **Forgetting the citation step.** Without making the generator emit citations to specific $z$, you lose the ability to verify faithfulness. Always include a "cite as [n]" instruction.
- **Ignoring the independence assumption.** If your corpus has near-duplicates, top-k will return the same fact five times. Deduplicate at ingest or use maximal marginal relevance (MMR) at retrieval.

## Repo cross-references

- [Lab 06 - Agentic RAG from scratch](../labs/06-agentic-rag-from-scratch/) - implements the full pipeline end-to-end.
- [`concepts/rag/what-is-rag.md`](../concepts/rag/what-is-rag.md) - the engineering view.
- [`concepts/rag/hybrid-search.md`](../concepts/rag/hybrid-search.md) - production-strength $p(z \mid x)$.
- [`concepts/rag/retrieval-failure-modes.md`](../concepts/rag/retrieval-failure-modes.md) - what goes wrong in practice.
- [`patterns/08-agentic-rag.md`](../patterns/08-agentic-rag.md) - the agentic extension.

## Related pages

- [02 - Embeddings and vector similarity](./02-embeddings-vector-similarity.md) - how $p(z \mid x)$ is computed.
- [09 - Memory models](./09-memory-models.md) - memory as a personal RAG store.
- [11 - Evaluation metrics](./11-evaluation-metrics.md) - faithfulness and recall@k for RAG systems.
- [13 - Context-window optimization](./13-context-window-optimization.md) - what to do when the top-k documents will not all fit.
- [Glossary: RAG, Agentic RAG, Faithfulness](../glossary/terms.md) - short definitions.

## References

- Lewis, P., et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. The paper that established the marginalization formulation and introduced the term "RAG."
- Guu, K., et al. (2020). [*REALM: Retrieval-Augmented Language Model Pre-Training*](https://arxiv.org/abs/2002.08909). ICML 2020. Same era; emphasizes end-to-end training of retriever and generator together.
- Gao, Y., et al. (2023). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997). A useful 2023 survey cataloging extensions: HyDE, RAG-Fusion, Self-RAG, agentic RAG.
- Asai, A., et al. (2023). [*Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*](https://arxiv.org/abs/2310.11511). ICLR 2024. Formalizes adaptive retrieval: agent decides when retrieving is worth it.
- Es, S., et al. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). The faithfulness, answer relevance, and context recall metrics referenced on page 11.
