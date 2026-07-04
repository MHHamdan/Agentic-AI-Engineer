# Foundations — Where Inference Optimization Sits in the Agentic Stack

Read before Lab 1. Assumes you know transformers, attention, and PyTorch; establishes the *serving-system* view this module takes.

## 1. The layer this module lives in

```
┌─────────────────────────────────────────────┐
│ Agent applications (this repo's other modules)│  planning, tools, RAG, reflection
├─────────────────────────────────────────────┤
│ Orchestration: routing, fallbacks, tracing   │  consumes THIS module's evidence
├─────────────────────────────────────────────┤
│ ► Serving engine (vLLM): scheduler,          │  ◄ THIS MODULE
│   continuous batching, PagedAttention,       │
│   prefix cache, OpenAI-compatible API,       │
│   /metrics                                   │
├─────────────────────────────────────────────┤
│ ► Model artifact: checkpoint + quantization  │  ◄ THIS MODULE
├─────────────────────────────────────────────┤
│ Kernels/runtime: CUDA graphs, FlashAttention,│  referenced, not authored here
│ Marlin, tensor parallel                      │
├─────────────────────────────────────────────┤
│ Hardware: VRAM, bandwidth, tensor cores      │  the constraints everything obeys
└─────────────────────────────────────────────┘
```

Training-time ML intuition transfers imperfectly here. Three shifts to internalize:

1. **The bottleneck is memory bandwidth and capacity, not FLOPs.** Decode streams the entire weight matrix per token; VRAM left after weights bounds concurrency ([math §1–2](math-foundations.md)). GPU utilization % in `nvidia-smi` is routinely misleading for decode workloads.
2. **The unit of performance is the distribution, not the mean.** Production questions are p95/p99 questions; a system can look fine on averages while violating every SLO.
3. **Quality is a gate, not a metric to maximize.** Compression results are (memory Δ, speed Δ, quality Δ) triples; the third is checked against pre-registered acceptance criteria ([concepts.md#acceptance-criteria](concepts.md#acceptance-criteria)).

## 2. Why an *agentic* engineer must own this layer

Agents multiply inference: one user task fans into planning, tool selection, retrieval synthesis, code generation, reflection — 10–100× token amplification. Consequences:

- **Cost is multiplicative.** A 30% serving-throughput gain is a 30% agent-fleet cost cut ([math §6](math-foundations.md#6-cost-and-fleet-sizing)).
- **Latency compounds.** k chained calls compound their percentiles; per-call SLOs must be derived from the task SLO ([math §5](math-foundations.md#5-latency-slos-queueing)).
- **Agent traffic is structurally cache-friendly.** Long shared prefixes (system prompt, tool schemas, growing history) make prefix caching disproportionately valuable — the module's strongest through-line ([concepts.md#prefix-caching](concepts.md#prefix-caching), [diagram D8](diagrams.md#d8-agent-workload--inference-optimization-map-module-thesis)).
- **Quantization risk is agent-specific.** Benchmarks can hold while tool-call JSON fidelity degrades — the failure mode that actually breaks agents, hence structured-output checks in the eval suite.

## 3. Prerequisites checklist

You should already be comfortable with: transformer forward pass and attention shapes (`n_layers`, `n_heads`/`n_kv_heads`, `head_dim`); softmax attention cost intuition; Python + HTTP clients; reading Prometheus-style metrics (taught briefly in Lab 5 if not). You do **not** need CUDA programming, distributed training, or prior vLLM experience.

## 4. The five questions this module teaches you to answer

1. How much memory does this deployment need, and what concurrency does that buy? → Lab 1, [math §1](math-foundations.md#1-memory)
2. Which quantization scheme, and how do I prove it didn't hurt? → Labs 3–4, 7
3. At what load does this deployment stop meeting its SLO? → Lab 6, [D6](diagrams.md#d6-latencythroughput-frontier-and-the-slo-knee-lab-6-target-figure)
4. Is this server memory-bound or compute-bound right now, and what's the fix? → Lab 5, [D7](diagrams.md#d7-memory-pressure-diagnostic-from-metrics)
5. Given a GPU budget, an SLO, a quality floor, and agent traffic — what do I deploy? → Lab 8 capstone

## 5. Module map

Coverage and lab specs: [COVERAGE_GUIDE.md](COVERAGE_GUIDE.md). Tier selection: run `detect_tier.py` first; T0 (CPU-only) completes every learning objective via the mock server + audited result packs — a skipped real-tool step is by design, never a broken lab.
