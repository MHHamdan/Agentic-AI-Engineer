# Project 02 — PDF Q&A bot

> 🟢 Beginner · ⏱ 15-20 hours · 📍 Build Challenge after Path 01 + Path 02 (canonical RAG) · 🛠 Verified 2026-05-29

## What you're building

A chat agent that ingests PDF documents (research papers, manuals, contracts, financial filings), chunks them sensibly, embeds them into a vector store, retrieves relevant passages, and answers questions with inline citations pointing back to the source pages. The agent runs as a CLI or small web UI; the deliverable is the agent plus three example PDF corpora plus a write-up.

This is the canonical RAG starter project. Where [Project 01 (Personal research assistant)](../01-personal-research-assistant/) consumes the open web with a search API, this project consumes a fixed document set with a vector store. The architectural difference between the two is small; the practical difference is enormous — PDFs require pre-processing discipline that web pages don't.

## Why this matters

Three reasons this is the canonical "second project":

1. **It teaches the canonical RAG pipeline end-to-end** — ingestion / chunking / embedding / indexing / retrieval / generation / citation. Every commercial RAG system implements these seven stages; this project exposes the whole pipeline.
2. **PDFs are the production-RAG nightmare case** — multi-column layouts, tables, figures, scanned pages, encoded ligatures, embedded fonts. Production RAG systems spend more engineering time on PDF ingestion than on anything else; building this gives you the failure-mode intuition.
3. **It produces a useful deliverable** — point the agent at your bookshelf, your saved papers, or your company's internal docs. The dogfooding loop tightens fast.

The 2026 production framing: PDF Q&A is the use case where chunking strategy, retrieval quality, and citation accuracy all matter at once. Getting any one wrong produces obvious failures. The project's pedagogical value is that you'll see all three failure surfaces.

## Prerequisites

| Required | Why |
|---|---|
| **Path 01 — Foundations** complete | Agent loop, tool calling, structured outputs |
| **Path 02 — Agentic RAG** (canonical RAG portion) | Chunking strategies, retrieval, RAG failure modes |
| Working Python 3.10+ environment | Repo baseline |
| Anthropic API key (or OpenAI / similar) | The model the agent runs on |
| An embedding model and vector store | Local options: `sentence-transformers` + FAISS or ChromaDB; hosted: OpenAI embeddings + Pinecone/Weaviate/Qdrant |
| Comfort with `pdfplumber` / `PyPDF2` / similar | PDF parsing is half the project |

Helpful but not required: a small batch of real PDFs you care about (your saved papers, a textbook chapter, an annual report).

## What you'll build

Three concrete deliverables:

1. **A working CLI or small web UI** — `python qa.py "your question"` after ingesting a corpus
2. **Three example PDF corpora with example Q&A sessions** — research papers, a manual, and a financial filing or similar. Commit `examples/corpus-01/`, `examples/corpus-02/`, `examples/corpus-03/` with a `questions.md` and `answers.md` per corpus
3. **A `WRITEUP.md`** — your architecture choices and what you learned

Optional fourth deliverable: a web UI where you can drop a PDF and start asking questions (FastAPI + a single HTML page).

## Architecture overview

The agent has seven canonical stages. Each maps to a specific decision you'll defend in the WRITEUP.

| Stage | What happens | Key decision |
|---|---|---|
| **1 — Ingest** | Parse PDFs into text + page metadata | Library choice: `pdfplumber` / `PyMuPDF` / `unstructured` / `marker` |
| **2 — Chunk** | Split text into retrieval units | Size + overlap + boundary strategy |
| **3 — Embed** | Vectorize chunks | Embedding model choice + dimensionality |
| **4 — Index** | Store vectors with metadata for retrieval | Vector store choice: FAISS / Chroma / Pinecone / Weaviate / Qdrant |
| **5 — Retrieve** | Vector similarity (+ optional hybrid keyword) lookup | Top-K, score threshold, hybrid weighting if used |
| **6 — Generate** | LLM answers from retrieved passages with citation requirement | Prompt structure + citation format |
| **7 — Cite** | Inline citations back to source page numbers | Citation verification before returning to user |

The tool surface stays minimal:

| Tool | Used in stage | Implementation |
|---|---|---|
| `ingest_pdf(path)` → list of chunks with page metadata | 1-2 | `pdfplumber` is the recommended default; `PyMuPDF` if you need image extraction |
| `search(query, top_k)` → ranked chunks with relevance scores | 5 | The retrieval call against your vector store |
| `answer(question, context)` → answer with inline citations | 6-7 | The LLM call with prompt that enforces citation format |

The simplest topology: single agent with `search` + `answer` tools available. The agent's reasoning chain handles retrieval + generation in one or two turns per question.

## Milestones

Five phases, each ending with a working checkpoint.

### Milestone 1 — Ingestion that doesn't lose information (3-4 hours)

Get PDF parsing working on three representative documents: one with simple layout (a blog post PDF), one with tables and figures (a research paper), one with multi-column layout (a financial filing). The goal is to confirm your parsing pipeline preserves the information you'd need to cite back to.

**Done when**: for each test PDF, you can extract text + page numbers + (where applicable) table contents; spot-check 5 random pages per PDF and confirm the extracted text matches the visible content.

**Failure modes to watch for**: missed ligatures (`ff`, `fi`), hyphenated line breaks not rejoined, footnote numbers mixing into body text, table contents lost, headers/footers polluting body text. Production PDF Q&A engineering is 80% solving these — accept that this milestone is the hardest one.

### Milestone 2 — Chunking with overlap (2-3 hours)

Implement chunking. Recommended starting point: 500-1000 tokens per chunk with 100-200 token overlap, boundary on sentence breaks where possible. Each chunk carries metadata (source file, page number, chunk index).

**Done when**: for a typical document, chunking produces 10-50 chunks; chunk boundaries don't split sentences mid-word; metadata propagates correctly.

**The decision to document in WRITEUP**: did you use fixed-size, semantic, or hierarchical chunking? The tradeoffs map to Path 02's chunking material.

### Milestone 3 — Embedding and indexing (2-3 hours)

Pick an embedding model + vector store. For local-only setup: `sentence-transformers/all-MiniLM-L6-v2` (or the larger `all-mpnet-base-v2`) + FAISS in-memory. For hosted: OpenAI `text-embedding-3-small` + Pinecone or Chroma Cloud.

Embed all chunks; build the index; test retrieval against 5-10 sample queries to verify it returns plausibly-relevant chunks.

**Done when**: a query like "what's the main finding?" against a research-paper corpus returns chunks from the abstract or conclusion sections, not random body text.

### Milestone 4 — Agent loop with citations (4-5 hours)

Build the question-answering agent. The agent receives a question, calls `search` to retrieve relevant chunks, calls `answer` to generate a response with inline citations. Citations format: `[1]`, `[2]`, etc. in the answer body; numbered references list at the bottom with file + page + (optional) chunk preview.

**Done when**: for each example corpus, you can ask 10 questions and get answers with cite-able sources. Manually verify 30 citations total (3 corpora × 10 questions × 1 spot-check per answer) — at least 90% should point at pages that actually support the claim.

**The citation-integrity check**: like Project 01, this is the load-bearing quality metric. Hallucinated citations are the canonical failure; you defend against them by requiring the agent to quote a short verbatim excerpt alongside each citation.

### Milestone 5 — Polish and write-up (3-5 hours)

Add error handling for the canonical PDF failures: encrypted PDFs, scanned PDFs (no text layer), PDFs in non-English languages, very large PDFs (>500 pages). Add basic logging — print which chunks were retrieved per question, with their relevance scores. Write the WRITEUP and commit the example sessions.

**Done when**: someone unfamiliar with the project can install dependencies, ingest a PDF you didn't provide, ask a question, and get a useful answer with a citation.

## Evaluation criteria

The beginner-tier rubric, adapted for RAG-specific concerns:

| Dimension | What it measures | Beginner-tier target |
|---|---|---|
| **Retrieval precision** | Do the retrieved chunks actually contain the answer? | 80%+ of questions have the right answer present in the top-3 retrieved chunks |
| **Citation accuracy** | Do the citations point at pages that actually support the claim? | 90%+ of citations verified manually as accurate |
| **Answer quality** | Are the generated answers correct given the retrieved context? | Spot-check pass on 90%+ of generated answers |
| **Cost per query** | What does an average question cost? | < $0.05 per query at Sonnet pricing; < $0.01 at Haiku-class |

The retrieval-precision check is the new dimension Project 01 didn't have. It separates "the agent is hallucinating" failures from "the retrieval is missing relevant content" failures. Both are common; the diagnostic difference matters.

### Citation accuracy as the load-bearing check (continued from Project 01)

Same discipline as Project 01: pick 30 citations from your example sessions; click each one; verify the cited page actually supports the claim. Below 90% accuracy is a fix-it-before-submitting blocker. The fix is the same: have the agent quote a short verbatim excerpt with each citation.

## Stretch goals

Pick at most two.

- **Hybrid search** — combine vector similarity with BM25 keyword matching. Demonstrates the hybrid-search pattern from Path 02's RAG material. Helps with technical-term queries where embeddings underperform.
- **Re-ranking** — after retrieval, re-rank the top-K with a cross-encoder model. The accuracy gains are meaningful; the cost is one extra small model call per query.
- **Multi-document reasoning** — handle questions that require integrating information from multiple chunks across multiple PDFs. The next-step beyond single-passage retrieval.
- **Table-aware retrieval** — if your corpus has structured tables, parse them separately and route table-related queries to a structured-query path.
- **Web UI with PDF preview** — upload PDFs, see the highlighted source passage when clicking a citation. Portfolio-screenshot territory.
- **Conversation memory** — multi-turn conversations where follow-up questions can reference earlier exchanges. Adds Path 05 Module 4 (memory tiers) depth.

## Anti-scope

What you don't need to build for this project:

- **Multi-agent orchestration** — single agent is the deliverable; multi-agent comes in Project 03+
- **Fine-tuned embedding models** — off-the-shelf models are sufficient at beginner tier
- **Production deployment** — local + a small hosted demo is fine
- **OCR for scanned PDFs** — if your corpus has scanned-only PDFs, document the limitation; OCR (Tesseract, AWS Textract) is its own engineering surface
- **Streaming responses** — synchronous responses are fine at this tier
- **Authentication and multi-user** — single-user CLI is the assumed shape

## Resources

**Architecture references**:
- [Path 02 — Agentic RAG](../../../learning-paths/02-agentic-rag/) — every stage in this project's pipeline
- [`concepts/rag/`](../../../concepts/rag/) — chunking, retrieval, hybrid search, RAG failure modes

**Tool / library documentation**:
- [pdfplumber](https://github.com/jsvine/pdfplumber) — recommended PDF parsing default; preserves layout info
- [PyMuPDF](https://pymupdf.readthedocs.io/) — alternative with image extraction support
- [unstructured](https://unstructured-io.github.io/unstructured/) — heavier-weight library for messy PDF corpora
- [marker](https://github.com/VikParuchuri/marker) — newer ML-based PDF-to-markdown converter
- [sentence-transformers documentation](https://www.sbert.net/) — local embedding models
- [FAISS documentation](https://faiss.ai/) — local vector store
- [Chroma documentation](https://docs.trychroma.com/) — alternative local vector store with metadata filtering

**Repo cross-references**:
- [Project 01 — Personal research assistant](../01-personal-research-assistant/) — the prior beginner project; same agent-loop foundation with a different data source
- [`patterns/01-single-agent-tool-use.md`](../../../patterns/01-single-agent-tool-use.md) — the architectural pattern this project implements
- [`patterns/08-agentic-rag.md`](../../../patterns/08-agentic-rag.md) — the RAG-specific pattern this project's architecture maps to
- [`concepts/rag/`](../../../concepts/rag/) — the RAG concept pages

## Submission guide

Three artifacts go in your repo when you're done:

1. **The agent code** — clean structure (ingestion/, retrieval/, agent/, examples/); README with setup + usage; `.env.example` for required keys
2. **Three example corpora with sessions** — `examples/corpus-XX/` each containing the PDFs, a `questions.md`, and an `answers.md`. Pick corpora you care about; the dogfooding shows in the example quality.
3. **`WRITEUP.md`** — a ~500-word reflection covering:
   - Which PDF library you picked and why
   - Your chunking strategy decision (size + overlap + boundary policy)
   - The single most surprising thing about how your retrieval performed
   - One thing you'd do differently with the time you spent

Add yourself to `docs/community/showcase.md` when you submit.

## What this project leads to

After PDF Q&A bot, the natural progressions:

- **Project 03 (Project management agent)** — adds Path 03 multi-agent + Path 04 MCP. Different domain (tasks vs documents), same core skills.
- **Project 04 (Data analysis agent)** — same RAG-augmented agent loop with a different tool surface (CSVs + visualizations).
- **Path 02 deeper material** — HyDE, RAG-Fusion, multi-vector retrieval, GraphRAG. The agentic-RAG architectures you'll want for production deployments past the beginner tier.

This is the canonical Build Challenge for engineers who want a production-shaped RAG portfolio piece without committing to capstone-tier scope.
