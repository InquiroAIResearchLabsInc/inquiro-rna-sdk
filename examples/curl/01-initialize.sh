#!/usr/bin/env bash
# Set RNA_URL=http://localhost:8000/mcp to use mock server
# Tests: JSON-RPC tools/list
set -euo pipefail
RNA_URL="${RNA_URL:-https://aiflightrecorder.onrender.com/mcp}"
curl -sS -X POST "$RNA_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' \
  | python -m json.tool
