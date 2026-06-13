# Style and contribution rules

These rules keep the track original, consistent, and verifiable. They mirror the conventions of the parent repository.

## Originality and attribution
- All content is written from scratch. Do not copy text from any source, including the external articles used to plan the curriculum.
- Do not include blog author names, newsletter names, or personal-name attributions from those articles anywhere in the repository.
- The external articles are a topic and sequencing guide only. They are never cited as the source of a technical claim.

## References
- Every non-obvious technical claim cites a canonical source: a peer-reviewed paper, a standard, a specification, official documentation, or a recognized benchmark.
- Prefer primary sources (the paper or the spec) over secondary write-ups.
- Collect references in `references/references.md` and link to them from concept notes.

## Writing
- Write for an engineer who knows software but is new to the specific topic. Define a term the first time it appears.
- Favor plain prose over filler. Avoid marketing language and empty intensifiers.
- Use SI-style precision: name the model, the benchmark, the version, and the date when they matter, and flag fast-moving facts as such.
- Diagrams use Mermaid and live in `diagrams/` or inline where they aid a single note.

## Labs
- Labs are runnable and offline-first. Each ships a deterministic `--self-test`.
- Keep shell usage POSIX-friendly; create files individually rather than relying on shell-specific expansion.
- A lab states clearly where it uses a stand-in and what a production version would swap in.

## Batches
- Work proceeds in numbered batches. Each content batch ships a coordinated set: concept notes, at least one runnable lab, a diagram, new glossary terms, references, and navigation updates.
- Verify before marking a batch done: self-tests pass, links resolve, counts and the changelog are updated.
- Record each batch in `CHANGELOG.md`.
