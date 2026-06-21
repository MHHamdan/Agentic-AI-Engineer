# Glossary

Shared vocabulary for the track. Terms are added as the batches that introduce them land; entries are alphabetical and link to where the term is used.

**Agent.** A system that uses a model to pursue a goal over multiple steps, deciding actions, calling tools, and reacting to results rather than answering in a single pass. → `concepts/agents/`.

**Attention.** The mechanism that lets each token build a new representation by pulling in information from other tokens, weighted by relevance: a query matches keys, a softmax turns matches into weights, and the output blends values. Defines the transformer. → `concepts/llm/attention.md`.

**BPE (byte-pair encoding).** A subword tokenization algorithm that starts from characters and repeatedly merges the most frequent adjacent pair, so common words become single tokens and rare words fall back to pieces. → `concepts/llm/tokens-and-embeddings.md`.

**Context window.** The maximum span of tokens a model can attend to in one request. Instructions, state, retrieved memory, tool schemas, tool outputs, and the user's message all compete for it. → `concepts/context/`.

**Cosine similarity.** The dot product of two length-normalized vectors, bounded in [-1, 1]; it compares direction (meaning) rather than magnitude, and is the measure behind retrieval. → `math-foundations/01-embeddings-and-similarity.md`.

**Embedding.** A numeric vector representing text (or other data) so that similar meanings sit close together, enabling search by meaning rather than exact keywords. → `concepts/vector-db/`.

**Fine-tuning.** Continuing to train a model on your data to change its behavior — tone, format, narrow skills — baking the change into the weights, as opposed to retrieval, which changes knowledge externally. → `concepts/llm/fine-tuning-vs-retrieval.md`.

**Hallucination.** Fluent, confident model output that is not grounded in fact, produced because the model predicts probable continuations rather than verifying them. → `concepts/llm/hallucination-and-cutoff.md`.

**Knowledge cutoff.** The date past which a model has no parametric knowledge, because its weights were fixed at the end of training; the structural reason models cannot know recent or private facts on their own. → `concepts/llm/hallucination-and-cutoff.md`.

**Logits.** The raw, unnormalized scores a model emits for every vocabulary token at a step, turned into probabilities by a softmax before decoding. → `concepts/llm/decoding-and-sampling.md`.

**Memory (agent).** Information an agent carries across tasks — past decisions, lasting preferences, and external reference data — as distinct from state, which is the current task. → `concepts/memory/`.

**PPMI (positive pointwise mutual information).** A re-weighting of co-occurrence counts by how much more than chance two items co-occur, clamped at zero; it suppresses frequent words so embedding geometry tracks meaning. → `math-foundations/01-embeddings-and-similarity.md`.

**RAG (retrieval-augmented generation).** Supplying a model with relevant retrieved context at query time so its answer is grounded in current, citable sources instead of only its frozen parameters. → `concepts/rag/`.

**Softmax.** The function that turns a vector of logits into a probability distribution that sums to one; used both inside attention and at the output to define next-token probabilities. → `concepts/llm/decoding-and-sampling.md`.

**State (agent).** The agent's picture of the current task: the plan, active constraints, what is done, and what comes next. → `concepts/memory/`.

**Temperature.** A decoding control that scales logits before the softmax: below 1 sharpens the distribution (more deterministic), above 1 flattens it (more varied), and 0 reduces to greedy. → `concepts/llm/decoding-and-sampling.md`.

**Token.** The unit a model actually processes — an integer id for a piece of text from a fixed vocabulary, often a subword. Budget and cost are counted in tokens, not words. → `concepts/llm/tokens-and-embeddings.md`.

**Tokenization.** Splitting text into tokens from a fixed vocabulary and mapping them to ids; modern models use subword tokenization such as BPE. → `concepts/llm/tokens-and-embeddings.md`.

**Top-k / top-p.** Decoding controls that restrict sampling to the k most probable tokens (top-k) or to the smallest set whose probabilities sum to p (top-p, "nucleus"), capping how far into the tail the model can reach. → `concepts/llm/decoding-and-sampling.md`.
