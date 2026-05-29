---
quiz_id: a2a-endpoint-production-depth
topic: A2A endpoint at production depth
difficulty: intermediate
concept_pages:
  - concepts/tools/a2a-endpoint-production-depth.md
lab: labs/29-a2a-endpoint-production-depth/
question_count: 8
question_type: single_select
---

# Quiz — A2A endpoint at production depth

Pair with [Module 6 — A2A endpoint at production depth](../../concepts/tools/a2a-endpoint-production-depth.md) and [Lab 29](../../labs/29-a2a-endpoint-production-depth/). Eight questions covering persistence, identity, authentication, streaming, and observability.

---

### 1. You replaced `InMemoryTaskStore` with `DatabaseTaskStore` pointing at PostgreSQL. The SDK release notes for the next minor version warn about a breaking change to the `tasks` table schema. Which approach actually protects your existing tasks during the upgrade?

- A. Trust the SDK to migrate the schema during `await store.initialize()`
- B. Pin the SDK version and treat the schema as append-mostly until the SDK ships migrations
- C. Run `await store.delete_all()` before upgrading, then restore from backup
- D. Switch to `InMemoryTaskStore` during the upgrade window

<details>
<summary>Answer</summary>

**B**. The SDK doesn't yet ship Alembic-style migrations; `initialize()` creates the table on first use but doesn't migrate existing schema across versions. The defensive posture is to pin the SDK version and treat schema as append-mostly until migrations land. Option A is wrong because the SDK explicitly leaves migrations as an open problem. Option C destroys real production data. Option D loses every active task as soon as the process restarts.

</details>

---

### 2. You verified that a signed Agent Card fetched from `https://billing.acme.com/.well-known/agent-card.json` has a valid JWS signature. What does that guarantee — and what does it NOT guarantee?

- A. Guarantees the card came from acme.com; does not guarantee the agent's behavior matches the card's claims
- B. Guarantees the agent will perform the actions in the card; does not guarantee freshness
- C. Guarantees the public key you used belongs to acme.com; does not guarantee the card was generated today
- D. Guarantees the card hasn't been tampered with since the signer signed it; does not guarantee the signer's key actually belongs to whoever you think it does

<details>
<summary>Answer</summary>

**D**. JWS signatures only prove that the holder of the private key signed the payload — they prove nothing about *who* that key holder is. Key distribution is out of A2A's scope; without a trust mechanism (PKI cert chain, JWKS endpoint from a known domain, out-of-band exchange), an attacker can sign a perfectly-valid card with their own key. Option A conflates signature validation with domain ownership; nothing in the protocol ties a JWS signature to a specific domain. Option B confuses identity with behavior. Option C inverts the chain of trust — you must already know the public key belongs to acme.com before verification is meaningful.

</details>

---

### 3. Your A2A endpoint declares `apiKey` as a `SecurityRequirement` in its Agent Card. Lab 29 puts the API-key check in a Starlette middleware, but skips `/.well-known/` paths. Why?

- A. Performance — the Agent Card is fetched frequently and the auth check adds latency
- B. The Agent Card discovery URL is the bootstrap entry point for trust establishment; gating it behind auth would prevent callers from learning what credentials they need
- C. The SDK's `create_agent_card_routes` rejects authenticated requests
- D. To support legacy v0.3 clients that don't send authentication headers

<details>
<summary>Answer</summary>

**B**. The Agent Card discovery URL is the entry point for trust establishment — it's where a caller learns *what auth scheme to use*. Putting auth on the discovery URL creates a chicken-and-egg problem: the caller needs to read the card to know what credentials to send, but can't fetch the card without credentials. The signature on the card itself provides integrity (Q2); auth gates the *actions*, not the *discovery*. Option A is incidental, not the design reason. Option C is fabricated. Option D inverts cause and effect.

</details>

---

### 4. Module 6 recommends RS256 over the bare `EdDSA` algorithm for signing Agent Cards. Which statement best captures the reasoning?

- A. RS256 produces shorter signatures, reducing card payload size
- B. RS256 is faster on commodity hardware than Ed25519
- C. Bare `EdDSA` was deprecated by RFC 9864 (split into `Ed25519` and `Ed448`); RS256 has no equivalent deprecation churn and is universally supported
- D. Ed25519 keys are not compatible with the `AgentCardSignature` proto type

<details>
<summary>Answer</summary>

**C**. RFC 9864 deprecated the bare `EdDSA` algorithm name in favor of the curve-specific `Ed25519` and `Ed448` names. The `joserfc` library raises a `SecurityWarning` for bare `EdDSA`. RS256 with RSA-2048 has no such deprecation, is widely understood by every auth stack, and remains a defensible default. Option A is the opposite — RSA signatures are *larger* than Ed25519. Option B is also wrong — Ed25519 is faster than RSA. Option D is fabricated — `AgentCardSignature` is algorithm-agnostic; it carries whatever the JWS header declares.

</details>

---

### 5. You enabled `SendStreamingMessage` by setting `card.capabilities.streaming = True` and a client streams a long-running task. The agent's `execute()` calls `await updater.start_work()`, then `await updater.add_artifact(...)`, then `await updater.complete()`. What does the client see in the SSE stream?

- A. One event containing the final completed Task
- B. Four events: the initial Task, a `WORKING` status update, the artifact update, and a `COMPLETED` status update
- C. Three events: `WORKING`, the artifact, `COMPLETED` (the initial Task is returned as the response body, not as an SSE event)
- D. Two events: a single status update with the final state and the artifact bundled together

<details>
<summary>Answer</summary>

**B**. The canonical streaming sequence for a simple agent is four SSE events: (1) the initial Task object with state `SUBMITTED` (created from the user message), (2) a `TaskStatusUpdateEvent` with state `WORKING` from `start_work()`, (3) a `TaskArtifactUpdateEvent` from `add_artifact()`, and (4) a `TaskStatusUpdateEvent` with state `COMPLETED` from `complete()`. The dispatcher publishes the initial Task as the first SSE event, not in a separate response body. Option A describes synchronous `SendMessage`, not streaming. Options C and D conflate event types or omit the initial Task event.

</details>

---

### 6. In Lab 29, the server uses `SimpleSpanProcessor` to export OTel spans. The notebook explicitly notes this choice over `BatchSpanProcessor`. Which scenario justifies `SimpleSpanProcessor` over `BatchSpanProcessor`?

- A. Lower memory overhead in long-running production servers
- B. Lower latency per request in steady-state production traffic
- C. Spans must be visible immediately, including when the process is terminated mid-batch — e.g. a notebook subprocess that gets killed by the test harness
- D. SimpleSpanProcessor supports OTLP export; BatchSpanProcessor does not

<details>
<summary>Answer</summary>

**C**. `BatchSpanProcessor` buffers spans in memory and flushes on a timer or shutdown. When a subprocess is terminated via SIGTERM (e.g., `subprocess.terminate()` in the lab), buffered spans are lost unless the shutdown hook completes — which is fragile in test environments. `SimpleSpanProcessor` exports each span synchronously, so spans are immediately on disk and survive termination. Option A is wrong — `SimpleSpanProcessor` has *higher* per-span overhead than batched export. Option B is also wrong — `BatchSpanProcessor` is the latency winner in steady state. Option D is fabricated — both work with any exporter, including OTLP.

</details>

---

### 7. You used `subprocess.terminate()` to kill the first server in Lab 29 Step 6. Then you spawned a fresh process and called `GetTask` with a task ID from before the restart. The task came back successfully. What concretely made this work?

- A. The fresh process inherited the in-memory task state from the parent
- B. The `DatabaseTaskStore` wrote tasks to a SQLite file the fresh process re-opens; the protobuf-stored task is rehydrated from the row
- C. The SDK auto-saves tasks to `~/.a2a/cache/` when the process exits
- D. The signed Agent Card includes a snapshot of recent tasks

<details>
<summary>Answer</summary>

**B**. `DatabaseTaskStore` wraps a SQLAlchemy AsyncEngine pointed at `sqlite+aiosqlite:///./a2a_tasks.db`. Each `save(task, ctx)` call commits the task row to the file. The new process opens the same file and `get(task_id, ctx)` reads the row back, rehydrating the protobuf Task. The DB file is the persistence boundary; processes are stateless. Option A is wrong — `subprocess.terminate()` kills the child cleanly; there's no inheritance. Option C is fabricated — the SDK doesn't auto-cache. Option D confuses identity (the card) with state (the tasks).

</details>

---

### 8. Module 6 covers push notifications conceptually but Lab 29 explicitly defers their implementation to Module 7. Which reason best explains the deferral?

- A. Push notifications require a webhook receiver running in a second process, which makes sense in the multi-agent orchestrator context of Module 7 rather than the single-endpoint Lab 29
- B. Push notifications require an OAuth2 access token, which Lab 29 doesn't provide
- C. The SDK's `BasePushNotificationSender` is not yet stable enough for tutorials
- D. Push notifications only work with `DatabasePushNotificationConfigStore`, which Lab 29 doesn't use

<details>
<summary>Answer</summary>

**A**. A push-notification flow needs the *client* to expose a webhook URL the *server* can POST to. That means running a second HTTP listener inside the notebook — perfectly doable, but added complexity for what's already a 5-concern lab. Module 7's orchestrator-pattern lab is the natural home: long-running cross-agent delegations are exactly the case where push beats polling or holding an SSE stream open. The lab README explicitly states this anti-scope. Option B is wrong — push notifications work with any auth scheme. Option C is fabricated. Option D is also wrong — push works with both store implementations.

</details>

---

## What's next

- 🧠 [MCP security threat model quiz](./mcp-security-threat-model.md) — the analogous quiz for the MCP side
- 🧪 [Lab 29 — A2A endpoint at production depth](../../labs/29-a2a-endpoint-production-depth/) — the lab this quiz pairs with
- 📖 [Module 6 — A2A endpoint at production depth](../../concepts/tools/a2a-endpoint-production-depth.md) — the concept page
- 📖 **Future Module 7** — MCP + A2A composition; the orchestrator pattern that closes out Path 04
