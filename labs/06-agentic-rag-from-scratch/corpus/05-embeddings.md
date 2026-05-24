# Embeddings: What They Are and How They Behave

An embedding is a dense numeric vector representing a piece of text. The vector has a fixed dimensionality — typically 384, 768, 1024, or 1536 — chosen by the model architecture. Two texts with similar meaning produce vectors with high cosine similarity; two texts with unrelated meaning produce vectors with low cosine similarity.

## What "similar meaning" actually means

This is the part most overviews skim past, but it matters for understanding when embeddings work and when they don't.

An embedding model is trained on pairs of texts that are labeled as similar or dissimilar. The training objective pushes similar pairs together in the vector space and pushes dissimilar pairs apart. The "meaning" the model captures is therefore the meaning of similarity *in the training data*.

For general-purpose models trained on web-scale data — like the popular `all-MiniLM-L6-v2` — the captured notion of similarity is broadly "these texts are about the same thing." This works well for question-answering over informational documents.

It works less well for queries where similarity in the everyday sense and similarity in the training-data sense diverge. Two pieces of code with identical functionality but different variable names may not embed similarly. Two legal clauses with identical effect but different terminology may not embed similarly. A specific numeric value embedded with surrounding context may not match a query about that value.

Embedding models are not magical understanding engines. They're statistical models of the training distribution. Knowing this helps you anticipate when they'll work and when they won't.

## Dimensionality

A 384-dimensional embedding takes 384 floats × 4 bytes per float = 1.5 KB. A 1536-dimensional embedding takes 6 KB. For a corpus of 10,000 chunks, that's the difference between 15 MB and 60 MB of vector storage.

Larger dimensionality generally means richer representation. The relationship is sublinear — doubling the dimensionality doesn't double the quality — but it's positive.

Some models support Matryoshka-style dimension reduction: you can request a lower-dimensional version of the same embedding with graceful quality degradation. OpenAI's text-embedding-3 family supports this via a `dimensions` parameter. It's useful for storage cost optimization in large indexes.

## Normalization

If you normalize an embedding to unit length (divide by its L2 norm), the dot product of two normalized embeddings equals their cosine similarity. This is mechanically convenient: cosine similarity becomes a single matrix multiplication.

Most embedding models support a `normalize_embeddings` flag in their encode method. Setting it to True at encode time is the cleanest pattern, because every downstream similarity calculation simplifies.

If you forget to normalize, your similarity calculations need to include explicit denominators, which is easy to get wrong. Many vector stores assume normalized embeddings by default; passing un-normalized vectors silently produces wrong-looking results.

## The token-limit foot-gun

Every embedding model has a maximum input length. Inputs longer than the limit are silently truncated. The model doesn't error, doesn't warn, and the resulting embedding represents only the truncated prefix.

For `all-MiniLM-L6-v2`, the limit is 256 wordpieces, roughly 200 LLM-tokens. For OpenAI's `text-embedding-3-small`, the limit is 8,191 tokens. For most sentence-transformer models, the limit is in the 256-512 wordpiece range.

If your document chunks exceed your model's token limit, your embeddings are not representing the chunks you think they are. This is the most common source of "my RAG system isn't retrieving the right things" in production. The fix is always: chunk smaller, or use a model with a larger context.

Knowing your model's limit is non-optional.

## When embeddings disagree with humans

Embeddings sometimes rank chunks in orders that surprise humans. Two chunks that a reader would consider equally relevant may have markedly different cosine similarity to a query. Two chunks that a reader would consider unrelated may cluster closely.

The usual cause is the training-data effect: the embedding model has learned a notion of similarity that doesn't match human intuition on certain content types. The mitigation is usually re-ranking — running a separate, more expensive model (typically a cross-encoder) on the top-30-50 candidates and re-scoring them. This improves alignment with human judgments at the cost of one more inference call per query.

Re-ranking is covered in a later batch of curriculum material. For first-pass RAG systems, raw embedding similarity is usually adequate.
