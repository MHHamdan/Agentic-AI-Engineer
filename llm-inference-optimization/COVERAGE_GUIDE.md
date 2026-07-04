# MODULE COVERAGE GUIDE (v3) — Efficient LLM Inference

Internal authoring spec. Not learner copy. v3 integrates the tier-audit review: capability contracts, serve-vs-quantize separation, FP8 precision matrix, KV-FP8 quality checks, prefix-cache workload design, prefill/decode disaggregation, SLO-based benchmarking, capacity math, pinned models, auditable result packs, tier certification, maintenance watchlist, research watch, and a constraint-driven capstone.

Companion learner-facing files: [foundations](foundations.md) · [math](math-foundations.md) · [concepts](concepts.md) · [diagrams](diagrams.md) · [glossary](glossary.md) · [models](models.md).

**Design principles (unchanged):** offline-first labs; real tools (vLLM, LLM Compressor, GuideLLM, lm-eval) as optional overlays with graceful skip; verify every command against pinned official docs; derive numbers on-screen; vLLM is the reference implementation.

---

## Hardware tiers — capability contracts

Tiers are defined by **what the learner can validate**, not just VRAM. Each tier ships a machine-readable contract (`tiers/T{n}.yaml`) with the fields below; `detect_tier.py` selects and prints the contract so a skipped step reads as *by design*, never *broken*.

Contract fields: `hardware_class, vram_gb, cpu_ram_gb, model_size_max, max_model_len, quant_modes[], kv_cache_dtypes[], can_serve_vllm, can_quantize_locally, eval_mode (local|sampled|result_packs), expected_failure_modes[]`.

| | T0 | T1 | T2 (reference) | T3 (stretch) |
|---|---|---|---|---|
| Hardware | CPU-only laptop | 8–16 GB GPU (3060, T4/Colab) | 24–48 GB GPU (4090, L4/L40S, A100-40G) | 2–8× A100/H100 |
| CPU RAM assumed | 8 GB | 16 GB | 32 GB | 128 GB+ |
| Canonical model | simulator + result packs | 3B instruct ([models.md](models.md)) | 7–8B instruct | 70B class |
| Max model len (labs) | n/a | 4k | 8k | 16k+ |
| Quant modes | simulated | **serve** pre-quantized W4A16/FP8-weight; **quantize** 3B W4A16 only | quantize + serve: FP8 data-free, W4A16 GPTQ/AWQ | + tensor parallel, FP8 compute |
| KV dtypes | simulated | fp16, **fp8** | fp16, fp8 | fp16, fp8 |
| Real vLLM serving | no (mock server) | yes (small) | yes | yes (TP) |
| Local quantization | no | 3B only (see serve≠quantize rule) | yes | yes |
| Evaluation | result packs | `--limit` sampled + result packs | full local runs → **generates result packs** | optional |
| Expected failure modes | none (must be zero-failure) | calibration OOM on 7B; FP8-compute fallback on pre-Ada; long-context OOM | none expected | NCCL/driver mismatch; interconnect variance |

### Rule: **serving ≠ quantizing** (formalized)
- Serving a pre-quantized checkpoint is a *low-memory* task (quantized weights + KV).
- Quantizing from full precision is a *high-memory* task (full-precision model resident during calibration; GPTQ/AWQ mitigate via layer-wise sequential offload but still need headroom + CPU RAM).
- Calibration knobs are tier-controlled in the tier config: `num_calibration_samples`, `max_seq_length`, calibration batch size, algorithm (RTN data-free ≪ GPTQ ≪ AWQ in cost).
- Every quantization lab ships **two routes**:
  1. **Author route** — quantize from full precision (T2+ certified; T1 for 3B only).
  2. **Learner route** — pull the pinned pre-quantized checkpoint from [models.md](models.md), inspect its `config.json` (compressed-tensors format, scheme, group size), evaluate it. Learning objective preserved; hardware never the bottleneck.

---

## 1. LLM inference cost model

Coverage as v2 (weights math, three memory consumers, KV sizing formula with GQA, compute- vs bandwidth-bound intuition) — all formulas now live in [math-foundations.md §1–2](math-foundations.md) and labs must import from a shared `formulas.py` so docs and code can't drift.

**Expanded (review pt. 8): Lab 1 is a capacity planner, not just a memory calculator.** Required outputs:
- max concurrent requests at given context length; max context at given concurrency,
- effect toggles: KV dtype (fp16→fp8), weight scheme (bf16/fp8/int4), GQA ratio,
- explicit safety margin parameter for runtime overhead (default 10%, taught as a real deployment habit, cf. `--gpu-memory-utilization`),
- **GPU count estimator** for a target traffic level: tokens/s demand ÷ per-GPU throughput (from Lab 6 measurements or result packs), with utilization headroom. See [math §6](math-foundations.md#6-cost-and-fleet-sizing).

## 2. Inference mechanics

As v2: autoregressive loop; prefill (compute-bound, TTFT) vs decode (bandwidth-bound, ITL); KV growth and fragmentation motivation; chunked prefill as default behavior; metric vocabulary (TTFT/ITL/e2e/throughput/goodput, percentiles-first) defined once here.

**Add (review pt. 6): concept box — prefill/decode disaggregation.** Prefill and decode have opposite resource profiles; co-scheduling them creates interference (long prefills inflate others' ITL). Disaggregated serving runs prefill and decode on separate workers/pools with KV transfer between them, letting TTFT and ITL be tuned and scaled independently. Position: advanced/prod pattern, optional T3/instructor content, no lab dependency; especially relevant to agent workloads (long prompts, many short generations). Cross-ref [concepts.md#disaggregation](concepts.md#prefilldecode-disaggregation) and the vLLM docs' disaggregated prefill feature at authoring time.

## 3. Compression and quantization

As v2 (precision ladder, weight-only vs W+A, `W{w}A{a}` naming, RTN/GPTQ/AWQ at concept level, granularity, sparsity out of scope).

**Replace the single FP8 gotcha with a precision-mode matrix (review pt. 3).** "FP8" is several deployment choices; teach them as distinct rows and reuse this table in [concepts.md](concepts.md#fp8-is-not-one-thing):

| FP8 mode | Saves memory? | Speeds compute? | Hardware-dependent? | Quality risk? | Where used |
|---|---|---|---|---|---|
| FP8 **weight storage** (W8 fmt, dequant to bf16 for matmul) | yes (~2× vs bf16) | mildly (less weight traffic in decode) | no — runs anywhere via weight-only kernels (Marlin-class) | very low | any-tier serving of FP8 checkpoints |
| FP8 **activations/matmul** (true W8A8-FP8 compute) | yes | yes — prefill & high-batch gains | **yes** — needs FP8 tensor cores (Hopper / Ada, CC ≥ 8.9); pre-Ada falls back to weight-only path | low, calibration-free variants exist | T2(Ada)/T3 |
| FP8 **KV-cache storage** (`--kv-cache-dtype fp8`) | yes (~2× KV → ~2× concurrency headroom) | indirectly (bigger batches) | broadly supported; scaling-factor details vary by version | low but **not zero — must be measured** (see below) | all GPU tiers; the universal lever |
| FP8 **attention compute** | no extra | yes (attention kernels in FP8) | yes — kernel + arch specific | moderate; newest, least mature | T3 / research watch |
| **Fallback behavior** | — | — | pre-Ada GPUs load FP8 checkpoints via weight-only dequant: memory savings **without** FP8-matmul speedups | — | teach so T1 learners don't misread benchmarks |

**KV-FP8 stays the universal takeaway, with mandatory quality check (review pt. 4).** Add a required mini-evaluation to Lab 5/7: identical prompts + generation params + seed, fp16-KV vs fp8-KV runs; compare latency, memory, and *output stability* (exact-match rate on greedy decoding, task scores on the mini-suite); flag task classes where small drift matters (code gen, tool-call JSON, math). For agentic use, the check runs on **multi-turn traces** (Lab 8 workload), not single-turn prompts — KV error compounds as cache contents feed subsequent turns.

## 4. LLM Compressor workflow (tool-specific optional path)

As v2 (recipe/modifier/oneshot abstractions, two canonical recipes, compressed-tensors handoff to vLLM, version pinning, BOS gotcha planted) — now restructured around the **author route / learner route** split defined in the tier section. Lab 4 deliverable is identical on both routes: a table of (scheme, size on disk, config.json quant metadata) so T0/T1 learners produce the same artifact shape as T2.

## 5. Serving with vLLM

As v2 (launch, flags tied to theory, continuous batching, PagedAttention always-on, prefix caching default-on in V1, metrics set incl. V1 vs legacy naming, memory-bound vs compute-bound diagnostic pattern, one-paragraph alternatives).

**Add (review pt. 5): prefix-cache workload design.** Prefix caching only teaches well if the workload has real shared prefixes. Lab 5/6 must run three profiles and compare TTFT + prefill token counts + (real path) `vllm` prefix-cache metrics:
1. **No reuse** — i.i.d. random prompts → expect ≈ no benefit (control condition),
2. **System-prompt reuse** — one shared system/developer prompt, varied user tasks → moderate TTFT gains,
3. **Agent/session reuse** — shared tool schemas + retrieval template + growing multi-turn history → large gains; this profile is reused as the Lab 8 capstone workload.
Teaching point: prefix caching is workload-dependent, not a universal speedup; cache-hit rate is a *property of your traffic*, and agent traffic is unusually cache-friendly.

## 6. Benchmarking

As v2 (methodology before tools; seeds/warmup/percentiles/workload-shape control; latency–throughput frontier; GuideLLM sweep usage with version-pinned CLI; offline deterministic harness emitting GuideLLM-compatible schema; bundled real result packs).

**Upgrade to SLO-based reporting (review pt. 7).** The standard report schema (offline harness and GuideLLM post-processing alike) must include: p50/p95/p99 TTFT; p50/p95/p99 ITL; request success rate; timeout rate; queue time; **throughput at fixed latency target** (goodput); memory headroom (peak KV usage %, preemptions); **max stable concurrency before degradation**. Lab 6's graded question is no longer "which run is fastest?" but:

```text
At what concurrency does this deployment stop meeting the latency target?
```

— answered with the frontier plot + the SLO table, for baseline vs quantized, per workload profile from §5.

## 7. Quality evaluation

As v2 (perplexity uses + limits; lm-eval with vllm backend, `add_bos_token`, `--batch_size auto`, `--limit` for iteration only, version pinning; task-suite logic; pre-registered acceptance criteria; ship/no-ship exercise on T2 result packs).

**Add:** the KV-FP8 stability check (§3) and a **structured-output/tool-call fidelity check** (JSON validity rate, schema-conformance rate on a fixed tool-call prompt set) join the acceptance criteria — quantization can hold benchmark scores while degrading function-calling formatting, which is the failure mode that actually breaks agents.

## 8. Production relevance to agentic AI systems

As v2 (token amplification economics; prefill-heavy/prefix-repetitive workload shape; routing & model tiering; fallbacks/circuit breakers; task-level SLOs compounding across chained calls; trace-ID observability and per-task token accounting; safety-check routes as high-QPS quantization candidates with asymmetric-risk eval; multi-seed eval stability).

**Capstone rewritten as a constrained decision (review pt. 14).** Lab 8 brief:

```text
You have: a fixed GPU budget (e.g., 2× L40S), a p95 TTFT target (800 ms),
a minimum quality threshold (≥99% of baseline suite average, ≥98% tool-call
schema conformance), and a target request rate (agent traces, profile 3).
Choose: model, quantization mode, KV-cache dtype, max context length,
and routing/fallback policy. Justify every choice with benchmark (§6)
and evaluation (§7) evidence. Deliverable: 1–2 page decision memo + the
capacity plan from Lab 1 showing the budget closes.
```

Grading rubric keys on *evidence-linked tradeoffs*, not on picking the "right" configuration.

## Research watch (review pt. 13 — advanced, non-lab, clearly labeled)

One short section, revisited each maintenance pass, ≤1 paragraph per item: lower-bit KV-cache quantization (INT4/2-bit KV); semantic / workload-aware prefix-cache eviction (beyond LRU); prefill/decode disaggregation systems; multi-turn agent-serving schedulers (session-aware KV placement); hybrid/recurrent-architecture caching (SSM/linear-attention models have different "KV" economics). Core labs must never depend on anything in this section.

## Governance artifacts

- **[models.md](models.md)** (review pt. 9): pinned model IDs only; per-row license verified against the model card; license verification is a scripted lab-setup step (`check_licenses.py` prints license field from each pinned card). Never claim a family-level license ("Qwen is Apache-2.0") — pin and verify per model ID.
- **Result packs (review pt. 10):** every pack is a directory `result_packs/<name>/` containing `manifest.yaml` (model ID + revision hash, quant recipe, calibration dataset + sample count, vllm/llmcompressor/guidellm/lm-eval versions, GPU model, driver + CUDA versions, exact benchmark/eval commands), `raw/*.json`, `summary.md`, `limitations.md`. A pack without a manifest fails CI.
- **Certification (review pt. 11):** T0 runs in CI on every commit (simulations only, zero-failure contract). T1–T3 are manual certification tiers with records in [certification/](certification/) (pass/fail per lab, hardware, command outputs, skipped sections + reasons). Release requires fresh T0 CI green + T2 certification ≤ 90 days old.
- **[maintenance.md](maintenance.md)** (review pt. 12): watchlist of fast-moving parts (vLLM CLI/metrics naming, quant-scheme support, FP8 hardware paths, model licenses, GuideLLM flags, lm-eval task versions, CUDA/kernel compat) with last-verified dates.

## Source inventory

1. vLLM docs — https://docs.vllm.ai/ (serving, quantization, metrics design, disaggregated prefill)
2. PagedAttention — Kwon et al., SOSP 2023, arXiv:2309.06180
3. LLM Compressor — https://docs.vllm.ai/projects/llm-compressor/ · https://github.com/vllm-project/llm-compressor
4. GuideLLM — https://github.com/vllm-project/guidellm
5. lm-evaluation-harness — https://github.com/EleutherAI/lm-evaluation-harness
6. Hugging Face model cards for every pinned ID in [models.md](models.md)
7. Theory (cite where taught): SmoothQuant arXiv:2211.10438 · GPTQ arXiv:2210.17323 · AWQ arXiv:2306.00978 · Orca (OSDI 2022) · DistServe (disaggregation) arXiv:2401.09670

## Pre-publication checklist

- [ ] All snippets executed on pinned versions (recorded in maintenance.md) on the stated date
- [ ] Metric names match pinned vLLM `/metrics` output (V1 vs legacy checked)
- [ ] GuideLLM flag syntax matches pinned version
- [ ] All numbers reproduce from `formulas.py` / Lab 1
- [ ] T0 green in CI on clean CPU container, no network
- [ ] T1/T2 certification records current; result packs carry complete manifests
- [ ] `check_licenses.py` passes for every pinned model ID
- [ ] Similarity pass: no wording overlap with any public course page
