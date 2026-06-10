---
title: Consistent Hashing
slug: consistent-hashing
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - CAP Theorem
unlocks:
  - Message Queues
related_topics:
  - CAP Theorem
  - Message Queues
code_lab: ../../../labs/23-consistent-hashing/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Consistent Hashing.

## What You Will Build

A minimal Python example under labs/23-consistent-hashing/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/23-consistent-hashing/demo.py
- labs/23-consistent-hashing/test_consistent_hashing.py

## Run the Example

```bash
cd labs/23-consistent-hashing
python demo.py
```

## Expected Output

The script should show how Consistent Hashing changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for key movement percentage, node balance, hot key rate, and replica count.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [CAP Theorem](../22-cap-theorem/concept.md)
- [Message Queues](../24-message-queues/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [CAP Theorem](../22-cap-theorem/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Message Queues](../24-message-queues/concept.md)


