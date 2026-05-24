# Search backends — tool snapshot

> 🔴 **Tool snapshot — search backends for Lab 03, verified 2026-05-24**
> Primary sources: [ddgs on PyPI](https://pypi.org/project/ddgs/) · [Tavily Python SDK reference](https://docs.tavily.com/sdk/python/reference) · [ddgs GitHub](https://github.com/deedy5/ddgs)

Lab 03 needs a search backend that lets a community learner work through a real research agent without paying for anything or filling out forms before they've written a line of code. Search backends are 🔴 because they wrap services whose ToS, rate limits, and selectors change underneath us; this page pins what works *today* and tells you what to check when something stops working.

## What the lab uses

By default: **`ddgs`** (the metasearch library formerly known as `duckduckgo-search`). It needs no API key, no signup, and works out of the box.

When `ddgs` gets rate-limited or the educational disclaimer doesn't fit your use case: **`tavily-python`** with a free Tavily account (1,000 searches/month, no credit card on the free tier).

The lab ships both code paths. The default prose uses `ddgs`; the Tavily path is a few-line drop-in. The decision below is about which to reach for first — both are valid.

## Verified versions & pins

```toml
# pyproject.toml
ddgs = ">=9.0,<10"          # required
tavily-python = ">=0.5"     # optional, used if you have a TAVILY_API_KEY
beautifulsoup4 = ">=4.12"   # for fetch_page (HTML → text)
requests = ">=2.31"         # for fetch_page
```

| Library | Latest as of 2026-05-24 | Status |
|---------|-------------------------|--------|
| `ddgs` | `9.14.4` (May 15, 2026) | Production/Stable per PyPI classifiers; `9.x` line stable since Jul 2025 |
| `tavily-python` | check [docs.tavily.com/sdk/python/reference](https://docs.tavily.com/sdk/python/reference) at install time | Stable, officially maintained by Tavily AI |
| `beautifulsoup4` | `4.12+` | Stable for years; pinned for safety |
| `requests` | `2.31+` | Stable |

## `ddgs` (the default)

### Status

- **Package**: `ddgs` on PyPI. **Previously named** `duckduckgo-search` and renamed in 2024; old code may import from `duckduckgo_search` — both names exist on PyPI, but new code should use `ddgs`. The legacy PyPI page now points to the new one directly.
- **Maintained by** [deedy5](https://github.com/deedy5/ddgs) under MIT.
- **What it actually is**: a *metasearch* library that aggregates DuckDuckGo, Bing, Google, Brave, Yahoo, Yandex, Mojeek, Startpage, Wikipedia, and Grokipedia, with automatic fallback if one engine is unavailable. The "DDGS" name is now backronymed to "Dux Distributed Global Search," reflecting that scope.
- **Python**: requires `>=3.10`. Matches our project floor of 3.11.

### API the lab uses

```python
from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException, TimeoutException

with DDGS(timeout=10) as ddgs:
    results = ddgs.text(
        query="agentic AI architectures 2026",
        region="us-en",          # us-en, uk-en, ru-ru, ...
        safesearch="moderate",   # on, moderate, off
        timelimit="m",           # d, w, m, y, or None
        max_results=10,
        backend="auto",          # or "duckduckgo", "bing", "google", ...
    )
# results: list[{"title": str, "href": str, "body": str}, ...]
```

The result schema is stable across the `9.x` line: each dict has `title`, `href`, and `body` keys. The lab uses only these three; it does not depend on any optional fields.

### What changed in `9.x`

Two things matter for users coming from older code:

- **Package rename**: `duckduckgo-search` → `ddgs`. Import path changed from `from duckduckgo_search import DDGS` to `from ddgs import DDGS`. Behavior is otherwise compatible.
- **Metasearch fallback**: prior to `9.x`, the library queried DuckDuckGo only. From `9.6.0` (Sep 2025) onward, it falls back across multiple engines automatically. This makes individual queries more reliable but the *engine that answered* is no longer deterministic — important to know for production logging.

### Honest tradeoffs

- **Rate-limited.** DDG and the upstream engines rate-limit aggressively when they detect bots. For a single learner running a notebook a few times, this is rarely a problem. For a CI loop that hits the API on every push, it absolutely is. The lab runs offline by default for this reason.
- **"For educational purposes only"** is in the package's own disclaimer. That's fine for a tutorial lab and fine for personal projects. For commercial production use, the explicit official statement is to **use the engines' own paid APIs** (Bing Search API, Google Custom Search JSON API, Brave Search API), or use a search-optimized API like Tavily.
- **Result shape isn't normalized across engines.** All engines emit `title`/`href`/`body`, but snippet quality and relevance ranking vary by which backend served the result.
- **No structured ToS guarantee.** The library could break if an upstream engine changes their selectors or anti-bot stance. Pin a version, and don't depend on it being available indefinitely.

### Failure modes you'll see

- `RatelimitException` — back off and retry, or switch backends.
- `TimeoutException` — network or the upstream engine is slow. Retry once, then surface to the agent.
- Empty list — query returned no results. The agent must handle this; the lab demonstrates how.
- Garbage results — anti-bot fallback HTML being parsed; this is rare with `9.x`'s multi-engine fallback but possible.

## `tavily-python` (the production-oriented alternative)

### When to reach for it

- You're hitting `ddgs` rate limits enough that the friction outweighs the no-account-needed convenience.
- You're building something you'll ship, even informally, and want a service with an SLA-shaped behavior model rather than a "for educational purposes" disclaimer.
- You want search results **specifically optimized for LLM consumption** — Tavily's API returns cleaner snippets and supports `include_answer` and `include_raw_content` flags.

### API the lab uses

```python
from tavily import TavilyClient

client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
response = client.search(
    query="agentic AI architectures 2026",
    search_depth="basic",       # or "advanced" (uses more credits)
    max_results=10,
    include_answer=False,        # we want to do the synthesis ourselves
    include_raw_content=False,   # we'll fetch pages separately
)
# response["results"] is list[{"title", "url", "content", "score"}]
```

Note the field rename — Tavily returns `url` where `ddgs` returns `href`, and `content` where `ddgs` returns `body`. The lab includes a tiny `normalize_search_result(...)` helper that maps both to a common shape so the agent code doesn't care which backend ran.

### Free tier (verified 2026-05-24)

Per Tavily's own signup documentation, the free tier provides **1,000 API calls per month with no credit card required**. That's enough for casual learner use and small personal projects. The current pricing terms are at [tavily.com](https://tavily.com) — verify before relying on specific numbers.

### Honest tradeoffs

- **Requires signup.** Email + OAuth; the key starts with `tvly-`. For a community learner, this is friction. For someone shipping a project, it's a 2-minute task.
- **Costs money past the free tier.** Production-grade options always do.
- **Locked to one provider.** Unlike `ddgs`'s metasearch, you're depending on Tavily's stack. They're well-funded and integrated into LangChain/LlamaIndex/CrewAI ecosystems, but it's a vendor dependency.

## Why not Google CSE / Bing / Brave / SerpAPI directly?

We considered each:

- **Google Custom Search JSON API** — requires a Programmable Search Engine setup, GCP project, billing account; 100 free queries/day then $5/1000. The configuration friction is too high for a first research lab.
- **Bing Web Search API** — *deprecated* by Microsoft; new customers were blocked in 2025. Not a stable target.
- **Brave Search API** — solid, has a free tier (2,000 queries/month free as of late 2025), good ToS for AI use. A reasonable third option; we just didn't want to make the lab choose between three.
- **SerpAPI** — well-known commercial wrapper; requires an account, has a small free tier (100/month) and per-credit pricing beyond. Reasonable but more expensive than Tavily for the same use.

If you have a preference, the lab's search function is small enough to swap (~30 lines). The point of the lab isn't the backend; it's the agent's reasoning about its results.

## `fetch_page` (the second tool)

The lab needs to fetch the *full content* of a page once the agent picks a search result. We use `requests` + `beautifulsoup4` rather than a higher-level wrapper because:

- **Pedagogically** the lab needs to show learners how to handle HTTP timeouts, error codes, paywalls, and JS-rendered pages — abstracting that into a library hides the failure modes that are the whole point of the lab.
- **`ddgs.extract(url)`** does exist as a convenience and uses an HTML-to-Markdown conversion — production code can use it for cleaner output. The lab covers this in a sidebar.
- **`tavily_client.extract(urls)`** is the Tavily-side equivalent. Also covered as a sidebar.

The lab's `fetch_page` returns one of:

```python
{"status": "ok",       "url": str, "title": str, "text": str, "elapsed_ms": int}
{"status": "error",    "url": str, "kind": "timeout" | "http_4xx" | "http_5xx" | "parse" | "blocked", "detail": str}
{"status": "too_long", "url": str, "title": str, "text": str, "truncated_at": int}
```

This shape is deliberately the same as Lab 02's structured error pattern, so learners reuse vocabulary across labs.

## Where this snapshot is used

When this page updates, the following content depends on it and may need updates too:

- 🧪 [`labs/03-multi-step-research-agent/`](../../labs/03-multi-step-research-agent/) — primary consumer
- 📖 [`concepts/tools/search-tools.md`](../../concepts/tools/search-tools.md) — the conceptual framing
- 🗺 [`learning-paths/01-foundations/README.md`](../../learning-paths/01-foundations/README.md) — Module 4 references this snapshot

## Freshness check

Before trusting this page as current, verify each of the following from primary sources. If anything is more than a minor version drift, update the page.

1. **`ddgs` is still maintained.** Check [pypi.org/project/ddgs](https://pypi.org/project/ddgs/) for a recent release. If the latest release is older than ~3 months, investigate before relying on it.
2. **API shape unchanged.** Run a smoke test: `pip install -U ddgs && python -c "from ddgs import DDGS; r=DDGS().text('hello', max_results=1); print(list(r[0].keys()))"`. Expect `['title', 'href', 'body']` or a superset.
3. **Tavily free tier still exists.** Check [tavily.com](https://tavily.com) for current pricing. If the free tier has changed, update the section above.
4. **`tavily-python` import path unchanged.** Check [docs.tavily.com/sdk/python/reference](https://docs.tavily.com/sdk/python/reference) — should still be `from tavily import TavilyClient`.
5. **Bing Web Search API** — confirm it's still deprecated. Microsoft may un-deprecate; if so, that becomes another viable option.

When you update this page, bump the verification date at the top and add a row to the [CHANGELOG](../../CHANGELOG.md) under **Verified Tool Snapshots** in the `[Unreleased]` section.

## Primary sources

| Source | What it covers |
|---|---|
| [pypi.org/project/ddgs](https://pypi.org/project/ddgs/) | Current `ddgs` package status, version history, API surface |
| [github.com/deedy5/ddgs](https://github.com/deedy5/ddgs) | `ddgs` repository, release notes, issue tracker |
| [docs.tavily.com/sdk/python/reference](https://docs.tavily.com/sdk/python/reference) | Tavily Python SDK API reference |
| [tavily.com](https://tavily.com) | Tavily pricing and free-tier terms |

When a community blog post contradicts one of these, trust the official doc.
