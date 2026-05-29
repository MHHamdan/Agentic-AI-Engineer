# Compression and summarization

> 🟡 Intermediate · ⏱ ~26 min · 🛠 Verified 2026-05-29 · 📍 Module 3 of [Path 05 — Context Engineering](../../learning-paths/05-context-engineering/); read after [`foundations.md`](./foundations.md) and [`token-budgets.md`](./token-budgets.md)

## What this page is for

[`token-budgets.md`](./token-budgets.md) introduced the soft cap / hard cap two-threshold pattern. The soft-cap *trigger* fires when a zone reaches 80% of its budget; what fires *after* the trigger is compression. This page covers the compression mechanics: what compression methods are available, when each helps vs hurts, and how to avoid the canonical failure mode where compressed context degrades faster than uncompressed context would have.

The 2026 production framing per [Zylos Research February 2026](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies): "Context drift kills agents before context limits do. Nearly 65% of enterprise AI failures in 2025 were attributed to context drift or memory loss during multi-step reasoning — not raw context exhaustion."

That stat reframes the engineering problem. Compression isn't primarily about staying under the model's context limit (the hard cap); it's about preserving the quality of agent reasoning before the limit is approached. The 2026 compression literature converged on three approaches that produce different quality/cost profiles, plus a provider-native option that Anthropic shipped in January 2026.

This page covers:

1. **The four compression strategies** — truncation, summarization, masking, context folding — and when each applies
2. **Lossy vs lossless** — what's recoverable and what isn't
3. **Anchored iterative summarization** — the production-mature pattern that outperforms full-reconstruction
4. **Provider-native compaction** — Anthropic's `compact-2026-01-12` beta API
5. **Agent-centric compression** — ACON, Focus, recursive language models, context folding
6. **The recursive summarization trap** — why naive recursive compression degrades agent reasoning
7. Operational discipline, anti-patterns, anti-scope

## The four compression strategies

When a zone hits its soft cap, four approaches reduce token count. Each has a different cost / quality profile.

| Strategy | Token reduction | Quality impact | Recoverable? | Typical use |
|---|---|---|---|---|
| **Truncation** | High (linear) | High (drops content) | No | History zone when oldest turns are stale; tool outputs when only the tail matters |
| **Summarization** | Moderate to high | Moderate (depends on prompt) | Partially (via the summary) | History zone with anchored iterative pattern; long retrieved documents |
| **Masking** | Zero token reduction but improves attention | Low (preserves all content) | Yes (just unmask) | When KV cache reuse matters more than token count; per Manus 2025 pattern |
| **Context folding** | High (recursive reduction) | Variable (depends on branch design) | Via stored summaries | Long-horizon agents with explicit branching |

The choice depends on what the zone is for. Conversation history of a customer-support agent that already resolved the user's first three issues benefits from truncation — the early turns aren't needed anymore. Conversation history of a research agent tracing a multi-step investigation needs summarization or context folding — the early decisions matter for the final report.

### Truncation

The simplest reduction: keep the most recent N tokens; drop the rest. Per [TianPan April 2026](https://tianpan.co/blog/2026-04-13-token-budget-as-architecture-constraint), truncation is what happens implicitly when an agent silently exceeds its context window — the model truncates at the front and the request usually still works. The discipline is to make truncation *explicit* and *bounded*:

```python
def truncate_history(history: list[Turn], max_tokens: int) -> list[Turn]:
    # Keep most recent turns until budget runs out
    selected = []
    total = 0
    for turn in reversed(history):
        turn_tokens = count_tokens(turn)
        if total + turn_tokens > max_tokens:
            break
        selected.insert(0, turn)
        total += turn_tokens
    return selected
```

Two considerations: (1) preserve the system prompt — never truncate Zone 1 per [`foundations.md`](./foundations.md); (2) the first user turn often contains the original task framing — truncating it loses the task definition. Many production systems keep the first turn plus the most-recent-N pattern (the "FIFO with pinned-head" variant).

### Summarization

Replace older content with a generated summary. Per [Zylos Research February 2026](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies), "anchored iterative summarization consistently outperforms full-reconstruction" — Factory's evaluation across 36,000 real engineering session messages showed that merging new summaries into a persistent state (rather than regenerating the summary from scratch each time) produces higher accuracy, completeness, and continuity scores.

The anchored pattern:

```python
class AnchoredSummarizer:
    def __init__(self):
        self.persistent_summary = ""  # The anchor — survives compactions

    def compact(self, recent_turns_to_compact: list[Turn]) -> str:
        # Merge new turns into the persistent summary, NOT regenerate from scratch
        return self.llm.generate(
            f"Existing summary:\n{self.persistent_summary}\n\n"
            f"New events to merge:\n{format_turns(recent_turns_to_compact)}\n\n"
            f"Output: updated summary preserving all decisions, blockers, and open questions."
        )
```

The persistent summary is what survives every compaction; the older raw turns get replaced by their contribution to the summary. Full-reconstruction (regenerate the summary from scratch every time) loses information at each cycle because the LLM has no anchor to preserve from.

### Masking

Per [Manus 2025 via Lee Kangwook March 2026](https://kangwooklee.com/talks/2026_03_BLISS/bliss_seminar_monograph.html): "Provide all information in the system prompt from the start. 'Mask' out irrelevant parts via logit masking instead of adding or removing. The prefix never changes, so the KV cache is always reused."

The KV cache angle matters because prompt caching ([`../../production/cost-engineering.md`](../../production/cost-engineering.md) Layer 3a) gives 10x cost reduction on cached prefixes. Any compression that changes the prefix invalidates the cache. Masking changes which tokens the model *attends* to without changing the prefix — cache stays valid.

Tradeoff: masking doesn't reduce input tokens; the model still pays the full token cost. It buys attention-quality improvement, not cost reduction. Best suited where attention dilution is the bottleneck (Zone 2 dynamic context with many low-relevance entries) and cache reuse matters.

### Context folding

Per [Prime Intellect 2026 on Recursive Language Models](https://www.primeintellect.ai/blog/rlm): "the agent can actively branch its rollout, and return from the branch; within the branch, it retains the full previous context, but after returning, only a self-chosen summary of the branch remains." Per [RE-TRAC (arxiv:2602.02486)](https://arxiv.org/pdf/2602.02486): REcursive TRAjectory Compression specifically for deep search agents handling 128K-256K token contexts.

Context folding is the most aggressive reduction strategy — sub-trajectories get compressed to summaries; the agent's main context only sees the summary, not the full sub-work. Best suited for long-horizon agents (research, multi-step debugging) where the main agent doesn't need the intermediate steps to make the final decision.

## Lossy vs lossless

Lossless compression: the original content is fully recoverable from the compressed form. In practice, only masking (no actual token reduction) and structured truncation with metadata pointers (drop the raw content but keep a database key) qualify.

Lossy compression: the original content is not fully recoverable. Summarization, content-aware truncation, and context folding are all lossy — by design. The discipline is to be deliberate about what gets lost.

Three categories of content that compression should preserve regardless of strategy:

1. **Identifiers and references** — case IDs, transaction IDs, file paths, function names. The agent needs these to take further action; compression that drops them produces follow-up failures.
2. **Open questions and blockers** — anything the agent hasn't resolved yet. The summary needs to track what remains TODO.
3. **User-stated constraints** — refund caps, allowed actions, deadlines. These shape every subsequent decision; losing them produces inconsistent behavior.

What's safe to lose: routine conversational pleasantries, the exact wording of resolved exchanges, intermediate tool-call arguments where only the result mattered, repeated information the user already received.

## Anchored iterative summarization — the production pattern

The Factory 36,000-session evaluation per [Zylos](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies) named the winner: anchored iterative summarization. Three properties that make it work:

1. **The summary persists across compactions.** The persistent summary state survives every compression cycle; only the un-summarized recent turns get added at each cycle. Information from cycle 1 carries through to cycle 10 via the summary's persistence.
2. **The compression prompt is structured.** Generic "summarize the above" produces drifting summaries. A structured prompt — preserve identifiers, preserve open questions, preserve constraints, then summarize the rest — produces stable summaries.
3. **Failure-driven prompt refinement.** Per [ACON (OpenReview 2026)](https://openreview.net/pdf?id=7JbSwX6bNL): "ACON reduces memory usage 26-54% while preserving 95%+ task accuracy. The failure-driven guideline optimization approach — where compression prompts are iteratively refined by analyzing cases where compressed context caused failures — is gradient-free and compatible with closed-source models." The compression prompt itself gets tuned against compression failures.

The contrast with full-reconstruction:

| Approach | What's preserved | What degrades |
|---|---|---|
| **Anchored iterative** | The persistent summary anchor | Recent turns only re-summarized once |
| **Full-reconstruction** | Nothing across cycles | All older content re-summarized at each cycle; information loss compounds |

The compounding-loss problem is what makes full-reconstruction the dominant failure mode for naive compression. By cycle 5, a full-reconstruction summary has been generated from a summary of a summary of a summary — each cycle losing 5-10% of useful detail. Anchored iterative caps the loss at the first cycle and stabilizes from there.

## Provider-native compaction

Per [Zylos Research February 2026](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies), Anthropic shipped `compact-2026-01-12` as a beta in January 2026:

```python
response = await client.messages.create(
    model="claude-opus-4-7",
    max_tokens=8096,
    betas=["compact-2026-01-12"],
    compaction_config={"trigger_token_count": 50000},
    messages=conversation_history,
)
```

The trigger fires when input token count exceeds `trigger_token_count`; the API generates a compaction and replaces older turns with the summary. The discipline this exposes to the developer: pick the trigger threshold and trust the provider's compaction prompt, or roll your own with the anchored iterative pattern above.

When provider-native makes sense: deployments without specific quality requirements on what gets preserved; teams that want one less moving part; cases where the provider's default prompt is good enough.

When custom anchored iterative makes sense: deployments with domain-specific preservation requirements (medical case IDs, legal jurisdiction tracking, financial transaction references); cases where the compaction prompt itself needs ACON-style refinement against observed failures.

Both compose with the soft cap pattern from [`token-budgets.md`](./token-budgets.md) — the soft cap is what triggers the call into the compaction layer. The compaction layer is what produces the new compact state.

## Agent-centric compression

The 2026 research direction: instead of an external compactor that the agent doesn't control, the *agent itself* decides when to compress and what to preserve. Three approaches in the literature:

### Focus (Active Context Compression)

Per [arxiv:2601.07190 (January 2026)](https://arxiv.org/abs/2601.07190): "the Focus Agent autonomously decides when to consolidate key learnings into a persistent 'Knowledge' block and actively withdraws (prunes) the raw interaction history." Inspired by Physarum polycephalum (slime mold) biological exploration strategies. The agent treats memory consolidation as a tool-like action it explicitly invokes.

### ACON (Agent Context Optimization)

Per [OpenReview 2026](https://openreview.net/pdf?id=7JbSwX6bNL): three compression directions in the literature (document/retrieval-based, dialogue memory summarization, KV cache compression) all fall short for the dynamic and heterogeneous contexts agents produce. ACON addresses this by jointly optimizing across the three surfaces with failure-driven prompt refinement.

### Recursive Language Models

Per [Prime Intellect 2026](https://www.primeintellect.ai/blog/rlm) and [arxiv:2602.02486 (RE-TRAC)](https://arxiv.org/pdf/2602.02486): the agent writes a program that spawns sub-agents to handle compressible work; the sub-agents' contexts can bloat with details; the main agent only sees concise summaries. "This is context isolation in action."

The common pattern: the agent's planning loop includes compression as a first-class operation, not as something that happens silently in the background. The cost: more complex agent design. The benefit: better preservation of what the agent actually needs.

## The recursive summarization trap

Per [Dev|Journal May 2026](https://earezki.com/ai-news/2026-05-11-implementing-prompt-compression-to-reduce-agentic-loop-costs/): "production agents using recursive summarization to reduce 500K token contexts to 32K windows" hit a specific failure mode — "high latency and compute overhead caused by sending redundant context tokens repeatedly."

The trap: each summarization cycle is an LLM call. With aggressive soft caps (compress every N turns), the total compression cost can exceed what the original full context would have cost to pass through. The math:

- Uncompressed: 100K-token input × 1 LLM call = 100K input tokens
- Compressed every 10 turns: 50K-token input × 10 LLM calls + 10 summarization calls (each ~5K input + 1K output) = 500K + 50K + 10K = 560K total tokens

The 5.6× total token usage is what produces the latency and cost overhead. Three mitigations:

1. **Trigger compression on token-count thresholds, not turn counts.** A turn-count trigger fires on conversations that don't need compression. A token-count trigger fires only when the budget is actually approached.
2. **Use cheaper models for the compression call.** Haiku-class models can compress conversation history at ~10% the cost of Opus-class models; the quality is usually sufficient for the summary prompt.
3. **Cache the compaction result.** A compaction is deterministic given the same input; cache the result so the same conversation doesn't get re-compressed.

The deeper trap: information loss across cycles when the compaction prompt isn't anchored. Per the anchored iterative pattern above, the persistent summary state prevents the loss-compounding. Without it, recursive summarization is a slow degradation pipeline.

## Operational discipline

Five practices for sustained compression hygiene:

1. **Instrument compaction events**. Every compaction emits a trace event: trigger reason (soft cap hit on which zone), tokens before, tokens after, compaction strategy used, downstream task success. The 65% context-drift failure rate from [Zylos](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies) is only addressable when compaction-quality metrics are visible.
2. **Measure post-compaction task success rate**. The metric that matters: does the agent succeed at the task after the compaction? A compaction that reduces tokens by 40% but drops task success rate by 20% is a net loss. Path 06 v2 Lab 24's regression set is where these get tracked.
3. **Preserve identifier vocabulary in the compaction prompt**. The structured prompt explicitly lists what categories of content must survive — case IDs, transaction IDs, open blockers, user constraints. Generic "summarize the above" doesn't preserve these reliably.
4. **A/B test compaction strategies against each other**. Provider-native vs custom anchored iterative vs full-reconstruction can be A/B'd on production traffic. The winning strategy is task-specific; no universal best.
5. **Don't compress the system prompt zone**. Zone 1 from [`foundations.md`](./foundations.md) is authored, not accumulated. Compression doesn't apply; only prompt caching does (Layer 3a of cost engineering).

## Anti-patterns

Three compression patterns that look reasonable and aren't:

### Compressing too early

A soft cap at 30% of budget triggers compression on conversations that don't need it. The compression cost (LLM call) is incurred for no quality benefit (the agent had plenty of headroom). The right trigger threshold is 70-80% of budget — enough headroom that the post-compression state has room to grow before the next cycle.

### Full-reconstruction summarization

Regenerating the summary from the full raw history each cycle. Information loss compounds; the summary drifts further from the original at each cycle. The anchored iterative pattern is what production-mature systems use; full-reconstruction is the naive default that should be replaced when discovered.

### Compression without preservation requirements

A summarization prompt that says "summarize the above conversation" produces what the LLM thinks is salient. The agent's downstream task often needs specific identifiers / constraints / blockers that the generic prompt doesn't preserve. Domain-specific compaction prompts (medical, legal, financial) outperform generic prompts by 20-40% on task success in the Factory study.

## Anti-scope

What this page does not cover:

- **Memory-tier separation** (short-term / long-term / episodic) — that's Module 4 (`memory-tiers.md`). This page covers what happens *within* the conversation-history zone; Module 4 covers the broader architecture across tiers.
- **Context drift detection** — the four early-warning signals — that's Module 5 (`context-drift-detection.md`, planned). Drift is what compression should prevent; detection is the monitoring layer.
- **Long-context model selection** — when to use 1M-token models vs compressing aggressively — that's Module 6 (`long-context-models.md`, planned). The Claude Opus 4.7 1M-token-at-flat-pricing change ([`memory-tiers.md`](../memory/memory-tiers.md)) shifts when compression is the right answer.
- **KV cache mechanics in detail**. Masking touches KV cache reuse; the production discipline lives in [`../../production/cost-engineering.md`](../../production/cost-engineering.md) Layer 3a (prompt caching).
- **Specific framework abstractions** (LangChain `ConversationSummaryBufferMemory` — now deprecated per the 2026 LangChain memory migration; LangGraph `checkpointer` summarization hooks; OpenAI Agents SDK compaction APIs). Per Path 05 anti-scope, framework wrappers are addressed at the conceptual layer only.
- **Domain-specific compaction prompt engineering**. Medical / legal / financial preservation requirements are real but vary by domain; this page covers the structural discipline.

## References

**Compression research (2026)**:
- [Zylos Research (February 2026), *AI Agent Context Compression: Strategies for Long-Running Sessions*](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies) — 65% context-drift failure rate; Factory 36,000-session anchored-iterative-vs-full-reconstruction evaluation; Anthropic `compact-2026-01-12` API
- [ACON (OpenReview 2026), *Optimizing Context Compression for Long-Horizon LLM Agents*](https://openreview.net/pdf?id=7JbSwX6bNL) — 26-54% memory reduction with 95%+ task accuracy; failure-driven guideline optimization; gradient-free closed-source compatibility
- [arxiv:2601.07190 (January 2026), *Active Context Compression: Autonomous Memory Management in LLM Agents*](https://arxiv.org/abs/2601.07190) — Focus agent-centric architecture; Physarum polycephalum inspiration; agent-decided consolidation
- [arxiv:2602.02486, *RE-TRAC: REcursive TRAjectory Compression for Deep Search Agents*](https://arxiv.org/pdf/2602.02486) — recursive trajectory compression; 128K-256K context settings
- [Prime Intellect (2026), *Recursive Language Models: the paradigm of 2026*](https://www.primeintellect.ai/blog/rlm) — RLM harness; context folding; DeepDive / math-python / Oolong evaluation environments
- [Lee Kangwook (March 2026), *Toward More Efficient and Useful LLM Agents*](https://kangwooklee.com/talks/2026_03_BLISS/bliss_seminar_monograph.html) — Manus masking pattern (KV cache reuse via logit masking); sub-agent context isolation

**Production patterns (2026)**:
- [Dev|Journal (May 2026), *Implementing Prompt Compression to Reduce Agentic Loop Costs*](https://earezki.com/ai-news/2026-05-11-implementing-prompt-compression-to-reduce-agentic-loop-costs/) — quadratic agentic loop costs; recursive summarization trap; 500K→32K reduction patterns

**Repo cross-references**:
- [`foundations.md`](./foundations.md) — Module 1; three-zone vocabulary this page operates on
- [`token-budgets.md`](./token-budgets.md) — Module 2; soft cap is what triggers compression; hard cap is what compression prevents
- [`../memory/memory-tiers.md`](../memory/memory-tiers.md) — Module 4; the broader memory architecture this page's history-zone compaction is one piece of
- [`../../production/cost-engineering.md`](../../production/cost-engineering.md) — Layer 3a (prompt caching) is what masking preserves; Layer 4 (budgets) is the cost layer compression operates within
- [`../../security/prompt-injection.md`](../../security/prompt-injection.md) — Defense 3 (tool-output sanitization) handles tool-result compression at the security layer
- [Path 03 Pattern 2 — Shared-state boundaries](../../learning-paths/03-multi-agent-systems/patterns/02-shared-state-boundaries.md) — 15× token-burn case; the failure shape compression addresses
- [Path 06 v2 — Adversarial red-teaming at scale](../evaluation/adversarial-red-teaming-at-scale.md) — Lab 24's regression set is where compaction-quality metrics live
