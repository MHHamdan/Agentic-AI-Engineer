# Projects

Substantial builds that combine work across multiple paths. Two tiers:

- **Build Challenges** — beginner and intermediate. Time-boxed builds (a few hours to a couple of days) with a clear deliverable.
- **Capstone Projects** — advanced. End-to-end systems with evaluation, observability, deployment, and a write-up you can show off.

## Folder structure

```
projects/
├── beginner/          Build Challenges for early learners
├── intermediate/      Build Challenges combining 2–3 paths
└── capstone/          Full-stack agentic systems
```

Each project folder contains:

```
projects/<tier>/NN-name/
├── README.md          The brief: goal, architecture, milestones, rubric
├── starter/           Working starter code (optional)
└── solution/          Reference implementation (optional)
```

## Planned catalog

The initial set covers most production patterns:

### Beginner

| # | Project | Status |
|---|---|---|
| 01 | [Personal research assistant](./beginner/01-personal-research-assistant/) | ✅ Brief shipped (Batch 62) |
| 02 | [PDF Q&A bot](./beginner/02-pdf-qa-bot/) | ✅ Brief shipped (Batch 63) |

See [`./beginner/`](./beginner/) for the tier landing page.

### Intermediate

| # | Project | Status |
|---|---|---|
| 03 | [Project management agent](./intermediate/03-project-management-agent/) | ✅ Brief shipped (Batch 63) |
| 04 | Data analysis agent | 📋 Brief planned |
| 05 | Multi-server MCP agent | 📋 Brief planned |

See [`./intermediate/`](./intermediate/) for the tier landing page.

### Capstone

| # | Project | Status |
|---|---|---|
| 06 | Financial research analyst | 📋 Brief planned |
| 07 | [Evaluated multi-agent system](./capstone/07-evaluated-multi-agent-system/) | ✅ Brief shipped (Batch 62) |
| 08 | Production-ready deep research | 📋 Brief planned |

See [`./capstone/`](./capstone/) for the tier landing page.

## How to approach a project

1. **Read the brief end-to-end** before writing any code. The architecture diagram tells you which paths the project draws from.
2. **Pick a deployment target up front** — local-only, FastAPI + Docker, or hosted. Different targets change the architecture.
3. **Build a tiny version first.** Get end-to-end flow working with stub data before optimizing any one piece.
4. **Add observability early.** A traced agent is a debuggable agent.
5. **Evaluate before you ship.** Even a 20-example golden set tells you more than running it once and checking the output.

## Showcase

When you finish a project — your build, your fork, your variation — please consider adding it to [`docs/community/showcase.md`](../docs/community/showcase.md). A screenshot and a paragraph is plenty. We highlight community builds in the README rotation.

## Contributing

New project briefs are very welcome but go through more design review than recipes or concept pages — open a Discussion before drafting. See [`CONTRIBUTING.md`](../CONTRIBUTING.md).

> 🔴 Capstones depend on fast-changing tools. Project READMEs carry their own *verified-as-of* dates.
