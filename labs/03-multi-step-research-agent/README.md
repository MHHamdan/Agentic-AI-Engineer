# Lab 03: Multi-step research agent

> 🟡 Intermediate · ⏱ ~90–120 min · 📊 Real-world I/O

## 🎯 Goal

Build a research agent that answers questions requiring **multiple web searches and page fetches**, synthesizes across sources, and **cites the URLs it actually used**. From scratch in Python — no framework, no embeddings, no vector store. The agent has just two tools and a loop, but the trajectory is non-trivial: search → triage → fetch → re-search → synthesize → cite.

This is the first lab that touches the real internet. Lab 01 was a canned customer database; Lab 02 fixed broken tools on that same canned domain; Lab 05 rebuilt Lab 01 in LangGraph. Lab 03 hands the agent the open web, with all its rate limits, paywalls, 404s, and noisy snippets.

By the end you should be able to:

- Design and implement a `web_search` + `fetch_page` tool pair with the structured-error pattern from Lab 02.
- Read multi-step agent trajectories and identify *when* the agent searched, *what* it fetched, and *why* the answer is (or isn't) grounded.
- Handle the real failure modes of web I/O: empty results, paywalls, timeouts, irrelevant pages, rate limits.
- Implement repeated-action detection so an agent doesn't loop on the same dead query.
- Track citations cleanly — the *URLs the agent actually read*, not just URLs it saw in search results.
- Recognize when to surface "I couldn't find a confident answer" rather than hallucinate.

## 📋 Prerequisites

**Read first:**

- 📖 [Search tools](../../concepts/tools/search-tools.md) — the conceptual framing this lab builds on
- ⚙️ [Search backends snapshot](../../tools/search/snapshot-v1.0.md) — verified versions and APIs

**Complete first:**

- 🧪 [Lab 01: First agent from scratch](../../labs/01-first-agent-from-scratch/) — Lab 03 reuses Lab 01's loop and extends it.
- 🧪 [Lab 02: Tool design and selection](../../labs/02-tool-design-and-selection/) — Lab 03 reuses Lab 02's structured-error pattern.

You can skip Lab 05 (the LangGraph rewrite) without consequence. Lab 03 stays from-scratch on purpose.

**Setup:**

Python 3.11+ with the repo's environment. Three new dependencies:

```bash
uv add 'ddgs>=9.0,<10' 'beautifulsoup4>=4.12' 'requests>=2.31'
```

Optional, if you want to swap in Tavily later:

```bash
uv add 'tavily-python>=0.5'
# then export TAVILY_API_KEY=tvly-...
```

The default lab path needs no API key for search. You'll still need an `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for the model.

## 🛠 Tools and versions

| Library | Version | Verified |
|---|---|---|
| `ddgs` | `>=9.0,<10` (latest: `9.14.4` as of 2026-05-24) | 2026-05-24 |
| `tavily-python` *(optional alternative)* | `>=0.5` | 2026-05-24 |
| `beautifulsoup4` | `>=4.12` | 2026-05-24 |
| `requests` | `>=2.31` | 2026-05-24 |
| `openai` *or* `anthropic` | from prior labs | 2026-05-24 |

Pinned APIs and primary-source links live in [the snapshot page](../../tools/search/snapshot-v1.0.md). If you're running this lab more than ~3 months after the verification date, re-check the snapshot first — search libraries change behavior faster than most other tools.

## What you'll build

Same `run_agent(question) → answer` shape as Lab 01, but the *trajectory* is meaningfully longer and the answer must include `citations`:

```python
result = run_agent("What were the headline announcements at LangChain 1.0 in October 2025?")
# {
#     "answer": "LangChain 1.0 launched on Oct 22, 2025 with ...",
#     "citations": [
#         {"url": "https://blog.langchain.com/...", "title": "...", "used_in": "..."},
#         {"url": "https://...", "title": "...", "used_in": "..."},
#     ],
#     "steps": 5,
#     "stopped_reason": "answer_with_citations"
# }
```

Two tools:

1. **`web_search(query, recency="any", max_results=8)`** — returns ranked snippets via `ddgs`. The `recency` argument lets the model scope by freshness.
2. **`fetch_page(url, max_chars=8000)`** — fetches and cleans a single page via `requests` + `beautifulsoup4`. Returns structured results: `ok`, `error` (with `kind`), or `too_long` (with truncation).

One loop, with explicit:

- **Step cap** (default 8 steps) and a graceful "couldn't find confident answer" exit.
- **Repeated-action detection** so the agent doesn't re-search the same query or re-fetch the same URL.
- **Citation tracking** in the loop's state, not in the LLM's working memory.

## Steps

The notebook walks through these in order:

**0. Setup.** Imports, env, provider-agnostic LLM client (OpenAI default, Anthropic alternative).

**1. The `web_search` tool.** Wrap `ddgs.text(...)` with the structured-error pattern from Lab 02. Demonstrate rate-limit handling and empty-result handling on canned scenarios.

**2. The `fetch_page` tool.** Wrap `requests.get` + `BeautifulSoup` with the same structured-error pattern. Handle timeouts, 4xx/5xx, paywalls (content-length heuristic), and truncation for very long pages.

**3. The agent loop.** Lab 01's loop, with two changes:
   - A `seen_actions` set tracks `(tool_name, args_hash)` tuples to detect repeated actions.
   - A `citations` list tracks every URL the agent *fetched* (not just searched) — the source of truth for the final citations.

**4. The system prompt.** Three paragraphs covering: how to use snippet vs. full-page fetches, when to give up and re-search, when to surface "no confident answer." This is where the agent learns the *strategy*, not just the mechanics.

**5. Three test queries.** Easy / Medium / Hard, with sample trajectories:
   - **Easy:** "What is LangGraph?" — typically resolves in 1 search + 0–1 fetches.
   - **Medium:** "What were the major announcements at LangChain 1.0?" — 1–2 searches + 1–2 fetches, requires synthesis across sources.
   - **Hard:** A multi-hop question requiring iterative refinement, e.g., "Which Python search library did the ddgs project rename from, and why?" — search → fetch → realize the answer is partial → re-search → fetch → synthesize.

**6. Failure-mode walkthrough.** Drive the agent into each failure mode (empty results, timeout, paywall heuristic, rate-limit simulation) and observe the recovery. This is the heart of the lab.

**7. Citations check.** After each query, inspect `result["citations"]`. Are the URLs the ones the agent actually *read*? Or did some leak in from a search-results page the agent never opened?

**8. (Stretch) Swap the search backend to Tavily.** With `TAVILY_API_KEY` set, the `web_search` tool's body is a 6-line change. Same agent, same loop — the backend is genuinely pluggable.

## What we *don't* do in this lab

Anti-scope, kept explicit because the temptation is strong:

- **No vector stores or embeddings.** That's Path 02.
- **No multi-agent topologies.** That's Path 03.
- **No LangGraph.** Reserving framework treatments for Lab 05+ rewrites.
- **No LangSmith tracing.** Path 06.
- **No JavaScript-rendered pages.** `requests` + `beautifulsoup4` can't run JS, and that's fine — adding Playwright or Selenium would 5× the install footprint and isn't the point. Pages that require JS to render content count as "fetch failed."
- **No advanced anti-bot evasion.** We respect ToS and back off when rate-limited.

This is intentional. The lab's headline is "what does it take to build a research agent that handles the real web?" — adding more surface area dilutes the answer.

## Common gotchas

A few things that catch people on the first run:

- **The first search-result run is slow.** `ddgs`'s first request often takes 5–15 seconds because it's cold-starting the backend fallback chain. Subsequent calls are faster. This is normal; don't add timeouts that fire on the first call.
- **Rate limits kick in around 10–20 queries in quick succession.** If you re-run the notebook many times during development, expect `RatelimitException`. Wait 60 seconds or switch to Tavily.
- **`BeautifulSoup` warnings on raw HTML** are normal — `bs4` whines about not using a strict parser. We silence them in the lab.
- **Snippets in results may contain rendering artifacts** like `&amp;` or stray HTML tags. The lab includes a tiny `clean_text` helper. Don't let learners over-engineer this; the agent can handle moderate noise.
- **The model sometimes "hallucinates a citation"** — emits a URL in the answer that it never fetched. The lab's citation tracker catches this by only listing URLs from the tool-call log, not from the model's claims. Make sure learners trust the tracker, not the model.

## Solution discussion

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) with notes in [`solution/README.md`](./solution/README.md). 17 cells vs the lab's 35; the three-failure-mode walkthrough is removed since the hardening ships as default behavior. Three design choices worth flagging:

- **We deliberately don't use `ddgs.extract(url)`** for `fetch_page`. It works and produces cleaner Markdown — but the whole point of `fetch_page` is to make the HTTP failure modes visible. Abstracting them away defeats the lab. Production code should consider `ddgs.extract` or `tavily_client.extract`.
- **`max_chars=8000` on `fetch_page` is a deliberately tight cap.** Real pages can be 100K+ characters. The cap forces the agent to deal with truncation as a real failure mode, which is what production agents face when context-budgeting.
- **The system prompt nudges the model to fetch sparingly.** Without that nudge, the model will fetch every result it sees, blowing through context. With the nudge, it actually triages — which is the behavior we want to teach.

## 🧮 Going deeper

- 🧮 [Agents as policies](../../math-foundations/04-agents-as-policies.md) — multi-step research is where trajectory length $T$ stops being trivial. Reward sparsity (only the final answer is "graded") matters.
- 📖 [Tool design](../../concepts/tools/tool-design.md) — every structured-error pattern from Lab 02 appears here on real I/O.

## ✅ Check your understanding

After finishing the lab, take the quiz:

- 🧠 [`quizzes/foundations/multi-step-research-agent.md`](../../quizzes/foundations/multi-step-research-agent.md) — 8 questions on multi-step trajectories, citation handling, and search-failure modes.

If you score below 6/8, re-read the search-tools concept page and the failure-mode walkthrough in step 6 of the notebook.

## What comes next

You've now built a research agent that handles the real web. The Foundations path is practically complete.

- **Path 02 — Agentic RAG** is the natural next step. Same multi-step pattern, but the corpus is yours (documents you indexed) instead of the public web. Citation tracking transfers cleanly.
- **Path 03 — Multi-Agent Systems.** What happens when one agent isn't enough — a researcher feeding a synthesizer, a planner managing executors, etc.
- **Path 06 — Evaluation & Observability.** Once you have a research agent, how do you tell if it's any good? Trajectory-level evaluation, citation accuracy metrics, hallucination detection.
