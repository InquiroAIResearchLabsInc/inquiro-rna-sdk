#!/usr/bin/env bash
# Example 03: Verify a receipt by hash (mock server in-memory lookup).
# Run: bash examples/curl/03-verify-receipt.sh <sha256_hex>:<blake3_hex>
# If no hash is supplied, uses an intentionally unknown hash to demonstrate valid:false.
set -euo pipefail

BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"
HASH="${1:-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb}"

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"tools/call\",\"params\":{\"name\":\"verify_receipt\",\"arguments\":{\"receipt_hash\":\"$HASH\"}}}"
