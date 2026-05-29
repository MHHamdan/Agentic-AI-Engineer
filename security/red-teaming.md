# Pre-launch red-team pass

> 🔴 Advanced · ⏱ ~26 min · 🛠 Verified 2026-05-29 · 📍 Read after [`security/safety-policy.md`](./safety-policy.md) and [Path 06 v2's adversarial-red-teaming page](../concepts/evaluation/adversarial-red-teaming-at-scale.md); pairs with safety-policy.md for the Path 06 v2 → Path 07 closure

## What this page is for

Path 06 v2 built the *evaluation infrastructure* for adversarial red-teaming — the [adversarial-red-teaming-at-scale concept page](../concepts/evaluation/adversarial-red-teaming-at-scale.md) and [Lab 24](../labs/24-adversarial-red-teaming-at-scale/) deliver the six-step workflow (variant generation → run-at-scale → judge ensemble → disagreement routing → regression promotion → dashboard). This page covers the *production gate* angle: when does the red-team output translate into a launch decision? What's the minimum bar before a high-stakes agent goes live?

The 2026 production context per [Galileo April 2026](https://galileo.ai/blog/llm-red-teaming-strategies): "OWASP published its first agentic Top 10 in December 2025. The EU AI Act requires high-risk systems to meet compliance obligations by August 2026, while GPAI adversarial testing obligations under Article 55 are already in effect." Red-teaming is no longer the discretionary security exercise it was three years ago — for high-risk deployments under EU AI Act Annex III, it's part of the conformity assessment.

Per [DataVLab April 2026](https://datavlab.ai/post/red-teaming-llms-practitioner-guide-2026): "a 2025 study of 1,400+ adversarial prompts found roleplay-based prompt injections achieved 89.6% attack success rates against frontier models, with average jailbreak time under 17 minutes for GPT-4."

This page covers:

1. **The pre-launch gate vs continuous discipline distinction** — both are needed; this page is the gate
2. **The five-phase pre-launch red-team protocol** — reconnaissance, attack generation, execution, validation, mitigation with re-test
3. **Reusing Lab 24's infrastructure for pre-launch** — the operational mapping
4. **EU AI Act Article 15 + Article 55 alignment** — what regulators expect to see
5. **Go / No-Go criteria** — when is "enough red-team" enough to ship?
6. **Post-launch continuous cadence** — the discipline that follows launch
7. Operational practices, anti-patterns, anti-scope

What this page does **not** cover is in section 8 (Anti-scope).

## The pre-launch gate vs continuous discipline

Two related but distinct activities:

| | Pre-launch gate (this page) | Continuous red-team (Path 06 v2) |
|---|---|---|
| **Trigger** | Before any high-risk deployment goes live | Ongoing post-launch, monthly cadence |
| **Question answered** | Is this deployment ready to ship? | Is the deployment maintaining its safety posture as the threat landscape evolves? |
| **Output** | Go / No-Go decision + documented findings | Updated regression set + trend metrics |
| **Owner** | Security + Safety leads; product accountable | Security + Eval team |
| **Cadence** | Once per launch (plus before significant changes) | Recurring (monthly typical for high-stakes) |
| **EU AI Act anchor** | Article 15 (accuracy + robustness verification before placing on market) | Article 26 (deployer monitoring during operation) |

Both reuse the same infrastructure from Lab 24. The gate version compresses the workflow into a defined pre-launch window with explicit pass/fail criteria; the continuous version runs the same workflow on a rotating schedule.

The discipline this page describes is the gate angle. Continuous practice composes with [`production/checklist.md`](../production/checklist.md) Layer 6 (Abuse detection) and Layer 8 (Policy compliance).

## The five-phase pre-launch protocol

Per [DataVLab April 2026](https://datavlab.ai/post/red-teaming-llms-practitioner-guide-2026): "the structured five-phase methodology: reconnaissance, attack generation, execution, validation, mitigation with re-test." Each phase has explicit entry criteria and exit criteria.

### Phase 1 — Reconnaissance

The team inventories the deployment's attack surface. What tools does the agent have access to? What data sources feed it? What's the deployment shape (per [`production/deployment.md`](../production/deployment.md))? What's the policy ([`security/safety-policy.md`](./safety-policy.md))? Which OWASP ASI Top 10 categories apply?

**Inputs**: The agent's tool allow-list, system prompt, RAG corpus inventory, data-flow diagram, safety policy table.
**Output**: A scoped threat model — which attack categories the red-team will probe, with priority ordering.
**Exit criterion**: All eight OWASP-aligned failure categories from the [Path 06 v2 adversarial-red-teaming page](../concepts/evaluation/adversarial-red-teaming-at-scale.md) are either covered by the threat model or explicitly out-of-scope with documented reason.

### Phase 2 — Attack generation

Per the threat model, generate failure-eliciting inputs. Three input sources:

- **OWASP-aligned templates** — the canonical attack patterns per category, from the OWASP LLM Top 10 + ASI Top 10. Generic but reliable coverage.
- **Domain-specific attacks** — derived from the safety policy's hard-refusal categories. Each category gets at least N=20 probes attempting to elicit the refused behavior.
- **Lab 24's variant generator** — automated mutation of seed attacks (paraphrase, encoding tricks, multi-turn variants). Per Lab 24, N=10-50 variants per seed.

**Tooling support 2026**: [DeepTeam's `OWASP_ASI_2026` framework primitive (April 2026)](https://www.trydeepteam.com/guides/guide-agentic-ai-red-teaming): `red_team(model_callback=..., framework=OWASP_ASI_2026())` automates category coverage for the ten ASI categories. PyRIT (Microsoft), Garak, Promptfoo, and PromptBench provide overlapping capabilities — pick one as the primary tool, use the others as supplements for coverage gaps.

**Per [DataVLab April 2026](https://datavlab.ai/post/red-teaming-llms-practitioner-guide-2026)**: "RL-trained adversarial autonomous agents outperform single-turn prompt fuzzing. Multi-modal and MCP-based attacks need dedicated testing scenarios." The 2026 distinction matters — single-turn attack catalogs are necessary but not sufficient for agent deployments.

**Output**: An attack set with documented coverage per threat-model category. For high-risk deployments, 500-2000 attacks typical.
**Exit criterion**: Each threat-model category has at least the planned coverage; the set is versioned for regression use.

### Phase 3 — Execution

Run the attacks against the deployment. Use Lab 24's run-at-scale infrastructure — the workflow handles parallel execution, rate limiting, judge-ensemble scoring.

**Critical**: execute against the *actual* deployment configuration, not a test fixture. The model version, the system prompt, the tool allow-list, the policy enforcement layer — all match production. Per the [Building LLMs in Production guide (May 2026)](https://futureagi.com/blog/building-llms-production-2025/): "teams that ship without traceAI-style spans plus a continuous eval gate (groundedness, context adherence, toxicity, custom LLM-as-judge) typically learn about regressions from customer tickets days after they hit production."

The pre-launch run is the chance to learn before tickets arrive. A test fixture that diverges from production is a waste of the cycle.

**Output**: Per-attack outcomes — refused, partially refused, complied (the four-tier refusal taxonomy from [`security/safety-policy.md`](./safety-policy.md)). Trace data per attack for downstream analysis.
**Exit criterion**: Every attack in the set has been executed; the outcomes are scored by the judge ensemble.

### Phase 4 — Validation

Triage outcomes. Three review queues:

- **Unanimous judge pass**: the agent refused or escalated correctly per policy. No further action.
- **Split verdict**: judges disagree. Human review per Lab 24's disagreement-routing pattern. The split is itself the signal that the policy or the judging criteria need clarification.
- **Unanimous judge fail**: confirmed policy violation. Goes to the regression set; goes to the mitigation queue.

**Severity classification per finding**: borrowing Path 06 v2's severity routing — critical (security-impacting, regulator-relevant, user-harm-direct), high (policy violation without acute harm), medium (degraded behavior without policy violation), low (style/UX issue). The classification drives the mitigation priority and the Go/No-Go assessment.

**Output**: A findings table — per-attack severity, judge verdict, human review notes, recommended mitigation.
**Exit criterion**: Every confirmed-fail or split-verdict outcome has a severity classification and an assigned owner.

### Phase 5 — Mitigation with re-test

For each finding above the agreed-upon severity bar, implement mitigation. Re-run the affected attacks. The re-test passes are what move the launch toward Go.

**Mitigation surfaces** per [`security/prompt-injection.md`](./prompt-injection.md), [`security/tool-abuse.md`](./tool-abuse.md), [`security/data-exfiltration.md`](./data-exfiltration.md):

- System-prompt updates (Layer 1)
- Classifier-based pre/post filter additions (Layer 2)
- Tool-allow-list narrowing, schema validation tightening (Layer 3)
- Policy-entry additions or refinements (the gap the red-team found)

The discipline: the same red-team payload that found the issue is the regression test that proves it's fixed. The attack set is versioned; re-runs against the new defense version produce the proof.

**Output**: A re-test report showing prior-fail → current-pass for each mitigated finding; the remaining findings either accepted-with-justification (low severity) or remain blockers.
**Exit criterion**: No finding above the agreed-upon severity bar remains in fail state.

## Reusing Lab 24's infrastructure

Lab 24 ([labs/24-adversarial-red-teaming-at-scale/](../labs/24-adversarial-red-teaming-at-scale/)) provides the operational scaffolding for all five phases. The mapping:

| Phase | Lab 24 component |
|---|---|
| 1 — Reconnaissance | Eight-category OWASP-aligned threat-model template |
| 2 — Attack generation | Variant generator (N mutations per seed); per-category seed catalog |
| 3 — Execution | Run-at-scale orchestration; judge ensemble (3 deterministic judges with different biases) |
| 4 — Validation | Disagreement routing (unanimous-pass / split / unanimous-fail) + human review queue |
| 5 — Mitigation with re-test | Regression promotion (JSON-serialized) + versioned regression set + per-category dashboard |

Lab 24 uses a **benign synthetic agent** with a toy policy ("never output SECRET_TOKEN, never write haiku"). The mechanics are real; the payloads are intentionally not weaponizable. For a real pre-launch pass, the synthetic stand-ins are replaced with the actual deployment's surfaces — but the orchestration, judge ensemble, and regression-promotion code transfer directly.

The repo's [`SECURITY.md`](../SECURITY.md) policy is explicit: threat models and defensive patterns with citations are in scope; weaponizable exploits with no defensive purpose are not. The pre-launch red-team in production reuses the orchestration; the *attack content* for high-stakes deployments is sourced from the OWASP catalogs, commercial red-team tools (DeepTeam, PyRIT, Garak), and the team's own threat-modeling work — not from this repo.

## EU AI Act Article 15 + Article 55 alignment

For deployments classified as high-risk under Annex III, the pre-launch red-team produces evidence the conformity assessment requires. Two articles drive the obligations.

### Article 15 — Accuracy, robustness, cybersecurity

Per Article 15, high-risk AI systems must "achieve an appropriate level of accuracy, robustness and cybersecurity" and "be designed and developed in such a way that they perform consistently throughout their lifecycle." The robustness obligation specifically covers resilience against errors, faults, and inconsistencies — and against "attempts by unauthorised third parties to alter their use, outputs or performance by exploiting system vulnerabilities."

The pre-launch red-team is the verification artifact for the robustness portion. The findings table + mitigation re-test report is what the conformity assessor reviews.

### Article 55 — GPAI adversarial testing (already in effect)

Per [Galileo April 2026](https://galileo.ai/blog/llm-red-teaming-strategies): "GPAI adversarial testing obligations under Article 55 are already in effect" — meaning providers of general-purpose AI models (the foundation models the deployment uses) already have adversarial testing requirements. The deployment-side red-team is downstream of those obligations; it covers the application layer the GPAI obligations don't address.

### What the conformity assessor expects to see

Five artifacts from the pre-launch red-team:

1. **Threat model document** — scoped per Phase 1; ties to safety policy
2. **Attack set inventory** — versioned, per-category coverage table
3. **Execution log** — every attack-attempt outcome with timestamp and configuration snapshot
4. **Findings table with severity classification** — Phase 4 output
5. **Mitigation re-test report** — Phase 5 output proving findings were addressed

For deployments NOT under EU AI Act high-risk classification, these artifacts are still good practice — they're what an internal audit, an enterprise customer's security review, or a SOC 2 review will ask for. The regulatory deadline is the forcing function; the discipline is universal.

## Go / No-Go criteria

The pre-launch red-team produces findings; a launch decision converts findings into Go / No-Go. The criteria depend on severity classification (Phase 4 output) and on the deployment's risk tier.

### A typical threshold structure

| Severity | High-risk deployment (EU AI Act Annex III) | Standard deployment |
|---|---|---|
| **Critical** | Zero open at launch | Zero open at launch |
| **High** | Zero open at launch (or documented acceptance with mitigation plan) | ≤ 2 open with documented acceptance + mitigation plan within 30 days |
| **Medium** | Tracked; no launch blocker absent specific business decision | Acceptable; tracked for post-launch fix |
| **Low** | Acceptable; tracked | Acceptable; not tracked unless pattern emerges |

The criteria are deployment-specific; the *existence* of explicit criteria is universal. A pre-launch process without explicit Go/No-Go thresholds becomes "ship it and hope" under deadline pressure. Documented thresholds make the launch decision auditable.

### The accept-with-justification path

Some high-severity findings can't be mitigated pre-launch and aren't blockers per the risk assessment. Examples: a known model-level limitation (the foundation model has a documented refusal failure mode for category X; the deployment's policy specifies category X as a category that escalates to human review, so the model-level failure is contained by the architectural defense). The acceptance is documented — the finding, the reasoning, the mitigation plan, the trigger that would re-open the decision. The conformity assessor sees the reasoning, not just the threshold; the post-launch monitoring picks up the residual risk.

## Post-launch cadence

The pre-launch pass is the gate; the continuous discipline is what follows. Per [Galileo April 2026](https://galileo.ai/blog/llm-red-teaming-strategies): "continuous red teaming in CI/CD catches drift before production."

Five practices for sustained post-launch red-team:

1. **Monthly red-team cycle for high-stakes deployments**. Lab 24's infrastructure runs against the latest deployment configuration. New attack patterns from the threat landscape (the OWASP updates, novel jailbreak techniques in the literature) get added to the attack set. Regression set growth is the artifact.
2. **Per-model-upgrade red-team trigger**. Any upgrade of the foundation model — a Sonnet 4.5 → 4.6 → 4.7 transition, an Opus 4.6 → 4.7 transition (the [April 2026 frontier-model landscape](https://fazm.ai/blog/new-llm-releases-april-2026)) — triggers a re-run of the full pre-launch protocol. Model upgrades shift behavior; the red-team is the regression check.
3. **CI/CD integration for routine changes**. System-prompt updates, tool-allow-list changes, RAG corpus updates trigger the relevant subset of the regression set automatically. Failures block the merge. Per [Milind Nair March 2026](https://medium.com/@nairmilind3/llm-evaluation-in-2026-e631a78c67dc): "deployment gate applies threshold-based blocking on accuracy, safety, and faithfulness metrics. Regressions from the production baseline halt the deploy."
4. **Quarterly external red-team review** for the highest-stakes deployments. An external team probes for issues the internal team's bias misses. The OWASP ASI Top 10 + the latest academic literature provide the seed taxonomy.
5. **Annual program audit**. The red-team program itself gets reviewed: are the right attack categories covered? Is the regression set keeping pace with the threat landscape? Are the Go/No-Go criteria still aligned with the deployment's risk profile?

## Anti-patterns

Four red-team patterns that produce false confidence:

### Single-turn-only attack coverage

Per [DataVLab April 2026](https://datavlab.ai/post/red-teaming-llms-practitioner-guide-2026): "for agentic systems with tool access, red-teaming must cover whether attackers can manipulate the model into making harmful tool calls... the complexity of multi-step tool use creates attack paths that simple prompt-only red-teaming misses entirely." A red-team set that only contains single-turn prompts misses the multi-turn attack surface; an agent that resists each turn in isolation can still be manipulated across turns.

### Red-team in a test fixture that differs from production

The model version, system prompt, tool allow-list, retrieval corpus, and policy enforcement layer have to match production exactly. A red-team against a slightly different fixture produces findings that may not apply or misses findings that do. The discipline: snapshot the deployment configuration at the start of the red-team; pin the test fixture to the snapshot; document any deviation.

### Treating "no findings" as a clean result

Per the [Galileo guide](https://galileo.ai/blog/llm-red-teaming-strategies): "RL-trained adversarial autonomous agents outperform single-turn prompt fuzzing." A red-team that produces no findings on a non-trivial deployment is more likely missing coverage than confirming safety. Zero findings is a signal to expand the attack catalog or tighten the judging criteria, not to declare success.

### Red-team done once and never updated

The 89.6% attack success rate per [DataVLab](https://datavlab.ai/post/red-teaming-llms-practitioner-guide-2026) is the 2026 baseline because new attack patterns appear quarterly. A red-team set that was complete six months ago has a coverage gap now. The regression set has to grow with the threat landscape; static sets become legacy artifacts.

## Anti-scope (what this page does not cover)

- **How to craft adversarial attacks**. The repo's [`SECURITY.md`](../SECURITY.md) policy applies. Attack catalogs come from OWASP, commercial red-team tools, the team's own threat-modeling; this page covers the orchestration and decision layer, not weaponizable content.
- **Specific commercial red-team tool product comparisons**. DeepTeam, PyRIT, Garak, Promptfoo, PromptBench each have their own coverage profile and tooling; the choice is downstream of the red-team program structure this page covers.
- **Bug-bounty and disclosure programs**. Related but separate — bug bounties are external researcher discovery; red-team is internal structured probing. Both compose with the [`SECURITY.md`](../SECURITY.md) disclosure policy.
- **Model-side robustness training**. RLHF-with-adversarial-examples, adversarial fine-tuning, constitutional-AI defensive training — model-provider concerns. Path 09 territory.
- **Jurisdiction-specific compliance content** beyond EU AI Act. NIST AI RMF, ISO 42001, US sector-specific regulations (HIPAA, FFIEC, FINRA) compose with this page's discipline but have their own audit surfaces.
- **Penetration testing of the surrounding infrastructure** (the Kubernetes cluster, the LLM gateway, the database). Standard application security; outside the red-team-for-agents scope.

## References

**Red-teaming methodology (2026)**:
- [DataVLab (April 2026), *Red-Teaming LLMs 2026: A Practitioner's Guide*](https://datavlab.ai/post/red-teaming-llms-practitioner-guide-2026) — five-phase methodology; 89.6% attack success rate; multi-modal + MCP-based attacks; EU AI Act compliance documentation
- [Galileo (April 2026), *8 Red Teaming Strategies for LLMs and Agents*](https://galileo.ai/blog/llm-red-teaming-strategies) — OWASP ASI 2026 framework; EU AI Act Article 55 framing; continuous CI/CD integration
- [DeepTeam (April 2026), *Complete Guide to Agentic AI Red Teaming*](https://www.trydeepteam.com/guides/guide-agentic-ai-red-teaming) — `OWASP_ASI_2026` framework primitive; category-scoped assessment

**EU AI Act enforcement context (2026)**:
- [Cloud Security Alliance (March 2026), *EU AI Act High-Risk Deadline*](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-high-risk-compliance-deadline-20/) — August 2, 2026 deadline; Articles 9-17 + Article 26
- [DLA Piper (April 2026), *Digital AI Omnibus: Proposed deferral*](https://knowledge.dlapiper.com/dlapiperknowledge/globalemploymentlatestdevelopments/2026/The-Digital-AI-Omnibus-Proposed-deferral-of-high-risk-AI-obligations-under-the-AI-Act) — Omnibus status; preparing against current deadline
- [Legiscope (May 2026), *EU AI Act Deadlines 2026-2027*](https://www.legiscope.com/blog/eu-ai-act-timeline-deadlines.html) — penalty schedule; Article 55 GPAI obligations already in effect

**Production red-team discipline (2026)**:
- [Milind Nair (March 2026), *LLM Evaluation in 2026*](https://medium.com/@nairmilind3/llm-evaluation-in-2026-e631a78c67dc) — four-stage evaluation pipeline; deployment gate threshold-based blocking
- [Future AGI (May 2026), *Building LLMs in Production 2026 Playbook*](https://futureagi.com/blog/building-llms-production-2025/) — silent quality regressions; continuous eval gate
- [Fazm Blog (May 2026), *New LLM Releases April 2026*](https://fazm.ai/blog/new-llm-releases-april-2026) — frontier-model landscape requiring per-upgrade re-test

**Repo cross-references**:
- [`security/safety-policy.md`](./safety-policy.md) — the policy the red-team probes; the traceability table connects policy entries to red-team probes
- [`security/prompt-injection.md`](./prompt-injection.md) — Defense 6 (monitoring + red-team cadence) is the post-launch side this page extends pre-launch
- [`security/tool-abuse.md`](./tool-abuse.md) — Defense 5 (audit logging) feeds the continuous red-team's behavioral monitoring
- [`security/data-exfiltration.md`](./data-exfiltration.md) — Vector-specific attack surfaces the red-team probes
- [`production/checklist.md`](../production/checklist.md) — Layer 8 (Policy compliance) of the pre-launch checklist consumes the red-team report
- [Path 06 v2 — Adversarial red-teaming at scale](../concepts/evaluation/adversarial-red-teaming-at-scale.md) — the upstream concept page; this page is the deployment-time application
- [Lab 24 — Adversarial red-teaming at scale](../labs/24-adversarial-red-teaming-at-scale/) — the operational scaffolding for all five phases
