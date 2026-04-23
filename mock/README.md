# Mock MCP Server

A local mock of the Inquiro RNA MCP server for protocol testing.

## IMPORTANT: What this mock does and does NOT do

### What it does

- Implements the full MCP JSON-RPC protocol (tools/list, tools/call)
- Exposes all 5 RNA tools: submit_attestation, verify_receipt,
  query_flight_summary, get_flight_health, verify_chain_segment
- Returns correctly structured JSON responses matching the live API schema
- Tracks submitted receipts within the current session for verify_receipt (by receipt_hash)

### What it does NOT do

- Compute real SHA256 or BLAKE3 hashes from your payload (hashes are randomly generated)
- Generate real Ed25519 signatures
- Maintain a real Merkle chain (chain_position is a sequential counter only)
- Persist receipts across restarts
- Enforce real tenant isolation

Use this mock to test your MCP client code and JSON-RPC integration.
Use the live API for cryptographic verification.

## Setup

With uv (recommended):

```bash
uv venv && uv pip install -r requirements.txt
uv run python mock_server.py
```

With pip:

```bash
pip install -r requirements.txt
python mock_server.py
```

Server starts at http://localhost:8000/mcp

## Quick test

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```
