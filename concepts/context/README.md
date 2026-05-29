# Context engineering concepts

> Path 05 lives here. Context engineering is the discipline of choosing what fills the model's context window deliberately, not by accumulation. Per [logic.inc April 2026](https://logic.inc/resources/context-engineering-guide-for-ai-teams): "frontier model capability has closed the prompting gap; the failures you see in production today are almost always context failures."

## Pages

| Page | Covers | Status |
|---|---|---|
| [`foundations.md`](./foundations.md) | Three context zones; prompt-vs-context distinction; attention budget; 100:1 input-to-output ratio; canonical failure modes (suicide by context, context rot, re-reading) | ✅ Shipped (Batch 59) |
| [`token-budgets.md`](./token-budgets.md) | Five-category production allocation; soft caps + hard caps; per-tenant tiers; static vs dynamic allocation; budget enforcement in the agent loop | ✅ Shipped (Batch 59) |
| `compression-and-summarization.md` | When to compress / truncate / summarize; lossy vs lossless; recursive summarization trap | 📋 Planned (Path 05 Module 3) |
| `context-drift-detection.md` | Four early-warning signals (re-reads, re-decisions, task reframing, retrieval-precision collapse); instrumenting at trace level | 📋 Planned (Path 05 Module 5) |
| `long-context-models.md` | 1M-token tier (Claude Sonnet 4 beta, MiniMax-M1, Qwen3); pricing tier cliffs; needle-in-haystack degradation; choosing context size as a design decision | 📋 Planned (Path 05 Module 6) |

The companion memory-tier work (Path 05 Module 4) lives in `concepts/memory/` when it ships.

## How these pages compose

`foundations.md` establishes the vocabulary (three zones, attention budget, the canonical failure modes). `token-budgets.md` operationalizes it — explicit per-zone allocations, soft/hard caps, per-tenant tier tables. The remaining modules build on both: compression mechanics, memory-tier separation, drift detection, long-context model selection.

## What lives elsewhere

| Concern | Where it lives |
|---|---|
| Per-agent cost envelopes (multi-agent) | [Path 03 Pattern 4](../../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) |
| Cost attribution + model routing + prompt caching + budget hierarchies | [`production/cost-engineering.md`](../../production/cost-engineering.md) |
| Streaming output delivery | [`production/streaming.md`](../../production/streaming.md) |
| Tool-output sanitization (security side of suicide-by-context) | [`security/prompt-injection.md`](../../security/prompt-injection.md) Defense 3 |
| Retrieval mechanics (chunking, hybrid search, reranking) | [`concepts/rag/`](../rag/) |
| Memory-tier separation (short-term, long-term, episodic) | `concepts/memory/` (planned) |

## Status

🟢 Stable — these pages cover the conceptual discipline. Specific framework wrappers (LangChain `ConversationBufferMemory`, LangGraph `checkpointer`, OpenAI Agents SDK memory APIs) are intentionally out of scope per Path 05's anti-scope. The techniques here transfer across frameworks.
