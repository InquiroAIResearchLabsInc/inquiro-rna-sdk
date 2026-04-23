#!/usr/bin/env bash
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
