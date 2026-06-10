---
title: Bloom Filters
slug: bloom-filters
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Batch vs Stream Processing
unlocks:
  - Geohashing
related_topics:
  - Batch vs Stream Processing
  - Geohashing
code_lab: ../../../labs/28-bloom-filters/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Bloom Filters.

## What You Will Build

A minimal Python example under labs/28-bloom-filters/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/28-bloom-filters/demo.py
- labs/28-bloom-filters/test_bloom_filters.py

## Run the Example

```bash
cd labs/28-bloom-filters
python demo.py
```

## Expected Output

The script should show how Bloom Filters changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for false positive probability, bit-array size, number of hash functions, and insert count.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Batch vs Stream Processing](../27-batch-vs-stream-processing/concept.md)
- [Geohashing](../29-geohashing/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Batch vs Stream Processing](../27-batch-vs-stream-processing/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Geohashing](../29-geohashing/concept.md)


