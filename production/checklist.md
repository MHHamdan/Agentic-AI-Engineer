# The pre-launch checklist

> 🔴 Advanced · ⏱ ~30 min · 🛠 Verified 2026-05-29 · 📍 Last read before flipping production traffic on; pairs with [`production/deployment.md`](./deployment.md)

## What this page is for

The pre-launch checklist is the discipline of *not skipping the boring parts*. Most production agent incidents in 2026 come from a small set of recurring gaps: secrets in env vars instead of secret manager, no per-tenant rate limit, no kill switch wired up, no rollback procedure rehearsed. None of these are intellectually interesting; all of them are 3am pages waiting to happen.

This page is the consolidated checklist — the things teams forget the first time, organized by layer. It's deliberately exhaustive: the team going through it before launch should catch the things they would have otherwise discovered in incident response.

The checklist is grouped into eight sections corresponding to the operational layers:

1. **Secrets and credentials** — what to put where, rotation procedure
2. **Rate limiting and quota management** — three-layer pattern, per-user / per-tenant / per-provider
3. **Kill switches and feature flags** — the breaker between you and a runaway agent
4. **Rollback and deployment safety** — what makes a deploy reversible
5. **Observability and alerting** — what you need to see to know there's a problem
6. **Abuse detection and refusal monitoring** — the user-facing signals of trouble
7. **Runbook readiness** — the documentation gates
8. **The dress rehearsal** — what to actually do the day before launch

This is the companion piece to [`production/deployment.md`](./deployment.md) — that page covers the architecture decisions; this page covers the launch discipline.

## Layer 1 — Secrets and credentials

The least-glamorous and most-skipped layer. Get this wrong and the smallest incident becomes a credential-rotation post-mortem.

### Checklist

- [ ] **All API keys in a secret manager**, not env vars. AWS Secrets Manager, HashiCorp Vault, Doppler, 1Password Secrets Automation, Google Secret Manager, Azure Key Vault — any of these. Env vars are visible in container inspection, CI/CD logs, error stack traces, and crash dumps.
- [ ] **Per-service API keys**, not a single shared key. Per [Hivenet's 2026 production checklist](https://www.hivenet.com/post/llm-production-checklist): "per-service keys, with strong key management practices including regular key rotation, access controls, and monitoring." If your Anthropic key leaks, you don't want to rotate it across 8 services simultaneously.
- [ ] **Key rotation procedure documented and rehearsed.** A runbook entry that a not-the-author teammate can follow. Rehearse it in staging at least once before launch — keys you've never rotated are keys you don't know how to rotate.
- [ ] **No keys in Git history.** Run `git-secrets` or equivalent in CI to block commits that include credential patterns. If a key did land in history at any point, it's compromised regardless of subsequent rebases — rotate immediately.
- [ ] **Database connection strings include credentials only in the secret manager.** The `POSTGRES_URI` pulled at runtime, never hard-coded. Same for vector DB connections, Redis, message-queue endpoints.
- [ ] **Audit logging on secret access.** AWS CloudTrail / GCP Audit Logs / Vault audit log — when an unexpected service accesses your Anthropic key, you should see it within minutes, not after the bill arrives.
- [ ] **JWT signing keys rotated independently of API keys.** Different blast radius, different rotation cadence. JWT signing keys should rotate quarterly minimum; API keys should rotate when there's any suspicion of compromise.
- [ ] **Per-environment isolation**. Staging keys must not work against production endpoints (and vice versa). Confirmed by attempting a cross-environment request and seeing it fail.

### What you're defending against

Three failure modes this layer prevents:
1. **Credential leak via error stack trace.** A `KeyError` exception with the env-var name in the message gets posted to a public bug tracker by a teammate; the env-var name was a complete key.
2. **Disgruntled-departure compromise.** An employee leaves; the on-call team can't remember which keys they had access to; you end up rotating everything for safety.
3. **CI/CD log leak.** A flaky test dumps the API key into the build log; the CI log is public for OSS projects.

## Layer 2 — Rate limiting and quota management

Per [TrueFoundry's May 2026 rate-limiting guide](https://www.truefoundry.com/blog/rate-limiting-ai-agents-preventing-llm-api-exhaustion): "drained the API quota in 20 minutes is not a mythical SRE story; it's a Tuesday afternoon with a poorly bounded loop." Rate limiting is the structural defense.

### Checklist

- [ ] **Three-layer rate limit at the gateway**:
  - [ ] **Per-user**: token-bucket per `user_id`, prevents one user saturating the pool (typical: 60 requests/min, 100K tokens/hour)
  - [ ] **Per-tenant**: per-tenant total across all users (typical: 1M requests/day on enterprise tier)
  - [ ] **Per-LLM-provider**: per-`(provider, model)` total to stay under provider TPM/RPM ceilings (typical: 80% of provider's published limit, with headroom)
- [ ] **Token-aware limits, not just request-count.** A 50K-token research-pipeline request is structurally different from a 200-token chat request. Rate-limit on tokens-per-minute for the provider-facing limit; request-count is fine for the user-facing limit.
- [ ] **Quota dashboard with current consumption visible.** Grafana or equivalent showing: requests-per-second by tenant, tokens-per-minute by `(tenant, model)`, error rate by tenant. The dashboard is the first thing the on-call team looks at when a customer reports degradation.
- [ ] **429 responses include `Retry-After` header.** Clients should back off automatically; gateway should set `Retry-After` to a value larger than the rate-limit window remainder.
- [ ] **Per-tenant quota alerts**. When a tenant reaches 80% of monthly quota, page their account manager; when they reach 100%, the gateway returns `quota_exhausted` with an upgrade prompt.
- [ ] **Cost alerts at 50%, 80%, 95% of monthly budget.** Per [DigitalApplied's April 2026 cost attribution guide](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026): "by the time the data is legible, the pricing conversation with the runaway customer is already awkward." Alert early.
- [ ] **Per-conversation token-budget cap** per [Path 03 Pattern 4](../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md). A single conversation that would consume 1M tokens (degenerate research question, infinite-loop bug, prompt-injection-induced runaway) hits the cap and partial-finalizes with an explicit caveat.

### What you're defending against

- **Quota exhaustion from one bad actor or one bug.** A poorly-bounded `while True:` in an agent loop consumes a quarter's API budget in 20 minutes. With per-user + per-tenant + per-conversation budgeting, the blast radius is one conversation, not one quarter.
- **429 cascades**. Provider returns 429; agent retries immediately; multiplied across users; rate-limit-on-rate-limit cycle. Three-layer rate limit at YOUR gateway prevents your traffic from creating provider-side 429s in the first place.
- **Cost surprise.** The monthly bill arrives 8× expected; nobody noticed during the month because the only cost view was the provider's billing dashboard, checked once at month-end.

## Layer 3 — Kill switches and feature flags

The breaker between you and a runaway agent. Every production agent system should have at least three kill switches at three different layers.

### Checklist

- [ ] **Per-agent kill switch**, flippable from a config UI or Redis key, no deploy required. When you discover a bug in the billing-specialist agent's tool selection, you flip the kill switch and route to a fallback response while you fix.
- [ ] **Per-tenant kill switch**. When a customer's traffic is causing problems and you need to disable their access while you investigate, no deploy required.
- [ ] **Global kill switch (all agents off)**. The "we have a security incident; everything off until we understand" switch. Returns a generic maintenance message to all users.
- [ ] **Kill switches default to ON in production**, flipped explicitly when needed. Some teams default to OFF to avoid accidental disable; the safer default is ON with explicit kill option per [the agentgateway February 2026 case study](https://agentgateway.dev/blog/2026-02-21-kill-switch/).
- [ ] **Kill-switch state visible in observability**. When the kill switch is flipped, every observability signal (Grafana, LangSmith, on-call channel) shows it; no engineer should debug "why is the agent returning maintenance" while the cause is a flipped switch.
- [ ] **Feature flags for risky changes**. A new prompt, a new model, a new tool — gated behind a feature flag with 1% / 10% / 50% / 100% rollout stages.
- [ ] **High-risk action confirmation gates**. Per [Wiz's February 2026 LLM security guide](https://www.wiz.io/academy/ai-security/llm-security): "high-risk action confirmation: require a second check for actions like 'reset MFA,' 'wire funds,' 'rotate secrets,' or 'delete data.'" These actions require human-in-the-loop approval per [Pattern 10](../patterns/10-human-in-the-loop.md), enforced at the tool boundary.

### The four-line test

The kill switch works only if any on-call engineer can flip it. The four-line test: have a teammate who didn't build the system disable a specific agent within 60 seconds, using only the runbook and access they're routinely granted. If they can't, the kill switch isn't ready for production.

## Layer 4 — Rollback and deployment safety

Deploys must be reversible. The 2026 production literature ([FutureAGI February 2026](https://futureagi.com/blog/llm-deployment-best-practices-2026)) is explicit: "a prompt change ships at 4pm on Tuesday. By 5pm, refund agent groundedness is down 12%, refusal rate has flipped from 4% to 27%, and customer support is fielding angry emails. The on-call engineer rolls the prompt back from a Slack thread."

### Checklist

- [ ] **Container image rollback procedure documented and rehearsed**. Within 5 minutes, an on-call engineer should be able to roll back to the previous image tag. Tested in staging at least once before launch.
- [ ] **Database migration reversibility**. Every Alembic migration (or equivalent) has a working `downgrade()` path. Tested by running upgrade-then-downgrade in CI.
- [ ] **Prompt versioning and rollback**. Prompts stored in a versioned prompt registry (Langfuse, LangSmith, internal registry) — not hard-coded in source. A prompt change is a config-level operation, not a code deploy, and rolls back without a code deploy.
- [ ] **Model version pinning**. The exact model string (`claude-sonnet-4-5-20260201`, `gpt-4o-2024-08-06`) pinned in config. Provider-side model upgrades that move the default `latest` tag should not silently change your production behavior.
- [ ] **Blue-green or canary deploy pattern**. New version rolls out to 1-5% of traffic first; eval gates check for regression; promotes to 100% only after passing.
- [ ] **Eval gates in CI/CD pipeline**. Per [FutureAGI February 2026](https://futureagi.com/blog/llm-deployment-best-practices-2026): the prompt change that caused the 12% groundedness drop "passed code review, deployed without eval gates, hit production without per-user A/B, and triggered no automatic rollback." Eval gates are the structural defense.
- [ ] **Automatic rollback on quality regression**. If post-deploy metrics (refusal rate, error rate, P95 latency, faithfulness score) regress beyond threshold within the first hour, automatic rollback. Don't require human judgment in the loop for the obvious cases.
- [ ] **Deploy-window discipline**. No deploys on Fridays after noon, no deploys before holiday weekends. Per [Hivenet's 2026 checklist](https://www.hivenet.com/post/llm-production-checklist): the on-call team responding to an incident shouldn't be debugging "what did we change this afternoon" simultaneously.

## Layer 5 — Observability and alerting

You can't operate what you can't see. Per [LangChain's April 2026 deep agents runtime guide](https://www.langchain.com/blog/runtime-behind-production-deep-agents): "observability tells you what happened; time travel lets you ask what would have happened if something had gone differently." Both layers matter.

### Checklist

- [ ] **Distributed tracing on every request** — OpenTelemetry or LangSmith — with `trace_id`, `thread_id`, `user_id`, `tenant_id`, `model_string` as standard span attributes.
- [ ] **Per-request cost attribution.** Each trace shows the dollar cost of that request; aggregations by `tenant_id`, `user_id`, `agent_kind` available in the trace UI. The four token layers (prompt, tool, memory, response) tracked separately per [DigitalApplied April 2026](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026).
- [ ] **Latency histograms** (p50, p95, p99) for: end-to-end response, per-LLM-call, per-tool-call, per-database-query. The p99 is the most informative for production: it's where the tail latency lives.
- [ ] **Error-rate dashboards** broken down by error class: LLM 5xx, LLM 429, tool 5xx, tool 4xx, database timeout, validation error. Different error classes call for different responses.
- [ ] **Alert on rate-of-change, not absolute thresholds**, for quality metrics. Refusal rate of 4% is fine; refusal rate moving from 4% to 27% in an hour is a P1 page. Set alerts on the delta, not the value.
- [ ] **PagerDuty (or equivalent) integration** with at least two tiers:
  - [ ] **T2 (page eval engineer)**: post-deploy quality regression > threshold; sustained 5xx > 1% over 5 minutes; cost spike > 3× rolling average
  - [ ] **T3 (page on-call)**: complete service outage; security incident; sustained error rate > 10%
- [ ] **Alert deduplication and rate-limiting** on the alert pipeline itself. A 500-alert flood from one root cause should consolidate into one page, not 500.
- [ ] **Logs structured (JSON), not free-text**. `structlog` or equivalent; each log line is parseable; correlation IDs (`request_id`, `trace_id`) on every line.
- [ ] **Log retention sized for incident response.** At minimum, 30 days hot (queryable in under a second) + 90 days cold (archived). Most incidents reach the post-mortem within 7-14 days; the data you need must still exist.

## Layer 6 — Abuse detection and refusal monitoring

The user-facing signals of trouble. Sometimes the agent is doing something it shouldn't; sometimes users are doing something they shouldn't. Both need visibility.

### Checklist

- [ ] **Refusal-rate monitoring per `(model, prompt_version, tenant)`**. A sudden refusal-rate spike usually means either a prompt change (Layer 4 catches this) or a real user-base shift toward harder queries. Both are diagnostic signals.
- [ ] **Prompt-injection attempt detection**. Inputs containing classic injection patterns (`Ignore previous instructions`, `IGNORE ALL PRIOR`, base64-encoded instructions, role-confusion templates) flagged in observability. Path 07 Module 4 will cover the detection patterns in depth; the *monitoring* of attempts is part of pre-launch.
- [ ] **PII leakage detection on outputs**. Outputs scanned for credit-card patterns, SSN patterns, email patterns that didn't appear in input — these are the canonical exfiltration signals. Per [Wiz's February 2026 LLM security guide](https://www.wiz.io/academy/ai-security/llm-security), "AI Security Posture Management (AI-SPM) provides continuous visibility into enterprise AI deployments."
- [ ] **Per-user behavior anomaly detection**. One user issuing 10× their median request volume in an hour, or making requests at 3am from a new country — these are signals that don't necessarily mean compromise but warrant investigation.
- [ ] **Tool-call frequency monitoring**. An agent that suddenly starts calling the `delete_user` tool 100× its baseline is either misrouted, prompt-injected, or buggy. Per-tool-per-agent rate monitoring catches all three.
- [ ] **User-reported issue triage path**. When a user reports "the agent said something weird," the triage path goes: trace lookup by user-message-hash → conversation replay → root-cause classification (model regression / prompt issue / data issue / injection attempt). Documented in the runbook (Layer 7).
- [ ] **Audit log for high-stakes actions** — refunds applied, accounts modified, payments initiated. Append-only table at the database level (the application role cannot UPDATE or DELETE), with cryptographic chain integrity if compliance requires it.

## Layer 7 — Runbook readiness

The discipline of writing down what to do so the on-call team doesn't have to figure it out at 3am.

### Checklist

- [ ] **"How to flip the kill switch" runbook entry**. Step-by-step including which Redis key to set, how to verify it took effect, how to communicate the outage.
- [ ] **"How to roll back a deploy" runbook entry**. Container image rollback + database migration rollback + prompt-registry rollback. Each is a separate procedure; the runbook documents the sequence.
- [ ] **"How to investigate a cost spike" runbook entry**. Trace lookup by cost, top-N expensive conversations, attribution by `tenant_id` and `user_id`. The path from "cost is up" to "this tenant is doing X" should be five minutes, not a Slack archaeology session.
- [ ] **"How to investigate a quality regression" runbook entry**. Eval-set re-run, dataset diff, model-version check, prompt-registry version check. The path from "quality is down" to "we deployed prompt v17 at 2pm and it's regressing on category X" should be ten minutes.
- [ ] **"How to debug a misrouted conversation" runbook entry**. Trace lookup by `conversation_id`, routing decision in the trace, expected vs actual route, model-string check. Annotated example with arrows in the runbook.
- [ ] **"Who do I page when X is down" matrix**. PagerDuty integration is necessary but not sufficient; the matrix is the human-readable layer: vector DB down → DBA team; LLM provider down → switch to fallback model + page eval engineer; Postgres slow → page DBA team.
- [ ] **"How to communicate with users during an incident" template**. Status page update template, customer support escalation template, executive briefing template — pre-written, with placeholders for incident specifics.
- [ ] **Runbook tested by a teammate not involved in writing it**. The four-line test from Layer 3 generalizes: any on-call engineer should be able to execute any runbook from a clean state. If they can't, the runbook isn't ready.

## Layer 8 — The dress rehearsal

The day before launch (or staging-to-production cutover), run the rehearsal. The point is to find the things you can't think of beforehand.

### Checklist

- [ ] **Load test at 2× expected peak traffic**. Half-day load test against staging at twice the projected peak. P95 latency under load is the data you want; observed failure modes are the data you really want.
- [ ] **Kill-switch dry run**. Flip the kill switch in staging; confirm all traffic routes to the fallback within 30 seconds; flip it back; confirm normal operation resumes. Time it.
- [ ] **Rollback dry run**. Deploy a known-bad change to staging; trigger the rollback procedure; time it end-to-end. The 5-minute target from Layer 4 should hold.
- [ ] **Alert pipeline test**. Intentionally trigger each alert class (5xx burst, cost spike, refusal-rate spike, latency spike). Verify each fires the right page, to the right team, with the right runbook link in the alert body.
- [ ] **Cost-budget exhaustion test**. Set a per-conversation cost budget intentionally low; trigger a request that exceeds it; confirm partial-finalize with structured caveat, not silent over-spend or stack trace.
- [ ] **Multi-LLM-provider fallback test**. Disable the primary LLM provider in staging (firewall rule blocking egress); confirm the agent falls back to the secondary provider within the retry budget; confirm the fallback is visible in observability.
- [ ] **One adversarial walkthrough**. Have a security-minded teammate spend an hour trying to break the agent — prompt injection, jailbreak attempts, tool abuse. Find the gap before launch; Module 7 (red-team pass) covers the structured version.
- [ ] **One pricing walkthrough**. Have a finance/product person walk through the cost dashboard, identify the most expensive 1% of conversations, and answer "are these prices what we'd want to bill the customer at." The answer is sometimes no, and the conversation is better had before launch than after.

### The 30-minute pre-flight call

The dress rehearsal closes with a 30-minute call: engineering + product + on-call. Walk through each layer's checklist out loud. Anyone with a "wait, what about..." gets heard. The checklist gets updated based on what surfaces. The launch is approved only when every item is either checked or has a documented and accepted exception.

## What this checklist does not cover

- **Generic application-security hygiene** — SQL injection, XSS, CSRF, OAuth flows. Standard web/API security still applies; Path 07 covers what's new in agentic systems specifically.
- **Compliance certifications** — SOC 2, HIPAA, ISO 27001 certifications are their own discipline. This checklist covers the practices that make compliance work easier, not the certification process itself.
- **Specific tool choices** for each layer. Secrets-manager choice, observability backend choice, paging tool choice — all organizational decisions. The checklist enumerates the categories; the tool selection is downstream.
- **Post-launch operational practices** — incident response process, post-mortem format, on-call rotation discipline. Standard SRE practices apply; Path 07 doesn't re-derive them.
- **The actual prompt-injection defense stack** (Module 4) and **tool-abuse defenses** (Module 5). The *monitoring* of those threats is in Layer 6 here; the *defenses* are their own modules.

## References

**2026 production checklists and operational guides**:
- [FutureAGI (Feb 2026), *LLM Deployment Best Practices in 2026: A Production Checklist*](https://futureagi.com/blog/llm-deployment-best-practices-2026) — six-layer production architecture; the 4pm-Tuesday-prompt-change failure mode
- [Hivenet, *Production Checklist for Your LLM API*](https://www.hivenet.com/post/llm-production-checklist) — per-service keys; key management; deploy-window discipline
- [DigitalApplied (Apr 2026), *LLM Agent Cost Attribution Guide*](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026) — four token layers; three attribution dimensions; the "deferred to once we have traffic" failure mode
- [TrueFoundry (May 2026), *Rate Limiting AI Agents*](https://www.truefoundry.com/blog/rate-limiting-ai-agents-preventing-llm-api-exhaustion) — three-layer gateway pattern; on-call rotation between platform and product
- [agentgateway (Feb 2026), *Multi-Agent Architecture with a Kill Switch*](https://agentgateway.dev/blog/2026-02-21-kill-switch/) — kill switch as default-ON with explicit kill option

**Security and abuse-detection sources (2026)**:
- [Wiz (Feb 2026), *LLM Security: Protecting Models, RAG & Data Pipelines*](https://www.wiz.io/academy/ai-security/llm-security) — high-risk action confirmation; AI-SPM continuous visibility
- [Prospeo, *Autonomous AI Agents for Sales in 2026: Deploy Safely*](https://prospeo.io/s/autonomous-ai-agents-for-sales) — stoplight mode, approval gates, kill switch ownership
- The OWASP Top 10 for LLM Applications at [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10) — the threat-model taxonomy this checklist's Layer 6 references

**Observability and operational discipline (2026)**:
- [LangChain (Apr 2026), *The Runtime Behind Production Deep Agents*](https://www.langchain.com/blog/runtime-behind-production-deep-agents) — observability + time-travel debugging framing
- [Aiamastery Substack (Jan 2026), *Lesson 6: Interacting with LLM APIs — production integration patterns at enterprise scale*](https://aiamastery.substack.com/p/lesson-6-interacting-with-llm-apis) — secure credential management; token-bucket rate limiting; circuit breakers

**Repo cross-references**:
- [`production/deployment.md`](./deployment.md) — the deployment shapes this checklist applies to
- [`production/README.md`](./README.md) — the production playbook this checklist anchors
- [Path 03 Pattern 3 (Escalation and fallback)](../learning-paths/03-multi-agent-systems/patterns/03-escalation-and-fallback.md) — the T0-T3 tier semantics used in Layer 5's alerting tiers
- [Path 03 Pattern 4 (Per-agent cost budgeting)](../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) — the per-conversation cost-budget cap used in Layer 2
- [Path 03 Pattern 5 (Retry policies)](../learning-paths/03-multi-agent-systems/patterns/05-retry-policies.md) — the retry-with-backoff foundation Layer 4 assumes is in place
- [Pattern 10 (Human-in-the-loop)](../patterns/10-human-in-the-loop.md) — the architecture pattern for high-risk action approval gates in Layer 3
