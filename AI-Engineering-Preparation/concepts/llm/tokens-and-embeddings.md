# Tokens and embeddings

> Concept note. ~9 min. Runnable companion: [`labs/01-tokenization-and-embeddings/`](../../labs/01-tokenization-and-embeddings/). Math: [`math-foundations/01`](../../math-foundations/01-embeddings-and-similarity.md).

A language model never sees your text. It sees a sequence of integer **token ids**, and it works in a space of **vectors**. Two steps bridge the gap, and almost every practical surprise about cost, context limits, and "why does it think these two things are similar" traces back to them.

## Tokenization: text becomes tokens

A tokenizer splits text into units from a fixed vocabulary and maps each to an id. Modern models use **subword** tokenization, most often byte-pair encoding (BPE): start from individual characters and repeatedly merge the most frequent adjacent pair into a new symbol. Frequent words end up as a single token; rare or novel strings fall back to several smaller pieces. A byte-level base vocabulary (the 256 possible bytes) means nothing is ever truly out-of-vocabulary — any string can be represented, just at the cost of more tokens.

The consequence that matters in practice: the model counts **tokens, not words**. A common word is one token; an unusual name, a long URL, or code with rare identifiers can be many. This is the "tokenization tax" — the same idea fills more of the context window and costs more — and it is why you budget in tokens. The runnable lab builds BPE from scratch and shows a trained word collapsing to one token while an unseen word splits into five.

## Embeddings: tokens become meaning

Once text is tokens, each token becomes a vector — an **embedding** — chosen so that closeness in the vector space reflects closeness in meaning. The justification is the distributional hypothesis: words that appear in similar contexts tend to mean similar things. That hypothesis is directly usable: a word's row in a co-occurrence matrix already behaves like an embedding, and the cosine of the angle between two such vectors ranks related words above unrelated ones.

Raw counts have an obvious flaw — frequent words like "the" co-occur with everything, so they dominate. Re-weighting with Positive Pointwise Mutual Information (PPMI), which measures how much more than chance two words co-occur, suppresses the ubiquitous words and surfaces real associations. In the lab this takes the similarity of `cat` and `car` from 0.77 down to 0.07 while `cat` and `dog` stay high.

Production embeddings are **dense** vectors learned by a network rather than raw count rows — word2vec first, then the contextual encoders behind modern retrieval — but the geometry is identical. The cosine similarity you compute by hand here is the exact operation a [vector database](../vector-db/) runs at scale, and the reason retrieval can find passages by meaning rather than keywords.

## What to remember

- The model works in tokens and vectors, never raw text.
- Budget and cost are in tokens; rare strings cost more tokens than their word count suggests.
- Embeddings turn meaning into geometry; cosine similarity is the measuring stick, and PPMI (or a trained network) is what makes the geometry meaningful.

## References

- Sennrich, R., Haddow, B., Birch, A. (2016). *Neural Machine Translation of Rare Words with Subword Units.* arXiv:1508.07909.
- Mikolov, T., et al. (2013). *Efficient Estimation of Word Representations in Vector Space.* arXiv:1301.3781.
- Harris, Z. (1954). *Distributional Structure.* See [`../../references/references.md`](../../references/references.md).
