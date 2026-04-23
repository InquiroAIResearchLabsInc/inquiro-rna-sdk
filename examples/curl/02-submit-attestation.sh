#!/usr/bin/env bash
# Example 02: Submit an attestation payload and save the receipt.
# Run: bash examples/curl/02-submit-attestation.sh
# Optionally set RNA_BASE_URL to point at the live API.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"
OUT="${RNA_RECEIPT_OUT:-/tmp/receipt.json}"

PAYLOAD=$(cat "$ROOT/payloads/identity_verified.json")

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"tools/call\",\"params\":{\"name\":\"submit_attestation\",\"arguments\":{\"payload\":$PAYLOAD}}}" \
  -o "$OUT"

echo "Receipt saved to $OUT"
python3 "$ROOT/verifier/verify.py" "$OUT"
