# LLM Inference Optimization — Quantization, vLLM Serving, Benchmarking, Quality Evaluation

> Module of [`Agentic-AI-Engineer`](../README.md). Everything an agentic system does — planning, tool use, retrieval synthesis, reflection, and multi-agent coordination — eventually becomes a model call. This module is where those calls become **cheap, fast, reliable, and measurable**.

## Why this module matters

Inference optimization is the layer between a promising agent design and a deployable system. It answers questions such as:

- Which model and serving stack fit the hardware budget?
- Where does latency actually come from: prefill, decode, memory bandwidth, or scheduling?
- How much quality is lost when applying quantization or KV-cache compression?
- At what concurrency does the system stop meeting its latency target?
- What evidence is strong enough to recommend a deployment decision?

This module treats inference as an engineering discipline: model choice, quantization, serving, benchmarking, quality evaluation, and release certification.

## Module map

| File | Purpose | Use it when |
|---|---|---|
| [COVERAGE_GUIDE.md](COVERAGE_GUIDE.md) | Authoring and maintenance spec: topics, labs, tiers, constraints | Extending or maintaining the module |
| [foundations.md](foundations.md) | Where inference fits in the agentic stack, prerequisites, mental model | Start here |
| [math-foundations.md](math-foundations.md) | Core formulas and worked examples: KV sizing, roofline intuition, queueing, cost, and evaluation uncertainty | Alongside Labs 1, 3, 6, 7 |
| [concepts.md](concepts.md) | Compact concept cards: prefill/decode, PagedAttention, prefix caching, goodput, SLOs, and more | Reference during all labs |
| [diagrams.md](diagrams.md) | Mermaid diagrams for the serving path, scheduler behavior, caches, and deployment decisions | Visual reference or slide source |
| [glossary.md](glossary.md) | A–Z terminology | Quick lookup |
| [models.md](models.md) | Pinned model registry, revisions, and license verification guidance | Before any real-path lab |
| [maintenance.md](maintenance.md) | Churn watchlist, version pinning, and maintenance procedure | During refresh or upgrade work |
| [certification/](certification/) | Tier-specific release validation records (T0–T3) | Before shipping or sign-off |

## Visual learning path

```mermaid
flowchart TD
    A[foundations.md<br/>Inference in the agentic stack] --> B[math-foundations.md §1–2<br/>Memory sizing and throughput basics]
    B --> C[Lab 1<br/>Memory calculator]

    C --> D[concepts.md<br/>Prefill, decode, batching]
    D --> E[Lab 2<br/>Scheduler simulator]

    E --> F[math-foundations.md §3<br/>Quantization math]
    F --> G[Lab 3<br/>NumPy quantization]
    G --> H[Lab 4<br/>LLM Compressor<br/><i>optional GPU</i>]

    H --> I[concepts.md<br/>PagedAttention and prefix caching]
    I --> J[Lab 5<br/>Mock or real vLLM server<br/>plus metrics]

    J --> K[math-foundations.md §5<br/>SLOs, queueing, and goodput]
    K --> L[Lab 6<br/>Benchmark sweep<br/><i>GuideLLM optional</i>]

    L --> M[math-foundations.md §4<br/>Evaluation uncertainty and acceptance]
    M --> N[Lab 7<br/>lm-eval and quality gates]

    N --> O[Lab 8 Capstone<br/>Deployment decision under constraints]
