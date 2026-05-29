# Token budgets per zone

> 🟡 Intermediate · ⏱ ~26 min · 🛠 Verified 2026-05-29 · 📍 Module 2 of [Path 05 — Context Engineering](../../learning-paths/05-context-engineering/); read after [`foundations.md`](./foundations.md)

## What this page is for

[`foundations.md`](./foundations.md) established the three-zone vocabulary (system prompt / dynamic context / current query) and the attention-budget framing. This page makes the allocation concrete. The decision rule from [Wire Blog April 2026](https://usewire.io/blog/context-budgets-how-to-allocate-tokens-for-ai-agents/): "treat the context window as a budget rather than storage." A 200K-token window is a 200K-token budget that you partition across explicit zones, with soft caps that trigger compression and hard caps that trigger errors.

The 2026 production framing per Wire Blog: "a customer service agent processing 10,000 conversations a day costs roughly $255,000 a year when context is unmanaged, and about $102,000 a year after a 60 percent context reduction. Same model, same task, same volume. The difference is whether the team treats the context window as storage or as a budget."

This page covers:

1. **Five-category budget allocation** — the production-standard percentages from 2026 sources
2. **Soft caps and hard caps** — the two-threshold pattern that catches drift before failure
3. **Per-tenant budget tiers** — extending [Path 03 Pattern 4](../../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) from per-agent to per-zone-per-tenant
4. **Dynamic vs static allocation** — when to fix the budget vs adapt per task
5. **Budget enforcement in the agent loop** — where the checks belong

What this page does **not** cover is in section 6 (Anti-scope).

## Five-category budget allocation

Per [Wire Blog April 2026](https://usewire.io/blog/context-budgets-how-to-allocate-tokens-for-ai-agents/) and [Maxim October 2025](https://www.getmaxim.ai/articles/context-engineering-for-ai-agents-production-optimization-strategies/), production teams converge on a five-category split that refines the three-zone model from [`foundations.md`](./foundations.md) (Zone 2 — dynamic context — gets sub-divided into tools / retrieval / history).

| Category | Production allocation | Maps to Module 1 zone | Notes |
|---|---|---|---|
| **System prompt** | 10-15% | Zone 1 | Strongest influence per token; cache-eligible |
| **Tool descriptions + parameters** | 15-20% | Zone 2a | Often static across a deployment; cache-eligible |
| **Retrieved knowledge (RAG)** | 30-40% | Zone 2b | Most volatile; per-query growth |
| **Conversation history** | 20-30% | Zone 2c | Linear in turn count; compression target |
| **Buffer (current query + reasoning)** | 10-15% | Zone 3 + headroom | Reserved for output planning |

The percentages are *defaults*, not laws. The right allocation depends on task shape: a research agent inverts retrieved-knowledge vs history (more retrieval, less history); a long-form support agent inverts the other way (more history, less retrieval per turn). The discipline is in the *explicitness* — every deployment has documented per-zone percentages, even if those percentages differ from the table.

### A concrete example — 200K-token Claude Sonnet 4.5 deployment

For a 200K-token context window with the table's default split:

| Category | Budget |
|---|---|
| System prompt | 20,000-30,000 tokens |
| Tool descriptions | 30,000-40,000 tokens |
| Retrieved knowledge | 60,000-80,000 tokens |
| Conversation history | 40,000-60,000 tokens |
| Buffer | 20,000-30,000 tokens |

The 60-80K-token retrieval budget is the dominant lever. A retrieval policy that returns top-10 chunks at 1K tokens each fits in 10K; top-50 at 2K each blows the budget. The chunk-size × chunk-count product is what the budget constrains.

Per [machinelearningmastery April 2026](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/): "aim for roughly 60-80% context utilization rather than maxing out capacity." The buffer category in the table is the operationalization — 10-15% of context window deliberately left empty as headroom for unexpected tool-output growth, model planning tokens, and the "suicide by context" prevention margin ([`foundations.md`](./foundations.md) Failure 1).

## Soft caps and hard caps

A single threshold per category doesn't catch drift before it becomes failure. The two-threshold pattern: soft cap triggers mitigation; hard cap triggers error.

### Soft cap — triggers compression or selection

When a zone approaches its budget, the soft cap triggers an action *before* the budget is exhausted. Three soft-cap actions:

| Zone | Soft cap action when 80% of budget reached |
|---|---|
| **Conversation history** | Summarize the oldest N turns into a single 500-token summary; drop the original turns from context |
| **Retrieved knowledge** | Re-rank the retrieved set; drop the lowest-relevance entries until back under threshold |
| **Tool descriptions** | Filter to the tools the planner determined relevant for the current task type (just-in-time per [`../../security/tool-abuse.md`](../../security/tool-abuse.md) Defense 2) |
| **System prompt** | Static — soft cap doesn't apply (system prompt is authored, not accumulated) |

The soft cap is a *quality* lever: compress before degradation, not after. The 80% threshold is typical; deployments with high tool-output variance run softer caps (60-70%) to leave more buffer.

### Hard cap — triggers error

When a zone exceeds its absolute maximum, the agent loop *errors* rather than silently truncates. Per [TianPan April 2026](https://tianpan.co/blog/2026-04-13-token-budget-as-architecture-constraint) on suicide by context: "the request fails. The agent never understands why. It doesn't crash or throw an exception — it just stops working."

The hard cap converts the silent failure into an explicit one. The error gets caught by the agent's retry / escalation logic (Path 03 Pattern 3); the user sees a "I encountered an issue processing that — let me try a different approach" rather than the agent staring into the void.

```python
@dataclass
class ZoneBudget:
    zone: str
    soft_cap: int  # tokens; triggers compression
    hard_cap: int  # tokens; triggers error

class ContextBudgetManager:
    def __init__(self, budgets: list[ZoneBudget]):
        self.budgets = {b.zone: b for b in budgets}

    def check_zone(self, zone: str, current_tokens: int) -> Literal["ok", "compress", "error"]:
        budget = self.budgets[zone]
        if current_tokens >= budget.hard_cap:
            return "error"
        if current_tokens >= budget.soft_cap:
            return "compress"
        return "ok"

    def enforce(self, zone: str, current_tokens: int, content: str, compressor) -> str:
        outcome = self.check_zone(zone, current_tokens)
        if outcome == "error":
            raise ContextBudgetExceeded(zone, current_tokens, self.budgets[zone].hard_cap)
        if outcome == "compress":
            return compressor.compress(zone, content, target_tokens=int(self.budgets[zone].soft_cap * 0.6))
        return content
```

Three properties:

1. **The compressor is zone-aware** — history compression (summarization) differs from retrieved-knowledge compression (re-ranking) differs from tool-description compression (filtering). The manager dispatches to zone-specific compressors.
2. **Hard-cap errors propagate** — they're not swallowed. The agent's retry layer decides whether to retry with a more aggressive compression policy, escalate to a human, or report failure.
3. **The thresholds are configuration**, not constants — different deployments have different sensible defaults.

## Per-tenant budget tiers

Per [Path 03 Pattern 4](../../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md), per-agent cost budgets are the canonical multi-agent cost-control primitive. Path 05 Module 2 extends this from *per-agent* to *per-zone-per-tenant*: different tenants get different per-zone allocations within the same shared deployment.

### The tenant-tier table

A SaaS deployment serving free / pro / enterprise tiers might run:

| Zone | Free tier | Pro tier | Enterprise tier |
|---|---|---|---|
| System prompt | 5K tokens (shared cached prompt) | 5K tokens (shared cached prompt) | 10K tokens (per-tenant custom prompt) |
| Tool descriptions | 5K tokens (limited tool set) | 10K tokens (full tool set) | 15K tokens (full + tenant tools) |
| Retrieved knowledge | 10K tokens (shared corpus) | 30K tokens (shared + tenant corpus) | 50K tokens (shared + tenant + premium sources) |
| Conversation history | 5K tokens (short rolling window) | 20K tokens (longer window + summary) | 50K tokens (full session + cross-session memory) |
| Buffer | 5K tokens | 10K tokens | 20K tokens |
| **Total context budget** | **30K** | **75K** | **145K** |

The tier choice maps to model selection — free tier might use a Haiku-class model with 200K context window but constrain to 30K to manage cost; enterprise tier uses Sonnet 4.5+ with the full 200K window. The cost-engineering layer ([`../../production/cost-engineering.md`](../../production/cost-engineering.md)) handles the model-tier routing; the context-engineering layer handles the per-zone allocation within whatever budget the cost layer assigns.

### What the tiering buys

Per Wire Blog's $255K → $102K example: the 60% context reduction came from realistic per-tenant tiers. The free tier doesn't get the enterprise's 145K-token budget because most free-tier tasks don't need it. The enterprise tier doesn't pay free-tier prices because its workload is genuinely larger. The tier alignment to actual workload is what produces the cost reduction without quality loss.

### Implementation surface

The tier mapping lives at request entry:

```python
def get_context_budget(tenant_id: str, task_type: str) -> ContextBudget:
    tier = lookup_tenant_tier(tenant_id)  # free / pro / enterprise
    task_profile = lookup_task_profile(task_type)  # research / support / code-assist / ...

    base = TIER_BUDGETS[tier]
    return base.adjust_for_task_profile(task_profile)
```

The `adjust_for_task_profile` step is where the workload-aware allocation happens — a research task gets more retrieved-knowledge budget at the expense of conversation-history budget; a support task does the opposite.

## Dynamic vs static allocation

Two valid approaches to setting budgets:

### Static allocation

Per-zone percentages fixed at deployment. The budget table is a config file; changes go through PR review. Predictable, easy to monitor, easy to debug.

**When static works**: production deployments with relatively uniform task shapes. A customer-support agent handles tickets that look similar enough that one budget allocation fits 90%+ of traffic.

**When static fails**: deployments with high task-shape variance. A code-assistant that handles both 5-line snippet questions and full-codebase refactors needs vastly different budgets per task.

### Dynamic allocation

Per [machinelearningmastery April 2026](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/): "use dynamic allocation: simple tasks get minimal context, while complex multi-step tasks get more. This balances cost and capability."

The pattern: a lightweight classifier scores the incoming task and selects from a small set of budget profiles (typically 3-5). Simple tasks get the minimal-budget profile (saves cost); complex tasks get the high-budget profile (better quality).

```python
def select_budget_profile(task: TaskRequest) -> ContextBudget:
    complexity = task_complexity_classifier(task)  # 0.0 - 1.0
    if complexity < 0.3:
        return BUDGET_PROFILES["minimal"]   # 20K total
    elif complexity < 0.7:
        return BUDGET_PROFILES["standard"]  # 75K total
    else:
        return BUDGET_PROFILES["large"]     # 150K total
```

The classifier itself is cheap (Haiku-class model classifying a task in <1K tokens; ~$0.0001 per classification). The budget savings on simple tasks pay back the classifier cost within hundreds of requests.

**When dynamic works**: high task-shape variance; the cost of misallocating is significant; the classifier achieves >80% accuracy on task complexity.

**When dynamic fails**: low variance (the classifier doesn't add value); poor classifier accuracy (mis-classified tasks get the wrong budget and fail).

The hybrid pattern most production deployments converge on: static base budgets per tenant tier + dynamic adjustment per task within the tier.

## Budget enforcement in the agent loop

Where the budget checks belong matters as much as the budgets themselves.

### Check at three points

1. **Before each LLM call** — sum the current zone token counts; compare to budgets; if any zone is over soft cap, compress; if any zone is over hard cap, error.
2. **After tool calls return** — tool outputs are the main source of unexpected zone growth ([`foundations.md`](./foundations.md) Failure 1). Post-tool checks catch the growth before the next LLM call uses it.
3. **At conversation-handoff boundaries** — multi-agent systems where one agent hands off to another need to check budgets at the handoff (the receiving agent inherits the context).

### Don't check mid-LLM-call

The model is generating tokens within a single call; intervening mid-stream produces broken responses. Budget enforcement happens *between* calls, not during them. The streaming pattern from [`../../production/streaming.md`](../../production/streaming.md) is orthogonal to budget enforcement — streaming controls how tokens reach the user; budget enforcement controls what tokens reach the model.

### Where to put the manager

The `ContextBudgetManager` belongs in the agent's harness, not in the LLM client. The LLM client is a thin wrapper that issues API calls; the harness is where the agent's reasoning loop, tool dispatching, and state management live. Budget enforcement is a harness concern.

Per [the Agent Harness Engineering survey (CMU + Yale + JHU + others, 2026)](https://github.com/muratcankoylan/agent-skills-for-context-engineering): "improving token efficiency, retrieval precision, prefix reuse, masking, partitioning, or budget allocation for agent systems" lives at the harness layer.

## Operational discipline

Five practices for sustained budget hygiene:

1. **Per-zone token metrics in trace data**. Every agent step records per-zone token counts. Aggregated dashboards show per-tenant, per-task-type, per-agent zone distributions. The data is what makes budget review possible.
2. **Quarterly budget review per tenant tier**. Tier allocations drift as tools change and corpora grow. A quarterly review checks whether tier budgets still match observed task distributions; adjusts where they don't.
3. **Soft-cap-trigger rate as a leading indicator**. A tenant whose conversation-history soft cap triggers in >40% of turns is in a workload that doesn't fit the tier's history budget — either the user needs a tier upgrade or the tier needs a budget increase.
4. **Hard-cap-trigger rate as a critical metric**. Hard caps should fire rarely; >1% of requests is a budget gap. Either the budget is wrong or the upstream allocation logic isn't filtering correctly.
5. **Budget changes go through the same PR review as code**. The per-zone allocation is config; config changes affect production behavior; config changes need review. Path 06 v2 Lab 24's regression set should include budget-allocation cases.

## Anti-patterns

Three budget-related patterns that look reasonable and aren't:

### Equal allocation across zones

Splitting 200K tokens evenly into 40K per zone seems fair. It isn't. The Wire Blog production allocations (10-15% / 15-20% / 30-40% / 20-30% / 10-15%) reflect that retrieved-knowledge dominates by usage; the system prompt is small but outsized in influence per token; history compounds with turn count. Equal allocation wastes the system-prompt budget and starves retrieved-knowledge.

### Soft cap = hard cap

A single threshold without the soft/hard distinction misses the compression opportunity. By the time the budget is exhausted, it's too late to gracefully degrade — the agent has to error. The two-threshold pattern catches drift early; compresses; continues. Production deployments without the soft-cap layer routinely fail in ways that good telemetry would have warned about.

### Per-tenant tiers without task-profile adjustment

A tier table fixed by tenant ignores task variance within the tenant. An enterprise user doing both 5-minute support queries and 60-minute research investigations doesn't fit a single budget. The static tier + dynamic task adjustment hybrid is what handles real workloads.

## Anti-scope

What this page does not cover:

- **Compression mechanics** — what gets summarized vs truncated vs re-ranked; lossy vs lossless. Module 3 (`compression-and-summarization.md`, planned).
- **Memory-tier separation** — short-term / long-term / episodic. Module 4 (`memory-tiers.md`, planned). The conversation-history zone here is short-term memory; Module 4 covers the longer-horizon tiers.
- **Context drift detection** — the re-read / re-decide / task-reframing signals. Module 5 (`context-drift-detection.md`, planned). Drift is the failure mode budgets don't catch.
- **Long-context model selection** — when to use 1M-token Claude Sonnet 4 / MiniMax-M1 / Qwen3 vs sticking with 200K models. Module 6 (`long-context-models.md`, planned).
- **Prompt-caching specifics** — Anthropic 1.25× write / 0.10× read break-even math. Covered in [`../../production/cost-engineering.md`](../../production/cost-engineering.md) Layer 3a.
- **RAG-specific retrieval policies** — top-k vs MMR vs hybrid retrieval. [`../rag/`](../rag/) and Path 02.
- **Per-token model selection at runtime** — that's model routing ([`../../production/cost-engineering.md`](../../production/cost-engineering.md) Layer 2), not context engineering.

## References

**Budget allocation patterns (2026)**:
- [Wire Blog (April 2026), *Context budgets: how to allocate tokens for AI agents*](https://usewire.io/blog/context-budgets-how-to-allocate-tokens-for-ai-agents/) — five-category production split; $255K → $102K customer-service example; budget-as-architecture framing
- [Maxim (October 2025), *Context Engineering for AI Agents: Token Economics and Production Optimization*](https://www.getmaxim.ai/articles/context-engineering-for-ai-agents-production-optimization-strategies/) — per-zone allocation table; Google DeepMind early-position findings
- [harnessengineering.academy (April 2026), *Context Engineering: The Key Skill*](https://harnessengineering.academy/blog/context-engineering-the-key-skill-every-ai-developer-needs-in-2026/) — three-zone vocabulary; the Manus production techniques; 83%→96% lift comparison
- [machinelearningmastery (April 2026), *Effective Context Engineering for AI Agents*](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/) — 60-80% utilization target; dynamic allocation pattern; tool outputs as largest cost source

**Hard ceiling and constraint framing (2026)**:
- [TianPan (April 2026), *Token Budget as Architecture Constraint*](https://tianpan.co/blog/2026-04-13-token-budget-as-architecture-constraint) — suicide by context; dynamic reallocation patterns; constrained-first architectures
- [Tokalator paper (arxiv:2604.08290)](https://arxiv.org/pdf/2604.08290) — visibility into context budget consumption; per-source attribution

**Agent harness perspective (2026)**:
- [muratcankoylan/agent-skills-for-context-engineering (2026)](https://github.com/muratcankoylan/agent-skills-for-context-engineering) — cited by *Meta Context Engineering via Agentic Skill Evolution* (Peking University, 2025) and *Agent Harness Engineering: A Survey* (CMU + Yale + JHU + others, 2026); foundational static-skill architecture

**Repo cross-references**:
- [`foundations.md`](./foundations.md) — Module 1; the three-zone vocabulary this page allocates against
- [`../../production/cost-engineering.md`](../../production/cost-engineering.md) — Layer 1 (attribution): per-zone counting; Layer 2 (routing): tier-to-model mapping; Layer 3a (prompt caching): system-prompt zone optimization; Layer 4 (budgets): the per-conversation/per-user-hour/per-tenant-day hierarchy this page maps to per-zone budgets within
- [Path 03 Pattern 4 — Per-agent cost budgeting](../../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) — the per-agent envelope this page extends to per-zone-per-tenant
- [Path 03 Pattern 2 — Shared-state boundaries](../../learning-paths/03-multi-agent-systems/patterns/02-shared-state-boundaries.md) — the 15× token-burn case; the failure shape budget enforcement prevents
- [`../../security/tool-abuse.md`](../../security/tool-abuse.md) — Defense 2 (just-in-time permissions): the tool-description-zone filtering this page lists as a soft-cap action
- [`../../production/streaming.md`](../../production/streaming.md) — orthogonal concern; streaming controls output delivery, budget enforcement controls input composition
- [Path 06 Module 6 cost attribution](../../learning-paths/06-evaluation-observability/) — the trace-level token-counting infrastructure this page's metrics depend on
