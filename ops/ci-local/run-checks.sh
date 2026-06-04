#!/usr/bin/env bash
# Run the same checks as the CI workflows, locally. Two tiers:
#   --offline : the fast self-tests that need no services (fakeredis / moto). Always safe to run.
#   (default) : the offline tier, then the live integration + smoke tests against the compose
#               services (requires `docker compose up -d` first).
#
# This mirrors .github/workflows/backend-integration.yml and nightly-smoke.yml so a green run here
# predicts a green run in CI.
set -euo pipefail
cd "$(dirname "$0")/../.."   # repo root

echo "== offline tier (no services) =="
( cd labs/57-real-backends-integration && python backends.py --self-test )
( cd labs/57-real-backends-integration && python smoke_sqs.py --self-test )

if [ "${1:-}" = "--offline" ]; then
  echo "offline tier passed"; exit 0
fi

echo "== live tier (needs docker compose up) =="
export REDIS_URL="redis://localhost:6379"
export AWS_ENDPOINT_URL="http://localhost:4566"
export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1
( cd labs/57-real-backends-integration && pytest test_integration.py -v )
( cd labs/57-real-backends-integration && python smoke_sqs.py )
echo "live tier passed"
