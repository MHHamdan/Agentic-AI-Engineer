# Concepts — LLM Inference Optimization

Concept cards: *what it is → why it exists → gotcha → where it's used*. Math lives in [math-foundations.md](math-foundations.md); pictures in [diagrams.md](diagrams.md).

---

## Prefill vs decode
**What:** Prefill processes the whole prompt in parallel and fills the KV cache; decode generates one token per forward pass.
**Why it matters:** They have opposite resource profiles — prefill is compute-bound, decode is memory-bandwidth-bound ([math §2](math-foundations.md#2-compute-vs-bandwidth-roofline-lite)). TTFT is a prefill+queue problem; ITL is a decode problem. Any optimization claim must say *which phase* it targets.
**Gotcha:** A long prefill co-scheduled with others' decodes inflates their ITL — the interference chunked prefill and disaggregation address.
**Used in:** Labs 2, 5, 6; agent workloads are prefill-dominated.

## KV cache
**What:** Cached key/value tensors for every past token in every layer, so decode doesn't recompute attention over the whole sequence.
**Why:** Trades memory for compute; without it decode would be O(n²) per token.
**Gotcha:** It grows linearly per token per request and competes with weights for VRAM — usually the binding constraint on concurrency ([math §1.2–1.3](math-foundations.md#12-kv-cache-per-token)). GQA/MQA shrink it architecturally; FP8-KV shrinks it numerically.
**Used in:** Everything. The module's central object.

## Continuous batching
**What:** Iteration-level scheduling — after every decode step, finished sequences leave the batch and queued ones join.
**Why:** Static batching wastes 60–80% of slots as padding/idle; continuous batching keeps the GPU saturated and raises decode arithmetic intensity ([math §2](math-foundations.md#2-compute-vs-bandwidth-roofline-lite)).
**Gotcha:** Higher batch = better throughput but each request's ITL rises slightly; it moves you along the latency–throughput frontier, not off it.
**Used in:** Lab 2 (simulated), Lab 5 (vLLM), lm-eval `--batch_size auto`.

## PagedAttention
**What:** KV cache stored in fixed-size blocks with a logical→physical block table per sequence (OS virtual-memory analogy).
**Why:** Contiguous max-length pre-allocation fragments memory; paging eliminates fragmentation and enables block sharing (Kwon et al., SOSP 2023).
**Gotcha:** Always on in vLLM — there is no enable flag. The tunable is the memory budget (`--gpu-memory-utilization`), which sets the block-pool size after weights load.
**Used in:** Lab 5; prerequisite for prefix caching.

## Prefix caching
**What:** Reuse of KV blocks across requests that share an identical prompt prefix (system prompt, tool schemas, chat history).
**Why:** Skips recomputing prefill for the shared part → TTFT and prefill-compute savings proportional to hit rate.
**Gotcha:** Benefit is a property of *your traffic*, not the engine — three workload profiles (no reuse / system-prompt reuse / agent-session reuse) give ≈0 / moderate / large gains. Measure hit rate; don't assume it. Exact-prefix matching: one differing early token kills the match.
**Used in:** Labs 5, 6, 8; the strongest inference↔agents through-line.

## Chunked prefill
**What:** Long prompts split into chunks interleaved with other requests' decode steps.
**Why:** Prevents head-of-line blocking where one huge prompt stalls everyone's ITL.
**Gotcha:** Default behavior in modern vLLM (V1) — teach as standard, and expect slightly higher TTFT for the long request in exchange for protected ITL fleet-wide.

## Prefill/decode disaggregation
**What:** Prefill and decode run on separate worker pools with KV transfer between them.
**Why:** Opposite resource profiles → separating them removes interference and lets TTFT and ITL scale independently.
**Gotcha:** KV-transfer bandwidth becomes the new constraint; operational complexity is significant. Advanced/prod pattern — T3/instructor content only, no lab depends on it.
**Used in:** Concept box §2 of the [guide](COVERAGE_GUIDE.md#2-inference-mechanics); research watch.

## Quantization taxonomy
**What:** `W{w-bits}A{a-bits}` naming. Weight-only (W4A16/W8A16): smaller weights, faster decode via reduced memory traffic, needs mixed-precision kernels. Weight+activation (W8A8 INT8/FP8): low-precision matmuls → prefill/high-batch compute gains, usually needs calibration or smoothing.
**Why:** Memory ([math §1.1](math-foundations.md#11-weights)) and bandwidth ([math §2](math-foundations.md#2-compute-vs-bandwidth-roofline-lite)) are the costs; precision is the currency.
**Gotcha:** Algorithm choice (RTN/GPTQ/AWQ) is about *where the error goes*, not how many bits — see [math §3.2](math-foundations.md#32-quantization-error-and-outliers).
**Used in:** Labs 3, 4, 7.

## FP8 is not one thing
Four distinct deployment choices — weight storage, activation/matmul compute, KV-cache storage, attention compute — with different hardware requirements and quality risks. Full matrix in the [coverage guide §3](COVERAGE_GUIDE.md#3-compression-and-quantization). The two rules of thumb: FP8-*compute* needs Hopper/Ada (CC ≥ 8.9) with weight-only fallback on older GPUs; FP8-*KV* works nearly everywhere and is the universal concurrency lever — but its output drift must be measured, especially on multi-turn agent traces.

## Serving ≠ quantizing
Serving a pre-quantized checkpoint is cheap (quantized weights + KV). Producing one is expensive (full-precision model resident during calibration). Every quantization lab has an author route (quantize) and a learner route (pull pinned pre-quantized checkpoint, inspect, evaluate). Formal rule + tier controls in the [guide](COVERAGE_GUIDE.md#rule-serving--quantizing-formalized).

## SLO and goodput
**What:** SLOs are latency/quality targets at percentiles (p95 TTFT ≤ 800 ms; p95 ITL ≤ 60 ms). Goodput = rate of requests meeting all SLOs.
**Why:** Past the saturation knee, raw throughput keeps rising while goodput collapses — "fastest run" is the wrong question; "max concurrency that still meets the SLO" is the right one ([math §5](math-foundations.md#5-latency-slos-queueing)).
**Gotcha:** Agent tasks chain calls, so per-call SLOs must be derived from the task SLO — percentiles compound.
**Used in:** Labs 6, 8.

## Acceptance criteria
**What:** Pre-registered quality thresholds for adopting a compressed model (suite-relative %, per-task floor, tool-call schema conformance), evaluated with pinned harness version/tasks/shots/seeds on baseline and candidate alike.
**Why:** Post-hoc thresholds rationalize whatever you got; sampled runs can't resolve 1% deltas ([math §4](math-foundations.md#4-evaluation-statistics)).
**Gotcha:** Benchmark scores can hold while tool-call formatting degrades — include structured-output checks for any model serving agents.
**Used in:** Lab 7; generalizes to all agent evals in the repo.

## Result pack
**What:** An auditable benchmark/eval bundle: `manifest.yaml` (model revision, recipe, tool versions, GPU, driver/CUDA, exact commands) + raw JSON + summary + limitations.
**Why:** T0/T1 learners make decisions on T2-generated data; without a manifest that data is a screenshot, not evidence.
**Used in:** Labs 6–8; governance section of the [guide](COVERAGE_GUIDE.md#governance-artifacts).
