# Project 01 — Personal research assistant

> 🟢 Beginner · ⏱ 15-20 hours · 📍 First project after Path 01 · 🛠 Verified 2026-05-29

## What you're building

A research agent that takes a topic, plans an investigation, browses multiple web sources, synthesizes findings, and produces a citation-grounded report. The agent runs as a CLI or a small web UI; the deliverable is a working agent plus a write-up plus three example research outputs you can show off.

The 2026 production framing per [arxiv:2601.09688 (January 2026)](https://arxiv.org/html/2601.09688v1) on the DeepResearchEval benchmark: "Deep research systems are a specialized class of agents designed for complex, multi-stage investigative tasks. Unlike conventional QA systems, they autonomously plan long-horizon workflows, navigate heterogeneous web sources, and synthesize information into structured, citation-grounded reports."

You're building a stripped-down version of what OpenAI Deep Research, Perplexity Sonar Pro, and Gemini Deep Research do under the hood. The full commercial systems are 20-30 page report generators with 30-minute research budgets; yours will be a 2-4 page report generator with a 3-5 minute research budget. That's sufficient to learn the architecture and to ship something useful.

## Why this matters

The research agent is the canonical first agentic build for three reasons:

1. **It exercises every Path 01 primitive** — the agent loop, tool calling, conversation state, structured outputs. If you can ship this, you understand the foundations.
2. **It produces a visible deliverable** — a written report with citations. You can put a finished research output in front of a non-engineer and get useful feedback.
3. **It's a real workflow people use** — once it works, you'll use it. The dogfooding loop tightens your evaluation discipline naturally.

The 2026 distinction per [arxiv:2601.09688](https://arxiv.org/html/2601.09688v1): deep research systems generate citation-grounded reports across multi-stage investigations that traditionally require substantial human effort. That's the value proposition. You're building a personal version of a commercial product.

## Prerequisites

| Required | Why |
|---|---|
| **Path 01 — Foundations** complete | The agent loop, tool calling, and structured outputs all live here |
| Working Python 3.10+ environment | The repo's environment baseline |
| Anthropic API key (or OpenAI / similar) | The model the agent runs on |
| A web search API account | One of: Tavily ($5/mo for hobby), Exa (free tier), Perplexity Sonar ($5/1K searches), or Serper |
| Comfort with `git`, basic CLI tools | Standard software engineering practice |

Helpful but not required: Path 02 (light retrieval — useful if you want to add a "researched once before" cache).

## What you'll build

Three concrete deliverables:

1. **A working CLI agent** — `python research.py "topic here"` produces a markdown report
2. **Three example research outputs** — research three different topics you actually care about; commit the outputs as `examples/01.md`, `examples/02.md`, `examples/03.md`
3. **A write-up** — a `WRITEUP.md` that documents your architecture choices, what surprised you, and what you'd do differently

Optional fourth deliverable: a small web UI (FastAPI + a single HTML page) if you want a portfolio screenshot.

## Architecture overview

The agent has three logical phases per the [DeepResearchEval framing](https://arxiv.org/html/2601.09688v1) ("iterative web browsing, targeted information retrieval, cross-source verification, and multi-perspective synthesis"):

| Phase | What happens | Inputs | Outputs |
|---|---|---|---|
| **1 — Plan** | Decompose the topic into 3-7 specific sub-questions | User's topic | Structured plan (list of sub-questions) |
| **2 — Research** | For each sub-question, run a web search, fetch the top results, extract the relevant content | Sub-questions | Source-grounded notes per sub-question |
| **3 — Synthesize** | Combine the notes into a structured report with inline citations | All notes | Markdown report with `[1]`, `[2]`, etc. citations |

The tool surface stays minimal:

| Tool | Used in phase | Implementation |
|---|---|---|
| `web_search(query)` → list of URLs + snippets | 2 | Tavily / Exa / Perplexity / Serper — pick one |
| `web_fetch(url)` → page content (or PDF text) | 2 | `httpx` + a markdown converter like `trafilatura` or `markdownify` |
| `write_report(title, body)` → saves to disk | 3 | Just file I/O — separate tool keeps the agent's reasoning clean |

The model call wraps all three phases. The simplest topology: a single LLM with all three tools available and a system prompt that defines the plan→research→synthesize flow. The agent does the orchestration in its reasoning chain.

Per [Firecrawl May 2026](https://www.firecrawl.dev/blog/best-deep-research-apis): "Choose Tavily when you need simple search grounding for existing LLM applications" — Tavily's simplicity makes it the recommended default for this project; the other APIs are upgrades you can explore later.

## Milestones

Five phases, each ending with a working checkpoint. Time estimates assume comfort with Path 01 material.

### Milestone 1 — The hello-world agent (2-3 hours)

Get a single-turn agent working: takes a topic, calls `web_search` once, prints the results. No planning, no synthesis. The goal is to confirm your environment, API keys, and basic agent loop all work.

**Done when**: `python research.py "what is the airspeed velocity of an unladen swallow"` returns search results.

### Milestone 2 — The two-tool agent (3-4 hours)

Add `web_fetch`. Now the agent searches, picks the top result, fetches the page content, and returns a summary. Still single-pass; no multi-step reasoning yet.

**Done when**: the agent can answer a question that requires reading one page (not just a search snippet).

### Milestone 3 — The planning loop (3-4 hours)

Add the planning phase. The agent first decomposes the topic into sub-questions, then iteratively researches each. The reasoning chain is what makes the agent "agentic" instead of a smarter QA system.

**Done when**: for an open-ended topic like "How does AlphaFold work?", the agent generates 4-6 sub-questions, researches each, and tracks what it's found so far. Output is messy — that's expected at this milestone.

### Milestone 4 — The synthesis phase (3-4 hours)

Add the final synthesis step. The agent's accumulated notes get organized into a structured report with inline citations. The citation discipline matters per [JMIR March 2026](https://www.jmir.org/2026/1/e88195/PDF): "A recurring concern is the integrity of citations and content" — hallucinated references are the canonical failure mode you're trying to avoid.

**Done when**: a 2-4 page markdown report with `[1]`, `[2]`, etc. inline citations, and a numbered references section at the bottom that lists actual URLs. Citations point at sources the agent actually fetched, not at sources it invented.

### Milestone 5 — Polish and write-up (3-5 hours)

The agent works. Now:

- Add error handling for the canonical failures: search returns no results, fetch returns a 403/404, the page is JavaScript-only, the model returns malformed structured output
- Add basic logging — print which sub-questions are being researched, which URLs are being fetched
- Write the three example research outputs
- Write `WRITEUP.md` (see Submission guide below)

**Done when**: you can hand the repo to someone else and they can run it, read the writeup, and understand what you built.

## Evaluation criteria

What "good" looks like for this project. The four-dimension rubric:

| Dimension | What it measures | Beginner-tier target |
|---|---|---|
| **Correctness** | Does the agent produce reports that match what's actually on the cited pages? | 90%+ of citations actually support their claim (manually spot-check 10 claims per example) |
| **Coverage** | Does the agent address the topic broadly enough to be useful? | 4+ distinct sub-topics per research output |
| **Latency** | How long does a research run take? | < 5 minutes wall-clock; < 30 LLM calls total |
| **Cost** | How much does a research run cost? | < $0.50 per research at Claude Sonnet 4.6 pricing; < $0.10 per research at Haiku-class models |

The four-dimension rubric mirrors the production-evaluation patterns from Path 06. You don't need automated evals at this tier — manual spot-checks against the rubric are sufficient.

### Citation integrity as the load-bearing check

Per the [JMIR March 2026](https://www.jmir.org/2026/1/e88195/PDF) framing: deep research agents "May show weaker claim-source alignment. Higher risk of hallucinated references." That's the failure mode this project is designed to demonstrate AND defend against. Your test: pick 10 claims from each example output; for each claim, click the citation; verify the cited page actually supports the claim. Anything below 90% claim-source alignment is a fix-it-before-submitting blocker.

The fix: make the agent quote a short verbatim snippet from each source alongside the citation, in a "Sources" appendix the user can verify. This costs a few hundred extra tokens per report and dramatically improves trust.

## Stretch goals

Pick at most two. The goal is a finished project, not a feature collection.

- **Caching layer** — if the same topic was researched before, skip the web search phase and synthesize from the cached sources. Cuts cost and latency on iteration; introduces RAG concepts from Path 02.
- **Multi-modal sources** — handle PDF papers and YouTube transcripts in addition to HTML pages. The `pdfplumber` and `yt-dlp` libraries get you most of the way.
- **Critique-and-revise loop** — after synthesizing the first draft, the agent critiques its own report against the rubric and revises. Demonstrates reflexive evaluation; a tiny version of what Path 06 v1 covers in depth.
- **Web UI** — single-page HTML + FastAPI backend; portfolio screenshot.
- **Citation deduplication** — when the same URL gets cited multiple times for different claims, merge into a single reference. Small touch but visibly improves report quality.

## Anti-scope

What you don't need to do for this project:

- **Multi-agent orchestration** — that's Project 06+ territory; this is a single-agent build
- **Custom evaluation harness** — manual spot-checks against the rubric are sufficient at beginner tier
- **Production deployment** — local CLI is the deliverable; hosting waits for capstone tier
- **Observability stack** — basic print logging is fine; OpenTelemetry instrumentation isn't required
- **Authentication / user management** — single-user CLI is the assumed deployment shape
- **Real-time streaming output** — the agent can run synchronously and print the final report

If you find yourself building any of the above, you're scope-creeping. Park the feature in `STRETCH.md` and ship the smaller deliverable first.

## Resources

**Architecture references**:
- [arxiv:2601.09688 (January 2026), DeepResearchEval](https://arxiv.org/html/2601.09688v1) — the canonical 2026 framing for deep research agents; iterative web browsing + targeted retrieval + cross-source verification + multi-perspective synthesis
- [JMIR March 2026, Viewpoint Deep Research Agents](https://www.jmir.org/2026/1/e88195/PDF) — the citation-integrity failure modes and what to defend against
- [arxiv:2604.10741 (April 2026), Deep-Reporter](https://arxiv.org/html/2604.10741v2) — three-level evaluation (structural adherence / section-level grounding / full-report quality); the rubric pattern this project's evaluation criteria simplify

**Tool API documentation**:
- [Tavily docs](https://docs.tavily.com/) — recommended default; simple search-grounded API
- [Exa documentation](https://docs.exa.ai/) — embeddings-based semantic search; the discovery-phase upgrade
- [Perplexity Sonar API](https://docs.perplexity.ai/) — the deeper integration that includes their reasoning model
- [Firecrawl May 2026 comparison of deep research APIs](https://www.firecrawl.dev/blog/best-deep-research-apis) — the May 2026 landscape for picking your search backend

**Repo cross-references**:
- [Path 01 — Foundations](../../../learning-paths/01-foundations/) — every primitive this project uses
- [Path 02 — Agentic RAG](../../../learning-paths/02-agentic-rag/) — the upgrade path if you want to add the caching stretch goal
- [`concepts/agents/`](../../../concepts/agents/) — the agent-loop concept page
- [`concepts/tools/`](../../../concepts/tools/) — tool design and tool selection
- [`patterns/01-single-agent-tool-use.md`](../../../patterns/01-single-agent-tool-use.md) — the architectural pattern this project implements

## Submission guide

When you're done, three artifacts go in your repo:

1. **The agent code** — clean, with a README that explains setup and usage. Include a `.env.example` listing the API keys you need.
2. **Three example research outputs** — `examples/01.md`, `examples/02.md`, `examples/03.md`. Pick topics you actually care about; the bar is "would you read this if someone else wrote it?"
3. **`WRITEUP.md`** — a ~500-word reflection covering:
   - The architecture choice you made (which planning approach, which search backend, which model)
   - One thing that surprised you about how the agent behaved
   - One thing you'd do differently with the time you spent
   - Two stretch goals you considered and your reason for picking them (or not)

Add yourself to `docs/community/showcase.md` when you submit. We highlight community builds in the README rotation.

## What this project leads to

After Personal Research Assistant, the natural progressions:

- **Project 02 (PDF Q&A bot)** — adds Path 02 retrieval depth; same agentic-loop foundation
- **Project 04 (Data analysis agent)** — adds tool design depth; shows the same agent loop with different tool surface
- **Project 07 (Evaluated multi-agent system)** — the capstone-tier version of what you just built, with full observability, multi-agent topology, and production evaluation

The Personal Research Assistant is the foundation. The next three projects each extend one dimension of it.
