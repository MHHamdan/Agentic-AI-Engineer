# Embeddings and similarity

> Mathematical foundation. ~8 min. Anchor: [`labs/01-tokenization-and-embeddings/`](../labs/01-tokenization-and-embeddings/). Supports [tokens and embeddings](../concepts/llm/tokens-and-embeddings.md).

## Why this matters

Every retrieval system, every "find similar" feature, and every vector database rests on one operation: measuring how close two vectors are. This page defines that operation, explains why cosine similarity is the usual choice for text, and shows why raw counts need re-weighting before the geometry means anything.

## Vectors, dot product, norm

An embedding is a vector $x \in \mathbb{R}^d$. Two quantities define the geometry. The **dot product**

$$
x \cdot y = \sum_{i=1}^{d} x_i y_i
$$

measures aligned magnitude, and the **norm** $\lVert x \rVert = \sqrt{x \cdot x}$ measures length. The angle $\theta$ between $x$ and $y$ satisfies $x \cdot y = \lVert x \rVert \lVert y \rVert \cos\theta$.

## Cosine similarity

**Cosine similarity** is the dot product of the length-normalized vectors:

$$
\cos(x, y) = \frac{x \cdot y}{\lVert x \rVert\, \lVert y \rVert} \in [-1, 1].
$$

It is $1$ when the vectors point the same way, $0$ when orthogonal, $-1$ when opposite. For text it is usually preferred over Euclidean distance because it ignores magnitude: a long document and a short one on the same topic should count as similar even though their raw count vectors have very different lengths. Normalizing away length keeps the comparison about direction — that is, about meaning — not about how many words were counted. (When vectors are already unit-normalized, cosine and dot product coincide, which is why many vector indexes store normalized vectors and rank by dot product.)

## Why raw counts mislead, and PPMI

If $x$ is a word's row in a co-occurrence matrix, cosine already ranks related words above unrelated ones — but imperfectly, because frequent words like "the" co-occur with everything and inflate every similarity. Pointwise Mutual Information corrects for chance co-occurrence:

$$
\text{PMI}(a, b) = \log \frac{p(a, b)}{p(a)\,p(b)}, \qquad \text{PPMI}(a, b) = \max\big(\text{PMI}(a, b),\, 0\big).
$$

The ratio compares how often $a$ and $b$ actually co-occur to how often they would by chance if independent. Dividing by $p(a)p(b)$ deflates pairs that are common only because the words are common, so ubiquitous words stop dominating. Clamping at zero (PPMI) keeps the well-estimated positive associations and discards the noisy negatives. In the lab this drops $\cos(\text{cat}, \text{car})$ from $0.77$ to $0.07$ while $\cos(\text{cat}, \text{dog})$ stays at $1$ — the same geometry, now measuring meaning.

## Nearest neighbors

"Find similar" is the **nearest-neighbor** problem: given a query vector $q$, return the stored vectors with the highest $\cos(q, x)$. Exact search compares $q$ against every vector, which is $O(nd)$ per query and does not scale to large $n$. Production systems use approximate nearest-neighbor indexes that trade a little recall for large speedups; that tradeoff is the subject of the [vector-db](../concepts/vector-db/) area. The similarity measure, though, is exactly the cosine defined here.

## What to remember

- Cosine similarity is the dot product of normalized vectors, bounded in $[-1, 1]$; it compares direction, not magnitude, which is what you want for text.
- Raw co-occurrence counts are dominated by frequent words; PPMI re-weights by association beyond chance so the geometry tracks meaning.
- "Find similar" is nearest-neighbor search under cosine; scaling it is the vector-database problem.

## See also

- [`labs/01-tokenization-and-embeddings/`](../labs/01-tokenization-and-embeddings/) — cosine and PPMI in code.
- [`concepts/vector-db/`](../concepts/vector-db/) — scaling nearest-neighbor search.
