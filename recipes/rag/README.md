# RAG recipes

> 🟡 Slow-moving · copy-paste solutions to common RAG problems. Each recipe is runnable with minimal dependencies.

Recipes are the "I have this specific problem, what's the fix?" content type. They are shorter and more copy-paste-oriented than [labs](../../labs/) (which walk you through building something) and more concrete than [concepts](../../concepts/) (which explain ideas). For the conceptual background behind any recipe here, follow its links into [`concepts/rag/`](../../concepts/rag/).

## Available recipes

| # | Recipe | Problem it solves | Pattern |
|---|---|---|---|
| 01 | [Basic RAG](./01-basic-rag.md) | Get a working retrieve-then-generate loop running | Canonical RAG |
| 02 | [Hybrid + reranked RAG](./02-hybrid-reranked-rag.md) | Dense retrieval misses exact-term queries | Hybrid search + cross-encoder rerank |
| 03 | [Corrective RAG (CRAG)](./03-corrective-rag.md) | Retrieval sometimes returns junk and the model uses it | CRAG (retrieval evaluator + fallback) |

## How to run

All recipes assume Python 3.11+ and an OpenAI-compatible API. To run against local models instead, see the [local-models note](#running-against-local-models) below.

```bash
pip install openai numpy
export OPENAI_API_KEY=sk-...    # or point at a local endpoint, see below
```

Each recipe is self-contained: copy the code block, set your key, run. They use small in-memory corpora so you can see the whole pipeline without standing up a vector database. For production you would swap the in-memory index for a real vector store (FAISS, Qdrant, Pinecone, Weaviate); the retrieval interface stays the same.

## Running against local models

Every recipe uses the OpenAI client, which speaks the OpenAI-compatible API that most local servers expose. To run against a local model via Ollama or any OpenAI-compatible endpoint, point the client at the local base URL:

```python
from openai import OpenAI

# Ollama (after `ollama pull llama3.1` and `ollama pull nomic-embed-text`)
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# Then use local model names:
#   chat:      model="llama3.1"
#   embedding: model="nomic-embed-text"
```

The rest of each recipe is unchanged. Embedding dimensions differ by model, but the cosine-similarity math does not care about the dimension, only that query and documents use the same model.

> Local embedding models vary in quality. For serious retrieval, check the [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) and pick a model that fits your latency and quality budget. This is fast-moving; verify current rankings.

## Choosing a recipe

Start with [01 Basic RAG](./01-basic-rag.md) to get a baseline running and measurable. Then:

- If exact-term or technical queries (product codes, error numbers) fail -> [02 Hybrid + reranked](./02-hybrid-reranked-rag.md).
- If retrieval sometimes returns irrelevant chunks the model then trusts -> [03 Corrective RAG](./03-corrective-rag.md).

For the full pattern landscape (Self-RAG, Adaptive RAG, Graph RAG, agentic RAG) and when each earns its cost, see [`concepts/rag/sota-rag-patterns.md`](../../concepts/rag/sota-rag-patterns.md). For measuring whether a recipe actually helped, see [`concepts/evaluation/rag-evaluation-framework.md`](../../concepts/evaluation/rag-evaluation-framework.md).

## See also

- [`concepts/rag/`](../../concepts/rag/) - the conceptual background for every recipe here.
- [`labs/06-agentic-rag-from-scratch/`](../../labs/06-agentic-rag-from-scratch/) - the guided, deeper version of recipe 01.
- [`patterns/08-agentic-rag.md`](../../patterns/08-agentic-rag.md) - the deployable agentic-RAG pattern.
- [`diagrams/rag-bundle.md`](../../diagrams/rag-bundle.md) - pipeline diagrams for these recipes.

> 🟡 Recipes use specific library calls and may need updating as APIs change. The patterns they teach are stable; the exact API surface is not. Verify against current SDK docs.
