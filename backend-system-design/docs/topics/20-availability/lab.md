---
title: Availability
slug: availability
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Change Data Capture
unlocks:
  - Single Point of Failure
related_topics:
  - Change Data Capture
  - Single Point of Failure
code_lab: ../../../labs/20-availability/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Availability.

## What You Will Build

A minimal Python example under labs/20-availability/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/20-availability/demo.py
- labs/20-availability/test_availability.py

## Run the Example

```bash
cd labs/20-availability
python demo.py
```

## Expected Output

The script should show how Availability changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for uptime percentage, error budget, mean time to recovery, and successful request rate.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Change Data Capture](../19-change-data-capture/concept.md)
- [Single Point of Failure](../21-single-point-of-failure/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Change Data Capture](../19-change-data-capture/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Single Point of Failure](../21-single-point-of-failure/concept.md)


