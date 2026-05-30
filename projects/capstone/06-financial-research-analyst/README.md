# Project 06 — Financial research analyst

> 🔴 Capstone · ⏱ 30-40+ hours · 📍 Capstone-tier — after Paths 01 + 02 + 03 + 04 + Path 06 · 🛠 Verified 2026-05-29

## What you're building

A multi-agent system that produces investment research reports against regulated-domain constraints: every claim traces back to a verifiable source (SEC filing / press release / market data feed); every model decision is logged with sufficient detail to satisfy an internal audit or external regulator; every output flows through a defensible review pipeline before delivery. The system has at least 3 cooperating agents (research / analysis / compliance review), an immutable audit log, and a provenance layer that makes "how did this system arrive at that recommendation?" a one-query answer.

This is the *regulated-domain capstone* — where the engineering challenge isn't just building a working agent, it's building one that survives a compliance review. Where [Project 07 (Evaluated multi-agent system)](../07-evaluated-multi-agent-system/) emphasizes observability and evaluation as production discipline, Project 06 emphasizes provenance and auditability as compliance discipline.

## Why this matters

Three distinguishing claims for a portfolio:

1. **Regulated-domain AI is the largest enterprise surface in 2026** — financial services, healthcare, legal, and government all have explicit AI governance requirements. Per [DEV Community April 2026](https://dev.to/waxell/your-ai-agents-and-the-audit-trail-what-compliance-actually-needs-33i5): "FINRA and the SEC are actively developing AI-specific guidance. The emerging theme is that explainability and auditability requirements that apply to automated decision-making in financial services extend to AI agent systems making or supporting consequential decisions."
2. **The audit trail is the load-bearing artifact** — per [Lawrence Emenike, December 2025](https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987): "Audit trails... allow a financial institution to reconstruct, explain, and defend every AI-driven decision when an auditor, regulator, or board member asks: 'How did this system arrive at that recommendation?'" Building the audit trail correctly is the engineering depth this project demonstrates.
3. **Provenance composes Path 03 Pattern 6 with real-domain constraints** — Path 03 v2 Pattern 6 (Cross-agent provenance) is the operational substrate; financial domain rules (SEC filing as source of truth; verified vs unverified claims) are the constraint surface. This capstone is where the two compose.

The portfolio claim: "I can ship agentic systems that satisfy regulatory audit requirements." This positions for any enterprise AI role in financial services, healthcare, legal tech, or government contracting.

## Prerequisites

| Required | Why |
|---|---|
| **Path 01 — Foundations** complete | Agent loop, tool calling, structured outputs |
| **Path 02 — Agentic RAG** (canonical RAG + agentic RAG) | Retrieval over SEC filings and financial documents |
| **Path 03 — Multi-Agent Systems** v1 + v2 patterns | Topology + the six v2 patterns; **Pattern 6 (Cross-agent provenance) is load-bearing** |
| **Path 04 — Tool Protocols (MCP + A2A)** (at least MCP consumption) | Real-data backend integration (SEC EDGAR, market data, internal systems) |
| **Path 06 — Evaluation & Observability** v1 + v2 | LLM-as-judge for the compliance reviewer; calibrated judges for high-stakes decisions |
| Working Python 3.10+ environment | Repo baseline |
| Anthropic / OpenAI API key | Models for the agents |
| SEC EDGAR API access (free) | Primary data source for verifiable filings |
| Trace storage backend with retention | Langfuse self-hosted, Phoenix OSS, or managed (Braintrust / Latitude) — must support long-term retention (90+ days) |
| Comfort with multi-day software builds | Capstone-tier scope |

Helpful but not required: Path 05 (token budgets useful for per-agent cost caps), Path 07 (if you want to add safety policy + red-teaming layer).

## What you'll build

Six concrete deliverables:

1. **A multi-agent research system** — at least 3 agents (research / analysis / compliance review) in a defended topology
2. **An immutable audit log** with the minimum schema (timestamp_UTC, audit_id, user_id, model_name, model_version, prompt_version, tool_calls, sources_cited, verdict) per the [Lawrence Emenike minimum schema](https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987)
3. **A provenance layer** — every numerical claim in every report traces to a specific SEC filing or data feed; clicking the citation returns the source span
4. **Three example research reports** with full audit trails: a 10-K analysis, a competitive comparison, an earnings-call synthesis
5. **A compliance reviewer agent** — automated first-pass review that flags missing citations, contradictions, claims that should not be in scope
6. **A `WRITEUP.md`** with ADRs per architecture layer (5-7 ADRs)

## Architecture overview

The system has five layers. Each maps to specific repo material and specific 2026 financial-AI source material.

| Layer | Components | Repo material | 2026 source |
|---|---|---|---|
| **1 — Agent topology** | Research agent (gathers) → Analysis agent (synthesizes) → Compliance reviewer (verifies) | [Path 03 v1 patterns](../../../learning-paths/03-multi-agent-systems/) — supervisor-worker or plan-and-execute | [FinregE December 2025](https://finreg-e.com/how-to-safely-use-llms-in-financial-services/) — review/validation/approval loop |
| **2 — Provenance substrate** | Every output traces to inputs to sources; Path 03 v2 Pattern 6 implemented as load-bearing | [Path 03 v2 Pattern 6 (cross-agent provenance)](../../../learning-paths/03-multi-agent-systems/patterns/) | [Lawrence Emenike Dec 2025](https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987) — transaction provenance + source attribution + regulatory mapping |
| **3 — Audit log layer** | Immutable append-only log per minimum schema; queryable for compliance retrieval | [Path 06 Modules 1-3 (tracing)](../../../learning-paths/06-evaluation-observability/) | [Lawrence Emenike Dec 2025](https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987) — minimum schema |
| **4 — Compliance review** | Automated reviewer agent + (optional) human approval gate for high-stakes outputs | [Path 06 Pattern 3 (judge ensemble)](../../../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md) | [DEV Community April 2026](https://dev.to/waxell/your-ai-agents-and-the-audit-trail-what-compliance-actually-needs-33i5) — explainability + audit-trail requirements |
| **5 — Source integration** | SEC EDGAR + (optional) market data + (optional) internal sources via MCP | [Path 04 — MCP consumption](../../../learning-paths/04-tool-protocols-mcp-a2a/) | SEC EDGAR API specification |

The five layers compose: requests flow through Layer 1; Layer 2 enforces provenance; Layer 3 logs everything; Layer 4 reviews before delivery; Layer 5 grounds claims in verifiable sources.

## The audit trail as load-bearing engineering challenge

Per the [Lawrence Emenike December 2025 framing](https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987): "the minimum and practical, schema-level traceability required for auditability in finance... allows a financial institution to reconstruct, explain, and defend every AI-driven decision when an auditor, regulator, or board member asks: 'How did this system arrive at that recommendation?'"

This is the project's load-bearing engineering decision. The minimum schema:

| Field | Format | Why required |
|---|---|---|
| `timestamp_UTC` | ISO 8601 | Temporal reconstruction; cross-jurisdiction time clarity |
| `audit_id` | UUID v4 | Unique immutable identifier; links backward to source, forward to outcomes |
| `user_id` | Anonymized ID with role | Segregation of duties; accountability |
| `model_name` + `model_version` | Exact spec | Rollback, reproducibility, drift identification |
| `prompt_version` | Versioned identifier | Prompt-side drift attribution |
| `tool_calls` | Array with per-call metadata | Action provenance |
| `sources_cited` | Array of {source_id, span, retrieval_score} | Claim grounding |
| `verdict` + `confidence` | Structured output | Output classification |

Every output produced by every agent in the system writes one record matching this schema. The audit log is the system's source of truth for "what happened when."

### The regulations that drive this

Three regulations frame the requirement in 2026:

- **SR 11-7 (Federal Reserve / OCC Model Risk Management)** — per [Fin.AI April 2026](https://fin.ai/learn/evaluate-ai-agent-compliance-financial-services): "AI models be subject to rigorous development documentation, independent validation, and ongoing monitoring. Your AI vendor should provide sufficient documentation of model architecture, training data provenance, and performance metrics."
- **NYDFS Part 500 (2023 amendments)** — per the same source: "the most operationally specific U.S. financial services regulation on AI governance, requiring risk assessments, access controls, and audit trails for any AI system processing customer data."
- **EU AI Act (effective August 2026)** — per [Lawrence Emenike December 2025](https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987): "requires institutions deploying high-risk AI systems to maintain... traceability documentation, including training data, testing protocols, and decision logs."

You're not building a regulated-deployment system in this project — you're building one that *demonstrates the architecture* that would satisfy these regulations. The audit trail is the demonstration.

## Milestones

Eight phases. Capstone-tier scope means each milestone takes ~4-6 hours.

### Milestone 1 — Pick the analyst archetype, scope the workload (3-4 hours)

Choose one financial analyst archetype to build for:

- **Equity research analyst** — reads 10-K / 10-Q filings, builds investment thesis, writes initiation-of-coverage or update notes
- **Credit analyst** — reads bond prospectuses, financial filings, credit reports; produces credit memos with rating recommendations
- **Earnings-call analyst** — reads transcripts + investor presentations; produces post-call summary notes with key takeaways

Define three concrete workflows for the chosen archetype:
- Workflow 1: a deep-dive on one company (e.g., "produce an initiation note on $TICKER")
- Workflow 2: a competitive comparison (e.g., "compare $A vs $B on profitability")
- Workflow 3: a thematic synthesis (e.g., "what are the three big themes from this quarter's tech earnings?")

**Done when**: archetype picked; three workflow descriptions written; you can manually walk through what a successful output looks like for each.

### Milestone 2 — SEC EDGAR integration (4-5 hours)

Build the SEC EDGAR data fetcher. The [EDGAR API](https://www.sec.gov/edgar/sec-api-documentation) gives free access to all public filings. Build:

- A retrieval interface (filing type + ticker + date range → filing text)
- Span-level provenance (every chunk of retrieved content carries source_id + page or section reference)
- Caching layer (filings don't change after submission; cache hits should be ~95%)

**Done when**: you can retrieve any 10-K filing from the last 5 years; every retrieved chunk has source span metadata; cached retrievals are fast.

### Milestone 3 — The three-agent topology (4-6 hours)

Implement the agent topology. Recommended starting shape: **plan-and-execute** with three specialists:

- **Research agent** — given a question, fetches relevant filings, extracts relevant sections, produces a research package with all sources cited
- **Analysis agent** — receives the research package, synthesizes the investment thesis or analytical conclusion, produces a structured output with claims-to-sources mapping
- **Compliance reviewer agent** — receives the analysis output, verifies every claim against its cited source, flags missing citations / contradictions / out-of-scope claims, produces a verdict (approved / needs_revision / rejected)

Handoff contracts (Path 03 v2 Pattern 1) between each pair are tight: only structured data crosses agent boundaries; raw chat history doesn't propagate.

**Done when**: a workflow runs end-to-end; the three agents communicate via structured handoffs; the compliance reviewer flags at least some issues (it should — drafts are imperfect).

### Milestone 4 — Provenance substrate (4-5 hours)

Implement Path 03 v2 Pattern 6 (Cross-agent provenance). Every output at every layer:

- Carries `source_ids` (which SEC filings it derived from)
- Carries `produced_by` (which agent / which version)
- Carries `derived_from` (which prior outputs it consumed)
- Has a `claim_grounding` map: every numerical claim points to a `source_id` + `span` + `retrieval_score`

The provenance layer is queryable: given a claim from a final report, you can retrieve the full chain back to the source filing.

**Done when**: pick 10 random claims from a generated report; for each, you can produce the full provenance chain in <5 seconds; the chain ends at a verifiable SEC filing span.

### Milestone 5 — Audit log layer (3-5 hours)

Implement the immutable audit log per the minimum schema above. Recommended storage: PostgreSQL with row-level append-only constraints, OR a managed trace backend (Langfuse / Braintrust) with retention policy set.

Every agent action writes one log entry. The log is queryable:

- "Show me every action by user X on date Y"
- "Show me every output that used prompt_version Z"
- "Show me every claim that cited source $TICKER 10-K"

**Done when**: ad-hoc queries return results in <2 seconds; the log preserves all minimum-schema fields; queries can answer the "how did this system arrive at that recommendation?" question end-to-end.

### Milestone 6 — Compliance reviewer agent + judge ensemble (5-7 hours)

Implement the compliance reviewer with judge-ensemble depth ([Path 06 Pattern 3](../../../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md)). Three calibrated judges with different scoping:

- **Citation-completeness judge** — every numerical claim has a citation; every citation resolves to a real source span
- **Contradiction-detection judge** — claims in the report don't contradict each other or contradict their cited sources
- **Scope-boundary judge** — claims stay within the analyst archetype's scope (no medical advice from a financial analyst; no legal advice from an equity analyst)

Disagreement structure:
- Unanimous pass → output approved for delivery
- Split verdict → flagged for human review; the audit log records the disagreement
- Unanimous fail → output rejected; the analysis agent receives feedback and regenerates

**Done when**: the judge ensemble is integrated; running the three example workflows produces approval/revision/rejection verdicts; inter-judge agreement is measurable.

### Milestone 7 — Run the three example workflows + deliberate-failure tests (4-6 hours)

Run the three example workflows end-to-end. Capture the audit logs + provenance chains + reviewer verdicts.

Then run deliberate-failure tests:

- **Test 1 — Source corruption**: deliberately give the research agent a stale 10-K (out-of-date). Verify the reviewer catches that the data is stale.
- **Test 2 — Contradiction injection**: deliberately have the analysis agent contradict its sources (e.g., source says revenue grew 10%, agent says it grew 15%). Verify the contradiction-detection judge catches it.
- **Test 3 — Out-of-scope drift**: deliberately have the analysis agent produce a recommendation that's out-of-scope (e.g., a stock-tip given a credit-analyst archetype). Verify the scope-boundary judge catches it.

Document each test's outcome.

**Done when**: three workflows produce delivered reports with full audit trails; three deliberate-failure tests produce expected reviewer interventions for at least 2 of 3.

### Milestone 8 — Polish, ADRs, write-up (3-5 hours)

The system works. Now:

- Write 5-7 ADRs covering the architecture decisions (topology / provenance schema / audit log storage / reviewer judges / source integration / human-in-the-loop or full-automation choice)
- Build a one-page dashboard: per-day request volume, per-judge verdict distribution, audit-log query examples, common reviewer-flagged issues
- Write `WRITEUP.md`
- Record a 2-3 minute screen recording showing one workflow end-to-end + the audit-log query interface

**Done when**: someone unfamiliar with the project can follow your write-up + dashboard and explain to a third person what the system does, how the audit trail works, and how they'd reproduce a specific finding from a delivered report.

## Evaluation criteria

The capstone-tier rubric — six dimensions, with regulated-domain specificity:

| Dimension | What it measures | Capstone-tier target |
|---|---|---|
| **Topology defense** | Is the three-agent topology genuinely necessary for the regulated-domain workload? | WRITEUP defends the three-agent choice against single-agent alternative; names specific failure modes a single agent would have |
| **Provenance completeness** | Does every claim in every output trace to a verifiable source? | 100% of numerical claims have provenance chains; manual spot-check of 20 claims confirms each chain resolves to an SEC filing span |
| **Audit log integrity** | Does the audit log capture the minimum schema for every agent action? | All schema fields present in every log entry; ad-hoc queries return correct results in <2 seconds |
| **Compliance reviewer rigor** | Are reviewer flags meaningful — catching real issues, not over-flagging benign content? | False-positive rate <20% on baseline good outputs; deliberate-failure tests pass for 2 of 3 |
| **Reproducibility** | Given a delivered report, can you reproduce the exact reasoning chain? | Pick any 3 reports; replay their audit log + provenance chain; verify the reasoning is reconstructable |
| **Cost per report** | What does a delivered report cost? | <$5.00 per delivered report at Sonnet pricing (research + analysis + 3 judges); <$1.00 at Haiku-class |

The six-dimension capstone-tier rubric. Each dimension separates capstone-tier from intermediate-tier. The reproducibility dimension is specific to regulated-domain work: a regulator-grade demonstration that any past decision can be reconstructed from the audit log alone.

## Stretch goals

Pick at most three.

- **Multi-source integration** — beyond SEC EDGAR, integrate one of: market data feed (Polygon, Alpha Vantage), news feed (NewsAPI, RSS), internal research repository. Demonstrates the cross-source provenance challenge.
- **Human-in-the-loop approval gate** — high-confidence outputs auto-publish; medium-confidence outputs go through the [`patterns/10-human-in-the-loop.md`](../../../patterns/10-human-in-the-loop.md) gate. Per [LangGraph April 2026](https://www.langchain.com/blog/runtime-behind-production-deep-agents): "pause for human approval... resumes from the exact point of interruption."
- **Regulatory mapping per claim** — beyond source attribution, every claim maps to the specific regulation it satisfies or relates to. The [Lawrence Emenike Dec 2025](https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987) framing extended: "Regulatory mapping: How this transaction satisfies compliance obligations."
- **Adversarial red-team testing** — per [FinVault arxiv:2601.07853](https://arxiv.org/pdf/2601.07853), execute systematic adversarial tests on the system's compliance posture. Promote findings into the regression set.
- **Multi-tenant scoping** — multiple analyst archetypes share the system with isolated audit logs per tenant. Production-readiness.
- **Versioned prompt registry** — every prompt is versioned; rollback is one query; A/B testing is supported. The [SR 11-7 framing](https://fin.ai/learn/evaluate-ai-agent-compliance-financial-services) extended to prompt artifacts.

## Anti-scope

What this capstone does NOT need to include:

- **Real regulated deployment** — you're demonstrating the architecture, not deploying to a regulated environment. SOC 2 / PCI-DSS / FedRAMP compliance is out of scope.
- **Custom fine-tuned models** — frontier models off the shelf are the target
- **Real-time market data with sub-second latency** — daily-cadence SEC filings are the assumed data source
- **Investment advice or recommendations to real users** — the system produces research artifacts; it does not give recommendations to anyone outside your testing
- **Multi-region failover or high availability** — local + a small hosted demo is fine
- **Encryption at rest with key management** — note the requirement in the WRITEUP; full KMS implementation belongs in a real deployment

If you find yourself building any of the above, you're crossing from "demonstration of architecture" to "production regulated system" — which is a much larger scope than capstone tier.

## Resources

**Architecture references**:
- [Fin.AI (April 2026), AI Agent Compliance for Financial Services 2026](https://fin.ai/learn/evaluate-ai-agent-compliance-financial-services) — SR 11-7, NYDFS Part 500, sector-specific regulations
- [DEV Community (April 2026), AI Agent Audit Trail: What Compliance Actually Requires in 2026](https://dev.to/waxell/your-ai-agents-and-the-audit-trail-what-compliance-actually-needs-33i5) — FINRA, SEC, state-level AI regulations; common audit-trail gaps
- [Lawrence Emenike (December 2025), Audit Trails and Explainability for Compliance](https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987) — the minimum audit-trail schema this project implements
- [FinregE (December 2025), How to safely use LLMs in financial services](https://finreg-e.com/how-to-safely-use-llms-in-financial-services/) — the review/validation/approval workflow pattern
- [arxiv:2508.00828, Finance Agent Benchmark](https://arxiv.org/pdf/2508.00828) — SEC EDGAR as verifiable ground truth; LLM-as-judge with rubric-based assessment
- [arxiv:2601.07853, FinVault](https://arxiv.org/pdf/2601.07853) — execution-grounded financial agent safety benchmark; multi-step risk characterization
- [arxiv:2509.10546, LLM Risk Concealment](https://arxiv.org/pdf/2509.10546) — implicit regulatory non-compliance failure mode in financial LLMs

**Tool / data documentation**:
- [SEC EDGAR API documentation](https://www.sec.gov/edgar/sec-api-documentation) — free access to all public filings; primary data source
- [Polygon.io](https://polygon.io/) — market data API (free tier); stretch-goal addition
- [NewsAPI](https://newsapi.org/) — news feed API (free tier); stretch-goal addition

**Repo cross-references — load-bearing**:
- [Path 03 v2 Pattern 6 (Cross-agent provenance)](../../../learning-paths/03-multi-agent-systems/patterns/) — the operational substrate this capstone makes load-bearing
- [Path 06 v1 Modules 1-3](../../../learning-paths/06-evaluation-observability/) — tracing fundamentals for the audit log layer
- [Path 06 Pattern 3 (Judge ensemble)](../../../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md) — the compliance reviewer implementation pattern
- [Project 07 — Evaluated multi-agent system](../07-evaluated-multi-agent-system/) — the eval/observability capstone; this project shares the multi-agent topology but emphasizes provenance instead of judge-ensemble depth

**Repo cross-references — supporting**:
- [Path 04 — Tool Protocols (MCP + A2A)](../../../learning-paths/04-tool-protocols-mcp-a2a/) — for the MCP-based source integration
- [`patterns/10-human-in-the-loop.md`](../../../patterns/10-human-in-the-loop.md) — for the HITL stretch goal
- [`security/safety-policy.md`](../../../security/safety-policy.md) — relevant if you add the adversarial red-team stretch goal

## Submission guide

When you're done, five artifacts go in your repo:

1. **The system code** — clean directory structure (agents/, provenance/, audit_log/, reviewer/, sources/, examples/, dashboards/); README explains setup, configuration, running locally
2. **A sample audit log** — JSON export of audit log entries for 10 representative agent actions; the reader can read the log structure without running the system
3. **Three example reports with full provenance chains** — `examples/report-XX/` each containing the request, the delivered report, the audit log, the provenance chain visualization
4. **The dashboard screenshot or recording** — one image or 2-3 minute screen recording demonstrating: the system delivering a report, the reviewer flagging an issue, and the audit log answering a regulator-style query
5. **`WRITEUP.md`** — a 2,000-3,000 word document covering:
   - The analyst archetype you chose and why
   - 5-7 ADRs covering the architecture decisions
   - The deliberate-failure test outcomes from Milestone 7
   - The audit-log schema implementation and how you ensured immutability
   - One thing that surprised you about regulated-domain engineering vs general agent work
   - What you'd do differently with 2× the time

Add yourself to `docs/community/showcase.md` when you submit. Capstone-tier regulated-domain submissions get highlighted in the project gallery and the README rotation; the audit-trail rigor makes them particularly valuable as community references.

## What this capstone leads to

After Financial Research Analyst, the natural progressions:

- **Project 07 (Evaluated multi-agent system)** — the eval/observability capstone; share the multi-agent topology with a different emphasis (judge ensembles + drift detection + regression promotion vs provenance + audit trails)
- **Project 08 (Production-ready deep research)** — adds long-running execution, durable checkpointing, HITL approval gates; the deployment-discipline capstone
- **Open-source contribution** — the audit-log + provenance schema you implement could be extracted as a small framework; several 2026 enterprise tooling startups began as exactly this kind of extraction
- **Path 07 production deployment** — if you want to take the system from "demonstration" to "real deployment," Path 07's production patterns + the regulated-domain constraints you've internalized are the path forward

This capstone is where Path 03 Pattern 6 stops being academic and becomes load-bearing. Finishing it means you've built one of the most-requested production patterns in 2026 enterprise AI: an agentic system that can survive an audit.
