# Lab 07: Retrieval strategies and reranking

> 🟡 Intermediate · ⏱ ~110–140 min · 📚 Same corpus as Lab 06; better retrieval

## 🎯 Goal

Extend Lab 06's `search_corpus` to a production-grade retrieval pipeline: BM25 alongside dense retrieval, Reciprocal Rank Fusion to combine them, MMR to diversify, and a cross-encoder reranker to sharpen the top of the ranking. Measure each upgrade against the Lab 06 baseline using the same corpus and the same queries Lab 06 had trouble with.

By the end you'll have built — from scratch where it matters — every standard component of a modern retrieval stack, and you'll know empirically which interventions paid off on this corpus and roughly how much.

By the end you should be able to:

- Build a BM25 index alongside a dense index and explain when each retriever wins.
- Implement Reciprocal Rank Fusion (RRF) in ~10 lines and combine two retrievers' outputs.
- Implement MMR diversification in ~15 lines of numpy.
- Wire a cross-encoder reranker into the bi-encoder retrieval pipeline.
- Calibrate `top_k` and the `candidate_k → final_k` ratio on a specific corpus.
- Run a side-by-side comparison: baseline dense vs. hybrid vs. hybrid+rerank.
- Decide which interventions to use in production, and which to skip.

## 📋 Prerequisites

**Read first:**

- 📖 [Retrieval strategies](../../concepts/rag/retrieval-strategies.md)
- 📖 [Hybrid search](../../concepts/rag/hybrid-search.md)
- 📖 [Reranking](../../concepts/rag/reranking.md)

The three Lab 06 prerequisites (what-is-rag, retrieval-as-a-tool, chunking-and-indexing) remain prerequisites. Lab 07 doesn't re-derive that material.

**Complete first:**

- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/) — Lab 07 reuses Lab 06's corpus, chunker, and bi-encoder retriever. Most of the lab is *extending* Lab 06's code with the additional retrievers.

**Setup:**

Python 3.11+ with the repo's environment. Two new dependencies on top of Lab 06's:

```bash
uv add 'rank-bm25>=0.2.2,<0.3'
# sentence-transformers is already installed from Lab 06; we use its CrossEncoder class
```

(`numpy` is already a dependency. The `sentence-transformers` install from Lab 06 covers both the bi-encoder and the cross-encoder.)

The default lab path needs no API key beyond the LLM provider key you set up in Lab 01. Two model downloads on first run:

- `sentence-transformers/all-MiniLM-L6-v2` — already cached from Lab 06 (~80 MB).
- `cross-encoder/ms-marco-MiniLM-L-6-v2` — ~80 MB on first run, cached thereafter.

Total disk: ~160 MB across both models.

## 🛠 Tools and versions

| Library | Version | Verified |
|---|---|---|
| `rank-bm25` | `>=0.2.2,<0.3` (latest: `0.2.2`) | 2026-05-24 |
| `sentence-transformers` | `>=5.0,<6.0` (latest: `5.5.1`) | 2026-05-24 (from Lab 06) |
| Bi-encoder model | `sentence-transformers/all-MiniLM-L6-v2` | 2026-05-24 |
| Reranker model | `cross-encoder/ms-marco-MiniLM-L-6-v2` | 2026-05-24 |
| `numpy` | `>=1.26` | 2026-05-24 |

API signatures live-verified via `inspect.signature` against installed packages. Pinned APIs and primary-source links: [embeddings snapshot](../../tools/embeddings/snapshot-v1.0.md).

A note on `rank-bm25`: it's the standard small BM25 library for Python (`0.2.2`, Apache-2.0, numpy as only dependency, ~6M downloads/month). It hasn't seen new releases in some time, which means it's *stable* — there's nothing to break — but if you scale beyond a few thousand chunks you'll want to migrate to `bm25s` or a real search engine. For lab-scale work, `rank-bm25` is the right call.

## What you'll build

A retrieval pipeline that produces measurably better top-k than Lab 06's bi-encoder-alone implementation:

```python
# Same contract as Lab 06's search_corpus, with a better implementation:
result = search_corpus(query, top_k=5)
# {
#     "status": "ok",
#     "results": [
#         {"chunk_id": ..., "doc_id": ..., "title": ...,
#          "snippet": ..., "score": ...,
#          "retrieval_signals": {"dense": 0.61, "bm25": 4.21, "rerank": 8.97}},
#         ...
#     ]
# }
```

The pipeline:

```
query → bi-encoder retrieval ─┐
                                ├─→ RRF fusion → MMR → top-30 candidates
        BM25 retrieval ────────┘                              │
                                                              ▼
                                                       cross-encoder rerank
                                                              │
                                                              ▼
                                                          top-5 final
```

Five components, each independently testable. The lab walks through them one at a time.

## Steps

The notebook covers these in order:

**0. Setup.** Imports, env, load Lab 06 corpus and chunker. Same provider-agnostic LLM client (only used for the final agent-integration step).

**1. Recreate the Lab 06 baseline.** Build the bi-encoder index and a top-5 baseline. Define a small set of evaluation queries — some Lab 06 handled well, some it handled poorly. This is what every later upgrade is measured against.

**2. Add BM25.** Build a `rank-bm25` index over the same chunks (with the same tokenization). Compare BM25's top-5 against the bi-encoder's on the evaluation queries. Confirm BM25 wins on proper-noun and exact-term queries; loses on semantic ones.

**3. Reciprocal Rank Fusion.** Implement RRF from scratch (~10 lines). Combine the two retrievers' outputs. Compare top-5 against either alone.

**4. MMR diversification.** Implement MMR from scratch (~15 lines of numpy). Apply to the fusion output. Show which queries benefit from diversification (overlap-heavy chunks) and which don't.

**5. Cross-encoder reranking.** Load `cross-encoder/ms-marco-MiniLM-L-6-v2`. Rerank the top-30 fusion candidates. Show the precision improvement.

**6. The full pipeline.** Combine all stages: dense + BM25 → RRF → MMR → reranker → top-5. This is the production-grade retrieval function.

**7. Wire into the agent loop.** Replace Lab 06's `search_corpus` body with the new pipeline. Re-run the three test queries from Lab 06. Show that the agent loop is unchanged but the retrieval results are better.

**8. (Stretch) Calibration on your own queries.** A pattern for measuring `top_k`, `candidate_k`, and the MMR `λ` on a small validation set.

## What we don't do in this lab

Anti-scope, kept explicit:

- **No RAG evaluation framework** (Ragas, TruLens, custom eval frameworks). The lab uses informal side-by-side comparison on a handful of queries to build intuition. Real RAG evaluation is Path 06.
- **No production vector stores** as default. We continue to use numpy + `rank-bm25` in-memory because the math is identical to what Chroma/Qdrant/Weaviate do under the hood, and the mechanics are visible.
- **No LangChain `EnsembleRetriever` or LlamaIndex `QueryFusionRetriever`.** Same pedagogical reason as Lab 06 — Lab 07's whole point is showing what those abstractions wrap.
- **No contextual retrieval, query expansion, or HyDE.** All planned for future Path 02 batches.
- **No late-interaction models** (ColBERT, PLAID). Production-grade infrastructure required; out of scope.
- **No reranker fine-tuning** on domain data. Useful at scale; off-the-shelf rerankers are surprisingly transferable.
- **No multi-agent retrieval** (researcher + judge + synthesizer). That's Path 03.

## Common gotchas

- **BM25 tokenization mismatch.** If you tokenize the corpus and the query *differently*, BM25 silently scores low across the board. Use the same tokenizer for both. The lab uses `re.findall(r"\w+", text.lower())` for simplicity — apply consistently.
- **Reranker downloads on first run.** First call to `CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")` downloads ~80 MB. Add 30-60 seconds.
- **Score scale confusion.** Bi-encoder cosine ∈ [-1, 1] with sensible chunks usually in [0.2, 0.8]. BM25 ∈ [0, ~30] depending on corpus. Cross-encoder logits ∈ [-15, +15]. Don't compare across; let RRF handle the unification.
- **Candidate set too small.** If you set `candidate_k=5` and reranker `top_k=5`, you've gained nothing — the reranker can't surface anything outside the bi-encoder's top-5. Default `candidate_k=30` for `final_k=5`.
- **MMR `λ` confusion.** `λ=1.0` means *pure relevance* (no diversification); `λ=0.0` means *pure diversity* (ignores the query). The naming is confusing in some implementations.
- **Reranking CPU performance.** ~30 pairs/second on a laptop. For a lab interactive feel, keep `candidate_k` ≤ 30. Real production GPU inference is 50-100× faster.

## Solution discussion

A reference implementation will land in [`solution/lab.ipynb`](./solution/lab.ipynb) in a dedicated solutions batch later. Three design choices worth flagging:

- **We use `rank-bm25` (a library) for BM25 but implement RRF and MMR from scratch.** BM25 has subtle math (term frequency saturation, length normalization, IDF) that's worth using a tested implementation for. RRF and MMR are 10-15 lines each — writing them from scratch is faster than learning a library's API.
- **The numpy index stays.** Lab 07's headline pipeline runs over a numpy array, just like Lab 06. The math is identical to what Chroma or Qdrant do; the moving parts are visible.
- **Evaluation is informal.** A handful of queries with known-good chunks lets the learner *see* the precision improvement step by step. Formal evaluation (recall@k, MRR, nDCG, faithfulness) is Path 06 — adding it here would dilute the focus on retrieval mechanics.

## 🧮 Going deeper

- 🧮 [Agents as policies](../../math-foundations/04-agents-as-policies.md) — the policy framing still applies; the action space is unchanged from Lab 06.
- 📖 [Retrieval as a tool](../../concepts/rag/retrieval-as-a-tool.md) — the agent-loop framing reranking and hybrid retrieval sit underneath.
- ⚙️ [Vector stores snapshot](../../tools/vector-stores/snapshot-v1.0.md) — which production stores have native hybrid + reranking support.

## ✅ Check your understanding

After finishing the lab, take the quiz:

- 🧠 [`quizzes/agentic-rag/retrieval-strategies.md`](../../quizzes/agentic-rag/retrieval-strategies.md) — 8 questions on the four knobs, hybrid fusion, reranking architecture, and when each intervention helps.

If you score below 6/8, re-read the three retrieval-quality concept pages and re-run step 7 of the notebook (the side-by-side comparison).

## What comes next

You've now built every standard component of a production-grade retrieval pipeline. Path 02 continues with:

- **Contextual retrieval** — Anthropic's chunk-augmentation technique that addresses some chunk-boundary failure modes. (Future batch.)
- **Query expansion / HyDE / multi-query** — the upstream-of-retrieval interventions. (Future batch.)
- **RAG evaluation** — measuring whether all this actually helps on your corpus. (Future batch; deeper treatment in Path 06.)
- **The framework bridge** — same RAG agent in LangChain/LangGraph. (Future batch.)

After this batch, your Lab 06 + Lab 07 stack covers ~80% of what production RAG systems do. The remaining 20% is per-corpus tuning plus evaluation.
