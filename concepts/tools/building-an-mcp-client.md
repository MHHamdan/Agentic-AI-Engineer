# Building an MCP client

> ⏱ ~13 min · 🟡 Intermediate · Prerequisites: [MCP foundations](./mcp-foundations.md), [Building an MCP server](./building-an-mcp-server.md). Helpful: [Pattern 01 — Single-agent tool use](../../patterns/01-single-agent-tool-use.md) — the loop the client integrates into.

The previous module shipped the server side. This module is the consuming side. By the end you'll be able to read any MCP-client code in 2026 and explain what it does, and you'll know which production failure modes to defend against.

The shape of the trade: a client is *cheap* to write (the protocol does the heavy lifting) and *expensive* to write defensively (network, schema drift, auth expiry, missing capabilities, all the production realities the local-function world hides). Most of this page is about the defensive side — that's where the work is.

## What a client actually does

Four jobs:

1. **Connect** to one or more MCP servers and complete the protocol handshake
2. **Discover** the available tools, resources, and prompts on each server
3. **Translate** between the LLM's native function-calling format and MCP's `tools/call` method
4. **Defend** against the failure modes that come with cross-process tool access

The first two are mostly framework code; FastMCP 3.x handles them via `Client("path-or-url")` and `await client.list_tools()`. The third is a 10-line schema converter. The fourth is the work that decides whether your client survives production.

## The minimum-viable client

```python
from fastmcp import Client
import asyncio

async def run_once():
    async with Client("notes_server.py") as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        result = await client.call_tool(
            "create_note",
            {"title": "Q3-plan", "body": "Ship Module 3 in Batch 46."},
        )
        return result.data

asyncio.run(run_once())
```

That's a working client. The `Client("notes_server.py")` argument is overloaded: a local file path spawns the server as a stdio subprocess; an `http://` or `https://` URL connects over Streamable HTTP; a `dict` object connects in-memory for testing. The context manager handles initialize/shutdown.

If your goal is connecting one agent to one server, that's the whole code. Everything else on this page is the operational scaffolding around it.

## The schema-translation layer

Your LLM speaks function-calling (Anthropic's `tools` parameter, OpenAI's tool format, Gemini's function declarations). MCP servers speak JSON-RPC with their own `tools/list` schema shape. The client converts between them every loop iteration.

FastMCP's `client.list_tools()` returns a list of `Tool` objects with `.name`, `.description`, `.inputSchema` fields. The conversion to Anthropic's format:

```python
def to_anthropic_tool(mcp_tool) -> dict:
    """Translate an MCP tool definition to Anthropic's tool format."""
    return {
        "name": mcp_tool.name,
        "description": mcp_tool.description or "",
        "input_schema": mcp_tool.inputSchema or {"type": "object", "properties": {}},
    }
```

For OpenAI:

```python
def to_openai_tool(mcp_tool) -> dict:
    """Translate an MCP tool definition to OpenAI's tool format."""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": mcp_tool.inputSchema or {"type": "object", "properties": {}},
        },
    }
```

Both are mechanical. The non-obvious part: **tool name collisions across servers**. If you connect to a filesystem server (`read_file`, `write_file`) and a Google Drive server (`read_file`, `write_file`), the LLM sees two `read_file` tools and picks unpredictably. The production fix is server-prefixed names:

```python
def prefix_tool_name(server_name: str, mcp_tool) -> str:
    """Prefix the tool name with the server identifier to avoid collisions."""
    return f"{server_name}__{mcp_tool.name}"  # e.g., "fs__read_file"
```

Then route by prefix when the LLM calls the tool:

```python
server_name, _, tool_name = called_tool_name.partition("__")
result = await clients[server_name].call_tool(tool_name, arguments)
```

This is the kind of detail that doesn't surface in tutorials and bites every team building their second multi-server client.

## The agent-loop integration

The client integrates into a standard agent loop. The shape is identical to [Pattern 01 — Single-agent tool use](../../patterns/01-single-agent-tool-use.md) — only the tool-execution line changes:

```python
async def run_agent_with_mcp(user_prompt: str, mcp_client) -> str:
    """A Pattern 01 agent talking to one MCP server."""
    mcp_tools = await mcp_client.list_tools()
    tool_schemas = [to_anthropic_tool(t) for t in mcp_tools]

    messages = [{"role": "user", "content": user_prompt}]

    for step in range(MAX_STEPS):
        response = llm_call(messages=messages, tools=tool_schemas)

        if response.stop_reason == "end_turn":
            return response.content[0].text

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                # The MCP-specific line: tool execution goes through MCP
                result = await mcp_client.call_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result.data),
                })
        messages.append({"role": "user", "content": tool_results})

    return "[max steps reached]"
```

That's the architectural relationship Pattern 11 (MCP integration) describes: the loop above the tool layer is identical to Pattern 01; only the tool-execution line moves from in-process to MCP.

## Multi-server orchestration

Real clients talk to multiple servers. Each server gets its own `Client` instance; the agent loop aggregates tool schemas from all of them:

```python
class MultiServerMcpClient:
    """Client connecting to N MCP servers, with collision-free routing."""

    def __init__(self, servers: dict[str, str]):
        """
        Args:
            servers: Mapping of short_name -> server path or URL.
                e.g., {"fs": "filesystem_server.py", "gh": "https://github.com/mcp"}
        """
        self.server_paths = servers
        self.clients: dict[str, Client] = {}

    async def __aenter__(self):
        for name, path in self.server_paths.items():
            client = Client(path)
            await client.__aenter__()
            self.clients[name] = client
        return self

    async def __aexit__(self, *args):
        for client in self.clients.values():
            await client.__aexit__(*args)

    async def list_all_tools(self) -> list[dict]:
        """Aggregate tool schemas from all servers, prefixed by server name."""
        all_tools = []
        for server_name, client in self.clients.items():
            tools = await client.list_tools()
            for t in tools:
                schema = to_anthropic_tool(t)
                schema["name"] = f"{server_name}__{t.name}"
                all_tools.append(schema)
        return all_tools

    async def call_tool(self, prefixed_name: str, arguments: dict):
        """Route a prefixed tool call to the right server."""
        server_name, _, tool_name = prefixed_name.partition("__")
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")
        return await self.clients[server_name].call_tool(tool_name, arguments)
```

Two architectural choices this exposes:

1. **Connection lifetime.** Long-lived clients (open at process start, close at shutdown) work for steady-state agents. Per-request clients (open per agent invocation) work for serverless or short-lived contexts. The tradeoff is connection-establishment latency vs. resource pinning — for stdio, each connection spawns a subprocess; for HTTP, each connection is a TCP+TLS handshake.

2. **Tool-budget enforcement.** With N servers, the LLM sees `sum(server_tool_counts)` tools. Past ~10 total tools, [`concepts/tools/tool-selection.md`](./tool-selection.md)'s selection-failure modes apply. Production deployments scope which servers/tools each agent sees — not by hiding from the LLM, but by curating the toolset per task. This is where MCP's coming Server Cards spec (2026 H2 roadmap) will help: servers declare capability tiers and clients filter.

## Discovery: how clients find servers

In Batch 43's Module 2 the server was launched manually as a subprocess. Production isn't that simple — agents need to *discover* available servers without hardcoded paths. Three patterns, in order of maturity:

**1. Configuration file.** Local hardcoded list. Claude Desktop's `claude_desktop_config.json` and Cursor's `mcp.json` are this. Works for personal use, breaks for fleets.

**2. The MCP Registry** at [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io). Anthropic's central index of public servers per the [WorkOS March 2026 MCP overview](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026). 27,432+ servers aggregated as of May 2026 per [MCPfinder](https://mcpfinder.dev/). The registry uses a `server.json` standard codified in late 2025 per [Glama October 2025](https://glama.ai/blog/2025-10-26-the-model-context-protocol-registry-standardizing-server-discovery-in-a-decentralized-ecosystem); clients fetch the catalog via REST, filter by capability, then connect to actual server endpoints. The registry stores metadata; the servers run elsewhere.

**3. MCP Server Cards** (2026 H2 roadmap). Standardized metadata published at `/.well-known/mcp-server-card.json` per the [WorkOS MCP roadmap](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026) — analogous to A2A's Agent Cards. A client can probe a known URL and discover what the server offers without hitting the registry. Less centralized; useful for internal-only servers.

For enterprise deployments, the picture is more layered: **MCP gateways** like Kong's MCP Registry, TrueFoundry's Virtual MCP Server, or the agentic-community gateway-registry aggregate multiple upstream servers behind a single endpoint, adding governance (which agents can call which tools), observability, and access control. They turn the "fleet of servers" problem into a "single endpoint per environment" problem.

For Lab 26, we connect to local servers by path — registry integration is a future Module 4+ topic.

## Production failure modes

Five failure modes that bite production MCP clients. The corresponding defenses:

**Server-side schema drift.** A server you depend on adds a required field to one of its tools; your LLM doesn't know; calls start failing. Defense: cache tool schemas with a TTL (5 minutes is reasonable); detect changes via `notifications/tools/list_changed`; refresh on any schema-mismatch error.

**Tool call timeout.** A tool that usually returns in 200ms hangs for 30s due to a transient downstream issue. Defense: every `call_tool` gets a per-tool timeout (default 10s; longer for known-slow tools); on timeout, return a structured error to the LLM rather than blocking the loop.

```python
async def call_tool_with_timeout(client, name, args, timeout=10.0):
    try:
        return await asyncio.wait_for(
            client.call_tool(name, args),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return {"status": "error", "error": "tool_timeout", "tool": name}
```

**Auth token expiry.** Long-running clients use bearer tokens that eventually expire; the next call returns 401. Defense: catch auth errors, refresh the token (OAuth refresh flow for OAuth 2.1 servers; re-fetch from secret store otherwise), retry the call once.

**Server unavailable.** The server's process crashed, or its host is unreachable. Defense: circuit-breaker pattern — after N consecutive failures (default 5), mark the server as unavailable for a cool-off period (default 60s) and report tool calls to that server as `server_unavailable` to the LLM. Don't let one broken server take down the whole client.

**Response payload too large.** A search tool returns 50K rows; the response blows up the LLM's context. Defense: response-size limits per tool (`max_response_chars` enforced client-side); on overflow, truncate with an explicit `[response truncated; N rows omitted]` marker and surface to the LLM as a structured signal it can act on.

These five aren't exhaustive but they cover the failure modes that hit production deployments within the first month of running. The [tech-insider.org February 2026 client patterns guide](https://www.kdnuggets.com/fastmcp-the-pythonic-way-to-build-mcp-servers-and-clients) covers the basic implementation; the defensive scaffolding above is what you add for production.

## Token-bloat: the FastMCP 3.1 code-mode escape hatch

[Apigene April 2026](https://apigene.ai/blog/fastmcp) reports tool schemas consuming 15,000+ tokens before the agent starts reasoning — the #1 production pain point. Connecting an agent to 5 MCP servers with 10 tools each means the LLM sees 50 tool definitions in every request.

FastMCP 3.1's **code mode** (introduced February 2026) addresses this: instead of sending all tool definitions upfront, the client exposes a small meta-tool surface (`list_servers`, `list_tools_on_server`, `call_tool_on_server`) that the LLM uses to *discover and call tools dynamically*. The agent fetches a tool's schema only when it decides to call it. Token cost drops from 15K to 2-3K per request per [Apigene](https://apigene.ai/blog/fastmcp); Cloudflare's similar "Code Mode" pattern reports 98%+ token savings per the [WorkOS 2026 MCP overview](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026).

The trade is one extra LLM call per tool invocation (discovery, then execution) in exchange for not paying the upfront tool-schema cost on every request. For agents that touch many servers but use few tools per task, code mode is a large net win. For agents with 5-10 carefully-curated tools, eager loading is still cheaper.

This pattern is Path 04 Module 4 territory — token-bloat is a *security* concern too (the attacker-controlled tool descriptions in arxiv:2601.10955 grow with eager loading) — but worth flagging here as the architectural choice it is.

## What's next

Now that you have the client mental model:

- 🧪 [Lab 26 — MCP client from scratch](../../labs/26-mcp-client-from-scratch/) — build a client end-to-end against Lab 25's notes server; add a second public server; implement the production defenses; integrate with a real LLM.
- 🧠 [MCP client and discovery quiz](../../quizzes/foundations/mcp-client-and-discovery.md) — 8 questions covering this page + Lab 26.
- 📖 Future [`concepts/tools/`] pages — Module 4 (MCP security threat model) covers what production deployments must defend against beyond the five failure modes above.

## References

**FastMCP and SDK**:
- [FastMCP at gofastmcp.com](https://gofastmcp.com/getting-started/welcome) — official documentation
- [github.com/prefecthq/fastmcp](https://github.com/prefecthq/fastmcp) — source; 4M+ daily downloads as of March 2026 per [Apigene](https://apigene.ai/blog/fastmcp)
- [The MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — what FastMCP wraps

**Discovery and registries**:
- [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) — the official central index
- [Glama (October 2025)](https://glama.ai/blog/2025-10-26-the-model-context-protocol-registry-standardizing-server-discovery-in-a-decentralized-ecosystem) — the `server.json` standardization
- [TrueFoundry (April 2026)](https://www.truefoundry.com/blog/best-mcp-registries) — comparison of registries for production
- [TrueFoundry (May 2026)](https://www.truefoundry.com/blog/centralized-mcp-registry-architecture) — registry architecture; multi-tenancy
- [MCPfinder (May 2026)](https://mcpfinder.dev/) — 27,432+ aggregated servers across Official Registry, Glama, and Smithery

**2026 production guidance**:
- KDnuggets (February 2026), *[FastMCP: The Pythonic Way to Build MCP Servers and Clients](https://www.kdnuggets.com/fastmcp-the-pythonic-way-to-build-mcp-servers-and-clients)* — client error-handling patterns
- WorkOS (March 2026), *[Everything your team needs to know about MCP in 2026](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026)* — Server Cards roadmap, session-scoped authorization, code mode
- Apigene (April 2026), *[FastMCP 3.0: Build MCP Servers in Python, Fast](https://apigene.ai/blog/fastmcp)* — FastMCP 3.1 code mode (15K → 2-3K tokens); 4M+ daily downloads
- tech-insider.org (April 2026), *[Build an MCP Server in Python: FastMCP Guide 2026](https://tech-insider.org/how-to-build-mcp-server-python-fastmcp-tutorial/)* — 70%+ of Python MCP servers use FastMCP

**Adjacent repo content**:
- 📖 [MCP foundations](./mcp-foundations.md) — Module 1 (protocol architecture)
- 📖 [Building an MCP server](./building-an-mcp-server.md) — Module 2 (the other side of the boundary)
- 🏛 [Pattern 11 — MCP integration](../../patterns/11-mcp-integration.md) — the architecture-level view
- 🏛 [Pattern 01 — Single-agent tool use](../../patterns/01-single-agent-tool-use.md) — the agent loop the client integrates into
- 📖 [`concepts/tools/tool-selection.md`](./tool-selection.md) — the failure modes that govern multi-server tool surfaces
- 🛣 [Path 04 README](../../learning-paths/04-tool-protocols-mcp-a2a/) — Module 3 lives here
