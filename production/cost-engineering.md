# Cost engineering at deployment scale

> 🔴 Advanced · ⏱ ~32 min · 🛠 Verified 2026-05-29 · 📍 Read after [`production/deployment.md`](./deployment.md) + Path 03 Pattern 4 (per-agent cost budgeting)

## What this page is for

Production LLM agent cost has three modes: gradual creep that nobody notices, sudden 10× spikes when a prototype ships to real traffic, and runaway loops that burn a month's budget in an afternoon. None of the three look the same on a dashboard; all three need different controls.

This page covers the four-layer cost-control stack the 2026 production literature has consolidated on:

1. **Attribution** — every request tagged at creation time with `tenant_id`, `user_id`, `feature`, `model`, `agent_kind`. Without this, the rest of the stack is guesswork.
2. **Model routing** — fast/cheap models for classification and routing; large models reserved for synthesis and reasoning. The single largest cost lever in 2026 production.
3. **Caching** — prompt caching (provider-side), semantic caching (gateway-side), KV cache optimization. 47-80% cost reduction in production when combined.
4. **Budgets and kill switches** — per-tenant / per-user / per-conversation hard caps that fire as structural defenses, not as nice-to-haves.

Skipping any layer is the most common failure pattern reported in 2026 post-mortems. The case study that anchors this page: a B2B SaaS company, ~400 engineers, eight AI features in production, $9M projected annual LLM spend; three months after adding attribution + routing + caching + budgets, projected spend dropped to $3.1M ([Vishnu N C, May 2026](https://medium.com/@vishnu_73501/llm-cost-optimization-a-practical-guide-for-engineering-teams-95bca0e9aaf3)). The mechanisms below produced that result.

What this page does **not** cover is in section 8 (Anti-scope).

## The cost shape in 2026

Three numbers frame the problem:

1. **LLM API spend doubled from $3.5B to $8.4B between late 2024 and mid-2025**, and 72% of organizations plan to increase AI budgets further in 2026 per [Maxim April 2026](https://www.getmaxim.ai/articles/reduce-llm-cost-and-latency-a-comprehensive-guide-for-2026/). The cost surface is growing faster than most engineering organizations' ability to instrument it.
2. **Costs do not creep — they spike**, often 10× in a single sprint per [Vishnu N C May 2026](https://medium.com/@vishnu_73501/llm-cost-optimization-a-practical-guide-for-engineering-teams-95bca0e9aaf3). A prototype gets promoted to production; real users hit it; the billing line item triples by week two. Monthly budget alerts that look fine on day 10 are not fine on day 20.
3. **Per-request pricing is variable on at least six dimensions in 2026**: input tokens, output tokens, model selection, cached tokens (different rate from uncached), reasoning tokens (priced separately on o-series and reasoning-mode Claude), and modality tokens (audio, image). A naive "total tokens × $X per million" dashboard hides where the spend lives.

The customer-support agent baseline from [CallSphere February 2026](https://callsphere.ai/blog/llm-caching-strategies-cost-optimization-2026) makes the numbers concrete: 10,000 conversations/day at 2,000 tokens per conversation costs $60-$300/day on input tokens alone at frontier-model pricing ($3-$15 per million input tokens). That's $1,800-$9,000/month for a single feature before caching, routing, or any optimization. Multiply by 5-8 features and a 3-10× multi-agent token amplifier per [MintSquare January 2026](https://www.agentframeworkhub.com/blog/ai-agent-production-costs-2026), and the $9M projection from the case study above stops being surprising.

## Layer 1 — Attribution

The first layer of cost control is the only one that gives you the data to optimize the other three. Per [Vishnu N C May 2026](https://medium.com/@vishnu_73501/llm-cost-optimization-a-practical-guide-for-engineering-teams-95bca0e9aaf3): "every single LLM call in your environment must carry metadata that ties it back to a feature, a tenant, a user cohort, and a business outcome. This is non-negotiable."

### Four token layers, tracked separately

Per [DigitalApplied April 2026](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026), each request consumes four kinds of tokens; aggregating them into one input/output bucket hides where the spend lives:

| Layer | What it is | Why it matters |
|---|---|---|
| **Prompt** | System prompt + few-shot examples + user query | Static across users; cache-friendly; the optimization target for prompt compression |
| **Tool** | Tool schemas + tool call args + tool results | Grows with tool count + tool-output verbosity; the target for output truncation |
| **Memory** | Conversation history + RAG-retrieved context | Grows linearly with turn count; the target for compression / summarization |
| **Response** | Model output tokens | Bounded by `max_tokens`; the target for structured output formats |

A 9,000-token system prompt drift (real example from [Vishnu N C May 2026](https://medium.com/@vishnu_73501/llm-cost-optimization-a-practical-guide-for-engineering-teams-95bca0e9aaf3): a customer-support copilot prompt ballooned from ~2,000 to 9,000 tokens after a year of incremental tweaks) shows up as a 60% per-call cost increase. Tracking only "total input tokens" misses the cause; tracking prompt vs tool vs memory separately points at the system prompt as the regression source.

### Three attribution dimensions

Per the same DigitalApplied framework, three dimensions answer three different product questions:

- **Per-user**: which users drive the most spend? (The 60% / 12-employees case from the $9M → $3.1M study.)
- **Per-task**: which agent task type costs most per invocation? (Surfaces the prompt-bloat regression above.)
- **Per-tenant**: which customer segment is profitable? (The pricing conversation the [DigitalApplied April 2026 guide](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026) calls "awkward when you have it after the fact.")

All three dimensions need to exist from day one. Retroactive tagging from logs always misses edge cases — Vishnu's "two weeks to add attribution" timeline is realistic only because his team did it before launch; teams doing it retroactively measure the same work in quarters.

### Concrete instrumentation

The structural primitive: a `trace_metadata` dict attached at request creation time, propagated through every LLM call in the request lifecycle.

```python
from langsmith import traceable
from contextvars import ContextVar

trace_ctx: ContextVar[dict] = ContextVar("trace_ctx", default={})

# In the FastAPI middleware, at request entry:
@app.middleware("http")
async def cost_attribution_middleware(request, call_next):
    trace_ctx.set({
        "tenant_id": request.state.tenant_id,
        "user_id": request.state.user_id,
        "feature": request.url.path,           # e.g., "/research/kickoff"
        "agent_kind": request.state.agent_kind, # e.g., "research_supervisor"
        "request_id": request.state.request_id,
    })
    return await call_next(request)

# Every LLM call picks up the context:
@traceable(metadata=lambda *a, **k: trace_ctx.get())
def call_llm(messages, model: str):
    response = client.messages.create(model=model, messages=messages, ...)
    return response
```

The discipline matters: the tag set is enforced at middleware, not at the call site. A new LLM call added by a teammate inherits the tag set; a missed tag is a code review issue, not a silent gap.

## Layer 2 — Model routing

The single largest cost lever in 2026 production deployments. Per [BSWEN March 2026](https://docs.bswen.com/blog/2026-03-06-agent-routing/) — anchored as the routing-cost framing in [Path 03 Project 1](../learning-paths/03-multi-agent-systems/projects/01-customer-support-multi-agent.md) — a properly-sized Haiku-class triage classifier costs 10-15% of total per-conversation spend; inverting to Opus-class for classification adds 40-60% to total cost for ~2-4 percentage points of routing accuracy.

### The cheap-classifier / expensive-execution pattern

Three tiers, sized correctly:

| Tier | Model class | Cost per million tokens (May 2026) | Use case |
|---|---|---|---|
| **Routing** | Haiku 4.5 / GPT-4o-mini / Gemini 1.5 Flash | $0.25-$0.80 input / $1-$4 output | Triage classification, intent detection, simple extractions |
| **Execution** | Sonnet 4.6 / GPT-4o / Gemini 1.5 Pro | $3-$10 input / $15-$30 output | Tool calling, multi-step reasoning, synthesis |
| **Hard reasoning** | Opus 4.7 / o3 / Gemini Ultra | $15-$30 input / $75-$150 output | Plan validation, faithfulness judging across diverse models, hard math/logic |

A 1000-conversation workload routed correctly (90% interactive routes through Haiku triage + Sonnet specialists, 10% hard cases route to Opus) costs roughly half what the same workload costs at Sonnet-for-everything. Routing inversion (Opus for triage) costs roughly 5× the correctly-sized baseline.

### Routing decision criteria

Three signals to route on:

1. **Question complexity**: short factual queries route to Tier 1; multi-step or compound queries route to Tier 2; questions that demand cross-domain reasoning route to Tier 3. The decomposition decision lives in the [Pattern 02 (Router)](../patterns/02-router.md) primitive.
2. **Cost-of-error**: a refund decision routes higher than a knowledge-base lookup; payment authorization routes higher than ticket triage. The cost of getting it wrong sets the model floor.
3. **Latency budget**: an interactive chat routes through Tier 1+2; an async research pipeline can absorb Tier 3 latency. Latency tolerance widens the routing options.

### Multi-provider routing as cost arbitrage

Per [Speakeasy March 2026](https://www.speakeasy.com/blog/ai-agent-framework-comparison) and the [Maxim April 2026 gateway comparison](https://www.getmaxim.ai/articles/5-enterprise-ai-gateways-for-llm-cost-control-in-2026/), production deployments in 2026 typically route across at least four providers (Anthropic, OpenAI, Google, AWS Bedrock or self-hosted). The arbitrage opportunities:

- **Cheaper equivalents**: Gemini 1.5 Flash is roughly 60% the cost of GPT-4o-mini at comparable quality for classification tasks
- **Spot capacity**: provider-specific batch APIs (Anthropic's `message-batches`, OpenAI's `batch`) offer 50% discount for non-interactive workloads
- **Geographic arbitrage**: Bedrock + Vertex AI regional pricing differs by region; for compliance-flexible workloads, this is a 10-20% lever
- **Failover as cost optimization**: an agent that falls back from Sonnet to Haiku-with-tool-calling-prompt-rewriting on 503 errors preserves uptime AND reduces cost on the degraded path

The trade-off is operational complexity — a multi-provider routing layer is a new component to maintain, monitor, and reason about. Gateway platforms (Bifrost, LiteLLM, OpenRouter, Portkey) commoditize this layer; the choice between "build it in-house" and "use a gateway" is itself a cost-engineering question that the [Maxim April 2026 gateway comparison](https://www.getmaxim.ai/articles/5-enterprise-ai-gateways-for-llm-cost-control-in-2026/) covers in detail.

## Layer 3 — Caching

Three caching layers, addressing different request patterns. Combined, they deliver 47-80% cost reduction in production per [Codezilla April 2026](https://codezilla.io/blog/how-to-optimize-llm-costs-in-production-2026-guide). Each layer needs its own pricing math.

### Layer 3a — Prompt caching (provider-side)

Anthropic and OpenAI both ship server-side prompt caching as of 2025-2026 (Anthropic since 2024, OpenAI's automatic prompt caching since late 2024). The pricing math:

- **Anthropic cache write**: 1.25× the base input token rate (one-time, per cache creation)
- **Anthropic cache read**: 0.10× the base input token rate (every subsequent hit, while warm)
- **Cache TTL**: 5 minutes default; extended cache (1 hour) costs 2× cache-write rate at creation but the same read rate
- **OpenAI automatic prompt caching**: 0.50× the base input rate for cached portions; no explicit cache-write fee

The break-even point: for Anthropic, a cache write at 1.25× pays for itself after ~2 cache reads at 0.10×. Any system prompt that's identical across 3+ calls within the TTL window benefits.

Where it works: static system prompts, few-shot example blocks, tool schemas. Where it doesn't: per-user personalized prompts (cache key per user means low hit rate), prompts that change frequently across deploys.

Per [CallSphere February 2026](https://callsphere.ai/blog/llm-caching-strategies-cost-optimization-2026): "the simplest approach: hash the full prompt and cache the response. If the same prompt appears again, return the cached response without calling the LLM." The application-side equivalent of provider prompt caching, for cases where the full request is identical (FAQ-style lookups, repeated administrative queries).

### Layer 3b — Semantic caching (gateway-side)

Semantic caching matches on embedding similarity rather than exact text. Paraphrased queries hit the cache; exact-match caches miss them. Production hit rates vary widely:

- [Redis LangCache (January 2026)](https://redis.io/blog/large-language-model-operations-guide/): up to 73% cost reduction reported at scale
- [Maxim April 2026 gateway comparison](https://www.getmaxim.ai/articles/semantic-caching-for-llms-cut-cost-and-latency-at-scale/): 30%+ of production requests repeat across user bases at meaningful similarity
- [Codezilla April 2026](https://codezilla.io/blog/how-to-optimize-llm-costs-in-production-2026-guide): combined with prompt caching + routing, 47-80% reduction

The two failure modes to budget for:

1. **False-positive cache hits** — a query about "how to cancel my subscription" returns a cached response for "how to cancel my subscription before the trial ends" — different answers. The fix: similarity threshold tuned per use case (0.95-0.97 typical for high-stakes), domain filtering on top of embedding similarity, and conversation-aware guards that exclude multi-turn-dependent queries from the cache.
2. **Cache poisoning** — an attacker submits a poisoned query; future similar queries return the poisoned response. The fix: cache writes are gated by output validation (faithfulness check, schema validation); per-tenant cache namespaces prevent cross-tenant contamination.

The structural decision: semantic cache lives in the gateway, not in application code. Application-side semantic cache means every team reimplements it; gateway-side means one configuration applies to every team's LLM calls. The [Maxim April 2026 enterprise gateway guide](https://www.getmaxim.ai/articles/5-enterprise-ai-gateways-for-llm-cost-control-in-2026/) makes this case explicitly.

### Layer 3c — KV cache optimization (model-side)

For self-hosted deployments (Shape 4 from [`production/deployment.md`](./deployment.md)), KV cache is the inference-side optimization. vLLM's PagedAttention is the production standard per [PyInns April 2026](https://www.pyinns.com/python/llm-and-generative-ai/llm-deployment-fastapi-docker-uv-python-2026-complete-guide-best-practices); the throughput gain over naive KV caching is 2-5× depending on workload concurrency.

Not relevant for hosted-API deployments — the KV cache lives inside the provider; you pay for the optimization implicitly through cached-token pricing in Layer 3a.

## Layer 4 — Budgets and kill switches

The structural defense between you and a runaway. Per [Path 03 Pattern 4 (per-agent cost budgeting)](../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md), every budget primitive has four dimensions: tokens, tool calls, cost in dollars, wall-clock. At deployment scale, these compose into a hierarchy.

### Hierarchical budgets

Per the [Maxim April 2026 gateway comparison](https://www.getmaxim.ai/articles/5-enterprise-ai-gateways-for-llm-cost-control-in-2026/): "an enterprise AI gateway controls LLM costs through three coordinated mechanisms: semantic caching to eliminate redundant provider calls, hierarchical budget controls to cap spend per team and key, and per-consumer rate limiting to prevent runaway pipelines."

| Level | Cap | Reset window | Enforcement |
|---|---|---|---|
| **Per-conversation** | $0.50-$10 (use-case dependent) | Per conversation | Hard stop with partial-finalize per [Path 03 Pattern 4](../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) |
| **Per-user-per-hour** | $5-$50 (tier-dependent) | Rolling 1 hour | 429 response with `quota_exhausted` flag |
| **Per-tenant-per-day** | $100-$10,000 (contract-dependent) | Rolling 24 hours | Account manager alert at 80%; kill switch at 100% |
| **Per-feature-per-month** | $1k-$1M (budget-dependent) | Calendar month | Engineering page at 80% projection; hard stop at 100% |

The four levels stack; a request that passes per-conversation may still trip per-user. The enforcement layer matters as much as the cap: per-conversation enforces in agent code (the partial-finalize path); per-user and per-tenant enforce at the gateway (the 429 response); per-feature is the monthly engineering review.

### Cost-anomaly detection

Static thresholds catch known failure modes; dynamic thresholds catch the unknown ones. The signals:

- **Rate-of-change on per-tenant cost**: tenant spend doubles week-over-week → investigation page (not necessarily a kill, but an investigation)
- **Distribution shift on per-conversation cost**: p95 conversation cost moves from $0.20 to $0.80 → look for a regression in prompt size, model routing, or tool-call frequency
- **Cache hit rate collapse**: semantic cache hit rate drops from 35% to 5% → either a query distribution shift or a cache invalidation bug

[FutureAGI February 2026's six-layer architecture](https://futureagi.com/blog/llm-deployment-best-practices-2026) treats cost anomaly detection as a peer layer to quality regression detection — the same observability primitives apply.

### The "tokenmaxxing" risk

Per [The New Stack May 2026](https://thenewstack.io/temporal-replay-2026-news/) (citing the broader 2026 industry framing): "tokenmaxxing is real, expensive & it's spreading." Three failure shapes:

1. **Agent self-amplification**: an agent that "thinks more" produces more tokens; reasoning-mode prompts ("think step by step in detail") can 3-5× output tokens for marginal quality. The fix: reasoning-mode is a use-case decision, not a default.
2. **Recursive elaboration**: each turn's summary gets fed back as context; summaries get longer; tokens compound. The fix: summary truncation at a fixed budget (typically 1500-2000 tokens for the rolling context).
3. **Tool-output verbosity**: a tool returning 8KB of JSON when 200 bytes would suffice consumes the agent's context. The fix: tool-output schemas with explicit truncation; "summary" return modes for verbose tools.

The structural defense: per-conversation budget enforcement (Layer 4) catches the symptoms; the diagnostic work happens against the per-conversation cost p95 distribution.

## Operational discipline: five practices

The five operational practices the 2026 literature treats as table stakes once the four layers are in place:

1. **Cost dashboard refreshed daily, per-tenant + per-feature.** The dashboard is the morning-standup artifact; weekly is too slow for the 10× single-sprint failure mode.
2. **Per-conversation top-1% review.** The 99th percentile most-expensive conversations get a weekly sanity-check — these are where the bugs live.
3. **Monthly model-version + prompt-version audit.** Provider model upgrades, prompt changes, tool additions all shift cost; a monthly audit catches the drift before quarterly billing.
4. **Cost-aware retrieval per [Path 06 Pattern 1](../learning-paths/06-evaluation-observability/patterns/01-cost-aware-retrieval.md).** The retrieval surface is one of the largest cost amplifiers; cost-aware short-circuiting on retrieval decisions is the integration with Path 06.
5. **Pricing model alignment with cost model.** The pricing conversation per [DigitalApplied April 2026](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026): "by the time the data is legible, the pricing conversation with the runaway customer is already awkward." Pricing tier and cost tier should match; if a customer on the $99/mo tier is generating $400/mo of spend, the pricing model is the bug, not the customer.

## Anti-patterns

Five cost-engineering moves that look reasonable and aren't:

### Optimize prompt length without measuring tail latency impact

Compressing a 4000-token system prompt to 1500 tokens saves ~60% on input tokens. It can also push the model into different reasoning patterns — fewer few-shot examples, different format priming. The cost win is real; the quality regression risk is real. Measure both per [Path 06's eval discipline](../learning-paths/06-evaluation-observability/).

### Aggressive semantic cache similarity threshold

A threshold of 0.85 catches more queries than 0.95, raising the hit rate. It also catches semantically-different queries that share keywords. The cost win compounds with a quality regression that surfaces 2-3 weeks later as customer-support complaints. Default 0.95; tune downward only with eval-set evidence.

### Switch to a cheaper model without re-evaluating

Gemini 1.5 Flash is 60% the cost of GPT-4o-mini. It also has a different refusal profile, different tool-calling style, different multilingual behavior. A swap based on cost alone produces quality regressions that aren't visible until users complain. Re-run the eval set after any model swap.

### Cache without per-tenant namespace

Cross-tenant cache hits leak data: tenant A's query returns a cached response from tenant B's similar query, including tenant B's data. The fix is namespacing every cache key with `tenant_id`. The cost overhead is negligible; the data-leak avoidance is not.

### Treat cost optimization as a one-time project

Cost shapes shift every quarter — provider pricing changes, model releases, prompt evolution, tool surface growth. A "cost optimization sprint" wins for a quarter; the gains compound back to the baseline within two quarters without sustained discipline. The five operational practices above are the sustaining mechanism.

## Anti-scope (what this page does not cover)

- **Specific gateway product reviews.** The [Maxim April 2026 enterprise-gateway comparison](https://www.getmaxim.ai/articles/5-enterprise-ai-gateways-for-llm-cost-control-in-2026/) covers Bifrost, LiteLLM, OpenRouter, Portkey, Cloudflare AI Gateway. Choice is organizationally specific.
- **Fine-tuning a smaller model for cost reduction.** Distillation-into-cheaper-model is a 3-12 month engineering investment; covered separately as it crosses into Path 09 territory (model-side intervention).
- **Self-hosting an open-source model to reduce per-token cost.** [`production/deployment.md`](./deployment.md) Shape 4 covers when self-hosting is the right call. Cost is one of several drivers; this page focuses on hosted-API optimization.
- **Geographic arbitrage as primary cost lever.** Real but secondary; 10-20% improvement on hosted-API workloads. Covered as a sub-bullet in Layer 2 routing.
- **Model-internal cost optimization** (quantization, pruning, MoE routing). These are model-research and model-serving topics; outside Path 07's scope of "what to do given the model's properties."
- **Batch API workflows in depth.** Anthropic's `message-batches` and OpenAI's `batch` API offer 50% discount for non-interactive workloads; the integration is straightforward but use-case-specific. Mentioned in Layer 2; not expanded here.

## References

**Cost-engineering guides and case studies (2026)**:
- [Vishnu N C (May 2026), *LLM Cost Optimization: A Practical Guide*](https://medium.com/@vishnu_73501/llm-cost-optimization-a-practical-guide-for-engineering-teams-95bca0e9aaf3) — the $9M → $3.1M case study; attribution as Layer 1; the 60%-from-12-employees anchor
- [DigitalApplied (April 2026), *LLM Agent Cost Attribution Guide*](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026) — four token layers; three attribution dimensions; instrument-on-day-one framing
- [Maxim (April 2026), *Reduce LLM Cost and Latency*](https://www.getmaxim.ai/articles/reduce-llm-cost-and-latency-a-comprehensive-guide-for-2026/) — $3.5B → $8.4B spend doubling; 47-80% combined reduction; 30%+ request repetition baseline
- [Maxim (April 2026), *5 Enterprise AI Gateways for LLM Cost Control*](https://www.getmaxim.ai/articles/5-enterprise-ai-gateways-for-llm-cost-control-in-2026/) — Bifrost, LiteLLM, OpenRouter, Portkey, Cloudflare comparison
- [Maxim (April 2026), *Best LLM Cost Tracking Tools*](https://www.getmaxim.ai/articles/best-llm-cost-tracking-tools-in-2026/) — variable per-request pricing dimensions; budget enforcement vs monitoring distinction
- [Maxim (April 2026), *Semantic Caching for LLMs*](https://www.getmaxim.ai/articles/semantic-caching-for-llms-cut-cost-and-latency-at-scale/) — dual-layer cache; conversation-aware guards
- [Codezilla (April 2026), *How to Optimize LLM Costs in Production*](https://codezilla.io/blog/how-to-optimize-llm-costs-in-production-2026-guide) — 47-80% combined reduction; prompt compression numbers
- [CallSphere (February 2026), *LLM Caching Strategies*](https://callsphere.ai/blog/llm-caching-strategies-cost-optimization-2026) — prompt vs semantic vs KV cache distinction; per-conversation cost baselines
- [Redis (January 2026), *LLMOps Guide*](https://redis.io/blog/large-language-model-operations-guide/) — Redis LangCache 73% reduction; vector + cache co-location

**Routing literature (2026)**:
- [BSWEN (March 2026), *AI Agent Routing*](https://docs.bswen.com/blog/2026-03-06-agent-routing/) — cheap-classifier / expensive-execution cost lever; 10-15% triage cost ratio
- [MintSquare (January 2026), *AI Agent Production Costs*](https://www.agentframeworkhub.com/blog/ai-agent-production-costs-2026) — 3-10× multi-agent token multiplier

**Repo cross-references**:
- [`production/deployment.md`](./deployment.md) — the deployment shapes this cost-engineering applies to (Layer 4 budget enforcement differs between Shape 1 and Shape 3)
- [`production/checklist.md`](./checklist.md) — Layer 2 (rate limiting + quota management) of the pre-launch checklist; the operational application of this page's Layer 4 budgets
- [Path 03 Pattern 4 (Per-agent cost budgeting)](../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) — the per-agent envelope this page's Layer 4 generalizes to per-tenant tiers
- [Path 06 Pattern 1 (Cost-aware retrieval)](../learning-paths/06-evaluation-observability/patterns/01-cost-aware-retrieval.md) — retrieval-side cost control that composes with this page's Layer 3 (caching)
- [Path 06 Lab 21 (Cost attribution and adaptive sampling)](../labs/21-cost-attribution-and-adaptive-sampling/) — the lab-level implementation of Layer 1 attribution
- [Pattern 02 (Router)](../patterns/02-router.md) — the architectural primitive this page's Layer 2 (model routing) operationalizes
