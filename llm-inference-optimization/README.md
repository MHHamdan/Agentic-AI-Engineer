# LLM Inference Optimization — Quantization, vLLM Serving, Benchmarking, Quality Evaluation

> Module of [`Agentic-AI-Engineer`](../README.md). Everything an agentic system does — planning, tool use, retrieval synthesis, reflection, multi-agent coordination — is a model call. This module is where those calls get **cheap, fast, and measurable**.

## How this module is organized

| File | What it is | Read when |
|---|---|---|
| [COVERAGE_GUIDE.md](COVERAGE_GUIDE.md) | Authoring spec (v3): topics, labs, tiers, constraints | Building/maintaining the module |
| [foundations.md](foundations.md) | Where inference sits in the agentic stack; prerequisites | Before Lab 1 |
| [math-foundations.md](math-foundations.md) | Every formula used, with worked examples | Alongside Labs 1, 3, 6 |
| [concepts.md](concepts.md) | Concept cards (prefill/decode, PagedAttention, prefix cache, SLO/goodput, …) | Alongside all labs |
| [diagrams.md](diagrams.md) | Mermaid diagrams (render on GitHub) | Visual reference, slides source |
| [glossary.md](glossary.md) | A–Z terms | Lookup |
| [models.md](models.md) | Pinned model registry + licenses (verification is part of lab setup) | Before any real-path lab |
| [maintenance.md](maintenance.md) | Known moving parts (tool churn watchlist) | Each maintenance pass |
| [certification/](certification/) | Per-tier end-to-end validation records (T0–T3) | Before each release |

## Learning path

```
foundations.md ─► math-foundations.md §1–2 ─► Lab 1 (memory calculator)
      │
      ▼
concepts.md: prefill/decode, batching ─► Lab 2 (scheduler simulator)
      │
      ▼
math §3 quantization ─► Lab 3 (NumPy quant) ─► Lab 4 (LLM Compressor, optional GPU)
      │
      ▼
concepts: PagedAttention, prefix cache ─► Lab 5 (mock/real vLLM server + /metrics)
      │
      ▼
math §5 SLO & queueing ─► Lab 6 (benchmark sweep, GuideLLM optional)
      │
      ▼
math §4 eval statistics ─► Lab 7 (lm-eval, acceptance criteria)
      │
      ▼
Lab 8 capstone: deployment decision under constraints (agent workload)
```

## Cross-links to sibling modules

- **Agentic RAG** (`../agentic-rag/`): prefix caching economics of retrieval templates → [concepts.md#prefix-caching](concepts.md#prefix-caching)
- **Agent orchestration**: routing/fallback policies consume this module's benchmark + eval evidence → [COVERAGE_GUIDE.md §8](COVERAGE_GUIDE.md#8-production-relevance-to-agentic-ai-systems)
- **Evaluation & observability**: lm-eval acceptance criteria pattern generalizes to agent evals → [concepts.md#acceptance-criteria](concepts.md#acceptance-criteria)

## Hardware tiers (pick yours, everything adapts)

T0 CPU-only (mandatory baseline, all labs runnable) · T1 consumer GPU 8–16 GB · T2 single 24–48 GB GPU (reference tier; generates all result packs) · T3 multi-GPU (stretch, demo-only). Full capability contracts: [COVERAGE_GUIDE.md → Hardware tiers](COVERAGE_GUIDE.md#hardware-tiers--capability-contracts).
