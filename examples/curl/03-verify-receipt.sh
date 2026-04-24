#!/usr/bin/env bash
<<<<<<< HEAD
# Set RNA_URL=http://localhost:8000/mcp to use mock server
# Tests: submit_attestation then verify_receipt with returned receipt_hash
set -euo pipefail
RNA_URL="${RNA_URL:-https://aiflightrecorder.onrender.com/mcp}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESP="$(python3 -c "
import json, pathlib
p = pathlib.Path(r'$REPO_ROOT') / 'payloads' / 'identity_verified.json'
att = json.loads(p.read_text(encoding='utf-8'))
req = {'jsonrpc': '2.0', 'id': '1', 'method': 'tools/call', 'params': {'name': 'submit_attestation', 'arguments': att}}
print(json.dumps(req))
" | curl -sS -X POST "$RNA_URL" -H "Content-Type: application/json" -d @-)"
RH="$(python3 -c "
import json, sys
api = json.loads(sys.argv[1])
r = api.get('result') or {}
rh = r.get('receipt_hash')
if not rh and r.get('content'):
    t = r['content'][0].get('text','')
    rh = json.loads(t).get('receipt_hash')
print(rh or '')
" "$RESP")"
if [ -z "$RH" ]; then
  echo "Failed to parse receipt_hash" >&2
  echo "$RESP" >&2
  exit 1
fi
export RECEIPT_HASH="$RH"
python3 -c "
import json, os
rh = os.environ['RECEIPT_HASH']
req = {'jsonrpc': '2.0', 'id': '2', 'method': 'tools/call', 'params': {'name': 'verify_receipt', 'arguments': {'receipt_hash': rh}}}
print(json.dumps(req))
" | curl -sS -X POST "$RNA_URL" -H "Content-Type: application/json" -d @- \
  | python -m json.tool
=======
# Example 03: Verify a receipt by hash (mock server in-memory lookup).
# Run: bash examples/curl/03-verify-receipt.sh <sha256_hex>:<blake3_hex>
# If no hash is supplied, uses an intentionally unknown hash to demonstrate valid:false.
set -euo pipefail

BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"
HASH="${1:-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb}"

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"tools/call\",\"params\":{\"name\":\"verify_receipt\",\"arguments\":{\"receipt_hash\":\"$HASH\"}}}"
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
