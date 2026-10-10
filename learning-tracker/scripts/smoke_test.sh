#!/usr/bin/env bash
# Checks the running stack end to end, through Nginx like a browser would.
# Usage: bash scripts/smoke_test.sh [base_url]     (default http://localhost)
set -euo pipefail
BASE_URL="${1:-http://localhost}"

echo "Waiting for $BASE_URL/api/health ..."
for i in $(seq 1 40); do
  if curl -fsS "$BASE_URL/api/health" >/dev/null 2>&1; then
    echo "API is up after ~$((i*2))s"; break
  fi
  [ "$i" -eq 40 ] && { echo "API did not become healthy in time" >&2; exit 1; }
  sleep 2
done

if [ "${CHECK_PAGE:-1}" = "1" ]; then
  echo "Checking the React page is served ..."
  curl -fsS "$BASE_URL/" | grep -q "Learning Tracker"
fi

echo "Creating an entry ..."
curl -fsS -X POST "$BASE_URL/api/entries" -H 'Content-Type: application/json' \
  -d '{"topic":"smoke-test","notes":"hello","hours":1.5}' | grep -q '"smoke-test"'

echo "Reading it back ..."
curl -fsS "$BASE_URL/api/entries" | grep -q '"smoke-test"'

echo "Checking stats ..."
curl -fsS "$BASE_URL/api/stats" | grep -q '"total_hours"'

echo "SMOKE TEST PASSED"
