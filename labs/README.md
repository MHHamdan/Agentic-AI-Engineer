# Labs

Hands-on, guided exercises. Each lab is a folder containing a `README.md` (the brief) and a `lab.ipynb` (the working notebook). Most labs take 30–120 minutes depending on how deep you want to go on the stretch goals.

## Format

Every lab folder looks like this:

```
labs/NN-name/
├── README.md          The brief: goal, prereqs, tools, time, steps
├── lab.ipynb          The runnable notebook (outputs stripped before commit)
└── solution/          Optional reference implementation
    └── solution.ipynb
```

The README is the source of truth for what the lab teaches. The notebook is *how* you learn it — with explanation cells interleaved between code.

## Difficulty bands

Every lab is tagged with a difficulty badge:

| Badge | Meaning | Typical reader |
|---|---|---|
| 🟢 Beginner | Comfortable with Python + LLM APIs | First few weeks of agentic AI |
| 🟡 Intermediate | Comfortable with async, types, basic distributed concepts | Built simple agents |
| 🔴 Advanced | Comfortable with production engineering | Shipping agents at scale |

A lab's prereqs (other labs, concept pages, math notes) are listed at the top of its README.

## Catalog

Labs are numbered for stable reference, not for required reading order. Use [`learning-paths/`](../learning-paths/) to find the right sequence for your goal.

A growing list:

| # | Lab | Difficulty |
|---|---|---|
| 01 | First agent from scratch | 🟢 |
| 02 | ReAct loop, no framework | 🟢 |
| 03 | Tool design and selection | 🟢 |
| 04 | Chat with memory | 🟢 |
| 05 | LangGraph state machine | 🟡 |
| 06 | Google ADK agent | 🟡 |
| 07 | RAG from scratch | 🟡 |
| 08 | Agentic RAG | 🟡 |
| 09 | Supervisor pattern | 🟡 |
| 10 | Hierarchical pattern | 🟡 |
| 11 | Swarm pattern | 🟡 |
| 12 | MCP server (financial data) | 🟡 |
| 13 | MCP multi-server client | 🔴 |
| 14 | A2A task delegation | 🔴 |
| 15 | Context budget profiling | 🟡 |
| 16 | LangSmith tracing | 🟡 |
| 17 | LLM-as-judge eval | 🔴 |
| 18 | RAGAS RAG eval | 🔴 |
| 19 | Red-team an agent | 🔴 |
| 20 | Cost & latency tuning | 🔴 |
| 31 | Corrective RAG (CRAG) from scratch | 🔴 |
| 32 | Self-RAG from scratch | 🔴 |
| 33 | Graph RAG from scratch | 🔴 |
| 34 | Head-to-head RAG pattern evaluation | 🔴 |
| 35 | Adaptive RAG router | 🔴 |

Labs land continuously. Check [`CHANGELOG.md`](../CHANGELOG.md) for the most recent additions.

## Running a lab

```bash
# From repo root, after running `uv sync` and setting up .env
uv run jupyter lab labs/01-first-agent-from-scratch/lab.ipynb
```

If a lab's notebook breaks against a newer framework version, please open an issue with the `bug` label — see [troubleshooting](../setup/troubleshooting.md) for common fixes.

## Contributing

The lab template, conventions, and PR checklist are in [`CONTRIBUTING.md`](../CONTRIBUTING.md#how-to-add-a-lab). Notebooks must be runnable end-to-end with only the `.env` populated, and outputs must be stripped before commit.

> 🟡 Labs are classified **slow-moving**. The teaching is stable, but the code is updated as tool versions advance.
