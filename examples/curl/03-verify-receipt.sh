#!/usr/bin/env bash
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
