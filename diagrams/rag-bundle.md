# RAG diagram bundle

> Colorful, vertical (`flowchart TD`) Mermaid diagrams for the RAG and RAG-evaluation curriculum. All render natively on GitHub. Source `.mmd` files live alongside this page in [`diagrams/`](./).

These complement the earlier horizontal diagrams (`rag-evaluation-loop.mmd`, `retrieval-pipeline.mmd`) with vertical, color-coded versions designed for the SOTA RAG bundle. Where both exist, prefer these for top-to-bottom reading.

## Contents

1. [Basic RAG pipeline](#1-basic-rag-pipeline)
2. [Advanced RAG pipeline](#2-advanced-rag-pipeline)
3. [RAG evaluation lifecycle](#3-rag-evaluation-lifecycle)
4. [Retrieval evaluation vs generation evaluation](#4-retrieval-evaluation-vs-generation-evaluation)
5. [Agentic RAG workflow](#5-agentic-rag-workflow)
6. [Graph RAG workflow](#6-graph-rag-workflow)
7. [Production RAG observability](#7-production-rag-observability)
8. [RAG failure diagnosis](#8-rag-failure-diagnosis)
9. [RAG evolution timeline](#9-rag-evolution-timeline)

---

## 1. Basic RAG pipeline

The seven-stage canonical pipeline: ingest, chunk, embed, index (offline) then retrieve, augment, generate (online).

```mermaid
flowchart TD
    subgraph OFFLINE["🗄️ Offline - indexing"]
        direction TB
        D[📄 Documents] --> CH[✂️ Chunk<br/><i>size + overlap + boundary</i>]
        CH --> EM[🔢 Embed<br/><i>embedding model</i>]
        EM --> IX[(🗂️ Vector index<br/><i>HNSW / IVF</i>)]
    end

    subgraph ONLINE["⚡ Online - query time"]
        direction TB
        Q[❓ User query] --> QE[🔢 Embed query]
        QE --> RET[🔍 Retrieve top-k<br/><i>nearest neighbors</i>]
        RET --> AUG[🧩 Augment prompt<br/><i>query + retrieved chunks</i>]
        AUG --> GEN[🤖 Generate<br/><i>LLM</i>]
        GEN --> ANS[✅ Answer + citations]
    end

    IX -.retrieved from.-> RET

    classDef offline fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef online fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef store fill:#fff8e1,stroke:#f57f17,stroke-width:2px,color:#e65100
    classDef answer fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f
    classDef sgOff fill:#e1f5fe,stroke:#0277bd,stroke-width:3px,color:#01579b
    classDef sgOn fill:#f1f8e9,stroke:#558b2f,stroke-width:3px,color:#33691e

    class D,CH,EM offline
    class Q,QE,RET,AUG,GEN online
    class IX store
    class ANS answer
    class OFFLINE sgOff
    class ONLINE sgOn
```

---

## 2. Advanced RAG pipeline

Pre-retrieval (query transformation), retrieval (hybrid), post-retrieval (rerank, compress), and generation with verification. Each added stage targets a specific failure mode.

```mermaid
flowchart TD
    Q[❓ Query] --> PRE

    subgraph PRE["🔧 Pre-retrieval"]
        direction TB
        RW[✍️ Query rewriting]
        EXP[➕ Query expansion / HyDE]
        DEC[🪓 Decomposition<br/><i>multi-hop</i>]
    end

    PRE --> HYB

    subgraph HYB["🔍 Hybrid retrieval"]
        direction TB
        DENSE[🧲 Dense<br/><i>embeddings</i>]
        SPARSE[🔤 Sparse<br/><i>BM25</i>]
        FUSE[🔗 Fuse<br/><i>RRF</i>]
        DENSE --> FUSE
        SPARSE --> FUSE
    end

    HYB --> POST

    subgraph POST["📊 Post-retrieval"]
        direction TB
        RR[🎯 Rerank<br/><i>cross-encoder</i>]
        COMP[🗜️ Compress / select<br/><i>context budget</i>]
        RR --> COMP
    end

    POST --> GEN[🤖 Generate]
    GEN --> VER{🛡️ Verify<br/>grounded?}
    VER -->|yes| ANS[✅ Answer + citations]
    VER -->|no| RW

    classDef pre fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#311b92
    classDef hyb fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef post fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#bf360c
    classDef gen fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef decision fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#e65100
    classDef answer fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    class RW,EXP,DEC pre
    class DENSE,SPARSE,FUSE hyb
    class RR,COMP post
    class GEN gen
    class VER decision
    class ANS answer
```

---

## 3. RAG evaluation lifecycle

Evaluation is not a one-time gate. It cycles: build an eval set, run pipelines, score, slice, decide, then promote production failures back into the set.

```mermaid
flowchart TD
    START([🚀 Start]) --> BUILD[📝 Build eval set<br/><i>golden queries +<br/>expected answers</i>]
    BUILD --> RUN[⚙️ Run pipeline<br/><i>retrieve + generate</i>]
    RUN --> SCORE

    subgraph SCORE["📊 Score"]
        direction TB
        RM[🔍 Retrieval metrics<br/><i>recall@k, MRR, NDCG</i>]
        GM[🤖 Generation metrics<br/><i>faithfulness, relevance</i>]
    end

    SCORE --> SLICE[🔪 Slice by category<br/><i>lexical / paraphrase /<br/>multi-hop / off-corpus</i>]
    SLICE --> DECIDE{🎯 Ship?}
    DECIDE -->|regression| FIX[🔧 Fix + iterate]
    FIX --> RUN
    DECIDE -->|pass| SHIP[🚢 Deploy]
    SHIP --> MON[👁️ Monitor production]
    MON --> PROMO[⬆️ Promote failures<br/>to regression set]
    PROMO --> BUILD

    classDef start fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef build fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef score fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#bf360c
    classDef decision fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#e65100
    classDef ship fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f
    classDef monitor fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#311b92

    class START start
    class BUILD,RUN build
    class RM,GM score
    class SLICE,DECIDE,FIX decision
    class SHIP,SHIP ship
    class MON,PROMO monitor
```

---

## 4. Retrieval evaluation vs generation evaluation

The two halves fail differently, get measured differently, and get fixed differently. Conflating them is the most common RAG-eval mistake.

```mermaid
flowchart TD
    SYS[🔧 RAG system output] --> SPLIT{Which half?}

    SPLIT -->|did we find<br/>the right chunks?| RET
    SPLIT -->|given chunks, did we<br/>write the right answer?| GEN

    subgraph RET["🔍 Retrieval evaluation"]
        direction TB
        R1["Context precision<br/><i>signal-to-noise</i>"]
        R2["Context recall<br/><i>did we miss evidence?</i>"]
        R3["Recall@k, MRR, NDCG<br/><i>ranking quality</i>"]
        R4["Needs: relevance labels"]
    end

    subgraph GEN["🤖 Generation evaluation"]
        direction TB
        G1["Faithfulness<br/><i>grounded in context?</i>"]
        G2["Answer relevance<br/><i>addresses the query?</i>"]
        G3["Citation correctness<br/><i>claims map to sources?</i>"]
        G4["Needs: LLM-as-judge<br/>or human labels"]
    end

    RET --> FIX_R[🔧 Fix: chunking,<br/>embeddings, hybrid,<br/>rerank]
    GEN --> FIX_G[🔧 Fix: prompt,<br/>model, context order,<br/>verification]

    classDef sys fill:#e8eaf6,stroke:#283593,stroke-width:2px,color:#1a237e
    classDef decision fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#e65100
    classDef ret fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef gen fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef fixr fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#01579b
    classDef fixg fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#33691e

    class SYS sys
    class SPLIT decision
    class R1,R2,R3,R4 ret
    class G1,G2,G3,G4 gen
    class FIX_R fixr
    class FIX_G fixg
```

---

## 5. Agentic RAG workflow

Retrieval becomes a tool the agent chooses to call, with the option to reformulate the query, retrieve again, or critique its own draft before answering.

```mermaid
flowchart TD
    Q[❓ Query] --> PLAN[🧠 Plan<br/><i>decompose if complex</i>]
    PLAN --> DECIDE{🤔 Need retrieval?}
    DECIDE -->|no| DRAFT
    DECIDE -->|yes| RETRIEVE[🔍 Retrieve tool call]
    RETRIEVE --> GRADE{📋 Relevant?}
    GRADE -->|no| REWRITE[✍️ Reformulate query]
    REWRITE --> RETRIEVE
    GRADE -->|yes| DRAFT[📝 Draft answer]
    DRAFT --> CRITIQUE{🔬 Self-critique<br/>grounded + complete?}
    CRITIQUE -->|needs more| RETRIEVE
    CRITIQUE -->|good| ANS[✅ Final answer + citations]

    classDef query fill:#e8eaf6,stroke:#283593,stroke-width:2px,color:#1a237e
    classDef plan fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#311b92
    classDef decision fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#e65100
    classDef action fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef draft fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#bf360c
    classDef answer fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    class Q query
    class PLAN plan
    class DECIDE,GRADE,CRITIQUE decision
    class RETRIEVE,REWRITE action
    class DRAFT draft
    class ANS answer
```

---

## 6. Graph RAG workflow

GraphRAG builds a knowledge graph from the corpus, detects communities, summarizes them, and traverses the graph at query time. Strong for global "what are the themes" questions and multi-hop reasoning.

```mermaid
flowchart TD
    subgraph BUILD["🏗️ Index time - build graph"]
        direction TB
        DOCS[📄 Documents] --> EXT[🔍 Extract entities<br/>+ relationships<br/><i>LLM</i>]
        EXT --> GRAPH[(🕸️ Knowledge graph<br/>nodes + edges)]
        GRAPH --> COMM[👥 Detect communities<br/><i>Leiden clustering</i>]
        COMM --> SUMM[📋 Summarize each<br/>community]
    end

    subgraph QUERY["⚡ Query time - traverse"]
        direction TB
        Q[❓ Query] --> TYPE{Global or local?}
        TYPE -->|global theme| GLOBAL[🌐 Map-reduce over<br/>community summaries]
        TYPE -->|specific entity| LOCAL[📍 Traverse local<br/>subgraph]
        GLOBAL --> SYNTH[🤖 Synthesize answer]
        LOCAL --> SYNTH
    end

    SUMM -.feeds.-> GLOBAL
    GRAPH -.feeds.-> LOCAL
    SYNTH --> ANS[✅ Answer + provenance]

    classDef build fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef store fill:#fff8e1,stroke:#f57f17,stroke-width:2px,color:#e65100
    classDef query fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef decision fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#e65100
    classDef answer fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f
    classDef sgBuild fill:#e1f5fe,stroke:#0277bd,stroke-width:3px,color:#01579b
    classDef sgQuery fill:#f1f8e9,stroke:#558b2f,stroke-width:3px,color:#33691e

    class DOCS,EXT,COMM,SUMM build
    class GRAPH store
    class Q,GLOBAL,LOCAL,SYNTH query
    class TYPE decision
    class ANS answer
    class BUILD sgBuild
    class QUERY sgQuery
```

---

## 7. Production RAG observability

Every stage emits spans. Traces feed both online evaluators (sampled, scored live) and dashboards (latency, cost, quality trends).

```mermaid
flowchart TD
    subgraph PIPE["🔧 RAG request"]
        direction TB
        S1[Span: query rewrite]
        S2[Span: retrieve]
        S3[Span: rerank]
        S4[Span: generate]
        S1 --> S2 --> S3 --> S4
    end

    PIPE --> OTEL[📡 OpenTelemetry<br/>collector]
    OTEL --> TRACE[(🗃️ Trace store)]

    TRACE --> ONLINE[🔬 Online evaluators<br/><i>sampled, async</i>]
    TRACE --> DASH[📊 Dashboards<br/><i>latency, cost, tokens</i>]

    ONLINE --> QUAL[📈 Quality signals<br/><i>faithfulness drift,<br/>retrieval precision</i>]
    QUAL --> ALERT{🚨 Threshold<br/>breached?}
    ALERT -->|yes| PAGE[📟 Alert on-call]
    ALERT -->|no| QUAL
    QUAL --> PROMO[⬆️ Promote failures<br/>to regression set]

    classDef pipe fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef otel fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#311b92
    classDef store fill:#fff8e1,stroke:#f57f17,stroke-width:2px,color:#e65100
    classDef eval fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef decision fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#e65100
    classDef alert fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c
    classDef sgPipe fill:#e1f5fe,stroke:#0277bd,stroke-width:3px,color:#01579b

    class S1,S2,S3,S4 pipe
    class OTEL otel
    class TRACE store
    class ONLINE,DASH,QUAL,PROMO eval
    class ALERT decision
    class PAGE alert
    class PIPE sgPipe
```

---

## 8. RAG failure diagnosis

A decision tree for "the answer is wrong." Localize the failure to a stage before reaching for a fix. Mirrors the [retrieval failure modes](../concepts/rag/retrieval-failure-modes.md) page.

```mermaid
flowchart TD
    BAD[❌ Wrong answer] --> Q1{Is the evidence<br/>in the corpus<br/>at all?}
    Q1 -->|no| F1[📥 Corpus gap<br/><i>ingest more sources</i>]
    Q1 -->|yes| Q2{Was it<br/>retrieved?}
    Q2 -->|no| Q3{In top-k but<br/>ranked low?}
    Q3 -->|not retrieved| F2[✂️ Chunking / embedding<br/><i>re-chunk, better model,<br/>hybrid search</i>]
    Q3 -->|low rank| F3[🎯 Add reranking]
    Q2 -->|yes| Q4{Did the model<br/>use it?}
    Q4 -->|ignored it| F4[🪟 Context order<br/><i>lost-in-the-middle,<br/>reduce k</i>]
    Q4 -->|used it wrong| Q5{Faithful to<br/>the evidence?}
    Q5 -->|no, made things up| F5[🛡️ Faithfulness<br/><i>prompt, verification,<br/>lower temperature</i>]
    Q5 -->|yes but off-topic| F6[🎯 Answer relevance<br/><i>prompt, query understanding</i>]

    classDef bad fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#b71c1c
    classDef decision fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#e65100
    classDef fix fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20

    class BAD bad
    class Q1,Q2,Q3,Q4,Q5 decision
    class F1,F2,F3,F4,F5,F6 fix
```

---

## 9. RAG evolution timeline

From classical IR to the 2024-2026 SOTA patterns. Each era added a capability the previous one lacked. Citations are on the [SOTA RAG patterns](../concepts/rag/sota-rag-patterns.md) page.

```mermaid
flowchart TD
    E1[📚 Classical IR<br/><i>TF-IDF, BM25</i><br/>pre-2019]
    E2[🧲 Dense retrieval<br/><i>DPR, dual encoders</i><br/>2020]
    E3[🔗 Canonical RAG<br/><i>Lewis et al. RAG</i><br/>2020]
    E4[🔧 Advanced RAG<br/><i>hybrid, rerank, HyDE</i><br/>2022-2023]
    E5[🔁 Self-reflective RAG<br/><i>Self-RAG, CRAG</i><br/>2023-2024]
    E6[🧭 Adaptive + Graph RAG<br/><i>query-complexity routing,<br/>GraphRAG</i><br/>2024]
    E7[🤖 Agentic RAG<br/><i>retrieval as a tool,<br/>multi-step reasoning</i><br/>2024-2026]

    E1 --> E2 --> E3 --> E4 --> E5 --> E6 --> E7

    classDef era1 fill:#eceff1,stroke:#455a64,stroke-width:2px,color:#263238
    classDef era2 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef era3 fill:#e0f7fa,stroke:#00838f,stroke-width:2px,color:#006064
    classDef era4 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef era5 fill:#fff8e1,stroke:#f57f17,stroke-width:2px,color:#e65100
    classDef era6 fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#311b92
    classDef era7 fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    class E1 era1
    class E2 era2
    class E3 era3
    class E4 era4
    class E5 era5
    class E6 era6
    class E7 era7
```

---

## Source files

Each diagram above is also available as a standalone `.mmd` file in this directory for embedding elsewhere:

- `rag-basic-pipeline.mmd`
- `rag-advanced-pipeline.mmd`
- `rag-evaluation-lifecycle.mmd`
- `rag-retrieval-vs-generation-eval.mmd`
- `rag-agentic-workflow.mmd`
- `rag-graph-workflow.mmd`
- `rag-production-observability.mmd`
- `rag-failure-diagnosis.mmd`
- `rag-evolution-timeline.mmd`

## See also

- [`concepts/rag/sota-rag-patterns.md`](../concepts/rag/sota-rag-patterns.md) - the patterns these diagrams illustrate, with citations.
- [`concepts/evaluation/rag-evaluation-framework.md`](../concepts/evaluation/rag-evaluation-framework.md) - the evaluation framework the lifecycle and retrieval-vs-generation diagrams support.
- [`math-foundations/14-retrieval-ranking-metrics.md`](../math-foundations/14-retrieval-ranking-metrics.md) - the math behind recall@k, MRR, NDCG shown in diagram 4.
