---
title: ACID Transactions
slug: acid-transactions
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - SQL vs NoSQL
unlocks:
  - Indexes
related_topics:
  - SQL vs NoSQL
  - Indexes
code_lab: ../../../labs/16-acid-transactions/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of ACID Transactions.

## What You Will Build

A minimal Python example under labs/16-acid-transactions/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/16-acid-transactions/demo.py
- labs/16-acid-transactions/test_acid_transactions.py

## Run the Example

```bash
cd labs/16-acid-transactions
python demo.py
```

## Expected Output

The script should show how ACID Transactions changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for commit latency, rollback count, lock wait time, deadlocks, and isolation anomalies.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [SQL vs NoSQL](../15-sql-vs-nosql/concept.md)
- [Indexes](../17-indexes/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [SQL vs NoSQL](../15-sql-vs-nosql/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Indexes](../17-indexes/concept.md)


