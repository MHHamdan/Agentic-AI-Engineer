# Glossary

Shared vocabulary for the track. Terms are added as the batches that introduce them land; entries are alphabetical and link to where the term is used.

> Batch 00: seed entries. The glossary grows per batch.

**Agent.** A system that uses a model to pursue a goal over multiple steps, deciding actions, calling tools, and reacting to results rather than answering in a single pass. → `concepts/agents/`.

**Context window.** The maximum span of tokens a model can attend to in one request. Instructions, state, retrieved memory, tool schemas, tool outputs, and the user's message all compete for it. → `concepts/context/`.

**Embedding.** A numeric vector representing text (or other data) so that similar meanings sit close together, enabling search by meaning rather than exact keywords. → `concepts/vector-db/`.

**Memory (agent).** Information an agent carries across tasks — past decisions, lasting preferences, and external reference data — as distinct from state, which is the current task. → `concepts/memory/`.

**RAG (retrieval-augmented generation).** Supplying a model with relevant retrieved context at query time so its answer is grounded in current, citable sources instead of only its frozen parameters. → `concepts/rag/`.

**State (agent).** The agent's picture of the current task: the plan, active constraints, what is done, and what comes next. → `concepts/memory/`.
