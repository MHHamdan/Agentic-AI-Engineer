# Lab 01 · Reference solution

The polished final implementation of [Lab 01: First agent from scratch](../README.md).

## What this is

A clean ~150-line agent loop with:

- Provider-agnostic chat client (OpenAI or Anthropic via `PROVIDER`).
- Two tools (`calculator`, `web_search`) with Pydantic argument schemas.
- Structured tool errors — every exception becomes `{"error": ..., "detail": ...}` that the model can react to on the next step.
- `MAX_STEPS = 8` step cap.
- Consecutive-duplicate-action detection that halts at 2 duplicates in a row.

Use this as a reference once you've finished the lab. The lab notebook is where the *reasoning* lives — why each piece is shaped this way, what failure modes it catches. This solution is the assembly.

## How it differs from `../lab.ipynb`

| Lab notebook (35 cells) | Solution (16 cells) |
|---|---|
| 10 numbered steps building up the loop incrementally | 6 consolidated sections |
| Walks through "build naïve loop → see it loop forever → add dedup" | Ships with dedup as the headline pattern |
| Step 6 deliberately provokes a controlled tool error to demonstrate recovery | The structured-error envelope is just the contract |
| Step 9 stretch covers swapping providers manually | The provider switch is a single `PROVIDER` variable |

## Implementation choices

A few decisions worth flagging since they're easy to get wrong:

1. **`AssistantMessage` is a small dataclass, not a TypedDict or Pydantic model.** Mutable, easy to compose, no schema validation overhead at the boundary. The provider-agnostic translation happens in `chat_with_tools` — once.
2. **The Anthropic branch composes `text` from text blocks via `"".join(b.text for b in resp.content if hasattr(b, "text"))`** because Anthropic's response is a list of content blocks (text + tool_use), not a single string. Anthropic's API isn't a drop-in for OpenAI's; the translation has shape that matters.
3. **The repeated-action signature uses `json.dumps(arguments, sort_keys=True)`** so that `{"a": 1, "b": 2}` and `{"b": 2, "a": 1}` hash to the same signature. The model genuinely produces both orderings; without sorting, the dedup misses obvious cases.
4. **The duplicate counter trips at `>= 2`, not `>= 1`.** One repeat is a valid retry; two in a row is a loop. The threshold is calibrated to the failure mode (model is stuck), not to "saw the same call once."
5. **The calculator returns a structured error rather than raising on disallowed characters.** Same envelope as a successful result, so the loop's tool-result handling stays uniform.

## What's deliberately out of scope

For a real deployment you'd also want: per-tool timeouts, total-time and total-token budgets, async tool execution for parallel calls, structured logging, per-tool circuit breakers, retry-with-backoff on provider 5xxs, and observability hooks. The agent loop itself doesn't change — those wrap around it. See [`concepts/agents/agents-vs-frameworks.md`](../../../concepts/agents/agents-vs-frameworks.md) for when reaching for a framework (Lab 05's LangGraph version) pays off.

## Running the solution

From the repo root, with your `.env` set:

```bash
cd labs/01-first-agent-from-scratch/solution
jupyter notebook lab.ipynb
```

Or run as a script with `papermill` / `jupyter nbconvert --execute` if you want a non-interactive run. The notebook's `.env` autoload walks up parent directories until it finds the repo's `.env.example`, so the working-directory move doesn't break.

## Next

- Take the [agent-loop quiz](../../../quizzes/foundations/agent-loop.md) if you haven't already.
- Continue to [Lab 02: Tool design and selection](../../02-tool-design-and-selection/).
