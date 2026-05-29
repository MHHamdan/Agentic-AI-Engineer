# How to use this repo

> 📍 The detailed navigation guide for the Agentic AI Engineer learning hub. Read this if [`docs/start-here.md`](./start-here.md) didn't give you enough orientation.

## The five content types

The repo's content is organized by what each piece *does* for you, not by topic. Five types:

| Content type | Folder | What it does |
|---|---|---|
| **Concepts** | [`concepts/`](../concepts/) | Short explainers — *what something is and when to use it* (~10 min/page). Stable. |
| **Labs** | [`labs/`](../labs/) | Hands-on guided exercises with Jupyter notebooks (~60-120 min each). Reproducible. |
| **Recipes** | [`recipes/`](../recipes/) | Copy-paste solutions to specific problems (~2-5 min each). Practical. |
| **Patterns** | [`patterns/`](../patterns/) | Architecture patterns with diagrams and tradeoffs (~15 min/page). Decision-making. |
| **Projects** | [`projects/`](../projects/) | Build Challenges and Capstones (~15-40+ hours each). Portfolio work. |

The five types overlap deliberately. A concept page links to relevant labs (for hands-on practice), patterns (for the decision-making view), and recipes (for the operational shortcuts). A pattern page links back to the concepts that motivate it. The cross-linking is what makes the repo navigable instead of organized.

## The supporting folders

Beyond the five content types, the repo has supporting folders that aren't themselves content but make the content usable:

| Folder | What lives here |
|---|---|
| [`learning-paths/`](../learning-paths/) | Nine curated reading lists across the rest of the repo — each path is a *journey*, not a duplicate folder |
| [`math-foundations/`](../math-foundations/) | Engineer-useful math with citations. Read theory-first or as-you-go. |
| [`production/`](../production/) | Deployment, cost engineering, latency/streaming/concurrency |
| [`security/`](../security/) | Threat models, defenses, red-teaming |
| [`evaluation/`](../evaluation/) | Eval frameworks, datasets, scorers |
| [`tools/`](../tools/) | Versioned snapshots of fast-moving frameworks |
| [`examples/`](../examples/) | Minimal reference implementations |
| [`references/`](../references/) | Papers, books, talks, community resources |
| [`glossary/`](../glossary/) | A-Z terminology |
| [`diagrams/`](../diagrams/) | Mermaid sources + rendered images |
| [`docs/`](../docs/) | Start-here pages, this page, community pages |
| [`setup/`](../setup/) | Environment setup |
| [`assets/`](../assets/) | Working artifacts not user-facing |
| [`quizzes/`](../quizzes/) | Knowledge checks across the curriculum |

## Three natural reading orders

The repo doesn't enforce a reading order. Three orders that work, depending on what you're trying to do:

### 1. The structured learner — paths in sequence

Best if you're learning agentic AI from the ground up.

| Order | Why |
|---|---|
| Path 01 — Foundations | The vocabulary and the agent loop |
| Path 02 — Agentic RAG | Retrieval as a first-class tool |
| Path 03 — Multi-Agent Systems | Topology + the six production patterns |
| Path 04 — Tool Protocols (MCP + A2A) | Standardized integration |
| Path 05 — Context Engineering | Token budgets + memory tiers + drift detection |
| Path 06 — Evaluation & Observability | Tracing + judge ensembles + drift detection |
| Path 07 — Production & Safety | Deployment + cost + safety + red-teaming |
| Path 08 — Math Foundations | Optional theory layer (read as-you-go) |
| Path 09 — Capstones | Portfolio projects combining everything |

You can skip paths or rearrange them, but the dependency graph above is the canonical order.

### 2. The problem-solver — recipes and patterns first

Best if you have a specific problem to solve right now.

1. Search [`recipes/`](../recipes/) for the exact phrasing of your problem
2. If no recipe matches, read the relevant [`patterns/`](../patterns/) page for the architectural decision
3. If patterns don't go deep enough, follow the references to the [`concepts/`](../concepts/) pages
4. If concepts reference labs, run the labs to confirm the approach works for your specific case

### 3. The portfolio builder — projects first

Best if you have a deployment target and want to build something to show.

1. Read [`projects/README.md`](../projects/README.md) and pick a project at your tier (beginner / intermediate / capstone)
2. Follow the project brief's prerequisites to identify which paths you need
3. Work through those paths' content as needed for the project — concept pages, then labs, then patterns
4. Build the project; submit to `docs/community/showcase.md` when done

## The status markers

The repo uses these markers consistently:

- ✅ **Shipped / Complete** — content is authored, reviewed, and stable
- 🚧 **In progress** — content is partially authored; the structure is locked but pages are landing in batches
- 📋 **Planned / Scaffold** — content is scaffolded (the structure exists; README documents what's planned) but not yet authored
- 🟢 **Stable** — content changes on a scale of years
- 🟡 **Intermediate stability** — content references frameworks that change every few months; reviewed regularly
- 🔴 **Fast-moving** — content references frameworks that change weekly; check the verified-as-of date

Status markers appear on path READMEs, project READMEs, and concept pages where stability matters. The verified-as-of dates at the top of fast-moving pages tell you when the content was last checked against current tools.

## Stable vs fast-moving content

The repo deliberately separates content by its rate of change:

- **Stable** content lives in [`concepts/`](../concepts/), [`math-foundations/`](../math-foundations/), [`patterns/`](../patterns/). The underlying ideas don't change much.
- **Fast-moving** content lives in [`tools/`](../tools/), [`recipes/`](../recipes/), some [`labs/`](../labs/). Tool versions and APIs change; the content is dated and versioned.

When you read a fast-moving page, check the verified-as-of date. When you read a stable page, the dates are less critical — the page is correct in concept even if specific tool references have shifted.

## How the labs work

Labs live in [`labs/`](../labs/) — each lab is a self-contained directory with a `README.md` (the guided narrative) and one or more Jupyter notebooks (the executable code). All 50 notebooks across the repo are pre-executed with outputs visible on GitHub — you can read them like an article. To run them locally:

```bash
git clone https://github.com/MHHamdan/Agentic-AI-Engineer.git
cd Agentic-AI-Engineer
# Set up environment per setup/README.md
jupyter notebook labs/01-first-agent-from-scratch/
```

The `setup/` folder has the canonical environment setup; if anything in the labs breaks, that's the first place to check.

## What "complete" means for this repo

The repo is community-maintained and continuously evolving. "Complete" at any moment means:

- Every link in path READMEs and the root README resolves
- Every cross-reference in concept and pattern pages points to existing content or to text-only markers for planned-but-unbuilt content
- Every lab notebook executes end-to-end on the documented environment
- The CHANGELOG names every batch of changes with verification fingerprints

Where content is genuinely planned-but-not-yet-shipped, the path READMEs say so explicitly with the 📋 marker and a "what's coming" section.

## How to contribute

[`CONTRIBUTING.md`](../CONTRIBUTING.md) is the canonical guide. The short version:

- New concept pages, math pages, recipes, and labs are welcomed
- New project briefs and pattern pages require a Discussion before drafting
- All content follows the per-folder template (concepts page template / lab template / project brief template / etc.)
- Source citations are required for any technical claim — see CONTRIBUTING for the citation rules

For first-time contributors, the [`good-first-issue`](https://github.com/MHHamdan/Agentic-AI-Engineer/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) label on GitHub Issues is the entry point.

## Quick reference — file types

| Extension | What it is |
|---|---|
| `.md` | Markdown content; renders on GitHub. Most repo content is `.md`. |
| `.ipynb` | Jupyter notebook; renders on GitHub with outputs visible. All labs are notebooks. |
| `.py` | Python source; usually in lab `solution/` directories or `examples/` |
| `.toml` / `.txt` / `.lock` | Environment files (`pyproject.toml`, `requirements.txt`, `uv.lock`) |
| `.cff` | Citation format file ([CITATION.cff](../CITATION.cff)) |
| `.mermaid` / `.svg` | Diagram sources and rendered output in [`diagrams/`](../diagrams/) |

## See also

- [`docs/start-here.md`](./start-here.md) — the 5-minute orientation; read first if you haven't
- [`README.md`](../README.md) — the repo's landing page with the Choose-Your-Path table
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — how to contribute content
- [`CHANGELOG.md`](../CHANGELOG.md) — what's been added and when
- [`learning-paths/README.md`](../learning-paths/README.md) — the full path catalog with current statuses
