# Retrieval as a tool

> 🟢 Stable · ⏱ ~9 min read · 🏷 rag, agents, tools

## TL;DR

In agentic RAG, retrieval isn't a step in a pipeline — it's a *tool the agent decides to call*. The agent loop is the one you already built in Lab 01 and refined in Lab 03; only the tool's implementation changes. This page is about the patterns that transfer from Lab 03 to Lab 06 (most of them) and the few that change because the corpus is now controlled.

If you understood the two-tools-not-one argument from [`concepts/tools/search-tools.md`](../tools/search-tools.md), this page extends it.

---

## The shape

Naive RAG is a pipeline; the LLM is called once. Agentic RAG is an agent loop; the LLM is called repeatedly, each time deciding whether to call a tool or finish.

```
┌──────────────┐     ┌───────────────┐     ┌──────────┐
│  agent       │ ──→ │  retrieval    │ ──→ │  agent   │  loop
│  decides     │     │  tool         │     │  reads   │   ↓
└──────────────┘     └───────────────┘     └──────────┘  ...
        ↑                                       │        eventually
        └───────────────────────────────────────┘        emit answer
```

The agent code is the same code you wrote in Lab 03. The only thing that differs is the implementation of the tools.

## Two tools, mirroring Lab 03

Lab 03 had `web_search(query)` for ranked snippets and `fetch_page(url)` for full content. Lab 06 has:

```python
def search_corpus(query: str, top_k: int = 5) -> dict:
    """Return top-k chunks from the corpus, ranked by similarity to the query.

    Returns dict with one of:
      {"status": "ok",    "results": [{"chunk_id": ..., "doc_id": ..., "title": ..., "snippet": ..., "score": ...}, ...]}
      {"status": "empty", "query": ..., "detail": "no chunks crossed similarity threshold"}
      {"status": "error", "kind": "...", "detail": ...}
    """

def read_chunk(chunk_id: str) -> dict:
    """Return the full text of a single chunk by id.

    Returns dict with one of:
      {"status": "ok",     "chunk_id": ..., "doc_id": ..., "title": ..., "text": ...}
      {"status": "error",  "kind": "not_found" | "other", "detail": ...}
    """
```

The parallels with Lab 03:

| Lab 03 (web search) | Lab 06 (corpus RAG) |
|---|---|
| `web_search(query)` → snippets | `search_corpus(query)` → chunk snippets |
| `fetch_page(url)` → cleaned text | `read_chunk(chunk_id)` → full chunk text |
| Snippets for triage, full pages for synthesis | Snippets for triage, full chunks for synthesis |
| Citation: `{url, title, used_in}` | Citation: `{chunk_id, doc_id, title}` |
| Citations recorded by the loop, not the LLM | Same |
| Repeated-action detection via `_action_hash` | Same |
| Step cap with graceful "I couldn't find a confident answer" | Same |

The point of the parallel naming is that **the pattern transfers**. If you can read Lab 03's agent code, you can read Lab 06's. The conceptual move is *only* "swap the I/O layer for retrieval over a local index."

## Why split into two tools (again)

Same argument as Lab 03, recapped because it's worth internalizing.

Retrieval over an index returns *snippets* — the chunk's text, usually 200–800 tokens, possibly truncated for display. That's enough to triage relevance: "is this chunk plausibly about what I asked?" But it may not be enough to synthesize an answer, especially when chunk boundaries split important content.

Reading a chunk in full is more expensive in token budget but lets the model see the actual answer. The agent decides which chunks to read.

A single combined `retrieve_and_return_full_chunks(query, k=5)` tool would dump all 5 full chunks into the model's context every time. At ~600 tokens per chunk, that's 3000 tokens per retrieval — and most of them irrelevant for any given query. Two tools let the agent pay only for the chunks it actually needs.

A bonus property: if the agent reads a chunk and decides it's not the answer, it can refine the query and search again without having burned the full chunk into the conversation history. The triage step lets the agent stay efficient on its own context budget.

## What changes from Lab 03

Three meaningful differences. The agent code doesn't change much; the *failure modes* do.

### 1. The corpus is bounded and you own it

In Lab 03, "the agent found nothing" could mean "the open web doesn't have an answer," "the search engine ranked the answer too low," "the answer is on a paywalled page we couldn't fetch," or "I phrased the query wrong." All four are plausible.

In Lab 06, "the agent found nothing" means one of three things:

- The answer isn't in the corpus.
- The chunking missed it (the answer spans a chunk boundary).
- The query is too distant from how the chunk is phrased.

The agent's recovery options shrink: it can refine the query (helps with the third case), but it can't fall back to "go fetch a different URL the web has lots of options." This makes graceful "I couldn't find this in our docs" both more important and more honest in agentic RAG.

### 2. No rate limits, no paywalls, no 404s — but new failure modes

The web's failure modes (timeouts, blocked, rate-limited, paywall, irrelevant page) mostly disappear. The lab's `search_corpus` and `read_chunk` should never time out (you control the index) or 404 (you control the chunks).

What replaces them:

- **Low-similarity floor.** No chunk crosses some minimum similarity threshold. The agent should treat this like Lab 03's empty result.
- **Wrong-but-confident retrieval.** A chunk that looks similar but isn't actually relevant — the retriever's mistake, not a network issue. The agent has to *read* and notice the mismatch.
- **Chunk-boundary loss.** The answer exists in the corpus but lives at the boundary between two chunks; neither chunk contains the full answer alone. This is a chunking problem, not a retrieval problem, and we'll come back to it in [`chunking-and-indexing.md`](./chunking-and-indexing.md).
- **Stale corpus.** You indexed last month; the doc was updated yesterday. The lab corpus is bundled so this can't happen in Lab 06, but it's the big production failure mode.

### 3. Citations get more precise

Lab 03's citations were URLs the agent fetched. Lab 06's citations are `(doc_id, chunk_id)` tuples — specific pieces of specific documents. This is *better*, not just different: a user can see exactly which chunk grounded which claim.

Like Lab 03, the citations are recorded by the agent loop the moment `read_chunk` returns successfully. The LLM doesn't enumerate citations at the end of its answer; the loop does. The LLM is free to write the answer however it wants; the citations are an out-of-band property of which chunks were *read*. This is the single most important property of the agent loop and it transfers verbatim from Lab 03.

## What stays the same

For completeness, here are the things that are identical between Lab 03 and Lab 06:

- **System prompt strategy.** Use snippets when sufficient. Read full chunks when synthesis requires their content. Refine when results are bad. Say "I couldn't find a confident answer" instead of guessing.
- **Repeated-action detection.** The `_action_hash` mechanism doesn't care what the tools do; it just refuses identical re-invocations.
- **Step cap with graceful exit.** The exit message becomes "I couldn't find this in the corpus" instead of "on the web," but the mechanism is the same.
- **Structured tool errors.** Same `{"status": ...}` discipline. Same shape, same handling.
- **Provider-agnostic LLM client.** OpenAI default, Anthropic alternative, same as prior labs.

The only thing genuinely new in Lab 06's agent loop is the citation tuple shape — `{chunk_id, doc_id, title}` instead of `{url, title}`. Two characters of code change.

## When you'd reach for naive RAG instead

Worth being explicit. **Not every question deserves agentic RAG.**

If your traffic is mostly single-hop factual questions ("what's our return policy?") that one good retrieval can answer, naive RAG is faster and cheaper. The agent loop is *worth* its extra LLM calls when:

- Multi-step questions are common.
- Refinement on first-query failures meaningfully improves answer quality.
- Citation precision matters per-chunk, not per-document.
- The corpus is large enough that the right answer is rarely in the top-5 chunks of any first query.

Production systems often run both, routing per-query (naive RAG for simple lookups, agentic RAG for synthesis tasks). The path will get to that routing pattern in a later batch. For now: build the agentic version, understand the patterns, and you'll be able to recognize when naive RAG is the right efficiency move.

## A common confusion to clear up

People sometimes describe agentic RAG as "the agent decides whether to use RAG or not." That's an *adjacent* pattern (routing) but not what agentic RAG specifically means.

The defining property of agentic RAG is **iterative use of the retrieval tool** — multiple retrievals per question, with refinement between them, driven by what the agent observes. Whether to invoke retrieval at all is a separate decision.

In Lab 06, retrieval is always available and always relevant (the lab's corpus is the only source of information). The agentic part is *how many times* the agent retrieves, *what* it queries, and *which chunks* it reads in full. Routing — "should I retrieve at all, or just answer from world knowledge" — is a Path 06 evaluation/routing concern.

## Design checklist for an agentic RAG system

If you're building one yourself (Lab 06 walks through this):

- [ ] Two tools: `search_corpus` (snippets) and `read_chunk` (full text).
- [ ] Both return *structured results* — typed status, kind, detail.
- [ ] Index is built once over all chunks; queries run against the static index.
- [ ] Embeddings are normalized so cosine similarity is a dot product.
- [ ] The agent tracks which chunks it *read* (citations), separately from which chunks it *saw* in `search_corpus` results.
- [ ] System prompt steers the model toward triage-then-read, not read-everything.
- [ ] Step cap with graceful "couldn't find a confident answer" exit.
- [ ] Repeated-action detection on `(name, args)` pairs.
- [ ] Sanity-test the empty-results path explicitly; don't ship without it.

Each of these mirrors Lab 03's checklist almost exactly. The point of Lab 06 is to make the transfer visible.

## See also

- 📖 [What is RAG?](./what-is-rag.md) — the naive vs agentic distinction.
- 📖 [Chunking and indexing](./chunking-and-indexing.md) — the decisions inside `search_corpus`'s implementation.
- 📖 [Search tools](../tools/search-tools.md) — the Lab 03 conceptual companion this page parallels.
- 📖 [Tool design](../tools/tool-design.md) — the general patterns these specialize.
- 🧪 [Lab 03: Multi-step research agent](../../labs/03-multi-step-research-agent/) — the search-the-web analog.
- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/) — the lab this concept page sets up.

## References

- Anthropic (2024). [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents) — covers the "retrieval as a tool" framing under its agentic patterns discussion.
- Khattab, O. et al. (2024). [*DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines*](https://arxiv.org/abs/2310.03714). ICLR 2024. DSPy treats retrieval as one composable module among many; reading their `RAG` and `MultiHop` modules shows the agentic pattern formalized.
- Gao, Y. et al. (2024). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997) — the survey's "modular RAG" section is the closest the literature comes to formalizing the agentic-retrieval pattern.
