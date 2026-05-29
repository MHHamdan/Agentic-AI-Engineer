# Lab 29 — A2A endpoint at production depth

> ⏱ 110-130 min · 🟡 Intermediate · Prerequisites: [Lab 28 — A2A endpoint from scratch](../28-a2a-endpoint-from-scratch/) (you'll extend its `hello_agent_server.py` pattern); [Module 6 — A2A endpoint at production depth](../../concepts/tools/a2a-endpoint-production-depth.md).

Extend Lab 28's in-memory A2A server with five production concerns end-to-end: **`DatabaseTaskStore` with SQLite** (task persistence across restart), **JWS-signed Agent Card** (cryptographic identity verification), **API-key middleware** (Starlette `BaseHTTPMiddleware` enforcement), **streaming `SendStreamingMessage`** (Server-Sent Events for progressive task updates), and **OpenTelemetry tracing** (capturing the ~40-span request lifecycle to a JSON-line file you can inspect after the request completes).

Push notifications are discussed in Module 6 but not implemented in Lab 29 (they require a webhook receiver on the client side; that complexity belongs to Module 7's orchestrator-pattern lab).

## What you'll build

```mermaid
flowchart LR
    Dev[You] --> Notebook[Notebook cells]

    Notebook -- "writes" --> ServerFile[production_agent_server.py<br/>~120 lines]
    Notebook -- "writes" --> Card[signed_card.json<br/>JWS-RS256]
    Notebook -- "writes" --> PubKey[pub_key.json<br/>RSA public]

    Notebook -- "subprocess.Popen" --> Server[uvicorn process<br/>:9998<br/>+ DatabaseTaskStore<br/>+ APIKeyMiddleware<br/>+ OTel SimpleSpanProcessor]

    ServerFile --> Server

    Notebook -- "GET .well-known<br/>(public)" --> Server
    Notebook -- "verify signed card<br/>(client-side JWS)" --> PubKey
    Notebook -- "POST without X-API-Key<br/>→ 401" --> Server
    Notebook -- "POST with X-API-Key<br/>+ A2A-Version: 1.0" --> Server

    Server -- "writes SQLite" --> SQLite[(a2a_tasks.db)]
    Server -- "writes spans" --> Spans[a2a_spans.jsonl]

    Notebook -- "kill + respawn" --> Server2[uvicorn process<br/>(restarted)]
    Notebook -- "GetTask after restart" --> Server2
    Server2 -- "reads SQLite" --> SQLite

    Notebook -- "SendStreamingMessage<br/>+ httpx async stream" --> Server2
    Server2 -- "SSE: 4 events" --> Notebook

    Notebook -- "reads spans file" --> Spans

    style Dev fill:#fff4e6
    style Notebook fill:#e6f2ff
    style Server fill:#e6f6ec
    style Server2 fill:#e6f6ec
    style SQLite fill:#f4e6f7
    style Spans fill:#f4e6f7
    style Card fill:#ffe8d1
    style PubKey fill:#ffe8d1
```

The notebook drives two subprocess incarnations of the same server — once to write tasks, once (after killing the first) to read them back. The DB and spans files persist between subprocess lifetimes; the notebook inspects both directly.

After running the lab you'll have:

- A working `production_agent_server.py` (~120 lines) demonstrating all five production concerns wired together with the official SDK 1.0.3
- A `signed_card.json` with a real JWS-RS256 signature attached and verified
- A SQLite database file showing actual persisted tasks
- A JSON-line file of OTel spans captured from a real request — ~40 spans across ~15 unique names per `SendMessage` call
- Practical familiarity with the five most-common production gotchas (schema migration risk, public-vs-private endpoints, RS256 vs deprecated EdDSA, `SimpleSpanProcessor` flushing in subprocess shutdown, streaming SSE consumption with httpx)

## Lab structure — 9 steps

| Step | Topic | Time |
|---|---|---|
| 0 | Environment setup; install `a2a-sdk` + `sqlalchemy[asyncio]` + `aiosqlite` + `joserfc` + `opentelemetry-sdk` | 5 min |
| 1 | Generate an RSA-2048 keypair; sign the Agent Card via JWS-RS256 with `joserfc`; attach the `AgentCardSignature` to the card; write the signed card and public key to disk | 15 min |
| 2 | Author `production_agent_server.py` — wire DatabaseTaskStore (SQLite file-backed), APIKeyMiddleware (Starlette `BaseHTTPMiddleware`), and OTel `SimpleSpanProcessor` exporting to a JSON-line file | 20 min |
| 3 | Spawn the server subprocess; fetch the signed Agent Card; verify the JWS signature with the public key; demonstrate tamper rejection (mutate one byte of the signature, verify fails) | 15 min |
| 4 | Auth — verify 401 without `X-API-Key`; verify 200 with the correct key; send two `SendMessage` requests; capture task IDs | 10 min |
| 5 | Direct SQLite inspection — open the DB file with `sqlite3`, query the `tasks` table, confirm the two tasks from Step 4 are persisted with their state and JSON-encoded contents | 10 min |
| 6 | Restart — terminate the server subprocess; spawn a fresh one; `GetTask` with one of the IDs from Step 4; observe the task is returned (persistence demonstrated across restart) | 10 min |
| 7 | Streaming — call `SendStreamingMessage` via httpx's async stream API; consume the SSE event stream; observe the canonical 4-event sequence (initial Task → `WORKING` status → artifact → `COMPLETED` status) | 15 min |
| 8 | OTel — read the JSON-line spans file the server wrote; group by span name; show the request fanout (`JsonRpcDispatcher.handle_requests` at the top, ~40 child spans across event queue and request handler) | 10 min |

## What you'll watch for (the lessons)

Six concrete observations the lab forces:

1. **`SimpleSpanProcessor` is the right shape for notebook OTel work.** `BatchSpanProcessor` buffers spans and flushes on a timer or shutdown; when you `terminate()` the subprocess, the buffer is lost. `SimpleSpanProcessor` flushes per-span synchronously — slower in production but visible in the notebook even if the server is killed mid-request.
2. **Schema migration is the persistence story's weak point.** The SDK doesn't yet ship Alembic migrations for `DatabaseTaskStore`. Step 5 inspects the SQLite schema directly so you can see what's there; Step 6 confirms cross-restart compatibility within the same SDK version. Cross-version upgrade isn't yet smooth — pin the SDK.
3. **The Agent Card discovery URL stays public even when other endpoints require auth.** Step 3 fetches `.well-known/agent-card.json` without credentials; Step 4 hits the RPC endpoint and gets 401. The signature on the card provides integrity; auth gates the actions, not the discovery. Putting auth on `.well-known/` breaks bootstrapping for every client.
4. **RS256 is the production-safe JWS algorithm.** The bare `EdDSA` algorithm name was deprecated by RFC 9864 (split into `Ed25519` + `Ed448`); `joserfc` raises a `SecurityWarning` for it. RS256 with RSA-2048 has no such warning and is universally supported. Lab 29 uses RS256.
5. **Streaming uses the same `AgentExecutor`**. You don't write a separate "streaming executor" — the SDK reads the card's `streaming: true` capability and routes `SendStreamingMessage` to SSE. The agent code is identical; only the dispatcher behavior changes.
6. **OTel auto-instrumentation captures more than you'd guess.** A single SendMessage call produces ~40 spans across ~15 unique names. The event queue alone emits 25+ spans (enqueue × 12, dequeue × 7, task_done × 6). This is informative but it's also a hint about production cost — `BatchSpanProcessor` with sampling is the production-shape way to handle the volume.

## Repo connections

- [Module 6 — A2A endpoint at production depth](../../concepts/tools/a2a-endpoint-production-depth.md) — the concept page this lab operationalizes
- [Lab 28 — A2A endpoint from scratch](../28-a2a-endpoint-from-scratch/) — the in-memory baseline; same `hello_agent_server.py` shape with `EchoAgent` extended to the production server
- [Pattern 12 — A2A federation](../../patterns/12-a2a-federation.md) — the architecture-level pattern
- [Module 4 — MCP security threat model](../../concepts/tools/mcp-security-threat-model.md) — analogous "what changes when this moves to production" framing

## Anti-scope — what this lab does NOT do

- **No push notifications.** Webhook receiver requires a second HTTP listener inside the notebook; Module 7's orchestrator-pattern lab is the natural home.
- **No OAuth2 token flow.** The Agent Card declares an `apiKey` security scheme; the middleware enforces it. OAuth2 with a real token issuer is a substantial implementation referenced in Module 6 but deferred to Module 7.
- **No PostgreSQL.** SQLite suffices for demonstrating the persistence story. PostgreSQL needs a running service which most learners don't have in their lab environment. The wiring is identical (just change the connection string), and Module 6 explicitly calls out the production recommendation.
- **No PKI / JWKS endpoint.** The public key is shared out-of-band (written to a file the notebook reads). Module 6 covers the production key-distribution patterns; Lab 29's simplification is pedagogically clearer.
- **No client library beyond `httpx`.** The SDK ships `A2ACardResolver` and `Client` classes for client-side use; Module 7's orchestrator lab introduces them. Lab 29 uses raw httpx so you see the wire-level protocol shapes.
- **No multi-agent delegation.** Module 7's territory; this lab focuses on hardening a single endpoint.
- **No production OTel collector.** `SimpleSpanProcessor` writes to a JSON-line file. Production points the same exporter at Jaeger / Honeycomb / Datadog via OTLP.

## What you'll have at the end

A `production_agent_server.py` you can run directly. An understanding of which production concerns are easy (persistence is one line; auth is a 10-line middleware), which are nontrivial (signing requires offline workflow + key distribution), and which are deferred (push notifications + OAuth2 belong to Module 7). The instinct for which OTel processor to choose in which environment. The recognition that the same `AgentExecutor` from Lab 28 still works — what changes is the layers wrapped around it.

## How to run the lab

```bash
# Activate the project venv
source .venv/bin/activate

# Install production dependencies (Python 3.10+)
pip install 'a2a-sdk>=1.0,<2.0' 'sqlalchemy>=2.0' aiosqlite joserfc \
    'opentelemetry-api>=1.20' 'opentelemetry-sdk>=1.20' \
    uvicorn httpx

# Verify
python -c "
import a2a, sqlalchemy, aiosqlite, joserfc, opentelemetry
print('Lab 29 deps OK')
"

# Open the notebook
jupyter lab lab.ipynb
```

The notebook runs cell-by-cell. Steps 3 and 6 each spawn a uvicorn subprocess on port 9998; if that port is in use you'll see a clear error and need to either kill the existing process or change the port in the scratch file. No external API keys, no LLM calls, no running infrastructure required beyond the local Python environment.

## References

- [Module 6 — A2A endpoint at production depth](../../concepts/tools/a2a-endpoint-production-depth.md) — full source list lives there
- [`a2a-sdk` GitHub](https://github.com/a2aproject/a2a-python) — SDK 1.0.3
- [RFC 7515 — JSON Web Signature](https://datatracker.ietf.org/doc/html/rfc7515) — the JWS spec
- [joserfc docs](https://jose.authlib.org/) — the JWS library used in this lab
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/) — the tracing library
