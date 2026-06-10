---
title: Change Data Capture
slug: change-data-capture
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Sharding
unlocks:
  - Availability
related_topics:
  - Sharding
  - Availability
code_lab: ../../../labs/19-change-data-capture/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Change Data Capture.

## What You Will Build

A minimal Python example under labs/19-change-data-capture/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/19-change-data-capture/demo.py
- labs/19-change-data-capture/test_change_data_capture.py

## Run the Example

```bash
cd labs/19-change-data-capture
python demo.py
```

## Expected Output

The script should show how Change Data Capture changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for capture lag, event throughput, duplicate rate, and replay success.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Sharding](../18-sharding/concept.md)
- [Availability](../20-availability/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Sharding](../18-sharding/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Availability](../20-availability/concept.md)


