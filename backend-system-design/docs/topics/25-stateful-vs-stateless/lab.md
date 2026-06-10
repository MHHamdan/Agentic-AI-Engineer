---
title: Stateful vs Stateless
slug: stateful-vs-stateless
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Message Queues
unlocks:
  - Concurrency vs Parallelism
related_topics:
  - Message Queues
  - Concurrency vs Parallelism
code_lab: ../../../labs/25-stateful-vs-stateless/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Stateful vs Stateless.

## What You Will Build

A minimal Python example under labs/25-stateful-vs-stateless/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/25-stateful-vs-stateless/demo.py
- labs/25-stateful-vs-stateless/test_stateful_vs_stateless.py

## Run the Example

```bash
cd labs/25-stateful-vs-stateless
python demo.py
```

## Expected Output

The script should show how Stateful vs Stateless changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for session count, state size, failover recovery, cache dependency, and instance replaceability.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Message Queues](../24-message-queues/concept.md)
- [Concurrency vs Parallelism](../26-concurrency-vs-parallelism/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Message Queues](../24-message-queues/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Concurrency vs Parallelism](../26-concurrency-vs-parallelism/concept.md)


