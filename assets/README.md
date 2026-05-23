# Assets

Working artifacts — content that supports the curriculum but isn't user-facing.

## What lives here

| Subfolder | Purpose |
|---|---|
| `slides-ocr/` | OCR'd content from source slide decks, used as raw material when authoring concept pages |
| `images/` | Screenshots, illustrations, and other static images referenced from concept and lab pages |

## Why this is separated

The curriculum is the published artifact. Slide OCR, working drafts, and other intermediate material are useful for contributors but would clutter the learner-facing experience if mixed in.

A few rules that follow from this:

- **Nothing in `assets/slides-ocr/` is the curriculum.** It's source material we transform from, not content we publish. The published concept pages are independently authored from outlines; they don't copy slide text.
- **Images in `assets/images/` are referenced from elsewhere.** If you add an image, you usually add it as part of a concept page or lab PR — not on its own.
- **`assets/` is exempt from the "every folder gets a learner-facing README" rule.** The folder's README is this one — for contributors, not learners.

## Contributing

If you're contributing a concept page derived from a source you own (your own slides, your own notes, a paper you wrote), the working notes can live here while the polished page is being drafted. Once the published page is in `concepts/`, the working draft can be removed or kept as historical reference.

If you're adding screenshots to a lab, drop them in `assets/images/lab-<NN>/` and reference them from the lab's notebook or README.

> ⚙️ Working artifacts. Not classified stable / slow / fast — this folder isn't part of the curriculum.
