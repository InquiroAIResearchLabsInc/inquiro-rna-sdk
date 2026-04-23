#!/usr/bin/env bash
# Example 05: Verify a chain segment by position range.
# Run: bash examples/curl/05-verify-chain.sh [start] [end]
set -euo pipefail

BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"
START="${1:-1}"
END="${2:-10}"

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"tools/call\",\"params\":{\"name\":\"verify_chain_segment\",\"arguments\":{\"start\":$START,\"end\":$END}}}"
