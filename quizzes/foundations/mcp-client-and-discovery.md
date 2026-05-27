---
quiz_id: foundations-mcp-client-and-discovery
title: "MCP client and discovery: building defensive clients, multi-server orchestration, MCP Registry, code mode"
source:
  - concepts/tools/building-an-mcp-client.md
  - labs/26-mcp-client-from-scratch/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "You're connecting an agent to three MCP servers: a filesystem server, a Google Drive server, and a database server. All three expose a tool called `search`. What happens when the LLM tries to call `search`, and what's the fix?"
    options:
      A: "Nothing — MCP resolves tool-name collisions automatically based on server connection order."
      B: "The LLM sees three tools with identical names and picks unpredictably; the fix is to prefix tool names with the server identifier (e.g., `fs__search`, `gdrive__search`, `db__search`) at the client and route by prefix when invoking."
      C: "FastMCP raises an exception at `list_tools()` time and refuses to connect."
      D: "The client must pick one server to be authoritative and disable `search` on the other two."
    answer: B
    explanation: |
      Tool-name collisions across servers are a real production issue
      that's invisible until you have multi-server clients. MCP itself
      doesn't resolve them — both servers legitimately own their own
      tool namespace. The client-side fix is server-prefixing: build
      a stable prefix per server connection, prepend it to every tool
      name shown to the LLM, and route by parsing the prefix on
      invocation. Option A is wrong (no automatic resolution).
      Option C is wrong (FastMCP doesn't refuse; it lets the client
      handle naming). Option D is the wrong shape — you'd lose
      capabilities you actually want.
    review:
      page: concepts/tools/building-an-mcp-client.md
      section: "The schema-translation layer"

  - id: q2
    difficulty: easy
    question: "Which best describes the relationship between Pattern 01 (single-agent tool use) and an MCP-using agent loop?"
    options:
      A: "MCP requires a fundamentally different loop shape; Pattern 01 doesn't apply when tools are out-of-process."
      B: "MCP and Pattern 01 are unrelated — Pattern 01 is for tools, MCP is for resources."
      C: "The MCP agent loop is structurally identical to Pattern 01 — only the tool-execution line changes from in-process invocation to `await mcp_client.call_tool(...)`. The loop above the tool boundary doesn't move."
      D: "Pattern 01 is a deprecated approach; modern agents use MCP-specific loop patterns documented in Module 3."
    answer: C
    explanation: |
      The architectural symmetry between Pattern 01 and Pattern 11
      (MCP integration) is the central point of both pages. The loop —
      send messages, get response, check stop_reason, execute tool
      calls, append results, repeat — is identical. Only the
      tool-execution line moves from in-process invocation
      to `await mcp_client.call_tool(...)`. This symmetry is what
      lets you upgrade a Pattern 01 agent to use MCP tools without
      rewriting the agent.
    review:
      page: concepts/tools/building-an-mcp-client.md
      section: "The agent-loop integration"

  - id: q3
    difficulty: easy
    question: "Your MCP client connects to a server. A tool call that usually returns in 200ms hangs for 30 seconds due to a downstream issue. The agent loop is now blocked. What's the operational defense?"
    options:
      A: "Increase the LLM's max_tokens so it has time to wait for the tool."
      B: "Wrap every `call_tool` invocation in `asyncio.wait_for` with a per-tool timeout (default 10s); on timeout, return a structured `{\"status\": \"error\", \"error\": \"tool_timeout\"}` to the LLM rather than blocking the loop."
      C: "Disable retries on the MCP server so it always returns quickly."
      D: "Use a synchronous client instead of an async one to avoid event-loop issues."
    answer: B
    explanation: |
      Per-tool timeouts are the canonical defense. The pattern: every
      `call_tool` invocation is wrapped in `asyncio.wait_for(...)` with
      a default timeout (10s is a reasonable starting point; some
      tools warrant longer). On timeout, the client returns a
      structured error envelope to the LLM, which can then decide to
      retry, try a different tool, or give up. The agent loop never
      blocks waiting for an unresponsive server. Options A, C, D
      misunderstand the failure shape — the LLM's token budget,
      server retry behavior, and sync-vs-async are unrelated to the
      "tool hangs forever" problem.
    review:
      page: concepts/tools/building-an-mcp-client.md
      section: "Production failure modes"

  - id: q4
    difficulty: medium
    question: "Your client connects to 5 MCP servers, each exposing 10 tools. The tool-schema layer is sending 6,000+ tokens to the LLM on every request before the agent even starts reasoning. What's the FastMCP 3.1-era architectural choice for reducing this cost?"
    options:
      A: "There's no fix — token cost is fixed by the LLM provider; tolerate it."
      B: "FastMCP 3.1's code mode: instead of sending all tool definitions upfront, expose a small meta-tool surface (`list_servers`, `list_tools_on_server`, `call_tool_on_server`); the LLM discovers and calls tools dynamically; token cost drops from 15K to 2-3K per request per Apigene April 2026. Tradeoff: one extra LLM call per tool invocation (discovery then execution) in exchange for not paying upfront cost."
      C: "Use OpenAI instead of Anthropic — OpenAI's function-calling format compresses better."
      D: "Compress the JSON schemas with gzip before sending."
    answer: B
    explanation: |
      Token bloat is the #1 production pain point with multi-server
      MCP clients per Apigene's April 2026 measurements. FastMCP 3.1's
      code mode (and Cloudflare's similar "Code Mode") addresses it by
      shifting from eager schema loading to dynamic discovery. The
      tradeoff is real: code mode adds latency for tool discovery on
      first use; eager loading is still cheaper for small,
      curated-toolset agents. For agents that touch many servers but
      use few tools per task, code mode is a large net win. Option A
      is defeatist. Option C confuses the format with the bloat
      (the bloat is in the schemas themselves, not the wire format).
      Option D doesn't help — the model has to see the JSON, not
      the bytes.
    review:
      page: concepts/tools/building-an-mcp-client.md
      section: "Token-bloat: the FastMCP 3.1 code-mode escape hatch"

  - id: q5
    difficulty: medium
    question: "Your MCP client uses bearer-token auth against a remote Streamable HTTP server. After 2 hours of running, every tool call starts returning 401 Unauthorized. What's the right defense?"
    options:
      A: "Restart the agent process to get a fresh client."
      B: "Use stdio transport instead of HTTP to skip authentication."
      C: "Catch 401 errors, refresh the token (OAuth refresh flow for OAuth 2.1 servers; re-fetch from a secret store otherwise), then retry the original call once. If the retry also returns 401, bubble the error up."
      D: "Hardcode a longer-lived token that never expires."
    answer: C
    explanation: |
      Token expiry is one of the five production failure modes Module
      3 documents. The pattern: catch the 401, attempt a token refresh,
      retry the call once. For OAuth 2.1 servers, the refresh flow is
      standardized (RFC 6749). For internal services using static
      bearer tokens, "refresh" means re-fetching from your secret
      store. Critical: retry exactly once. If the retry also fails,
      the token-refresh logic itself is broken — bubble the error up.
      Option A burns the whole agent state. Option B is wrong (stdio
      isn't an option for cross-machine deployments). Option D is a
      security anti-pattern; long-lived tokens are exactly what
      shouldn't be hardcoded.
    review:
      page: concepts/tools/building-an-mcp-client.md
      section: "Production failure modes"

  - id: q6
    difficulty: medium
    question: "Your client depends on a remote MCP server that adds a required field to one of its tools without coordinating with you. Your LLM keeps calling the tool with the old schema; calls now fail. What's the defense?"
    options:
      A: "Hardcode the tool schema in the client code so server changes don't affect you."
      B: "Cache the `list_tools()` result with a short TTL (5 minutes is reasonable); listen for `notifications/tools/list_changed` from the server; refresh the cache on any schema-mismatch error. The cache should never live longer than the slowest tool update cycle you can tolerate."
      C: "Pin the server to a specific version forever and never accept updates."
      D: "Add the missing field to your client-side schema manually each time and redeploy."
    answer: B
    explanation: |
      Schema drift is one of the five production failure modes. The
      defense pattern combines a TTL cache (so you re-discover
      schemas periodically) with push-based invalidation (so you
      respond to `notifications/tools/list_changed`) and reactive
      refresh (so a schema-mismatch error triggers an immediate
      re-fetch). Option A defeats the protocol's design — the whole
      point of `tools/list` is that schemas come from the server.
      Option C is operationally impossible for any server you don't
      own. Option D is the manual labor the cache pattern automates.
    review:
      page: concepts/tools/building-an-mcp-client.md
      section: "Production failure modes"

  - id: q7
    difficulty: hard
    question: "You're designing for a fleet of agents that each need to connect to ~3 MCP servers chosen at runtime from a pool of 80 candidates. Which discovery architecture fits best?"
    options:
      A: "Hardcode the 80 server paths in each agent's config file and let it pick at runtime."
      B: "Use the MCP Registry (`registry.modelcontextprotocol.io`) or an enterprise MCP gateway (Kong / TrueFoundry Virtual MCP Server / agentic-community gateway-registry): the registry stores server metadata via the `server.json` standard; agents query the registry to discover candidates filtered by capability and trust signals; the registry returns endpoints; agents connect directly to those endpoints. Combines centralized metadata with decentralized consumption."
      C: "Build a custom REST API for each agent to call to fetch server addresses."
      D: "Have one canonical agent that connects to all 80 servers and have other agents delegate through it."
    answer: B
    explanation: |
      The MCP Registry pattern is the production answer for fleet
      deployments. Per Glama October 2025, the registry uses a
      `server.json` standard for codified definitions; per TrueFoundry
      April 2026, enterprise gateways add governance (which agents can
      call which tools), observability, and access control on top.
      The key architectural insight per WorkOS March 2026 is
      "centralization of metadata authorship and version control,
      paired with the decentralization of consumption and filtering" —
      one canonical source of metadata; many independent agents
      filtering by their needs. Option A doesn't scale beyond a few
      agents. Option C reinvents the wheel — `server.json` already
      exists. Option D creates a single point of failure and routes
      every tool call through one agent.
    review:
      page: concepts/tools/building-an-mcp-client.md
      section: "Discovery: how clients find servers"

  - id: q8
    difficulty: hard
    question: "Three MCP servers feed your agent. One server starts returning 500 errors for every call due to a downstream outage. Your other two servers are healthy. Without intervention, what happens to the agent and what's the right defense?"
    options:
      A: "Nothing — async event loops handle this transparently; the failing server's calls just return errors and the agent continues."
      B: "All three servers' calls start timing out because they share the same client connection pool."
      C: "Every tool call to the failing server hits the per-tool timeout (10s by default), so the agent loop spends 10s per failed call before continuing. The defense is a circuit-breaker: track consecutive failures per server; after N (default 5), mark the server as unavailable for a cool-off period (default 60s) and return `server_unavailable` immediately for subsequent calls. The other two servers continue working."
      D: "FastMCP's built-in circuit-breaker handles this automatically — no client-side defense needed."
    answer: C
    explanation: |
      The circuit-breaker pattern is one of the five production
      failure modes Module 3 documents. Without it, every call to the
      failing server pays the full timeout cost (10s default). With
      a circuit-breaker tracking consecutive failures per server,
      after 5 consecutive failures the server is marked unavailable;
      subsequent calls return `server_unavailable` immediately;
      after a 60s cool-off the breaker tries again. The remaining
      healthy servers serve the agent's other tool needs. Option A
      is partly right (calls do return errors) but ignores the latency
      compounding. Option B is wrong (per-server clients have
      independent connections). Option D is wrong (FastMCP doesn't
      ship a circuit-breaker; it's a client-side defense pattern).
    review:
      page: concepts/tools/building-an-mcp-client.md
      section: "Production failure modes"
---

# MCP client and discovery quiz

> ⏱ ~10 min · Source pages: [Building an MCP client](../../concepts/tools/building-an-mcp-client.md), [Lab 26](../../labs/26-mcp-client-from-scratch/). Pass at 6/8.

Eight single-select questions on Path 04 Module 3 material. Coverage: client architecture (Q1, Q2), production defenses (Q3, Q5, Q6, Q8), token economics (Q4), discovery architecture (Q7).

The two hard questions (Q7, Q8) reward thinking about what changes between *one server in a lab* and *N servers in a fleet under failure*. Both come up in real production work.

Pass mark is 6/8. If you fall below, the "Review" link on each question points back to the specific concept-page section to re-read.

---

## Question 1

You're connecting an agent to three MCP servers: a filesystem server, a Google Drive server, and a database server. All three expose a tool called `search`. What happens when the LLM tries to call `search`, and what's the fix?

- **A.** Nothing — MCP resolves tool-name collisions automatically based on server connection order.
- **B.** The LLM sees three tools with identical names and picks unpredictably; the fix is to prefix tool names with the server identifier (e.g., `fs__search`, `gdrive__search`, `db__search`) at the client and route by prefix when invoking.
- **C.** FastMCP raises an exception at `list_tools()` time and refuses to connect.
- **D.** The client must pick one server to be authoritative and disable `search` on the other two.

<details>
<summary>Reveal answer</summary>

**Answer: B**

Tool-name collisions across servers are a real production issue that's invisible until you have multi-server clients. MCP itself doesn't resolve them — both servers legitimately own their own tool namespace. The client-side fix is server-prefixing: build a stable prefix per server connection, prepend it to every tool name shown to the LLM, and route by parsing the prefix on invocation. Options A, C, D misstate FastMCP's behavior or propose the wrong shape of fix.

📖 Review: [Building an MCP client § The schema-translation layer](../../concepts/tools/building-an-mcp-client.md#the-schema-translation-layer)
</details>

---

## Question 2

Which best describes the relationship between Pattern 01 (single-agent tool use) and an MCP-using agent loop?

- **A.** MCP requires a fundamentally different loop shape; Pattern 01 doesn't apply when tools are out-of-process.
- **B.** MCP and Pattern 01 are unrelated — Pattern 01 is for tools, MCP is for resources.
- **C.** The MCP agent loop is structurally identical to Pattern 01 — only the tool-execution line changes from in-process invocation to `await mcp_client.call_tool(...)`. The loop above the tool boundary doesn't move.
- **D.** Pattern 01 is a deprecated approach; modern agents use MCP-specific loop patterns documented in Module 3.

<details>
<summary>Reveal answer</summary>

**Answer: C**

The architectural symmetry between Pattern 01 and Pattern 11 (MCP integration) is the central point of both pages. The loop — send messages, get response, check stop_reason, execute tool calls, append results, repeat — is identical. Only the tool-execution line moves from in-process invocation to `await mcp_client.call_tool(...)`. This symmetry is what lets you upgrade a Pattern 01 agent to use MCP tools without rewriting the agent.

📖 Review: [Building an MCP client § The agent-loop integration](../../concepts/tools/building-an-mcp-client.md#the-agent-loop-integration)
</details>

---

## Question 3

Your MCP client connects to a server. A tool call that usually returns in 200ms hangs for 30 seconds due to a downstream issue. The agent loop is now blocked. What's the operational defense?

- **A.** Increase the LLM's max_tokens so it has time to wait for the tool.
- **B.** Wrap every `call_tool` invocation in `asyncio.wait_for` with a per-tool timeout (default 10s); on timeout, return a structured `{"status": "error", "error": "tool_timeout"}` to the LLM rather than blocking the loop.
- **C.** Disable retries on the MCP server so it always returns quickly.
- **D.** Use a synchronous client instead of an async one to avoid event-loop issues.

<details>
<summary>Reveal answer</summary>

**Answer: B**

Per-tool timeouts are the canonical defense. Every `call_tool` invocation is wrapped in `asyncio.wait_for(...)` with a default timeout (10s is a reasonable starting point; some tools warrant longer). On timeout, the client returns a structured error envelope to the LLM, which can then decide to retry, try a different tool, or give up. The agent loop never blocks waiting for an unresponsive server.

📖 Review: [Building an MCP client § Production failure modes](../../concepts/tools/building-an-mcp-client.md#production-failure-modes)
</details>

---

## Question 4

Your client connects to 5 MCP servers, each exposing 10 tools. The tool-schema layer is sending 6,000+ tokens to the LLM on every request before the agent even starts reasoning. What's the FastMCP 3.1-era architectural choice for reducing this cost?

- **A.** There's no fix — token cost is fixed by the LLM provider; tolerate it.
- **B.** FastMCP 3.1's code mode: instead of sending all tool definitions upfront, expose a small meta-tool surface (`list_servers`, `list_tools_on_server`, `call_tool_on_server`); the LLM discovers and calls tools dynamically; token cost drops from 15K to 2-3K per request per Apigene April 2026. Tradeoff: one extra LLM call per tool invocation (discovery then execution) in exchange for not paying upfront cost.
- **C.** Use OpenAI instead of Anthropic — OpenAI's function-calling format compresses better.
- **D.** Compress the JSON schemas with gzip before sending.

<details>
<summary>Reveal answer</summary>

**Answer: B**

Token bloat is the #1 production pain point with multi-server MCP clients per Apigene April 2026. FastMCP 3.1's code mode addresses it by shifting from eager schema loading to dynamic discovery. The tradeoff is real: code mode adds latency for tool discovery on first use; eager loading is still cheaper for small, curated-toolset agents. For agents that touch many servers but use few tools per task, code mode is a large net win.

📖 Review: [Building an MCP client § Token-bloat](../../concepts/tools/building-an-mcp-client.md#token-bloat-the-fastmcp-31-code-mode-escape-hatch)
</details>

---

## Question 5

Your MCP client uses bearer-token auth against a remote Streamable HTTP server. After 2 hours of running, every tool call starts returning 401 Unauthorized. What's the right defense?

- **A.** Restart the agent process to get a fresh client.
- **B.** Use stdio transport instead of HTTP to skip authentication.
- **C.** Catch 401 errors, refresh the token (OAuth refresh flow for OAuth 2.1 servers; re-fetch from a secret store otherwise), then retry the original call once. If the retry also returns 401, bubble the error up.
- **D.** Hardcode a longer-lived token that never expires.

<details>
<summary>Reveal answer</summary>

**Answer: C**

Token expiry is one of the five production failure modes. The pattern: catch the 401, attempt a token refresh, retry the call once. For OAuth 2.1 servers, the refresh flow is standardized (RFC 6749). For internal services using static bearer tokens, "refresh" means re-fetching from your secret store. Critical: retry exactly once. If the retry also fails, the token-refresh logic itself is broken — bubble the error up.

📖 Review: [Building an MCP client § Production failure modes](../../concepts/tools/building-an-mcp-client.md#production-failure-modes)
</details>

---

## Question 6

Your client depends on a remote MCP server that adds a required field to one of its tools without coordinating with you. Your LLM keeps calling the tool with the old schema; calls now fail. What's the defense?

- **A.** Hardcode the tool schema in the client code so server changes don't affect you.
- **B.** Cache the `list_tools()` result with a short TTL (5 minutes is reasonable); listen for `notifications/tools/list_changed` from the server; refresh the cache on any schema-mismatch error. The cache should never live longer than the slowest tool update cycle you can tolerate.
- **C.** Pin the server to a specific version forever and never accept updates.
- **D.** Add the missing field to your client-side schema manually each time and redeploy.

<details>
<summary>Reveal answer</summary>

**Answer: B**

Schema drift is one of the five production failure modes. The defense combines a TTL cache (so you re-discover schemas periodically) with push-based invalidation (so you respond to `notifications/tools/list_changed`) and reactive refresh (so a schema-mismatch error triggers an immediate re-fetch).

📖 Review: [Building an MCP client § Production failure modes](../../concepts/tools/building-an-mcp-client.md#production-failure-modes)
</details>

---

## Question 7

You're designing for a fleet of agents that each need to connect to ~3 MCP servers chosen at runtime from a pool of 80 candidates. Which discovery architecture fits best?

- **A.** Hardcode the 80 server paths in each agent's config file and let it pick at runtime.
- **B.** Use the MCP Registry (`registry.modelcontextprotocol.io`) or an enterprise MCP gateway (Kong / TrueFoundry Virtual MCP Server / agentic-community gateway-registry): the registry stores server metadata via the `server.json` standard; agents query the registry to discover candidates filtered by capability and trust signals; the registry returns endpoints; agents connect directly to those endpoints. Combines centralized metadata with decentralized consumption.
- **C.** Build a custom REST API for each agent to call to fetch server addresses.
- **D.** Have one canonical agent that connects to all 80 servers and have other agents delegate through it.

<details>
<summary>Reveal answer</summary>

**Answer: B**

The MCP Registry pattern is the production answer for fleet deployments. The key architectural insight per WorkOS March 2026 is "centralization of metadata authorship and version control, paired with the decentralization of consumption and filtering" — one canonical source of metadata; many independent agents filtering by their needs.

📖 Review: [Building an MCP client § Discovery: how clients find servers](../../concepts/tools/building-an-mcp-client.md#discovery-how-clients-find-servers)
</details>

---

## Question 8

Three MCP servers feed your agent. One server starts returning 500 errors for every call due to a downstream outage. Your other two servers are healthy. Without intervention, what happens to the agent and what's the right defense?

- **A.** Nothing — async event loops handle this transparently; the failing server's calls just return errors and the agent continues.
- **B.** All three servers' calls start timing out because they share the same client connection pool.
- **C.** Every tool call to the failing server hits the per-tool timeout (10s by default), so the agent loop spends 10s per failed call before continuing. The defense is a circuit-breaker: track consecutive failures per server; after N (default 5), mark the server as unavailable for a cool-off period (default 60s) and return `server_unavailable` immediately for subsequent calls. The other two servers continue working.
- **D.** FastMCP's built-in circuit-breaker handles this automatically — no client-side defense needed.

<details>
<summary>Reveal answer</summary>

**Answer: C**

The circuit-breaker pattern is one of the five production failure modes. Without it, every call to the failing server pays the full timeout cost. With a circuit-breaker tracking consecutive failures per server, after 5 consecutive failures the server is marked unavailable; subsequent calls return `server_unavailable` immediately; after a 60s cool-off the breaker tries again. The remaining healthy servers serve the agent's other tool needs.

📖 Review: [Building an MCP client § Production failure modes](../../concepts/tools/building-an-mcp-client.md#production-failure-modes)
</details>

---

## After the quiz

Next steps in [Path 04](../../learning-paths/04-tool-protocols-mcp-a2a/):

- **Module 4 — MCP security threat model** (future batch): the arxiv:2601.10955 resource-amplification attack walked through; tool-description injection mitigations
- **Modules 5-7 — A2A** (future batches): the agent-to-agent half of Path 04

If you found the defensive-client questions challenging, also see [Pattern 11 — MCP integration](../../patterns/11-mcp-integration.md) for the architecture-level framing of why the failure modes shape this way.
