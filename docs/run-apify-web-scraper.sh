#!/usr/bin/env bash
set -euo pipefail

API_TOKEN="${APIFY_API_TOKEN:-${1:-}}"
INPUT_FILE="${2:-$(dirname "$0")/apify-web-scraper-input.json}"

if [[ -z "${API_TOKEN}" ]]; then
  echo "Usage: APIFY_API_TOKEN=token $0 [token] [input-file]" >&2
  exit 1
fi

if [[ ! -r "${INPUT_FILE}" ]]; then
  echo "Input file is missing or not readable: ${INPUT_FILE}" >&2
  exit 1
fi

AUTH_SCHEME="Bearer"
AUTH_HEADER="Authorization: ${AUTH_SCHEME} ${API_TOKEN}"

curl -X POST \
  "https://api.apify.com/v2/actors/apify~web-scraper/runs" \
  -H "${AUTH_HEADER}" \
  -H "Content-Type: application/json" \
  --data-binary "@${INPUT_FILE}"
