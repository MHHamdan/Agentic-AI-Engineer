# 📖 Concepts · Observability

> 📖 concepts/observability/ covers what it takes to *see* an agent in production — traces, evals, alerts, and red teaming — and who owns which part. Where [concepts/evaluation/](../evaluation/) is the primer on measuring quality, this section is about wiring that measurement into a running system you can make decisions from.

In 2026, agent observability became a discipline of its own: agents run for hours, spend across tokens, runtime, and tool calls at once, and fail in ways that look like success. Traditional monitoring (latency, error rate) can't see a well-formed-but-wrong answer or a redundant tool loop. This section orients product and engineering on the loop that catches those failures.

## Current pages

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [observability-for-agent-pms.md](./observability-for-agent-pms.md) | ~18 min | Why observability is the priority for agent teams, the four pillars (traces, evals, alerts, red teaming) and how they form one loop, and where the PM's job ends and engineering's begins — with the metrics a PM should own. |

## How this maps to the hands-on labs

The pages here are the conceptual frame; the [Path 02](../../learning-paths/02-agentic-rag/) production tail (Modules 16–23) builds the pillars in code:

- **Traces** — the operating loop ([Lab 41](../../labs/41-operating-the-loop/)).
- **Evals** — the judge and its ceiling ([Lab 40](../../labs/40-annotation-quality/)), CI gates ([Labs 37–38](../../labs/37-rag-eval-gates/)), graded and adjudicated gold ([Labs 47](../../labs/47-trustworthy-gold/), [49](../../labs/49-graded-gold/)), and calibration ([Lab 51](../../labs/51-calibrated-multidimensional/)).
- **Alerts** — hardening the signal path ([Labs 42](../../labs/42-hardening-operations/), [44](../../labs/44-hardening-the-signals/), [46](../../labs/46-scaling-the-signals/), [48](../../labs/48-distributed-and-graded/)) and closing the failure loop ([Lab 50](../../labs/50-closing-the-failure-loop/)).
- **Red teaming** — the adversarial pillar ([Lab 52](../../labs/52-red-teaming-trajectories/): grading adversarial trajectories on tool-selection, recovery, and leakage).
- **Cost & latency** — per-session cost tails, runaway-loop detection, and model routing ([Lab 53](../../labs/53-cost-latency-observability/)).
