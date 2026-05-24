# Search and Retrieval: A Useful Distinction

Search and retrieval are often used interchangeably in casual conversation. In the context of agentic AI systems, they refer to different things, and the difference matters.

## Search queries an external corpus you do not control

A web search tool — DuckDuckGo, Tavily, Brave, Google — queries an external index of the public web. The corpus is enormous, the indexing is decided by the search provider, the ranking is decided by the provider's algorithms, and the freshness of any given page is up to whoever published it.

The defining property is **lack of corpus control**. You can't guarantee what's indexed. You can't guarantee that a result available today will be available tomorrow. You can't guarantee that the snippets you receive accurately reflect the linked pages. You're working with an external service whose behavior is opaque.

This is fine for many use cases. Research agents, fact-checking workflows, current-events monitoring — all need access to public web content. Search is the natural mechanism.

## Retrieval queries a corpus you do control

A retrieval system — built around embeddings, a vector index, and chunks of documents you've assembled — queries a corpus you assembled. You decided which documents to include. You decided how to chunk them. You decided which embedding model to use. You decided when to re-index.

The defining property is **corpus control**. You know exactly what's in the index. You know when it was last updated. You can guarantee that a chunk available today will be available tomorrow (unless you delete it). You can decide what citation format to use, because you own the chunk IDs.

Retrieval is the mechanism behind RAG — Retrieval-Augmented Generation. RAG systems use retrieval to ground LLM outputs in a known corpus of evidence.

## Why the distinction matters operationally

The failure modes differ. Search fails because the open web is messy: paywalls, rate limits, blocked bots, irrelevant top results, stale pages. Retrieval fails because of decisions you made: bad chunking, low-similarity floors, missing metadata for filtering, stale corpus that needs re-indexing.

The recovery options differ. When search fails, the agent can try a different query, different time window, different search backend. When retrieval fails, the agent can try a different query or surface "I couldn't find this in our docs" — there's no fallback corpus.

The citation semantics differ. Search citations are URLs ("I read this page"). Retrieval citations are chunk identifiers ("I read this specific chunk from document X"). The latter is more precise and more verifiable.

The trust model differs. Search results carry the credibility of their source domain. Retrieval results carry the credibility of whoever assembled the corpus — which is, by definition, you.

## They can be combined

Production systems often use both. The agent has a `search_web` tool for external content and a `search_corpus` tool for internal knowledge. The system prompt steers the agent to prefer the corpus for company-specific questions and the web for current events. Citations from each are tracked separately.

This combination is more powerful than either alone, but it's also more complex. The first version of a system is usually one or the other.

## The phrase to avoid

"RAG is just search with embeddings." This phrase encodes a real misconception. Search and RAG share a shape — query, ranked results, use results to answer — but they're not the same pattern. Conflating them leads to designs that import the failure modes of search into the corpus-control regime where they don't belong, or that import the trust assumptions of a controlled corpus into the open-web regime where they shouldn't.

Building agentic AI well requires keeping the two patterns distinct in your head, even when they look superficially alike.
