#!/usr/bin/env bash
# Example 04: Query the flight summary — chain length and all receipts in memory.
# Run: bash examples/curl/04-query-summary.sh
set -euo pipefail

BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"query_flight_summary","arguments":{}}}'
