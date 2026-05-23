# Licensing

This repository uses **two licenses**, applied to different kinds of content. This page explains which license covers what, how to attribute, and what to do if something is unclear.

If you only need a quick answer:

- **Reusing code, notebooks, scripts, configs?** → [Apache License 2.0](./LICENSE).
- **Reusing prose, diagrams, illustrations, or curriculum structure?** → [Creative Commons Attribution 4.0 International](./LICENSE-CC-BY-4.0).
- **Both?** Attribute both. Linking back to this repo satisfies attribution for both licenses.

---

## What's covered by Apache-2.0

Apache License 2.0 covers everything that's **executable, configurable, or programmatic**:

- All `.py` files
- All `.ipynb` notebooks (cell contents — both code cells and any embedded docstrings)
- `pyproject.toml`, `requirements*.txt`, lockfiles
- `.env.example` and other environment templates
- `.github/workflows/*.yml` CI configuration
- Shell scripts, Dockerfiles, Makefiles
- Any other code you'd `import`, `run`, or `execute`

You can use this code commercially, modify it, distribute it, and build proprietary products on top of it, subject to the standard Apache-2.0 conditions: preserve the copyright notice, indicate changes, and keep the license text with the distribution. Apache-2.0 also includes an explicit patent grant, which we chose specifically because some patterns in this repo touch on production deployment techniques.

The canonical license text lives in [`LICENSE`](./LICENSE).

---

## What's covered by CC-BY-4.0

Creative Commons Attribution 4.0 International covers everything that's **written or visual**:

- All `.md` Markdown content — concept pages, recipe explanations, pattern write-ups, README files, learning-path overviews, and so on
- Markdown cells inside `.ipynb` notebooks (the prose between code cells)
- All Mermaid diagram sources (`.mmd`) and rendered images (`.svg`, `.png`)
- Architecture diagrams, illustrations, screenshots
- Curriculum structure (the way learning paths, concepts, and labs are organized)
- Math notes and the equation explanations in `math-foundations/`

You can reuse, translate, adapt, and build on this material — including for commercial use — provided you give appropriate credit, link back to the source, and indicate if changes were made. CC-BY-4.0 does not require derivative works to use the same license, so if you adapt a concept page into your own course, you can license your version however you like.

The canonical license text lives in [`LICENSE-CC-BY-4.0`](./LICENSE-CC-BY-4.0).

---

## Why a dual license

A single license never fits both code and curriculum well:

- **Apache-2.0** is the right answer for code: it's permissive, widely understood, OSI-approved, and explicit about patents. Choosing CC-BY-4.0 for code would technically work but isn't what either license was designed for, and would surprise downstream users.
- **CC-BY-4.0** is the right answer for educational prose: it's the standard for openly licensed teaching material, well-understood by educators, and explicit about attribution. Apache-2.0 isn't designed for textual content and produces awkward attribution requirements for short excerpts.

This split follows the same approach used by major open educational projects (e.g., MDN Web Docs, many university OER initiatives).

---

## Mixed files

Some files contain both code and prose:

| File type | Code cells | Markdown cells | Practical guidance |
|---|---|---|---|
| `.ipynb` notebooks | Apache-2.0 | CC-BY-4.0 | Attribute the repo. In practice, one attribution covers both. |
| `.md` files containing fenced code blocks | Apache-2.0 (the code block) | CC-BY-4.0 (the prose around it) | Same — one attribution covers both. |

If you're reusing only the code from a notebook or only the prose from a Markdown file, the relevant license applies on its own.

---

## How to attribute

When reusing either kind of content, please include:

1. The title of the source (`Agentic AI Engineer`).
2. A link back to this repository.
3. The license (Apache-2.0 for code, CC-BY-4.0 for prose).
4. An indication of any changes you made (CC-BY-4.0 specifically requires this; Apache-2.0 has the same effect via the "Changes" requirement in §4(b)).

A single example covers most reuse cases:

```
Adapted from "Agentic AI Engineer" — https://github.com/<your-org>/agentic-ai-engineer
Code under Apache-2.0; prose and diagrams under CC-BY-4.0. Changes: <brief description>.
```

If you're embedding a single recipe or diagram in a blog post, a one-line credit linking to the source is sufficient.

---

## What this license does *not* cover

The licenses above cover original content in this repository. They do not extend to:

- **External libraries and dependencies.** Each library brings its own license. The `pyproject.toml` and `requirements.txt` files list them; check each one if you're packaging a redistribution.
- **Trademarks and product names** mentioned in the repo (e.g., LangGraph, LangSmith, Anthropic, OpenAI, Google ADK, MCP, A2A). Naming a product to discuss it is fine; using a logo or claiming endorsement is not granted by either license.
- **Cited papers, books, and external articles.** When we link to or briefly quote external sources, those remain under their original licenses. We follow the citation rules in [`CONTRIBUTING.md`](./CONTRIBUTING.md#citation-and-source-rules).
- **Community contributions before they're merged.** Once a PR is merged, the contributor agrees to the repo's dual-license terms by the act of contributing (this is implicit in the standard "inbound = outbound" GitHub flow, and stated explicitly in [`CONTRIBUTING.md`](./CONTRIBUTING.md)).

---

## If a file is unclear

If you can't tell which license applies to a particular file, default to the stricter interpretation (attribute under both) and open an issue. We'd rather clarify than leave ambiguity in the repo.

---

## Recommended files for this repo

A clean repo carries these license-related files:

| File | Purpose |
|---|---|
| [`LICENSE`](./LICENSE) | Full Apache-2.0 license text. GitHub auto-detects this and displays the license badge. |
| [`LICENSE-CC-BY-4.0`](./LICENSE-CC-BY-4.0) | Full Creative Commons Attribution 4.0 license text. |
| [`LICENSING.md`](./LICENSING.md) | This page — the explainer that disambiguates what's covered by what. |
| `NOTICE` *(optional)* | Apache-2.0 NOTICE file, added if/when third-party code is bundled. |

Both `LICENSE` and `LICENSING.md` are referenced from the root [`README.md`](./README.md) and from [`CONTRIBUTING.md`](./CONTRIBUTING.md).
