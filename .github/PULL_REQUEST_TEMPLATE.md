<!--
Thanks for contributing! This template is auto-loaded on every PR.
Replace placeholder text in <angle brackets> with your details, then delete this comment.
-->

## What this PR does

<one or two sentences on the change>

## Type of change

<!-- Pick one (and only one) by replacing [ ] with [x] -->
- [ ] `content` — new or improved concept, math note, recipe, or pattern
- [ ] `lab` — new or updated lab
- [ ] `tool-snapshot` — refresh a `tools/` page for a new version
- [ ] `recipe` — new copy-paste solution
- [ ] `fix` — bug fix (broken code, wrong claim, stale link, etc.)
- [ ] `docs` — documentation improvement (README, CONTRIBUTING, glossary, etc.)
- [ ] `chore` — repo infrastructure (CI, configs, dependencies)

## Related issues

<!-- "Closes #123" auto-closes the issue on merge. -->
Closes #

## Checklist

The full PR checklist lives in [`CONTRIBUTING.md`](../CONTRIBUTING.md#pull-request-checklist). The high-impact items:

**Content**
- [ ] Page follows the relevant template from `CONTRIBUTING.md`.
- [ ] Voice matches the style guide — no hype words, no corporate filler.
- [ ] All non-obvious claims cite a source.
- [ ] Any tool-version reference includes a *verified as of YYYY-MM-DD* note and a primary-source link.

**Code (if any)**
- [ ] Runs end-to-end with only `.env` populated.
- [ ] Notebook outputs stripped (`jupyter nbconvert --clear-output --inplace`).
- [ ] No API keys or personal paths committed.
- [ ] Linted with `ruff`, formatted with `black`.

**Cross-linking**
- [ ] Linked from any relevant concept page, pattern, or learning path.
- [ ] Internal links are relative paths.
- [ ] Mermaid diagrams render correctly (preview the PR).

**Changelog**
- [ ] If this PR adds new content or bumps a tool snapshot, `CHANGELOG.md` has an entry under `[Unreleased]`.

## Why (not just what)

<!--
What problem does this solve? What gap does it fill? If it's an opinion-bearing
change (e.g., a new pattern recommendation), what's the reasoning?
-->

## Notes for the reviewer

<!-- Anything worth flagging — design decisions, things you weren't sure about, follow-up work. -->
