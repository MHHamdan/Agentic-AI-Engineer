# Chunking Strategies for RAG

Chunking is the decision that has the largest effect on retrieval quality in a RAG system. It's also the decision most teams underinvest in, because the consequences only surface once the system is deployed and the model is silently failing to find answers that exist in the corpus.

## What chunks are for

A chunk is a sub-section of a document that gets embedded and indexed independently. Each chunk gets one vector. Queries return chunks, not documents.

Two constraints force chunking even before any retrieval-quality argument:

First, embedding models have maximum input lengths. A 30-page document cannot be embedded as one piece because no embedding model accepts that many tokens. The document must be split.

Second, document-level embeddings smear specific facts together. An embedding of an entire 30-page document is a blurry average of everything in it. Asking "what does page 17 say about X?" against a document-level index produces useless rankings, because the embedding has lost track of which content lives where.

Chunks are the retrieval unit. Choosing them well is choosing the granularity at which your system can be helpful.

## The size tradeoff

Each chunk should be small enough that its embedding focuses on one coherent topic. Each chunk should be large enough that its content is self-contained when read by the LLM. These pull in opposite directions.

Most production systems settle in the 200-800 token range. Common defaults are 512 tokens for general-purpose RAG over knowledge bases and articles, and 256 tokens for short-answer retrieval over FAQs and reference content.

The right size depends on the corpus. Dense technical content (statutes, API references) can use smaller chunks because each sentence carries meaning. Discursive content (essays, blog posts) benefits from larger chunks that preserve argumentative flow.

If you're using a small embedding model with a tight token limit — like all-MiniLM-L6-v2, which truncates at 256 wordpieces — your chunks must stay under the limit. The model silently truncates excess content, leaving you with embeddings that don't represent what you think they represent. This is the most common chunking failure mode in tutorial-grade RAG systems.

## Overlap

Chunk boundaries are where information is lost. A fact stated in one sentence at the end of chunk A and clarified in the next sentence at the start of chunk B is invisible to retrieval — neither chunk contains the full statement.

Overlap fixes this. Adjacent chunks share their boundary region, typically 10-20% of the chunk size. A 512-token chunk with 20% overlap means each chunk shares 102 tokens with the previous chunk and 102 with the next.

The cost is 20% more storage and embedding compute. The benefit is that boundary-spanning information is recoverable: each fact appears in full in at least one chunk.

Overlap is almost always worth it. Production systems that don't use overlap usually wish they had.

## Boundary selection

Three strategies for picking where chunks break, in increasing order of sophistication:

**Fixed-window splitting** splits every N tokens regardless of content. Trivial to implement. Boundaries often fall mid-sentence, mid-paragraph, mid-list. Acceptable for prototypes.

**Recursive splitting on document structure** tries to split at paragraph breaks first, then sentence breaks, falling back to fixed-window only as a last resort. The popular `RecursiveCharacterTextSplitter` from LangChain implements this; it's also straightforward to write from scratch. Chunks become non-uniform in size — some 300 tokens, some 700 — but boundaries respect natural structure. This is what most production systems use.

**Semantic splitting** uses a separate model pass to detect topic boundaries and splits where similarity between adjacent sentences drops. Most expensive at index time. Sometimes meaningfully better than recursive splitting, sometimes not. Most useful for stable corpora where re-indexing is rare.

For a first-pass RAG system, recursive splitting is almost always the right choice. Optimize later if needed.

## Metadata

Every chunk should carry metadata. At minimum, the document ID it came from, a stable chunk ID, the document's title, and a pointer to the source (file path, URL).

Optional but powerful additions: the section heading the chunk falls under, the chunk's position in the document, creation and update timestamps, category tags. Metadata enables filtered retrieval — similarity search within a subset of the corpus, which dramatically improves precision for many real-world use cases.

Metadata is essentially free to store and indispensable to maintain over time. Plan the schema before indexing. Adding new metadata fields after the corpus is indexed usually requires re-indexing.

## The diagnostic patterns

When debugging a RAG system that isn't finding the right content, the most common chunking-side causes:

Retrieval returns chunks that are close to the question but never quite contain the answer. The answer spans a chunk boundary. Increase overlap or use semantic splitting.

Retrieval scores are uniformly low across queries. Chunks are too large, smearing multiple topics. Reduce chunk size.

The same chunk keeps coming back regardless of query. The corpus contains duplicates or near-duplicates. Dedupe before indexing.

Recently-updated information isn't retrieved. The index is stale. Re-index periodically; add update timestamps to metadata.

Question is about a specific code or proper noun and retrieval misses it. Dense embeddings sometimes miss exact tokens. Hybrid search — combining BM25 keyword search with dense retrieval — helps significantly with this class of failure.

Most of these are diagnosable from inspection of the retrieved chunks. Audit your retrievals when something is going wrong.
