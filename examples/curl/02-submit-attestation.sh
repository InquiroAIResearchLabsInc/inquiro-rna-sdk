#!/usr/bin/env bash
<<<<<<< HEAD
# Set RNA_URL=http://localhost:8000/mcp to use mock server
# Tests: submit_attestation with payloads/identity_verified.json
set -euo pipefail
RNA_URL="${RNA_URL:-https://aiflightrecorder.onrender.com/mcp}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
python3 -c "
import json, pathlib
p = pathlib.Path(r'$REPO_ROOT') / 'payloads' / 'identity_verified.json'
att = json.loads(p.read_text(encoding='utf-8'))
req = {'jsonrpc': '2.0', 'id': '1', 'method': 'tools/call', 'params': {'name': 'submit_attestation', 'arguments': att}}
print(json.dumps(req))
" | curl -sS -X POST "$RNA_URL" -H "Content-Type: application/json" -d @- \
  | python -m json.tool
=======
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
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
