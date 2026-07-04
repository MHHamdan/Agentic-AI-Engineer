# Diagrams — LLM Inference Optimization

All diagrams are Mermaid (render natively on GitHub). Source of truth for slides/figures.

## D1. GPU memory budget (why weights and KV compete)

```mermaid
flowchart LR
    subgraph VRAM["GPU VRAM × gpu-memory-utilization"]
        W["Model weights<br/>P × bytes/param<br/>(fixed at load)"]
        KV["KV cache block pool<br/>(everything left over)<br/>= concurrency capacity"]
        O["Runtime overhead<br/>activations, CUDA ctx"]
    end
    Q["Weight quantization<br/>BF16→FP8→INT4"] -->|shrinks| W
    K8["--kv-cache-dtype fp8"] -->|doubles tokens per GB| KV
    W -.->|"smaller weights ⇒ bigger pool"| KV
```

## D2. Request lifecycle (prefill → decode) and where metrics attach

```mermaid
sequenceDiagram
    participant C as Client
    participant Q as Scheduler queue
    participant P as Prefill (compute-bound)
    participant D as Decode loop (bandwidth-bound)
    C->>Q: request (prompt)
    Note over Q: queue_time
    Q->>P: schedule
    P->>P: process all prompt tokens, fill KV
    P-->>C: first token  ⟵ TTFT = queue + prefill + 1 step
    loop one token per step
        D->>D: read full KV + stream weights
        D-->>C: token  ⟵ ITL between tokens
    end
    D-->>C: EOS  ⟵ e2e latency
```

## D3. Static vs continuous batching

```mermaid
gantt
    dateFormat X
    axisFormat %L
    section Static batch
    ReqA (long)        :0, 10
    ReqB (short, then idle slot) :0, 3
    ReqC (short, then idle slot) :0, 4
    section Continuous batch
    ReqA :0, 10
    ReqB :0, 3
    ReqD joins at t=3 :3, 6
    ReqC :0, 4
    ReqE joins at t=4 :4, 5
```

## D4. PagedAttention block mapping

```mermaid
flowchart LR
    subgraph Logical["Logical KV (per sequence)"]
        A1["seq A blk0"] --> A2["seq A blk1"] --> A3["seq A blk2"]
        B1["seq B blk0"] --> B2["seq B blk1"]
    end
    subgraph Physical["Physical block pool (non-contiguous)"]
        P0[blk 17]; P1[blk 3]; P2[blk 42]; P3[blk 8]
    end
    A1 --> P1
    A2 --> P2
    A3 --> P0
    B1 --> P1
    B2 --> P3
    note["seq A and seq B share physical blk 3<br/>= prefix caching (shared system prompt)"]
    P1 --- note
```

## D5. Quantization → serving → evaluation pipeline (author vs learner route)

```mermaid
flowchart TD
    FP["Full-precision checkpoint (HF)"]
    subgraph Author["Author route (T2+)"]
        R["Recipe: GPTQ/AWQ/RTN modifier"]
        CAL["Calibration data<br/>(tier-controlled: samples, seq len)"]
        OS["llmcompressor.oneshot()"]
    end
    PQ["Pre-quantized checkpoint<br/>(compressed-tensors, pinned in models.md)"]
    subgraph Learner["Learner route (T0/T1)"]
        DL["Pull pinned checkpoint"]
        INS["Inspect config.json:<br/>scheme, group size, format"]
    end
    V["vllm serve"]
    G["GuideLLM / offline harness<br/>SLO report"]
    E["lm-eval + tool-call fidelity<br/>acceptance criteria"]
    SHIP{"ship / no-ship"}
    FP --> R --> OS --> PQ
    CAL --> OS
    FP -.->|baseline| E
    PQ --> DL --> INS --> V
    PQ --> V
    V --> G --> SHIP
    V --> E --> SHIP
```

## D6. Latency–throughput frontier and the SLO knee (Lab 6 target figure)

```mermaid
flowchart LR
    subgraph Frontier["as offered load increases →"]
        L1["low load:<br/>low latency,<br/>low throughput"] --> L2["rising load:<br/>throughput ↑,<br/>p95 stable"] --> K["KNEE:<br/>max stable concurrency<br/>= last point meeting SLO"] --> S["saturation:<br/>throughput plateaus,<br/>p95/p99 explode,<br/>goodput collapses"]
    end
    style K fill:#f9f,stroke:#333
```

## D7. Memory-pressure diagnostic (from /metrics)

```mermaid
flowchart TD
    W["vllm:num_requests_waiting rising"] --> C{kv_cache_usage_perc?}
    C -->|high, preemptions > 0| M["MEMORY-BOUND<br/>→ kv-cache-dtype fp8<br/>→ lower max-model-len<br/>→ quantize weights"]
    C -->|low| CPU["COMPUTE-BOUND<br/>→ scale out replicas<br/>→ smaller/quantized model<br/>→ W8A8 for prefill compute"]
```

## D8. Agent workload → inference optimization map (module thesis)

```mermaid
flowchart LR
    subgraph Agent["One agent task"]
        PL[Planning] --> TU[Tool calls] --> RS[Retrieval synthesis] --> CG[Code gen] --> RF[Reflection]
    end
    subgraph Shape["Workload shape"]
        H1["long shared prefixes<br/>(system + tool schemas + history)"]
        H2["short structured outputs"]
        H3["10–100× token amplification"]
        H4["chained calls ⇒ SLOs compound"]
    end
    subgraph Levers["Optimization levers"]
        PC["prefix caching"]
        CPk["chunked prefill"]
        KVq["KV-FP8"]
        RT["routing / model tiers"]
        FB["fallbacks + circuit breakers"]
    end
    Agent --> Shape
    H1 --> PC
    H1 --> CPk
    H3 --> KVq
    H3 --> RT
    H4 --> FB
```

## D9. Hardware tiers and lab coverage

```mermaid
flowchart TD
    T0["T0 · CPU-only<br/>simulator + result packs<br/>ALL labs runnable"]
    T1["T1 · 8–16 GB GPU<br/>3B model · serve pre-quantized<br/>KV-FP8 · sampled eval"]
    T2["T2 · 24–48 GB GPU<br/>7–8B · full quantize+serve+bench+eval<br/>GENERATES result packs"]
    T3["T3 · multi-GPU<br/>70B · tensor parallel · FP8 compute<br/>demo only"]
    T0 -->|"same scripts, tier.yaml swap"| T1 -->|" "| T2 -->|" "| T3
    T2 -.->|result packs flow down| T0
    T2 -.-> T1
```
