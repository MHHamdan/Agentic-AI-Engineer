---
quiz_id: foundations-a2a-foundations
title: "A2A foundations: protocol primitives, lifecycle, MCP-vs-A2A distinction, SDK 1.0 patterns, ecosystem state"
source:
  - concepts/tools/a2a-foundations.md
  - labs/28-a2a-endpoint-from-scratch/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "What is the canonical relationship between A2A and MCP?"
    options:
      A: "A2A and MCP are competing protocols — pick one based on framework support."
      B: "A2A replaces MCP for organizations on the Linux Foundation governance side."
      C: "A2A and MCP are complementary layers, not competitors. MCP handles agent-to-tool access (one agent reaching out to its own tools and data sources); A2A handles agent-to-agent delegation (one agent delegating a task to another agent, possibly built by a different vendor or operated by a different organization). Per the A2A protocol homepage: 'Build with ADK or any framework, equip with MCP or any tool, communicate with A2A to remote agents, local agents, and humans.' Each agent typically uses MCP internally for its own tools while the orchestrator uses A2A to coordinate across agent boundaries."
      D: "MCP is a deprecated predecessor to A2A; new deployments should use A2A only."
    answer: C
    explanation: |
      This is the single most-cited misunderstanding about A2A in 2026.
      Per Stellagent April 2026: "A2A and MCP are complementary layers,
      not competitors." The clearest mental model: imagine a customer-
      service workflow. The orchestrator agent uses MCP to access its
      own knowledge base, calendar, and CRM. When the orchestrator needs
      to delegate a refund question, it uses A2A to call a billing
      specialist agent (possibly from a different team or vendor). The
      billing specialist then uses MCP internally for its own tools
      (payment system, refund policy database). Confusing the two
      "is frequently observed and has consequences" per dev.to April 2026
      — picking the wrong protocol means building the wrong abstraction.
    review:
      page: concepts/tools/a2a-foundations.md
      section: "A2A and MCP are complementary"

  - id: q2
    difficulty: easy
    question: "What are the three primitives of the A2A protocol, and where is the Agent Card typically served?"
    options:
      A: "Agents, Methods, and Responses; the Agent Card is served at /api/v1/agent."
      B: "Agent Cards (JSON capability descriptors), Tasks (stateful work units with lifecycle), and Transport (JSON-RPC 2.0 over HTTP+SSE). The Agent Card is served at the well-known URL /.well-known/agent-card.json — the discovery entry point any A2A client probes to learn what the agent can do, what auth it requires, and where to reach it."
      C: "Models, Prompts, and Tools; the Agent Card is served at the SDK-specific path."
      D: "Capabilities, Workflows, and Orchestrators; the Agent Card is published to a central Linux Foundation registry."
    answer: B
    explanation: |
      The three primitives per the official A2A protocol documentation
      and Rapid Claw's "OpenAPI for Agents" framing: Agent Cards
      (capability advertisement at /.well-known/agent-card.json),
      Tasks (the stateful work units exchanged with explicit lifecycle
      states), and Transport (HTTP + SSE + JSON-RPC 2.0 — no new
      protocol layer, deliberately reusing existing web infrastructure
      the same way MCP does). The .well-known/ URL convention follows
      RFC 8615 — the same pattern used for OpenID Connect discovery,
      Let's Encrypt ACME challenges, and other well-established
      protocols. Any A2A-compliant client starts by GET-ing this URL.
    review:
      page: concepts/tools/a2a-foundations.md
      section: "The three primitives"

  - id: q3
    difficulty: easy
    question: "How many states are in the A2A Task lifecycle (per the SDK 1.0.3 TaskState enum, ignoring TASK_STATE_UNSPECIFIED), and which are terminal?"
    options:
      A: "Three states (started, running, done); all are terminal."
      B: "Eight states total. Four non-terminal (submitted, working, input-required, auth-required) and four terminal (completed, failed, canceled, rejected). Terminal states are permanent — once a Task reaches one, it cannot transition to another state. Non-terminal states are 'alive but waiting' — the agent is either processing, waiting for client input, or waiting for auth."
      C: "Two states (pending, complete)."
      D: "Five states (submitted, in-progress, success, failure, timeout); all transitions are bidirectional."
    answer: B
    explanation: |
      The SDK 1.0.3 TaskState enum has 9 values: TASK_STATE_UNSPECIFIED
      (the protobuf default zero) plus 8 meaningful states. The
      non-terminal four represent ways a task can be alive but not done
      — the agent is working, waiting for the client to provide more
      input, or waiting for the client to authenticate. The terminal
      four represent the four ways a task can permanently end:
      successful completion, intentional cancellation by client or
      agent, agent failure, or agent rejection (the agent refused the
      task — e.g. it doesn't have a skill matching the request). The
      lifecycle is unidirectional — no recovery from a terminal state
      except creating a new Task.
    review:
      page: concepts/tools/a2a-foundations.md
      section: "Tasks"

  - id: q4
    difficulty: medium
    question: "An A2A client gets back the JSON-RPC error -32009 with message 'A2A version 0.3 is not supported by this handler. Expected version 1.0.' What's the cause and the fix?"
    options:
      A: "The server is broken; report an issue to the SDK maintainers."
      B: "The client is missing the `A2A-Version: 1.0` HTTP header. SDK 1.0.3 servers default to expecting v1.0 messages; if no version header is sent, the server falls back to assuming v0.3 (the previous default) and then refuses because it doesn't support v0.3 by default. The fix is to send the `A2A-Version: 1.0` header explicitly with every request. Servers can opt into v0.3 compatibility via the `enable_v0_3_compat=True` flag on `create_jsonrpc_routes` for legacy clients."
      C: "The agent's Agent Card has the wrong protocolVersion field; modify the card to say '1.0'."
      D: "The client is using `httpx`; switch to `requests` which negotiates the version automatically."
    answer: B
    explanation: |
      The header-based version negotiation is one of the two most
      common gotchas building A2A endpoints (the other is the "enqueue
      Task before TaskUpdater" pattern). The server's behavior is
      conservative: without an explicit version header, it assumes the
      client is speaking v0.3 (the prior default) — and since SDK 1.0.3
      servers don't enable v0.3 compat by default, the request is
      refused. Production A2A clients always send `A2A-Version: 1.0`.
      The `enable_v0_3_compat=True` flag exists for migration scenarios
      where you can't yet update every client; new deployments should
      speak v1.0 from the start.
    review:
      page: labs/28-a2a-endpoint-from-scratch/
      section: "Step 8a"

  - id: q5
    difficulty: medium
    question: "When implementing an `AgentExecutor.execute()` method using the SDK 1.0.3 `TaskUpdater`, what's the critical ordering requirement?"
    options:
      A: "Call `TaskUpdater.complete()` first to reserve the task ID, then publish artifacts."
      B: "The execute method must enqueue the initial `Task` object via `event_queue.enqueue_event(task)` BEFORE calling any TaskUpdater lifecycle methods (`submit`, `start_work`, `complete`). Calling `updater.submit()` first yields `-32006 INVALID_AGENT_RESPONSE` with message 'Agent should enqueue Task before TaskStatusUpdateEvent event'. The canonical pattern is: extract message → `new_task_from_user_message(context.message)` → `event_queue.enqueue_event(task)` → create TaskUpdater → call lifecycle methods → call `complete()`."
      C: "The execute method must use synchronous `await asyncio.sleep(0)` between every TaskUpdater call to avoid race conditions."
      D: "The order doesn't matter; the SDK reorders events automatically."
    answer: B
    explanation: |
      This is the most common AgentExecutor bug. The mental model:
      the `TaskUpdater` publishes `TaskStatusUpdateEvent` objects to
      the event queue; the server's event-processing logic requires
      seeing the initial `Task` object first so it can register the
      task in the store before status updates start landing. Without
      that prior enqueue, the server has no Task to update and the
      error fires. The fix is uniform across all AgentExecutor
      implementations: enqueue the Task first, then use the
      TaskUpdater. Lab 28 Step 3 demonstrates the correct pattern;
      this is the second of the two most common A2A gotchas (the
      first being the `A2A-Version` header from Q4).
    review:
      page: labs/28-a2a-endpoint-from-scratch/
      section: "Step 3"

  - id: q6
    difficulty: medium
    question: "What's the practical implication of A2A SDK 1.0.3 using protobuf-based types instead of Pydantic (the pre-1.0 pattern)?"
    options:
      A: "Pydantic was deprecated; protobuf is faster and that's the only difference."
      B: "Tutorials and blog posts dated pre-2026 will show patterns that no longer work. Protobuf types don't have `model_fields`, `model_dump()`, or `.json()`. Instead they use `DESCRIPTOR.fields` for introspection, `MessageToDict`/`ParseDict` for serialization, and `HasField(name)` for optional-field checks. Field names use `snake_case` on the wire (`message_id`, `task_id`, `protocol_binding`); JSON marshaling adds camelCase (`messageId`, `taskId`, `protocolBinding`) only for HTTP responses. Enums are integer-valued (`Role.ROLE_USER = 1`, `TaskState.TASK_STATE_COMPLETED = 3`) with explicit `*_UNSPECIFIED = 0` defaults. Migrating Pydantic-era A2A code to 1.0+ requires non-trivial type-handling changes."
      C: "Nothing changes; the import paths are identical."
      D: "Pydantic and protobuf coexist in 1.0.3; you can use either."
    answer: B
    explanation: |
      The 2026 protobuf shift is a real architectural break. Three
      practical consequences: (1) Type introspection looks different —
      you can't iterate `model_fields` to discover what an AgentCard
      requires; instead you read `AgentCard.DESCRIPTOR.fields`. (2)
      Serialization looks different — protobuf's `MessageToDict` /
      `ParseDict` replace Pydantic's `.model_dump()` / parsing. (3) Field
      naming has a subtle dual nature — Python uses `snake_case`
      consistently, but JSON marshaling produces camelCase. Step 1 of
      Lab 28 makes the protobuf surface explicit so the rest of the
      lab can use it correctly. Tutorials predating 2026 (including
      some still linked from the SDK README) may show
      `model_json_schema()` calls that will throw AttributeError
      against 1.0.3 types.
    review:
      page: labs/28-a2a-endpoint-from-scratch/
      section: "Step 1"

  - id: q7
    difficulty: hard
    question: "A team is designing a customer-service multi-agent system. The orchestrator agent must coordinate with three internal specialist agents (billing, technical-support, account-management) that all live in the same Python process AND with one external partner agent (legal-review, hosted by a third-party law firm). Which protocols should they use?"
    options:
      A: "A2A for all four delegations; the protocol is designed for arbitrary inter-agent coordination."
      B: "MCP for all four delegations; MCP is faster and simpler than A2A."
      C: "A2A only for the external partner (legal-review); use in-process supervisor-worker patterns from Path 03 Module 1 for the three internal specialists. A2A adds HTTP + JSON-RPC + Agent Card discovery latency that's pure overhead when all agents share a process. A2A's design payoff is across process and organizational boundaries — the latency is acceptable for the legal-review delegation but wasteful for in-process coordination. MCP doesn't apply because the question is agent-to-agent, not agent-to-tool."
      D: "Build a custom JSON protocol for the internal three; use A2A for the partner."
    answer: C
    explanation: |
      The two scope decisions: in-process vs. cross-process, and
      agent-to-agent vs. agent-to-tool. The three internal specialists
      run in the same Python process as the orchestrator — A2A's HTTP
      transport is unnecessary; an in-process supervisor-worker pattern
      from Path 03 Module 1 is the right shape (no HTTP, no JSON-RPC,
      no Agent Card discovery, sub-millisecond delegation). The
      external partner is across an organizational boundary — A2A's
      design assumptions match exactly (signed Agent Cards for trust,
      explicit task lifecycle for long-running tasks, version
      negotiation for heterogeneous infrastructure). MCP doesn't apply
      because every delegation in the system is to *another agent*, not
      to a *tool*. The internal specialists may use MCP for their own
      tools (payment system, knowledge base) — but the orchestrator
      doesn't reach those tools directly; it delegates to the specialist
      agents that own them.
    review:
      page: concepts/tools/a2a-foundations.md
      section: "When NOT to use A2A"

  - id: q8
    difficulty: hard
    question: "Which of the following correctly describes the A2A ecosystem's evolution from April 2025 to April 2026?"
    options:
      A: "A2A remained a Google-only proprietary protocol with three partner organizations."
      B: "Launched April 9 2025 with 50+ partners; donated to Linux Foundation June 23 2025; IBM's ACP merged into A2A August 2025; v1.0 with Signed Agent Cards landed early 2026; v1.2 (current stable) landed March 2026; one-year mark April 9 2026 with 150+ organizations supporting the standard. Native integrations across Google ADK, LangGraph, CrewAI, LlamaIndex Agents, Semantic Kernel, AutoGen. Production deployments at Salesforce Agentforce, SAP Joule, ServiceNow Now Assist. Spec changes now go through a public RFC process."
      C: "A2A was abandoned in late 2025 after MCP became the dominant protocol."
      D: "A2A is governed by a Google-controlled consortium; the Linux Foundation has no role."
    answer: B
    explanation: |
      Per the Linux Foundation's April 9 2026 one-year announcement,
      Stellagent's April 2026 status report, and Rapid Claw's April
      2026 complete guide: the protocol moved fast in its first year.
      Three milestones matter most. (1) The June 2025 Linux Foundation
      donation removed vendor-lock-in concerns and enabled the 150+
      organization growth. (2) The August 2025 IBM ACP merger
      eliminated A2A's biggest potential competitor by absorbing it.
      (3) The early-2026 v1.0 release with Signed Agent Cards met the
      enterprise production bar — most major cloud platforms (Azure AI
      Foundry, AWS Bedrock AgentCore, Google Cloud Vertex) integrated
      A2A natively by April 2026. For any operator designing inter-
      agent integration today, there is essentially no alternative to
      A2A as of mid-2026.
    review:
      page: concepts/tools/a2a-foundations.md
      section: "v1.0 → v1.2 evolution"
---

# A2A foundations quiz

> ⏱ ~10 min · Source pages: [A2A foundations](../../concepts/tools/a2a-foundations.md), [Lab 28](../../labs/28-a2a-endpoint-from-scratch/). Pass at 6/8.

Eight single-select questions on Path 04 Module 5 material. Coverage: protocol relationship to MCP (Q1), the three primitives (Q2), Task lifecycle (Q3), version negotiation (Q4), AgentExecutor patterns (Q5), the protobuf-vs-Pydantic shift (Q6), in-process vs cross-process decision (Q7), ecosystem evolution (Q8).

Q7 and Q8 are hard — they reward thinking about *protocol selection* and *ecosystem context* rather than just SDK mechanics. Pass mark is 6/8.

---

## Question 1

What is the canonical relationship between A2A and MCP?

- **A.** A2A and MCP are competing protocols — pick one based on framework support.
- **B.** A2A replaces MCP for organizations on the Linux Foundation governance side.
- **C.** A2A and MCP are complementary layers, not competitors. MCP handles agent-to-tool access (one agent reaching out to its own tools and data sources); A2A handles agent-to-agent delegation (one agent delegating a task to another agent, possibly built by a different vendor or operated by a different organization). Per the A2A protocol homepage: "Build with ADK or any framework, equip with MCP or any tool, communicate with A2A to remote agents, local agents, and humans." Each agent typically uses MCP internally for its own tools while the orchestrator uses A2A to coordinate across agent boundaries.
- **D.** MCP is a deprecated predecessor to A2A; new deployments should use A2A only.

<details>
<summary>Reveal answer</summary>

**Answer: C**

The single most-cited misunderstanding about A2A. The two protocols target different layers: MCP for agent-to-tool, A2A for agent-to-agent. Confusing them means building the wrong abstraction.

📖 Review: [A2A foundations § A2A and MCP are complementary](../../concepts/tools/a2a-foundations.md#a2a-and-mcp-are-complementary-not-competing)
</details>

---

## Question 2

What are the three primitives of the A2A protocol, and where is the Agent Card typically served?

- **A.** Agents, Methods, and Responses; the Agent Card is served at `/api/v1/agent`.
- **B.** Agent Cards (JSON capability descriptors), Tasks (stateful work units with lifecycle), and Transport (JSON-RPC 2.0 over HTTP+SSE). The Agent Card is served at the well-known URL `/.well-known/agent-card.json` — the discovery entry point any A2A client probes to learn what the agent can do, what auth it requires, and where to reach it.
- **C.** Models, Prompts, and Tools; the Agent Card is served at the SDK-specific path.
- **D.** Capabilities, Workflows, and Orchestrators; the Agent Card is published to a central Linux Foundation registry.

<details>
<summary>Reveal answer</summary>

**Answer: B**

The .well-known URL convention follows RFC 8615 — same pattern as OpenID Connect discovery and Let's Encrypt ACME challenges. Any A2A client starts by GET-ing this URL.

📖 Review: [A2A foundations § The three primitives](../../concepts/tools/a2a-foundations.md#the-three-primitives)
</details>

---

## Question 3

How many states are in the A2A Task lifecycle (per the SDK 1.0.3 TaskState enum, ignoring TASK_STATE_UNSPECIFIED), and which are terminal?

- **A.** Three states (started, running, done); all are terminal.
- **B.** Eight states total. Four non-terminal (submitted, working, input-required, auth-required) and four terminal (completed, failed, canceled, rejected). Terminal states are permanent — once a Task reaches one, it cannot transition to another state.
- **C.** Two states (pending, complete).
- **D.** Five states (submitted, in-progress, success, failure, timeout); all transitions are bidirectional.

<details>
<summary>Reveal answer</summary>

**Answer: B**

The terminal four are permanent — no recovery except creating a new Task. The non-terminal four are "alive but waiting" — agent processing, awaiting client input, or awaiting auth.

📖 Review: [A2A foundations § Tasks](../../concepts/tools/a2a-foundations.md#2-tasks)
</details>

---

## Question 4

An A2A client gets back the JSON-RPC error `-32009` with message "A2A version '0.3' is not supported by this handler. Expected version '1.0'." What's the cause and the fix?

- **A.** The server is broken; report an issue to the SDK maintainers.
- **B.** The client is missing the `A2A-Version: 1.0` HTTP header. SDK 1.0.3 servers default to expecting v1.0 messages; if no version header is sent, the server falls back to assuming v0.3 and then refuses because it doesn't support v0.3 by default. The fix is to send the `A2A-Version: 1.0` header explicitly with every request.
- **C.** The agent's Agent Card has the wrong protocolVersion field; modify the card to say "1.0".
- **D.** The client is using `httpx`; switch to `requests` which negotiates the version automatically.

<details>
<summary>Reveal answer</summary>

**Answer: B**

One of the two most common gotchas. Production A2A clients always send `A2A-Version: 1.0`. The `enable_v0_3_compat=True` flag exists for migration scenarios; new deployments should speak v1.0 from the start.

📖 Review: [Lab 28 § Step 8a](../../labs/28-a2a-endpoint-from-scratch/)
</details>

---

## Question 5

When implementing an `AgentExecutor.execute()` method using the SDK 1.0.3 `TaskUpdater`, what's the critical ordering requirement?

- **A.** Call `TaskUpdater.complete()` first to reserve the task ID, then publish artifacts.
- **B.** The execute method must enqueue the initial `Task` object via `event_queue.enqueue_event(task)` BEFORE calling any TaskUpdater lifecycle methods. Calling `updater.submit()` first yields `-32006 INVALID_AGENT_RESPONSE` ("Agent should enqueue Task before TaskStatusUpdateEvent event"). The canonical pattern is: extract message → `new_task_from_user_message(context.message)` → `event_queue.enqueue_event(task)` → create TaskUpdater → call lifecycle methods → `complete()`.
- **C.** The execute method must use synchronous `await asyncio.sleep(0)` between every TaskUpdater call.
- **D.** The order doesn't matter; the SDK reorders events automatically.

<details>
<summary>Reveal answer</summary>

**Answer: B**

The most common AgentExecutor bug. The TaskUpdater publishes status updates to the event queue; the server's event processing requires seeing the initial Task first so it can register the task in the store. Lab 28 Step 3 demonstrates the correct pattern.

📖 Review: [Lab 28 § Step 3](../../labs/28-a2a-endpoint-from-scratch/)
</details>

---

## Question 6

What's the practical implication of A2A SDK 1.0.3 using protobuf-based types instead of Pydantic?

- **A.** Pydantic was deprecated; protobuf is faster and that's the only difference.
- **B.** Tutorials and blog posts dated pre-2026 will show patterns that no longer work. Protobuf types don't have `model_fields`, `model_dump()`, or `.json()`. Instead: `DESCRIPTOR.fields` for introspection, `MessageToDict`/`ParseDict` for serialization, `HasField(name)` for optional-field checks. Field names use `snake_case` on the wire (`message_id`, `task_id`, `protocol_binding`); JSON marshaling adds camelCase only for HTTP responses. Enums are integer-valued with explicit `*_UNSPECIFIED = 0` defaults. Migrating Pydantic-era A2A code to 1.0+ requires non-trivial type-handling changes.
- **C.** Nothing changes; the import paths are identical.
- **D.** Pydantic and protobuf coexist in 1.0.3; you can use either.

<details>
<summary>Reveal answer</summary>

**Answer: B**

The 2026 protobuf shift is a real architectural break. Step 1 of Lab 28 makes the protobuf surface explicit so the rest of the lab can use it correctly. Some tutorials still linked from the SDK README may show `model_json_schema()` calls that throw AttributeError against 1.0.3 types.

📖 Review: [Lab 28 § Step 1](../../labs/28-a2a-endpoint-from-scratch/)
</details>

---

## Question 7

A team is designing a customer-service multi-agent system. The orchestrator agent must coordinate with three internal specialist agents (billing, technical-support, account-management) that all live in the same Python process AND with one external partner agent (legal-review, hosted by a third-party law firm). Which protocols should they use?

- **A.** A2A for all four delegations; the protocol is designed for arbitrary inter-agent coordination.
- **B.** MCP for all four delegations; MCP is faster and simpler than A2A.
- **C.** A2A only for the external partner (legal-review); use in-process supervisor-worker patterns from Path 03 Module 1 for the three internal specialists. A2A adds HTTP + JSON-RPC + Agent Card discovery latency that's pure overhead when all agents share a process. A2A's design payoff is across process and organizational boundaries — the latency is acceptable for the legal-review delegation but wasteful for in-process coordination. MCP doesn't apply because the question is agent-to-agent, not agent-to-tool.
- **D.** Build a custom JSON protocol for the internal three; use A2A for the partner.

<details>
<summary>Reveal answer</summary>

**Answer: C**

Two scope decisions: in-process vs. cross-process, and agent-to-agent vs. agent-to-tool. A2A's payoff scales with the value of HTTP transport — across processes and organizational boundaries. For in-process specialists, the supervisor-worker pattern from Path 03 is sub-millisecond. The internal specialists may use MCP internally for their own tools; the orchestrator doesn't reach those directly.

📖 Review: [A2A foundations § When NOT to use A2A](../../concepts/tools/a2a-foundations.md#when-not-to-use-a2a)
</details>

---

## Question 8

Which of the following correctly describes the A2A ecosystem's evolution from April 2025 to April 2026?

- **A.** A2A remained a Google-only proprietary protocol with three partner organizations.
- **B.** Launched April 9 2025 with 50+ partners; donated to Linux Foundation June 23 2025; IBM's ACP merged into A2A August 2025; v1.0 with Signed Agent Cards landed early 2026; v1.2 (current stable) landed March 2026; one-year mark April 9 2026 with 150+ organizations supporting the standard. Native integrations across Google ADK, LangGraph, CrewAI, LlamaIndex Agents, Semantic Kernel, AutoGen. Production deployments at Salesforce Agentforce, SAP Joule, ServiceNow Now Assist.
- **C.** A2A was abandoned in late 2025 after MCP became the dominant protocol.
- **D.** A2A is governed by a Google-controlled consortium; the Linux Foundation has no role.

<details>
<summary>Reveal answer</summary>

**Answer: B**

Three milestones mattered most. The June 2025 Linux Foundation donation removed vendor-lock-in concerns. The August 2025 IBM ACP merger eliminated the biggest potential competitor. The early-2026 v1.0 with Signed Agent Cards met the enterprise production bar.

📖 Review: [A2A foundations § v1.0 → v1.2 evolution](../../concepts/tools/a2a-foundations.md#v10--v12-evolution-the-first-year)
</details>

---

## After the quiz

Next steps in [Path 04](../../learning-paths/04-tool-protocols-mcp-a2a/):

- **Module 6 — Building an A2A endpoint at production depth** (future batch): Signed Agent Cards, `DatabaseTaskStore` (PostgreSQL), OAuth2 auth, streaming via `SendStreamingMessage`, push notifications, OpenTelemetry tracing
- **Module 7 — MCP + A2A composition** (future batch): the orchestrator pattern with `A2ACardResolver` + `ClientFactory`; agents using MCP for their own tools while using A2A to coordinate
