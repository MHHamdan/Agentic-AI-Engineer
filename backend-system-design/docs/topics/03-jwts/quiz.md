---
title: JWTs Quiz
slug: jwts-quiz
level: intermediate
estimated_time: 10 minutes
prerequisites:
  - JWTs
unlocks:
  - Secure token management
related_topics:
  - JWTs
code_lab: ../../../labs/03-jwts/jwt_demo.py
official_sources:
  - JWT7519
academic_sources: []
last_verified: 2026-06-09
---

# Quiz

## Multiple Choice

1. Which JWT claim indicates when the token expires?
   - A) `iss`
   - B) `exp`
   - C) `sub`
   - D) `aud`

2. What is a common security risk with JWTs?
   - A) Token size too small
   - B) Using weak signing keys
   - C) Using HTTPS
   - D) Storing claims in JSON

## Short Answer

1. Why is token expiration important?
2. What are the benefits of stateless JWT validation?

## Code Review Questions

1. How would you validate a token signature in `jwt_demo.py`?
2. What should happen if the token has expired?

## System Design Questions

1. Describe how JWTs enable distributed services to authenticate requests.
2. Explain when you would use a refresh token.

## Answers

<details>
<summary>Show answers</summary>

1. B
2. B

Short answer examples:
- Expiration limits the window for compromised tokens.
- Stateless validation avoids a central session store.

Code review examples:
- Verify the JWT signature using the configured secret and algorithm.
- Return 401 for expired tokens.

</details>

## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Long Polling vs WebSockets](../06-long-polling-vs-websockets/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [API Gateways](../02-api-gateways/concept.md)



