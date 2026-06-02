# Troubleshooting

Common errors and their fixes. The smoke test (`python -m setup.verify`) points you here by section when it fails. If your problem isn't listed, open an issue with the `bug` label and include the full error and your `python --version`.

## Imports fail

The smoke test's first step imports the core libraries. A failure here is almost always an environment problem, not a code one.

- **`ModuleNotFoundError`** — the dependencies aren't installed in the environment you're running. Re-run `uv sync` (or `pip install -r requirements.txt`), and confirm you're in the right environment (`which python`). If you use notebooks, the kernel may point at a different interpreter than your shell — select the project environment as the kernel.
- **`SyntaxError` on `int | None`** — you're on Python 3.10 or earlier. The repo targets 3.11+. See [`python-environment.md`](./python-environment.md) for pinning a supported version.
- **A library imports but at the wrong version** — a stale environment. Recreate it from the lockfile rather than upgrading in place: remove the virtualenv and `uv sync` again.

## No API key found

The second step checks that at least one model-provider key is set.

- Confirm `.env` exists (copy it from `.env.example`) and holds at least one key. The minimal set for the foundations labs is in [`README.md`](./README.md).
- Confirm the process actually loads `.env`. If you export keys in your shell instead, make sure they're present in the same shell that runs the test (`echo $OPENAI_API_KEY`).
- A key set to an empty string still counts as "set" to some loaders but fails the call — remove the line rather than leaving it blank.

## The API call fails

The third step makes one low-cost call to confirm the key works.

- **401 / authentication error** — the key is wrong, revoked, or for a different provider than the variable name implies. Re-issue it from the provider console.
- **429 / rate or quota error** — you're out of quota or sending too fast. Check the provider's usage dashboard; a brand-new key sometimes needs billing enabled before any call succeeds.
- **Connection / timeout errors** — a proxy or firewall is blocking the provider. The labs only need outbound HTTPS to the provider you configured.

## A lab notebook breaks against a newer framework version

The labs are pinned to the versions in the lockfile. If you've upgraded a framework (or installed outside the lockfile), a notebook can break on a renamed import or a changed signature.

- First, reproduce against the pinned versions (`uv sync`) to confirm it's a version drift and not a bug in the lab.
- Check [`CHANGELOG.md`](../CHANGELOG.md) under **Verified Tool Snapshots** for the version each lab was verified against, and the affected tool page for migration notes on major upgrades (e.g., LangChain/LangGraph 1.0).
- If a lab is broken against the *pinned* version, that's a real bug — open an issue with the `bug` label and the full traceback.

## A lab can't find its data or a sibling file

- Run notebooks from the lab's own directory (or the repo root, as the lab's README states). Relative paths like `./data/...` assume the documented working directory.
- If a lab reads from a sibling lab's toolkit (the operating-the-loop labs do), keep the repo layout intact — those imports are by relative path.

## Smoke test passes but a specific lab still fails

A green smoke test only confirms imports, a key, and one call. A lab can still fail on its own dependencies (a vector store, a local model download, a dataset). Read the lab's **Prerequisites** and **Setup** sections — they list anything beyond the base environment.
