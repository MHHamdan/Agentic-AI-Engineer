# Lab 03 · Reference solution

The polished final implementation of [Lab 03: Multi-step research agent](../README.md).

## What this is

A web-research agent with:

- **`web_search`** — wraps `ddgs` with structured `recency` enum, normalized result shape, and structured-error envelope on every documented failure mode (rate limit, timeout, empty, other).
- **`fetch_page`** — distinguishes the failure modes that matter for an agent: timeout, blocked (401/403/429), http_4xx, http_5xx, paywall (body-heuristic), parse error, and `too_long` (truncated but readable). Identifies itself via a custom User-Agent.
- **Agent loop** — `MAX_STEPS = 8`, system prompt that establishes the search-triage-fetch-synthesize trajectory, action-hash deduplication on `(tool_name, sorted_args)`, and **citations tracked by the loop, not the LLM** — only successful `fetch_page` results get appended.

## How it differs from `../lab.ipynb`

| Lab notebook (35 cells) | Solution (17 cells) |
|---|---|
| Step 6 walks through three failure modes deliberately (empty, paywall, repeated action) | Skipped — the hardening is just the default behavior |
| Steps 5/6 run multiple test queries against live web | One demo query |
| Step 8 stretch covers swapping to Tavily | Out of scope here — `ddgs` is the default |
| Inconsistent message-dict shape (mixed `msg["content"]` and `msg.content`) | Consistent dataclass attribute access |

## Implementation choices

1. **`RecencyType = Literal["any", "day", "week", "month", "year"]` with `_RECENCY_MAP`.** The agent sees a clean enum in the schema; the mapping to `ddgs`'s `timelimit=` codes happens inside `web_search`. The model never sees `"d"`, `"w"`, etc., so it can't get the codes wrong.
2. **Citations are appended only on `status in ("ok", "too_long")`** — never on snippet view. This is the structural property that makes citations trustworthy: the agent loop records what it *read*, not what the LLM *claims* to have read. The lab's `concepts/tools/search-tools.md` ("Why split into two tools") makes the case explicitly.
3. **Tool results are capped at 4000 chars** before appending to state. Long pages would otherwise dominate the context window across multi-step trajectories.
4. **The repeated-action handler returns a structured error**, not a hard halt. The model gets `{"status": "error", "kind": "repeated_action", "detail": "..."}` on its next step and can choose to try a different query.
5. **Paywall detection uses body-text markers**, not status codes — many paywalls return 200 with a teaser. The five markers in `PAYWALL_MARKERS` cover the most common templates; production systems would expand this list.
6. **Step-cap fallback returns a *graceful* answer**, not an exception. The user sees "I reached the step limit; I fetched these pages: ..." with the URLs the agent did manage to read. Useful for debugging.

## What's deliberately out of scope

For a real deployment:

- **Paid search backend** — `ddgs` is "for educational purposes only" per its own PyPI page and depends on scraping that upstream engines actively block. Production needs Tavily, Brave Search API, or Exa with terms of use.
- **`robots.txt` awareness** — fetch politely; the User-Agent identifies the bot, but real systems check `robots.txt` before fetching.
- **Per-host rate limiting** — multiple consecutive fetches from one domain should backoff politely.
- **Better content extraction** — `bs4` + manual cleanup works but loses a lot. `Trafilatura` or `Readability` produce cleaner output for synthesis.
- **Citation-quality verification** — does the cited page actually support the claim? That's RAG evaluation territory (Lab 09).

## Running the solution

```bash
cd labs/03-multi-step-research-agent/solution
jupyter notebook lab.ipynb
```

The demo cell makes live web calls; expect 3-8 seconds depending on the queries it picks. No API key for search is required (`ddgs` is keyless), but you do need `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.

## Next

- Take the [research-agent quiz](../../../quizzes/foundations/multi-step-research-agent.md) if you haven't already.
- Continue to [Lab 05: LangGraph rewrite](../../05-langgraph-rewrite/).
- Or jump to [Lab 06: Agentic RAG from scratch](../../06-agentic-rag-from-scratch/) — the search-vs-RAG transition.
