#!/usr/bin/env bash
<<<<<<< HEAD
# Set RNA_URL=http://localhost:8000/mcp to use mock server
# Tests: JSON-RPC tools/list
set -euo pipefail
RNA_URL="${RNA_URL:-https://aiflightrecorder.onrender.com/mcp}"
curl -sS -X POST "$RNA_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' \
  | python -m json.tool
=======
# Example 01: Initialize — confirm the mock server is up and list available tools.
# Run: bash examples/curl/01-initialize.sh
set -euo pipefail

BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
