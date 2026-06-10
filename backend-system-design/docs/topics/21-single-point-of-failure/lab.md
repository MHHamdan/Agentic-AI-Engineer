---
title: Single Point of Failure
slug: single-point-of-failure
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Availability
unlocks:
  - CAP Theorem
related_topics:
  - Availability
  - CAP Theorem
code_lab: ../../../labs/21-single-point-of-failure/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Single Point of Failure.

## What You Will Build

A minimal Python example under labs/21-single-point-of-failure/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/21-single-point-of-failure/demo.py
- labs/21-single-point-of-failure/test_single_point_of_failure.py

## Run the Example

```bash
cd labs/21-single-point-of-failure
python demo.py
```

## Expected Output

The script should show how Single Point of Failure changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for dependency criticality, failover time, redundancy count, and blast radius.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Availability](../20-availability/concept.md)
- [CAP Theorem](../22-cap-theorem/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Availability](../20-availability/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [CAP Theorem](../22-cap-theorem/concept.md)


