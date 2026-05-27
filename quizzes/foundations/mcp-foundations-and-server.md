---
quiz_id: foundations-mcp-foundations-and-server
title: "MCP foundations and server: protocol architecture, FastMCP, schema inference, transports"
source:
  - concepts/tools/mcp-foundations.md
  - concepts/tools/building-an-mcp-server.md
  - labs/25-mcp-server-from-scratch/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "Your team has 4 agents that all need to read from a shared PostgreSQL database. Currently each agent has its own bespoke `psycopg`-based wrapper. Why does adopting MCP for the database access likely pay off?"
    options:
      A: "MCP is faster than direct psycopg connections, so the latency improves."
      B: "MCP collapses the N×M integration problem (each agent × each tool) to N+M (each agent speaks MCP once, the database exposes MCP once). The integration cost moves from per-pair to per-side."
      C: "MCP automatically adds row-level security to the database."
      D: "MCP eliminates the need for an LLM in the agent loop."
    answer: B
    explanation: |
      The N×M-to-N+M collapse is the foundational rationale for MCP per
      the foundations page. Four agents × one database is still only
      five integrations to maintain, but the pattern scales poorly:
      add a second database and you need 8 wrappers, add a third agent
      and you need 12. MCP makes the cost linear in (agents + tools)
      not (agents × tools). Option A is wrong — MCP adds a JSON-RPC
      indirection layer, so it's marginally *slower* than direct
      psycopg, not faster. Option C is wrong — MCP doesn't add database
      security; that's a server-implementation responsibility. Option D
      is wrong — MCP is orthogonal to the LLM; it sits between the
      agent and its tools.
    review:
      page: concepts/tools/mcp-foundations.md
      section: "Why MCP exists — the N×M problem"

  - id: q2
    difficulty: easy
    question: "Which of these is correctly classified as an MCP **resource** (not a tool or prompt)?"
    options:
      A: "`send_email(to, subject, body)` — sends an email via the SMTP server."
      B: "`weekly_report.md` — a static document the agent's host wants to inject into every conversation as background context."
      C: "`/summarize` — a slash command the user picks to summarize the current document."
      D: "`create_calendar_event(title, time, attendees)` — creates a calendar event."
    answer: B
    explanation: |
      Resources are **host-controlled, read-only** data — addressable
      by URI, fetched by the host without LLM invocation. A static
      document the host wants in every conversation is exactly that
      shape. Option A is a tool (mutating action, LLM-initiated).
      Option C is a prompt (user-initiated template). Option D is also
      a tool (mutating, LLM-initiated). The "who initiates" axis is the
      key distinguisher: LLM → tool; host → resource; user → prompt.
    review:
      page: concepts/tools/mcp-foundations.md
      section: "The three primitives — tools, resources, prompts"

  - id: q3
    difficulty: easy
    question: "You're deciding between stdio and Streamable HTTP transport for a new MCP server. The server will run on a remote machine and serve multiple desktop clients across an organization. Which transport is correct?"
    options:
      A: "stdio — it's simpler and has no network configuration."
      B: "Streamable HTTP — it's the production default since the 2026 MCP spec; stdio requires the host and server to run as parent and subprocess on the same machine."
      C: "Either works the same way; the choice is purely aesthetic."
      D: "Use the deprecated HTTP+SSE transport for backward compatibility."
    answer: B
    explanation: |
      stdio launches the server as a subprocess of the host and pipes
      messages through stdin/stdout — by construction, the server runs
      on the same machine as the host. Cross-machine access requires
      Streamable HTTP, which is the production-default transport since
      the 2026 spec. Option A is wrong about stdio's capabilities.
      Option C ignores the cross-machine constraint. Option D names the
      deprecated transport — `mcp run --sse` is no longer recommended.
    review:
      page: concepts/tools/mcp-foundations.md
      section: "The transports — stdio vs Streamable HTTP"

  - id: q4
    difficulty: medium
    question: "Which decorator chain creates an MCP **tool** in FastMCP 3.0 that takes a single string parameter `title` and a constrained `priority` parameter that must be 1, 2, or 3?"
    options:
      A: |
        `@mcp.tool()`
        `def set_priority(title: str, priority: int) -> dict: ...`
      B: |
        `@mcp.resource()`
        `def set_priority(title: str, priority: Literal[1, 2, 3]) -> dict: ...`
      C: |
        `@mcp.tool()`
        `def set_priority(title: str, priority: Literal[1, 2, 3]) -> dict: ...`
      D: |
        `@mcp.prompt()`
        `def set_priority(title: str, priority: int) -> dict: ...`
    answer: C
    explanation: |
      Two things have to be right: the decorator and the type. The
      decorator is `@mcp.tool()` because the question specifies it's a
      tool. The type for the constrained parameter is
      `Literal[1, 2, 3]` — FastMCP translates `Literal` into a JSON
      Schema `enum` constraint, so the LLM can only generate 1, 2, or
      3. Option A uses the right decorator but `int` is too
      permissive — the LLM could pass any integer. Option B uses the
      wrong decorator (`@mcp.resource()`). Option D uses the wrong
      decorator (`@mcp.prompt()`).
    review:
      page: concepts/tools/building-an-mcp-server.md
      section: "Type hints become JSON Schema — the inference rules"

  - id: q5
    difficulty: medium
    question: "You've written an MCP tool with the docstring `\"creates\"`. The LLM keeps calling it instead of the correct tool. What's the root cause?"
    options:
      A: "The MCP protocol doesn't support short docstrings; you must use at least 20 words."
      B: "FastMCP rejects tools with docstrings under 10 characters."
      C: "The LLM uses the tool description (derived from the docstring) to decide which tool to call. A vague description like `\"creates\"` doesn't give the LLM signal to differentiate this tool from others — tool selection becomes nearly random. The fix is to write a descriptive docstring."
      D: "MCP servers have an LLM bias toward the first tool registered; rename the tool to start with a later letter."
    answer: C
    explanation: |
      This is the most common MCP failure mode and it's the same
      failure mode as poorly-named tools in single-agent design
      (covered in `concepts/tools/tool-selection.md`). The LLM picks
      tools based on names and descriptions; vague descriptions
      produce vague selections. Option A and Option B are made-up
      protocol restrictions; FastMCP places no length requirement on
      docstrings. Option D is nonsense; tool selection order has
      nothing to do with alphabetical position.
    review:
      page: concepts/tools/building-an-mcp-server.md
      section: "Common mistakes"

  - id: q6
    difficulty: medium
    question: "Your `send_email` MCP tool is being called twice when the network blips — the same email gets delivered to the user twice. The retry behavior is at the **client** layer, outside your server. What's the right server-side fix?"
    options:
      A: "Disable retries at the client; tell users not to retry."
      B: "Add an `idempotency_key` parameter to `send_email`. On each call, check if you've already processed that key; if so, return the same result without re-sending. This makes the tool replay-safe regardless of client retry behavior."
      C: "Wrap the tool body in a try/except and silently swallow duplicate-send errors."
      D: "Increase the server's response timeout so the client never retries."
    answer: B
    explanation: |
      Idempotency keys are the canonical fix for side-effectful tools
      that can be retried. The client (or network) generates a unique
      key per intended call; the server checks the key and skips
      duplicate processing. This is independent of retry behavior — the
      tool is safe to call N times with the same key and produces the
      same effect once. The pattern is the same one used in
      Path 03 Pattern 5 (Retry policies) for in-process tools. Option
      A doesn't scale — retries happen for legitimate reasons (network
      blips). Option C masks the failure mode without fixing it.
      Option D is a band-aid that doesn't address the root cause.
    review:
      page: concepts/tools/building-an-mcp-server.md
      section: "Common mistakes"

  - id: q7
    difficulty: hard
    question: "You're reviewing an MCP server's `tools/list` response in the MCP Inspector. One of the tools has the description `\"Tool for note operations.\"` and a parameter `operation: str`. The same server has separate tools `create_note`, `update_note`, `delete_note`, each with focused descriptions. Why is the catch-all tool a problem?"
    options:
      A: "It's not a problem — fewer tools is always better for LLM context."
      B: "FastMCP doesn't allow tools whose names start with 'tool'."
      C: "The catch-all tool dilutes tool selection signal: the LLM has to disambiguate between the focused tools and the catch-all, and the catch-all's description doesn't help disambiguation. The result is the LLM picks the catch-all when it shouldn't. The fix is to remove the catch-all and let the focused tools own their respective verbs."
      D: "The catch-all tool causes JSON Schema validation errors in clients."
    answer: C
    explanation: |
      The tool-selection failure mode here is the inverse of vague
      docstrings. Even with good focused descriptions on the
      `create_note` / `update_note` / `delete_note` tools, an
      additional catch-all that says it does "note operations"
      creates ambiguity at selection time. The LLM has to reason
      about whether to use the specific or the general tool, and the
      general tool's description doesn't help. Removing the catch-all
      (or rewriting it to point users at the focused tools) restores
      signal. Option A misstates the relationship — focused tools
      are usually clearer than catch-alls, even at higher tool count.
      Option B and D are made-up restrictions.
    review:
      page: concepts/tools/tool-selection.md
      section: "Tool selection failure modes"

  - id: q8
    difficulty: hard
    question: "Your team is deciding whether the `summarize_note(title)` capability should be an MCP **tool** or an MCP **prompt**. The LLM generates the summary; the input is the note body; the user occasionally wants to invoke 'summarize' on the current document. Which is the right primitive?"
    options:
      A: "Tool — because the LLM has to do work (the summarization)."
      B: "Prompt — because the user invokes it (as a slash command), it's a parameterized template the user picks from a menu, and the LLM generation happens in the host's regular LLM call after the prompt is substituted. Tools are LLM-initiated; prompts are user-initiated."
      C: "Resource — because the summary is a piece of data."
      D: "Either works equivalently."
    answer: B
    explanation: |
      The 'who initiates' axis decides this. The user picks
      `/summarize_note title="Q3-plan"` from the slash-command menu;
      the host fetches the prompt template, substitutes the title,
      and sends the result to the LLM as a regular message. The LLM
      does the summarization in its normal generation step, not as
      a tool call. Option A confuses "the LLM does the work" with
      "the LLM initiates the action" — those are different axes.
      Option C is wrong because resources are read-only addressable
      data, not generators of derived content. Option D ignores the
      semantic distinction; the host UI presents prompts and tools
      differently to the user.
    review:
      page: concepts/tools/mcp-foundations.md
      section: "The three primitives — tools, resources, prompts"
---

# MCP foundations and server quiz

> ⏱ ~10 min · Source pages: [MCP foundations](../../concepts/tools/mcp-foundations.md), [Building an MCP server](../../concepts/tools/building-an-mcp-server.md), [Lab 25](../../labs/25-mcp-server-from-scratch/). Pass at 6/8.

Eight single-select questions on the Path 04 Module 1+2 material. The questions cover protocol architecture (Q1-Q3), FastMCP and schema inference (Q4), tool-selection failure modes (Q5, Q7), production patterns (Q6), and the three-primitive distinction (Q2, Q8).

If you've read both concept pages and completed Lab 25, you should clear 6/8 comfortably. The two hard questions (Q7, Q8) reward thinking about *who initiates* and *how the LLM disambiguates among tools* — both come up in real production work.

Pass mark is 6/8. If you fall below, the "Review" link on each question points back to the specific concept-page section to re-read.

---

## Question 1

You're working on a team with 4 agents that all need to read from a shared PostgreSQL database. Currently each agent has its own bespoke `psycopg`-based wrapper. Why does adopting MCP for the database access likely pay off?

- **A.** MCP is faster than direct `psycopg` connections, so the latency improves.
- **B.** MCP collapses the N×M integration problem (each agent × each tool) to N+M (each agent speaks MCP once, the database exposes MCP once). The integration cost moves from per-pair to per-side.
- **C.** MCP automatically adds row-level security to the database.
- **D.** MCP eliminates the need for an LLM in the agent loop.

<details>
<summary>Reveal answer</summary>

**Answer: B**

The N×M-to-N+M collapse is the foundational rationale for MCP per the foundations page. Four agents × one database is still only five integrations to maintain, but the pattern scales poorly: add a second database and you need 8 wrappers, add a third agent and you need 12. MCP makes the cost linear in (agents + tools) not (agents × tools). Option A is wrong — MCP adds a JSON-RPC indirection layer, so it's marginally *slower* than direct `psycopg`, not faster. Option C is wrong — MCP doesn't add database security; that's a server-implementation responsibility. Option D is wrong — MCP is orthogonal to the LLM; it sits between the agent and its tools.

📖 Review: [MCP foundations § Why MCP exists — the N×M problem](../../concepts/tools/mcp-foundations.md#why-mcp-exists--the-nm-problem)
</details>

---

## Question 2

Which of these is correctly classified as an MCP **resource** (not a tool or prompt)?

- **A.** `send_email(to, subject, body)` — sends an email via the SMTP server.
- **B.** `weekly_report.md` — a static document the agent's host wants to inject into every conversation as background context.
- **C.** `/summarize` — a slash command the user picks to summarize the current document.
- **D.** `create_calendar_event(title, time, attendees)` — creates a calendar event.

<details>
<summary>Reveal answer</summary>

**Answer: B**

Resources are **host-controlled, read-only** data — addressable by URI, fetched by the host without LLM invocation. A static document the host wants in every conversation is exactly that shape. Option A is a tool (mutating action, LLM-initiated). Option C is a prompt (user-initiated template). Option D is also a tool (mutating, LLM-initiated). The "who initiates" axis is the key distinguisher: LLM → tool; host → resource; user → prompt.

📖 Review: [MCP foundations § The three primitives](../../concepts/tools/mcp-foundations.md#the-three-primitives--tools-resources-prompts)
</details>

---

## Question 3

You're deciding between stdio and Streamable HTTP transport for a new MCP server. The server will run on a remote machine and serve multiple desktop clients across an organization. Which transport is correct?

- **A.** stdio — it's simpler and has no network configuration.
- **B.** Streamable HTTP — it's the production default since the 2026 MCP spec; stdio requires the host and server to run as parent and subprocess on the same machine.
- **C.** Either works the same way; the choice is purely aesthetic.
- **D.** Use the deprecated HTTP+SSE transport for backward compatibility.

<details>
<summary>Reveal answer</summary>

**Answer: B**

stdio launches the server as a subprocess of the host and pipes messages through stdin/stdout — by construction, the server runs on the same machine as the host. Cross-machine access requires Streamable HTTP, which is the production-default transport since the 2026 spec. Option A is wrong about stdio's capabilities. Option C ignores the cross-machine constraint. Option D names the deprecated transport — `mcp run --sse` is no longer recommended.

📖 Review: [MCP foundations § The transports](../../concepts/tools/mcp-foundations.md#the-transports--stdio-vs-streamable-http)
</details>

---

## Question 4

Which decorator chain creates an MCP **tool** in FastMCP 3.0 that takes a single string parameter `title` and a constrained `priority` parameter that must be 1, 2, or 3?

- **A.** `@mcp.tool()` / `def set_priority(title: str, priority: int) -> dict: ...`
- **B.** `@mcp.resource()` / `def set_priority(title: str, priority: Literal[1, 2, 3]) -> dict: ...`
- **C.** `@mcp.tool()` / `def set_priority(title: str, priority: Literal[1, 2, 3]) -> dict: ...`
- **D.** `@mcp.prompt()` / `def set_priority(title: str, priority: int) -> dict: ...`

<details>
<summary>Reveal answer</summary>

**Answer: C**

Two things have to be right: the decorator and the type. The decorator is `@mcp.tool()` because the question specifies it's a tool. The type for the constrained parameter is `Literal[1, 2, 3]` — FastMCP translates `Literal` into a JSON Schema `enum` constraint, so the LLM can only generate 1, 2, or 3. Option A uses the right decorator but `int` is too permissive — the LLM could pass any integer. Option B uses the wrong decorator (`@mcp.resource()`). Option D uses the wrong decorator (`@mcp.prompt()`).

📖 Review: [Building an MCP server § Type hints become JSON Schema](../../concepts/tools/building-an-mcp-server.md#type-hints-become-json-schema--the-inference-rules)
</details>

---

## Question 5

You've written an MCP tool with the docstring `"creates"`. The LLM keeps calling it instead of the correct tool. What's the root cause?

- **A.** The MCP protocol doesn't support short docstrings; you must use at least 20 words.
- **B.** FastMCP rejects tools with docstrings under 10 characters.
- **C.** The LLM uses the tool description (derived from the docstring) to decide which tool to call. A vague description like `"creates"` doesn't give the LLM signal to differentiate this tool from others — tool selection becomes nearly random. The fix is to write a descriptive docstring.
- **D.** MCP servers have an LLM bias toward the first tool registered; rename the tool to start with a later letter.

<details>
<summary>Reveal answer</summary>

**Answer: C**

This is the most common MCP failure mode and it's the same failure mode as poorly-named tools in single-agent design (covered in [`concepts/tools/tool-selection.md`](../../concepts/tools/tool-selection.md)). The LLM picks tools based on names and descriptions; vague descriptions produce vague selections. Option A and Option B are made-up protocol restrictions; FastMCP places no length requirement on docstrings. Option D is nonsense; tool selection order has nothing to do with alphabetical position.

📖 Review: [Building an MCP server § Common mistakes](../../concepts/tools/building-an-mcp-server.md#common-mistakes)
</details>

---

## Question 6

Your `send_email` MCP tool is being called twice when the network blips — the same email gets delivered to the user twice. The retry behavior is at the **client** layer, outside your server. What's the right server-side fix?

- **A.** Disable retries at the client; tell users not to retry.
- **B.** Add an `idempotency_key` parameter to `send_email`. On each call, check if you've already processed that key; if so, return the same result without re-sending. This makes the tool replay-safe regardless of client retry behavior.
- **C.** Wrap the tool body in a try/except and silently swallow duplicate-send errors.
- **D.** Increase the server's response timeout so the client never retries.

<details>
<summary>Reveal answer</summary>

**Answer: B**

Idempotency keys are the canonical fix for side-effectful tools that can be retried. The client (or network) generates a unique key per intended call; the server checks the key and skips duplicate processing. This is independent of retry behavior — the tool is safe to call N times with the same key and produces the same effect once. The pattern is the same one used in [Path 03 Pattern 5 (Retry policies)](../../learning-paths/03-multi-agent-systems/patterns/05-retry-policies.md) for in-process tools. Option A doesn't scale — retries happen for legitimate reasons (network blips). Option C masks the failure mode without fixing it. Option D is a band-aid that doesn't address the root cause.

📖 Review: [Building an MCP server § Common mistakes](../../concepts/tools/building-an-mcp-server.md#common-mistakes)
</details>

---

## Question 7

You're reviewing an MCP server's `tools/list` response in the MCP Inspector. One of the tools has the description `"Tool for note operations."` and a parameter `operation: str`. The same server has separate tools `create_note`, `update_note`, `delete_note`, each with focused descriptions. Why is the catch-all tool a problem?

- **A.** It's not a problem — fewer tools is always better for LLM context.
- **B.** FastMCP doesn't allow tools whose names start with 'tool'.
- **C.** The catch-all tool dilutes tool selection signal: the LLM has to disambiguate between the focused tools and the catch-all, and the catch-all's description doesn't help disambiguation. The result is the LLM picks the catch-all when it shouldn't. The fix is to remove the catch-all and let the focused tools own their respective verbs.
- **D.** The catch-all tool causes JSON Schema validation errors in clients.

<details>
<summary>Reveal answer</summary>

**Answer: C**

The tool-selection failure mode here is the inverse of vague docstrings. Even with good focused descriptions on the `create_note` / `update_note` / `delete_note` tools, an additional catch-all that says it does "note operations" creates ambiguity at selection time. The LLM has to reason about whether to use the specific or the general tool, and the general tool's description doesn't help. Removing the catch-all (or rewriting it to point users at the focused tools) restores signal. Option A misstates the relationship — focused tools are usually clearer than catch-alls, even at higher tool count. Option B and D are made-up restrictions.

📖 Review: [`concepts/tools/tool-selection.md`](../../concepts/tools/tool-selection.md)
</details>

---

## Question 8

Your team is deciding whether the `summarize_note(title)` capability should be an MCP **tool** or an MCP **prompt**. The LLM generates the summary; the input is the note body; the user occasionally wants to invoke 'summarize' on the current document. Which is the right primitive?

- **A.** Tool — because the LLM has to do work (the summarization).
- **B.** Prompt — because the user invokes it (as a slash command), it's a parameterized template the user picks from a menu, and the LLM generation happens in the host's regular LLM call after the prompt is substituted. Tools are LLM-initiated; prompts are user-initiated.
- **C.** Resource — because the summary is a piece of data.
- **D.** Either works equivalently.

<details>
<summary>Reveal answer</summary>

**Answer: B**

The 'who initiates' axis decides this. The user picks `/summarize_note title="Q3-plan"` from the slash-command menu; the host fetches the prompt template, substitutes the title, and sends the result to the LLM as a regular message. The LLM does the summarization in its normal generation step, not as a tool call. Option A confuses "the LLM does the work" with "the LLM initiates the action" — those are different axes. Option C is wrong because resources are read-only addressable data, not generators of derived content. Option D ignores the semantic distinction; the host UI presents prompts and tools differently to the user.

📖 Review: [MCP foundations § The three primitives](../../concepts/tools/mcp-foundations.md#the-three-primitives--tools-resources-prompts)
</details>

---

## After the quiz

Next steps in [Path 04](../../learning-paths/04-tool-protocols-mcp-a2a/):

- **Module 3 — Building an MCP client** (future batch): consuming external servers from your agent; tool discovery; error handling
- **Module 4 — MCP security and the tool-layer threat model** (future batch): the arxiv:2601.10955 resource-amplification attack; safe-default tool exposure; rate limits and idempotency at the server
- **Modules 5-7 — A2A** (future batches): the agent-to-agent half of Path 04

If you found the tool-selection questions challenging, also see the [Lab 02 (tool design and selection)](../../labs/02-tool-design-and-selection/) concept work — the same patterns govern both single-agent tools and MCP tools.
