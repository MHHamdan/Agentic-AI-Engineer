# Memory concepts

> Multi-tier memory architecture for AI agents — what gets stored short-term vs long-term vs episodically, which storage backend fits each tier, and how forgetting policies keep the system manageable. This subdir is the home for Path 05 Module 4 and downstream memory work.

## Pages

| Page | Covers | Status |
|---|---|---|
| [`memory-tiers.md`](./memory-tiers.md) | Three memory tiers (short-term / long-term / episodic); four memory dimensions trade-off; Mem0 594→8,000 token scaling; storage backends (vector / graph / SQL); Claude Opus 4.7 1M-token crossover; LangChain deprecation footgun; forgetting mechanisms | ✅ Shipped (Batch 60) |

The companion compression work for the short-term tier (Path 05 Module 3) lives in [`../context/compression-and-summarization.md`](../context/compression-and-summarization.md).

## What lives elsewhere

| Concern | Where it lives |
|---|---|
| Three context zones + token budgets + compression | [`../context/`](../context/) (Path 05 Modules 1-3 + 5-6) |
| Vector DB internals (HNSW, IVF, embedding model choice) | [`../rag/`](../rag/) |
| Per-tenant tiering / cost budgets | [`../context/token-budgets.md`](../context/token-budgets.md) + [`../../production/cost-engineering.md`](../../production/cost-engineering.md) |
| Memory-related safety + policy (retention, deletion) | [`../../security/safety-policy.md`](../../security/safety-policy.md) |
| Multi-agent shared state | [Path 03 Pattern 2 — Shared-state boundaries](../../learning-paths/03-multi-agent-systems/patterns/02-shared-state-boundaries.md) |

## Status

🟢 Stable — the underlying memory-tier discipline doesn't change quickly. Specific framework wrappers (Mem0 SDK, LangMem, Zep Graphiti, Letta) move faster and are intentionally out of scope at the framework-implementation level per Path 05's anti-scope. The techniques covered here transfer across frameworks.
