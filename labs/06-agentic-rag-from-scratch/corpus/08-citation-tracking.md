# Citation Tracking in Agentic Systems

A research-style agent that answers questions from a corpus needs to cite its sources. The naive approach — asking the model to enumerate citations at the end of its answer — fails in subtle ways that erode trust in the entire system. The robust approach treats citation tracking as a structural property of the agent loop rather than a behavior to coax from the language model.

## Why models can't be trusted to enumerate citations

Several failure modes recur in practice.

The model sometimes claims to have read a source it only saw in search results. The query returned ten chunks; the model picked one to fetch in full; in its final answer it cites all ten. The chunks it didn't fetch are still in its context window from the search results, so it confuses "I saw a snippet" with "I read this in full." From the user's perspective, the citation list looks complete; from the underlying mechanics, half the citations are fabrications.

The model sometimes invents citation details. The chunk ID is right; the chunk title is wrong. The document name is right; the section heading is invented. Across hundreds of citations, this error rate compounds into noticeable noise.

The model sometimes attributes a claim to the wrong source. The first three chunks were relevant; the fourth chunk was about a different topic; the model nonetheless wraps the fourth chunk's content into the final answer with a citation pointing at the third chunk. Subtly wrong attributions are harder to catch than outright fabrications.

The model sometimes drops citations for facts it actually used. The agent fetched a chunk, synthesized from it, and then forgot to cite it. The final answer reads as if it's coming from the model's parametric knowledge when in fact it came from a specific retrieved chunk.

None of these failures are model-quality issues that scale up with bigger models. They're structural mismatches between "what the agent read" and "what the agent claims it read." The model has no way to reliably reconcile these two without external tracking.

## The structural solution

Track citations in the agent loop's state, not in the language model's prompt. Every time a tool call retrieves or fetches a chunk, append an entry to a citations list. The list grows as the agent works; it's append-only and tamper-proof from the model's perspective.

When the agent produces its final answer, the citations list is the ground truth for what was actually read. The model writes the answer prose however it likes — citing chunks by ID in inline brackets, summarizing across chunks, whatever the style guide calls for. But the citation list returned to the user is the loop's list, not the model's reconstruction of it.

In code, the pattern is straightforward:

```python
citations = []

for step in range(max_steps):
    response = llm.respond(messages, tools=[...])

    for tool_call in response.tool_calls:
        result = execute(tool_call)
        if tool_call.name == "read_chunk" and result["status"] == "ok":
            citations.append({
                "chunk_id": result["chunk_id"],
                "doc_id":   result["doc_id"],
                "title":    result["title"],
            })
        messages.append(tool_message(tool_call.id, result))

    if not response.tool_calls:
        return {"answer": response.content, "citations": citations}
```

The list contains exactly the chunks the agent actually read. The model cannot add to it, cannot remove from it, cannot reorder it.

## Sourcing versus reading

A subtlety worth being explicit about. Search-style tools return snippets — short previews of chunks the agent might want to read in full. These snippets exist in the agent's context, but seeing a snippet isn't the same as having read the underlying chunk.

The citation tracker should record only chunks that were *read* via the read-chunk tool, not chunks that were merely seen in search results. The distinction matters because the agent's final answer should be grounded in chunks it actually consumed, not in snippets that happened to scroll past.

In practice, this means the search-results tool call doesn't trigger citation tracking. Only the read-chunk tool call does. The agent must explicitly fetch a chunk to have it counted as a source.

## What this enables

Several downstream capabilities depend on this structural pattern.

Faithfulness evaluation becomes tractable. You can check, for any cited chunk, whether the final answer's claims are actually supported by that chunk's content. Without reliable citations, faithfulness evaluation requires inferring which chunks supported which claims — a much harder problem.

Audit trails are clean. A user who wants to verify the agent's answer can read exactly the chunks the agent consumed. There's no question of which chunks contributed to the synthesis.

Caching and replay become safe. If you re-run the same query against the same corpus and embedding model, the retrieval results are deterministic. The agent's tool-call log fully captures what it saw and what it read. Reproducing a past trajectory is straightforward.

Citation hallucination, the canonical RAG failure mode, is eliminated structurally rather than mitigated probabilistically. The mechanism is the same whether the corpus is the open web (URL citations) or a local document collection (chunk-ID citations).
