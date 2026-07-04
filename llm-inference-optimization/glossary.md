# Glossary — LLM Inference Optimization

Deep dives: [concepts.md](concepts.md) · formulas: [math-foundations.md](math-foundations.md)

| Term | Definition |
|---|---|
| **Acceptance criteria** | Pre-registered quality thresholds a compressed model must meet before adoption; defined before evaluation, applied with pinned harness versions/seeds. |
| **Arithmetic intensity** | FLOPs per byte moved; determines whether a kernel is compute- or bandwidth-bound (roofline model). |
| **AWQ** | Activation-aware Weight Quantization; protects the ~1% most activation-salient weight channels via per-channel scaling before quantizing. |
| **Calibration** | Forward passes over a small dataset to collect statistics (ranges, Hessians, activation magnitudes) needed by PTQ algorithms like GPTQ/AWQ/SmoothQuant. |
| **Chunked prefill** | Splitting long prompt prefills into chunks interleaved with decode steps of other requests; protects fleet-wide ITL. Default-on in modern vLLM. |
| **Compressed-tensors** | Checkpoint format produced by LLM Compressor (`save_compressed=True`) and loaded natively by vLLM; quant metadata lives in `config.json`. |
| **Continuous batching** | Iteration-level scheduling where sequences join/leave the batch at every decode step (a.k.a. in-flight batching; Orca, OSDI 2022). |
| **Decode** | Token-by-token generation phase; memory-bandwidth-bound; governs ITL. |
| **Disaggregation (prefill/decode)** | Running prefill and decode on separate worker pools with KV transfer; tunes TTFT and ITL independently. Advanced/prod pattern. |
| **e2e latency** | Request arrival → final token. ≈ TTFT + (n_out−1)·ITL. |
| **FP8 (E4M3/E5M2)** | 8-bit float formats. Distinguish weight storage / matmul compute / KV storage / attention compute — different hardware paths and risks. |
| **Goodput** | Rate of requests satisfying all SLOs; the production objective (vs raw throughput). |
| **GPTQ** | PTQ algorithm minimizing layer output error via Hessian-based error compensation; needs calibration data. |
| **GQA / MQA** | Grouped-/Multi-Query Attention; fewer KV heads than query heads → proportionally smaller KV cache. |
| **Group size (g)** | Number of weights sharing one quantization scale (e.g., g=128 in W4A16-G128); smaller g = finer resolution, more overhead. |
| **GuideLLM** | vLLM-project load generator for OpenAI-compatible endpoints; profiles include synchronous, concurrent, poisson/constant, throughput, sweep. |
| **ITL / TPOT** | Inter-Token Latency / Time Per Output Token; the streaming smoothness metric; decode-side. |
| **KV cache** | Per-layer key/value tensors cached for all past tokens; grows linearly per token; the usual concurrency constraint. |
| **KV-cache quantization** | Storing KV in lower precision (typically FP8): ~2× concurrency headroom; output drift must be measured, especially multi-turn. |
| **Little's law** | L = λW; links concurrency, arrival rate, and latency; used to derive max sustainable request rate under an SLO. |
| **lm-evaluation-harness (lm-eval)** | EleutherAI task-evaluation framework; HF/vLLM/OpenAI-compatible backends; the de-facto standard for task-level quality checks. |
| **LLM Compressor** | vLLM-project PTQ library; recipes of modifiers applied via `oneshot()`; outputs compressed-tensors checkpoints. |
| **Marlin (-class kernels)** | Fast mixed-precision GEMM kernels enabling weight-only quantized matmul (e.g., INT4/FP8 weights × FP16 activations). |
| **Oneshot** | LLM Compressor entrypoint applying a recipe post-training without fine-tuning. |
| **PagedAttention** | Block-based KV memory management with logical→physical block tables; eliminates fragmentation; enables sharing (Kwon et al., SOSP 2023). Always on in vLLM. |
| **Perplexity (PPL)** | exp(mean NLL); cheap quant-damage regression signal; not cross-tokenizer comparable; blind to instruction/tool-call fidelity. |
| **Preemption** | Engine evicting a running request's KV under memory pressure, later recomputing; correct but wasteful; `vllm:num_preemptions_total`. |
| **Prefill** | Parallel processing of the full prompt filling KV; compute-bound; governs TTFT. |
| **Prefix caching** | Reusing KV blocks across requests sharing an exact prompt prefix; benefit ∝ traffic's prefix-reuse rate; default-on in vLLM V1. |
| **PTQ** | Post-Training Quantization (vs QAT, quantization-aware training). |
| **Result pack** | Auditable benchmark/eval bundle: manifest (versions, hardware, commands, revision hashes) + raw outputs + summary + limitations. |
| **Roofline model** | Performance bound = min(peak FLOPs, bandwidth × arithmetic intensity); explains prefill vs decode behavior. |
| **RTN** | Round-To-Nearest; data-free quantization; baseline algorithm and the data-free FP8 path. |
| **SLO** | Service-Level Objective; percentile latency/quality target (e.g., p95 TTFT ≤ 800 ms). |
| **SmoothQuant** | Migrates activation outlier scale into weights so both quantize well; enabler for W8A8-INT8. |
| **Speculative decoding** | Draft model/heuristic proposes tokens verified in parallel by the target model; decode-latency technique (mentioned, not a lab). |
| **Sweep (GuideLLM)** | Profile running synchronous baseline → max-throughput → interpolated rates to map the latency–throughput frontier. |
| **Tensor parallelism** | Splitting each layer's weights across GPUs (`--tensor-parallel-size`); required when weights exceed one GPU. |
| **Throughput** | Output tok/s (or total tok/s, or req/s) — always state which; rises with batching until saturation. |
| **TTFT** | Time To First Token = queue + prefill + first step; the interactivity metric; prefill-side. |
| **W{w}A{a}** | Quantization naming: weight bits / activation bits (W4A16, W8A8-FP8, …); the lingua franca across LLM Compressor, vLLM, HF cards. |
