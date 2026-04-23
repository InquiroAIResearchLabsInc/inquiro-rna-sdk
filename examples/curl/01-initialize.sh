#!/usr/bin/env bash
# Example 01: Initialize — confirm the mock server is up and list available tools.
# Run: bash examples/curl/01-initialize.sh
set -euo pipefail

BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
