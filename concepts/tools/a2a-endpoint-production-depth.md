# A2A endpoint at production depth

> ⏱ ~15 min · 🟡 Fast-changing protocol (v1.2 stable as of March 2026; SDK 1.0.3 protobuf-based; production patterns continue to firm up). Prerequisites: [Module 5 — A2A foundations](./a2a-foundations.md) for the three primitives and the SDK surface; [Lab 28](../../labs/28-a2a-endpoint-from-scratch/) for the `hello_agent_server.py` shape this module extends. Helpful: [Module 4 — MCP security threat model](./mcp-security-threat-model.md) for the analogous "what changes when this moves to production" framing.

Lab 28 built the minimum viable A2A endpoint: in-memory task store, unsigned Agent Card, no auth, no streaming, no observability. That endpoint is enough to learn the protocol shape; it's not enough to deploy. Module 6 walks through what changes when the same `hello-agent` becomes a production deployment.

Six production concerns, in roughly the order you'll encounter them:

1. **Persistence** — survive process restarts; replace `InMemoryTaskStore` with `DatabaseTaskStore`
2. **Identity** — let calling agents verify the card was issued by the agent's domain owner; sign the Agent Card with JWS
3. **Authentication** — require credentials on the RPC endpoint; declare the scheme in the card
4. **Streaming** — emit progress events for long-running tasks; switch to `SendStreamingMessage` + SSE
5. **Push notifications** — let the server tell the client when a long task completes asynchronously
6. **Observability** — distributed tracing across A2A boundaries; OpenTelemetry integration

Each concern has a "minimum viable production" answer in the SDK; this module walks through what that answer looks like, what it costs, and where it breaks. Lab 29 implements four of the six end-to-end (persistence, signed cards, auth, streaming, observability); push notifications are conceptually covered here but deferred to Module 7 since they require a webhook receiver on the client side.

## 1. Persistence — `DatabaseTaskStore`

`InMemoryTaskStore` is fine for development and for tasks whose total lifetime is shorter than your server process. For anything else, tasks must outlive the process.

The SDK 1.0.3 ships `DatabaseTaskStore` — a SQLAlchemy-async-engine-based store. Per [AI Workflow Lab March 2026](https://aiworkflowlab.dev/article/how-to-build-a2a-agents-python-production-guide): "`InMemoryTaskStore` is fine for development but loses all state on restart. For production, pick a persistent backend." The three supported backends:

- **PostgreSQL** — the recommended production default; full ACID compliance; battle-tested for multi-instance deployments
- **SQLite** — appropriate for single-node deployments, development, and CI environments; ships in Python stdlib; trivial setup
- **MySQL** — viable if your existing infrastructure already runs MySQL

Wire it up like this:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from a2a.server.tasks import DatabaseTaskStore

# Development: SQLite file-backed
engine = create_async_engine("sqlite+aiosqlite:///./a2a_tasks.db")

# Production: PostgreSQL
# engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")

store = DatabaseTaskStore(engine=engine)
await store.initialize()  # creates the 'tasks' table on first run
```

Then pass `store` to `DefaultRequestHandler` exactly as you passed `InMemoryTaskStore` in Lab 28. The protocol-facing API is identical; what changed is the durability story.

**The migration gotcha that bites in production**: the `tasks` table schema isn't yet stable across SDK versions. When the spec moved from v0.3 to v1.0, the table layout changed; an upgrade required either dropping the table (losing tasks) or running a manual ALTER. The SDK doesn't yet ship Alembic migrations — that's an [open issue tracking](https://github.com/a2aproject/a2a-python) discussed in the project's roadmap. For now, treat the schema as append-mostly and pin your SDK version.

**Concurrent writes**: SQLAlchemy's async engine handles the connection pooling; multi-instance deployments work because the database is the source of truth. PostgreSQL's MVCC handles concurrent task updates cleanly; SQLite serializes writes, which is fine until you scale past a single instance.

## 2. Identity — Signed Agent Cards

Module 5 introduced Signed Agent Cards as the v1.0 enterprise-production feature. The threat the signature mitigates: a malicious party claiming to be a trusted agent by serving a forged Agent Card at a similar-looking URL. Without a signature, the receiving agent has no way to verify the card came from the domain owner.

A2A signatures follow the [JSON Web Signature (JWS) standard, RFC 7515](https://datatracker.ietf.org/doc/html/rfc7515). The `AgentCardSignature` proto type in the SDK is a direct mapping of the JWS JSON Serialization shape:

```python
class AgentCardSignature:
    protected: str   # base64url-encoded JWS protected header (alg, kid, etc)
    signature: str   # base64url-encoded JWS signature
    header: dict     # optional unprotected JWS header
```

**The signing workflow** (typically done offline, not at server startup):

```python
import json
from joserfc import jws
from joserfc.jws import JWSRegistry
from joserfc.jwk import RSAKey
from google.protobuf.json_format import MessageToDict
from a2a.types import AgentCardSignature

# 1. Build the unsigned card
card = AgentCard(name="billing-agent", version="1.0.0", ...)

# 2. Canonicalize the JSON (sort keys for determinism)
card_dict = MessageToDict(card)
payload_bytes = json.dumps(card_dict, sort_keys=True).encode()

# 3. Sign with the agent's private key
key = RSAKey.import_key(open("./agent_key.pem", "rb").read())
registry = JWSRegistry(algorithms=["RS256"])
signed_compact = jws.serialize_compact(
    {"alg": "RS256", "typ": "JWS"}, payload_bytes, key, registry=registry,
)
header_b64, _, sig_b64 = signed_compact.split(".")

# 4. Attach the signature to the card
card.signatures.append(AgentCardSignature(protected=header_b64, signature=sig_b64))

# 5. Publish the signed card
with open("./signed_card.json", "w") as f:
    json.dump(MessageToDict(card), f)
```

**Verification on the client side**:

```python
# Client fetches the card, then reconstructs the signed compact form
card_dict = await fetch_card(agent_url)
sig = card_dict["signatures"][0]

# Strip signatures before verifying (the signed payload doesn't include them)
unsigned = {k: v for k, v in card_dict.items() if k != "signatures"}
payload_bytes = json.dumps(unsigned, sort_keys=True).encode()
import base64
payload_b64 = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=").decode()
compact = f"{sig['protected']}.{payload_b64}.{sig['signature']}"

# Verify with the known public key (fetched out-of-band — see Key Distribution below)
jws.deserialize_compact(compact, public_key, registry=registry)
```

**Algorithm choice**: RS256 (RSA 2048-bit with SHA-256) is the universal default — it's widely supported and not subject to the EdDSA-deprecation churn of [RFC 9864](https://datatracker.ietf.org/doc/html/rfc9864). Ed25519 is a smaller, faster alternative but joserfc raises a `SecurityWarning` for the bare `EdDSA` algorithm; if you want Ed25519, use the `Ed25519` algorithm name explicitly per RFC 9864. For most production deployments, RS256 is the safer choice.

**Key distribution is out of scope for A2A.** The protocol defines how to attach a signature to a card; it doesn't define how the client gets the agent's public key. Three common approaches:

1. **PKI / TLS certificate** — derive the agent's identity from its TLS cert (subject, SAN). The public key is whatever the cert says; verification piggybacks on TLS trust chain.
2. **JWKS endpoint** — the agent publishes a JSON Web Key Set at `/.well-known/jwks.json` containing its current public keys. The card's `protected` header includes a `kid` field; the client looks up the key by `kid`.
3. **Out-of-band exchange** — the agent's public key is shared via a trusted channel (an enterprise key registry, a manual deployment artifact, an organization's PKI). The simplest pattern for closed-network deployments.

Lab 29 uses out-of-band exchange (the public key is written to a file the client reads). Production deployments use one of the first two.

## 3. Authentication — declaring the scheme + enforcing on the server

The Agent Card already has fields for declaring what auth the agent requires. The two relevant types:

- `SecurityScheme` — describes an auth mechanism (API key, HTTP auth, OAuth2, OpenID Connect, mTLS)
- `SecurityRequirement` — declares which schemes the agent expects on incoming requests

The minimum-viable production case is API-key auth: a shared secret in an HTTP header.

```python
from a2a.types import SecurityScheme, APIKeySecurityScheme

card.security_schemes["apiKey"] = SecurityScheme(
    api_key_security_scheme=APIKeySecurityScheme(
        location="header",
        name="X-API-Key",
    )
)
```

That's the **declarative** half — the card now tells clients "I require an `X-API-Key` header." The **enforcement** half is server-side. The SDK doesn't ship middleware for this; you wire it into your Starlette app yourself:

```python
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Agent Card discovery is public by design — let it through
        if request.url.path.startswith("/.well-known/"):
            return await call_next(request)
        if request.headers.get("X-API-Key") != EXPECTED_KEY:
            return JSONResponse(
                {"error": {"code": -32001, "message": "Unauthorized"}},
                status_code=401,
            )
        return await call_next(request)

app = Starlette(
    routes=card_routes + rpc_routes,
    middleware=[Middleware(APIKeyMiddleware)],
)
```

**OAuth2 is the production answer** for cross-organizational deployments. The SDK's `OAuth2SecurityScheme` proto captures the flow metadata (token URL, refresh URL, scopes); enforcement still happens in your middleware. The middleware decodes the bearer token, validates against your auth server (or a JWKS), and rejects on failure. This is a substantial implementation; for a credible production deployment expect to wire `authlib` or `python-jose` into the middleware and integrate with your identity provider. Module 7's compositional examples assume OAuth2 is already wired.

**One specific recommendation**: keep the Agent Card discovery endpoint (`/.well-known/agent-card.json`) public, even when other endpoints require auth. The discovery URL is the entry point for trust establishment — if it requires auth, callers can't even bootstrap. The signature on the card itself provides the integrity guarantee; auth gates the *actions* (sending messages, fetching tasks), not the *discovery*.

## 4. Streaming — `SendStreamingMessage` over SSE

For tasks that complete in milliseconds, synchronous `SendMessage` (Lab 28's pattern) is fine — the client waits, the server returns the completed Task. For tasks that take seconds to minutes (LLM generation, multi-step workflows, long-running data operations), streaming is the right shape.

The SDK supports streaming via `SendStreamingMessage` — same JSON-RPC method dispatch, but the server returns Server-Sent Events instead of a single response. Each event in the stream is one of:

- **Initial Task** — the full Task object created from the user's message (state `SUBMITTED`)
- **`TaskStatusUpdateEvent`** — emitted on state transitions (`WORKING`, `INPUT_REQUIRED`, terminal states)
- **`TaskArtifactUpdateEvent`** — emitted when the agent publishes a new artifact

The client consumes the stream via httpx's SSE support or a similar SSE client. Each SSE event has `data:` containing a JSON-RPC envelope around the event.

**Enabling streaming on the server**: declare it in `AgentCapabilities` and call `SendStreamingMessage` instead of `SendMessage`:

```python
card.capabilities.streaming = True
```

The `AgentExecutor.execute()` method doesn't change — it still publishes events via `TaskUpdater`. The dispatcher reads the `streaming` capability from the card and routes streaming requests appropriately. The same `execute()` implementation handles both sync and streaming clients.

**SSE on the client side** (httpx pattern):

```python
async with httpx.AsyncClient() as client:
    async with client.stream("POST", agent_url + "/", json=rpc_envelope,
                              headers={"A2A-Version": "1.0", "X-API-Key": key}) as resp:
        async for line in resp.aiter_lines():
            if line.startswith("data: "):
                event = json.loads(line[6:])
                # event has the JSON-RPC envelope with the next state/artifact
```

For a four-event task (Lab 29 demonstrates this), the client sees: initial Task → `WORKING` status → artifact → `COMPLETED` status. Each event carries the full task state at that moment, so the client can render progress without holding the prior events in memory.

**When streaming earns its keep**: agents using LLMs that generate token-by-token (most current models); multi-step agents emitting intermediate artifacts; long-running data jobs reporting progress percentages. For sub-second responses, the SSE overhead isn't worth it — synchronous `SendMessage` is simpler for both sides.

## 5. Push notifications — out-of-process completion

For tasks that take minutes to hours (data pipelines, batch jobs, agents that wait on human input), even SSE is impractical — the client doesn't want to hold an HTTP connection open that long. A2A's push notification mechanism is the answer: the client gives the server a webhook URL; the server POSTs to the webhook when the task completes.

The protocol shape:

1. Client creates the task as usual via `SendMessage` or `SendStreamingMessage`.
2. Client calls `CreateTaskPushNotificationConfig` with a webhook URL and (optionally) a shared secret for HMAC signing.
3. Server stores the config in a `PushNotificationConfigStore` (the SDK ships `InMemoryPushNotificationConfigStore` + `DatabasePushNotificationConfigStore`).
4. Server runs the task to completion (could be hours).
5. On terminal state, server's `PushNotificationSender` POSTs to the webhook with the completed Task.

```python
card.capabilities.push_notifications = True

# Wire push config store + sender into the handler
from a2a.server.tasks import InMemoryPushNotificationConfigStore, BasePushNotificationSender

handler = DefaultRequestHandler(
    agent_executor=agent,
    task_store=task_store,
    agent_card=card,
    push_config_store=InMemoryPushNotificationConfigStore(),
    push_sender=BasePushNotificationSender(),
)
```

**Why Lab 29 doesn't demonstrate push notifications**: the client side needs to expose a webhook URL the server can reach, which means running a second HTTP listener inside the notebook. That's well-defined but adds complexity for what's already a 5-concern lab. Module 7's lab (the orchestrator pattern) is the natural home for push notifications since multi-agent flows often involve long-running cross-agent delegations.

**Security on the webhook callback**: the SDK supports HMAC signing of webhook payloads via a shared secret. The receiving agent verifies the HMAC against its config; replay attacks and unauthorized senders are blocked. Without HMAC, the webhook is open — any party that knows the URL can POST fake completions.

## 6. Observability — OpenTelemetry tracing

A2A calls cross process and organizational boundaries. When something goes wrong, the question is which agent (or which delegation hop) actually failed. The answer is distributed tracing — and the SDK ships OpenTelemetry support out of the box.

Per [AI Workflow Lab March 2026](https://aiworkflowlab.dev/article/how-to-build-a2a-agents-python-production-guide): "The SDK has built-in OpenTelemetry support for tracing A2A requests across agent boundaries... Traces propagate automatically through A2A calls, giving you distributed tracing across your agent mesh."

The SDK auto-instruments several classes via `@trace_class`:

- `DefaultRequestHandler` / `DefaultRequestHandlerV2` — server-side request lifecycle (server-kind spans)
- `JsonRpcDispatcher` / `RestDispatcher` — JSON-RPC and REST route dispatch
- `EventQueue` / `EventConsumer` — the publish-subscribe machinery between executor and response
- `TaskManager` — task-store interaction
- `InMemoryQueueManager` — in-memory queue lifecycle
- v0.3 compat transports (client-kind spans for legacy connections)

To wire OTel into a server, configure the tracer provider before importing `a2a` (so the SDK's `@trace_class` decorators pick up the right tracer):

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")))
trace.set_tracer_provider(provider)

# Now import a2a — the SDK's @trace_class decorators bind to the configured provider
from a2a.server.request_handlers import DefaultRequestHandler
# ... build the app as usual
```

For Lab 29, the lab uses an in-process `SimpleSpanProcessor` writing to a JSON-line file the notebook reads after the request completes. That's pedagogically clearer than running an external OTel collector. Production deployments point at an OTel collector (Jaeger, Honeycomb, Datadog, etc.).

**What you'll see**: a single SendMessage request produces ~40 spans across ~15 unique names — `JsonRpcDispatcher.handle_requests` at the top of the stack, `DefaultRequestHandlerV2.on_message_send` one level down, then a fan of `EventQueueSource` operations as the executor publishes events. The trace IDs propagate through the SDK; a multi-hop delegation (Module 7 territory) lights up across multiple agents in the same trace.

**Cost of OTel in production**: the auto-instrumentation overhead is small (microseconds per span); the dominant cost is the exporter's network calls. `SimpleSpanProcessor` exports synchronously and adds latency; `BatchSpanProcessor` buffers and adds memory. Production deployments use `BatchSpanProcessor` and tune the batch size to balance latency overhead against buffer memory.

**Disabling OTel**: set `OTEL_INSTRUMENTATION_A2A_SDK_ENABLED=false`. Useful for benchmarking or for environments where you don't want the dependency surface.

## What's next

- 🧪 [Lab 29 — A2A endpoint at production depth](../../labs/29-a2a-endpoint-production-depth/) — extends Lab 28's `hello_agent_server.py` with `DatabaseTaskStore` + signed Agent Card + API-key middleware + streaming + OTel; demonstrates all four end-to-end with subprocess uvicorn + real httpx client. Push notifications discussed but not implemented (Module 7).
- 🧠 [A2A endpoint production-depth quiz](../../quizzes/foundations/a2a-endpoint-production-depth.md) — 8 questions covering this page + Lab 29
- 📖 **Future Module 7** — MCP + A2A composition: the orchestrator pattern with `A2ACardResolver` + `ClientFactory`; agents using MCP for their own tools while using A2A to coordinate; push notifications across orchestrator-worker boundaries

## References

**Primary sources**:
- [A2A Protocol official documentation](https://a2a-protocol.org/latest/) — Linux Foundation governed; the canonical spec reference
- [github.com/a2aproject/a2a-python](https://github.com/a2aproject/a2a-python) — Python SDK 1.0.3; v0.3 → v1.0 migration guide
- [RFC 7515 — JSON Web Signature (JWS)](https://datatracker.ietf.org/doc/html/rfc7515) — the canonical JWS spec; Agent Card signatures are JWS JSON Serialization per RFC 7515 §7.2
- [RFC 9864 — JWS and JWE algorithm review](https://datatracker.ietf.org/doc/html/rfc9864) — the EdDSA-deprecation context for algorithm choice

**2026 industry grounding**:
- [AI Workflow Lab — A2A Agents in Python (March 2026)](https://aiworkflowlab.dev/article/how-to-build-a2a-agents-python-production-guide) — persistent task stores (PostgreSQL/MySQL/SQLite); OpenTelemetry built-in; Python 3.10+
- [Stellagent — A2A Protocol Explained (April 2026)](https://stellagent.ai/insights/a2a-protocol-google-agent-to-agent) — Signed Agent Cards as the enterprise production bar
- [Rapid Claw — A2A Complete Guide (April 2026)](https://rapidclaw.dev/blog/a2a-protocol-complete-guide-2026) — production deployments (Salesforce, SAP, ServiceNow); v1.2 March 2026

**Adjacent repo content**:
- 📖 [A2A foundations](./a2a-foundations.md) — Module 5; the protocol primitives this module operationalizes
- 🧪 [Lab 28 — A2A endpoint from scratch](../../labs/28-a2a-endpoint-from-scratch/) — the in-memory baseline Lab 29 extends
- 📖 [MCP security threat model](./mcp-security-threat-model.md) — Module 4; analogous "what changes when this moves to production" framing for tools
- 🏛 [Pattern 12 — A2A federation](../../patterns/12-a2a-federation.md) — the architecture-level pattern; this module is its production-depth implementation
