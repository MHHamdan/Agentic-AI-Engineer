# Lab 53: Cost and latency observability

> 🔴 Advanced · ⏱ ~80–100 min · 📚 Builds on the observability guide; pairs with Lab 52

## 🎯 Goal

The [observability guide](../../concepts/observability/observability-for-agent-pms.md) put **cost per session — mean and p90/p99** — on the list of metrics a PM owns, because in 2026 agents bill across tokens, runtime, and tool calls at once, and a few runaway loops dominate the spend. This lab makes that measurable: account per-session cost, surface the tail, detect runaways, quantify re-sent context, and simulate model routing.

By the end you should be able to:

- Account per-session cost across all three billing dimensions and read the p90/p99 tail.
- Detect a runaway loop and explain why routing won't fix it.
- Quantify the re-sent-context share of the bill and the saving from caching and model routing.

## 📋 Prerequisites

**Recommended:** 📖 [Observability for AI Agent PMs](../../concepts/observability/observability-for-agent-pms.md) (the cost metrics this implements) and 🧪 [Lab 41](../41-operating-the-loop/) (the alert path the budget gate reuses).

**Assumed background:** token-based LLM pricing, percentiles, and the idea that an agent re-sends its history each step.

**Setup:** Python 3.11+; no model or network. Session traces are in `sessions.jsonl`; `cost.py` is deterministic.

## 🛠 Data and module

| Component | Notes |
|---|---|
| `sessions.jsonl` | 40 synthetic session traces (36 normal, 4 runaway loops); per-step model, tokens, history, tool, duration |
| `cost.py` | per-session cost, percentiles, runaway detection, re-sent-context fraction, caching, routing (`--self-test`) |

## What the numbers say (2026 list rates)

| Finding | Here |
|---|---|
| Heavy tail — own p90/p99, not the mean | mean ~$0.50 but p99 ~$4.91 (≈10×) |
| Runaway loops dominate | 4 sessions repeat one query 45–60× |
| Re-sent context is most of the bill | ~61% (normal), ~90% (loops) |
| Caching the history cuts cost | ~54% off total |
| Routing routine steps to a cheap model | ~47% off the routine bill |

## Steps

1. **Setup** (0).
2. **The tail** (1).
3. **Runaway detection** (2).
4. **Re-sent context and caching** (3).
5. **Model routing** (4).
6. **Budget gate on the tail** (5).

## Design choices and tradeoffs

- **Two cost problems, two controls.** Routine token spend is fixed by *routing* routine steps to a cheaper model; runaway loops are fixed by *loop detection / a step budget*. Routing does nothing for a runaway — it's an expensive planning loop, and a cheaper model just loops cheaper. Conflating them is the most common cost-control mistake.
- **Own the tail.** A budget set on the mean (or even p90) never fires until the runaways are already in the bill. The p99 is where the spend hides — here mean and p90 look fine under a $1 budget while p99 breaches at ~$4.91.
- **Cost is three dimensions at once.** Tokens, runtime, and tool calls accrue inside one session and don't map to any existing cloud-billing construct, which is why this needs its own accounting.

## Common gotchas

- **The dollar amounts are illustrative.** Token counts here are small for a checkable, offline lab; real sessions are tens to hundreds of thousands of tokens. The *ratios* are the lesson.
- **Routing needs its own eval.** The `simple` flag is given here; a real system predicts it with a classifier, and a wrong route can cost quality. Route, then measure quality on the routed path.
- **Rates move fast.** 2026 list prices are baked in for the arithmetic — verify current prices before quoting.

## 🧮 Going deeper

- 📖 [Observability for AI Agent PMs](../../concepts/observability/observability-for-agent-pms.md) — cost as a PM-owned metric.
- 🧪 [Lab 41](../41-operating-the-loop/) — the alert path the budget gate wires into.

## What comes next

OpenTelemetry GenAI span instrumentation so per-step cost is captured from live traces rather than synthetic ones, and a learned `simple`-step classifier for the routing decision (with its own quality eval).
