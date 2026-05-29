# Production

The going-to-prod playbook. Everything between *"it works on my notebook"* and *"it's serving real users without burning money or leaking secrets."*

## What's covered

| Page | Covers | Status |
|---|---|---|
| [`deployment.md`](./deployment.md) | Deployment patterns — FastAPI, durable execution, serverless, on-prem | ✅ Shipped (Batch 55) |
| `observability.md` | Tracing, metrics, logs — and how to actually use them | 📋 Planned |
| [`cost-engineering.md`](./cost-engineering.md) | Token budgets, model routing, caching, batching, prompt compression | ✅ Shipped (Batch 56) |
| `caching-and-routing.md` | Multi-tier caching, semantic caching, model routing strategies | 📋 Planned |
| `streaming.md` | Streaming tokens, partial tool outputs, frontend wiring | 📋 Planned |
| `async-and-concurrency.md` | Async patterns for parallel tool calls and multi-agent fan-out | 📋 Planned |
| [`checklist.md`](./checklist.md) | Pre-launch checklist — the things you forget the first time | ✅ Shipped (Batch 55) |

The conceptual side (what backpressure means, when to cache, what calibration achieves) lives in [`concepts/`](../concepts/). This folder is the engineering side — patterns, tradeoffs, and the things you only learn after a 3am page.

## Why production is its own folder

Most agentic-AI tutorials stop at *"the agent works."* The work between that point and a healthy production system is typically larger than the work to get the agent working in the first place. We treat it as a first-class topic.

## Common tracks through this folder

| If you're worried about... | Read in this order |
|---|---|
| Cost burning out of control | `cost-engineering.md` → `caching-and-routing.md` |
| User-perceived latency | `streaming.md` → `async-and-concurrency.md` → `caching-and-routing.md` |
| Reliability and uptime | `deployment.md` → `observability.md` → `checklist.md` |
| Security and abuse | [`../security/`](../security/) → `deployment.md` |

## Relationship to other folders

- **[`evaluation/`](../evaluation/)** comes before production. You don't ship what you can't measure.
- **[`security/`](../security/)** runs alongside production — prompt injection, tool abuse, data exfiltration.
- **[`tools/`](../tools/)** has the framework-specific deployment details (e.g., LangGraph Platform, durable execution).

## Contributing

War stories make the best production content. If you've debugged a real incident — cost runaway, latency cliff, tool-call thrashing, prompt-injection compromise — please consider writing it up.

> 🔴 Production deployment specifics are classified **fast-changing**. Snapshot dates on each page.
> 🟡 Underlying concepts (caching, streaming, async) are stable.
