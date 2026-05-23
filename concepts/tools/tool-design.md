# Tool design

> 🟢 Stable · ⏱ ~12 min read · 🏷 tools, foundations, design

## TL;DR

A tool is not just a function — it's a function plus a **schema**, a **name**, a **description**, and a **return contract** that all show up directly in the model's prompt. Bad tool design produces hallucinated calls, lost arguments, and silent failures. Good tool design follows the same principles as good API design, with two extra constraints: the *names and descriptions are read by a language model*, and *every byte you return costs context*.

If you can write a clear OpenAPI spec for a tool, you can probably write a clear LLM tool. The mistakes are the same. The cost of getting it wrong is just more visible.

---

## What "a tool" actually consists of

When the LLM provider receives your tool definition, it sees four things:

1. **The name.** A short identifier. Becomes a token sequence the model uses to refer to the tool.
2. **The description.** A natural-language explanation of what the tool does, when to use it, and any constraints. The single most important field for correct tool selection.
3. **The parameter schema.** JSON Schema describing the arguments — types, required fields, allowed values, descriptions per field.
4. **The return contract.** *Not* part of the schema you send — but the shape of what you return becomes the observation the model reasons about next. Treat it like API output, not a data dump.

Plus one thing the model *doesn't* see directly:

5. **The executor** — your Python function. The model never reads its body, only its name, description, and schema. So the executor's behavior must match what the description promises, exactly.

---

## The five components, in detail

### 1. The name

Short, in lowercase, snake_case, and *unambiguous in the toolset*. The model uses the name during retrieval-from-prompt — "which tool fits this need?" — and ambiguous names cause selection errors.

| Bad | Better | Why |
|---|---|---|
| `process` | `extract_pdf_text` | "process" matches everything |
| `db` | `lookup_customer_by_email` | states action and target |
| `helper` | `unit_convert` | functional, not vague |
| `searchUserDb_v2_final` | `find_user` | versions and adjectives are clutter |

Don't include version numbers in tool names. If the schema changes, change the schema; if you need two coexisting versions, give them distinct meanings (`find_user` vs `search_users`, not `find_user_v1` vs `find_user_v2`).

### 2. The description

This is the only place in your toolset where you're allowed to be verbose, and it's where most bugs hide. The description has to do three jobs:

1. **State what the tool does** in plain language.
2. **State when to use it** — and, if there's a similar tool, when *not* to use this one.
3. **State the contract** — units, formats, error conditions the model should know to handle.

A pattern that works:

```
{action verb} — {one-line purpose}.
Use this when {trigger condition}. Do not use this for {anti-trigger}.
Returns {shape}. Errors on {failure modes}.
```

A concrete example:

```
Look up a customer record by email address. Use this when you have an email
and need profile info (name, plan, status). Do not use this for partial-match
or fuzzy search — use `search_customers` for that. Returns a customer object
with id, name, plan, status, created_at. Returns null if the email is not in
the system; raises an error only on malformed input.
```

Note the *negative* instruction. Tool descriptions that only describe what the tool does — without distinguishing it from neighbors — produce confused selection. We come back to that in [`tool-selection.md`](./tool-selection.md).

OpenAI and Anthropic both expose a description field per tool; OpenAI's is currently capped at around 1024 characters in some API surfaces, so be concise. Concrete examples in the description ("Example query: `find_user(email='ada@example.com')`") improve selection more than abstract elaboration.

### 3. The parameter schema

Use a schema generator (Pydantic, dataclasses-json, or jsonschema directly). Hand-written JSON Schema for tools is a category of bug we don't need.

Three rules that pay off in practice:

**Rule 1: Use the most specific type that fits.**
A status field that can be one of `"active" | "suspended" | "cancelled"` should be a literal, not a free `string`:

```python
status: Literal["active", "suspended", "cancelled"]
```

The schema becomes `{"enum": [...]}` and the model has explicit values to choose from. Open strings invite typos and hallucinated values.

**Rule 2: Mark optional fields with `None`, not by omitting `required`.**
If you use OpenAI's strict mode (and you should), *all* fields in `properties` must appear in `required`. Optional fields are expressed by allowing `null` as a type, not by omitting them:

```python
class SearchArgs(BaseModel):
    query: str
    limit: int | None = None     # optional → represented as nullable
```

This is one of two non-obvious requirements of strict mode. The other: `additionalProperties` must be `false` on every object. Pydantic v2's `model_json_schema` doesn't add `additionalProperties: false` by default — set `model_config = ConfigDict(extra="forbid")` to get it.

**Rule 3: Give each field its own `description`.**
Field descriptions are read by the model when filling arguments, separately from the tool-level description. Each one is a sentence answering "what should I put here?":

```python
query: str = Field(
    description=(
        "The exact text to search for. Use lowercase. "
        "Tokenized on whitespace; phrases need to be quoted."
    )
)
```

That cost (one extra sentence) buys you fewer malformed arguments.

### 4. The return contract

The return value becomes an **observation** the model reads on the next step. Three principles:

**Structure beats prose.** Return JSON-shaped data, not human-readable text:

```python
# Bad
return f"Customer {name} is active on the Pro plan."

# Better
return {"id": cust.id, "name": cust.name, "plan": cust.plan, "status": cust.status}
```

The model summarizes structured data well; it parses prose into structured data badly.

**Distinguish "not found" from "error" from "empty".** A null result, an exception, and an empty list are three different signals:

```python
# Tool returns:
{"result": null}           # explicit not-found (e.g., no customer with that email)
{"error": "RATE_LIMIT"}    # tool failed (transient, retryable)
{"results": []}            # tool succeeded with no results (the search ran fine, nothing matched)
```

A model that sees `null` for all three has no signal for what to do next. A model that sees the three different shapes can react correctly.

**Compress aggressively.** A 50 KB JSON response is 50 KB of context that gets re-sent on every subsequent step. If your raw output is large, either summarize before returning, or return a handle the model can dereference selectively:

```python
# Instead of returning all 200 results
return {
    "summary": "Found 200 customers matching 'gmail'. Top 5 by recency:",
    "top_5": top_five_summaries,
    "total_count": 200,
    "page_token": "abc123",   # call again with this to see more
}
```

The "return a handle" pattern is standard in API design and works just as well for tools.

### 5. The executor

The function the model never sees. Three things that bite:

**Validate before executing.** Pydantic's `.model_validate(args)` is usually enough, but for tools that touch real systems, add a second layer that checks business invariants (e.g., "this user is allowed to do this"). Don't trust the LLM's output any more than you'd trust an unauthenticated HTTP request.

**Make errors structured, not exceptions.** If your tool can fail in expected ways (not found, rate limited, validation error), return those failures as data, not as raised exceptions. The agent runtime will catch raw exceptions and convert them — but the conversion loses the model's ability to distinguish failure types:

```python
def lookup_customer(args):
    try:
        return {"customer": fetch(args.email)}
    except CustomerNotFound:
        return {"error": "not_found", "email": args.email}
    except RateLimitError:
        return {"error": "rate_limit", "retry_after_seconds": 30}
    # Truly unexpected errors still raise — the runtime converts them.
```

**Side effects need confirmation.** Any tool whose effect can't be undone (sending email, charging a card, deleting data) should either route through a human approval step or require an explicit `confirmed=True` argument that the model has to set after acknowledging the consequences. We cover this in the [Human-in-the-loop pattern](../../patterns/10-human-in-the-loop.md).

---

## Schema design patterns

Three patterns worth knowing.

### Pattern A: One tool per intent

The first tool design instinct is usually "I'll make one big tool with a `mode` parameter":

```python
class DatabaseArgs(BaseModel):
    mode: Literal["lookup", "search", "create", "update", "delete"]
    entity: str
    query: dict
```

This is almost always wrong. The model has to reason about the `mode` field separately from the schema, and the schema can't enforce per-mode argument validity (a `delete` doesn't need the same fields as a `create`). Split it:

```python
def lookup_customer(args: LookupArgs): ...
def search_customers(args: SearchArgs): ...
def create_customer(args: CreateArgs): ...
```

Now each tool's schema *is* its specification, and the model picks the right tool by name rather than the right mode by string match.

The exception: when the modes truly share structure (a unit converter handling 30 unit types should not be 30 tools), keep them in one tool. The rule of thumb: if the *required arguments* differ between modes, split; if they're the same, combine.

### Pattern B: Discriminated unions

When a tool legitimately has multiple input shapes, use a discriminated union — a `kind` field with a literal type that selects the rest of the schema:

```python
class EmailLookup(BaseModel):
    kind: Literal["email"] = "email"
    email: str

class IdLookup(BaseModel):
    kind: Literal["id"] = "id"
    customer_id: int

class LookupArgs(BaseModel):
    query: EmailLookup | IdLookup = Field(discriminator="kind")
```

The schema makes the disjoint shapes explicit. The model picks the variant that matches the available data.

### Pattern C: Pagination over expansion

When a tool can return arbitrarily many results, default to returning *few* (top 5 or 10) plus a continuation token:

```python
class SearchResult(BaseModel):
    results: list[Item]                  # the first page only
    total_count: int                     # so the model knows there's more
    next_page_token: str | None = None   # null when there's nothing more
```

If the model wants more, it calls the tool again with the token. This keeps the per-step observation small and lets the model decide whether to keep digging.

---

## Common tool-design mistakes

A short list of failure modes you'll see in production, with the cause and fix:

| Symptom | Likely cause | Fix |
|---|---|---|
| The model invents tool names | Tool description is vague; model guesses what *should* exist | Tighter descriptions, fewer overlapping tools |
| Arguments are off by one (string for int, etc.) | No schema validation; or schema is permissive | Pydantic strict mode; `additionalProperties: false` |
| Model calls the same tool 5 times with slight tweaks | Tool returns no actionable signal on each call | Return distinct error/data shapes; consider summarization |
| Model never calls a tool that exists | Description doesn't trigger on real-user phrasings | Add examples and trigger phrases to the description |
| Tool returns 50KB and context blows up by step 4 | No compression in return contract | Truncate, summarize, or return handles |
| Side effects fire on broken inputs | Executor trusts validated-but-still-wrong data | Add business-rule validation after schema validation |
| Two tools both match the request, model picks wrong | Overlapping descriptions, no negative guidance | Add "Do not use this for X — use Y" to both |

We exercise each of these in [Lab 02](../../labs/02-tool-design-and-selection/) by building a deliberately-bad toolset, watching it fail, and fixing it step by step.

---

## 🧮 Math behind it

Tool design choices change the **action space** $\mathcal{A}$ available to the policy $\pi_\theta(a_t \mid s_t)$. Each tool is an element of $\mathcal{A}_{\text{tool}}$, and the schema constrains which arguments are valid for that tool. Three observations:

- **Splitting a multi-mode tool into per-intent tools** expands $\mathcal{A}_{\text{tool}}$ in cardinality but *shrinks* the valid-argument space per element. Empirically, models pick correctly more often from a clean-shaped action space than from a single tool with a sprawling argument space.
- **Description text doesn't change $\mathcal{A}$**, but it changes $\pi_\theta$'s output distribution over $\mathcal{A}$ — the description is part of $s_t$. Better descriptions concentrate probability on the right tool for the state.
- **Return contracts shape $o_t$**, which shapes $s_{t+1}$, which shapes the next $\pi_\theta(\cdot \mid s_{t+1})$ call. A noisy return is a noisy state, which is a noisier action distribution.

→ Full treatment of the action space: [`math-foundations/04-agents-as-policies.md`](../../math-foundations/04-agents-as-policies.md).

---

## See also

- 📖 [Tool selection](./tool-selection.md) — given a designed toolset, how does the model pick? Why does it fail?
- 📖 [What is an agent?](../agents/what-is-an-agent.md) — the broader context.
- 📖 [Agent loop](../agents/agent-loop.md) — where tools sit in the loop.
- 🧪 [Lab 02: Tool design and selection](../../labs/02-tool-design-and-selection/) — hands-on with the patterns above.
- 🏛 [Single-agent tool-use pattern](../../patterns/01-single-agent-tool-use.md) — architectural perspective.
- 🧮 [Agents as policies](../../math-foundations/04-agents-as-policies.md) — the math of action spaces.

---

## References

- OpenAI. [*Function calling*](https://platform.openai.com/docs/guides/function-calling) — the canonical guide. Covers strict mode, `tool_choice`, and parallel calls.
- Anthropic. [*Tool use overview*](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview). Equivalent for Claude. Worth reading both to see where the abstractions converge.
- Schick, T. et al. (2023). [*Toolformer: Language Models Can Teach Themselves to Use Tools*](https://arxiv.org/abs/2302.04761). NeurIPS 2023. Background on tool use as a primitive.
- Patil, S. G. et al. (2024). [*Gorilla: Large Language Model Connected with Massive APIs*](https://arxiv.org/abs/2305.15334). NeurIPS 2024. Useful on how API selection scales with tool count.
- UC Berkeley CS294/194-196 *Agentic AI*, Fall 2025. [Course page](https://rdi.berkeley.edu/agentic-ai/f25). Lectures on planning + tool use; useful for the broader academic framing.
