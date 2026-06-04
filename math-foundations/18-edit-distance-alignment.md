# Edit-distance alignment and error decomposition

> Mathematical foundation. About 10 minutes to read. Anchors: [`labs/63-ocr-on-real-images/`](../labs/63-ocr-on-real-images/), [`labs/62-ocr-reading-quality/`](../labs/62-ocr-reading-quality/). Builds on [`17-multimodal-eval-metrics.md`](./17-multimodal-eval-metrics.md).

## Why this matters for agentic AI

CER and WER give a single number, but when you are debugging a real OCR or transcription pipeline the number is not enough - you need to know *which* characters are being confused and whether the engine is dropping, inserting, or substituting them, because each points at a different fix (resolution, deskew, a font issue, a language model). The edit distance already contains that information; you recover it by backtracing the dynamic program to an alignment and decomposing the errors into substitutions, insertions, and deletions.

## The alignment, not just the distance

Page 17 defined the Levenshtein distance by the DP recurrence on the matrix $D$ with $D_{i,j}$ the distance between the length-$i$ prefix of the reference $r$ and the length-$j$ prefix of the hypothesis $h$. The value $D_{n,m}$ is the distance. The *alignment* is the path through the matrix that achieves it, recovered by backtracing from $(n, m)$ to $(0, 0)$: at each cell, the move that attained the minimum is the operation taken.

$$
(i, j) \;\leftarrow\;
\begin{cases}
(i-1, j-1) & \text{match/substitution, if } D_{i,j} = D_{i-1,j-1} + \mathbb{1}[r_i \ne h_j] \\
(i-1, j) & \text{deletion, if } D_{i,j} = D_{i-1,j} + 1 \\
(i, j-1) & \text{insertion, if } D_{i,j} = D_{i,j-1} + 1
\end{cases}
$$

A match consumes one character from each string at no cost; a substitution does the same at cost 1; a deletion consumes a reference character ($h$ is missing it); an insertion consumes a hypothesis character ($h$ has an extra). The alignment is read off the reversed sequence of moves.

## The S/I/D decomposition

Count the operations on the optimal path as $S$ substitutions, $I$ insertions, $D$ deletions. Then

$$
d(r, h) = S + I + D, \qquad \text{CER} = \frac{S + I + D}{|r|}.
$$

This is the same identity WER uses at the word level, which is why speech and OCR error reports always break the rate into these three. The decomposition is what makes the metric diagnostic: a pipeline dominated by deletions is *losing* characters (under-segmentation, faint strokes, aggressive binarization), one dominated by insertions is *hallucinating* them (speckle noise read as punctuation, JPEG ringing), and one dominated by substitutions is *confusing* them (look-alike glyphs, low resolution). The fixes differ, and the single CER cannot tell them apart.

As a worked example, the real misread from [Lab 63](../labs/63-ocr-on-real-images/) of "annual revenue 9.4 billion" as "arsual revenue 94 bien" has $d = 7$ with $S = 3$, $I = 0$, $D = 4$: three look-alike substitutions (n to r, n to s, o to e) and four deletions, including the deleted decimal point that turns 9.4 into 94. The substitution list is a character **confusion profile** - aggregate it over a corpus and the systematic glyph confusions of the engine and font appear directly.

## Non-uniqueness, and what to fix

The minimal alignment is not unique: when more than one move attains the minimum, different backtrace conventions yield different - equally optimal - alignments, so the split between, say, a substitution and an adjacent insertion+deletion can vary. The distance and CER are invariant; the per-type counts can shift slightly at ties. For diagnosis this rarely matters because systematic errors dominate the tie noise, but if you report S/I/D rates, fix a convention (a consistent tie-break order) so the numbers are comparable across runs.

## The link back to value-aware scoring

The decomposition also explains why CER is the wrong score for a number, sharpening page 17's point. The decimal-point deletion above is a single deletion - one unit of edit distance, a contribution of $1/|r|$ to CER - yet it multiplies the value by ten. Edit distance treats every character as one unit of cost; the information content of the characters in a number is wildly non-uniform. No reweighting of insert/delete/substitute costs recovers correctness, because the damage is in the *value*, not the *string*. That is the structural reason a numeric answer needs a value-aware metric alongside CER, and why a single deleted character is the most dangerous OCR error of all.

## What to remember

- Backtrace the DP to an alignment; the distance alone hides the error structure.
- Decompose into substitutions, insertions, and deletions: $d = S + I + D$, and each type points at a different cause and fix.
- Aggregate the substitutions into a confusion profile to find systematic glyph errors.
- The alignment is not unique at ties; fix a convention before comparing S/I/D rates.
- A single deletion (a lost decimal point) is one unit of CER and a tenfold value error - the math reason numbers need a value-aware check.

## See also

- [`17-multimodal-eval-metrics.md`](./17-multimodal-eval-metrics.md) - CER/WER and the end-to-end decomposition this refines.
- [`labs/63-ocr-on-real-images/`](../labs/63-ocr-on-real-images/) - real OCR whose errors this decomposes.
- [`labs/62-ocr-reading-quality/`](../labs/62-ocr-reading-quality/) - the metric definitions and numeric tolerance.
