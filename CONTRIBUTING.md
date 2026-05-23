# Contributing to Agentic AI Engineer

Thanks for considering a contribution. This repo is maintained as a community resource for working engineers, and most of what we ship comes from people who hit a real problem and wrote down what they learned. That's the kind of contribution we value most.

---

## Contribution philosophy

A few principles that shape what we accept:

- **Engineering over hype.** We don't ship "X is the future of AI" content. We ship "here's the failure mode, here's the fix, here's why it works."
- **Stable separated from volatile.** Concepts, math, and patterns are written to last. Tool-specific content is dated and isolated so it can be updated without rewriting everything around it.
- **Sources over confidence.** When a claim is non-obvious or version-dependent, cite it. When you can't cite it, soften the claim or remove it.
- **Show your work.** Working code beats prose. A recipe with a runnable snippet beats three paragraphs of explanation.
- **Small is fine.** A one-line fix to a stale version number is a great PR. So is a typo.

---

## Types of contributions accepted

We actively want:

| Type | What it looks like |
|---|---|
| **New recipes** | A real problem you solved, with a runnable snippet. |
| **New concept pages** | A focused explainer on a stable idea (10-minute read). |
| **New labs** | A guided hands-on notebook + README, tested locally. |
| **New patterns** | An architecture pattern with a Mermaid diagram and tradeoffs. |
| **Tool-page updates** | Bumping a version, adding a deprecation note, refreshing a snapshot date. |
| **Translations** | Concept and pattern pages, primarily. |
| **Showcase entries** | A community project that uses the material. |
| **Bug fixes** | Broken links, stale code, mis-rendered Mermaid, wrong math. |
| **Issues** | Reports of unclear, wrong, or outdated content. |

What we're cautious about:

- **New frameworks pages** unless the framework is widely adopted. We'd rather cover six tools well than 30 thinly.
- **Long opinion pieces.** This isn't a blog. Strong opinions belong in patterns ("when NOT to use") with diagrams and tradeoffs.
- **Marketing content.** If your contribution promotes a specific commercial product without engineering substance, it will be declined.

If you're not sure whether a contribution fits, open a [Discussion](../../discussions) before investing time.

---

## How to add a concept page

Concept pages live in `concepts/<category>/<name>.md`. Categories include `agents/`, `llms/`, `rag/`, `tools/`, `multi-agent/`, `protocols/`, `context/`, `memory/`, `evaluation/`, `safety/`.

Use this template:

````markdown
# <Concept name>

> 🟢 Stable · ⏱ ~N min read · 🏷 tag1, tag2

## TL;DR

Two or three sentences. The reader should be able to stop here and have the gist.

## The problem this solves

What goes wrong without this concept. Concrete examples are better than abstractions.

## How it works

The mechanism. Diagrams are encouraged — use Mermaid in-page or link to `diagrams/`.

## When to use it

Two or three specific situations.

## When NOT to use it

Two or three failure modes or wrong-fit situations.

## Common failure modes

Bullets. Things that bite you in production.

## 🧮 Math behind it (optional)

A short inline equation if it sharpens the engineering intuition, with a link to the full
treatment in `math-foundations/`.

## See also

- Math: [`math-foundations/...`](../../math-foundations/...)
- Lab: [`labs/...`](../../labs/...)
- Pattern: [`patterns/...`](../../patterns/...)

## References

- Author, *Title*, venue, year. [link]
````

**Guidelines:**

- Keep it focused on one concept. Two concepts is two pages.
- Aim for 600–1500 words. If you go longer, it's probably two pages.
- Cite any non-obvious technical claim.
- Don't repeat tool-specific syntax inside a concept page — that belongs in `tools/`.

---

## How to add a lab

Labs live in `labs/NN-name/` with a `README.md` and a `lab.ipynb` (and optionally a `solution/` subfolder).

Use this template for the README:

````markdown
# Lab N: <name>

> 🟢 / 🟡 / 🔴 difficulty · ⏱ ~N min · 📊 Beginner / Intermediate / Advanced

## 🎯 Goal

One sentence describing what the learner will be able to do after this lab.

## 📋 Prerequisites

- Concept pages they should read first (with links).
- Other labs they should complete first (with links).
- API keys or local models they need.

## 🛠 Tools and versions

- `<tool>` `<version>` — verified as of YYYY-MM-DD. Source: [link].

## What you'll build

Brief, with a screenshot or terminal output if helpful.

## What you'll learn

Three to five concrete takeaways.

## Step 0: Setup

## Step 1: ...

## Step N: ...

## Stretch goals

Optional extensions for learners who want more.

## Solution discussion

What the working solution looks like and why it works. Link to `solution/` if you ship one.

## 🧮 Going deeper

Links into `math-foundations/` for the relevant theory.
````

**Notebook conventions:**

- Cells should be runnable top-to-bottom without manual edits beyond the `.env` file.
- Use `python-dotenv` for API keys. Never commit a key.
- Pin notable libraries with a version range, not an exact version.
- Strip outputs before committing: `jupyter nbconvert --clear-output --inplace lab.ipynb`.
- Add a final cell that prints "✓ Lab complete" so smoke tests can detect success.

---

## How to add a recipe

Recipes live in `recipes/<imperative-name>.md`. The filename is a command: `add-retry-with-backoff.md`, `parse-structured-output-safely.md`, `deploy-agent-to-fastapi.md`.

Use this template:

````markdown
# Recipe: <Imperative title>

> ⏱ ~N min · 🛠 `<tool>` `<version>` (verified YYYY-MM-DD)

## Problem

One or two sentences. What's broken or missing.

## Solution

```python
# Working code, top of the file. Copy-pasteable as-is.
```

## Why this works

Three or four sentences. The engineering intuition.

## Gotchas

- Bullet list of common pitfalls.

## Variations

- "If you also need X, do Y."

## See also

- Concept: [`concepts/...`](../concepts/...)
- Pattern: [`patterns/...`](../patterns/...)
````

**Guidelines:**

- The code should run with minimal setup. Imports at the top, no hidden state.
- One problem per recipe. If you find yourself writing two, split into two recipes.
- Include the version you tested against. Recipes age faster than concepts.

---

## How to update a tools page

Tool pages live in `tools/<tool-name>/`. They're the most volatile part of the repo.

When you update a tool page, you must:

1. **Update the version badge** at the top of the page:

   ```markdown
   > 🔴 Tool snapshot — <tool> v<version>, verified YYYY-MM-DD
   > Source: <link to official release notes / changelog / spec>
   ```

2. **Update any breaking-change notes.** If APIs renamed, deprecated, or moved, add a migration note.

3. **Test any code snippets** against the new version. Stale snippets are worse than no snippet.

4. **Add an entry to [`CHANGELOG.md`](./CHANGELOG.md)** under "Verified Tool Snapshots":

   ```
   - `tools/<tool>/` — bumped to <version>, verified YYYY-MM-DD.
   ```

5. **Open the PR with the label `tool-snapshot`.** Maintainers prioritize these.

Stale tool pages are tracked via the [`stale-tool-version`](../../issues?q=label%3Astale-tool-version) issue label. If you spot one without fixing it, opening the issue is a real contribution.

---

## Style guide

### Voice

- Direct, second person, present tense. "You build a graph. The graph fails. You add retries."
- No hype words: *revolutionary, cutting-edge, game-changing, paradigm shift, unleash, supercharge*.
- No corporate hedging: "it's important to note that," "in this section we will explore," "let's dive into." Just say the thing.
- It's okay to have an opinion. "Use Postgres for this — SQLite checkpoints break under concurrent load" is better than "there are several options."

### Formatting

- **Headings:** Sentence case, not Title Case. (`## How retrieval works`, not `## How Retrieval Works`.)
- **Code:** Triple-backtick fenced blocks with a language tag (`python`, `bash`, `json`, `yaml`).
- **Inline code:** Backticks around identifiers, file paths, CLI commands.
- **Lists:** Use them when items don't flow as prose. Don't bulletize paragraphs.
- **Tables:** Used for comparison, decision aids, and version matrices. Not for prose disguised as rows.
- **Emoji icons:** Use the repo's vocabulary consistently — 📖 concept, 🧪 lab, 🧰 recipe, 🏛 pattern, 🚀 project, 🧮 math, ⚙️ tool, 🟢/🟡/🔴 stability or difficulty. Don't add new ones casually.
- **Mermaid:** Inline for diagrams under ~20 nodes. For larger diagrams, store the `.mmd` source in `diagrams/` and link to the rendered image.

### Math

- Use GitHub-flavored MathJax: `$...$` inline, `$$...$$` block.
- Define every symbol the first time it appears.
- Every equation needs a citation or a "definitional" note.
- No invented notation. If a paper uses $\pi(a \mid s)$, we use $\pi(a \mid s)$ too.
- Math sections must include the *what / why / where / source* template from the [math-foundations README](./math-foundations/README.md).

### Code

- Python 3.11+ is the floor. We use `from __future__ import annotations` and PEP 604 union syntax (`int | None`).
- Type hints on all public functions.
- `ruff` for linting, `black` for formatting (line length 100).
- Async by default for I/O-bound agent code. Don't mix sync and async in the same module.
- Real error handling. `except Exception: pass` is grounds for rejection.

### Filenames

- Folders: `kebab-case` (`learning-paths/`, `agentic-rag/`).
- Markdown files: `snake_case.md` or short kebab — be consistent within a folder.
- Numbered files: zero-padded (`01_...`, not `1_...`).
- Notebooks: match the README filename inside the same folder.

---

## Citation and source rules

This is the rule that protects the repo's credibility. Read it carefully.

1. **Every version claim needs a primary source.** If you write "LangGraph 1.0 is the first stable release," link the official changelog entry. Wikipedia and blog summaries are acceptable as secondary sources but not as the only citation.

2. **No invented numbers.** Don't write "adopted by 1000+ companies" unless you can link the source. If the source is marketing material, soften it: "promoted by Vendor X as widely adopted, per their announcement."

3. **No invented equations.** Use standard formulations from the original paper. If you can't find a citation for an equation, it shouldn't be in the repo.

4. **Mark working drafts.** If you're contributing content that includes claims you couldn't verify, add a `> ⚠️ This page contains unverified claims marked with [needs source]` callout at the top. Maintainers can help fill them in.

5. **Future-dated content is not allowed.** Don't write about a release that hasn't shipped yet as if it has. If you mention an RC or a roadmap item, label it as such and link to the announcement.

6. **External quotes:** Short, attributed, and only when paraphrasing would lose meaning. Don't reproduce paragraphs from external sources — link to them.

---

## Pull request checklist

Before opening a PR, check each item below. PRs that miss multiple items will be sent back without review.

**Content**

- [ ] The page or notebook follows the relevant template above.
- [ ] The voice and formatting match the [style guide](#style-guide).
- [ ] No hype words, no corporate filler.
- [ ] Headings use sentence case.
- [ ] All non-obvious claims cite a source.
- [ ] All tool-version references include a *verified as of YYYY-MM-DD* note and a source link.
- [ ] Math (if any) defines its symbols and cites its source.

**Code**

- [ ] Code runs end-to-end with only the `.env` file populated.
- [ ] Notebook outputs are stripped (`jupyter nbconvert --clear-output --inplace`).
- [ ] No API keys, tokens, or personal paths committed.
- [ ] Linted with `ruff` and formatted with `black`.
- [ ] Type hints on public functions.

**Cross-linking**

- [ ] Linked from any relevant concept page, pattern, or learning path.
- [ ] Internal links use relative paths (`../concepts/...`), not absolute URLs.
- [ ] Mermaid diagrams render correctly on GitHub (preview the PR).

**Repo hygiene**

- [ ] PR title follows the form `<type>: <short description>` where `<type>` is one of `content`, `recipe`, `lab`, `tool-snapshot`, `fix`, `docs`, `chore`.
- [ ] PR description explains *why*, not just *what*.
- [ ] If the PR adds or changes a tool snapshot, a `CHANGELOG.md` entry is included.
- [ ] If the PR closes an issue, the description includes `Closes #<issue-number>`.

---

## Reporting issues

Open an issue when:

- You spot stale tool versions (`stale-tool-version` label).
- A code snippet no longer runs (`bug` label).
- A concept is unclear or wrong (`docs` label).
- You want a new recipe, lab, or pattern (`enhancement` label).

For security-sensitive issues (e.g., a recipe that demonstrates an exploit unsafely), please email the maintainers rather than opening a public issue.

---

## Code of conduct

This project follows the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be useful, be respectful, assume good faith.

---

## What happens after you submit

- A maintainer will triage within a few days. We're a small group; please be patient.
- Reviews focus on engineering substance first, style second.
- We may suggest splitting a large PR into smaller ones.
- Once merged, your contribution is credited in the page's footer via Git history.

Thanks for making this better.
