# Multimodal RAG

> Concept note. About 10 minutes to read. Related: [`retrieval-strategies.md`](./retrieval-strategies.md), [`chunking-and-indexing.md`](./chunking-and-indexing.md), [`reranking.md`](./reranking.md).

Most RAG corpora are not pure text. Product manuals have diagrams, financial filings have tables and charts, slide decks are mostly images, and scanned documents are images of text. Multimodal RAG is retrieval over a corpus where the unit of evidence can be an image (or a table, or a chart) as well as a passage, and where the generator is a vision-language model that can read what it retrieves. The design questions are how to embed mixed content into a searchable space, how to index it, and how to evaluate a system whose answers depend on pixels.

## Two architectures

**Embed everything into a shared space.** A multimodal embedding model (CLIP, SigLIP, or a newer vision-language embedder) maps both text and images into one vector space, so a text query can retrieve an image directly. One index, one query path. The cost is fidelity: CLIP-style models capture *what an image is about* well but are weak on dense text inside an image (a table of numbers, a paragraph in a screenshot), because they were trained on caption-level alignment, not document reading.

**Caption-then-embed (text as the bridge).** Run each non-text element through a vision-language model to produce a textual description — a chart becomes "bar chart of quarterly revenue, Q4 highest at $4.2M," a table becomes its Markdown — then embed and index that text alongside the real passages. Retrieval is ordinary text retrieval; at generation time you pass the model the original image *and* its description. This preserves dense in-image text and reuses your text stack, at the cost of an offline captioning pass and the captioner's errors becoming retrieval errors.

A common production hybrid keeps both: a shared-space index for "find the figure that looks like this" and a captions index for "find the figure that says this," fused with the same techniques as [hybrid search](./hybrid-search.md).

## Chunking and indexing mixed content

- **Keep the image with its context.** A figure's caption, the paragraph that references it, and the figure itself are one retrieval unit. Splitting them is the multimodal version of the chunking failures in [chunking-and-indexing.md](./chunking-and-indexing.md).
- **Tables are neither text nor image.** Linearizing a table to Markdown preserves its values for text retrieval; rasterizing it preserves layout for a vision model. Storing both, keyed to the same unit, avoids choosing wrong.
- **Page-level vs element-level.** Indexing whole pages is simple and tolerant of layout-parsing errors; indexing extracted elements (figures, tables, headings) is more precise but depends on a document parser that will sometimes mis-segment. Match the granularity to how clean your documents are.

## Retrieval and reranking

A multimodal cross-encoder reranker (one that scores a query against an image+text candidate) earns its place here even more than in text RAG, because first-stage multimodal recall is noisier. The [lost-in-the-middle](./lost-in-the-middle.md) effect still applies: a retrieved figure buried in the middle of a long multimodal prompt is under-used, so rerank the strongest visual evidence toward an edge.

## Evaluating multimodal RAG

The failure modes are the text ones plus new ones, and the eval has to separate them:

- **Retrieval**: did the right image/table/passage make the top-k? Standard recall@k, but the gold label is now a mixed-type element.
- **Grounding**: did the answer actually use the retrieved image, or did the model answer from its parametric knowledge and ignore the pixels? This is the multimodal version of faithfulness, and it needs eval items where the correct answer is *only* in the image.
- **OCR / reading**: when the evidence is text-in-an-image, did the model read it correctly? A wrong number copied from a chart is a different failure than a wrong retrieval, and conflating them hides the cause.

Build the eval set with at least some questions whose answer is present only in a figure or table, or the suite cannot distinguish a model that reads images from one that pattern-matches the surrounding text.

## Gotchas

- **CLIP can't read.** Dense in-image text is the most common surprise — a shared-space model retrieves the right-looking chart but the answer is in numbers it never encoded. Use the caption-then-embed path for text-heavy visuals.
- **Captioner errors are silent.** If a chart is captioned wrong offline, retrieval fails in a way that looks like a retrieval bug, not a captioning bug. Spot-check captions and version them.
- **Token cost balloons.** Passing high-resolution images to the generator is expensive; downscale to the model's effective resolution and cap the number of images per prompt (which also helps lost-in-the-middle).

## See also

- 📖 [Retrieval strategies](./retrieval-strategies.md), [hybrid search](./hybrid-search.md), [reranking](./reranking.md), [lost-in-the-middle](./lost-in-the-middle.md).
- 📖 [RAG evaluation framework](../evaluation/rag-evaluation-framework.md) — where grounding and OCR metrics fit.
- A runnable multimodal-RAG lab needs a vision-language embedder and generator; the architecture and eval design here are the prerequisite.
