# Safety policy authorship

> 🔴 Advanced · ⏱ ~26 min · 🛠 Verified 2026-05-29 · 📍 Read after [`security/prompt-injection.md`](./prompt-injection.md) and [`security/tool-abuse.md`](./tool-abuse.md); pairs with [`security/red-teaming.md`](./red-teaming.md) for the Path 06 v2 → Path 07 closure of the safety-evaluation surface

## What this page is for

[`security/prompt-injection.md`](./prompt-injection.md) and [`security/tool-abuse.md`](./tool-abuse.md) describe defenses — the technical mechanisms that catch attacks. This page describes the layer *above* defenses: the policy that specifies what the system should refuse, escalate, or allow in the first place. The two layers are coupled but distinct. A defense without a policy is enforcement without rules; a policy without defenses is rules without enforcement.

Path 06 v2's adversarial-red-teaming page explicitly deferred the policy-authoring work to Path 07. This page is the closure. The 2026 production reality per [DataVLab April 2026](https://datavlab.ai/post/red-teaming-llms-practitioner-guide-2026): "OWASP published its first agentic Top 10 in December 2025. The EU AI Act requires high-risk systems to meet compliance obligations by August 2026."

This page covers:

1. **The policy/defense distinction** — why these are separate concerns and how they compose
2. **Domain-specific harm taxonomies** — medical / legal / financial vertical patterns
3. **Refusal-criteria specifications** — the four-tier refusal taxonomy and the five response strategies
4. **The policy-to-implementation translation surface** — turning natural-language policy into runtime enforcement
5. **EU AI Act alignment** — how the policy maps to Annex III high-risk obligations
6. **Operational discipline** — sustaining policy quality over time

What this page does **not** cover is in section 7 (Anti-scope).

## The policy/defense distinction

Per the [Galileo April 2026 red-teaming strategies guide](https://galileo.ai/blog/llm-red-teaming-strategies): "OWASP's ASI 2026 framework targets agentic applications specifically. The EU AI Act mandates adversarial robustness testing by August 2026." Both target the same surface — what the agent should do, what it shouldn't, what falls in between — from different layers.

| Layer | What it answers | Owner | Output |
|---|---|---|---|
| **Policy** | What categories of behavior should we refuse / escalate / allow? Why? | Product + Legal + Safety | Natural-language specifications, audit-friendly |
| **Defense** | What technical mechanisms enforce the policy? | Engineering + Security | Code, configs, runtime checks |
| **Evaluation** | Does the system actually behave per policy? | Eval team (Path 06) | Test sets, metrics, regression dashboards |
| **Red-team** | What attacks would bypass the defenses against the policy? | Security + Red-team | Attack catalog, regression set |

A policy gap (the policy doesn't say what to do about X) produces inconsistent enforcement. A defense gap (the policy is clear but no defense enforces it) produces incidents. An evaluation gap (the defenses exist but no test confirms they work) produces silent regressions. All four layers are independent failure modes; this page covers the first.

The 2026 enforcement landscape is the forcing function. Per [Cloud Security Alliance March 2026](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-high-risk-compliance-deadline-20/): the EU AI Act's high-risk obligations under Annex III become enforceable on August 2, 2026 (subject to the still-unresolved Digital Omnibus deferral debate — the second trilogue ended without agreement on April 28, 2026, so the August 2026 date holds as written law). Article 9 requires a risk-management system; Article 26 requires deployer responsibilities including human oversight protocols and policy documentation. The policy artifacts this page describes are what those articles demand.

## Domain-specific harm taxonomies

The OWASP LLM01:2025 + ASI Top 10 frameworks describe attack *patterns*; harm taxonomies describe *outcomes*. A medical agent that gives incorrect medication advice is producing a different category of harm than a customer-support agent that leaks a refund policy — even if the underlying attack technique is identical. Per the [LLM Harms taxonomy paper (December 2025, arxiv:2512.05929)](https://arxiv.org/pdf/2512.05929): "LLM usage across healthcare, finance, education, and creative industries has been drastic... real-world incident repositories like the AI Incident Database (AIID) and MIT's AI Risk Repository have indexed over a thousand AI failure incidents by mid-2025."

The discipline: the policy is anchored to the *deployment context*, not to a generic taxonomy. Three vertical patterns illustrate the shape.

### Medical / healthcare

Hard refusal categories: diagnosing patients, prescribing medication, replacing professional medical advice. The agent never crosses these lines regardless of how the request is framed.

Escalation categories: symptom triage, medication interactions for an existing prescription, urgent symptom recognition. The agent provides information up to a defined boundary, then surfaces a "this needs a clinician" handoff.

Allowed categories: general health education, appointment scheduling, post-visit summarization (with the clinical content authored by the clinician).

The hard line: regulatory. FDA in the US treats certain clinical-decision-support functions as medical devices subject to 510(k) clearance; the policy has to be explicit about which side of that line the agent operates on. Per the [Legal Alignment for Safe and Ethical AI paper (January 2026)](https://aigi.ox.ac.uk/wp-content/uploads/2026/01/Kolt-Caputo-et-al.-2026-Legal-Alignment-for-Safe-and-Ethical-AI.pdf): "output filters and classifiers such as Llama Guard use hazard taxonomies that are grounded in legal categories." Medical policy maps to legal categories before it maps to model behavior.

### Legal / professional services

Hard refusal: providing specific legal advice, drafting binding legal documents that purport to come from a licensed practitioner, jurisdiction-specific guidance the agent isn't qualified to give.

Escalation: contract review (the agent summarizes; the lawyer signs off), case strategy (the agent organizes; the lawyer decides), document discovery (the agent surfaces candidates; the lawyer reviews).

Allowed: general information about the law, document templates clearly marked as starting points, legal research summarization with citations.

The hard line: unauthorized practice of law (UPL) statutes vary by jurisdiction. The policy has to track which jurisdictions the agent serves and which UPL standards apply. In the US, this is per-state. In the EU, this composes with the AI Act's Annex III high-risk classification for AI used in "administration of justice" contexts.

### Financial services

Hard refusal: tax/investment/insurance advice without a licensed human; account modifications above thresholds; transactions involving sanctioned counterparties.

Escalation: refund requests above per-tier limits ([`production/cost-engineering.md`](../production/cost-engineering.md) Layer 2 budgets parallel this), suspicious-activity flagging, AML triggers.

Allowed: account-status lookups, transaction history, general financial-product information.

The hard line: SEC, FINRA, and FCA regulations on what qualifies as advice; KYC/AML obligations; data-protection rules for financial data (PCI DSS for cards, GLBA for US consumer financial info). Financial policy has more pre-existing regulatory scaffold than medical or legal — the policy work is mostly mapping the agent's capabilities to existing categories.

### The cross-vertical pattern

Each vertical follows the same structure: hard refusal (regulatory red lines), escalation (the qualified-human handoff), allowed (general information). The vertical-specific work is identifying where each category's boundary sits — which is a domain-expert task, not an engineering task. The policy author's job is to make the boundaries explicit enough that the implementation layer can enforce them.

## Refusal-criteria specifications

The policy specifies *what* to refuse; the response strategy specifies *how* to refuse. Per [arxiv:2511.23174 (2025) on refusal taxonomy](https://arxiv.org/pdf/2511.23174), four refusal categories:

1. **Complete refusal** — the agent does not engage with the request at all ("I can't help with that")
2. **Partial refusal** — the agent acknowledges competing objectives and provides a constrained response ("I can't recommend a specific dosage, but I can describe general guidelines")
3. **No refusal** — the agent answers directly without engaging the safety surface
4. **Full compliance with redirection** — the agent provides what was requested while pointing to a more appropriate channel ("I can summarize this contract, and for binding decisions you'll want a licensed attorney")

Per the [LLM Guardrails contextual-effects study (arxiv:2506.00195)](https://arxiv.org/pdf/2506.00195), five response strategies in the production literature: direct refusal, explanation-based refusal, redirection, partial compliance, full compliance. The choice between them per category matters for user experience and for whether the policy actually holds up.

### The structured policy entry

For each refusal-worthy category, the policy specifies:

```yaml
category: medical_diagnosis
applies_when:
  - user requests interpretation of medical symptoms as a diagnosis
  - user requests prescription recommendations
  - user requests treatment plans
response_strategy: redirection_with_explanation
example_response: >
  I'm not able to diagnose medical conditions or recommend treatment.
  Based on what you've described, this sounds like something a clinician
  should look at. If symptoms are severe or worsening, contact urgent
  care or your primary provider. For non-urgent questions about
  symptoms in general, I can share information from authoritative
  medical sources.
escalation:
  - flag: medical_urgency_keywords_detected → escalate to crisis-line handoff
audit_required: true
review_cadence: quarterly
```

Six properties matter:

1. **`applies_when`** is enumerable, not vague. "Anything medical" produces inconsistent enforcement; specific trigger patterns produce consistent enforcement.
2. **`response_strategy`** is named, not freeform. The strategy determines tone and structure; the engineering side can verify it from the strategy alone.
3. **`example_response`** is the canonical reference. Eval tests measure against the example; deviation triggers flags.
4. **`escalation`** specifies the handoff conditions. Not every refusal is just "no" — some require redirecting to a different resource.
5. **`audit_required`** flags categories where every refusal event gets logged for review. High-stakes categories (medical, legal, financial harm) get audit; low-stakes categories don't.
6. **`review_cadence`** sets the maintenance interval. Static policies drift; quarterly review on high-stakes categories catches drift before it becomes a regulatory issue.

### The Inverse Risk Calibration problem

Per [arxiv:2602.01600 (February 2026) on Expected Harm](https://www.arxiv.org/pdf/2602.01600): "models disproportionately exhibit stronger refusal behaviors for low-likelihood (high-cost) threats while remaining vulnerable to high-likelihood (low-cost) queries." The pattern: a refusal policy that triggers aggressively on dramatic-sounding-but-rare requests while letting through routine-sounding-but-actually-harmful ones.

The mitigation in the policy is to weight refusal criteria by *expected harm* (severity × likelihood), not severity alone. A request to write a phishing email is high-likelihood low-cost (anyone can adapt it) — refuse. A request to describe historical atrocities for an essay is low-likelihood for harm but high-cost to refuse (frustrates legitimate research) — answer with context. The policy authorship work includes calibrating these weights for the deployment's actual risk profile, not the headline-grabbing one.

## The policy-to-implementation translation surface

A natural-language policy doesn't enforce itself. Three implementation layers translate policy into runtime behavior.

### Layer 1 — System-prompt encoding

The agent's system prompt encodes the refusal categories and response strategies as model instructions. Per the [Are LLMs Good Safety Agents paper (arxiv:2511.23174)](https://arxiv.org/pdf/2511.23174), this is the cheapest layer; it works for the majority of routine cases; it fails against motivated attackers per the prompt-injection literature ([`security/prompt-injection.md`](./prompt-injection.md)).

### Layer 2 — Classifier-based pre-filter and post-filter

A separate classifier (Llama Guard, AWS Bedrock Guardrails, Azure Content Safety, NeMo Guardrails) scores inputs and outputs against the policy's hard-refusal categories. Per the [Legal Alignment paper](https://aigi.ox.ac.uk/wp-content/uploads/2026/01/Kolt-Caputo-et-al.-2026-Legal-Alignment-for-Safe-and-Ethical-AI.pdf): "output filters and classifiers such as Llama Guard use hazard taxonomies that are grounded in legal categories, including the MLCommons benchmark that contains hazards relating to violent crime, defamation, and intellectual property." This catches Layer-1 failures for the categories the classifier is trained on; it adds latency (~50-200ms typical); it has false positives that need tuning.

### Layer 3 — Tool-boundary enforcement

For categories that involve *action* rather than just *content* (the agent shouldn't apply refunds over $50; the agent shouldn't write to admin tables; the agent shouldn't email external addresses), the policy enforcement is at the tool boundary per [`security/tool-abuse.md`](./tool-abuse.md). Schema validation, allow-lists, approval gates. This is the strongest layer because it's architecturally enforced, not stylistically enforced.

The three layers compose. A policy that only relies on Layer 1 (system prompt) fails to injection. A policy that only relies on Layer 2 (classifier) misses the action surface. A policy that only relies on Layer 3 (tool boundary) doesn't catch content-only harms (giving bad advice without taking any tool action). Each policy entry maps to at least one layer; high-stakes entries map to all three.

### The traceability requirement

Every policy entry has at least one corresponding evaluation test (Path 06 territory) and at least one corresponding red-team probe ([`security/red-teaming.md`](./red-teaming.md)). The mapping is the artifact that proves the policy is enforced:

| Policy entry | Defense layer | Evaluation test | Red-team probe |
|---|---|---|---|
| Refuse medical diagnosis | System prompt + Llama Guard | `test_refusal_medical_diagnosis.py` | `redteam_medical_jailbreak_v3.json` |
| Refund cap at $50 | Tool schema validation | `test_refund_above_50_blocked.py` | `redteam_refund_escalation.json` |
| Refuse legal advice (US, EU) | System prompt + classifier | `test_refusal_legal_advice.py` | `redteam_legal_jailbreak.json` |

This is the EU AI Act Article 9 + Article 17 + Article 26 mapping in concrete form — risk-management system (Article 9), quality-management system (Article 17), deployer obligations (Article 26). The Annex III audit asks for this table; the policy authorship work produces it.

## EU AI Act alignment

Per [Cloud Security Alliance March 2026](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-high-risk-compliance-deadline-20/), the August 2, 2026 enforcement of Annex III high-risk obligations brings five concrete demands the policy needs to satisfy:

1. **Risk-management system (Article 9)** — documented identification, analysis, evaluation, and mitigation of foreseeable risks. The policy's refusal-categories table feeds this.
2. **Data and data governance (Article 10)** — data used to train/develop the system has documented characteristics. Less direct for deployers using foundation models; matters more for providers.
3. **Technical documentation (Article 11)** — including the design specification, system architecture, and the validation procedures. The policy-to-implementation traceability table feeds this.
4. **Record-keeping (Article 12)** — automatic logging of events. The `audit_required: true` flag in policy entries determines what gets logged.
5. **Human oversight (Article 14)** — protocols enabling natural persons to oversee the system. The escalation categories in the policy specify the human-in-the-loop surface.

Plus Article 26 deployer obligations: monitor operation per documented use, suspend if serious incident, report to authorities. The policy is the spec the deployer monitors against.

The Digital Omnibus debate (proposing to defer to December 2027) does not change the policy work — even if the deadline shifts, the obligations themselves don't, and the policy is what an organization owns regardless of regulatory timing. Per [DLA Piper](https://knowledge.dlapiper.com/dlapiperknowledge/globalemploymentlatestdevelopments/2026/The-Digital-AI-Omnibus-Proposed-deferral-of-high-risk-AI-obligations-under-the-AI-Act): "If the Omnibus is not formally adopted before 2 August 2026, the original AI Act's provisions, including the high-risk obligations and their current timeline, will apply from that date as written. Organisations should continue preparing for compliance against the current 2 August 2026 deadline."

The policy authorship is also forward-compatible with NIST AI RMF (US, voluntary) and ISO 42001 (international AI management system standard, certifiable). The mapping work overlaps significantly — a policy structured per EU AI Act Articles 9-17 maps cleanly to NIST AI RMF's GOVERN/MAP/MEASURE/MANAGE functions and to ISO 42001's Annex A controls.

## Operational discipline

Five practices for sustained policy authorship:

1. **Policy entries reviewed quarterly per category**. High-stakes categories (medical, legal, financial harm) get full review. Lower-stakes categories rotate through the review cycle. Drift surfaces in the diff between successive reviews.
2. **Policy ownership clearly named per category**. A policy without a named owner is everyone's job and no one's job. Each entry has a Domain Lead (the subject-matter expert) and an Engineering Lead (who maintains the implementation).
3. **Policy-to-implementation traceability table as a living artifact**. Per the table above; PR review on tool changes or system-prompt changes checks the traceability. New tools that touch policy-relevant surfaces require a policy review before merge.
4. **Incident → policy update loop**. Every safety incident in production has a post-mortem that explicitly asks: did the policy cover this? If no, the policy gets an entry. If yes, the defense layer needs strengthening. The incident-driven update is what keeps the policy current.
5. **Red-team findings feed policy review**. Per [`security/red-teaming.md`](./red-teaming.md), red-team probes that find policy gaps (not just defense gaps) trigger policy review at the next quarterly cycle. The red-team is finding what the policy didn't anticipate.

## Anti-patterns

Three policy-authorship patterns that produce gaps:

### Policy written as a list of "don't" rules with no positive specification

A policy that says "don't give medical advice" without saying what the agent SHOULD do when asked produces inconsistent behavior. Different model versions interpret the gap differently; different deployments end up with different effective policies. The fix: every refusal category has a paired allowed/escalation specification that says what the agent *does* in the same situation.

### Policy that doesn't distinguish hard refusal from escalation from allowed

A flat "refuse anything risky" policy refuses too much (frustrating legitimate users — the Layer-2 false positives the [Galileo guide](https://galileo.ai/blog/llm-red-teaming-strategies) flags as a top operational concern) AND too little (missing the escalation tier where qualified-human handoff is the right answer). The three-tier structure (hard refusal / escalation / allowed) is the minimum granularity that produces useful enforcement.

### Policy authored once and not maintained

The threat landscape moves faster than any annual review cycle. New jailbreak techniques appear quarterly; new regulatory guidance appears every few months; new domain-specific risks surface from production. A policy that hasn't been updated in six months is one that's drifted from what the deployment actually needs. Quarterly review on high-stakes categories is the minimum cadence.

## Anti-scope (what this page does not cover)

- **Specific commercial guardrails products** (NeMo Guardrails, AWS Bedrock Guardrails, Azure AI Content Safety, Lakera, Protect AI, Guardrails AI). The implementation choice is downstream of policy. The (planned) `security/guardrails.md` page will cover specific products; this page is policy-only.
- **Constitutional AI training**, RLHF refusal-tuning, and other model-side safety methods. Path 09 (Safety & Alignment) territory; the policy authorship here is for application-layer enforcement on top of whatever model-side training is in place.
- **Jurisdiction-by-jurisdiction legal mapping**. The page describes the structural alignment with EU AI Act, NIST AI RMF, ISO 42001; specific obligation interpretation per US state, per EU member state, per non-EU jurisdiction is legal-counsel territory.
- **Bias and fairness specification**. Real but its own category — the harm taxonomies in this page cover hard-refusal categories; bias/fairness has its own taxonomy, audit methodology, and regulatory anchor (NIST AI RMF MEASURE.2, EU AI Act Article 10 + Article 15 + AILD considerations). Path 09 territory.
- **Privacy policy specifically**. GDPR, CCPA, and similar map to data-handling rules that compose with this page's content-and-action policy but are operationally separate. Path 08 (Privacy & Compliance) territory if it gets opened; otherwise enterprise-security playbooks cover it.
- **Public statement / marketing claims about safety**. Trust-and-safety communications work; outside engineering scope.

## References

**2026 AI policy and regulation**:
- [Cloud Security Alliance (March 2026), *EU AI Act High-Risk Deadline: Enterprise Readiness Gap*](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-high-risk-compliance-deadline-20/) — August 2, 2026 enforcement deadline; Articles 9-17 + Article 26; Digital Omnibus status
- [DLA Piper (April 2026), *Digital AI Omnibus: Proposed deferral of high risk AI obligations*](https://knowledge.dlapiper.com/dlapiperknowledge/globalemploymentlatestdevelopments/2026/The-Digital-AI-Omnibus-Proposed-deferral-of-high-risk-AI-obligations-under-the-AI-Act) — second trilogue April 28, 2026 ended without agreement; August 2026 still binding as written
- [Legiscope (May 2026), *EU AI Act Deadlines 2026-2027*](https://www.legiscope.com/blog/eu-ai-act-timeline-deadlines.html) — €35M / 7% turnover penalty schedule; full compliance calendar
- [Holland & Knight (April 2026), *U.S. Companies Face EU AI Act's August 2026 Deadline*](https://www.hklaw.com/en/insights/publications/2026/04/us-companies-face-eu-ai-acts-possible-august-2026-compliance-deadline) — extraterritorial reach; provider vs deployer distinction
- [Secure Privacy (April 2026), *EU AI Act 2026: Key Compliance Requirements*](https://secureprivacy.ai/blog/eu-ai-act-2026-compliance) — practical compliance translation
- [McKenna Consultants (February 2026), *EU AI Act High-Risk Compliance Technical Readiness Guide*](https://www.mckennaconsultants.com/eu-ai-act-high-risk-compliance-a-technical-readiness-guide-for-august-2026/) — Article-by-Article engineering translation

**Refusal taxonomy and policy literature (2025-2026)**:
- [arxiv:2602.01600 (February 2026), *Expected Harm: Rethinking Safety Evaluation of (Mis)Aligned LLMs*](https://www.arxiv.org/pdf/2602.01600) — Inverse Risk Calibration finding; severity × likelihood weighting
- [arxiv:2511.23174 (2025), *Are LLMs Good Safety Agents or a Propaganda Engine?*](https://arxiv.org/pdf/2511.23174) — four-tier refusal taxonomy (complete / partial / no / full compliance)
- [arxiv:2506.00195 (2026), *Let Them Down Easy! Contextual Effects of LLM Guardrails on User Perceptions*](https://arxiv.org/pdf/2506.00195) — five response strategies (direct refusal, explanation-based, redirection, partial compliance, full compliance)
- [arxiv:2605.16282 (April 2026), *Taxonomy and Consistency Analysis of Safety Benchmarks for AI Agents*](https://arxiv.org/html/2605.16282v1) — agent-internal vs multi-agent vs environmental injection threat axes
- [arxiv:2512.05929 (December 2025), *LLM Harms: A Taxonomy and Discussion*](https://arxiv.org/pdf/2512.05929) — AIID + MIT AI Risk Repository as taxonomy sources

**Legal grounding for policy**:
- [Legal Alignment for Safe and Ethical AI (Oxford AIGI, January 2026)](https://aigi.ox.ac.uk/wp-content/uploads/2026/01/Kolt-Caputo-et-al.-2026-Legal-Alignment-for-Safe-and-Ethical-AI.pdf) — hazard taxonomies grounded in legal categories; Llama Guard + MLCommons

**Repo cross-references**:
- [`security/prompt-injection.md`](./prompt-injection.md) — the defense layer Layer 1 (system-prompt encoding) builds on
- [`security/tool-abuse.md`](./tool-abuse.md) — the defense layer Layer 3 (tool-boundary enforcement) builds on
- [`security/red-teaming.md`](./red-teaming.md) — the pre-launch red-team pass that probes whether the policy is enforced; produces the regression set that feeds policy review
- [`production/checklist.md`](../production/checklist.md) — Layer 8 (Policy compliance) of the pre-launch checklist consumes this page's traceability table
- [`production/cost-engineering.md`](../production/cost-engineering.md) — financial-vertical policy boundaries (refund caps) parallel the per-agent cost budgets
- [Path 06 v2 — Adversarial red-teaming at scale](../concepts/evaluation/adversarial-red-teaming-at-scale.md) — the upstream eval surface; this page is the "what to evaluate against" the upstream "how to evaluate"
- [Pattern 10 (Human-in-the-loop)](../patterns/10-human-in-the-loop.md) — the escalation tier's architectural pattern
- [Path 03 Pattern 3 (Escalation and fallback)](../learning-paths/03-multi-agent-systems/patterns/03-escalation-and-fallback.md) — escalation-tier topology
