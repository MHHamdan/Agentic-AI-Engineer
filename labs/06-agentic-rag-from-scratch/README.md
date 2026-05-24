# Lab 06: Agentic RAG from scratch

> 🟡 Intermediate · ⏱ ~100–130 min · 📚 Controlled corpus, real retrieval

## 🎯 Goal

Build a research-style RAG agent that answers questions from a **controlled corpus of bundled Markdown documents**, with the same multi-step reasoning, structured-error, and citation-tracking discipline Lab 03 established for the open web. The agent has two tools — `search_corpus` and `read_chunk` — that mirror Lab 03's `web_search` and `fetch_page`. The loop is the loop you've built three times now. Only the I/O layer changes.

This lab is the practical entry point to Path 02 — Agentic RAG. By the end you'll have built the entire retrieval stack from scratch: embedding the corpus, chunking the documents, indexing the chunks in numpy, querying the index, integrating it as an agent tool, and tracking citations as a structural property of the loop.

By the end you should be able to:

- Implement chunking that respects document structure and stays under your embedding model's token limit.
- Build a vector index from scratch in ~20 lines of numpy, and articulate what production vector stores add on top.
- Wire retrieval into the agent loop as a tool, mirroring Lab 03's pattern.
- Track chunk-level citations in the loop's state, not the LLM's working memory.
- Recognize the chunking and retrieval failure modes by inspection of the agent's trajectory.
- Swap the headline embedding model for `text-embedding-3-small` with a few lines of code.
- Explain to a teammate why "RAG is just search with embeddings" is the wrong way to think about it.

## 📋 Prerequisites

**Read first:**

- 📖 [What is RAG?](../../concepts/rag/what-is-rag.md)
- 📖 [Retrieval as a tool](../../concepts/rag/retrieval-as-a-tool.md)
- 📖 [Chunking and indexing](../../concepts/rag/chunking-and-indexing.md)
- ⚙️ [Embedding models snapshot](../../tools/embeddings/snapshot-v1.0.md)

**Complete first:**

- 🧪 [Lab 01: First agent from scratch](../../labs/01-first-agent-from-scratch/) — Lab 06 reuses the agent loop directly.
- 🧪 [Lab 02: Tool design and selection](../../labs/02-tool-design-and-selection/) — Lab 06 reuses the structured-error pattern.
- 🧪 [Lab 03: Multi-step research agent](../../labs/03-multi-step-research-agent/) — Lab 06 is the same shape with a different corpus. If you can read Lab 03, you can read Lab 06.

Lab 05 (LangGraph) is *not* required. Lab 06 stays from-scratch for the same pedagogical reasons.

**Setup:**

Python 3.11+ with the repo's environment. Two new dependencies:

```bash
uv add 'sentence-transformers>=5.0,<6.0'
```

(`numpy` is already a transitive dependency from prior labs. `requests`, `pydantic`, and `openai`/`anthropic` come along too from prior labs.)

The default lab path needs no API key beyond the LLM provider key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) you already have set. The bundled corpus is in this folder; no downloads required.

**Optional, for the OpenAI embeddings swap-in section:**

```bash
# Already installed if you did prior labs:
uv add 'openai>=1.40'
```

## 🛠 Tools and versions

| Library | Version | Verified |
|---|---|---|
| `sentence-transformers` | `>=5.0,<6.0` (latest: `5.5.1` as of 2026-05-24) | 2026-05-24 |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | 2026-05-24 |
| `numpy` | `>=1.26` | 2026-05-24 |
| `openai` *(optional embedding swap-in)* | `>=1.40` (latest: `2.38.0`) | 2026-05-24 |
| `openai` *or* `anthropic` *(LLM)* | from prior labs | 2026-05-24 |

Pinned APIs and primary-source links: [embedding snapshot](../../tools/embeddings/snapshot-v1.0.md). If you're running this lab more than ~3 months after the verification date, re-check the snapshot first.

## What you'll build

Same `run_agent(question) → answer` shape as Lab 03, but the citations point to chunks instead of URLs:

```python
result = run_agent("What is the ReAct pattern and how does it differ from a plain agent loop?")
# {
#     "answer": "The ReAct pattern is a way of structuring agent decisions ...",
#     "citations": [
#         {"chunk_id": "03-react-pattern.md:0", "doc_id": "03-react-pattern.md",
#          "title": "The ReAct Pattern"},
#         {"chunk_id": "01-agent-loop.md:0", "doc_id": "01-agent-loop.md",
#          "title": "The Agent Loop: A Brief Introduction"},
#     ],
#     "steps": 4,
#     "stopped_reason": "answer_with_citations"
# }
```

Two tools:

1. **`search_corpus(query, top_k=5)`** — embeds the query, computes cosine similarity against every chunk, returns top-k with snippets. Same role as Lab 03's `web_search`.
2. **`read_chunk(chunk_id)`** — returns the full text of a single chunk by ID. Same role as Lab 03's `fetch_page`.

One loop with explicit:

- **Step cap** (default 8) and graceful exit.
- **Repeated-action detection** via `_action_hash` (same mechanism as Lab 03).
- **Citation tracking** in the loop's state, recording only chunks that were *read* via `read_chunk` (not snippets that were merely seen in search results).

## Steps

The notebook walks through these in order:

**0. Setup.** Imports, env, provider-agnostic LLM client (OpenAI default, Anthropic alternative). Same wrapper as prior labs.

**1. Load and chunk the corpus.** Read every `.md` file in `corpus/`, recursively split into chunks at ~200 tokens with 20% overlap, attach metadata. Inspect the chunks before indexing — chunking should be transparent.

**2. Build the embedding index.** Load `all-MiniLM-L6-v2`, encode all chunks with `normalize_embeddings=True`, stack into a single `(n_chunks, 384)` numpy array. Print storage cost and index size.

**3. Implement `search_corpus`.** Embed the query, compute dot product against the index (= cosine similarity on normalized vectors), return top-k with snippets. Structured-error pattern matching Lab 03.

**4. Implement `read_chunk`.** Look up the chunk by ID, return its full text. Handles `not_found` gracefully.

**5. The agent loop.** Lab 03's loop, with two changes:
   - Citation entries are `(chunk_id, doc_id, title)` tuples instead of `(url, title)`.
   - The system prompt mentions "the corpus" instead of "the web."
   - Everything else is identical.

**6. Three test queries.** Easy / medium / hard, with sample trajectories:
   - **Easy:** "What is the ReAct pattern?" — typically 1 search + 1 read.
   - **Medium:** "How does chunking interact with the embedding model's token limit?" — synthesis across two documents (chunking + embeddings).
   - **Hard:** "What's the difference between a search tool and a retrieval tool, and which failure modes does each have?" — multi-hop, requires reading 3+ chunks across multiple documents.

**7. Failure-mode walkthrough.** Drive the agent into:
   - Empty results (a deliberately off-topic query).
   - Wrong-but-confident retrieval (a query that surfaces a similar-but-not-quite-right chunk; the agent has to *read* and notice).
   - Repeated-action refusal (simulated).

**8. (Stretch) Swap to OpenAI embeddings.** With `OPENAI_API_KEY` set, swap the embedding function in ~10 lines of code. Same loop, same tools — the embedding layer is genuinely pluggable.

## What we don't do in this lab

Anti-scope, kept explicit:

- **No production vector stores** (Chroma, pgvector, Qdrant, Weaviate, Pinecone). Covered as alternatives in the [vector-stores snapshot](../../tools/vector-stores/snapshot-v1.0.md). The headline lab uses numpy so the cosine math is visible.
- **No LangChain RAG abstractions** (`RetrievalQA`, `VectorStoreRetriever`, etc.). Reserved for a future framework-bridge lab analogous to Lab 05.
- **No re-ranking, no hybrid search, no contextual retrieval.** All planned for future Path 02 batches.
- **No RAG evaluation framework** (Ragas, TruLens, custom evaluators). That's Path 06.
- **No multi-agent coordination.** That's Path 03.
- **No LangSmith tracing.** Path 06.

The lab's headline is "what does an agentic RAG system look like from scratch?" Adding more surface area dilutes the answer.

## Common gotchas

- **First run is slow.** The first call to `SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")` downloads the model (~80 MB). Add 30–60 seconds; subsequent runs reload from cache.
- **The 256-wordpiece foot-gun.** If you change the chunk size and exceed 256 wordpieces (~200 LLM-tokens), MiniLM silently truncates. Lab 06 chunks at 200 tokens deliberately. If you bump this, expect retrieval quality to drop sharply.
- **Forgetting `normalize_embeddings=True`.** Cosine similarity reduces to a dot product only when vectors are normalized. Forget the flag and your similarity scores will look wildly off, with no error message.
- **Mixing chunk IDs across re-indexings.** If you change the chunking, the chunk IDs change. Don't compare runs from different chunking strategies — the citations won't be comparable.
- **Expecting tab-completion on `read_chunk(chunk_id=...)`.** Chunk IDs are strings like `03-react-pattern.md:0`. The agent gets them from search results; you don't have to memorize them.

## Solution discussion

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) with notes in [`solution/README.md`](./solution/README.md). 19 cells vs the lab's 38 — the failure-mode walks are removed since you've worked through them. Chunker config is pinned (`TARGET_TOKENS=160`, `OVERLAP_TOKENS=32`) for stability across Labs 07-09. Three design choices worth flagging up front:

- **We use `sentence-transformers` even though it's a heavyweight dependency** (~500 MB with PyTorch). The alternative — calling a hosted embedding API as the default — requires an API key and adds network latency. For a community lab focused on retrieval mechanics, having the embedding layer local and inspectable is more valuable than a smaller install footprint.
- **The numpy index is *not* a toy.** It's a real, working vector index — just brute-force at this scale. Production vector stores add persistence, metadata indexing, and ANN algorithms, but the math is identical. Knowing this changes how you read the marketing.
- **The chunking is intentionally simple** (recursive splitting on paragraph and sentence boundaries). A more sophisticated semantic-splitting approach would chunk better but obscure the mechanics. Optimization is reserved for a later batch.

## 🧮 Going deeper

- 🧮 [Agents as policies](../../math-foundations/04-agents-as-policies.md) — the policy framing still applies; the action space includes retrieval now.
- 📖 [Tool design](../../concepts/tools/tool-design.md) — every structured-error and tool-contract pattern from Lab 02 reappears here on retrieval I/O.
- 📖 [Search tools](../../concepts/tools/search-tools.md) — the Foundations companion that this lab's pattern parallels.

## ✅ Check your understanding

After finishing the lab, take the quiz:

- 🧠 [`quizzes/agentic-rag/rag-fundamentals.md`](../../quizzes/agentic-rag/rag-fundamentals.md) — 8 questions on the patterns, the 256-wordpiece foot-gun, citation tracking, and when to upgrade from numpy.

If you score below 6/8, re-read the three concept pages and re-run the failure-mode walkthrough in step 7 of the notebook.

## What comes next

You've now built an agentic RAG system. Path 02 continues with:

- **Retrieval strategies** — top-k tuning, MMR, the recall-precision tradeoff. (Future batch.)
- **Re-ranking** — cross-encoders that rescore the top-N candidates from dense retrieval. (Future batch.)
- **Hybrid search** — BM25 + dense fusion, useful for queries with specific tokens. (Future batch.)
- **Contextual retrieval** — Anthropic's technique for augmenting chunks with document-level context before embedding. (Future batch.)
- **The framework bridge** — same RAG agent in LangChain/LangGraph, analogous to Lab 05 for Foundations. (Future batch.)

After Path 02, the natural continuation is Path 03 (Multi-Agent Systems) or Path 06 (Evaluation & Observability), depending on what you want to do with the agents you can now build.
