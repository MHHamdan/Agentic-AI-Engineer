# Local CI runner

Reproduce the GitHub Actions integration jobs ([`backend-integration.yml`](../../.github/workflows/backend-integration.yml), [`nightly-smoke.yml`](../../.github/workflows/nightly-smoke.yml)) on your machine, so you can debug a CI failure without pushing.

## Two tiers

```bash
./run-checks.sh --offline        # fakeredis + moto self-tests; no services needed
# or, for the full live run:
docker compose up -d             # Redis + LocalStack (same images as CI)
./run-checks.sh                  # offline tier, then live integration + smoke
docker compose down
```

The script sets the same `REDIS_URL` / `AWS_ENDPOINT_URL` the workflows set, and runs the same commands (`backends.py --self-test`, `smoke_sqs.py --self-test`, `pytest test_integration.py`, `smoke_sqs.py`). A green local run predicts a green CI run because the code under test and the service images are identical; the only difference is where the containers are started.

## Why this exists

Service-container CI is hard to debug from the Actions log alone. Running the exact same tiers locally - fast offline first, then live - turns a red CI into something you can step through, and lets you confirm a fix before it reaches the pipeline.
