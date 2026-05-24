# Tool Design for Language Model Agents

Most agent reliability problems are tool design problems wearing different costumes. When an agent picks the wrong tool, fails to call one at all, or loops on a confusing observation, the underlying cause is almost always in how the tools were specified rather than in the model's reasoning.

## The five parts of a tool

A tool, in the modern function-calling sense, consists of five elements that the model interacts with:

The **name** is what the model emits when it decides to invoke the tool. Names should be verb-noun style and specific enough to disambiguate from siblings. `get_customer` is better than `lookup`; `cancel_subscription` is better than `update`.

The **description** is the natural-language explanation the model reads when deciding whether to call this tool. Good descriptions explain not just what the tool does but when to use it. A description that begins "Use this tool to..." outperforms a bare statement of functionality.

The **schema** defines the arguments. Modern function-calling APIs accept JSON Schema with optional strict-mode validation. Strict schemas with disallowed extra fields and typed enums catch model errors before they become tool-execution errors.

The **return contract** is the shape of what the tool returns to the model. Structured returns with explicit status fields ("status": "ok" vs "status": "error" with a typed kind) let the model reason about failures instead of crashing on them.

The **executor** is the Python (or other language) function that actually does the work. The executor is invisible to the model; it's pure plumbing on your side of the API.

## The pattern that fixes most agent bugs

Structured errors. Instead of raising exceptions, return error dicts with a typed kind field. The model reads the error, decides whether to retry with different arguments, switch tools, or surface the failure to the user. Exceptions crash the loop; structured errors give the model something to reason about.

A canonical shape:

```python
{"status": "ok",    "data": ...}
{"status": "error", "kind": "not_found" | "rate_limit" | "invalid_input", "detail": "..."}
```

The kind field is enumerable. The model learns the vocabulary quickly. Production tools should always return this shape, even for happy paths.

## Tool count and selection

Models pick tools less reliably as the count grows. Past about a dozen tools, selection accuracy degrades noticeably. Past two dozen, it's a coin flip on the harder queries.

The mitigations are pruning, grouping, and routing. Pruning removes tools that aren't relevant to the current sub-task. Grouping bundles related tools into a single discriminated-union tool with an action argument. Routing uses a meta-tool that selects the right specialist tool from a tagged set.

The simplest mitigation, though, is fewer tools. If you can solve a problem with five well-designed tools, don't ship fifteen.

## Destructive actions need explicit gates

If a tool deletes data, sends an email, charges a credit card, or otherwise affects the world in ways the user can't easily reverse, the tool should require an explicit confirmation argument. The confirmation must be set to a non-default value (typically `true`) by the model on a separate call before the destructive action executes.

This pattern catches both accidental tool selection and model misreadings of user intent. A `delete_customer(customer_id, confirmed=False)` call returns a structured "requires confirmation" response. The agent's next step is either to actually confirm or to ask the user. Either way, the destructive action doesn't happen by reflex.
