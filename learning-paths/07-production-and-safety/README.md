# Path 07 — Production & Safety

> 🔴 Advanced · ⏱ 10–15 hours (planned) · 📍 Start here after Path 06 (Evaluation & Observability) · 📋 **Scaffold — content forthcoming**

> ⚠️ **This path is a scaffold.** The structure, prerequisites, and learning outcomes are locked. The actual concept pages, labs, and module content land in future batches. The "What you can read right now" section below points at real, existing artifacts in the repo — including the substantive [`production/`](../../production/) and [`security/`](../../security/) directories — that already cover material this path will build on.

## Who this path is for

Engineers with an evaluated agent and a deployment target. You've measured the system in Path 06; now you need to ship it without burning money, leaking secrets, or shipping a model that can be jailbroken into the wrong tool. You've felt one or more of: cost runaway after a launch spike, a prompt-injection compromise that bypassed your guardrails, a tool-call thrashing incident, or the "it works on my notebook but not in production" gap.

## What you'll be able to do

When this path is complete, you'll be able to:

- **Estimate and reduce production cost** — token budgets at the deployment scale, model routing, multi-tier caching, semantic caching, batching, prompt compression. The cost-control playbook builds on Path 03 Pattern 4 (per-agent budgets) and Path 06 Module 6 (cost attribution).
- **Design defense-in-depth against prompt injection** — direct and indirect injection patterns; input filtering, output filtering, content classification; sandboxing and least-privilege tool access. No single defense is reliable per the [`security/`](../../security/) framing; layering is.
- **Deploy a stateful agent with durable execution** — FastAPI patterns, durable workflows, serverless trade-offs, on-prem deployments; checkpoint-and-resume vs replay-from-trace semantics.
- **Run a structured red-team pass** — pre-launch adversarial probing using the Path 06 v2 adversarial red-teaming infrastructure; jailbreak resistance; data-exfiltration testing; tool-abuse scenarios.
- **Author a domain-specific safety policy** — what counts as a harm in your context; content-moderation taxonomies; refusal-criteria specifications. This is the policy-authorship dimension that Path 06 v2's adversarial-eval batch explicitly leaves to Path 07.
- **Pass the pre-launch checklist** — the production-readiness items teams forget the first time: secrets rotation, rate limits, abuse detection, escalation paths, kill switches, rollback procedures.

## Prerequisites

- **Path 06 Evaluation & Observability** complete. You don't ship what you can't measure; Path 07 assumes Path 06's evaluation infrastructure is in place.
- **Path 03 Multi-Agent Systems** recommended if your production system is multi-agent — Pattern 4 (cost budgeting) and Pattern 3 (escalation/fallback) are the operational substrate.
- Real-world deployment experience (any non-trivial production system, not just agents) helps significantly. Path 07 assumes you've seen production incidents before, not necessarily LLM ones.

## Path structure (planned)

The planned module breakdown:

| Module | Topic | Status |
|---|---|---|
| 1 | **Deployment patterns** — FastAPI + Docker, durable execution (Temporal, Inngest, LangGraph Cloud), serverless trade-offs, on-prem; stateful vs stateless agent design | 📋 Planned |
| 2 | **Cost engineering at deployment scale** — extends Path 03 Pattern 4 to per-tenant tiers; model routing strategies; multi-tier and semantic caching; batching | 📋 Planned |
| 3 | **Latency and streaming** — token streaming, partial tool outputs, frontend wiring; async patterns for parallel tool calls and multi-agent fan-out | 📋 Planned |
| 4 | **Defense-in-depth against prompt injection** — direct and indirect injection; tool-output sanitization; the OWASP Top 10 for LLM Applications framing; defenses that work vs defenses that sound reassuring | 📋 Planned |
| 5 | **Tool abuse and data exfiltration** — least-privilege tool access; output-channel control; the agent attack surface vs the LLM attack surface | 📋 Planned |
| 6 | **Safety policy authorship** — the Path 06 v2 anti-scope this path closes. Domain-specific harm taxonomies; refusal-criteria specifications; the medical / legal / financial vertical patterns | 📋 Planned |
| 7 | **Pre-launch red-team pass** — adversarial probing using Path 06 v2's adversarial-red-teaming infrastructure; the EU AI Act high-risk obligations (August 2026 enforcement deadline) | 📋 Planned |
| 8 | **The pre-launch checklist** — the things teams forget; secrets, rate limits, kill switches, rollbacks, runbooks | 📋 Planned |

Each module will follow the Path 06 shape: concept page(s) + lab + recipes where appropriate, with reference solutions where labs apply.

## What you can read right now

This path is the *only* path with two complete, substantive supporting directories in the repo already. Reading them is the right preparation for the eventual modules:

**The production playbook** — substantive, structured, ready to extend:
- [`production/README.md`](../../production/README.md) — 60+ line README cataloging the seven planned production pages (`deployment.md`, `observability.md`, `cost-engineering.md`, `caching-and-routing.md`, `streaming.md`, `async-and-concurrency.md`, `checklist.md`). The "Common tracks through this folder" table is the right starting point for triaging your specific problem.

**The security playbook** — substantive, structured, ready to extend:
- [`security/README.md`](../../security/README.md) — 60+ line README cataloging six planned security pages (`prompt-injection.md`, `tool-abuse.md`, `data-exfiltration.md`, `jailbreaks.md`, `guardrails.md`, `red-teaming.md`). The "grounding note" on what's well-understood vs actively researched is the right calibration for any 2026 security claim.

**Adversarial red-teaming as evaluation/observability** (already shipped in Path 06 v2):
- [`concepts/evaluation/adversarial-red-teaming-at-scale.md`](../../concepts/evaluation/adversarial-red-teaming-at-scale.md) — the Path 06 v2 concept page that closes the evaluation/observability dimension of red-teaming. Path 07 Module 6 + 7 will cover the *complementary* safety-policy-authorship dimension.
- [Lab 24 adversarial red-teaming](../../labs/24-adversarial-red-teaming-at-scale/) — the executable red-team harness; Path 07 Module 7 will use this infrastructure for the pre-launch pass

**Operational patterns from Path 03 v2** (cost and escalation foundations):
- [Path 03 Pattern 4 — Per-agent cost budgeting](../03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) — the per-agent envelope; Module 2 extends to per-tenant tiers and per-deployment scaling
- [Path 03 Pattern 3 — Escalation and fallback](../03-multi-agent-systems/patterns/03-escalation-and-fallback.md) — the T0-T4 escalation ladder; Module 7's red-team pass uses this routing infrastructure
- [Path 03 Pattern 5 — Retry policies](../03-multi-agent-systems/patterns/05-retry-policies.md) — state-level circuit breakers; the production-incident substrate

**The architecture-pattern catalog**:
- [Top-level `patterns/README.md`](../../patterns/) — Pattern 10 (Human-in-the-loop) is the architecture-level entry for the HITL approval gates this path will operationalize

**Foundational reading** (start here before the path lands):
- The OWASP Top 10 for LLM Applications at genai.owasp.org/llm-top-10
- Anthropic, OpenAI, and Google DeepMind agent-security research
- The EU AI Act high-risk-category obligations (August 2026 enforcement deadline)

## What's not in this path (anti-scope)

When Path 07 ships, these are explicitly out of scope:

- **Generic application security** (SQL injection, XSS, CSRF, OAuth flows). Path 07 covers what's *new* in agentic systems: prompt injection, tool abuse via the LLM, exfiltration through tool outputs. Standard web/API security still applies and is well-covered elsewhere.
- **Vendor product reviews** of specific guardrail libraries. The guardrail library market is fast-changing; Path 07 covers defense-in-depth *principles* and *patterns* that survive specific vendor changes.
- **Compliance certifications** (SOC 2, HIPAA, ISO 27001 specifically). Path 07 covers the security and safety practices that *enable* compliance work; the certification process itself is its own discipline.
- **Model-internal safety training** (RLHF, constitutional AI, refusal tuning). Path 07 covers what to do *given* a model's safety properties, not how to train them. The safety-policy-authorship work in Modules 6-7 informs what you'd want from a tuned model but is downstream of that work.
- **Operational SRE practices that aren't LLM-specific** — pager rotation, runbook structure, post-incident review formats. These transfer from existing SRE literature; Path 07 covers the LLM-specific differences.

## What comes next

Contributions are welcome. The way to help build Path 07:

1. **Open an issue or discussion** describing which module you want to contribute to (concept page, lab, recipe, or all three).
2. **Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md)** — the source-citation rules and the security-content rules in particular are non-negotiable.
3. **War stories make the best Path 07 content.** If you've debugged a real incident — cost runaway, prompt-injection compromise, tool-call thrashing, data exfiltration — that's the highest-leverage contribution this path can receive.

The natural first batch for Path 07 would be Module 1 (Deployment patterns) + Module 8 (Pre-launch checklist) shipped together — they bookend the path and make it actionable for anyone with a deployment deadline.

## References

Seed references for the modules that will land. Each module will add its own; these are the foundational sources Path 07 will build on:

**Production-system design**:
- [`production/README.md`](../../production/README.md) — the playbook this path will deepen
- Anthropic (2024), *[Building effective agents](https://www.anthropic.com/research/building-effective-agents)* — the production-grounded essay; deployment patterns appear throughout
- Google's *Site Reliability Engineering* book — the SRE foundations Path 07 specializes for LLM systems

**Security**:
- [`security/README.md`](../../security/README.md) — the threat-model playbook this path will deepen
- OWASP Top 10 for LLM Applications — the canonical 2026 threat taxonomy
- Anthropic, OpenAI, Google DeepMind agent-security research — published threat models and defense patterns

**Regulatory and standards**:
- EU AI Act — high-risk category obligations; August 2026 enforcement deadline
- NIST AI Risk Management Framework — Measure 2.6 adversarial-testing-and-escalation requirement
- ISO 42001 — AI management system standard

**Adversarial evaluation (already shipped in Path 06 v2)**:
- [`concepts/evaluation/adversarial-red-teaming-at-scale.md`](../../concepts/evaluation/adversarial-red-teaming-at-scale.md) — Path 06 v2 concept; the evaluation/observability dimension of red-teaming
- [Lab 24](../../labs/24-adversarial-red-teaming-at-scale/) — executable harness; Path 07's Module 7 builds on this

**Adjacent repo content**:
- [Path 03 v2 patterns](../03-multi-agent-systems/patterns/) — operational mechanisms; Patterns 3, 4, 5 are the most production-relevant
- [Path 06 Evaluation & Observability](../06-evaluation-observability/) — the measurement infrastructure Path 07 builds on top of
- [Top-level `patterns/`](../../patterns/) — architecture-level pattern catalog; Pattern 10 (HITL) is the canonical Path 07 entry
