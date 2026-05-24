# Embedding models — tool snapshot

> 🔴 **Tool snapshot — embedding libraries, verified 2026-05-24**
> Primary sources: [sentence-transformers on PyPI](https://pypi.org/project/sentence-transformers/) · [sentence-transformers/all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) · [OpenAI embedding models announcement](https://openai.com/index/new-embedding-models-and-api-updates/) · [OpenAI embeddings guide](https://platform.openai.com/docs/guides/embeddings)

Embedding models map text to dense vectors. They're 🔴 because the SOTA leaderboard shifts quarterly and pricing/availability of hosted models changes underneath us. This page pins what the Path 02 labs *actually use*, not a survey of every option.

## What the labs use

By default in Lab 06: **`sentence-transformers/all-MiniLM-L6-v2`** loaded via the `sentence-transformers` library. No API key, runs on CPU, ~80 MB download on first use.

As a documented swap-in: **`text-embedding-3-small`** via the `openai` Python SDK. Requires `OPENAI_API_KEY` but produces higher-quality embeddings.

Both code paths are in the lab. The default narration uses MiniLM; the OpenAI section is a clearly-marked alternative.

## Verified versions & pins

```toml
# pyproject.toml
sentence-transformers = ">=5.0,<6.0"   # used in Lab 06 as the default
openai = ">=1.40"                       # already pinned in prior labs; used for embeddings as swap-in
```

| Library | Current as of 2026-05-24 | Status |
|---|---|---|
| `sentence-transformers` | `5.5.1` (May 20, 2026) | Stable; the 5.x line has been current since mid-2025 |
| `openai` SDK | `2.38.0` | Stable; multiple major versions with stable `embeddings.create` API |

The `sentence-transformers` 5.x line introduced ONNX and OpenVINO backends as alternative inference backends. The labs use the default `torch` backend; the others are mentioned but not required.

---

## `all-MiniLM-L6-v2` (the headline default)

### Status

- **Model**: `sentence-transformers/all-MiniLM-L6-v2` on Hugging Face Hub.
- **Maintained** as part of the official `sentence-transformers` model collection by the maintainers of the library.
- **Architecture**: 6-layer MiniLM (distilled from a larger teacher), 384-dim output, mean-pooled token embeddings.
- **Training**: fine-tuned on 1B sentence pairs with a contrastive objective. Strong on semantic similarity for general English text.
- **Size**: ~80 MB on disk after first download. Loads in seconds on a modern CPU.
- **License**: Apache 2.0.

### API the labs use

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Encode either a single string or a list of strings
embeddings = model.encode(
    sentences=["The agent loop calls a model.", "Tools are functions the model invokes."],
    normalize_embeddings=True,   # crucial: makes cosine sim == dot product
    convert_to_numpy=True,        # default; we use numpy downstream
    batch_size=32,                # default; tune for very large corpora
)
# embeddings: np.ndarray of shape (n_sentences, 384), dtype float32
```

The lab calls `model.encode(...)` with `normalize_embeddings=True` so that **cosine similarity reduces to a dot product** — which is faster, cleaner code and the convention almost every vector store expects. If you forget `normalize_embeddings=True`, downstream similarity calculations need explicit norms in the denominator.

### Honest tradeoffs

- **Max sequence length is 256 wordpieces.** Inputs longer than that are *silently truncated*. This is the single most common foot-gun with this model. A 4,000-word document encoded as a single string is represented entirely by its first ~200 words; the rest is invisible. **Chunk your documents before encoding.** This is so important it gets its own treatment in [`concepts/rag/chunking-and-indexing.md`](../../concepts/rag/chunking-and-indexing.md).
- **English-only.** Inputs in other languages produce embeddings, but quality drops sharply. For cross-lingual workloads use `paraphrase-multilingual-MiniLM-L12-v2` or `BGE-M3`.
- **Not 2026-SOTA.** On MTEB benchmarks, larger models (BGE-large-en, GTE-large, E5-Mistral, NV-Embed-v2, Qwen3-Embedding) outperform MiniLM by ~8–16 average points. The reason MiniLM is still everywhere is the operational tradeoff: 384-dim vectors are 4× cheaper to store than 1536-dim, the model runs on CPU comfortably, and on small corpora the recall difference rarely matters. For a community lab against a 10-document corpus, it's the right default.
- **Distilled, so embeddings are coarser** than full-size models. Two genuinely-similar sentences score around 0.65–0.75 cosine; two unrelated ones around 0.10–0.20. The dynamic range is real but compressed compared to larger models.

### Failure modes you'll see

- Encoding a long document as a single string → embedding represents only the first ~200 wordpieces. Always chunk first.
- Encoding non-English text → embeddings exist but cluster poorly.
- Forgetting `normalize_embeddings=True` → cosine similarity needs explicit denominators; easy to get wrong.
- Running the very first encode call on a fresh machine → triggers the model download (~80 MB). Add 30–60 seconds; subsequent calls are fast.

---

## `text-embedding-3-small` (the OpenAI swap-in)

### Status

Verified at [OpenAI's embeddings announcement](https://openai.com/index/new-embedding-models-and-api-updates/) and [pricing page](https://platform.openai.com/docs/guides/embeddings) as of 2026-05-24:

- **1536 dimensions** by default. Supports Matryoshka-style dimension reduction via the `dimensions` parameter (256, 512, 1024, etc.) for storage cost reduction.
- **Max input**: 8,191 tokens per request. Multiple texts can be batched in a single call.
- **Pricing**: $0.02 per 1M input tokens at standard rate; $0.01 per 1M via the Batch API (50% off, 24-hour async). No output token cost — embeddings are input-only.
- **Free tier**: new OpenAI accounts get $5 credit, ≈250M tokens of `text-embedding-3-small` — enough for substantial experimentation. Verify current terms at signup.

### API the labs use

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["The agent loop calls a model.", "Tools are functions the model invokes."],
)
# response.data is a list of Embedding objects, each with a .embedding (list[float])
embeddings = [d.embedding for d in response.data]
```

For Matryoshka reduction (storage cost):

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts,
    dimensions=512,   # reduce from default 1536; quality drops modestly
)
```

### Honest tradeoffs

- **Requires an API key.** Hence the swap-in role.
- **Quality**: meaningfully better than MiniLM on most retrieval benchmarks, especially for technical content with proper-noun specifics. The difference matters at larger corpus scale (>10K chunks); at the lab's corpus size (5–15 documents) it's mostly a wash.
- **Higher dimensionality** (1536 default vs MiniLM's 384) means each vector costs 4× the storage. With the optional `dimensions` parameter you can pay for this with minor quality drop.
- **Async latency** (network call) vs MiniLM's sync local encoding. For batch indexing this doesn't matter; for online query-time encoding it adds 50–200 ms per call.
- **Cost is real but small for tutorial use.** Embedding the lab's bundled corpus costs fractions of a cent.

## `text-embedding-3-large` (the not-default)

We mention it for completeness. **3072-dim, $0.13 per 1M tokens**, ~6.5× more expensive than 3-small. MTEB retrieval benchmark only ~2–3 points better than 3-small. The honest summary, from multiple production-experience writeups: for most RAG applications, the 3-small/3-large gap is not worth the price. Reach for it only when domain-specific or non-English content benefits clearly.

---

## What we don't recommend in the headline lab

Listed honestly so readers know what was *considered* and *rejected*:

- **`text-embedding-ada-002`** — OpenAI's older model. Superseded by 3-small at one-fifth the price with better quality. No reason to use ada-002 in new code.
- **Cohere `embed-v4`** — strong (scores ~66 on MTEB) and has a useful `input_type` distinction for separately optimizing index vs query embeddings. Reasonable production choice; just adds a vendor relationship we're not requiring of a community learner.
- **Voyage AI `voyage-3` / `voyage-3-large`** — competitive on quality, but lower mind-share in the ecosystem and not the right place to send a new learner.
- **Google `text-embedding-005`** — cheapest hosted at $0.00625/M tokens. Locked to Google Cloud auth, which is operationally more friction than OpenAI's bearer-token API for a tutorial.
- **`paraphrase-multilingual-MiniLM-L12-v2`** — multilingual sibling of our default. The lab corpus is English-only, so we don't need it; mentioned here as the right swap if you have a multilingual workload.
- **`BGE-large-en`, `GTE-large`, `E5-Mistral`, `NV-Embed-v2`, `Qwen3-Embedding`** — current SOTA range. All would work; all are heavier than MiniLM. Reach for these when MiniLM's recall is the blocking issue.

---

## Where this snapshot is used

When this page updates, the following content depends on it and may need updates too:

- 🧪 [`labs/06-agentic-rag-from-scratch/`](../../labs/06-agentic-rag-from-scratch/) — primary consumer; both encode paths.
- 📖 [`concepts/rag/chunking-and-indexing.md`](../../concepts/rag/chunking-and-indexing.md) — references the 256-wordpiece limit explicitly.
- 🗺 [`learning-paths/02-agentic-rag/README.md`](../../learning-paths/02-agentic-rag/README.md) — Module 2 references this snapshot.

## Freshness check

Before trusting this page as current, verify the following from primary sources. Anything more than a minor version drift on the libraries, or a price change on OpenAI's side, should trigger an update.

1. **`sentence-transformers` is still maintained.** Check [pypi.org/project/sentence-transformers](https://pypi.org/project/sentence-transformers/). If the latest release is older than ~3 months, investigate before relying on it.
2. **API shape unchanged.** Smoke test:
   ```bash
   pip install -U sentence-transformers
   python -c "from sentence_transformers import SentenceTransformer; \
              m = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
              print(m.encode(['hello']).shape)"
   ```
   Expect `(1, 384)`.
3. **OpenAI pricing for `text-embedding-3-small` unchanged.** Check [platform.openai.com/docs/guides/embeddings](https://platform.openai.com/docs/guides/embeddings).
4. **`openai` SDK still exposes `client.embeddings.create(model=..., input=...)`.** This API has been stable for years, but the major version is on `2.x` as of this snapshot — check before relying.
5. **`all-MiniLM-L6-v2` is still the natural community default.** Watch the [Hugging Face Embedding leaderboard](https://huggingface.co/spaces/mteb/leaderboard) for a no-API-key, CPU-runnable replacement that meaningfully outperforms it without exploding install size.

When you update this page, bump the verification date at the top and add a row to the [CHANGELOG](../../CHANGELOG.md) under **Verified Tool Snapshots** in the `[Unreleased]` section.

## Primary sources

| Source | What it covers |
|---|---|
| [pypi.org/project/sentence-transformers](https://pypi.org/project/sentence-transformers/) | `sentence-transformers` version history, API surface |
| [huggingface.co/sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | The model card: architecture, training, intended use, limitations |
| [openai.com — embedding models announcement](https://openai.com/index/new-embedding-models-and-api-updates/) | The 2024 launch of the `text-embedding-3-*` series |
| [platform.openai.com/docs/guides/embeddings](https://platform.openai.com/docs/guides/embeddings) | Current API reference and pricing |

When a blog post contradicts one of these, trust the official source.
