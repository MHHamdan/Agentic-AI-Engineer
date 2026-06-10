---
title: CDN
slug: cdn
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Cache Eviction
unlocks:
  - SQL vs NoSQL
related_topics:
  - Cache Eviction
  - SQL vs NoSQL
code_lab: ../../../labs/14-cdn/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of CDN.

## What You Will Build

A minimal Python example under labs/14-cdn/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/14-cdn/demo.py
- labs/14-cdn/test_cdn.py

## Run the Example

```bash
cd labs/14-cdn
python demo.py
```

## Expected Output

The script should show how CDN changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for edge hit rate, origin offload, time to first byte, and geographic latency.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Cache Eviction](../13-cache-eviction/concept.md)
- [SQL vs NoSQL](../15-sql-vs-nosql/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Cache Eviction](../13-cache-eviction/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [SQL vs NoSQL](../15-sql-vs-nosql/concept.md)


