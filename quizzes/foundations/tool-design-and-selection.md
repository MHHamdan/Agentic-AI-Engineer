---
quiz_id: foundations-tool-design-and-selection
title: "Tool design and selection"
source:
  - concepts/tools/tool-design.md
  - concepts/tools/tool-selection.md
  - labs/02-tool-design-and-selection/
length_minutes: 8
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "Which of these is the **single most important** field for correct tool selection?"
    options:
      A: "The tool's name."
      B: "The tool's description."
      C: "The tool's return type."
      D: "The tool's execution latency."
    answer: B
    explanation: |
      Names matter, but they're short. Return types and latency don't affect
      selection at all. The description is where the model learns when this
      tool applies, when it doesn't, and how it differs from similar tools.
      Good descriptions are the highest-leverage change you can make to
      improve tool selection.
    review:
      page: concepts/tools/tool-design.md
      section: "2. The description"

  - id: q2
    difficulty: easy
    question: "You have a database tool with a `mode` parameter that switches between `lookup`, `search`, `create`, `update`, and `delete`. Should you split it?"
    options:
      A: "No — combining keeps the toolset small."
      B: "Yes — when *required arguments differ* between modes, split into per-intent tools."
      C: "It doesn't matter — the model treats them identically."
      D: "Yes — every tool should have only one argument."
    answer: B
    explanation: |
      The "one tool per intent" rule says: if the *required arguments differ*
      between modes (a `delete` doesn't need the same fields as a `create`),
      split. The schema then *is* the per-intent specification, and the
      model picks by tool name instead of by string match on a mode field.
      Combining is right only when modes share structure (e.g., a unit
      converter handling many units with the same shape).
    review:
      page: concepts/tools/tool-design.md
      section: "Pattern A: One tool per intent"

  - id: q3
    difficulty: medium
    question: "Under OpenAI's `strict` mode for function calling, how do you express an *optional* field?"
    options:
      A: "Omit it from the `required` list."
      B: "Add it to `properties` but allow `null` as a type."
      C: "Set `default: null` in JSON Schema."
      D: "You can't have optional fields in strict mode."
    answer: B
    explanation: |
      Strict mode has a quirk that catches everyone: *all* fields in
      `properties` must appear in `required`. Optional fields are expressed
      by allowing `null` as a type, not by omission. In Pydantic this is
      just `field: int | None = None`. Strict mode also requires
      `additionalProperties: false` on every object — set
      `model_config = ConfigDict(extra="forbid")` in your Pydantic model.
    review:
      page: concepts/tools/tool-design.md
      section: "3. The parameter schema"

  - id: q4
    difficulty: medium
    question: "A tool returns `null` when there are no results. Why is this a bad design choice?"
    options:
      A: "Null values are slower to serialize."
      B: "The model can't distinguish 'not found' from 'tool failed' from 'tool succeeded with empty results'."
      C: "Null is reserved by the OpenAI API."
      D: "It breaks JSON schema validation."
    answer: B
    explanation: |
      Returning `null` for every failure mode collapses three different
      signals into one. The model can't decide whether to retry (transient
      error), broaden its query (not found), or stop (empty result is
      definitive). Return structured shapes like `{"error": "rate_limit"}`,
      `{"customer": null}`, and `{"results": []}` so the model can react
      differently to each.
    review:
      page: concepts/tools/tool-design.md
      section: "4. The return contract"

  - id: q5
    difficulty: medium
    question: "You have 20+ tools in your toolset, and selection accuracy is degrading. What is the **most effective** first intervention?"
    options:
      A: "Switch to a larger model."
      B: "Rewrite all tool descriptions to be longer and more detailed."
      C: "Prune the toolset per call — show only the relevant subset."
      D: "Set `tool_choice='required'` on every step."
    answer: C
    explanation: |
      Empirically, selection accuracy degrades past ~12–25 tools. The
      strongest fix is *pruning*: only show the model the tools relevant to
      the current state. A router step picks the family of tools, then the
      main agent operates on a smaller set. Bigger models help marginally
      but don't eliminate the issue. Longer descriptions can make it worse
      (more tokens to scan). `tool_choice="required"` doesn't change which
      tools are visible.
    review:
      page: concepts/tools/tool-selection.md
      section: "Failure 4: The 'tool stew' — too many tools"

  - id: q6
    difficulty: medium
    question: "Which `tool_choice` value should you use on the *synthesis step* — when the agent should now write a final answer without calling another tool?"
    options:
      A: "`'auto'` — let the model decide."
      B: "`'required'` — force a tool call."
      C: "`'none'` — forbid tool calls."
      D: "A named tool, e.g., `{'type': 'function', 'function': {'name': 'synthesize'}}`."
    answer: C
    explanation: |
      Leaving `tool_choice="auto"` on the synthesis step is a common bug:
      the model may keep calling tools out of inertia. Setting `"none"`
      explicitly forbids tool calls and forces a text response. Modern
      agent frameworks (LangGraph, ADK, OpenAI Agents SDK) handle this
      routing automatically, but you should know the mechanism.
    review:
      page: concepts/tools/tool-selection.md
      section: "Lever 4 — The `tool_choice` parameter"

  - id: q7
    difficulty: hard
    question: "Two tools `search_customers` (fuzzy) and `find_customer_by_email` (exact) both seem to apply to a user's request. The agent keeps picking the wrong one. What's the strongest fix?"
    options:
      A: "Delete one of the tools."
      B: "Add explicit **negative guidance** to both descriptions ('Do NOT use this for X — use Y for that')."
      C: "Increase the model's temperature."
      D: "Rename them to something shorter."
    answer: B
    explanation: |
      Negative guidance — "Do NOT use this for X — use Y" — is the single
      most reliable fix for selection drift between overlapping tools. It
      states the boundary the description otherwise leaves implicit.
      Deleting a tool is too coarse (the capability may be needed).
      Temperature doesn't fix conceptual ambiguity. Names matter but won't
      override genuinely overlapping descriptions.
    review:
      page: concepts/tools/tool-selection.md
      section: "Failure 1: The 'wrong-but-similar' pick"

  - id: q8
    difficulty: hard
    question: "In Lab 02, the same agent code was run against `tools_v0` (broken design) and `tools_v1` (fixed design). The destructive `update_order` cancelled an order immediately in v0, but in v1 it required confirmation. Where did the safety come from in v1?"
    options:
      A: "A new layer of code in the agent loop."
      B: "A switch to a more capable model."
      C: "A schema-level change: a `confirmed: bool` field plus a tool-side check that returns a structured error when it's `false`."
      D: "A system-prompt instruction that warned the model about destructive tools."
    answer: C
    explanation: |
      The safety came from the schema and the tool's return contract — not
      from the agent code, the model, or the prompt. The tool requires
      `confirmed=True` for destructive transitions and returns a
      `{"error": "confirmation_required"}` observation otherwise. The model
      reads that observation and asks the user to confirm. This is the
      headline point of Lab 02: tool design changes agent behavior more
      than prompt engineering does.
    review:
      page: labs/02-tool-design-and-selection/README.md
      section: "Solution discussion"
---

# 🧠 Quiz · Tool design and selection

> ⏱ ~8 min · 🎯 Pass: 6/8 · 📖 Sources:
>
> - [`concepts/tools/tool-design.md`](../../concepts/tools/tool-design.md)
> - [`concepts/tools/tool-selection.md`](../../concepts/tools/tool-selection.md)
> - [`labs/02-tool-design-and-selection/`](../../labs/02-tool-design-and-selection/)

Try each question before expanding its answer. Score yourself at the end.

---

## Question 1 *(easy)*

Which of these is the **single most important** field for correct tool selection?

A. The tool's name.  
B. The tool's description.  
C. The tool's return type.  
D. The tool's execution latency.

<details>
<summary>Show answer</summary>

**Answer: B** — The description.

Names matter, but they're short. Return types and latency don't affect selection at all. The description is where the model learns when this tool applies, when it doesn't, and how it differs from similar tools. Good descriptions are the highest-leverage change you can make to improve tool selection.

→ Review: [`tool-design.md` § "2. The description"](../../concepts/tools/tool-design.md#2-the-description)

</details>

---

## Question 2 *(easy)*

You have a database tool with a `mode` parameter that switches between `lookup`, `search`, `create`, `update`, and `delete`. Should you split it?

A. No — combining keeps the toolset small.  
B. Yes — when *required arguments differ* between modes, split into per-intent tools.  
C. It doesn't matter — the model treats them identically.  
D. Yes — every tool should have only one argument.

<details>
<summary>Show answer</summary>

**Answer: B** — Yes, when required arguments differ between modes.

The "one tool per intent" rule says: if the *required arguments differ* between modes (a `delete` doesn't need the same fields as a `create`), split. The schema then *is* the per-intent specification, and the model picks by tool name instead of by string match on a mode field. Combining is right only when modes share structure (e.g., a unit converter handling many units with the same shape).

→ Review: [`tool-design.md` § "Pattern A: One tool per intent"](../../concepts/tools/tool-design.md#pattern-a-one-tool-per-intent)

</details>

---

## Question 3 *(medium)*

Under OpenAI's `strict` mode for function calling, how do you express an *optional* field?

A. Omit it from the `required` list.  
B. Add it to `properties` but allow `null` as a type.  
C. Set `default: null` in JSON Schema.  
D. You can't have optional fields in strict mode.

<details>
<summary>Show answer</summary>

**Answer: B** — Nullable type, not omission from `required`.

Strict mode has a quirk that catches everyone: *all* fields in `properties` must appear in `required`. Optional fields are expressed by allowing `null` as a type, not by omission. In Pydantic this is just `field: int | None = None`. Strict mode also requires `additionalProperties: false` on every object — set `model_config = ConfigDict(extra="forbid")` in your Pydantic model.

→ Review: [`tool-design.md` § "3. The parameter schema"](../../concepts/tools/tool-design.md#3-the-parameter-schema)

</details>

---

## Question 4 *(medium)*

A tool returns `null` when there are no results. Why is this a bad design choice?

A. Null values are slower to serialize.  
B. The model can't distinguish "not found" from "tool failed" from "tool succeeded with empty results".  
C. Null is reserved by the OpenAI API.  
D. It breaks JSON schema validation.

<details>
<summary>Show answer</summary>

**Answer: B** — Three different signals collapse to one.

Returning `null` for every failure mode collapses three different signals into one. The model can't decide whether to retry (transient error), broaden its query (not found), or stop (empty result is definitive). Return structured shapes like `{"error": "rate_limit"}`, `{"customer": null}`, and `{"results": []}` so the model can react differently to each.

→ Review: [`tool-design.md` § "4. The return contract"](../../concepts/tools/tool-design.md#4-the-return-contract)

</details>

---

## Question 5 *(medium)*

You have 20+ tools in your toolset, and selection accuracy is degrading. What is the **most effective** first intervention?

A. Switch to a larger model.  
B. Rewrite all tool descriptions to be longer and more detailed.  
C. Prune the toolset per call — show only the relevant subset.  
D. Set `tool_choice='required'` on every step.

<details>
<summary>Show answer</summary>

**Answer: C** — Prune the toolset per call.

Empirically, selection accuracy degrades past ~12–25 tools. The strongest fix is *pruning*: only show the model the tools relevant to the current state. A router step picks the family of tools, then the main agent operates on a smaller set. Bigger models help marginally but don't eliminate the issue. Longer descriptions can make it worse (more tokens to scan). `tool_choice="required"` doesn't change which tools are visible.

→ Review: [`tool-selection.md` § "Failure 4: The 'tool stew' — too many tools"](../../concepts/tools/tool-selection.md#failure-4-the-tool-stew--too-many-tools)

</details>

---

## Question 6 *(medium)*

Which `tool_choice` value should you use on the *synthesis step* — when the agent should now write a final answer without calling another tool?

A. `'auto'` — let the model decide.  
B. `'required'` — force a tool call.  
C. `'none'` — forbid tool calls.  
D. A named tool, e.g., `{'type': 'function', 'function': {'name': 'synthesize'}}`.

<details>
<summary>Show answer</summary>

**Answer: C** — `'none'` forbids tool calls.

Leaving `tool_choice="auto"` on the synthesis step is a common bug: the model may keep calling tools out of inertia. Setting `"none"` explicitly forbids tool calls and forces a text response. Modern agent frameworks (LangGraph, ADK, OpenAI Agents SDK) handle this routing automatically, but you should know the mechanism.

→ Review: [`tool-selection.md` § "Lever 4 — The `tool_choice` parameter"](../../concepts/tools/tool-selection.md#lever-4--the-tool_choice-parameter)

</details>

---

## Question 7 *(hard)*

Two tools `search_customers` (fuzzy) and `find_customer_by_email` (exact) both seem to apply to a user's request. The agent keeps picking the wrong one. What's the strongest fix?

A. Delete one of the tools.  
B. Add explicit **negative guidance** to both descriptions ("Do NOT use this for X — use Y for that").  
C. Increase the model's temperature.  
D. Rename them to something shorter.

<details>
<summary>Show answer</summary>

**Answer: B** — Negative guidance is the strongest selection fix.

Negative guidance — "Do NOT use this for X — use Y" — is the single most reliable fix for selection drift between overlapping tools. It states the boundary the description otherwise leaves implicit. Deleting a tool is too coarse (the capability may be needed). Temperature doesn't fix conceptual ambiguity. Names matter but won't override genuinely overlapping descriptions.

→ Review: [`tool-selection.md` § "Failure 1: The 'wrong-but-similar' pick"](../../concepts/tools/tool-selection.md#failure-1-the-wrong-but-similar-pick)

</details>

---

## Question 8 *(hard)*

In Lab 02, the same agent code was run against `tools_v0` (broken design) and `tools_v1` (fixed design). The destructive `update_order` cancelled an order immediately in v0, but in v1 it required confirmation. Where did the safety come from in v1?

A. A new layer of code in the agent loop.  
B. A switch to a more capable model.  
C. A schema-level change: a `confirmed: bool` field plus a tool-side check that returns a structured error when it's `false`.  
D. A system-prompt instruction that warned the model about destructive tools.

<details>
<summary>Show answer</summary>

**Answer: C** — Schema-level change + structured error.

The safety came from the schema and the tool's return contract — not from the agent code, the model, or the prompt. The tool requires `confirmed=True` for destructive transitions and returns a `{"error": "confirmation_required"}` observation otherwise. The model reads that observation and asks the user to confirm. This is the headline point of Lab 02: tool design changes agent behavior more than prompt engineering does.

→ Review: [`labs/02-tool-design-and-selection/README.md` § "Solution discussion"](../../labs/02-tool-design-and-selection/README.md#solution-discussion)

</details>

---

## Scoring

| Score | Meaning |
|---|---|
| 8/8 | You can teach this material. |
| 6–7/8 | Solid grasp. Move on. |
| 4–5/8 | Re-read the relevant concept-page sections, then retake. |
| < 4/8 | Work through both concept pages and re-run Lab 02 with attention to the failure modes, then come back. |

You've now finished the **Foundations** quizzes. When Lab 05 (LangGraph) and Path 02 (Agentic RAG) land, their quizzes will appear in this folder too.
