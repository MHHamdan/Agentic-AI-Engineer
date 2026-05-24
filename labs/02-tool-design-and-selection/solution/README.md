# Lab 02 · Reference solution

The polished final implementation of [Lab 02: Tool design and selection](../README.md).

Ships only `tools_v1` (the working design) — the lab notebook walks through both `tools_v0` and `tools_v1` side by side to demonstrate *why* the v1 shape works. The lab is where the diagnosis lives; this solution is the final state.

## What this is

A six-tool customer-support toolset with:

- **One tool per intent.** `lookup_customer_by_email` and `lookup_customer_by_id` are separate tools, not a single `lookup_customer(mode=...)`.
- **`Literal` enum for status.** `OrderStatus = Literal["pending", "shipped", "delivered", "cancelled"]` — the model literally cannot invent invalid statuses.
- **Confirmation gate on destructive operations.** `update_order` with `new_status="cancelled"` requires `confirmed=true`; without it, returns `{"error": "confirmation_required", ...}` that the agent surfaces to the user.
- **Strict schemas via `StrictModel`.** `ConfigDict(extra="forbid")` — required for OpenAI's strict function-calling mode.
- **Negative-guidance descriptions.** "Do NOT use this for X — use Y" appears in three of the six tool descriptions. This is the single most reliable fix for selection drift between overlapping tools.

## How it differs from `../lab.ipynb`

| Lab notebook (32 cells) | Solution (21 cells) |
|---|---|
| Ships both `tools_v0` and `tools_v1` for side-by-side comparison | Ships only `tools_v1` |
| Step 3 runs `tools_v0` and watches it fail on three patterns | Skipped — the failures are in the concept page |
| Step 4 "Diagnose" walks through what `tools_v0` got wrong | Implicit; the v1 design is the answer |
| Step 8 stretch adds a tiny router for the "tool stew" problem | Out of scope here — the v1 toolset is small enough to skip routing |

## Implementation choices

1. **`StrictModel(BaseModel)` with `ConfigDict(extra="forbid")` as a common base.** Without `extra="forbid"`, OpenAI's strict function-calling mode rejects the schema. Subclassing avoids per-tool boilerplate.
2. **`OrderStatus = Literal[...]` instead of a free-text string with validation.** The constraint is in the schema, not in the handler — the model sees the allowed values in the JSON Schema enum and can't even propose an invalid one. This is the single highest-leverage type choice in the file.
3. **The `confirmation_required` error is a returned dict, not a raised exception.** Same envelope shape as any other tool result — the loop's handling is uniform. The agent reads the structured error on its next step, sees the `message` field, and surfaces it to the user.
4. **The confirmation gate is on the *tool*, not the *agent*.** Moving the safety up into the agent's prompt ("ask the user before cancelling") is fragile — the model may forget under pressure. Moving it down into the tool's return contract is bulletproof — the cancellation literally cannot fire without `confirmed=true`.
5. **The registry stores `(handler, args_model, description)` as a tuple.** Description is part of the registry, not docstrings, because tool descriptions have to be carefully written and reviewed (they're prompt-engineering surfaces). Docstrings drift; explicit description fields don't.

## What's deliberately out of scope

For a real deployment add: idempotency keys on destructive operations (so a retried cancel doesn't double-cancel), audit logging of every destructive call, per-tool authorization checks (does the user own this order?), and rate-limiting. The tool *design* is the foundation — those wrap the handlers.

The lab's Step 8 (router for 20+ tool stews) is also out of scope here. Six tools is well under the ~12-25-tool threshold where selection accuracy degrades; routing pays off at scale, not at this size.

## Running the solution

```bash
cd labs/02-tool-design-and-selection/solution
jupyter notebook lab.ipynb
```

## Next

- Take the [tool-design quiz](../../../quizzes/foundations/tool-design-and-selection.md) if you haven't already.
- Continue to [Lab 03: Multi-step research agent](../../03-multi-step-research-agent/).
