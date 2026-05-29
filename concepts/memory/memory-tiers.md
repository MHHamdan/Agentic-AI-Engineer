# Memory tiers

> 🟡 Intermediate · ⏱ ~28 min · 🛠 Verified 2026-05-29 · 📍 Module 4 of [Path 05 — Context Engineering](../../learning-paths/05-context-engineering/); read after [`../context/foundations.md`](../context/foundations.md), [`../context/token-budgets.md`](../context/token-budgets.md), and [`../context/compression-and-summarization.md`](../context/compression-and-summarization.md)

## What this page is for

[`../context/foundations.md`](../context/foundations.md) named the conversation-history sub-zone of dynamic context (Zone 2c) as one of three sub-categories with linear growth in turn count. This page covers what happens when "conversation history" needs to span more than one session — when the agent has to remember the user across multiple interactions, recall facts from weeks ago, or replay past trajectories. That's the multi-tier memory problem.

The 2026 production framing per [Mem0 February 2026](https://mem0.ai/blog/long-term-memory-ai-agents): "Mem0 benchmarks show 91% lower p95 latency and 90% token reduction versus full-context prompting. Structured memory pipelines enable personalization across hundreds of sessions without re-reading prior history." That's the canonical scaling argument — without tiered memory, multi-session agents either don't remember (poor UX) or burn tokens re-reading everything (poor economics).

But the landscape changed in 2026. Per [Digital Applied May 2026](https://www.digitalapplied.com/blog/ai-agent-memory-vector-graph-episodic-2026): "Claude Opus 4.7's 1M-token context at flat pricing has made 'just stuff it in context' operationally cheaper than a Mem0 + Pinecone stack for agents with fewer than roughly 500K tokens of accumulated history. That crossover point reshapes the decision tree for single-user and small-fleet deployments." Tiered memory remains the right architecture for many use cases; it's no longer the obvious default for all of them.

This page covers:

1. **The three memory tiers** — short-term (conversation buffer) vs long-term (vector DB) vs episodic (past traces)
2. **The four memory dimensions** — the trade-off space no single tool solves
3. **The Mem0 594→8,000 token cost progression** — the canonical scaling pattern
4. **Storage backends per tier** — when vector DB / graph DB / SQL each fits
5. **The Claude Opus 4.7 1M-token crossover** — when long-context replaces tiered memory
6. **The LangChain memory deprecation footgun** — the 2026 migration most builds need
7. **Forgetting mechanisms** — why remembering everything is the wrong default
8. Operational discipline, anti-patterns, anti-scope

## The three memory tiers

Per [DigitalOcean March 2026](https://www.digitalocean.com/community/tutorials/langgraph-mem0-integration-long-term-ai-memory): "Memory vs Context Window: Context window provides short-term contextual memory that expires at the end of the session. Long-term (persistent) memory: This is a stable, user-specific memory that persists across sessions."

The three tiers correspond to three time horizons:

| Tier | Horizon | Storage | Typical content | Token cost per access |
|---|---|---|---|---|
| **Short-term** | Current session | Context window directly | Conversation buffer; turn-by-turn state | 0 (already in context) |
| **Long-term** | Across sessions | Vector DB / graph DB / SQL | User preferences; persistent facts; learned patterns | Retrieval-driven (5K-50K typical per query) |
| **Episodic** | Specific past events | Trace store / event log | Past complete trajectories; reference cases; learned procedures | Variable; usually retrieval-driven |

The boundary between short-term and long-term is the session boundary — what survives when the user comes back tomorrow. The boundary between long-term and episodic is the granularity — long-term stores *facts* ("user prefers concise responses"); episodic stores *experiences* ("on April 14, the agent successfully handled a similar billing escalation by routing to specialist X"). Per [Analytics Vidhya April 2026](https://www.analyticsvidhya.com/blog/2026/04/memory-systems-in-ai-agents/): "researchers have developed multi-layered memory models, including short-term working memory and long-term episodic, semantic, and procedural memory."

### Short-term memory

The conversation buffer that sits in the context window. Per [`../context/token-budgets.md`](../context/token-budgets.md) Module 2's allocation table, this is Zone 2c (20-30% of context budget). Module 3 ([`../context/compression-and-summarization.md`](../context/compression-and-summarization.md)) covers the compression strategies that fire when this zone hits its soft cap. There's no separate storage backend — the model's context window IS the short-term store.

### Long-term memory

Persists across sessions. Three storage backends in 2026 production:

- **Vector DB** (Pinecone, Weaviate, Qdrant, Chroma) — semantic similarity retrieval. Strong at "find facts similar to this query." Weak at multi-hop relationships.
- **Graph DB** (Neo4j, Memgraph, Zep's Graphiti) — relationship traversal. Strong at "what does X depend on, and what depends on that?" Weak at semantic similarity.
- **SQL / Postgres** — structured facts. Strong at exact lookups, audit, ACID. Weak at fuzzy matching.

Per [47Billion March 2026](https://47billion.com/blog/ai-agent-memory-types-implementation-best-practices/): "Vector DBs → Excellent semantic similarity but poor multi-hop. Graph DBs → Fast relationship traversal (ideal for episodic + procedural). SQL/Postgres → Reliable, auditable, ACID-compliant for long-term facts."

The 2026 mature pattern is hybrid storage. Mem0 uses Postgres for long-term facts + vectors for similarity + graph for relationships, all behind a unified API.

### Episodic memory

Past complete experiences the agent can retrieve and replay. Per [Atlan April 2026](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/), LangMem's three memory types are "episodic (past interactions), semantic (facts and preferences), and procedural (agents updating their own system instructions)." The episodic tier matters most for agents that need to learn from past trajectories — what worked, what didn't, what to do differently.

Zep / Graphiti is the canonical 2026 choice for agents that need to reason about *how facts change over time* per Atlan: "best for agents that reason about how facts change over time." The temporal-knowledge-graph approach treats episodic memory as a sequence of stateful events.

## The four memory dimensions

Per [DEV Community April 2026 referencing the ECAI paper](https://dev.to/vektor_memory_43f51a32376/the-state-of-ai-agent-memory-in-2026-what-the-research-actually-shows-3aja): "no single approach solves all four memory dimensions simultaneously. Every architecture involves trade-offs, and understanding those trade-offs is the foundation of making a sound choice."

The four dimensions:

| Dimension | What it measures | Best-served by |
|---|---|---|
| **Semantic similarity** | "Find facts like this query" | Vector DB |
| **Multi-hop reasoning** | "What depends on what?" | Graph DB |
| **Temporal recall** | "What happened when?" | Event log / temporal graph (Zep) |
| **Cross-session coherence** | "Connect this turn to a turn from three weeks ago" | Long-term store with user-scoped indexing |

The trade-off: optimizing for one dimension usually weakens another. A pure-vector-DB approach excels at semantic similarity, fails at multi-hop. A pure-graph approach excels at relationships, fails at fuzzy matching. The hybrid approach (Mem0, Zep) covers more dimensions at the cost of operational complexity.

The decision: pick the dimensions the deployment actually needs. A customer-support agent often needs semantic similarity (find past tickets like this one) and cross-session coherence (remember this user); a research agent needs multi-hop and temporal; a debugging assistant needs episodic plus procedural. There's no universal best.

## The Mem0 594→8,000 token cost progression

Per [niteagent.com May 2026](https://niteagent.com/blog/ai-agent-cost-optimization-2026/) on Mem0 2026 production traces: "24 memory entries inject 594 tokens; 500 entries inject 8,000 tokens." That progression is the canonical scaling pattern — memory retrieval cost is roughly linear in stored entry count when stored entries are short and the retrieval policy is top-k.

The math:

- 24 entries × ~25 tokens/entry = 600 tokens ≈ 594 observed
- 500 entries × ~16 tokens/entry = 8,000 tokens (entries shrink slightly as the system learns)

Per [Mem0 February 2026](https://mem0.ai/blog/long-term-memory-ai-agents): "Mem0 benchmarks show 91% lower p95 latency and 90% token reduction versus full-context prompting. Structured memory pipelines enable personalization across hundreds of sessions without re-reading prior history." The 90% token reduction is what makes the long-term tier economically necessary at scale — without it, every multi-session deployment burns tokens re-reading history.

The cost curve:

| Stored memory entries | Memory-injection tokens | Equivalent full-history tokens | Reduction |
|---|---|---|---|
| 24 (light user) | ~594 | ~2,000 | 70% |
| 500 (heavy user) | ~8,000 | ~80,000+ | 90% |
| 2,000 (power user) | ~25,000 | ~300,000+ | 92% |

The reduction percentage stays high because Mem0 stores distilled facts, not raw turns. The raw-turn equivalent grows faster than the distilled-fact equivalent, so the ratio improves at the high end. That's why the architecture pays off most for heavy users.

## Storage backends — when each fits

### Vector DB

When semantic similarity dominates. "Find docs/turns/facts like this query" is the canonical operation. Performance characteristics: 50-200ms p99 retrieval typical at 1M-entry scale; embedding cost ~$0.0001 per entry.

When it fits: knowledge-base lookup, retrieval-augmented generation ([`../rag/`](../rag/)), find-similar-past-tickets.

When it doesn't: relationship traversal ("what depends on X?"), exact lookups (use SQL), multi-hop reasoning (use graph DB).

### Graph DB

When relationship traversal matters. Per [47Billion March 2026](https://47billion.com/blog/ai-agent-memory-types-implementation-best-practices/): "Graph DBs → Fast relationship traversal (ideal for episodic + procedural)." The 2026 mature options: Neo4j (heavy), Memgraph (lighter), Zep's Graphiti (purpose-built for agent memory).

When it fits: agents that reason about cause-and-effect chains, dependency analysis, procedural memory ("how did we solve a similar problem before?").

When it doesn't: pure semantic search (vector DB is faster), simple key-value lookups (SQL/Redis), high-throughput write workloads (vector DBs handle bulk inserts better).

### SQL / Postgres

When auditability matters. Per [47Billion March 2026](https://47billion.com/blog/ai-agent-memory-types-implementation-best-practices/): "SQL/Postgres → Reliable, auditable, ACID-compliant for long-term facts." Regulated industries (medical, legal, financial — overlap with [`../../security/safety-policy.md`](../../security/safety-policy.md)) often need the audit trail; SQL provides it natively.

When it fits: user preferences, account-level facts, anything that needs exact lookup + audit + ACID guarantees.

When it doesn't: fuzzy matching (use vector DB), relationship traversal at scale (use graph DB).

### Hybrid

Production-mature systems typically combine all three. Mem0's architecture per [Atlan April 2026](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/): "hybrid store combining vectors, graph relationships, and key-value." The complexity is the cost; the four-dimension coverage is the benefit.

## The Claude Opus 4.7 1M-token crossover

Per [Digital Applied May 2026](https://www.digitalapplied.com/blog/ai-agent-memory-vector-graph-episodic-2026): "Claude Opus 4.7's 1M-token context window is flat-priced at $5 input / $25 output per Mtok — no surcharge above 200K unlike prior generations. For single-user agents with fewer than ~500K tokens of accumulated history and fewer than 10 sessions, the operational cost of long-context can undercut maintaining a Mem0 + Pinecone stack."

The 2026 shift: long-context is now a legitimate memory architecture for small fleets. The decision:

| User scale | History size | Recommended architecture |
|---|---|---|
| Single user, <500K tokens accumulated | Small | Long-context (stuff it all in) — simpler, cheaper at this scale |
| Single user, >500K tokens | Medium | Tiered memory required — long-context economics break down |
| Multi-user, any history size | Any | Tiered memory required — per-user indexing matters more than per-call cost |
| Large fleet (>1000 active users) | Any | Tiered memory + multi-tenancy ([`../context/token-budgets.md`](../context/token-budgets.md) Module 2 per-tenant tiers) |

The crossover is an economics decision, not a capability gap. For single-user / small-fleet cases, the operational simplicity of long-context can outweigh the per-call token cost. For multi-user / large-fleet cases, the per-user retrieval cost of a tiered system stays roughly constant while the long-context cost scales linearly with user count.

The capability angle: even at 1M tokens, the n² attention dilution from [`../context/foundations.md`](../context/foundations.md) applies. Per [Atlan April 2026](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/): "Large context windows delay but do not fix memory failures." Long-context is a deferral, not a solution; for any deployment where memory failures matter, tiered memory's selective retrieval is the right approach.

## The LangChain memory deprecation footgun

Per [Digital Applied May 2026](https://www.digitalapplied.com/blog/ai-agent-memory-vector-graph-episodic-2026): "LangChain memory is officially deprecated — migrate to LangGraph. As of 2026, BufferMemory, ConversationBufferMemory, ConversationSummaryBufferMemory, and VectorStoreRetrieverMemory from langchain.memory are deprecated. LangGraph's checkpointer-based short_term + long_term memory pattern is the only officially supported approach. Many published tutorials still reference the deprecated APIs — this is a build-phase footgun for any team following older guides."

Three things this means for new builds:

1. **Don't follow LangChain memory tutorials from before 2026**. The APIs they show have been deprecated; rewriting later is more painful than starting with LangGraph.
2. **LangGraph's checkpointer is the memory primitive**. Short-term memory lives in the checkpointer's per-thread state; long-term memory lives in the StateGraph's persistent store layer.
3. **LangMem (Q1 2025 launch) is the LangChain-stack long-term memory SDK**. Per Atlan: "LangMem supports three memory types: episodic (past interactions), semantic (facts and preferences), and procedural (agents updating their own system instructions). The SDK is free and open source. Long-term memory requires LangGraph's StateGraph — it does not work with older non-LangGraph chains."

The cross-framework note: Mem0 works with any agent stack via REST API (no LangChain dependency); LangMem requires the LangGraph ecosystem. For teams already on LangChain/LangGraph, LangMem is closer; for teams on different frameworks or building framework-agnostic, Mem0's REST surface is more portable.

## Forgetting mechanisms

Per [47Billion March 2026](https://47billion.com/blog/ai-agent-memory-types-implementation-best-practices/): "Forgetting Mechanisms: Not remembering everything is a feature. Use temporal decay, relevance scoring, or user-defined policies (e.g., forget after one semester in education agents)."

Three forgetting strategies in production:

1. **Temporal decay** — older entries get exponentially lower retrieval scores. The agent still has access to them on direct lookup but they fall out of top-k retrieval over time. Simple to implement; matches most "older = less relevant" intuitions.
2. **Relevance scoring** — entries that don't get retrieved over N sessions get pruned. Equivalent to LRU cache eviction. Risk: rarely-used-but-critical facts get evicted (the user's actual name, used only at start-of-session).
3. **User-defined policies** — domain-specific rules. Medical: HIPAA-driven retention windows. Legal: matter-bounded scopes. Financial: regulatory-period limits. Education: per-semester resets.

The cross-reference to [`../../security/safety-policy.md`](../../security/safety-policy.md): the policy author's data-retention requirements set the constraints; the memory architecture implements them. Forgetting isn't optional in regulated verticals.

GDPR's right-to-be-forgotten adds an externally-triggered category: users can request deletion of their data, and the memory tier has to support it. Hard requirement: long-term memory entries must be deletable per-user, not just per-collection. Per the [DigitalOcean March 2026](https://www.digitalocean.com/community/tutorials/langgraph-mem0-integration-long-term-ai-memory) production-concerns note: "Plan for privacy, retention policies, and scalability."

## Operational discipline

Five practices for sustained memory hygiene:

1. **Tier ownership clearly named per use case**. Each memory access has a documented tier and reason. Short-term retrieval (context window) is implicit; long-term retrieval (vector / graph / SQL) is explicit with a query and a scope.
2. **Per-user retrieval cost as a first-class metric**. Per [Mem0](https://mem0.ai/blog/long-term-memory-ai-agents)'s 90% token reduction claim: the metric that proves it is per-user retrieval cost vs full-history cost. Trace it.
3. **Memory write path with conflict resolution**. Two facts that contradict ("user prefers concise responses" from session 1 and "user wants detailed explanations" from session 5) need conflict-resolution logic. Per [Analytics Vidhya April 2026](https://www.analyticsvidhya.com/blog/2026/04/memory-systems-in-ai-agents/): "memory management techniques — such as semantic consolidation, intelligent forgetting, and conflict resolution — are essential."
4. **Audit trail for high-stakes memory writes**. What got remembered, when, and why. Regulated verticals require it; non-regulated verticals benefit from it during debugging.
5. **Quarterly review of forgetting-policy effectiveness**. Are users running into stale-memory issues? Are critical facts getting evicted? The forgetting policy is config; config drifts; review it.

## Anti-patterns

Three memory-architecture patterns that look reasonable and aren't:

### Storing everything by default

A memory architecture that writes every turn to long-term storage produces the cost progression in reverse — 8,000 tokens to inject 500 entries when most of them aren't useful. The discipline per [Mem0](https://mem0.ai/blog/long-term-memory-ai-agents): "Production uses extract → consolidate → store → retrieve via vectors or graphs." The extract step is where the agent decides what's worth remembering; storing everything skips it.

### One memory backend for all dimensions

A pure-vector-DB approach excels at semantic similarity, fails at multi-hop. A pure-graph approach excels at relationships, fails at fuzzy matching. Production-mature systems combine backends per dimension. The complexity is real; the four-dimension coverage is what makes the system actually work.

### Treating long-context as a memory architecture without measuring

The Claude Opus 4.7 1M-token-at-flat-pricing change makes long-context plausible at small scale. It doesn't make it universally better. Per [Atlan April 2026](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/): "large context windows delay but do not fix memory failures." Teams that switch to long-context without measuring memory-failure rates often discover the failures only after the user-experience degradation surfaces.

## Anti-scope

What this page does not cover:

- **Context drift detection** — the four early-warning signals — Module 5 (`context-drift-detection.md`, planned). Memory-tier drift is a sub-case; Module 5 covers the broader signal set.
- **Long-context model selection** in depth — Module 6 (`long-context-models.md`, planned). This page references the Claude Opus 4.7 crossover; Module 6 covers the broader long-context tradeoffs (needle-in-haystack performance, pricing-tier cliffs across providers, context-window selection as a design decision).
- **Specific vector DB tuning** (HNSW parameters, IVF vs Flat indexes, embedding model choice). That's [`../rag/`](../rag/) territory and Path 02. Path 05 covers how the agent *uses* the memory tier; Path 02 covers how the retrieval is implemented.
- **Framework-specific API walkthroughs** (full Mem0 SDK reference, LangGraph checkpointer tutorial, Zep Graphiti setup). Per Path 05 anti-scope: framework wrappers at the conceptual layer only.
- **Privacy compliance details** (GDPR, HIPAA, CCPA specifics). Real but legal-counsel territory; this page covers the architectural requirements (per-user deletion support, retention policies) without prescribing legal interpretations.
- **MemGPT / Letta OS-level memory management in depth**. Referenced as a category (per Atlan: "best for long-running agents that need OS-level memory management"); a full architectural treatment is its own document.

## References

**Memory architecture landscape (2026)**:
- [Atlan (April 2026), *Best AI Agent Memory Frameworks in 2026: Compared and Ranked*](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/) — Mem0 / Zep / LangMem / Letta / Semantic Kernel / Cognee / Supermemory / Redis Agent Memory Server comparison; three-memory-type taxonomy (episodic, semantic, procedural)
- [Digital Applied (May 2026), *AI Agent Memory 2026: Vector, Graph, Episodic Update*](https://www.digitalapplied.com/blog/ai-agent-memory-vector-graph-episodic-2026) — Claude Opus 4.7 1M-token crossover at ~500K accumulated history; LangChain memory deprecation footgun
- [DEV Community (April 2026), *The State of AI Agent Memory in 2026*](https://dev.to/vektor_memory_43f51a32376/the-state-of-ai-agent-memory-in-2026-what-the-research-actually-shows-3aja) — ECAI paper's four-dimension trade-off framing; Mem0 LoCoMo 91.6 / LongMemEval 93.4 benchmarks
- [47Billion (March 2026), *AI Agent Memory: Types, Implementation, Challenges & Best Practices 2026*](https://47billion.com/blog/ai-agent-memory-types-implementation-best-practices/) — vector vs graph vs SQL backend trade-offs; forgetting mechanisms taxonomy
- [Analytics Vidhya (April 2026), *Architecture and Orchestration of Memory Systems in AI Agents*](https://www.analyticsvidhya.com/blog/2026/04/memory-systems-in-ai-agents/) — CoALA framework; multi-layered memory; semantic consolidation / intelligent forgetting / conflict resolution

**Production patterns (2026)**:
- [Mem0 (February 2026), *Long-Term Memory for AI Agents: The What, Why and How*](https://mem0.ai/blog/long-term-memory-ai-agents) — 91% lower p95 latency; 90% token reduction; extract→consolidate→store→retrieve pipeline
- [DigitalOcean (March 2026), *Building Long-Term Memory in AI Agents with LangGraph and Mem0*](https://www.digitalocean.com/community/tutorials/langgraph-mem0-integration-long-term-ai-memory) — LangGraph + Mem0 integration; memory-vs-context-window distinction
- [AI Practitioner (February 2026), *Long-Term Memory: Unlocking Smarter, Scalable AI Agents*](https://aipractitioner.substack.com/p/long-term-memory-unlocking-smarter-38d) — operational footprint (storage, embedding, indexing, reranking, retrieval); OS-inspired tiered memory designs
- [niteagent.com (May 2026), *AI Agent Cost Optimization in 2026*](https://niteagent.com/blog/ai-agent-cost-optimization-2026/) — Mem0 594→8,000 token scaling progression

**Repo cross-references**:
- [`../context/foundations.md`](../context/foundations.md) — Module 1; three-zone vocabulary; conversation-history sub-zone (Zone 2c) is what this page extends across sessions
- [`../context/token-budgets.md`](../context/token-budgets.md) — Module 2; per-tenant tier table; the multi-tenant memory architecture this page references
- [`../context/compression-and-summarization.md`](../context/compression-and-summarization.md) — Module 3; compression within the short-term tier; this page's long-term and episodic tiers compose with it
- [`../../production/cost-engineering.md`](../../production/cost-engineering.md) — Layer 4 (budgets); the per-user-day / per-tenant-month budget hierarchies this page's memory architecture lives within
- [`../../security/safety-policy.md`](../../security/safety-policy.md) — the policy's data-retention requirements drive the forgetting policy in this page
- [`../rag/`](../rag/) — retrieval mechanics (HNSW, IVF, embedding choice) for the vector-DB backend
- [Path 03 Pattern 2 — Shared-state boundaries](../../learning-paths/03-multi-agent-systems/patterns/02-shared-state-boundaries.md) — the 15× token-burn case; what tiered memory prevents at scale
- [Path 06 Module 6 cost attribution](../../learning-paths/06-evaluation-observability/) — the per-tier token-accounting infrastructure
