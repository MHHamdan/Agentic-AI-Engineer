---
title: Rate Limiting
slug: rate-limiting
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Long Polling vs WebSockets
unlocks:
  - Idempotency
related_topics:
  - Long Polling vs WebSockets
  - Idempotency
code_lab: ../../../labs/07-rate-limiting/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Rate Limiting.

## What You Will Build

A minimal Python example under labs/07-rate-limiting/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/07-rate-limiting/demo.py
- labs/07-rate-limiting/test_rate_limiting.py

## Run the Example

```bash
cd labs/07-rate-limiting
python demo.py
```

## Expected Output

The script should show how Rate Limiting changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for requests per window, burst size, rejected request rate, and remaining quota.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Long Polling vs WebSockets](../06-long-polling-vs-websockets/concept.md)
- [Idempotency](../08-idempotency/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [API Gateways](../02-api-gateways/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Idempotency](../08-idempotency/concept.md)


