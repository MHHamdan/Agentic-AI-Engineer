# ⚙️ Tools · LangGraph

> 🔴 Fast-changing. Pages here carry a verified-as-of date in their header. Treat anything older than ~3 months with caution and run the freshness check.

This folder holds the versioned tool snapshots and migration notes for LangGraph as used elsewhere in the repo. The structure mirrors what we do for any 🔴-tier dependency:

- One **snapshot page per major version line** (`snapshot-v1.0.md` covers the `1.x` series).
- Future **migration notes** (e.g., `migrate-0.x-to-1.0.md`) when a major-version cut creates user-visible breakage.

## Current pages

| Page | What it covers | Verified |
|------|----------------|----------|
| 📌 [snapshot-v1.0.md](./snapshot-v1.0.md) | LangGraph `1.x` series — pinned APIs, deprecations, tradeoffs | 2026-05-23 |

## Where this is used in the curriculum

- 🧪 [Lab 05: LangGraph rewrite of Lab 01](../../labs/05-langgraph-rewrite/) — primary consumer
- 📖 [Agents vs. frameworks](../../concepts/agents/agents-vs-frameworks.md) — the conceptual framing for "when does a framework pay off?"
- 🧠 [LangGraph basics quiz](../../quizzes/foundations/langgraph-basics.md)
- 🗺 [Foundations path](../../learning-paths/01-foundations/README.md) — Module 6

## How to update

When LangGraph ships a release that affects content in this repo:

1. **Patch (`1.0.x` → `1.0.y`)** — no action unless a CVE or behavior bug affects the labs. Verify the latest version in the snapshot's table and bump the verification date.
2. **Minor (`1.0` → `1.1`)** — re-run the freshness check at the bottom of the snapshot page. Add new APIs to the "stable APIs" list if the labs are about to start using them. Bump verification date.
3. **Major (`1.x` → `2.0`)** — create a new `snapshot-v2.0.md` page. Keep `snapshot-v1.0.md` around with a "superseded by 2.0" banner. Write a `migrate-1.x-to-2.0.md` note. Bump verification dates on dependent pages and update lab notebooks to the new APIs.

In every case, add an entry to the `[Unreleased]` section of [`CHANGELOG.md`](../../CHANGELOG.md) under **Verified Tool Snapshots** with the new version, verification date, and primary source link.

## What's not here (and why)

We don't try to be comprehensive. The point of these snapshots is to **pin what the curriculum uses**, not to mirror upstream docs. If you want the full API surface, the [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview) are the source — we link there from every page.
