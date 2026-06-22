# Glossary

**Abstention.** Returning "I don't have evidence for that" instead of answering, when retrieval finds nothing relevant; a core defense against RAG hallucination. → `concepts/rag/rag-end-to-end.md`.

**Advantage.** In policy-gradient RL, how much better an action did than a baseline (the state's value): A(s, a) = Q(s, a) − V(s). Subtracting the baseline cuts variance without changing the optimum. → `concepts/rl/policy-gradients.md`.

**Agent.** A system that uses a model to pursue a goal over multiple steps, deciding actions, calling tools, and reacting to results rather than answering in a single pass. → `concepts/agents/`.

**ANN (approximate nearest neighbor).** Search that returns vectors close to the true nearest neighbors much faster than exact search, trading a little recall for large speedups; the core of a vector database. → `concepts/vector-db/similarity-and-ann.md`.

**Attention.** The mechanism that lets each token build a new representation by pulling in information from other tokens, weighted by relevance: a query matches keys, a softmax turns matches into weights, and the output blends values. Defines the transformer. → `concepts/llm/attention.md`.

**Bi-encoder.** A retrieval model that embeds the query and each document independently, so document vectors can be precomputed and indexed; fast but less precise than a cross-encoder. → `concepts/rag/chunking-and-retrieval.md`.

**BM25.** A lexical (sparse) retrieval scoring function from the probabilistic relevance framework, weighting term matches by frequency and rarity; a strong keyword-retrieval baseline. → `concepts/rag/chunking-and-retrieval.md`.

**BPE (byte-pair encoding).** A subword tokenization algorithm that starts from characters and repeatedly merges the most frequent adjacent pair, so common words become single tokens and rare words fall back to pieces. → `concepts/llm/tokens-and-embeddings.md`.

**Checkpoint (and rollback).** A snapshot of agent task state taken before a step, so a later correction can roll back to it and re-run only the affected steps rather than restarting. → `concepts/memory/state-vs-memory.md`.

**Chunking.** Splitting documents into passages before embedding them for retrieval; chunk size caps retrieval quality — too large dilutes, too small fragments. → `concepts/rag/chunking-and-retrieval.md`.

**Citation (attribution).** Attributing each claim in an answer to the retrieved chunk it came from, making the answer verifiable and pushing the model to answer from context. → `concepts/rag/reranking-and-citation.md`.

**Compaction.** Reversibly reducing context by stripping content recoverable from the environment and keeping a pointer (e.g. a file path instead of the file's contents); the lightest-touch context reduction. → `concepts/context/context-strategies.md`.

**Concept drift.** A change in the input-to-output relationship itself, so the same inputs now map to a different correct output; harder to detect than data drift because inputs can look familiar. → `concepts/ml-system-design/monitoring-and-drift.md`.

**Consolidation (memory).** Periodically summarizing many small memory entries into compact higher-level ones to keep the store small and retrievable, at the cost of detail. → `concepts/memory/memory-lifecycle.md`.

**Context engineering.** The practice of deliberately designing what a model sees on every inference call, organized as write, select, compress, and isolate. → `concepts/context/context-engineering.md`.

**Context rot.** The measured degradation in model output quality as input length grows, present even below the window limit; driven by lost-in-the-middle, attention dilution, and distractors. → `concepts/context/context-rot-and-failure-modes.md`.

**Concept drift.** A change in the input-to-output relationship itself, so the same inputs now map to a different correct output; harder to detect than data drift because inputs can look familiar. → `concepts/ml-system-design/monitoring-and-drift.md`.

**Context window.** The maximum span of tokens a model can attend to in one request. Instructions, state, retrieved memory, tool schemas, tool outputs, and the user's message all compete for it. → `concepts/context/`.

**Cosine similarity.** The dot product of two length-normalized vectors, bounded in [-1, 1]; it compares direction (meaning) rather than magnitude, and is the measure behind retrieval. → `math-foundations/01-embeddings-and-similarity.md`.

**Cross-encoder.** A reranking model that reads the query and a candidate chunk together to judge relevance directly; far more accurate than a bi-encoder and far slower, so it runs only on a shortlist. → `concepts/rag/reranking-and-citation.md`.

**Data drift (covariate shift).** A change in the distribution of model inputs (new segments, seasons, products) without necessarily changing the learned relationship; detectable without labels. → `concepts/ml-system-design/monitoring-and-drift.md`.

**Discount factor (γ).** A weight in [0, 1) that makes sooner rewards count more in the return, setting how far ahead an RL agent looks and keeping the sum finite. → `math-foundations/02-rl-objectives.md`.

**Embedding.** A numeric vector representing text (or other data) so that similar meanings sit close together, enabling search by meaning rather than exact keywords. → `concepts/vector-db/`.

**External memory.** Reference knowledge an agent retrieves from but does not hold in context — documents, a knowledge base, a vector index; effectively unbounded. → `concepts/memory/memory-types.md`.

**Feature store.** A system that computes, stores, and serves features from one definition to both training and serving, preventing training/serving skew; usually an offline (throughput) and an online (low-latency) half. → `concepts/ml-system-design/feature-stores.md`.

**Fine-tuning.** Continuing to train a model on your data to change its behavior — tone, format, narrow skills — baking the change into the weights, as opposed to retrieval, which changes knowledge externally. → `concepts/llm/fine-tuning-vs-retrieval.md`.

**Grounding.** Answering from retrieved source text rather than parametric memory, so claims can be traced to evidence. → `concepts/rag/rag-end-to-end.md`.

**Hallucination.** Fluent, confident model output that is not grounded in fact, produced because the model predicts probable continuations rather than verifying them. → `concepts/llm/hallucination-and-cutoff.md`.

**HNSW (hierarchical navigable small world).** A graph-based ANN index that greedily walks a layered neighbor graph toward the query; high recall at low latency, at a memory cost. → `concepts/vector-db/hnsw.md`.

**Hybrid retrieval.** Combining lexical and dense retrieval scores; often strongest because the two methods fail on different queries (exact terms vs. paraphrase). → `concepts/rag/chunking-and-retrieval.md`.

**IVF (inverted file).** An ANN index that clusters vectors into cells (k-means) and searches only the cells nearest the query; nprobe sets how many cells are searched. → `concepts/vector-db/ivf-and-quantization.md`.

**Just-in-time retrieval.** Holding lightweight identifiers (file paths, queries) and loading the underlying content into context only when a step needs it, instead of front-loading everything. → `concepts/context/context-strategies.md`.

**Knowledge cutoff.** The date past which a model has no parametric knowledge, because its weights were fixed at the end of training; the structural reason models cannot know recent or private facts on their own. → `concepts/llm/hallucination-and-cutoff.md`.

**Logits.** The raw, unnormalized scores a model emits for every vocabulary token at a step, turned into probabilities by a softmax before decoding. → `concepts/llm/decoding-and-sampling.md`.

**Long-term memory.** Information that persists across sessions — preferences, conventions, summaries of past conversations — retrieved into context when relevant. → `concepts/memory/memory-types.md`.

**Lost in the middle.** The tendency of models to attend well to the start and end of a context but poorly to the middle, so buried facts are missed. → `concepts/context/context-rot-and-failure-modes.md`.

**Memory (agent).** Information an agent carries across tasks — past decisions, lasting preferences, and external reference data — as distinct from state, which is the current task. → `concepts/memory/`.

**nprobe.** The IVF knob for how many clusters to search: more probes give higher recall and more work; probing every cluster reduces to exact search. → `concepts/vector-db/ivf-and-quantization.md`.

**Policy.** In RL, the agent's strategy: a mapping from state to action (or a distribution over actions). It is the thing being learned. → `concepts/rl/rl-primitives.md`.

**Policy gradient.** A family of RL methods that adjust a parameterized policy directly, raising the probability of actions with positive advantage; scales to large and continuous action spaces. → `concepts/rl/policy-gradients.md`.

**PPMI (positive pointwise mutual information).** A re-weighting of co-occurrence counts by how much more than chance two items co-occur, clamped at zero; it suppresses frequent words so embedding geometry tracks meaning. → `math-foundations/01-embeddings-and-similarity.md`.

**PPO (proximal policy optimization).** A policy-gradient method that clips each update so the new policy stays close to the old one, trading speed for the stability that makes RL on large models practical; the usual optimizer in RLHF. → `concepts/rl/policy-gradients.md`.

**Product quantization (PQ).** Compressing vectors into short codes from learned codebooks, cutting index memory and comparison cost for some loss of recall; often combined with IVF. → `concepts/vector-db/ivf-and-quantization.md`.

**Q-learning.** A model-free, off-policy, value-based RL algorithm that learns Q[state][action] via the temporal-difference update toward r + γ·max Q(next); the greedy policy on Q converges to optimal. → `concepts/rl/rl-primitives.md`.

**RAG (retrieval-augmented generation).** Supplying a model with relevant retrieved context at query time so its answer is grounded in current, citable sources instead of only its frozen parameters. → `concepts/rag/`.

**Recall@k.** Of the true k nearest neighbors, the fraction an approximate index actually returns; the quality axis of an ANN tradeoff curve. → `math-foundations/03-nearest-neighbor-search.md`.

**Reinforcement learning (RL).** Learning to act from reward signals and consequences rather than labeled examples, via an agent interacting with an environment. → `concepts/rl/rl-primitives.md`.

**Reranker.** A second-stage model that re-scores a retrieved shortlist for precision before generation, typically a cross-encoder. → `concepts/rag/reranking-and-citation.md`.

**Retrieval (lexical / dense).** Lexical retrieval matches words (TF-IDF, BM25); dense retrieval matches meaning via embeddings; hybrid combines them. → `concepts/rag/chunking-and-retrieval.md`.

**Reward.** The scalar an RL environment returns after an action — the only signal of what is good; designing it well is the hard part. → `concepts/rl/rl-primitives.md`.

**Reward hacking.** When a policy optimizes the reward it is given rather than the one intended, exploiting flaws in a reward model (length, sycophancy) to score well without real quality. → `concepts/rl/rlhf.md`.

**Reward model.** A model fit from human pairwise preferences (Bradley-Terry) that scores outputs so preferred ones score higher; it stands in for a hand-written reward in RLHF. → `concepts/rl/rlhf.md`.

**RLHF (reinforcement learning from human feedback).** Aligning a model by learning a reward from human comparisons, then optimizing a policy against it: SFT, reward model, RL with a KL penalty. → `concepts/rl/rlhf.md`.

**Short-term (working) memory.** The in-context conversation so far — messages, tool calls, and tool results — bounded by the window and gone when the session ends. → `concepts/memory/memory-types.md`.

**Softmax.** The function that turns a vector of logits into a probability distribution that sums to one; used both inside attention and at the output to define next-token probabilities. → `concepts/llm/decoding-and-sampling.md`.

**State (agent).** The agent's picture of the current task: the plan, active constraints, what is done, and what comes next. → `concepts/memory/`.

**Sub-agent isolation.** Giving a subtask its own context window via a sub-agent that returns only a concise result, keeping the main agent's window free of subtask clutter. → `concepts/context/context-strategies.md`.

**Summarization (context).** Lossily reducing a stretch of history into a shorter form with a model, recovering window space at the cost of discarded detail; used when reversible compaction is not enough. → `concepts/context/context-strategies.md`.

**Temperature.** A decoding control that scales logits before the softmax: below 1 sharpens the distribution (more deterministic), above 1 flattens it (more varied), and 0 reduces to greedy. → `concepts/llm/decoding-and-sampling.md`.

**TF-IDF.** A lexical weighting that scores a term by its frequency in a document (TF) times its rarity across the corpus (IDF), so distinctive words drive the match. → `concepts/rag/chunking-and-retrieval.md`.

**Token.** The unit a model actually processes — an integer id for a piece of text from a fixed vocabulary, often a subword. Budget and cost are counted in tokens, not words. → `concepts/llm/tokens-and-embeddings.md`.

**Tokenization.** Splitting text into tokens from a fixed vocabulary and mapping them to ids; modern models use subword tokenization such as BPE. → `concepts/llm/tokens-and-embeddings.md`.

**Top-k / top-p.** Decoding controls that restrict sampling to the k most probable tokens (top-k) or to the smallest set whose probabilities sum to p (top-p, "nucleus"), capping how far into the tail the model can reach. → `concepts/llm/decoding-and-sampling.md`.

**Training/serving skew.** When features computed in the live serving path differ from those used in training (different window, defaults, timing), silently degrading accuracy; what feature stores exist to prevent. → `concepts/ml-system-design/feature-stores.md`.

**Value.** The expected long-run (discounted) reward from a state, or state-action pair, under a policy — not the immediate reward but everything that follows. → `concepts/rl/rl-primitives.md`.

**Vector database.** A store that indexes embeddings for fast approximate nearest-neighbor search at scale; the search layer under retrieval. → `concepts/vector-db/similarity-and-ann.md`.
