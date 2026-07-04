# Math Foundations — LLM Inference Optimization

All formulas used across the module, with worked examples. Lab code imports these from `formulas.py`; this file is the human-readable derivation. Notation: `B` = bytes, `P` = parameter count.

Links: [concepts.md](concepts.md) · [diagrams.md](diagrams.md) · [glossary.md](glossary.md)

---

## 1. Memory

### 1.1 Weights

```
M_weights = P × bytes_per_param
```

| Model | Precision | bytes/param | Weights |
|---|---|---|---|
| 8B | BF16 | 2 | ~16 GB |
| 8B | INT4 (W4A16, incl. ~0.25 overhead for scales/zeros at g=128) | ~0.56 | ~4.5 GB |
| 70B | BF16 | 2 | ~140 GB |
| 70B | FP8 | 1 | ~70 GB |
| 70B | INT4 | ~0.56 | ~39 GB |

Group-wise quantization overhead: per group of `g` weights you store a scale (and zero-point if asymmetric), so effective bits ≈ `w_bits + (16 + z·16)/g`. At `w=4, g=128`, symmetric: `4 + 16/128 = 4.125` bits → the "0.56 bytes" above.

### 1.2 KV cache per token

```
KV_bytes/token = 2 × n_layers × n_kv_heads × head_dim × bytes_per_elem
                 └K and V┘
```

Worked example — Llama-3-8B (32 layers, 8 KV heads via GQA, head_dim 128), FP16:

```
2 × 32 × 8 × 128 × 2 B = 131,072 B ≈ 128 KB/token
32k-context request: 32,768 × 128 KB ≈ 4.0 GB   (one request!)
```

GQA effect: with full MHA (32 KV heads) this would be 512 KB/token — GQA at ratio 4 already cut KV 4×. KV-FP8 halves it again → 64 KB/token.

### 1.3 Capacity

```
KV_budget      = VRAM × gpu_mem_util − M_weights − M_overhead
max_concurrent_tokens = KV_budget / KV_bytes_per_token
max_requests(L)       = max_concurrent_tokens / L        # context length L
max_context(N)        = max_concurrent_tokens / N        # concurrency N
```

Worked example — 8B BF16 on 24 GB (util 0.90, overhead ~1 GB):

```
KV_budget = 24×0.90 − 16 − 1 ≈ 4.6 GB → 4.6 GB / 128 KB ≈ 37k tokens
  @ 4k context → ~9 concurrent requests (fp16 KV)
  @ 4k context → ~18 concurrent requests (fp8 KV)
  W4A16 weights (4.5 GB) + fp8 KV → KV_budget ≈ 16 GB → ~64 concurrent @ 4k
```

This one calculation is the module's thesis: **quantization is a concurrency multiplier before it is a speed trick.**

---

## 2. Compute vs bandwidth (roofline-lite)

Arithmetic intensity `I = FLOPs / bytes_moved`. A GPU is compute-bound when `I > FLOPs_peak / BW` (the "ridge point"), else bandwidth-bound.

- **Decode, batch 1:** each token requires streaming all weights once → `I ≈ 2·P FLOPs / P·b bytes = 2/b` FLOP/byte — hopelessly below any ridge point → **bandwidth-bound**. Upper bound on decode speed:

```
tokens/s ≤ memory_bandwidth / M_weights
e.g. A100 (2.0 TB/s), 8B BF16: 2000/16 ≈ 125 tok/s theoretical ceiling
     same GPU, W4A16 (4.5 GB): ≈ 440 tok/s ceiling → why weight quant speeds decode
```

- **Prefill:** all prompt tokens processed in one pass → weights amortized over `n_prompt` tokens → `I` scales with sequence length → **compute-bound**.
- **Batching decode:** batch size `b_s` amortizes weight streaming across `b_s` tokens → effective `I ∝ b_s` → throughput rises ~linearly with batch until compute or KV capacity saturates. This is *why* continuous batching works.

---

## 3. Quantization

### 3.1 Affine (asymmetric) quantization

```
s = (max_w − min_w) / (2^bits − 1)        # scale
z = round(−min_w / s)                      # zero-point
q = clamp(round(w/s) + z, 0, 2^bits − 1)
ŵ = s · (q − z)
```

Symmetric variant: `z = 0`, `s = max|w| / (2^(bits−1) − 1)`.

### 3.2 Quantization error and outliers

Uniform quantizer noise ≈ `s²/12` (MSE). One outlier channel inflates `max|w|` → inflates `s` → crushes resolution for everything else. Mitigations map 1:1 to algorithms: finer granularity (per-channel/group) shrinks each range; **SmoothQuant** migrates activation outlier scale into weights; **GPTQ** minimizes layer-output error `‖WX − ŴX‖²` using Hessian `H = XXᵀ` (error compensation across columns); **AWQ** protects the ~1% salient channels chosen by activation magnitude via per-channel scaling.

### 3.3 Perplexity

```
PPL = exp( −(1/N) Σᵢ log p(xᵢ | x_<i) )
```

Sensitive cheap regression signal for quant damage on the *same* model family/tokenizer; **not** comparable across tokenizers; does not measure instruction-following or tool-call fidelity. Quality deltas reported relative: `Δ% = (PPL_q − PPL_base)/PPL_base`.

---

## 4. Evaluation statistics

- Accuracy on `n` items has standard error `SE = √(p(1−p)/n)`. At `n=250` (a `--limit` smoke run), p≈0.75 → SE ≈ 2.7 pts → a "1% degradation" threshold is **not resolvable**. This is the quantitative reason `--limit` runs are iteration-only and ship/no-ship uses full T2 result packs.
- Pre-registered acceptance criteria (define *before* running): e.g. suite average ≥ 99% of baseline AND no task < 97% relative AND tool-call schema conformance ≥ 98%. Same harness version, tasks, shots, seeds on both sides.
- Greedy-decode exact-match rate between fp16-KV and fp8-KV runs is the KV-stability metric; report with `n` and CI.

---

## 5. Latency, SLOs, queueing

- `TTFT ≈ queue_time + prefill_time(prompt_len) + first_decode_step`
- `e2e ≈ TTFT + (n_out − 1) × ITL`
- Percentiles from histograms (Prometheus): `histogram_quantile(0.95, rate(vllm:time_to_first_token_seconds_bucket[5m]))`
- **Little's law** sanity check: `L = λ × W` (concurrency = arrival rate × mean latency). If the SLO caps W and the capacity model caps L, then max sustainable `λ = L_max / W_SLO` — the Lab 6 "max stable concurrency" question in one line.
- **Goodput** = rate of requests meeting *all* SLOs (e.g., p95 TTFT ≤ 800 ms ∧ p95 ITL ≤ 60 ms). Beyond the saturation knee, throughput can rise while goodput collapses — plot both.
- Chained agent calls: task-level latency across `k` sequential calls compounds; if per-call p95 = t, task p95 > t (approx `P(task ≤ T) = Πᵢ P(callᵢ ≤ tᵢ)` under independence). Per-call SLOs must be derived *from* the task SLO, not asserted.

---

## 6. Cost and fleet sizing

```
$/1M output tokens = GPU_$/hr / (throughput_tok/s × 3600) × 10⁶
GPUs_needed = ceil( peak_demand_tok/s / (per_GPU_goodput_tok/s × headroom) )   # headroom ≈ 0.7
```

Worked example: L40S at $1.0/hr serving 8B-W4A16 at 1,400 tok/s aggregate → $0.20/1M output tokens. Agent task consuming 40k total tokens across 12 calls → $0.008/task at this rate; ×1M tasks/month → $8k/month — the number that justifies (or kills) an optimization project.

Agent token amplification: `tokens/task = Σ_calls (prompt_i + output_i)`; with prefix caching at hit-rate `h`, effective prefill tokens ≈ `Σ prompt_i × (1 − h)` — measure `h` per workload profile (Lab 5), don't assume it.
