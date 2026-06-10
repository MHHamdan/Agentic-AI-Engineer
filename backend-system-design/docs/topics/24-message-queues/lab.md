---
title: Message Queues
slug: message-queues
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Consistent Hashing
unlocks:
  - Stateful vs Stateless
related_topics:
  - Consistent Hashing
  - Stateful vs Stateless
code_lab: ../../../labs/24-message-queues/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Message Queues.

## What You Will Build

A minimal Python example under labs/24-message-queues/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/24-message-queues/demo.py
- labs/24-message-queues/test_message_queues.py

## Run the Example

```bash
cd labs/24-message-queues
python demo.py
```

## Expected Output

The script should show how Message Queues changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for queue depth, consumer lag, throughput, retry rate, and dead-letter count.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Consistent Hashing](../23-consistent-hashing/concept.md)
- [Stateful vs Stateless](../25-stateful-vs-stateless/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Consistent Hashing](../23-consistent-hashing/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Stateful vs Stateless](../25-stateful-vs-stateless/concept.md)


