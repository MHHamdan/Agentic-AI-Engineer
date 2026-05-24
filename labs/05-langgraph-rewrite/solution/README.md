# Lab 05 · Reference solution

The polished final implementation of [Lab 05: LangGraph rewrite](../README.md).

## What this is

The `create_agent` shorthand as the headline, plus the checkpointer + `thread_id` pattern for conversation persistence and an `interrupt()`-based human-in-the-loop demo.

- **`create_agent` for the common case.** Five-line construction; produces the same `StateGraph` topology the lab walks manually.
- **`InMemorySaver` + `thread_id`** demonstrates durable state across `invoke()` calls — turn 2 references "her" and resolves the pronoun against turn 1.
- **`interrupt()`** in a `delete_customer` tool pauses execution mid-trajectory; `Command(resume=...)` continues with the approval decision.

## How it differs from `../lab.ipynb`

| Lab notebook (39 cells) | Solution (23 cells) |
|---|---|
| Step 3 walks the explicit `StateGraph` + `MessagesState` + `ToolNode` + `tools_condition` construction | Skipped — `create_agent` produces the same graph |
| Step 5 builds checkpointer separately from the v2 graph | Folded into the `create_agent` call directly |
| Step 6 introduces `create_agent` only after the explicit build | `create_agent` is the headline |
| Step 8 stretch covers streaming | Out of scope here |

## Implementation choices

1. **`create_agent` over explicit `StateGraph`** for the common case. The explicit build is *necessary knowledge* (it's what `create_agent` wraps), but the shorthand is what you'd actually use in production. The graph topology is still visible via `.get_graph().draw_ascii()`. Verified against [`tools/langgraph/snapshot-v1.0.md`](../../../tools/langgraph/snapshot-v1.0.md) — `create_agent` is from `langchain.agents`, NOT the deprecated `langgraph.prebuilt.create_react_agent`.
2. **`InMemorySaver` for the demo, not SQLite.** Demo simplicity. Production swaps in `SqliteSaver` or `PostgresSaver` — the rest of the code doesn't change.
3. **`interrupt()` payload is a dict, not a string.** Future-proofs against multi-field approval requests (e.g., adding a `severity` field).
4. **Approval is `bool`, not a complex object.** The caller chooses the resume value; the tool sees whatever was passed. A real review UI would pass a structured `{"approved": bool, "reviewer": "...", "note": "..."}` and the tool would unpack it. Demo simplicity.
5. **The checkpointer is *required* for `interrupt()`** — flagged explicitly in the notebook. Without persistence, there's nowhere to pause. The snapshot page lists this as the most common LangGraph gotcha.

## What's deliberately out of scope

For a real deployment:

- **Persistent checkpointing.** `SqliteSaver` (single-process) or `PostgresSaver` (multi-worker) — `InMemorySaver` resets on process exit.
- **Time-travel / replay.** LangGraph supports inspecting prior checkpoints by ID; useful for debugging trajectories but adds API surface this lab doesn't cover.
- **Streaming** (lab Step 8). `.stream()` lets you watch nodes emit state-deltas in real time; useful for chat-UI work, not the solution's focus.
- **Migration from `langgraph.prebuilt.create_react_agent`** — the older helper is deprecated in LangGraph 1.0+. See the snapshot for the migration path.

## Running the solution

```bash
cd labs/05-langgraph-rewrite/solution
jupyter notebook lab.ipynb
```

You need `langgraph >= 1.0` and `langchain >= 1.0` plus the provider-specific package (`langchain-openai` or `langchain-anthropic`).

## Next

- Take the [LangGraph basics quiz](../../../quizzes/foundations/langgraph-basics.md) if you haven't already.
- Continue to [Lab 06: Agentic RAG from scratch](../../06-agentic-rag-from-scratch/) — back to a hand-rolled loop, this time for retrieval.
