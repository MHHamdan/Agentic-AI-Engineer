# Maintenance — Known Moving Parts

Fast-changing items that can silently break labs or teach stale facts. Review each maintenance pass (target: quarterly); update `Last verified` and the pinned versions table.

## Pinned versions (single source of truth)

| Tool | Pinned | Last verified | Notes |
|---|---|---|---|
| vllm | `==X.Y.Z` (set at cert time) | ☐ | |
| llmcompressor | `==X.Y.Z` | ☐ | |
| guidellm | `==X.Y.Z` | ☐ | |
| lm_eval | `==X.Y.Z` | ☐ | |
| CUDA / driver (T2 cert box) | | ☐ | |

## Watchlist

| Moving part | Risk | What to check | Last verified |
|---|---|---|---|
| vLLM CLI & server flags | commands in Labs 4–6 break | `vllm serve --help` vs written snippets | ☐ |
| vLLM metrics naming (V1 vs legacy) | Lab 5 PromQL breaks; docs teach wrong names | `curl :8000/metrics` vs metric list in guide §5 (`kv_cache_usage_perc` vs `gpu_cache_usage_perc`) | ☐ |
| vLLM default behaviors | claims like "prefix caching default-on", "chunked prefill default" go stale | release notes + feature docs | ☐ |
| LLM Compressor modifiers/schemes | import paths & scheme lists shift between 0.x releases (e.g., 0.9.0 KV/attention refactor; AWQ beyond W4A16); sparsity removed | release notes; re-run Lab 4 author route | ☐ |
| FP8 hardware support matrix | fallback behavior descriptions (pre-Ada weight-only path) may change with new kernels | vLLM quantization docs; re-verify FP8 table in guide §3 | ☐ |
| GuideLLM CLI | `--rate-type` → `--profile` style migrations; output schema | docs/getting-started/benchmark.md at pinned tag; offline harness schema parity | ☐ |
| lm-eval task definitions | prompts/metrics change across releases → baselines incomparable | pin version; if bumping, regenerate ALL result packs | ☐ |
| Model licenses & gating | cards/licenses change; repos get gated or renamed | `check_licenses.py` against [models.md](models.md) | ☐ |
| Pre-quantized checkpoint repos | learner-route repos can move/change revision | revision hashes still resolve | ☐ |
| CUDA/kernel compatibility | Marlin/FlashAttention/FP8 kernel requirements shift | T1/T2 cert re-run | ☐ |
| Research-watch section | items graduate to mainstream (e.g., disaggregation in vLLM) → promote or prune | guide's Research watch | ☐ |

## Update procedure

1. Bump pinned versions in a branch; run T0 CI.
2. Re-certify T2 (regenerates result packs with new manifests); re-certify T1.
3. Diff `/metrics` names, CLI help, and lm-eval task hashes against the guide; patch docs.
4. Update `Last verified` dates here and in [models.md](models.md); merge.
