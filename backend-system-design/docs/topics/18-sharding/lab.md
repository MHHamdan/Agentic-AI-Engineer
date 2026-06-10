---
title: Sharding
slug: sharding
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Indexes
unlocks:
  - Change Data Capture
related_topics:
  - Indexes
  - Change Data Capture
code_lab: ../../../labs/18-sharding/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Sharding.

## What You Will Build

A minimal Python example under labs/18-sharding/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/18-sharding/demo.py
- labs/18-sharding/test_sharding.py

## Run the Example

```bash
cd labs/18-sharding
python demo.py
```

## Expected Output

The script should show how Sharding changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for shard balance, hot shard rate, cross-shard query count, and rebalancing cost.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Indexes](../17-indexes/concept.md)
- [Change Data Capture](../19-change-data-capture/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Indexes](../17-indexes/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Change Data Capture](../19-change-data-capture/concept.md)


