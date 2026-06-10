---
title: Concurrency vs Parallelism
slug: concurrency-vs-parallelism
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Stateful vs Stateless
unlocks:
  - Batch vs Stream Processing
related_topics:
  - Stateful vs Stateless
  - Batch vs Stream Processing
code_lab: ../../../labs/26-concurrency-vs-parallelism/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Concurrency vs Parallelism.

## What You Will Build

A minimal Python example under labs/26-concurrency-vs-parallelism/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/26-concurrency-vs-parallelism/demo.py
- labs/26-concurrency-vs-parallelism/test_concurrency_vs_parallelism.py

## Run the Example

```bash
cd labs/26-concurrency-vs-parallelism
python demo.py
```

## Expected Output

The script should show how Concurrency vs Parallelism changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for task latency, CPU utilization, contention, context switches, and throughput.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Stateful vs Stateless](../25-stateful-vs-stateless/concept.md)
- [Batch vs Stream Processing](../27-batch-vs-stream-processing/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Stateful vs Stateless](../25-stateful-vs-stateless/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Batch vs Stream Processing](../27-batch-vs-stream-processing/concept.md)


