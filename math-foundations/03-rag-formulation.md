# RAG formulation as marginalization

> 🧮 Mathematical foundation · ⏱ ~8 min read · Anchor: [`concepts/rag/`](../concepts/rag/)

## The equation

RAG generates an answer $y$ given a query $x$ by marginalizing over a latent retrieved document $z$:

$$
p(y \mid x) \;=\; \sum_{z \in \mathcal{Z}} p(y \mid x, z) \cdot p(z \mid x).
$$

The pieces:

- $p(z \mid x)$ — the **retriever**. Given the query $x$, scores each document $z$ in the corpus $\mathcal{Z}$ by relevance. In practice: embed the query, compute cosine similarity against indexed embeddings, take top-$k$.
- $p(y \mid x, z)$ — the **generator**. Given query + retrieved evidence, produces an answer. This is your LLM call.
- The sum — marginalizing over which document was the "right" one. In production, the sum is approximated: take top-$k$ documents, treat each as evidence, generate one answer per document, then combine (or feed all $k$ to a single generation call).

The full RAG formulation (Lewis et al. 2020) takes this exactly:

$$
p_{\text{RAG}}(y \mid x) \;\approx\; \sum_{z \in \text{top-}k(p(z|x))} p(y \mid x, z) \cdot p(z \mid x).
$$

---

## Mathematical intuition

The marginalization framing is the whole conceptual contribution of RAG over "just generate." Three things worth internalizing.

**The retriever and the generator solve different problems.** $p(z \mid x)$ is a *relevance* problem — does this document address the question? $p(y \mid x, z)$ is a *synthesis* problem — given evidence, what's the answer? Conflating them is the most common architecture mistake: people try to make the generator do retrieval implicitly (in-context search) or make the retriever do synthesis (return answers, not documents).

**Top-$k$ is a budget decision, not a quality decision.** Larger $k$ → higher chance the right document is in the set, but also higher generation cost (more tokens in the prompt) and higher risk of distractors (irrelevant documents that confuse the generator). The sweet spot is usually $k \in [3, 10]$ for production systems; below 3 the recall hit is too sharp; above 10 the "lost in the middle" effect (page 13) dominates.

**The independence assumption is implicit.** The factorization assumes each candidate $z$ is conditionally independent given $x$ — that retrieving document A is unrelated to whether document B was also retrieved. In practice this breaks when the corpus contains duplicates or near-duplicates (one fact in five places). Deduplication at retrieval time, or reranking with diversity, addresses this.

---

## Why it matters for engineers

Four practical implications you'll act on:

1. **Faithfulness is a generator problem; recall is a retriever problem.** If the answer hallucinates facts that aren't in the retrieved evidence, the generator is misbehaving (it's not conditioning on $z$ properly). If the right facts aren't in retrieved $z$ in the first place, the retriever failed. Different fixes — different parts of the equation. The [Faithfulness](../glossary/terms.md) metric in Path 06 measures the first; recall@k measures the second.

2. **Hybrid retrieval is dense plus sparse.** $p(z \mid x)$ doesn't have to be cosine similarity. Modern production retrievers compute a weighted combination of dense (embedding similarity) and sparse (BM25, keyword) scores, then rerank with a cross-encoder. Each stage approximates $p(z \mid x)$ better than the previous.

3. **The generator's prompt determines what $p(y \mid x, z)$ looks like.** "Use only the provided evidence; cite quotes verbatim" sharpens the conditional on $z$. "Combine your knowledge with the provided evidence" weakens it. The choice is engineering, not philosophy.

4. **Agentic RAG replaces the static marginalization with a learned policy over retrieval.** Instead of "retrieve once, generate once," the agent decides *when* to retrieve, *what* to retrieve, and *how many times*. The math becomes a multi-step policy over the action space *{retrieve(query'), generate(answer)}*, formalized in [Page 04](./04-agents-as-policies.md). See [`patterns/08-agentic-rag.md`](../patterns/08-agentic-rag.md).

---

## Where you'll see it in the code

From [Lab 02 — RAG from scratch](../labs/06-agentic-rag-from-scratch/), the marginalization is explicit:

```python
def rag_answer(query: str, corpus_vecs, corpus_texts, k=5) -> str:
    # p(z | x) — retrieve top-k by embedding similarity
    query_vec = embed(query)
    scores = [cosine_similarity(query_vec, dv) for dv in corpus_vecs]
    top_k_idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
    retrieved = [corpus_texts[i] for i in top_k_idx]

    # p(y | x, z) — generate conditioned on query + evidence
    # (the sum is approximated by feeding all k docs in one prompt)
    evidence_block = "\n\n".join(f"[{i+1}] {doc}" for i, doc in enumerate(retrieved))
    prompt = f"""Use only the evidence to answer. Cite as [n].

Evidence:
{evidence_block}

Question: {query}
"""
    return client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}],
        temperature=0,
    ).choices[0].message.content
```

This is the canonical RAG pattern in ~15 lines. Production systems extend it (hybrid retrieval, reranking, per-document generation + voting, citation verification) — but the math is the same.

---

## See also

- 📖 [Canonical RAG](../concepts/rag/what-is-rag.md) — the seven-stage production pipeline that implements this equation.
- 📖 [Agentic RAG pattern](../patterns/08-agentic-rag.md) — where retrieval becomes a tool the agent chooses to call.
- 🧮 [Embeddings and vector similarity](./02-embeddings-vector-similarity.md) — how $p(z \mid x)$ is computed in practice.
- 🧪 [Lab 02 — RAG from scratch](../labs/06-agentic-rag-from-scratch/) — implements this end-to-end.
- 📖 [Glossary — RAG, Agentic RAG, Faithfulness](../glossary/terms.md).

---

## Sources

- Lewis, P., et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS. The paper that established the marginalization formulation; introduced the term "RAG."
- Guu, K., et al. (2020). [*REALM: Retrieval-Augmented Language Model Pre-Training*](https://arxiv.org/abs/2002.08909). ICML. Same era; emphasizes end-to-end training of retriever + generator.
- Gao, Y., et al. (2023). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997). The 2023+ survey that catalogs the field's extensions: HyDE, RAG-Fusion, self-RAG, agentic RAG.
- Asai, A., et al. (2023). [*Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*](https://arxiv.org/abs/2310.11511). ICLR 2024. Formalizes adaptive retrieval — agent decides when retrieving is worth it.
