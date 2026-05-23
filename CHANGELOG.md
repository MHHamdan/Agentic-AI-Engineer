# Changelog

All notable changes to this repository are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), with one repo-specific section added: **Verified Tool Snapshots**.

---

## Versioning policy

This repository is versioned semantically, with content-aware semantics:

- **Major version (X.0.0):** A reorganization that breaks existing links or the learning-path structure. Rare.
- **Minor version (0.X.0):** New content tracks, new learning paths, or substantial expansions to existing sections.
- **Patch version (0.0.X):** Individual concept, lab, recipe, or pattern additions; tool-snapshot updates; bug fixes; typo fixes.

Releases are tagged on `main` as `vX.Y.Z`. The `CHANGELOG.md` is the source of truth for what changed; GitHub release notes link back to it.

Because this is an evolving educational resource and not a software library, we don't promise backwards-compatible URLs across major versions. We do promise to provide migration notes when major reorganizations happen.

---

## Tool snapshot policy

Pages in `tools/` and any code that depends on a specific framework version carry a snapshot date in this form:

```
> 🔴 Tool snapshot — <tool> v<version>, verified YYYY-MM-DD
> Source: <official docs / changelog / spec link>
```

Tool snapshots are tracked separately in the **Verified Tool Snapshots** section of each release. When you update a snapshot:

1. Update the badge on the relevant `tools/<tool>/` page.
2. Add a line to the current `[Unreleased]` section under **Verified Tool Snapshots**.
3. Include a primary-source link in your PR description.

Routine snapshot sweeps happen at minor releases. Individual updates land continuously between releases.

When a tool ships a breaking change (e.g., `langgraph.prebuilt` → `langchain.agents`), the snapshot update is paired with a migration note on the tool page and, if needed, code updates across labs and recipes.

---

## [Unreleased]

### Added

- **First curriculum content batch — Foundations.**
  - `concepts/agents/what-is-an-agent.md` — foundational concept page; the most-linked page in the repo.
  - `concepts/agents/agent-loop.md` — the four-step perceive/reason/act/observe cycle.
  - `concepts/agents/react-pattern.md` — ReAct prompting pattern with Yao et al. (ICLR 2023) citation.
  - `math-foundations/notation.md` — symbol and convention reference.
  - `math-foundations/04-agents-as-policies.md` — first real math page; $\pi_\theta(a_t \mid s_t)$ framing.
  - `math-foundations/06-react-formalization.md` — ReAct as a specialization of the policy.
  - `labs/01-first-agent-from-scratch/README.md` — lab brief.
  - `labs/01-first-agent-from-scratch/lab.ipynb` — ~150-line ReAct agent in pure Python, provider-agnostic (OpenAI default, Anthropic swap-in). Notebook outputs stripped; sample outputs in markdown cells.
  - `learning-paths/01-foundations/README.md` — curated reading list for the Foundations path.
  - `diagrams/agent-loop.mmd` — Mermaid source for the canonical agent-loop diagram.

- **`SECURITY.md`** (from previous patch batch) — closes the last Community Standards row; private reporting channel via GitHub Security Advisories.

### Changed

- **`CITATION.cff`** — `date-released` set to actual release date (`2026-05-23`). Passes `cffconvert --validate`.
- **`.lycheeignore`** — removed patterns for content now authored (concept pages, math notes, lab 01, learning-paths/01-foundations).
- **`.github/workflows/ci.yml`** — cleaner empty-repo handling, `markdownlint` made informational, lychee uses auto-detected `.lycheeignore` (no broken `--exclude-path` flag).
- **Internal links** in `README.md`, `CONTRIBUTING.md`, `LICENSING.md`, `docs/start-here.md`, `tools/README.md`, `diagrams/README.md` — converted GitHub-relative URLs (`../../issues`, `../../discussions`) to absolute `https://github.com/MHHamdan/Agentic-AI-Engineer/...` URLs; de-linked template placeholder paths to avoid false-positive link errors.

### Fixed

- Two CI failures from the initial v0.1.0 push: `Validate metadata` (placeholder date in `CITATION.cff`) and `Check Markdown links` (49 broken or forward-reference links). All CI jobs now pass.

### Verified Tool Snapshots

- `openai` ≥ 1.40 — verified 2026-05-23 (used in Lab 01).
- `anthropic` ≥ 0.34 — verified 2026-05-23 (used in Lab 01 as alternative provider).
- `pydantic` ≥ 2.7 — verified 2026-05-23 (used for tool schemas in Lab 01).

---

## [0.1.0] — Initial public release

The first public release of the Agentic AI Engineer learning hub. This release establishes the repository's identity, structure, and infrastructure. Content sections are scaffolded but mostly empty — they fill in over subsequent releases.

### Added

- **Root identity.** `README.md` defining mission, audience, and structure. Dual-license declaration (Apache-2.0 for code, CC-BY-4.0 for prose and diagrams).
- **Community infrastructure.**
  - `CONTRIBUTING.md` with content templates for concepts, labs, recipes, and tool-page updates.
  - `CODE_OF_CONDUCT.md` based on the Contributor Covenant.
  - `CITATION.cff` for academic citation.
  - `CHANGELOG.md` (this file) with versioning and tool-snapshot policies.
- **Top-level scaffold.** Empty directories with stub READMEs for:
  - `docs/` — onboarding and FAQ
  - `learning-paths/` — nine curated paths
  - `concepts/` — stable explainers
  - `math-foundations/` — engineer-useful math
  - `labs/` — hands-on guided exercises
  - `recipes/` — copy-paste solutions
  - `patterns/` — architecture patterns
  - `projects/` — Build Challenges and Capstone Projects
  - `examples/` — minimal reference implementations
  - `tools/` — versioned snapshots
  - `evaluation/`, `production/`, `security/`
  - `diagrams/`, `references/`, `glossary/`, `setup/`, `assets/`
- **Onboarding pages.**
  - `docs/start-here.md` — 5-minute repo tour.
  - `setup/README.md` — environment setup.
  - `learning-paths/README.md` — path overview and prerequisite map.
- **License files.** `LICENSE` (Apache-2.0), `LICENSE-CC-BY-4.0` (Creative Commons Attribution 4.0).
- **Environment scaffolding.** `pyproject.toml`, `.env.example`, `.gitignore`.

### Changed

- *(N/A — initial release.)*

### Fixed

- *(N/A — initial release.)*

### Verified Tool Snapshots

The following snapshots were checked against official sources at the time of release. Each `tools/<tool>/` page carries its own verification footer with the source link.

| Tool / Spec | Version / Status | Verified | Primary source |
|---|---|---|---|
| Model Context Protocol | Spec `2025-11-25` (current stable); RC `2026-07-28` announced | 2026-05-23 | [modelcontextprotocol.io/specification/2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25); [MCP blog — RC announcement](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) |
| Agent2Agent (A2A) Protocol | `v1.0` released; Linux Foundation project since June 2025 | 2026-05-23 | [a2a-protocol.org](https://a2a-protocol.org/latest/); [Announcing v1.0](https://a2a-protocol.org/latest/announcing-1.0/) |
| LangGraph | `1.0` GA (Oct 2025); `langgraph.prebuilt` deprecated → `langchain.agents` | 2026-05-23 | [LangGraph 1.0 GA — changelog](https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available) |
| LangChain | `1.0` GA (Oct 2025); introduces `create_agent`, middleware system | 2026-05-23 | [LangChain 1.0 GA — changelog](https://changelog.langchain.com/announcements/langchain-1-0-now-generally-available) |
| LangSmith | Snapshot pending; see `tools/langsmith/` for current verification | — | [changelog.langchain.com](https://changelog.langchain.com/) |
| Google ADK | Snapshot pending; see `tools/google-adk/` | — | [google.github.io/adk-docs](https://google.github.io/adk-docs/) |
| CrewAI | Snapshot pending; see `tools/crewai/` | — | Official repo and docs |
| AutoGen | Snapshot pending; see `tools/autogen/` | — | Official repo and docs |
| OpenAI Agents SDK | Snapshot pending; see `tools/openai-agents-sdk/` | — | Official repo and docs |
| Vector DBs (pgvector, Pinecone, Qdrant, Weaviate, Chroma) | Snapshots pending per page | — | Official docs per tool |

"Snapshot pending" means the tool page exists or is planned but a full verification pass has not yet been completed for this release. Contributions to fill in pending snapshots are welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md#how-to-update-a-tools-page).

---

## How to use this file as a contributor

When you open a PR that changes content meaningfully, add an entry under the appropriate subsection of `[Unreleased]`. Use the past tense and link to the changed pages. Maintainers will move `[Unreleased]` to a numbered release when cutting a tag.

Examples of good entries:

```
### Added
- `recipes/parse-structured-output-safely.md` — Pydantic-based parser with retry on validation failure.
- `concepts/agents/reflection-pattern.md` — explainer on self-correcting agent loops with Reflexion citation.

### Changed
- `tools/langgraph/state-and-checkpoints.md` — rewrote for `langgraph.checkpoint.postgres` API changes.

### Verified Tool Snapshots
- `tools/langgraph/` — bumped to `1.2.x`, verified YYYY-MM-DD. Source: [link].
```

Trivial changes (typo fixes, broken links) don't need changelog entries.
