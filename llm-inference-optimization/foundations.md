# Foundations — Where Inference Optimization Sits in the Agentic Stack

Read before Lab 1. Assumes you know transformers, attention, and PyTorch; establishes the *serving-system* view this module takes.

## 1. The layer this module lives in

```mermaid
flowchart TB
    A["Agent applications<br/>Planning · tool use · RAG · reflection"]
    B["Orchestration layer<br/>Routing · fallbacks · tracing<br/>Consumes serving evidence"]
    C["Serving engine — vLLM<br/>Scheduler · continuous batching · PagedAttention<br/>Prefix cache · OpenAI-compatible API · /metrics"]
    D["Model artifact<br/>Checkpoint · quantization format · tokenizer"]
    E["Kernels and runtime<br/>CUDA graphs · FlashAttention · Marlin · tensor parallelism"]
    F["Hardware constraints<br/>VRAM · memory bandwidth · tensor cores"]

    A --> B --> C --> D --> E --> F

    classDef app fill:#eef6ff,stroke:#2563eb,stroke-width:1.5px,color:#111827;
    classDef orchestration fill:#f5f3ff,stroke:#7c3aed,stroke-width:1.5px,color:#111827;
    classDef module fill:#ecfdf5,stroke:#059669,stroke-width:2.5px,color:#111827;
    classDef referenced fill:#fff7ed,stroke:#ea580c,stroke-width:1.5px,color:#111827;
    classDef hardware fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#111827;

    class A app;
    class B orchestration;
    class C,D module;
    class E referenced;
    class F hardware;
