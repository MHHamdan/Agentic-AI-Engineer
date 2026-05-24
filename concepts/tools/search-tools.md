# Search tools

> 🟢 Stable · ⏱ ~9 min read · 🏷 tools, search, retrieval

## TL;DR

A search tool returns *probabilistic, ranked, often-stale, paywall-prone* results — not the deterministic, exact-match answers your other tools give the model. That's not a deficiency; it's the nature of "what's on the public web right now," and it means agents using search must reason about result *selection* and *fetching* as separate steps. This page covers what makes search tools different, the patterns that work, and why a single `web_search(query)` call is *not* the same thing as RAG.

---

## How search tools differ from "normal" tools

The tools we covered in [`tool-design.md`](./tool-design.md) — `lookup_customer`, `compute_total`, `update_order` — share three properties:

1. **Deterministic given inputs.** Same args → same result (modulo legitimate state changes).
2. **Exact-match semantics.** You're not selecting *the best of several plausible candidates*.
3. **Closed world.** The set of valid IDs, fields, and operations is known.

Search tools have *none* of these. Same query at different moments returns different results. There's no single "correct" page among the candidates. The "world" is the public web, which is unbounded, partially paywalled, partially generated, and partially adversarial.

The implication: a search tool is not just "another tool the agent can call." It's a different *kind* of tool that demands different reasoning patterns from the agent.

## Two tools, not one

Almost every research agent benefits from splitting search into two tools:

```python
def web_search(query: str) -> list[SearchResult]:
    """Return ranked search results: title, URL, short snippet."""

def fetch_page(url: str) -> PageContent:
    """Fetch and clean the full content of a single URL."""
```

**Why split?** Because the cheap step (`web_search`) and the expensive step (`fetch_page`) have very different cost profiles, error modes, and reasoning requirements.

- `web_search` is cheap-ish, often rate-limited, returns snippets that may be enough to answer simple questions but rarely enough for synthesis.
- `fetch_page` is bandwidth-heavy, much slower, hits paywalls and JS-rendered pages and 404s. Each call costs real time.

If you merge them into a single "search and return full pages" tool, the agent loses the ability to *triage* — to look at the snippets, decide which 1–2 URLs are worth the full fetch, and skip the rest. That triage step is exactly where multi-step reasoning shows up, and it's the difference between an agent that makes 2 fetches and one that makes 8.

The pattern: **search broadly with snippets, fetch selectively, synthesize from what you fetched, cite the URLs you actually used.**

## Top-k result selection

`max_results=10` is the typical setting. You almost never want more.

The model receives the snippets as a tool result and decides which (if any) to fetch. A few design notes:

- **Snippets are 100–300 characters, not full pages.** Don't blow this up — the whole point is cheap triage. If a learner's agent passes `max_results=50` and then the model gets a 30K-token tool result, *that* is the bug.
- **Title matters as much as snippet.** Models seem to use the title heavily for relevance judgment, probably because it's the most reliable summary. Don't truncate titles.
- **Domain matters.** A snippet from `arxiv.org` and a snippet from `random-medium-blog.com` should not be treated as interchangeable. The model often picks up on this without prompting; sometimes you'll want to make it explicit ("prefer authoritative sources when available").
- **Top-1 ≠ best.** Search relevance ranking and *agent-usefulness* aren't the same thing. The agent should look at the top several results and pick, not just take #1.

A common failure mode: the agent fetches the top URL, finds it's a paywalled article, gives up, and writes "I couldn't find an answer." A good agent recognizes the paywall, drops to the next result, and tries again. Lab 03 demonstrates this explicitly.

## Snippet vs. full-page tradeoffs

Sometimes the snippet alone is enough. Sometimes only the full page will do. The agent needs to decide.

**Snippet-only works when:**

- The question is a quick factual lookup. "Who is the current Prime Minister of Canada?" — the snippet probably says it.
- You're orienting: "Is this person known for X or Y?" — snippets across multiple results converge on the answer.

**Full-page fetch is needed when:**

- The question requires reasoning over a section longer than 300 characters.
- The answer is buried (e.g., a methodology in a paper, an exception in a policy).
- Numerical precision matters and the snippet rounds.
- The snippet is ambiguous and you need disambiguation.

A good system prompt nudges the model toward this distinction: *"Use snippets when sufficient. Fetch pages when synthesis requires their content."* But this is a soft constraint, not a hard one — the model still has to judge per-question.

## Freshness

The web changes. Last week's news is yesterday's news; today's news is tomorrow's stale data.

Most search APIs let you scope by recency: `ddgs` has `timelimit="d"|"w"|"m"|"y"`, Tavily has a `time_range="day"|"week"|"month"|"year"` parameter. Use them when the question is recency-sensitive.

But don't over-restrict. "What is HTTP/3?" doesn't need a 1-week filter; you'll cut out the explanatory content that lives on stable docs sites. The pattern is:

- **Recency-sensitive questions** (news, prices, current events, recently-updated software): apply a time filter, default to month or shorter.
- **Stable-knowledge questions** (concepts, history, established science): no filter; old explanations are often better.
- **Mixed**: try a recent filter first, fall back to unfiltered if results are sparse.

The agent itself can encode this judgment by setting the time filter as an argument to `web_search`. A nice pattern is letting the tool accept `recency: Literal["any", "year", "month", "week", "day"]` so the model has to explicitly choose.

## Attribution and citation tracking

If your agent's final answer mentions a fact, the user should be able to verify where it came from. This is non-negotiable for any production research agent and good hygiene even in toy labs.

The clean pattern: **track the URLs the agent *actually used*, and emit them with the final answer**.

```python
{
  "answer": "...",
  "citations": [
    {"url": "https://...", "title": "...", "used_in": "the claim about X"},
    ...
  ]
}
```

Two things to watch:

- **"Used" means fetched and read.** Don't include URLs the agent merely searched and didn't open. If you do, the citation becomes "well, this URL was on a results page somewhere," which is meaningless.
- **Don't trust the model to enumerate citations from memory at the end.** Track them in your tool-call log, not in the LLM's working memory. The model's recall of "which URL did I just fetch?" is unreliable across 6-step trajectories. Lab 03 demonstrates the tracking pattern.

A foreshadowing: in Path 02 — Agentic RAG, you'll do this same citation tracking but over retrieved document chunks rather than fetched web pages. The mechanism transfers cleanly; only the source changes.

## Failure modes you'll see

A survey of what goes wrong in practice, with the right agent response:

| Failure | What it looks like | What the agent should do |
|---|---|---|
| **Empty results** | `web_search(...) → []` | Re-query with different terms. If still empty after 2 tries, surface "no relevant results found" rather than hallucinating. |
| **Noisy snippets** | Top results are SEO spam, listicles, or AI-generated junk | Look further down the results. Prefer sources with domain authority signals (arxiv, gov, edu, official docs). |
| **Timeout on fetch** | `fetch_page(url) → {"status": "error", "kind": "timeout"}` | Try the next result. Don't loop on the same URL. |
| **Paywall** | Status 200 but content is a "subscribe to read" wall | Detect via content heuristics (very short text, presence of paywall words). Skip to next result. |
| **Irrelevant page** | Fetched content doesn't actually address the query | Don't synthesize from it. Move on, or re-search. |
| **Rate limit** | `RatelimitException` | Back off (wait 5–30s) and retry once. Or surface the failure cleanly. |
| **Blocked / 403** | The site blocks bots | Don't retry; pick a different result. |
| **Redirected** | Final URL ≠ requested URL | Usually fine, but track both so citations point to the actual content. |

Most of these are not the agent's fault — they're the web being the web. The agent's job is to handle them gracefully, not eliminate them. Lab 03 exercises every one of these patterns explicitly.

## Why search is not RAG

This trips up enough people that it deserves explicit treatment.

**Search** queries the *open web* through a third-party engine. Results are ranked by the engine's relevance signals, change over time, and may be cached, paywalled, or generated. The agent has no control over what the corpus is — Google, DuckDuckGo, Bing, and friends decide what's indexed.

**RAG** queries a *known corpus that you control*. You picked the documents, you chunked them, you embedded them, you indexed them. The "search" step in RAG is a vector or hybrid similarity query over *your* index, returning chunks you put there.

The two patterns share a shape (query → ranked results → use results to answer), but they're fundamentally different in:

| | Web search | RAG |
|---|---|---|
| **Corpus** | The public web | A specific document set you chose |
| **Control over indexing** | None | Complete |
| **Result format** | Snippets pointing to live URLs | Pre-chunked text from your corpus |
| **Freshness** | Whatever the engine indexed recently | Whatever you ingested |
| **Reliability** | Variable; paywalls, 404s, garbage | Predictable; chunks always retrievable |
| **Cost model** | Per query (often rate-limited) | Per query (compute, sometimes per-token embedding cost) |
| **Citation** | "I read this URL" | "I retrieved this chunk from document X, page Y" |

A research agent can use *both*: search the web for context, query a domain-specific RAG corpus for proprietary knowledge. That's actually the architecture most production agents converge on. But conflating them — "RAG is just searching with embeddings" or "search is just RAG over the web" — leads to bad designs.

Lab 03 is web search only. Path 02 introduces RAG. By the end of both, the distinction should feel intuitive: search is *exploration over an external corpus you don't control*; RAG is *retrieval over a controlled corpus you built for purpose*.

## Design checklist for your own search tool

If you're wiring search into your own agent (Lab 03 will walk you through it):

- [ ] Two tools: `web_search` (snippets) and `fetch_page` (full content).
- [ ] `web_search` accepts a `recency` or `time_limit` argument so the model can scope it.
- [ ] Both tools return *structured errors* (typed status, kind, detail) — not raised exceptions.
- [ ] The agent tracks the URLs it *fetched and read*, separately from URLs it merely saw in results.
- [ ] The system prompt asks the agent to cite its sources in the final answer.
- [ ] There's a step cap with a graceful "I couldn't find a confident answer" exit path.
- [ ] Paywalls, timeouts, and empty-result cases are exercised in tests, not just the happy path.

If any of these is missing, the agent will appear to work on easy questions and fail in confusing ways on hard ones.

## See also

- 📖 [Tool design](./tool-design.md) — the general patterns this page specializes for search.
- 📖 [Tool selection](./tool-selection.md) — how the model decides between `web_search` and `fetch_page`.
- 🧪 [Lab 03: Multi-step research agent](../../labs/03-multi-step-research-agent/) — the practical exercise.
- ⚙️ [Search backends snapshot](../../tools/search/snapshot-v1.0.md) — pinned libraries and versions.
- 🗺 [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/) — the controlled-corpus counterpart.

## References

- Khattab, O. et al. (2024). [*DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines*](https://arxiv.org/abs/2310.03714). ICLR 2024. DSPy formalizes the search-then-synthesize pattern as composable modules.
- Schick, T. et al. (2023). [*Toolformer: Language Models Can Teach Themselves to Use Tools*](https://arxiv.org/abs/2302.04761). NeurIPS 2023. Search was one of the original Toolformer tools; the paper's analysis of *when* the model should reach for it is still useful.
- Anthropic (2024). [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents) — has a short section on "retrieval augmented generation" that's worth reading alongside this page to keep the search-vs-RAG distinction sharp.
- Lewis, P. et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. The original RAG paper; useful as the contrast to web search.
