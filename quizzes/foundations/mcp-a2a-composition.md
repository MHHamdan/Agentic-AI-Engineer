---
title: MCP + A2A composition
path: 04-tool-protocols-mcp-a2a
module: 7
difficulty: intermediate
question_count: 8
---

# MCP + A2A composition

> Covers [Module 7 — MCP + A2A composition](../../concepts/tools/mcp-a2a-composition.md) and [Lab 30](../../labs/30-mcp-a2a-composition/). The closer for Path 04.

---

### 1. The canonical Module 7 composition pattern is asymmetric. Which statement best describes the asymmetry?

- A) The agent uses A2A to call its own MCP tools internally
- B) The agent uses MCP internally for its own tools, and A2A externally to coordinate with peers
- C) MCP and A2A are alternatives — agents pick one or the other based on the task
- D) The MCP server wraps the A2A server, exposing it through MCP's tool interface

<details>
<summary>Show answer</summary>

**B.** MCP is for **agent-to-tool** (a fixed programmatic contract); A2A is for **agent-to-agent** (open-ended conversational coordination). The canonical composition is asymmetric: an agent uses MCP internally for its tools while using A2A externally to delegate to other agents. The two protocols layer; they don't compete. A and D invert the roles; C misses that real systems usually need both.

</details>

---

### 2. In Lab 30's composed worker, the `MCPClient` is opened inside `execute()` using `async with MCPClient(MCP_URL) as mcp`. What's the tradeoff vs. holding the client open in the executor's `__init__`?

- A) Inside `execute()`: simpler lifecycle; one new connection per request. In `__init__`: connection reuse for high-frequency workers, but you must handle reconnection on failures
- B) Inside `execute()`: required by the SDK; in `__init__` will raise a runtime error
- C) Inside `execute()`: faster because there's no shared state; in `__init__`: slower because of connection sharing
- D) The patterns are equivalent — the SDK pools connections automatically

<details>
<summary>Show answer</summary>

**A.** Per-request is the right default for short-lived or low-frequency workers — simple lifecycle, no shared state. High-frequency workers benefit from holding the client open in `__init__` (avoiding the TCP/TLS handshake + MCP initialize roundtrip per request), at the cost of explicit reconnection logic on transient failures. Neither the SDK nor the protocol mandates one pattern; B is wrong. C confuses connection sharing with performance — the per-request pattern is slower in steady state, not faster. D overstates what the SDK does.

</details>

---

### 3. Why does the standalone `client.create_task_push_notification_config(...)` call after `client.send_message(...)` race with task completion?

- A) The push config registration uses a different transport than send_message
- B) `send_message` waits for task completion before returning (synchronous default); by the time the standalone push-config call runs, the task is already terminal and no notification will fire
- C) The standalone call requires a separate authentication round
- D) The SDK validates push configs against a registry, which has its own queue

<details>
<summary>Show answer</summary>

**B.** The synchronous `send_message` returns once the task reaches a terminal state. The push notification sender fires on state *transitions*; if the task is already in the terminal state when the config is registered, there's nothing left to transition through. The atomic pattern (`SendMessageConfiguration.task_push_notification_config` + `return_immediately=True`) registers the config before the task starts and returns the SUBMITTED task without waiting, so the config is in place when transitions happen. A/C/D describe mechanics that aren't part of the actual race.

</details>

---

### 4. Lab 30's webhook receiver writes incoming notification bodies + headers to a JSONL file. The captured headers include `X-A2A-Notification-Token`. What's that header for in production deployments?

- A) Routing — it tells a multi-tenant webhook receiver which tenant's queue to use
- B) Idempotency — it deduplicates retried notifications
- C) Authentication — it carries a shared secret the receiver must validate before treating the body as authoritative
- D) Versioning — it identifies which A2A protocol version the worker is using

<details>
<summary>Show answer</summary>

**C.** The token is the shared secret named in `TaskPushNotificationConfig.token` when the config was registered. The SDK forwards it as the `X-A2A-Notification-Token` HTTP header on each push notification POST. Production receivers MUST validate the token; without that check, anyone who knows the webhook URL can POST fake completions. Rotation, per-task pinning, and replay protection are all natural extensions. A is a separate concern (multi-tenant routing usually uses a path or a separate header). B is partially relevant but the token itself is not an idempotency key — that's `(task_id, transition_index)`. D is wrong; protocol version goes in the `A2A-Version` header.

</details>

---

### 5. Multiple push notifications fire per task. For Lab 30's two-tool worker, the webhook typically receives 2-4 callbacks per task. What does this imply for webhook-receiver design?

- A) Receivers must rate-limit incoming notifications to prevent abuse
- B) Receivers must be idempotent — receiving the same `statusUpdate(COMPLETED)` or duplicate `artifactUpdate` should not double-process the result
- C) Receivers must reply with the same number of acknowledgments as notifications received
- D) Receivers should ignore everything except the first notification

<details>
<summary>Show answer</summary>

**B.** Each state transition + artifact publish generates a notification; the same logical event may also retry on transient HTTP failures. The webhook receiver must be idempotent — process the underlying business event once, even if the same notification arrives multiple times. Idempotency keys derived from `(task_id, transition_index)` are the standard defense. A doesn't address the actual problem (the notifications aren't abuse). C describes acknowledgments, not idempotency. D loses information — the first notification might be the initial Task, not the completion.

</details>

---

### 6. Lab 30's encapsulation check inspects the worker's Agent Card and verifies the description doesn't mention "MCP" and the card doesn't expose port 9991. What's the teaching point?

- A) Agent Cards must follow a strict naming convention that excludes protocol names
- B) The card describes the worker's *capability* (the contract); the MCP server is the *implementation*. Orchestrators get the contract; they don't get the implementation
- C) Mentioning MCP in the description triggers SDK validation errors
- D) Port 9991 is reserved by the SDK and can't appear in cards

<details>
<summary>Show answer</summary>

**B.** The composition pattern's value comes from the asymmetry: the orchestrator sees only what it needs (the skill name, the description of behavior, the input/output modes); the worker is free to swap its internal MCP server for direct database calls tomorrow without breaking the contract. If the card leaked "I use MCP at port 9991", the abstraction breaks — orchestrators might start calling the MCP server directly, defeating the entire point of the A2A boundary. A and C are wrong (no such validation exists). D is wrong (no port is "reserved").

</details>

---

### 7. Composition layers MCP and A2A. Which is NOT something composition solves out of the box?

- A) Cross-protocol tool encapsulation — the orchestrator never directly speaks MCP
- B) Cross-process boundary enforcement — each protocol has its own transport + auth
- C) Distributed tracing across the composition — `traceparent` headers propagating from orchestrator through worker through MCP server in a single trace
- D) Long-running task semantics — push notifications fire when the worker finishes

<details>
<summary>Show answer</summary>

**C.** Distributed tracing across the composition requires explicitly forwarding the `traceparent` header at each hop (orchestrator → worker → MCP server). The SDK auto-instruments each agent individually (Module 6's OTel coverage), but cross-process trace correlation needs application-level wiring. A, B, and D are real properties of the composition: encapsulation is the headline benefit; cross-process boundaries get protocol-specific defenses (Module 3's MCP five-defense, Module 6's A2A signed cards + auth); push notifications are exactly the right shape for long-running cross-agent delegation.

</details>

---

### 8. The Module 7 concept page names a specific report from a2a-mcp.org (March 2026) about composed-protocol deployments. What did it claim?

- A) Composed deployments are 10x more efficient than single-protocol systems
- B) Workflow-velocity improvement of 40-60% for orchestrated agent deployments using MCP for tools and A2A for agents
- C) MCP and A2A will merge into a single protocol by Q3 2026
- D) Composed deployments reduce token costs by 75%

<details>
<summary>Show answer</summary>

**B.** The a2a-mcp.org March 2026 reporting is the canonical "MCP for tools, A2A for agents" framing — it reports 40-60% workflow-velocity improvement for deployments using both protocols vs. monolithic single-protocol approaches. The number is a reporting claim (specific to the dataset and tasks measured); treat it as a directional signal that composition is working in practice rather than a precise benchmark you can hit in your own deployment. A overstates; C is not in the report; D conflates velocity with cost.

</details>

---

## Done?

This is the closer for Path 04. With Module 7 you've walked the full tool-protocols territory: MCP foundations + server + client + security; A2A foundations + production depth + composition. The Agent Card is your contract; the protocols are your transport; the rest is the work of building agents you can actually trust to delegate to. Next: pick an architectural pattern from [`patterns/`](../../patterns/) that fits your current system, or move to a path that engages a different problem — [Path 03](../../learning-paths/03-multi-agent-systems/) for in-process orchestration, [Path 06](../../learning-paths/06-evaluation-observability/) for measurement.
