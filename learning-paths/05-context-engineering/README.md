# Path 05 — Context Engineering

> 🟡 Intermediate · ⏱ 4–8 hours (planned) · 📍 Start here after Path 01 + one of Path 02 or Path 03 · 🚧 **v1 in progress** — Modules 1 + 2 shipped (Batch 59); Modules 3-6 forthcoming

> 🚧 **v1 in progress — 2 of 6 modules shipped.** Modules 1 (Context engineering foundations) and 2 (Token budgets per zone) shipped in Batch 59 — the opening pair the scaffold below named as the natural first batch. The foundational pages live at [`concepts/context/foundations.md`](../../concepts/context/foundations.md) and [`concepts/context/token-budgets.md`](../../concepts/context/token-budgets.md). Modules 3-6 are in the build queue. The "What you can read right now" section below points at adjacent artifacts the remaining modules will build on.

## Who this path is for

Engineers with a working agent whose context window is the bottleneck. Symptoms: agents that re-read files they already processed, decisions that get re-derived three handoffs later, $0.50 trajectories that should cost $0.05, response latency that scales with conversation length. You've felt the 24-entries-cost-594-tokens vs 500-entries-cost-8,000-tokens problem (per niteagent / Mem0 2026) and you want the discipline that fixes it.

## What you'll be able to do

When this path is complete, you'll be able to:

- Explain the **three context zones** — system prompt (stable instructions), dynamic context (retrieved documents, tool results, conversation history), current query — and **allocate explicit token budgets per zone** per harnessengineering.academy April 2026.
- **Measure context utilization rate, compression ratio, and retrieval precision** as first-class metrics. The 83% → 96% task-completion gain from context-pipeline redesign vs the 85% → 88% gain from prompt-tuning is the canonical lift comparison per harnessengineering.academy.
- **Detect context drift in long-running sessions** — agents re-reading files, re-stating prior decisions, gradually reframing the task away from user intent. These patterns appear in step-level traces before they surface in output quality per machinelearningmastery April 2026.
- **Decide between prompt engineering and context engineering** for a given problem. Single-turn tasks: prompt engineering. Multi-step agent workflows: context engineering dominates per logic.inc April 2026.
- **Apply the six core context-engineering techniques** — selection, compression, summarization, structured truncation, retrieval-as-tool, and memory-tier separation — and know when each helps vs hurts.
- **Use long-context models well** when they're the right call. Claude Sonnet 4 ships 1M tokens in beta for tier-4+ orgs at 2× input pricing above 200K (per aimultiple February 2026); MiniMax-M1-80k native 1M; Qwen3-30B-A3B 256K extendable to 1M. Choosing the right context size for the workload is part of the discipline.

## Prerequisites

- **Path 01 Foundations** complete. You have a working agent loop and you understand tool-calling.
- **One of Path 02 (Agentic RAG) or Path 03 (Multi-Agent Systems)** — context engineering pays off where retrieval and multi-step trajectories create the context bloat in the first place.
- Comfort with measuring token counts and reading trace data is helpful.

## Path structure (planned)

The planned module breakdown:

| Module | Topic | Status |
|---|---|---|
| 1 | **Context engineering foundations** — the three zones; the prompt-vs-context distinction; why frontier-model capability ceilings shifted the bottleneck to context per logic.inc April 2026 | ✅ Shipped (Batch 59) — [`concepts/context/foundations.md`](../../concepts/context/foundations.md) |
| 2 | **Token budgets per zone** — explicit allocation; soft caps and hard caps; per-tenant budget tiers (extends Path 03 Pattern 4 to the system-prompt + dynamic-context zones) | ✅ Shipped (Batch 59) — [`concepts/context/token-budgets.md`](../../concepts/context/token-budgets.md) |
| 3 | **Compression and summarization** — when to compress, when to truncate, when to summarize; lossy vs lossless; the recursive summarization trap | 📋 Planned |
| 4 | **Memory tiers** — short-term (conversation buffer) vs long-term (vector DB) vs episodic (past traces); the Mem0 memory-injection 594→8,000-token cost progression | 📋 Planned |
| 5 | **Context drift detection** — the four early-warning signals (re-reads, re-decisions, task reframing, retrieval-precision collapse); instrumenting at trace level | 📋 Planned |
| 6 | **Long-context models — when they help and when they don't** — the 1M-token tier (Claude Sonnet 4 beta, MiniMax-M1, Qwen3); pricing tier cliffs; the "needle in haystack" performance degradation; choosing context size as a design decision | 📋 Planned |

Each module will follow the Path 01/03/06 shape: concept page(s) + lab + quiz, with reference solutions where labs apply.

## What you can read right now

The repo already has substantive material that maps to this path. None of it is a duplicate of what Path 05 will eventually ship — these are adjacent artifacts that will be cross-referenced from the modules above when they land:

**Cost and budget context** (the Path 03 Pattern 4 connection):
- [Path 03 Pattern 4 — Per-agent cost budgeting](../03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) — the per-agent budget envelope; Path 05 Module 2 will extend this to per-zone budgets within a single agent's context window
- [Path 03 Pattern 2 — Shared-state boundaries](../03-multi-agent-systems/patterns/02-shared-state-boundaries.md) — the 15× token-burn case from full-transcript inlining is the canonical context-engineering failure mode

**Observability context** (the Path 06 connection):
- [Path 06 Module 6 cost attribution](../06-evaluation-observability/) — the baggage-propagation infrastructure that makes per-zone token measurement work
- [Path 06 adaptive sampling](../../concepts/evaluation/adaptive-sampling.md) — cost-driven policies; the cost-control runbook
- [`production/README.md`](../../production/README.md) — the production playbook; `cost-engineering.md`, `caching-and-routing.md` are the planned pages most relevant to Path 05

**RAG context** (the Path 02 connection):
- [Path 02 Agentic RAG](../02-agentic-rag/) — retrieval as a tool, not a pipeline; this is where dynamic-context-zone token consumption originates in most production agents
- [`concepts/rag/retrieval-strategies.md`](../../concepts/rag/retrieval-strategies.md), [`hybrid-search.md`](../../concepts/rag/hybrid-search.md), [`reranking.md`](../../concepts/rag/reranking.md) — retrieval choices that determine how much dynamic context lands in the window

**Foundational reading** (start here before the path lands):
- Anthropic (2024), *[Building effective agents](https://www.anthropic.com/research/building-effective-agents)* — context handling appears throughout
- Martin Fowler's *harness engineering* framing — context engineering as one of three pillars (alongside architectural constraints and entropy management)
- The OpenAI / Anthropic / Google long-context model documentation for the model your team uses

## What's not in this path (anti-scope)

When Path 05 ships, these are explicitly out of scope:

- **Vector database choice and tuning** — that's the [`concepts/rag/`](../../concepts/rag/) directory and Path 02. Path 05 covers how the agent *uses* retrieved context, not how retrieval is implemented.
- **Prompt engineering for single-turn tasks** — Path 05 is the *multi-step* / *long-running* counterpart. For single-shot prompt optimization, see the foundational prompt-engineering literature (OpenAI cookbook, Anthropic prompt-engineering docs).
- **Production observability infrastructure** — that's [Path 06](../06-evaluation-observability/). Path 05 will use Path 06's tracing patterns to *detect* drift but won't re-derive the observability stack.
- **Specific framework abstractions** — LangChain's `ConversationBufferMemory`, LangGraph's `checkpointer`, OpenAI Agents SDK's memory APIs all change quickly. Path 05 covers the *technique*; framework wrappers are addressed at the conceptual layer only.
- **Per-token model selection at runtime** — that's a downstream of context budgets but it's a model-routing concern (Path 06 cost attribution territory). Path 05 sets the budgets; routing reads them.

## What comes next

Contributions are welcome. The way to help build Path 05:

1. **Open an issue or discussion** describing which module you want to contribute to (concept page, lab, or both).
2. **Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md)** — the source-citation rules and the per-content-type templates are non-negotiable.
3. **Pick one module's scope, not the whole path.**

The first batch (Modules 1 + 2 — foundations + token budgets per zone) shipped in Batch 59 — the opening pair this scaffold's earlier draft named as the natural first batch. The natural next batch would be Module 3 (Compression and summarization) + Module 4 (Memory tiers), which together address how the budget gets *enforced* dynamically (compress when soft caps fire) and how the multi-tier memory architecture separates short-term conversation buffer from long-term vector DB from episodic past traces.

## References

Seed references for the modules that will land. Each module will add its own; these are the foundational sources Path 05 will build on:

**Context engineering as a discipline**:
- harnessengineering.academy (April 2026), *[Context Engineering: The Key Skill Every AI Developer Needs in 2026](https://harnessengineering.academy/blog/context-engineering-the-key-skill-every-ai-developer-needs-in-2026/)* — the three-zone model; the 83%→96% task-completion lift comparison vs prompt engineering's 85%→88%
- logic.inc (April 2026), *[Context engineering guide for AI teams 2026](https://logic.inc/resources/context-engineering-guide-for-ai-teams)* — "Frontier model capability has closed the prompting gap; the failures you see in production today are almost always context failures"
- machinelearningmastery.com (April 2026), *[Effective Context Engineering for AI Agents: A Developer's Guide](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/)* — production metrics (context utilization rate, compression ratio, retrieval precision); the four context-drift signals
- Martin Fowler — the harness-engineering framing (context engineering as one of three pillars of agent infrastructure)

**Long-context models**:
- aimultiple.com (February 2026), *[Best LLMs for Extended Context Windows in 2026](https://aimultiple.com/ai-context-window)* — Claude Sonnet 4 1M-token beta with 2× input / 1.5× output pricing above 200K; Cohere Command-R+ retrieval-optimized; OpenAI GPT-4 Turbo behavior at high context
- siliconflow.com (2026), *[The Best Open Source LLM for Context Engineering in 2026](https://www.siliconflow.com/articles/en/the-best-open-source-llm-for-context-enginneering)* — Qwen3-30B-A3B-Thinking-2507 256K extendable to 1M; MiniMax-M1-80k native 1M with lightning attention
- IBM, *[What is a context window?](https://www.ibm.com/think/topics/context-window)* — foundational definition; working-memory framing

**Memory and cost interaction**:
- niteagent.com (May 2026), *[AI Agent Cost Optimization in 2026](https://niteagent.com/blog/ai-agent-cost-optimization-2026/)* — Mem0 2026 memory-injection scaling (24 entries = 594 tokens; 500 entries = 8,000 tokens); production traces show 80-120K token contexts within 2-3 weeks of deployment

**Adjacent repo content**:
- [Path 03 Pattern 4 — Per-agent cost budgeting](../03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) — per-agent envelope (Path 05 extends to per-zone)
- [Path 03 Pattern 2 — Shared-state boundaries](../03-multi-agent-systems/patterns/02-shared-state-boundaries.md) — the 15× token-burn case
- [Path 06 Evaluation & Observability](../06-evaluation-observability/) — cost attribution and adaptive sampling infrastructure
- [`production/README.md`](../../production/README.md) — the production playbook
- [`concepts/rag/`](../../concepts/rag/) — RAG concept pages that determine dynamic-context shape
