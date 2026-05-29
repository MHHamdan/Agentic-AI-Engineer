# Project 3 — A2A-federated multi-agent

> 🔴 Advanced · ⏱ ~50 min reading · 🛠 ~7-10 day build · Verified 2026-05-29

## Project brief

You're building a cross-organization multi-agent system: your supervisor agent dispatches work to specialist agents that live in *different organizations* (or different teams/frameworks/clouds within your org), communicating over [A2A protocol](https://github.com/google-a2a/A2A) with MCP for each agent's tool surface. The deployment shape is the [Pattern 12 (A2A federation)](../../../patterns/12-a2a-federation.md) production target, with the actual identity, attestation, and cross-org authorization story shipped correctly — not deferred.

The use case grounds the project: your supervisor is a procurement-orchestration agent in Org A; it needs to query an inventory specialist in Org B, an approvals specialist in Org C (a vendor compliance service), and a payments specialist in Org D (a financial-services partner using AP2 per the [April 2026 Linux Foundation A2A milestone](https://www.prnewswire.com/news-releases/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year-302737641.html)). The pattern is the same for any 3-4 organization workflow — invoicing, supply chain, claim processing, partner onboarding.

**Deployment target**: FastAPI service exposing A2A endpoints (agent card + task lifecycle methods) deployed via your team's container platform. Per-agent MCP servers for the tool surface. OAuth 2.1 with the agent-card-bound JWS signatures landing in the wire format. PostgreSQL for task state; Redis for cross-agent task-id correlation.

**Scale assumption**: 1K-100K cross-org tasks/month, 1-3 person team per org, 3-4 federated agents total. If you're below 1K/month, the operational complexity isn't worth it; build the same logic single-process. If you're above 100K and latency-sensitive (sub-second p95), the per-task cross-org round trips become the bottleneck — consider co-locating frequently-coupled specialists.

This project composes [Pattern 11 (MCP integration)](../../../patterns/11-mcp-integration.md) + [Pattern 12 (A2A federation)](../../../patterns/12-a2a-federation.md) + [Pattern 03 (Supervisor + workers)](../../../patterns/03-supervisor-workers.md) + Path 03 v2 patterns 01 (handoff contracts), 06 (cross-agent provenance). It's the most advanced of the three Path 03 projects — pick it when your deployment crosses organizational boundaries and the value of doing it correctly (with real identity + provenance) is worth the engineering investment.

## Prerequisites

Before starting, you should have completed:

- **Required Path 04 modules**: All seven Path 04 modules end-to-end — [Modules 1-3 (MCP build/consume/secure)](../../04-tool-protocols-mcp-a2a/), [Module 4-5 (A2A foundations + production depth)](../../04-tool-protocols-mcp-a2a/), Module 7 (MCP+A2A composition). Project 3 is the production-deployment shape of Module 7. **If Path 04 isn't done, do that first**; this project is not a substitute.
- **Required Path 04 labs**: [Lab 25 (MCP server from scratch)](../../../labs/25-mcp-server-from-scratch/), [Lab 26 (MCP client from scratch)](../../../labs/26-mcp-client-from-scratch/), [Lab 29 (A2A production depth)](../../../labs/29-a2a-endpoint-production-depth/), [Lab 30 (MCP+A2A composition)](../../../labs/30-mcp-a2a-composition/).
- **Required Path 03 v1 labs**: [Lab 10 (Supervisor-worker)](../../../labs/10-supervisor-worker-from-scratch/) — the supervisor pattern doesn't change because we're crossing orgs; only the transport does.
- **Required Path 03 v2 patterns**: [Pattern 01 (Handoff contracts)](../patterns/01-handoff-contracts.md) — the envelope discipline matters more cross-org than in-process; [Pattern 06 (Cross-agent provenance)](../patterns/06-cross-agent-provenance.md) — cross-org provenance is a compliance requirement, not just an operational one.
- **Required top-level patterns**: [Pattern 11 (MCP)](../../../patterns/11-mcp-integration.md), [Pattern 12 (A2A federation)](../../../patterns/12-a2a-federation.md), [Pattern 03 (Supervisor + workers)](../../../patterns/03-supervisor-workers.md) read end-to-end.
- **External**: 3-4 distinct deployment targets (one per agent — different orgs, different clouds, or different teams within your org); a way to set up OAuth 2.1 + JWS-RS256 (Okta, Auth0, Keycloak, or AWS Cognito work); A2A SDK in your language of choice (Python `a2a-sdk` v0.5+ is the reference; JavaScript, Java, Go, .NET all supported per the [April 2026 milestone](https://www.prnewswire.com/news-releases/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year-302737641.html)).

If any of those are gaps, fix the gaps first. **Path 04 completion is non-negotiable for this project**; the build assumes the MCP and A2A primitives are already familiar.

## What you'll have when done

- A supervisor agent in Org A: FastAPI service exposing an A2A agent card at `/.well-known/agent-card.json`, dispatching tasks to 3 cross-org specialist agents via A2A `tasks/send`.
- An inventory specialist in Org B: A2A agent card + task lifecycle endpoints + 3 MCP-wrapped tools (`check_stock`, `reserve_units`, `lookup_lead_time`). MCP server runs as a sibling process in Org B's deployment.
- An approvals specialist in Org C (vendor compliance simulated): A2A endpoints + 2 MCP tools (`check_vendor_status`, `request_compliance_review`). Deployed in a separate cloud/region from the supervisor.
- A payments specialist in Org D (AP2 integration): A2A endpoints + AP2 mandate-extension for the payment authorization signature; 2 MCP tools (`initiate_payment`, `lookup_payment_status`).
- OAuth 2.1 auth on every cross-org call — agent cards advertise the required scopes; the supervisor authenticates against each specialist's IDP before sending tasks.
- JWS-RS256 signatures on agent cards — the supervisor verifies each specialist's card signature against a published JWK set before trusting the advertised capabilities.
- SSE streaming for long-running tasks (>30s wall-clock) — specialists stream progress events back to the supervisor; the supervisor relays to the end-user.
- Per-cross-org-call retry policy with exponential backoff + jitter — A2A's `taskNotFound` and `invalidParams` errors fast-fail; `serverError` retries up to 3 times.
- End-to-end provenance chain: every task carries `{task_id, originating_agent_did, dispatched_at, completed_at, completion_signature}` recorded in PostgreSQL; the supervisor's final response carries a provenance bundle attesting which specialist did what.
- A 15-task end-to-end acceptance suite covering: 3 normal procurement flows, 3 vendor-rejection flows, 3 payment-failure flows, 3 partial-completion flows (one specialist down), 3 multi-org-correlation flows (same task ID threading through all 4 agents).
- A runbook entry covering: rolling a specialist's signing key without breaking active tasks; the cross-org incident-response playbook (who do you page when Org C's compliance service is down?); the audit-log format for cross-org task chains.

## Architecture at a glance

```mermaid
flowchart TB
    User[End user<br/>or upstream agent] --> SupAPI[Org A FastAPI<br/>supervisor]

    SupAPI --> SupOrch[Supervisor<br/>orchestrator<br/>Pattern 03]
    SupOrch <--> SupMCP[(Supervisor<br/>local MCP<br/>own tools)]

    SupOrch -- A2A<br/>tasks/send<br/>OAuth 2.1 + JWS --> InvA2A[Org B A2A<br/>endpoint]
    SupOrch -- A2A<br/>tasks/send --> AppA2A[Org C A2A<br/>endpoint]
    SupOrch -- A2A<br/>tasks/send --> PayA2A[Org D A2A<br/>endpoint]

    InvA2A --> InvAgent[Inventory<br/>specialist]
    AppA2A --> AppAgent[Approvals<br/>specialist]
    PayA2A --> PayAgent[Payments<br/>specialist<br/>+ AP2 mandate]

    InvAgent <--> InvMCP[(Org B MCP<br/>3 tools)]
    AppAgent <--> AppMCP[(Org C MCP<br/>2 tools)]
    PayAgent <--> PayMCP[(Org D MCP<br/>2 tools)]

    InvA2A -. "SSE stream<br/>progress events" .-> SupOrch
    AppA2A -. "SSE stream" .-> SupOrch
    PayA2A -. "SSE stream" .-> SupOrch

    SupOrch --> ProvDB[(PostgreSQL<br/>cross-org<br/>task provenance)]
    SupOrch --> Audit[(Audit log<br/>append-only)]

    InvA2A -- "agent card<br/>JWS-signed" .-> CardReg{Agent Card<br/>Verifier}
    AppA2A -. "agent card" .-> CardReg
    PayA2A -. "agent card" .-> CardReg
    CardReg -. "JWK set<br/>per IDP" .-> SupOrch

    style User fill:#fff4e6
    style SupAPI fill:#fff4e6
    style SupOrch fill:#ffd6a5
    style InvAgent fill:#e6f2ff
    style AppAgent fill:#e6f2ff
    style PayAgent fill:#e6f2ff
    style SupMCP fill:#f3e8ff
    style InvMCP fill:#f3e8ff
    style AppMCP fill:#f3e8ff
    style PayMCP fill:#f3e8ff
    style ProvDB fill:#f3e8ff
    style Audit fill:#f3e8ff
    style CardReg fill:#e6f6ec
```

Four structural choices matter most. First, MCP and A2A are *complementary layers*, not alternatives — per [Atlan April 2026](https://atlan.com/know/google-a2a-protocol/), "MCP is the vertical layer (agent ↔ tool); A2A is the horizontal layer (agent ↔ agent)." Each specialist uses MCP locally for its tool surface and A2A externally to coordinate with the supervisor. Second, OAuth 2.1 is *not optional* — the [AIP arxiv:2603.24775 (2026)](https://arxiv.org/pdf/2603.24775) Knostic security scan found every one of ~2,000 production MCP servers lacked authentication; the project ships it correctly out of the gate rather than treating it as "ship later." Third, the JWS-signed agent card is the trust anchor for cross-org capability advertisement — without signature verification, an attacker could spoof a specialist's card and offer poisoned capabilities. Fourth, SSE streaming on long-running tasks means the supervisor doesn't poll every specialist on a fixed cadence — events arrive when there's news.

## Build milestones

### M1 — Supervisor agent in Org A with agent card + own MCP (~1 day)

**Goal**: ship the Org A supervisor's A2A face and local MCP tool surface.

**Scope**:
- FastAPI service with an A2A agent card at `/.well-known/agent-card.json`. Card lists supervisor's own capabilities and OAuth 2.1 metadata.
- JWS-RS256 signing of the agent card with a private key in the secret manager.
- Local MCP server (sibling process) with the supervisor's own tools (e.g., `decompose_procurement_request`, `synthesize_partial_response`).
- A2A task handlers (`tasks/send`, `tasks/get`, `tasks/cancel`) bridged to the supervisor's orchestrator code.
- Health check + readiness probe.

**Done when**:
- Curling `/.well-known/agent-card.json` returns a JWS-signed card; verifying the JWS with the published JWK passes.
- The supervisor's own MCP tools are listed when calling its MCP server's `tools/list` method.
- `POST /a2a/v1/tasks/send` with a stub task returns a `taskId`; `GET /a2a/v1/tasks/get/{taskId}` returns status progression.

### M2 — Inventory specialist in Org B (~1 day)

**Goal**: ship the first cross-org specialist with its own MCP tool surface.

**Scope**:
- Deployed in a different cloud region (or a different cluster — anything that demonstrates "this is a separate service") from Org A.
- Agent card advertising `inventory_lookup`, `unit_reservation` capabilities + the OAuth 2.1 scopes the supervisor needs.
- Three MCP-wrapped tools: `check_stock(sku: str) -> int`, `reserve_units(sku: str, count: int, hold_minutes: int = 5) -> ReservationId`, `lookup_lead_time(sku: str) -> int`.
- A2A task lifecycle: receives a task with `{sku, action, count}` parameters; returns `{stock, reservation_id, lead_time_days}` in the result.
- Idempotency keys on `reserve_units` — the same `(supervisor_task_id, sku, count)` doesn't double-reserve.

**Done when**:
- The supervisor in Org A successfully dispatches a `check_stock` task to Org B and gets a result via A2A.
- Inspecting the trace shows the OAuth 2.1 token exchange happening before the task dispatch (not as the task body).
- Re-sending the same `reserve_units` request returns the existing reservation ID, not a duplicate.

### M3 — Approvals (Org C) + Payments (Org D) specialists (~1.5 days)

**Goal**: ship the remaining two specialists; introduce AP2 integration for payments.

**Scope**:
- **Approvals (Org C)**: agent card + 2 MCP tools (`check_vendor_status(vendor_id) -> VendorStatus`, `request_compliance_review(vendor_id, scope) -> ReviewId`). Long-running tasks expected (compliance reviews take days); SSE streaming on `tasks/sendSubscribe`.
- **Payments (Org D)**: agent card + 2 MCP tools (`initiate_payment(amount, recipient, mandate) -> PaymentId`, `lookup_payment_status(payment_id) -> PaymentStatus`). AP2 mandate extension on the agent card declaring the supported mandate types; `initiate_payment` requires a signed mandate token from the user.
- Both specialists deploy with their own OAuth 2.1 IDP (or a shared one for the project; production deployments would use per-org IDPs).
- Both specialists implement the same idempotency-key contract as Org B.

**Done when**:
- The supervisor dispatches tasks to all 3 specialists in a single procurement flow; the trace shows task IDs threaded through.
- A long-running compliance review streams progress events to the supervisor via SSE; the supervisor relays them to its caller.
- `initiate_payment` without a valid AP2 mandate is rejected with a structured `mandate_required` error; with a valid mandate it succeeds.

### M4 — JWS-signed agent card verification (~0.5 day)

**Goal**: enforce signature verification on every specialist's agent card before trusting its capabilities.

**Scope**:
- Each specialist publishes a JWK Set at `/.well-known/jwks.json` (the public keys whose private counterparts sign their agent cards).
- The supervisor fetches each specialist's card on startup + every 24h refresh; verifies the JWS using the specialist's JWK Set; refuses to dispatch to specialists whose cards fail verification.
- An `agent_card_signature_failed` event is a T2 escalation per [Path 03 v2 Pattern 03](../patterns/03-escalation-and-fallback.md).
- Verified-card metadata cached for the 24h refresh window; stale cache returns prior-known-good card with a warning.

**Done when**:
- Manually tampering with a specialist's agent card response (e.g., a man-in-the-middle proxy returning an unsigned card) causes the supervisor to refuse to dispatch + emit a T2 escalation.
- Signing key rotation (specialist publishes a new JWK with the same `kid`; old JWS becomes invalid) is detected within the 24h refresh window.

### M5 — OAuth 2.1 on every cross-org call (~1 day)

**Goal**: every A2A call between organizations is authenticated.

**Scope**:
- The supervisor obtains an OAuth 2.1 access token from each specialist's IDP via client-credentials flow (or RFC 9068 token introspection).
- Tokens cached for ~80% of their TTL; refresh ahead of expiry.
- The Authorization header on every A2A request carries `Bearer <token>`.
- Each specialist validates the token: signature, expiry, audience (`aud` must be the specialist's agent card identifier), required scopes (e.g., `inventory:read inventory:reserve`).
- A token-validation failure returns A2A `401 unauthorized` with a structured `WWW-Authenticate` challenge.

**Done when**:
- A request without an Authorization header is rejected with 401.
- A request with a token for the wrong audience is rejected with 401 + `wrong_audience` in the response.
- Token refresh happens automatically (token expires; next request succeeds without manual intervention).
- The [Knostic-style audit](https://arxiv.org/pdf/2603.24775) finding ("every production MCP server lacked authentication") does NOT apply to this deployment — verify by running a curl with no token and confirming 401.

### M6 — End-to-end provenance + audit log (~1 day)

**Goal**: every cross-org task chain produces an audit-trail-quality provenance record.

**Scope**:
- Every task carries an immutable `{task_id, originating_agent_did, dispatched_at, parent_task_id?}` provenance header per [Path 03 v2 Pattern 06](../patterns/06-cross-agent-provenance.md).
- On task completion, the specialist signs a completion attestation: `{task_id, completed_at, result_hash, agent_did, signature}`.
- The supervisor accumulates the chain into a `provenance_bundle` in the final response.
- An append-only `audit_log` table in PostgreSQL captures every task dispatch + completion + escalation event with cryptographic integrity (each entry chained to the previous via `prev_entry_hash`).
- A query helper `get_task_chain(supervisor_task_id) -> list[ProvenanceEntry]` reconstructs the cross-org task chain.

**Done when**:
- Inspecting a completed end-to-end task shows the full provenance bundle: supervisor → inventory + approvals + payments, with signed attestations from each specialist.
- The audit log is append-only at the database level (no UPDATE or DELETE permissions on the `audit_log` table for the application role).
- Verifying the chain integrity: tampering with any audit entry breaks the `prev_entry_hash` chain on the next entry.

### M7 — Pattern 05 retry policies + SSE streaming + Pattern 03 escalation (~1 day)

**Goal**: ship the resilience + observability layers.

**Scope**:
- Retry wrapper on every A2A `tasks/send` call: 3 retries max, exponential backoff with jitter. Retry on `serverError`; fast-fail on `invalidParams`, `taskNotFound`, `unauthorized`.
- SSE streaming via `tasks/sendSubscribe` for tasks expected to take >30s wall-clock (compliance reviews, multi-step approvals).
- Escalation tiers wired per [Path 03 v2 Pattern 03](../patterns/03-escalation-and-fallback.md): T0 (low-stakes failure), T1 (cross-org task chain failed mid-flight; needs offline review), T2 (a specialist's agent card signature failed; security escalation), T3 (all 3 specialists down within 5 minutes; major incident).
- Cross-org incident response: the supervisor's escalation knows which org owns each specialist; the page payload includes "Org C's approvals specialist is down" not just "specialist 2 failed."

**Done when**:
- A transient 503 from Org B during a `check_stock` call retries 3 times before failing; the trace shows the retry sequence.
- A long-running compliance review streams `IN_PROGRESS` events; the supervisor's caller sees progress without polling.
- An injected "all specialists down" scenario triggers T3 with the correct org-ownership annotations in the page payload.

### M8 — 15-task acceptance suite + cross-org runbook (~0.5-1 day)

**Goal**: ship the regression suite + cross-org runbook.

**Scope**:
- 15 tasks across 5 categories: 3 normal procurement flows (all specialists succeed), 3 vendor-rejection flows (Org C returns reject), 3 payment-failure flows (Org D returns insufficient funds), 3 partial-completion flows (Org B down; tasks land at Org C and Org D anyway), 3 multi-org-correlation flows (deep chain across all 4 agents).
- Each task asserts: expected final result, expected number of cross-org calls, provenance-chain integrity, audit-log completeness.
- Cross-org runbook: signing-key rotation procedure (Org A side); incident-response who-to-call by org; audit-log format + how to reconstruct a task chain; AP2 mandate refresh procedure.

**Done when**:
- The 15-task suite passes in CI on a fresh branch.
- A teammate not involved in the build can follow the runbook to rotate the supervisor's signing key without breaking the in-flight tasks (key publishes alongside the old one for the refresh window; old key revoked after the window).

## The integration layer

| Milestone | Path 03 v1 lab | Path 03 v2 pattern | Top-level pattern | Path 04 module/lab |
|---|---|---|---|---|
| M1 — Supervisor + own MCP | [Lab 10 (Supervisor-worker)](../../../labs/10-supervisor-worker-from-scratch/) | — | [Pattern 03](../../../patterns/03-supervisor-workers.md), [Pattern 11 (MCP)](../../../patterns/11-mcp-integration.md), [Pattern 12 (A2A)](../../../patterns/12-a2a-federation.md) | Module 1 (MCP build), Module 4 (A2A foundations); [Lab 25](../../../labs/25-mcp-server-from-scratch/), [Lab 28](../../../labs/28-a2a-endpoint-from-scratch/) |
| M2 — Inventory specialist | — | — | [Pattern 11](../../../patterns/11-mcp-integration.md), [Pattern 12](../../../patterns/12-a2a-federation.md) | Module 5 (A2A production depth); [Lab 29 (A2A production depth)](../../../labs/29-a2a-endpoint-production-depth/) |
| M3 — Approvals + Payments | — | — | [Pattern 12](../../../patterns/12-a2a-federation.md) | Module 7 (MCP+A2A composition); [Lab 30 (MCP+A2A composition)](../../../labs/30-mcp-a2a-composition/) |
| M4 — JWS card verification | — | — | [Pattern 12](../../../patterns/12-a2a-federation.md) | Module 5 (A2A production depth — JWS-RS256 signed cards); [Lab 29](../../../labs/29-a2a-endpoint-production-depth/) |
| M5 — OAuth 2.1 on calls | — | — | [Pattern 11](../../../patterns/11-mcp-integration.md), [Pattern 12](../../../patterns/12-a2a-federation.md) | Module 3 (MCP security threat model), Module 6 (A2A production depth) |
| M6 — Provenance + audit | — | [Pattern 06 (Cross-agent provenance)](../patterns/06-cross-agent-provenance.md) | [Pattern 12](../../../patterns/12-a2a-federation.md) | Module 7 (MCP+A2A composition) |
| M7 — Retries + SSE + escalation | — | [Pattern 03 (Escalation)](../patterns/03-escalation-and-fallback.md), [Pattern 05 (Retry policies)](../patterns/05-retry-policies.md) | — | Module 5 (SSE streaming) |
| M8 — Suite + runbook | [Lab 16 (Multi-agent eval)](../../../labs/16-multi-agent-evaluation-from-scratch/) | — | — | — |

The integration layer is the densest of the three Path 03 projects. The Path 04 prerequisites are load-bearing — every milestone depends on at least one Path 04 module or lab.

## Acceptance rubric

A PR is ready to ship when:

1. **Every cross-org A2A call carries an OAuth 2.1 Bearer token.** Run a manual curl without the Authorization header against each specialist; all must return 401. This is the explicit defense against the [Knostic-style "every MCP server lacked authentication" finding](https://arxiv.org/pdf/2603.24775).
2. **Every agent card is JWS-RS256 signed; the supervisor verifies signatures before dispatching tasks.** Code review confirms the verification step happens before the first `tasks/send`. Manual tampering with a card during integration testing must trigger T2 escalation.
3. **MCP serves the tool surface for each agent; A2A serves the inter-agent transport.** No agent uses A2A for tool calls; no agent uses MCP for cross-org agent communication. This is the [Atlan April 2026 framing](https://atlan.com/know/google-a2a-protocol/) — vertical (MCP) vs horizontal (A2A).
4. **Idempotency keys on every state-mutating cross-org call.** Re-sending the same `(supervisor_task_id, action, args_hash)` returns the prior result, never duplicates a side effect (no double-reservations, no double-payments).
5. **Provenance bundle complete on every successful task.** The final result includes signed completion attestations from every specialist that contributed; no orphan claims.
6. **Audit log is append-only at the database level.** The application role has no UPDATE/DELETE on `audit_log`; tested with a manual SQL UPDATE attempt that must fail with a permission error.
7. **Per-cross-org-call retry policy fast-fails on `invalidParams` + `taskNotFound`** (these aren't transient); retries on `serverError` + transient 503s with 3-retry cap.
8. **SSE streaming wired for tasks expected to take >30s.** Compliance reviews stream progress; the supervisor's caller sees `IN_PROGRESS` events.
9. **Escalation pages carry org ownership.** A T2 page for an Org C signature failure says "Org C's approvals specialist failed signature verification at 14:23 UTC," not "specialist 2 failed."
10. **The 15-task suite passes in CI.** Failures across the partial-completion + multi-org-correlation categories are the most diagnostic — they exercise the provenance + retry + escalation paths together.
11. **AP2 mandate validation is correct on Org D's payments specialist.** `initiate_payment` without a valid mandate returns `mandate_required`; with a forged mandate (intentionally bad signature in test) returns `invalid_mandate`. Per the [AP2 / A2A Linux Foundation framing](https://www.prnewswire.com/news-releases/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year-302737641.html), this is the standard for cross-org payment authorization in 2026.

## Common failure modes and recoveries

### Agent card spoofing accepted because signature verification was deferred

The build ships M1-M3 and runs cross-org tasks in dev without M4 (JWS verification). At staging, someone notices a misconfigured specialist agent serving the wrong agent card; the supervisor trusts it and dispatches tasks based on advertised but non-existent capabilities.

**Recovery**: M4 is not optional. The verification step happens before the first `tasks/send` — there is no "ship it now, verify later" path that's safe. Production deployments without card-signature verification are the most common 2026 security finding per the AIP arxiv:2603.24775 paper.

### OAuth 2.1 token refresh deadlocks under load

Token refresh code uses a mutex that other refresh-callers can't enter; under load, all callers wait for the first refresh to complete, but the first refresh holds the mutex while making the network call. The deadlock causes 5-second p99 latency spikes whenever a token expires.

**Recovery**: refresh tokens at ~80% TTL (not on expiry), in a background task; cache the new token before signaling other callers. Refresh-in-the-hot-path is the antipattern.

### Cross-org provenance loses fidelity through synthesis

Supervisor's synthesis step composes specialist results into a final response; in the process, the specific source-org attribution drops. The compliance team can't answer "which org's data led to this approval decision" without re-running the task.

**Recovery**: provenance is structural data, not narrative prose. The synthesizer composes the narrative; the provenance_bundle is assembled separately by accumulating the signed attestations from each specialist call. They ride alongside in the response, not embedded in the prose.

### Idempotency-key collision across organizations

Org B and Org D both implement idempotency keying using `task_id`. A retried supervisor call propagates the same `task_id` to both specialists — but because the keys are scoped to the receiving org, there's no global uniqueness guarantee. A debugging session interpreting the audit log gets confused.

**Recovery**: idempotency keys derived from `(originating_agent_did, supervisor_task_id, child_task_id)` — the originating agent's DID makes the key globally unique. The audit log uses this composite key.

### SSE connection drops aren't recovered

A long-running compliance review (Org C, 2-hour task) streams progress events. A network blip between Org A and Org C drops the SSE connection at minute 47. The supervisor never receives the `COMPLETED` event; the task is "running" forever per the supervisor's view; the user's UI shows "in progress" indefinitely.

**Recovery**: SSE recovery via `tasks/get` polling fallback. After a connection drop, the supervisor falls back to polling `tasks/get` every 60s until either the SSE reconnects or the task completes. The same `taskId` reconciles state.

### Cross-org incident response without org-aware paging

A T3 incident fires: "all specialists down." The on-call team in Org A doesn't know that Org C is in a different time zone with a different on-call rotation. By the time someone reaches Org C's team, 90 minutes have passed.

**Recovery**: every specialist's agent card includes an `incident_contact` field (PagerDuty service key or equivalent). The supervisor's escalation page payload includes the right contact per specialist. Cross-org incidents page the right team in each org simultaneously.

### AP2 mandate refresh causes payment failures during user inactivity

User authorizes the supervisor to make payments via AP2 mandate. Mandate has a 24-hour TTL. User's session sits idle for 30 hours (waiting for a multi-day compliance review). When the payment fires, the mandate has expired; the payment fails; the user is surprised.

**Recovery**: mandate refresh proactive — the supervisor checks mandate TTL when dispatching; if the mandate will expire before the expected payment window, the supervisor surfaces a "please re-authorize" event back to the user before the long-running task starts.

## Operational checklist (pre-launch)

### Instrumentation

- [ ] Distributed tracing across all 4 agents (OpenTelemetry with W3C TraceContext propagation across A2A calls)
- [ ] Per-task cost attribution (each agent emits its own cost; supervisor aggregates)
- [ ] Per-cross-org-call latency histogram (Org A → Org B, A → C, A → D)
- [ ] Signature verification success/failure rate per specialist

### Deployment

- [ ] Each specialist deployed independently (no shared container image)
- [ ] Per-specialist secret management (each org owns its own signing key + IDP credentials)
- [ ] PostgreSQL with append-only enforcement on `audit_log` (database-level role permissions)
- [ ] Redis or equivalent for cross-org task-id correlation (with TTL appropriate to the longest expected task)

### Security

- [ ] OAuth 2.1 + client-credentials flow on every cross-org call; tokens cached, refreshed at ~80% TTL
- [ ] JWS-RS256 agent card verification on startup + every 24h refresh
- [ ] Signing key rotation procedure documented and rehearsed (M8 runbook)
- [ ] AP2 mandate validation on payment specialist (signature verification + TTL check + scope verification)
- [ ] Per-specialist allowlist of supervisor DIDs (so a specialist refuses requests from non-allowlisted supervisors)

### Monitoring

- [ ] Cross-org task chain completion rate dashboard
- [ ] Per-specialist availability + p95 latency dashboard
- [ ] T2 + T3 escalation rate, broken down by source org
- [ ] Audit-log integrity check (cron: verify the `prev_entry_hash` chain daily)

### Runbook

- [ ] Signing-key rotation procedure (Org A supervisor side) — overlap window, JWK set updates, monitoring during cutover
- [ ] Cross-org incident-response who-to-call by org (with timezone awareness)
- [ ] Audit-log query examples — reconstructing a task chain end-to-end
- [ ] AP2 mandate refresh procedure — proactive refresh + user re-authorization flow
- [ ] "A specialist's agent card signature is failing" — diagnosis steps (key rotation? misconfigured deployment? actual attack?)

## Cost envelope

| Scale | LLM tokens | Infrastructure | Observability | Cross-org transit | Total |
|---|---|---|---|---|---|
| 1K tasks/mo | ~$60 (4 agents × moderate per-task token spend) | ~$240 (4 deployments × $60: small FastAPI + small Postgres each) | ~$0 (OTel + local backend) | ~$5 (cross-region egress) | **~$305/mo** |
| 10K tasks/mo | ~$600 | ~$800 (4 × $200 medium tier) | ~$80 (vendor APM) | ~$25 | **~$1,505/mo** |
| 100K tasks/mo | ~$6,000 | ~$3,200 (4 × $800 autoscaled with Redis) | ~$500 | ~$200 | **~$9,900/mo** |

The 4-deployment infrastructure cost is the dominant non-LLM factor — each agent has its own FastAPI + Postgres + secret management + monitoring. Co-locating agents (3 in same cloud account, one external) drops the infrastructure cost ~40% but defeats some of the cross-org isolation; production deployments usually accept the cost for the boundary.

The high-variance components: cross-region egress (cloud providers move egress pricing periodically; AWS/GCP/Azure cross-region rates differ); each org's own observability backend (Datadog APM at 100K traces/mo per org × 4 orgs = potentially $1K+/mo if not careful); LLM token cost for the multi-agent token premium (4 agents × moderate per-call token spend is a structural multiplier per [MintSquare January 2026](https://www.agentframeworkhub.com/blog/ai-agent-production-costs-2026)). Re-verify each line quarterly.

## Extensions and where to go next

- **AIP (Agent Identity Protocol) when it lands** — the arxiv:2603.24775 paper proposes attenuable delegation tokens (macaroon-based) and chained policy with provenance-aware completion records. As of mid-2026, no production implementation exists, but Google DeepMind's Tomašev et al. 2026 paper and the four IETF Internet-Drafts (AIMS, WIMSE, Agentic JWT, SCIM for agents) signal the direction. When AIP ships, the OAuth 2.1 layer in this project becomes a backward-compatible step toward attenuable delegation.
- **A2A v2 features as they land** — the Linux Foundation governance of A2A means new features ship through a standardized RFC process. Track the [github.com/google-a2a/A2A](https://github.com/google-a2a/A2A) repo for new RFCs; integrate the ones relevant to your use case.
- **Google ADK 1.0 hierarchical agent trees** — per [n1n.ai 2026](https://explore.n1n.ai/blog/google-adk-1-0-a2a-protocol-multi-agent-standard-2026-05-04), ADK 1.0 (April 2026) provides a hierarchical agent tree where a root agent delegates to sub-agents which can in turn have their own sub-agents. Integrating Org D's payments agent into a 2-level hierarchy (parent payments coordinator + child specialists for ACH/wire/card) would add specialization without changing the supervisor's A2A interface to Org D.
- **AP2 expansion to other regulated flows** — the [April 2026 AP2 mandates extension](https://www.prnewswire.com/news-releases/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year-302737641.html) currently focuses on payments. As similar protocols emerge for healthcare consent, contract execution, or regulatory submission, the same mandate-verification pattern applies. Generalize the AP2 validator code to be protocol-agnostic.
- **Move to a service mesh** — at 100K+ tasks/mo with 4 agents in different deployments, mTLS + service-mesh policy (Istio, Linkerd) wraps the A2A transport layer. The agent-card-bound JWS + OAuth 2.1 remain at the application layer; mesh adds defense in depth.

## References + further reading

**Path 03 + Path 04 repo content**:
- [Path 03 README](../README.md) — the overall multi-agent path
- [Path 04 README](../../04-tool-protocols-mcp-a2a/) — the protocol-layer learning path (required prerequisite)
- [Pattern 11 (MCP integration)](../../../patterns/11-mcp-integration.md), [Pattern 12 (A2A federation)](../../../patterns/12-a2a-federation.md) — the architectural patterns this composes
- [Lab 29 (A2A production depth)](../../../labs/29-a2a-endpoint-production-depth/), [Lab 30 (MCP+A2A composition)](../../../labs/30-mcp-a2a-composition/) — the Path 04 labs whose patterns this project deploys

**2026 production guides + announcements**:
- [Linux Foundation (April 9, 2026), *A2A Protocol Surpasses 150 Organizations*](https://www.prnewswire.com/news-releases/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year-302737641.html) — the production-adoption milestone; AP2 mandates extension; 5 SDK languages (Python, JS, Java, Go, .NET)
- [Atlan (April 2026), *Google A2A Protocol: How Agent-to-Agent Coordination Works*](https://atlan.com/know/google-a2a-protocol/) — the MCP-vs-A2A vertical/horizontal framing; production-adoption status; SDK ecosystem maturity
- [dev.to (April 2026), *Google's A2A Protocol: How AI Agents Communicate Across Frameworks*](https://dev.to/agentsindex/googles-a2a-protocol-how-ai-agents-communicate-across-frameworks-52jj) — Andrew Ng + Ivan Nardini quotes; the "building agents is the easy part, getting them to talk is another game" framing
- [Galileo (January 2026), *Google's Agent2Agent Protocol Explained*](https://galileo.ai/blog/google-agent2agent-a2a-protocol-guide) — protocol overview; 40% enterprise application prediction; ecosystem-lock-in concerns

**Foundational papers**:
- [AIP: Agent Identity Protocol for Verifiable Delegation Across MCP and A2A (arXiv:2603.24775, 2026)](https://arxiv.org/pdf/2603.24775) — the Knostic security scan finding (every production MCP server lacked authentication); the attenuable-delegation framing; the four IETF Internet-Drafts (AIMS, WIMSE, Agentic JWT, SCIM for agents)
- Tomašev et al. (2026), *Intelligent AI Delegation* (Google DeepMind) — delegation capability tokens built on macaroons; the attenuation-first design philosophy

**Framework + protocol docs**:
- [A2A Protocol GitHub](https://github.com/google-a2a/A2A) — 22K+ stars; the canonical protocol repo; SDK references
- [MCP Specification](https://spec.modelcontextprotocol.io/) — the tool-protocol layer; v0.3 schema as of mid-2026
- [Google ADK 1.0](https://google.github.io/adk-docs/) — hierarchical agent tree framework; native A2A integration
