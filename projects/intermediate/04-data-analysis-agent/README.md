# Project 04 — Data analysis agent

> 🟡 Intermediate · ⏱ 25-30 hours · 📍 Build Challenge after Path 01 + Path 02 + Path 06 (light evaluation) · 🛠 Verified 2026-05-29

## What you're building

A single-agent system that takes a dataset (CSV / Parquet / Excel / database table) and an analytical question ("which marketing channel had the highest ROI last quarter?"), writes Python code in a sandboxed interpreter to interrogate the data, generates visualizations, and produces a written report with inline citations pointing back to specific computations and chart artifacts.

The agent uses the ReAct + code interpreter pattern: think → write code → execute in sandbox → observe results → refine. This is the architectural ancestor of OpenAI's Code Interpreter / Advanced Data Analysis, but built from primitives so you understand every decision.

## Why this matters

Three distinguishing claims:

1. **Code-as-action is the canonical agentic primitive for structured data** — per [Together.ai's open data scientist post](https://www.together.ai/blog/building-an-autonomous-and-open-data-scientist-agent-from-scratch): "the agent will first 'think' and then 'act'. Each action the agent generates is a Python snippet." Code generation gives the agent maximum flexibility against tabular data; pre-built tools that expect specific schemas can't match it.
2. **The Silent Error is the biggest 2026 failure mode** — per [Decodesfuture January 2026](https://www.decodesfuture.com/articles/best-llm-for-data-analysis-2026-review): "The biggest risk in 2026 is the Silent Error. This is when an AI gives a wrong number but acts very sure about it." Defending against silent errors is the load-bearing engineering decision for this project.
3. **Sandboxed execution is non-negotiable** — same source: "To stay safe, 2026 teams use special libraries like Smolagents. They also use locked-down spaces that block outside internet access. This stops bad code from running on your systems." Code execution without a sandbox is a vulnerability, not an architecture.

## Prerequisites

| Required | Why |
|---|---|
| **Path 01 — Foundations** complete | ReAct loop, tool calling, structured outputs |
| **Path 02 — Agentic RAG** (canonical RAG portion) | If your agent needs to retrieve from data dictionaries, schemas, or domain context |
| **Path 06 — Evaluation & Observability** (light: Modules 1-3) | Tracing the agent's reasoning + scoring its outputs |
| Working Python 3.10+ environment | Repo baseline |
| Anthropic API key (or OpenAI / similar) | The model the agent runs on |
| A sandboxed code execution environment | One of: [E2B](https://e2b.dev/), [Together Code Interpreter (TCI)](https://docs.together.ai/docs/code-interpreter), [Riza](https://riza.io/), local Docker, [Smolagents `LocalPythonExecutor`](https://huggingface.co/docs/smolagents) (limited; for development only) |
| 2-3 example datasets you care about | Public: Kaggle, UCI ML repo, FRED, World Bank Open Data. Personal: your fitness data, your transactions export, etc. |

Helpful but not required: Path 03 (only if you go multi-agent for the stretch goal); pandas/Polars fluency.

## What you'll build

Four concrete deliverables:

1. **A CLI or web UI** — `python analyze.py --dataset transactions.csv "what drove the spike in March?"` produces an analytical report with charts
2. **Three example analyses** — `examples/analysis-01/`, `examples/analysis-02/`, `examples/analysis-03/`. Each has the dataset (or a download link), the analytical question, the agent's report, and the chart artifacts.
3. **A test suite for silent-error detection** — at least 5 deliberately tricky questions where the obvious answer is wrong (e.g., questions where a missing-data pattern matters; questions where a confounder needs to be controlled for). Document whether the agent caught each one.
4. **A `WRITEUP.md`** — architecture decisions + sandbox choice + the silent-error defense

## Architecture overview

Four logical components. Each maps to a specific 2026 best-practice decision.

| Component | What it does | Key decision |
|---|---|---|
| **1 — The agent loop** | ReAct: think → write code → execute → observe → repeat | Iteration cap; when to stop and write the report |
| **2 — The code sandbox** | Executes the agent's Python code in isolation; returns stdout / stderr / artifacts | Sandbox choice (E2B / TCI / Riza / local Docker) |
| **3 — The data context** | What the agent knows about the dataset before writing code | Schema-only / sample-rows / data dictionary / lightweight RAG over docs |
| **4 — The report generator** | Synthesizes the executed-code observations into a written report with chart citations | Citation format; chart preservation; verification step |

The tool surface stays minimal:

| Tool | Used in | Implementation |
|---|---|---|
| `execute_code(code: str)` → stdout + stderr + artifacts | 1-2 | Wraps your sandbox of choice |
| `read_data_schema(path)` → column types + sample rows + null counts | 3 | Runs once at session start; primes the agent's context |
| `save_chart(figure, caption)` → chart_id | 2-4 | Captures matplotlib/plotly figures with metadata for later citation |
| `write_report(sections)` → markdown | 4 | Final synthesis step; structured output enforces citation format |

The agent does the orchestration in its reasoning chain. A typical 5-question analysis runs 20-40 tool calls across ~3-5 minutes.

## The silent-error defense

Per the [Decodesfuture 2026 framing](https://www.decodesfuture.com/articles/best-llm-for-data-analysis-2026-review): "The best models can spot bad data. They flag the problem instead of making up a fake result. They then suggest a better way to find the answer."

This is the load-bearing engineering challenge. Three defenses to implement at minimum:

1. **Data profiling on ingestion** — before answering any question, the agent runs a profiling pass: null counts per column, type distribution, range checks, outlier flags. Profiling results stay in the agent's context as a permanent reference.
2. **Self-skepticism prompt** — the system prompt explicitly instructs: "after computing an answer, ask yourself: is there a data-quality issue, missing-value pattern, or confounder that would change this answer? If yes, flag it before reporting."
3. **Verifiable citations** — every numerical claim in the report cites the chart_id or computation_id that produced it. Reviewers can click through to the exact code that generated the number.

These three together don't eliminate silent errors but make them detectable. The Milestone 5 test suite verifies the defenses are working.

## Milestones

Six phases. Time estimates assume comfort with pandas + LLM API usage.

### Milestone 1 — Sandbox setup + hello-world agent (3-4 hours)

Get the sandbox running. Recommended starting choice: **E2B** (managed; free tier; clean Python SDK) or **Together Code Interpreter** (managed; pay-per-use; clean integration). Local Docker works if you want full control.

Build the hello-world agent: takes one question, writes one code snippet, executes it, returns the output. No analysis, no reports — just verify the loop.

**Done when**: `python analyze.py "what's 2+2?"` returns `4` after the agent writes and executes `print(2+2)`.

### Milestone 2 — Data context + profiling (3-4 hours)

Add the data-context layer. When the agent receives a dataset, it first runs schema extraction + null counts + type distribution + sample rows. The profile lives in the agent's context for the rest of the session.

**Done when**: for a sample CSV, the agent's initial action is profiling; the profile output is visible in the conversation; subsequent questions reference the profile rather than re-reading the file.

### Milestone 3 — The ReAct loop with multiple iterations (4-6 hours)

Extend to multi-iteration analyses. The agent can write code, observe the output, write more code, etc. The loop terminates either when the agent declares the answer or when the iteration cap is hit.

**Done when**: for a question like "what's the average transaction size by category?", the agent makes 3-5 tool calls and produces an answer. For a more complex question, the agent makes 10-15 tool calls.

### Milestone 4 — Visualization + chart citation (3-4 hours)

Add `save_chart`. The agent generates matplotlib or plotly figures, saves them via the tool, and gets back chart_id values it can cite. Charts are persisted to disk; the report can reference them by file path.

**Done when**: the agent produces a written analysis with 3-5 charts embedded; each chart has a caption; the report references charts by their saved path.

### Milestone 5 — Silent-error defense + test suite (5-7 hours)

Implement the three defenses (profiling / self-skepticism / verifiable citations). Build the test suite: at least 5 questions where the naive answer is wrong because of a data-quality or confounder issue. Some examples:

- **Missing-data masquerade**: a column with 30% nulls treated as if it were complete
- **Outlier dominance**: one extreme row dominating an "average"
- **Confounder confound**: a correlation that disappears after controlling for a third variable
- **Survivorship bias**: a "best performers" analysis that ignores the failed cases
- **Aggregation paradox** (Simpson's): a trend that reverses when disaggregated

Run each question against the agent. Document whether each defense fired and whether the agent's final answer flagged the issue.

**Done when**: at least 3 of the 5 test cases produce an agent response that flags the data-quality issue rather than confidently returning the naive answer.

### Milestone 6 — Polish, examples, write-up (4-5 hours)

Pick three real analyses you care about. Run them end-to-end. Capture the reports + chart artifacts. Write the WRITEUP. Add basic logging — print which iteration the agent is on, which tool it called, how many tokens it's used.

**Done when**: someone unfamiliar with the project can install dependencies, point the agent at a new CSV, ask a question, and get a report with charts.

## Evaluation criteria

The intermediate-tier rubric — five dimensions:

| Dimension | What it measures | Intermediate-tier target |
|---|---|---|
| **Code correctness** | Does the agent's generated code do what it claims to do? | 95%+ of generated code blocks execute successfully; 90%+ produce results matching the agent's stated intent |
| **Answer accuracy** | Is the agent's final answer correct given the data? | Spot-check pass on 90%+ of generated answers; for the silent-error test suite, the agent flags the issue in 3+ of 5 cases |
| **Citation discipline** | Do numerical claims trace back to specific computations? | 100% of numerical claims in the report cite a chart_id or computation_id |
| **Latency** | How long does a typical analysis take? | <5 minutes wall-clock; <50 tool calls per analysis |
| **Cost per analysis** | What does an average analysis cost? | <$1.00 per analysis at Sonnet pricing; <$0.20 at Haiku-class |

The five-dimension intermediate-tier rubric is the pattern from [Project 03](../03-project-management-agent/). The dimensions specific to this project are *code correctness* (a code-writing agent failure mode) and *citation discipline* (the silent-error defense).

## Stretch goals

Pick at most two.

- **Multi-agent variant** — split into a planner agent + executor agent + critic agent. The planner decomposes the question; the executor writes and runs code; the critic spot-checks the answer for silent errors. Demonstrates [Path 03 v1 supervisor-worker topology](../../../learning-paths/03-multi-agent-systems/) with a real-domain workload. Per the InferA approach: "a supervisor agent that orchestrates a team of specialized agents responsible for distinct phases of the data retrieval and analysis."
- **Schema retrieval (light Path 02)** — for large schemas, run RAG over a data dictionary so the agent loads only the relevant columns into context. Demonstrates the canonical RAG pattern in a non-document workload.
- **Database backend** — instead of CSVs, the agent queries a real database (SQLite, PostgreSQL, DuckDB). Adds SQL-generation capability alongside Python.
- **Reproducibility export** — the agent's full code + outputs export as a Jupyter notebook. Makes the analysis reviewable and reproducible.
- **Streaming dashboard** — the agent's actions stream to a web UI in real time; users can watch the analysis unfold. Portfolio-screenshot territory.
- **Multi-format ingestion** — handle Parquet, Excel, JSON, and database tables in addition to CSV.

## Anti-scope

What you don't need to build for this project:

- **Full eval harness with judge ensemble** — that's capstone-tier; the silent-error test suite at this tier is the manual equivalent
- **Production deployment at scale** — local + a small hosted demo is fine
- **Custom fine-tuned models** — off-the-shelf frontier models are sufficient
- **Custom sandbox infrastructure** — use E2B / TCI / Riza / Docker; don't build your own
- **Real-time data sources** — static datasets are the assumed shape; streaming is out of scope
- **Multi-tenant support** — single-user system is the assumed shape

## Resources

**Architecture references**:
- [Together.ai (June 2025), Building an Autonomous and Open Data Scientist Agent from Scratch](https://www.together.ai/blog/building-an-autonomous-and-open-data-scientist-agent-from-scratch) — the ReAct + code interpreter reference architecture; CodeAct paper inspiration
- [arxiv:2402.18679, Data Interpreter](https://arxiv.org/pdf/2402.18679) — the MetaGPT data-science agent; hierarchical graph modeling + programmable node generation
- [Decodesfuture (January 2026), 7 Best LLMs for Data Analysis 2026](https://www.decodesfuture.com/articles/best-llm-for-data-analysis-2026-review) — the Silent Error framing; ArtifactsBench; 2026 sandboxing best practices
- [InferA — scalable scientific data analysis](https://www.researchgate.net/publication/394273021_Data_Interpreter_An_LLM_Agent_for_Data_Science) — the supervisor-worker multi-agent variant for terabyte-scale data

**Tool / library documentation**:
- [E2B documentation](https://e2b.dev/docs) — recommended sandbox default; managed; clean SDK
- [Together Code Interpreter](https://docs.together.ai/docs/code-interpreter) — alternative managed sandbox
- [Riza](https://riza.io/) — newer managed sandbox option
- [Smolagents docs](https://huggingface.co/docs/smolagents) — HuggingFace's code-action agent framework with `LocalPythonExecutor`
- [Polars documentation](https://pola.rs/) — modern DataFrame library; faster than pandas for many workloads
- [Plotly Python documentation](https://plotly.com/python/) — interactive charts the agent can produce

**Repo cross-references**:
- [Project 02 — PDF Q&A bot](../../beginner/02-pdf-qa-bot/) — the prior canonical-RAG starter; same agent-loop foundation with a different data source
- [Project 03 — Project management agent](../03-project-management-agent/) — the prior intermediate-tier project; multi-agent + MCP variant
- [Project 07 — Evaluated multi-agent system](../../capstone/07-evaluated-multi-agent-system/) — the capstone-tier version where the eval harness for silent-error detection becomes a judge ensemble
- [`patterns/01-single-agent-tool-use.md`](../../../patterns/01-single-agent-tool-use.md) — the architectural pattern this project implements at single-agent tier
- [`patterns/03-supervisor-workers.md`](../../../patterns/03-supervisor-workers.md) — the multi-agent stretch-goal pattern
- [`concepts/tools/`](../../../concepts/tools/) — tool design and tool selection

## Submission guide

Four artifacts go in your repo when you're done:

1. **The agent code** — clean structure (agent/, tools/, sandbox/, examples/); README with setup + sandbox configuration + usage; `.env.example` for required keys
2. **Three example analyses with reports** — `examples/analysis-XX/` each containing the dataset (or link), the question, the report, and the chart artifacts
3. **The silent-error test suite results** — `examples/silent-errors/` with the 5 test questions, the agent's responses, and your assessment of which defenses fired
4. **`WRITEUP.md`** — a ~1,000-word document covering:
   - The sandbox choice and why (ADR format: chose / alternatives / why / tradeoffs)
   - The silent-error defenses you implemented and how they performed on the test suite
   - One thing that surprised you about how the agent wrote code
   - One thing you'd do differently with 2× the time
   - Two stretch goals you considered and your reasoning for picking (or not)

Add yourself to `docs/community/showcase.md` when you submit.

## What this project leads to

After Data Analysis Agent, the natural progressions:

- Project 05 (Multi-server MCP agent) — same intermediate tier; extends to multi-server tool composition (planned)
- Project 07 (Evaluated multi-agent system) — capstone-tier; productionizes the silent-error defense as a full judge-ensemble eval harness
- Project 08 (Production-ready deep research) — capstone-tier; combines code interpreter with deep-research patterns for long-running scientific analyses

This is the canonical Build Challenge for engineers who want a code-writing agent in their portfolio without committing to capstone-tier observability scope.
