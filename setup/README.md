# Environment setup

Everything you need to get the labs running locally. If you only want the fast path, read [Quickstart](#quickstart) and skip the rest until something breaks.

---

## Quickstart

```bash
git clone https://github.com/MHHamdan/Agentic-AI-Engineer.git
cd Agentic-AI-Engineer

# Install dependencies (uv is recommended)
uv sync

# Configure API keys
cp .env.example .env       # then edit .env

# Verify everything works
uv run python -c "import langchain, langgraph; print('OK')"

# Launch the first lab
uv run jupyter lab labs/01-first-agent-from-scratch/lab.ipynb
```

If that worked, you're done. If anything failed, read on.

---

## Python version

The repo targets **Python 3.11 or higher**. We test against 3.11 and 3.12 in CI. Earlier versions don't have the typing syntax (`int | None`) we use throughout, and many of the libraries we depend on have dropped 3.10 support already.

Check your version:

```bash
python --version
```

If you need to upgrade, [`python-environment.md`](./python-environment.md) covers `pyenv`, the deadsnakes PPA on Ubuntu, and Homebrew on macOS.

---

## Dependency manager: uv, pip, or conda

We support three options. Pick the one that matches how you already work.

### Option A — uv *(recommended)*

[uv](https://github.com/astral-sh/uv) is fast, lockfile-aware, and handles Python version pinning. One command sets everything up:

```bash
# Install uv (once, system-wide)
curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS / Linux
# or: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

# In the repo
uv sync
```

`uv sync` reads `pyproject.toml`, creates a `.venv/`, and installs everything pinned in `uv.lock`. Subsequent commands use `uv run <command>` to execute inside the env without needing to activate it.

### Option B — pip + venv

Standard, works everywhere:

```bash
python -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Option C — conda / mamba

If you already have a conda workflow:

```bash
conda create -n agentic-ai python=3.12
conda activate agentic-ai
pip install -r requirements.txt
```

We don't ship a `environment.yml` because most of our dependencies are pip-only.

---

## API keys

Most labs require at least one model provider API key. The `.env.example` file lists what's used. Copy it to `.env` and fill in the keys you have:

```bash
cp .env.example .env
```

A minimal `.env` for the foundations labs:

```dotenv
# Pick at least one of these.
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Optional, for tracing labs.
LANGSMITH_API_KEY=...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=agentic-ai-engineer

# Optional, for web-search-using labs.
TAVILY_API_KEY=...

# Optional, for vector-DB labs.
PINECONE_API_KEY=...
QDRANT_URL=http://localhost:6333
```

`.env` is in `.gitignore` and must not be committed. The full breakdown of which lab needs which key is in [`api-keys.md`](./api-keys.md).

---

## Local model option

If you don't want to use paid APIs, most labs can run against a local model via [Ollama](https://ollama.com/) or [vLLM](https://docs.vllm.ai/). This trades cost for hardware: you'll want at least 16 GB of RAM and ideally a GPU for anything beyond toy examples.

Quick path with Ollama:

```bash
# Install Ollama (https://ollama.com/download)
ollama pull llama3.1:8b                  # or another model you have hardware for
ollama serve                             # keeps running in the background
```

Then in your `.env`:

```dotenv
LOCAL_MODEL_PROVIDER=ollama
LOCAL_MODEL_NAME=llama3.1:8b
LOCAL_MODEL_BASE_URL=http://localhost:11434
```

Labs that support local models include a `provider="local"` toggle near the top of the notebook. Some labs that depend on specific frontier-model capabilities (tool calling, structured output, vision) will note when a local model is unlikely to produce useful results. Full guidance in [`local-models.md`](./local-models.md).

---

## Docker option

If you'd rather not touch your system Python, the repo ships a Dockerfile:

```bash
docker build -t agentic-ai-engineer .
docker run --rm -it \
  -p 8888:8888 \
  -v "$(pwd)":/workspace \
  --env-file .env \
  agentic-ai-engineer
```

The image pre-installs all dependencies and exposes a Jupyter server on port 8888. Details and customization options in [`docker.md`](./docker.md).

---

## Verify your setup

Once dependencies are installed and `.env` is configured, run the smoke test:

```bash
uv run python -m setup.verify           # or: python -m setup.verify
```

The smoke test:

1. Imports the core libraries we depend on.
2. Checks that at least one model-provider API key is set.
3. Makes a single low-cost API call to confirm the key works.
4. Prints a summary of what's available.

If the smoke test fails, the error message points you to the relevant section of [`troubleshooting.md`](./troubleshooting.md).

---

## File-by-file reference

This folder contains setup documentation organized by topic:

| File | Covers |
|---|---|
| [`README.md`](./README.md) | This page — the overview. |
| [`python-environment.md`](./python-environment.md) | Python version management (`pyenv`, system installs, version pinning). |
| [`api-keys.md`](./api-keys.md) | Which key is needed for which lab, where to get each one, and rate-limit notes. |
| [`local-models.md`](./local-models.md) | Running labs against Ollama and vLLM; hardware notes; which labs support local. |
| [`docker.md`](./docker.md) | Container-based development environment. |
| [`troubleshooting.md`](./troubleshooting.md) | Common errors and their fixes. |

---

## Tool-version note

The libraries you install via `uv sync` (or `pip install -r requirements.txt`) are pinned to specific versions in the lockfile. Those versions are kept current via periodic dependency sweeps tracked in [`CHANGELOG.md`](../CHANGELOG.md) under **Verified Tool Snapshots**.

If you're working from a clone you made months ago and labs are breaking, the first thing to try is updating dependencies:

```bash
git pull
uv sync                  # or: pip install -r requirements.txt --upgrade
```

Major framework upgrades (e.g., LangChain 1.0, LangGraph 1.0) are noted in the changelog with migration notes on the affected tool pages.
