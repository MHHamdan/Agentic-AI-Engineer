# 01 · Foundations

> 🟢 Beginner-friendly · ⏱ 14–20 hours · 📍 Start here if you're new to agents

## Who this is for

You've called LLM APIs and built simple chat features, but you haven't built a *real* agent — one that uses tools, observes results, and decides what to do next. This path takes you from "I can prompt a model" to "I can build an agent loop from scratch, design tools the model can actually use, ship a multi-step research agent against the real web, rebuild any of these in LangGraph, and explain why each version exists."

By the end you should be able to:

- Explain the agent loop in your own words and identify it in any framework's code.
- Build a tool-using agent from scratch in Python, with no framework.
- Read modern function-calling APIs (OpenAI, Anthropic) and emit structured tool calls.
- Design tool schemas, descriptions, and return contracts that the model uses correctly.
- Recognize the common agent failure modes — both in the loop and in tool selection — and know what causes each.
- Build a research agent that handles the real web: rate limits, paywalls, 404s, noisy snippets, and citation tracking.
- Rebuild your from-scratch agent in LangGraph and articulate *what the framework adds* (state, routing, checkpointing, human-in-the-loop) vs. what stays the same (the model, the tools, the agent's reasoning).
- Understand the formal framing — agents as policies — well enough to read papers without getting stuck on notation.

## Prerequisites

- Python at intermediate level (type hints, async basics, working with libraries).
- Familiarity with an LLM API. If you've ever called `client.chat.completions.create(...)`, you're ready.
- No prior agent or framework experience needed.

If you're missing any of the above, work through them first — the rest of the path won't make sense without them.

## How this path is structured

The Foundations path layers five things in parallel: **concepts** (the ideas), **labs** (the practice), **math** (the formal grounding), **quizzes** (self-assessment after each module), and a **framework bridge** (rebuilding the same agent in LangGraph to see what the abstractions buy you). You can follow them strictly in order, or read the concepts first and come back to the math when you want to go deeper.

```mermaid
flowchart LR
    A[📖 What is an agent?] --> B[📖 Agent loop]
    B --> C[📖 ReAct pattern]
    C --> D[🧪 Lab 01: First agent from scratch]
    D --> T1[📖 Tool design]
    T1 --> T2[📖 Tool selection]
    T2 --> E[🧪 Lab 02: Tool design and selection]
    E --> S1[📖 Search tools]
    S1 --> R[🧪 Lab 03: Multi-step research agent]
    R --> M1[🧮 Math: Notation]
    M1 --> M2[🧮 Math: Agents as policies]
    M2 --> M3[🧮 Math: ReAct formalized]
    M3 --> F1[📖 Agents vs frameworks]
    F1 --> F2[🧪 Lab 05: LangGraph rewrite]
    F2 --> Q[🧠 Quizzes]
    Q --> H[Next path]
```

## The reading list

### Module 1 — Vocabulary

Before code, get the words right. These three concept pages define the terms the rest of the repo uses.

1. 📖 **[What is an agent?](../../concepts/agents/what-is-an-agent.md)** *(~10 min)* — The minimum definition: a system that uses an LLM to decide what to do next in a loop. Distinguishes agents from pipelines and explains why the loop matters more than the model size.

2. 📖 **[The agent loop](../../concepts/agents/agent-loop.md)** *(~10 min)* — The four-step cycle (perceive → reason → act → observe) every agent runs, with vocabulary for state, action, and observation. Covers stopping conditions explicitly.

3. 📖 **[The ReAct pattern](../../concepts/agents/react-pattern.md)** *(~10 min)* — The specific way modern agents structure the *reason* step: interleaved thoughts, actions, and observations. From Yao et al. (ICLR 2023).

> 💡 By the end of this module you should be able to read any "what is an AI agent" article online and (a) follow it, and (b) notice when it's wrong.

### Module 2 — Build the loop

Now make it real.

4. 🧪 **[Lab 01: First agent from scratch](../../labs/01-first-agent-from-scratch/)** *(~60–90 min)* — Build a working ReAct agent in ~150 lines of Python, no framework. Covers:
   - A provider-agnostic LLM wrapper.
   - Pydantic-typed tools with auto-generated schemas.
   - The loop, with thoughts, actions, and observations.
   - Structured error handling.
   - Repeated-action detection and step caps.

> 💡 This lab is the foundation for every later lab. Take your time. If something doesn't make sense, the concept pages in Module 1 will usually have the missing piece.

### Module 3 — Design tools that work

Most "the agent doesn't work" problems are tool problems wearing a costume. This module teaches you to see them — first on a canned domain, then on the real web.

5. 📖 **[Tool design](../../concepts/tools/tool-design.md)** *(~12 min)* — Name, description, schema, return contract, executor. Schema patterns (one-tool-per-intent, discriminated unions, pagination). The seven common tool-design mistakes mapped to symptoms and fixes.

6. 📖 **[Tool selection](../../concepts/tools/tool-selection.md)** *(~12 min)* — How the model picks among tools; the four levers (system prompt, descriptions, history, `tool_choice`); the five selection-failure modes; pruning strategies for large toolsets.

7. 🧪 **[Lab 02: Tool design and selection](../../labs/02-tool-design-and-selection/)** *(~90–120 min)* — Take Lab 01's agent, give it a deliberately-broken toolset, watch it fail, then fix the *tools alone* (not the agent code) and watch it become reliable. Covers strict-mode schemas, structured errors, destructive-action gates, `tool_choice` modes, parallel tool calls, and a stretch routing pattern.

8. 📖 **[Search tools](../../concepts/tools/search-tools.md)** *(~9 min)* — Why search tools differ from deterministic ones: probabilistic results, top-k triage, snippet vs. full-page tradeoffs, freshness, citation tracking, the failure modes of the open web, and why search is *not* RAG.

9. ⚙️ **[Search backends snapshot](../../tools/search/snapshot-v1.0.md)** *(~5 min reference)* — The pinned versions, APIs, and tradeoffs for `ddgs` (the default, no API key) and `tavily-python` (the production-oriented alternative). Read before Lab 03.

10. 🧪 **[Lab 03: Multi-step research agent](../../labs/03-multi-step-research-agent/)** *(~90–120 min)* — Build a research agent against the real web. Two tools (`web_search`, `fetch_page`), one loop, real failure modes: rate limits, paywalls, timeouts, empty results, irrelevant pages. Citation tracking, repeated-action detection, graceful step-cap exits.

> 💡 If you've built agents in a framework before, Module 3 is where you'll most often realize the bugs you thought were "model issues" were actually tool-design issues. Lab 03 in particular exercises every Lab 02 pattern on real I/O — paywalls and timeouts are the real-world equivalents of Lab 02's canned errors.

### Module 4 — The math, lightly

Optional but recommended. These pages connect what you just built to the formal language used in research papers.

11. 🧮 **[Notation reference](../../math-foundations/notation.md)** *(~5 min)* — The symbols and conventions used across all math pages. Bookmark it.

12. 🧮 **[Agents as policies](../../math-foundations/04-agents-as-policies.md)** *(~10 min)* — The framing $\pi_\theta(a_t \mid s_t)$. Connects the loop you wrote to RL vocabulary without pretending you're doing RL. Tool design changes $\mathcal{A}$; tool selection is a distribution over it.

13. 🧮 **[The ReAct loop, formalized](../../math-foundations/06-react-formalization.md)** *(~8 min)* — The same equation, specialized for the thought-action structure. Explains *why* the thought helps.

> 💡 You can skip these and still build working agents. They become valuable when you start debugging *why* an agent is misbehaving — the formal vocabulary maps onto specific failure modes.

### Module 5 — Bridge to frameworks

You've built the agent. Now build it again — in a framework — and see what shifts.

14. 📖 **[Agents vs. frameworks](../../concepts/agents/agents-vs-frameworks.md)** *(~12 min)* — When does a framework pay off? Eight dimensions where from-scratch and LangGraph differ (readability, state, debugging, reliability, checkpointing, human approval, maintainability, learning value), plus a decision table. Honest about tradeoffs; doesn't pretend frameworks fix tool-design problems.

15. ⚙️ **[LangGraph tool snapshot](../../tools/langgraph/snapshot-v1.0.md)** *(~5 min reference)* — The pinned versions, APIs, deprecations, and freshness check. Read once before Lab 05; refer back when you write your own LangGraph code.

16. 🧪 **[Lab 05: LangGraph rewrite of Lab 01](../../labs/05-langgraph-rewrite/)** *(~90–120 min)* — Rebuild Lab 01's agent in LangGraph 1.x: `StateGraph`, `MessagesState`, `add_messages` reducer, `ToolNode`, `tools_condition`. Then go beyond Lab 01 with `InMemorySaver` (checkpointing) and `interrupt(...)` / `Command(resume=...)` (human-in-the-loop). Same domain, same queries — only the wiring changes.

> 💡 This module is *deliberately* the last one in Foundations, not the first. Building the loop by hand first means you'll see LangGraph as "the same thing, organized differently" rather than as magic. If it feels like magic, go back to Lab 01.

### Module 6 — Quizzes

Self-assessment after the material above. Aim for 6/8 or better on each.

17. 🧠 **[Agents — basics](../../quizzes/foundations/agents-basics.md)** *(~7 min)* — Covers `what-is-an-agent.md`.
18. 🧠 **[The agent loop](../../quizzes/foundations/agent-loop.md)** *(~8 min)* — Covers `agent-loop.md`.
19. 🧠 **[The ReAct pattern](../../quizzes/foundations/react-pattern.md)** *(~7 min)* — Covers `react-pattern.md`.
20. 🧠 **[Tool design and selection](../../quizzes/foundations/tool-design-and-selection.md)** *(~8 min)* — Covers both tool concept pages and Lab 02.
21. 🧠 **[Multi-step research agent](../../quizzes/foundations/multi-step-research-agent.md)** *(~8 min)* — Covers `search-tools.md`, the search-backends snapshot, and Lab 03.
22. 🧠 **[LangGraph basics](../../quizzes/foundations/langgraph-basics.md)** *(~8 min)* — Covers `agents-vs-frameworks.md`, the LangGraph snapshot, and Lab 05.

Each quiz is 8 single-select questions with `<details>`-block answers. Every question has a `review:` field pointing to the exact source section, so if you miss one, you know exactly where to read again.

> 💡 The quizzes work on GitHub directly — no JavaScript, no build step. The YAML front-matter is also designed for a future interactive renderer, so the same content will eventually power a richer experience without rewriting.

## Topics this path deliberately doesn't cover

This is Foundations. We're keeping the surface small. The path does **not** cover:

- ADK, CrewAI, AutoGen — other frameworks each get their own bridge lab in later batches.
- Retrieval and RAG — that's the next path: [02 Agentic RAG](../02-agentic-rag/). Lab 03's web-search-and-cite pattern transfers cleanly; only the corpus changes.
- Multi-agent topologies (`langgraph-supervisor`, `langgraph-swarm`, custom hierarchies) — [03 Multi-Agent Systems](../03-multi-agent-systems/).
- Evaluation, observability, production concerns — [06](../06-evaluation-observability/) and [07](../07-production-and-safety/).
- MCP and A2A protocols — [04 Tool Protocols](../04-tool-protocols-mcp-a2a/).
- LangSmith tracing and LangGraph middleware — covered in their respective paths when we get to evaluation and production concerns.

The goal of Foundations is to make all of those *legible*. You'll come back here whenever a later concept references the agent loop, tool design, search tools, or the LangGraph runtime.

## What's next

Once you can explain the agent loop, have Labs 01, 02, 03, and 05 running, and have passed all six quizzes at 6+/8:

- **Heading toward RAG?** → [02 Agentic RAG](../02-agentic-rag/). Treats retrieval as a tool, not a pipeline. Lab 03's citation pattern transfers directly to chunk-level provenance.
- **Heading toward multi-agent?** → [03 Multi-Agent Systems](../03-multi-agent-systems/). Supervisor, hierarchical, swarm — all built on the LangGraph runtime you now know.
- **Theory-curious?** → [08 Mathematical Foundations](../08-mathematical-foundations/) goes deeper.

## A note on time

The 14–20 hour estimate is honest. Most of it is the four labs — first-time setup, working through the cells, occasionally re-reading a concept page when something doesn't click. If you've built agents before in a framework, you can skim the concepts and finish in 8–10 hours. If LLM APIs and frameworks are both new, expect closer to 22.

---

## References

Foundational sources cited in this path:

- Yao, S. et al. (2023). [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629). ICLR 2023.
- Sumers, T. R. et al. (2024). [*Cognitive Architectures for Language Agents*](https://arxiv.org/abs/2309.02427). TMLR 2024.
- Schick, T. et al. (2023). [*Toolformer: Language Models Can Teach Themselves to Use Tools*](https://arxiv.org/abs/2302.04761). NeurIPS 2023.
- Patil, S. G. et al. (2024). [*Gorilla: Large Language Model Connected with Massive APIs*](https://arxiv.org/abs/2305.15334). NeurIPS 2024.
- Lewis, P. et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. Useful as the contrast to web search (covered in Lab 03's prerequisites).
- LangChain team (2025). [*LangChain and LangGraph Agent Frameworks Reach v1.0 Milestones*](https://blog.langchain.com/langchain-langgraph-1dot0/). The official 1.0 announcement.
- LangChain docs. [*LangGraph migration guide*](https://docs.langchain.com/oss/python/migrate/langgraph-v1).
- Anthropic (2024). [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents).
- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.), Ch. 2.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). [Free online](http://incompleteideas.net/book/the-book-2nd.html).
- UC Berkeley CS294/194-196 *LLM Agents*, Fall 2024. [Course page](https://rdi.berkeley.edu/llm-agents/f24).
- UC Berkeley CS294/194-196 *Agentic AI*, Fall 2025. [Course page](https://rdi.berkeley.edu/agentic-ai/f25). Used as a benchmark for topic coverage on planning, tool use, and evaluation.
