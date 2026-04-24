#!/usr/bin/env bash
<<<<<<< HEAD
# Set RNA_URL=http://localhost:8000/mcp to use mock server
# Tests: query_flight_summary
set -euo pipefail
RNA_URL="${RNA_URL:-https://aiflightrecorder.onrender.com/mcp}"
python3 -c "
import json
req = {'jsonrpc': '2.0', 'id': '1', 'method': 'tools/call', 'params': {'name': 'query_flight_summary', 'arguments': {'flight_id': 'FLIGHT-DEMO-001', 'time_range': {}}}}
print(json.dumps(req))
" | curl -sS -X POST "$RNA_URL" -H "Content-Type: application/json" -d @- \
  | python -m json.tool
=======
# Example 04: Query the flight summary — chain length and all receipts in memory.
# Run: bash examples/curl/04-query-summary.sh
set -euo pipefail

BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"query_flight_summary","arguments":{}}}'
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
