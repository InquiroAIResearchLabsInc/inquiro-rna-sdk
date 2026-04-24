#!/usr/bin/env bash
<<<<<<< HEAD
# Set RNA_URL=http://localhost:8000/mcp to use mock server
# Tests: verify_chain_segment (uses receipt_hash from a fresh submit)
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
    rh = json.loads(r['content'][0]['text']).get('receipt_hash')
print(rh or '')
" "$RESP")"
export RECEIPT_HASH="$RH"
python3 -c "
import json, os
h = os.environ['RECEIPT_HASH']
req = {'jsonrpc': '2.0', 'id': '2', 'method': 'tools/call', 'params': {'name': 'verify_chain_segment', 'arguments': {'start_hash': h, 'end_hash': h}}}
print(json.dumps(req))
" | curl -sS -X POST "$RNA_URL" -H "Content-Type: application/json" -d @- \
  | python -m json.tool
=======
# Example 05: Verify a chain segment by position range.
# Run: bash examples/curl/05-verify-chain.sh [start] [end]
set -euo pipefail

BASE="${RNA_BASE_URL:-http://localhost:8000/mcp}"
START="${1:-1}"
END="${2:-10}"

curl -s -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"tools/call\",\"params\":{\"name\":\"verify_chain_segment\",\"arguments\":{\"start\":$START,\"end\":$END}}}"
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
