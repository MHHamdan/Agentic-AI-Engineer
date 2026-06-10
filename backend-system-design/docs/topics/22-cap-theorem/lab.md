---
title: CAP Theorem
slug: cap-theorem
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Single Point of Failure
unlocks:
  - Consistent Hashing
related_topics:
  - Single Point of Failure
  - Consistent Hashing
code_lab: ../../../labs/22-cap-theorem/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of CAP Theorem.

## What You Will Build

A minimal Python example under labs/22-cap-theorem/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/22-cap-theorem/demo.py
- labs/22-cap-theorem/test_cap_theorem.py

## Run the Example

```bash
cd labs/22-cap-theorem
python demo.py
```

## Expected Output

The script should show how CAP Theorem changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for stale read rate, write availability, quorum latency, and conflict rate.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Single Point of Failure](../21-single-point-of-failure/concept.md)
- [Consistent Hashing](../23-consistent-hashing/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Single Point of Failure](../21-single-point-of-failure/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Consistent Hashing](../23-consistent-hashing/concept.md)


