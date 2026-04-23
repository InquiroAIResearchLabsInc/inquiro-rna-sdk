#!/usr/bin/env bash
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
