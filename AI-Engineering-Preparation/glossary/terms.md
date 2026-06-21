# Glossary

Shared vocabulary for the track. Terms are added as the batches that introduce them land; entries are alphabetical and link to where the term is used.

**Advantage.** In policy-gradient RL, how much better an action did than a baseline (the state's value): A(s, a) = Q(s, a) − V(s). Subtracting the baseline cuts variance without changing the optimum. → `concepts/rl/policy-gradients.md`.

**Agent.** A system that uses a model to pursue a goal over multiple steps, deciding actions, calling tools, and reacting to results rather than answering in a single pass. → `concepts/agents/`.

**Attention.** The mechanism that lets each token build a new representation by pulling in information from other tokens, weighted by relevance: a query matches keys, a softmax turns matches into weights, and the output blends values. Defines the transformer. → `concepts/llm/attention.md`.

**BPE (byte-pair encoding).** A subword tokenization algorithm that starts from characters and repeatedly merges the most frequent adjacent pair, so common words become single tokens and rare words fall back to pieces. → `concepts/llm/tokens-and-embeddings.md`.

**Concept drift.** A change in the input-to-output relationship itself, so the same inputs now map to a different correct output; harder to detect than data drift because inputs can look familiar. → `concepts/ml-system-design/monitoring-and-drift.md`.

**Context window.** The maximum span of tokens a model can attend to in one request. Instructions, state, retrieved memory, tool schemas, tool outputs, and the user's message all compete for it. → `concepts/context/`.

**Cosine similarity.** The dot product of two length-normalized vectors, bounded in [-1, 1]; it compares direction (meaning) rather than magnitude, and is the measure behind retrieval. → `math-foundations/01-embeddings-and-similarity.md`.

**Data drift (covariate shift).** A change in the distribution of model inputs (new segments, seasons, products) without necessarily changing the learned relationship; detectable without labels. → `concepts/ml-system-design/monitoring-and-drift.md`.

**Discount factor (γ).** A weight in [0, 1) that makes sooner rewards count more in the return, setting how far ahead an RL agent looks and keeping the sum finite. → `math-foundations/02-rl-objectives.md`.

**Embedding.** A numeric vector representing text (or other data) so that similar meanings sit close together, enabling search by meaning rather than exact keywords. → `concepts/vector-db/`.

**Feature store.** A system that computes, stores, and serves features from one definition to both training and serving, preventing training/serving skew; usually an offline (throughput) and an online (low-latency) half. → `concepts/ml-system-design/feature-stores.md`.

**Fine-tuning.** Continuing to train a model on your data to change its behavior — tone, format, narrow skills — baking the change into the weights, as opposed to retrieval, which changes knowledge externally. → `concepts/llm/fine-tuning-vs-retrieval.md`.

**Hallucination.** Fluent, confident model output that is not grounded in fact, produced because the model predicts probable continuations rather than verifying them. → `concepts/llm/hallucination-and-cutoff.md`.

**Knowledge cutoff.** The date past which a model has no parametric knowledge, because its weights were fixed at the end of training; the structural reason models cannot know recent or private facts on their own. → `concepts/llm/hallucination-and-cutoff.md`.

**Logits.** The raw, unnormalized scores a model emits for every vocabulary token at a step, turned into probabilities by a softmax before decoding. → `concepts/llm/decoding-and-sampling.md`.

**Memory (agent).** Information an agent carries across tasks — past decisions, lasting preferences, and external reference data — as distinct from state, which is the current task. → `concepts/memory/`.

**Policy.** In RL, the agent's strategy: a mapping from state to action (or a distribution over actions). It is the thing being learned. → `concepts/rl/rl-primitives.md`.

**Policy gradient.** A family of RL methods that adjust a parameterized policy directly, raising the probability of actions with positive advantage; scales to large and continuous action spaces. → `concepts/rl/policy-gradients.md`.


**PPMI (positive pointwise mutual information).** A re-weighting of co-occurrence counts by how much more than chance two items co-occur, clamped at zero; it suppresses frequent words so embedding geometry tracks meaning. → `math-foundations/01-embeddings-and-similarity.md`.

**PPO (proximal policy optimization).** A policy-gradient method that clips each update so the new policy stays close to the old one, trading speed for the stability that makes RL on large models practical; the usual optimizer in RLHF. → `concepts/rl/policy-gradients.md`.

**Q-learning.** A model-free, off-policy, value-based RL algorithm that learns Q[state][action] via the temporal-difference update toward r + γ·max Q(next); the greedy policy on Q converges to optimal. → `concepts/rl/rl-primitives.md`.

**RAG (retrieval-augmented generation).** Supplying a model with relevant retrieved context at query time so its answer is grounded in current, citable sources instead of only its frozen parameters. → `concepts/rag/`.

**Reinforcement learning (RL).** Learning to act from reward signals and consequences rather than labeled examples, via an agent interacting with an environment. → `concepts/rl/rl-primitives.md`.

**Reward.** The scalar an RL environment returns after an action — the only signal of what is good; designing it well is the hard part. → `concepts/rl/rl-primitives.md`.

**Reward hacking.** When a policy optimizes the reward it is given rather than the one intended, exploiting flaws in a reward model (length, sycophancy) to score well without real quality. → `concepts/rl/rlhf.md`.

**Reward model.** A model fit from human pairwise preferences (Bradley-Terry) that scores outputs so preferred ones score higher; it stands in for a hand-written reward in RLHF. → `concepts/rl/rlhf.md`.

**RLHF (reinforcement learning from human feedback).** Aligning a model by learning a reward from human comparisons, then optimizing a policy against it: SFT, reward model, RL with a KL penalty. → `concepts/rl/rlhf.md`.

**Softmax.** The function that turns a vector of logits into a probability distribution that sums to one; used both inside attention and at the output to define next-token probabilities. → `concepts/llm/decoding-and-sampling.md`.

**State (agent).** The agent's picture of the current task: the plan, active constraints, what is done, and what comes next. → `concepts/memory/`.

**Temperature.** A decoding control that scales logits before the softmax: below 1 sharpens the distribution (more deterministic), above 1 flattens it (more varied), and 0 reduces to greedy. → `concepts/llm/decoding-and-sampling.md`.

**Token.** The unit a model actually processes — an integer id for a piece of text from a fixed vocabulary, often a subword. Budget and cost are counted in tokens, not words. → `concepts/llm/tokens-and-embeddings.md`.

**Tokenization.** Splitting text into tokens from a fixed vocabulary and mapping them to ids; modern models use subword tokenization such as BPE. → `concepts/llm/tokens-and-embeddings.md`.

**Top-k / top-p.** Decoding controls that restrict sampling to the k most probable tokens (top-k) or to the smallest set whose probabilities sum to p (top-p, "nucleus"), capping how far into the tail the model can reach. → `concepts/llm/decoding-and-sampling.md`.

**Training/serving skew.** When features computed in the live serving path differ from those used in training (different window, defaults, timing), silently degrading accuracy; what feature stores exist to prevent. → `concepts/ml-system-design/feature-stores.md`.

**Value.** The expected long-run (discounted) reward from a state, or state-action pair, under a policy — not the immediate reward but everything that follows. → `concepts/rl/rl-primitives.md`.
