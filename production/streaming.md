# Streaming for production agents

> 🔴 Advanced · ⏱ ~22 min · 🛠 Verified 2026-05-29 · 📍 Read after [`production/deployment.md`](./deployment.md); pairs with [`production/async-and-concurrency.md`](./async-and-concurrency.md) for Module 3 (Latency and streaming) of [Path 07](../learning-paths/07-production-and-safety/)

## What this page is for

Non-streamed agent responses block the user for 3-10 seconds before any output appears. Streamed responses surface the first token in under a second. Per the [machinelearningplus March 2026 streaming tutorial](https://machinelearningplus.com/gen-ai/llm-streaming-python/): "without streaming, the server builds the entire response before sending a single byte; the user stares at a blank screen for 3-10 seconds. With streaming on, the server ships each token the moment it's ready. Perceived latency drops from seconds to milliseconds."

This page covers four production patterns:

1. **SSE token streaming** — the default transport choice for one-way LLM-to-client streaming
2. **Streaming graph state** — multi-step agents that need to surface intermediate progress, not just final tokens
3. **Partial tool outputs** — long-running tool calls that need to stream their own progress
4. **Reverse-proxy and reconnection** — the production wiring that makes streaming actually work behind real infrastructure

The decision rule: stream any user-facing interaction over 2 seconds. Skip streaming for background jobs, sub-second responses, and structured-data-only outputs ([Focused March 2026](https://focused.io/lab/streaming-agent-state-with-langgraph)).

What this page does **not** cover is in section 6 (Anti-scope).

## Pattern 1 — SSE as the default transport

WebSockets, gRPC, and SSE all stream. For LLM-to-client one-way token streaming, SSE wins on operational simplicity per [Procedure Blog April 2026](https://procedure.tech/blogs/sse-for-llms/): "stateless, lightweight, and leaning on the battle-tested simplicity of HTTP."

### Why SSE over WebSockets for token streaming

| Concern | SSE | WebSockets |
|---|---|---|
| Direction | Server → client (one-way) | Bidirectional |
| Transport | Plain HTTP | HTTP upgrade then custom protocol |
| Reverse proxy compatibility | Works with nginx, Cloudflare, CDNs out of the box (with one header) | Requires sticky sessions, connection upgrades, often custom config |
| Auto-reconnect | Built into browser `EventSource` | Application-level implementation |
| Load balancer state | Stateless — any backend can serve a reconnecting client (with shared state store) | Stateful — connection is pinned to one backend |
| Backpressure | Standard HTTP semantics | Application-defined |

The trade-off: SSE is one-way. If the client also needs to send commands mid-stream (interrupt, modify, branch), WebSockets are the cleaner fit. For most chat and agent-progress UX, SSE is sufficient.

### The FastAPI + SSE production pattern

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from anthropic import AsyncAnthropic

app = FastAPI()
client = AsyncAnthropic()

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        try:
            async with client.messages.stream(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                messages=request.messages,
            ) as stream:
                async for event in stream:
                    if event.type == "content_block_delta":
                        yield f"data: {json.dumps({'token': event.delta.text})}\n\n"
                    elif event.type == "message_stop":
                        yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",       # disable nginx response buffering
            "Connection": "keep-alive",
        },
    )
```

Four properties matter:

1. **The async generator pattern** — `async def event_generator()` with `yield` lets FastAPI surface tokens as they arrive without buffering the full response.
2. **`X-Accel-Buffering: no` header** — nginx's default behavior buffers responses; this header disables it on a per-response basis. Without it, the client sees no output until the full response is generated (defeats the purpose of streaming). The [Focused March 2026 LangGraph guide](https://focused.io/lab/streaming-agent-state-with-langgraph) flags this as the most common production streaming bug.
3. **`text/event-stream` MIME type** — triggers the browser's `EventSource` API to handle the stream natively, including auto-reconnect on dropped connections.
4. **The `data: ... \n\n` SSE message format** — SSE requires lines prefixed with `data:` and terminated by a blank line. JSON payloads inside `data:` are the conventional encoding.

### Frontend wiring with EventSource

```javascript
const eventSource = new EventSource('/chat/stream');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.token) {
        appendToken(data.token);
    } else if (data.done) {
        eventSource.close();
    } else if (data.error) {
        showError(data.error);
        eventSource.close();
    }
};

eventSource.onerror = (err) => {
    // Browser auto-reconnects by default; only intervene if you want different behavior
    console.error('SSE error:', err);
};
```

The browser handles reconnect automatically — when the connection drops, it re-issues the request with the `Last-Event-ID` header set to the last received event ID. For this to work as expected, the backend has to support reconnection (Pattern 4).

## Pattern 2 — Streaming graph state

Token streaming covers the chat-UX case. Multi-step agents that take 10-60 seconds need more than per-token streams — they need to surface intermediate state changes (which node is currently running, what intermediate tool calls have completed) so the user sees progress, not just a long pause before tokens arrive.

The LangGraph pattern per [Focused March 2026](https://focused.io/lab/streaming-agent-state-with-langgraph): three stream modes combined.

| Mode | What it streams | Use for |
|---|---|---|
| `updates` | Node-level state transitions | Progress indicators ("Researching...", "Synthesizing...") |
| `custom` | Application-defined events via `get_stream_writer()` | Mid-task progress (e.g., "Retrieved 5/12 sources") |
| `messages` | Token-level LLM output | The final-response token stream |

Combined as `stream_mode=["updates", "custom", "messages"]`:

```python
from langgraph.graph import StateGraph

graph = build_agent_graph()

async def stream_agent(query: str):
    async for stream_type, chunk in graph.astream(
        {"messages": [HumanMessage(content=query)]},
        config={"configurable": {"thread_id": "..."}},
        stream_mode=["updates", "custom", "messages"],
    ):
        if stream_type == "updates":
            yield {"event": "node", "node": list(chunk.keys())[0]}
        elif stream_type == "custom":
            yield {"event": "progress", "data": chunk}
        elif stream_type == "messages":
            msg, _ = chunk
            if hasattr(msg, "content") and msg.content:
                yield {"event": "token", "token": msg.content}
```

The frontend distinguishes by event type — a node transition triggers a UI update to "Step 3 of 5: Synthesis", a custom event surfaces the per-source progress, and tokens flow into the response area.

### The verification gotcha

Per [Focused March 2026](https://focused.io/lab/streaming-agent-state-with-langgraph): "`stream_completeness` verifies that the streaming path produces equivalent output to `invoke()`. This catches bugs where stream chunking drops content, like an SSE serializer silently truncating chunks that exceed a size limit." The test is simple:

```python
def test_stream_completeness():
    invoke_result = graph.invoke({"messages": [...]})
    stream_result = "".join(chunk for chunk in graph.stream(..., stream_mode="messages"))
    assert invoke_result["messages"][-1].content == stream_result
```

Run this in CI for every graph that ships behind streaming. The failure mode it catches — an SSE serializer that truncates messages over a size threshold — is silent in production and only surfaces as customer reports of "the agent stopped mid-sentence."

## Pattern 3 — Partial tool outputs

A research tool that takes 45 seconds to query 8 sources can stream its own progress. The tool returns an async iterator instead of a single result; the agent consumes the iterator and forwards updates through the agent's own stream.

```python
async def deep_search(query: str) -> AsyncIterator[ToolUpdate]:
    """A tool that streams its own progress."""
    sources = await find_sources(query)
    yield ToolUpdate(progress=0, total=len(sources), message="Sources identified")

    results = []
    for i, source in enumerate(sources):
        result = await fetch_and_extract(source)
        results.append(result)
        yield ToolUpdate(
            progress=i + 1,
            total=len(sources),
            message=f"Processed {source.title}",
            partial_data=result,
        )

    yield ToolUpdate(
        progress=len(sources),
        total=len(sources),
        message="Search complete",
        final_data=results,
    )
```

The agent wires the tool's stream into its own custom-event stream:

```python
async def research_node(state: AgentState, writer):
    async for update in deep_search(state["query"]):
        writer({"type": "tool_progress", "tool": "deep_search", "update": update.dict()})
        if update.final_data is not None:
            return {"sources": update.final_data}
```

The frontend sees `tool_progress` events as the long-running tool advances. The user knows the agent is working, not stalled. The pattern matters most for tools with > 5-second tail latency — short tool calls don't need it, and the overhead of the streaming wiring doesn't pay back.

## Pattern 4 — Reverse-proxy compatibility and reconnection

The production gotchas that break streaming behind real infrastructure.

### Reverse-proxy buffering

nginx, Cloudflare, AWS ALB all buffer responses by default. Tokens stream from the agent process; the proxy holds them; the client sees nothing for seconds; then a wall of buffered tokens arrives. The result is worse than non-streaming: the user expected real-time output and got an unexplained pause.

Three fixes per [machinelearningplus March 2026](https://machinelearningplus.com/gen-ai/llm-streaming-python/):

1. **`X-Accel-Buffering: no` response header** — disables nginx buffering per response. The standard fix; works for most setups.
2. **`proxy_buffering off` in nginx config** — global per-location config. Use when the response header isn't sufficient or for catch-all behavior.
3. **Cloudflare's "Disable Buffering" setting** — enable per-route via Workers or the dashboard. Free tier supports it; some legacy plans don't.

### Reconnection and resumability

A streaming client holding an open connection through a deploy, a load balancer rotation, or a 30-second timeout will reconnect. The reconnect lands on a backend process that has no memory of the previous session. Without resumability, the agent restarts from scratch.

Per [Redis April 2026](https://redis.io/blog/streaming-llm-responses/): "a decoupled architecture, where partial output lives in an intermediate store rather than in-memory on a single instance, lets any backend serve a reconnecting client without losing what's already been generated."

The pattern: partial output writes to Redis (or equivalent) keyed by `thread_id`; the backend serving the reconnecting client reads from Redis and resumes from the last completed token.

```python
async def stream_with_resumption(thread_id: str, last_event_id: str | None):
    # 1. Replay buffered output from Redis up to last_event_id
    cached = await redis.lrange(f"stream:{thread_id}", 0, -1)
    for entry in cached:
        yield entry
        if entry.event_id == last_event_id:
            break  # client has everything up to here; switch to live stream

    # 2. Switch to live stream from the agent
    async for chunk in graph.astream(...):
        event_id = generate_event_id()
        formatted = format_sse(chunk, event_id)
        yield formatted
        # 3. Also persist to Redis for future reconnects
        await redis.rpush(f"stream:{thread_id}", formatted)
        await redis.expire(f"stream:{thread_id}", 3600)  # 1-hour TTL
```

The `Last-Event-ID` header sent by the browser's `EventSource` on reconnect drives the replay. Resumability adds infrastructure cost (Redis writes per token); skip it for ephemeral chats; include it for high-stakes workflows where mid-conversation data loss is unacceptable.

### Backpressure on slow clients

A streaming client that can't consume tokens fast enough creates backpressure that flows back through the FastAPI process. Without bounded queues, slow clients can hold open connections and exhaust the process's coroutine pool. The fix:

```python
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    queue = asyncio.Queue(maxsize=50)  # bounded — backpressure when full

    async def producer():
        async for chunk in agent_stream(request):
            try:
                await asyncio.wait_for(queue.put(chunk), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Client too slow; dropping connection")
                break
        await queue.put(None)  # sentinel for completion

    async def consumer():
        while (item := await queue.get()) is not None:
            yield item

    asyncio.create_task(producer())
    return StreamingResponse(consumer(), media_type="text/event-stream")
```

The bounded queue size (50) and per-put timeout (10s) put an upper bound on how much memory a slow client can hold. The producer task signals completion via the `None` sentinel.

## Operational discipline

Five practices for production streaming:

1. **Test stream completeness in CI** per Pattern 2's `test_stream_completeness` check. Catches the SSE-serializer-truncation class of silent bug.
2. **Monitor time-to-first-token (TTFT) as a top-level SLO**. Per [Redis April 2026](https://redis.io/blog/streaming-llm-responses/), TTFT is the metric users actually feel. Target p95 < 1 second; alert on > 2 seconds. Tokens-per-second is secondary.
3. **Per-route streaming-vs-buffered decision**. Not every endpoint should stream. Background-job endpoints, structured-data endpoints, and short-response endpoints don't benefit. Streaming everywhere adds infrastructure complexity for no UX gain.
4. **Reconnect-safety tests**. Disconnect the client mid-stream in staging; reconnect; confirm the agent resumes correctly. Manual rehearsal monthly; automated chaos test ideal.
5. **Per-client connection-time-budget tracking**. Sum of open SSE connection time across all clients should fit inside your FastAPI worker concurrency budget. If clients hold connections for 30s and you have 100 worker slots, you cap at ~3 connections/second sustainably. Above that, increase workers or shorten the connection lifecycle.

## Anti-scope (what this page does not cover)

- **Choosing between SSE, WebSockets, gRPC for bidirectional streaming.** This page covers the one-way LLM-to-client case where SSE wins. Bidirectional cases (the client modifies the stream mid-flight) are their own decision.
- **Stream-mode internals of every framework.** LangGraph's `updates`/`custom`/`messages` modes are covered; CrewAI, AutoGen, and OpenAI Agents SDK each have their own streaming surfaces with the same SSE wiring downstream.
- **Frontend frameworks beyond `EventSource`.** React patterns, Vue patterns, Svelte patterns all wrap the same browser API. The backend pattern is the same regardless.
- **Voice / audio streaming.** Real-time audio agents have additional latency budgets (TTFT < 500ms) and audio-encoding concerns that don't apply to text streaming.
- **Edge-deployed streaming** (Cloudflare Workers, Vercel Edge). The patterns work but with platform-specific config differences; the [`production/deployment.md`](./deployment.md) Shape 3 (serverless) page treats this surface.

## References

**SSE and streaming patterns (2026)**:
- [Procedure Blog (April 2026), *The Streaming Backbone of LLMs: Why SSE Still Wins in 2026*](https://procedure.tech/blogs/sse-for-llms/) — SSE vs WebSockets vs gRPC; operational simplicity argument
- [machinelearningplus (March 2026), *LLM Streaming Tutorial: SSE in Python Step-by-Step*](https://machinelearningplus.com/gen-ai/llm-streaming-python/) — FastAPI + SSE pattern with backpressure handling
- [Codastra (December 2025), *FastAPI Server-Sent Events for LLM Streaming*](https://medium.com/@2nick2patel2/fastapi-server-sent-events-for-llm-streaming-smooth-tokens-low-latency-1b211c94cff5) — production architecture and gotchas
- [Hadiyolworld (January 2026), *FastAPI + SSE for LLM Tokens*](https://medium.com/@hadiyolworld007/fastapi-sse-for-llm-tokens-smooth-streaming-without-websockets-001ead4b5e53) — async generator pattern; backpressure-aware yielding
- [Notes (January 2026), *Streaming Intelligence: How SSE Revolutionize Real-Time LLM APIs*](https://notes.suhaib.in/docs/tech/llms/streaming-intelligence-how-server-sent-events-revolutionize-real-time-llm-apis/) — incremental token generation framing

**LangGraph streaming patterns (2026)**:
- [Focused (March 2026), *Streaming LangGraph Agents: Real-Time Progress, Token Streaming, and Production Patterns*](https://focused.io/lab/streaming-agent-state-with-langgraph) — three-mode pattern; `stream_completeness` CI check; `X-Accel-Buffering` gotcha

**Reconnection and resumability (2026)**:
- [Redis (April 2026), *Streaming LLM Responses: Make Your AI App Feel Fast*](https://redis.io/blog/streaming-llm-responses/) — decoupled architecture; reconnection across backend instances; intermediate-store pattern

**FastAPI production deployment (2025-2026)**:
- [Zignuts, *Deploying LLMs with FastAPI: Production Guide*](https://www.zignuts.com/blog/fastapi-deploy-llms-guide) — async I/O architecture; streaming alongside metrics tracking

**Repo cross-references**:
- [`production/deployment.md`](./deployment.md) — the four deployment shapes; Shape 1 (FastAPI + Postgres) is the default for the streaming patterns here
- [`production/async-and-concurrency.md`](./async-and-concurrency.md) — the parallel-execution half of Module 3; streams compose with parallel tool calls
- [`production/checklist.md`](./checklist.md) — Layer 5 (Observability) defines the TTFT SLO surface
- [Path 06 Module 4 (Tracing and observability)](../learning-paths/06-evaluation-observability/README.md) — per-token, per-node tracing that streaming wiring feeds into
- [Path 03 v3 Project 2 (Research pipeline)](../learning-paths/03-multi-agent-systems/projects/02-research-pipeline-with-deep-research.md) — production example where multi-step streaming is load-bearing
