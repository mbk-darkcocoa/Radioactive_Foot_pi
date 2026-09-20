#!/usr/bin/env bash
set -euo pipefail

API_TOKEN="${APIFY_API_TOKEN:-}"
INPUT_FILE="${1:-$(dirname "$0")/apify-web-scraper-input.json}"

if [[ -z "${API_TOKEN}" ]]; then
  echo "Usage: APIFY_API_TOKEN=token $0 [input-file]" >&2
  exit 1
fi

if [[ ! -r "${INPUT_FILE}" ]]; then
  echo "Input file is missing or not readable: ${INPUT_FILE}" >&2
  exit 1
fi

RUN_URL="https://api.apify.com/v2/actors/apify~web-scraper/runs?token=${API_TOKEN}"

curl -X POST \
  "${RUN_URL}" \
  -H "Content-Type: application/json" \
  --fail-with-body \
  --data-binary "@${INPUT_FILE}"
