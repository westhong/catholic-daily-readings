#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKER_DIR="$(cd "$SCRIPT_DIR/../worker" && pwd)"
ENV_FILE="/home/jarvis/.hermes/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

# Wrangler expects the modern names. Hermes env may use CF_* aliases.
export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-${CF_API_TOKEN:-}}"
export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-${CF_ACCOUNT_ID:-}}"

if [[ -z "${CLOUDFLARE_API_TOKEN}" || -z "${CLOUDFLARE_ACCOUNT_ID}" ]]; then
  echo "Missing Cloudflare credentials: set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID" >&2
  exit 1
fi

cd "$WORKER_DIR"
npm run deploy
