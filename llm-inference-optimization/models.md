# Model Registry — Pinned IDs, Licenses, Tier Assignment

**Rule:** Use models only through pinned model IDs whose model cards explicitly allow the intended use. Treat license verification as part of lab setup — `python check_licenses.py` must pass before any real-path lab. Never rely on family-level license claims ("Qwen is Apache-2.0"): licenses vary by model *and by release* within a family. The `license` column below is a claim to be **verified against the live model card** on each maintenance pass; record the date.

| Model ID (pinned) | Params | License (verify on card) | Tier | Role | Quantized variant used | Ctx len in labs | Why included | Last verified |
|---|---|---|---|---|---|---|---|---|
| `Qwen/Qwen2.5-3B-Instruct` | 3B | check card (Qwen research license ≠ Apache for some sizes) | T1 | canonical small; author-route quantization target | lab-produced W4A16-G128 | 4k | small enough to calibrate on 8–16 GB | ☐ |
| `Qwen/Qwen2.5-7B-Instruct` | 7B | check card (Apache-2.0 claimed for this size — verify) | T2 | canonical reference; generates result packs | lab-produced FP8 + W4A16 | 8k | fits 24 GB quantized with KV headroom | ☐ |
| `meta-llama/Llama-3.2-3B-Instruct` | 3B | Llama 3.2 Community License — verify redistribution terms for course use | T1 alt | alternative small | pre-quantized (see below) | 4k | GQA worked example continuity with docs | ☐ |
| `meta-llama/Llama-3.1-8B-Instruct` | 8B | Llama 3.1 Community License — verify | T2 alt | alternative reference; matches most public quantization docs/examples | pre-quantized W4A16 from a maintained org (pin exact repo) | 8k | §1 worked example uses its architecture numbers | ☐ |
| *(pinned pre-quantized checkpoints)* | — | inherits base + check quantizer repo terms | T0/T1 learner route | serve-without-quantize path | e.g., RedHat/Neural Magic-published compressed-tensors repos — **pin exact repo ID + revision hash at authoring time** | — | learner route of the serve≠quantize rule | ☐ |
| `<T3 70B model>` | 70B | verify | T3 | instructor demo only | W4A16 or FP8 | 16k | makes 140 GB→~39 GB math tangible | ☐ |

Notes:
- Pin **revision hashes**, not just IDs, in `tiers/T{n}.yaml` and in every result-pack manifest.
- Gated models (Llama family) require HF access approval — call this out in lab setup; Qwen path exists precisely so no lab hard-depends on a gated model.
- Architecture parameters used by Lab 1 (`n_layers`, `n_kv_heads`, `head_dim`) are transcribed from each card into `configs/models.json` with the card URL as provenance.
- Any model added later must add a row here **and** a license check entry before appearing in a lab.
