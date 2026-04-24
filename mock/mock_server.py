"""
PROTOCOL TESTING ONLY — not suitable for cryptographic verification in production.
Local MCP HTTP mock: real SHA-256 + BLAKE3 over canonical attestation JSON.
Merkle position, Ed25519 signature, and tenant isolation are mocked per SDK spec.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import blake3  # noqa: E402

from canonical_payload import canonical_bytes  # noqa: E402

# Default loopback only. Set RNA_MOCK_BIND_ALL=1 to listen on 0.0.0.0 (LAN/shared dev).
HOST = "0.0.0.0" if os.environ.get("RNA_MOCK_BIND_ALL", "").strip().lower() in ("1", "true", "yes") else "127.0.0.1"
PORT = 8000


def dual_hex(payload: dict[str, Any]) -> tuple[str, str]:
    data = canonical_bytes(payload)
    sha = hashlib.sha256(data).hexdigest()
    b3 = blake3.blake3(data).hexdigest()
    return sha, b3


_TOOLS = [
    {
        "name": "submit_attestation",
        "description": "Submit an attestation payload; returns dual-hash receipt",
        "inputSchema": {
            "type": "object",
            "properties": {
                "payload": {"type": "object"},
            },
            "required": ["payload"],
        },
    },
    {
        "name": "verify_receipt",
        "description": "Look up a receipt by its dual hash (sha256hex:blake3hex); returns valid true/false",
        "inputSchema": {
            "type": "object",
            "properties": {
                "receipt_hash": {
                    "type": "string",
                    "description": "64-hex SHA-256 + colon + 64-hex BLAKE3",
                },
            },
            "required": ["receipt_hash"],
        },
    },
    {
        "name": "query_flight_summary",
        "description": "Return chain length and all in-memory receipts",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "verify_chain_segment",
        "description": "Verify receipts within a chain position range",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start": {"type": "integer", "description": "First chain_position (inclusive)"},
                "end": {"type": "integer", "description": "Last chain_position (inclusive)"},
            },
            "required": ["start", "end"],
        },
    },
    {
        "name": "get_flight_health",
        "description": "Return mock server health and chain statistics",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


class MCPHandler(BaseHTTPRequestHandler):
    _chain: int = 0
    _receipts: dict[str, dict[str, Any]] = {}

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"[mock] {self.address_string()} {fmt % args}\n")

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/health":
            self._send_json(200, {"status": "ok", "chain_length": MCPHandler._chain})
        else:
            self._send_json(404, {"error": "not_found", "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path != "/mcp":
            self._send_json(404, {"error": "not_found", "path": self.path})
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else b"{}"
        try:
            req = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as e:
            self._send_json(400, {"error": "invalid_json", "detail": str(e)})
            return
        if isinstance(req, dict) and req.get("jsonrpc") == "2.0":
            resp = self._handle_jsonrpc(req)
        elif isinstance(req, dict) and "event_type" in req:
            resp = self._build_receipt(req)
        else:
            self._send_json(400, {"error": "bad_request", "detail": "Expected JSON-RPC 2.0 or attestation object with event_type"})
            return
        self._send_json(200, resp)

    def _send_json(self, code: int, obj: Any) -> None:
        b = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _handle_jsonrpc(self, req: Any) -> dict[str, Any]:
        if not isinstance(req, dict):
            return _jsonrpc_error(None, -32600, "Invalid request")
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params") or {}

        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": _TOOLS}}

        if method == "tools/call":
            if not isinstance(params, dict):
                return _jsonrpc_error(req_id, -32602, "Invalid params")
            name = params.get("name")
            arguments = params.get("arguments") or {}
            if not isinstance(arguments, dict):
                return _jsonrpc_error(req_id, -32602, "Invalid arguments")

            if name == "submit_attestation":
                pl = arguments.get("payload")
                if not isinstance(pl, dict):
                    return _jsonrpc_error(req_id, -32602, "payload must be an object")
                receipt = self._build_receipt(pl)
                text = json.dumps(receipt, separators=(",", ":"), ensure_ascii=False)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"receipt": receipt, "content": [{"type": "text", "text": text}]}}

            if name == "verify_receipt":
                receipt_hash = arguments.get("receipt_hash", "")
                if receipt_hash in MCPHandler._receipts:
                    receipt = MCPHandler._receipts[receipt_hash]
                    result: dict[str, Any] = {"valid": True, "receipt": receipt}
                else:
                    result = {"valid": False}
                text = json.dumps(result, separators=(",", ":"), ensure_ascii=False)
                return {"jsonrpc": "2.0", "id": req_id, "result": {**result, "content": [{"type": "text", "text": text}]}}

            if name == "query_flight_summary":
                receipts = list(MCPHandler._receipts.values())
                result = {
                    "chain_length": MCPHandler._chain,
                    "receipt_count": len(receipts),
                    "receipts": receipts,
                }
                text = json.dumps(result, separators=(",", ":"), ensure_ascii=False)
                return {"jsonrpc": "2.0", "id": req_id, "result": {**result, "content": [{"type": "text", "text": text}]}}

            if name == "verify_chain_segment":
                start = int(arguments.get("start", 1))
                end = int(arguments.get("end", MCPHandler._chain))
                in_range = [r for r in MCPHandler._receipts.values() if start <= r.get("chain_position", 0) <= end]
                result = {"valid": True, "start": start, "end": end, "count": len(in_range)}
                text = json.dumps(result, separators=(",", ":"), ensure_ascii=False)
                return {"jsonrpc": "2.0", "id": req_id, "result": {**result, "content": [{"type": "text", "text": text}]}}

            if name == "get_flight_health":
                result = {"status": "ok", "chain_length": MCPHandler._chain, "note": "PROTOCOL TESTING ONLY"}
                text = json.dumps(result, separators=(",", ":"), ensure_ascii=False)
                return {"jsonrpc": "2.0", "id": req_id, "result": {**result, "content": [{"type": "text", "text": text}]}}

            return _jsonrpc_error(req_id, -32601, f"Unknown tool: {name!r}")

        if method in ("initialize", "initialized", "notifications/initialized"):
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        return _jsonrpc_error(req_id, -32601, f"Method not found: {method!r}")

    def _build_receipt(self, payload: dict[str, Any]) -> dict[str, Any]:
        MCPHandler._chain += 1
        sha, b3 = dual_hex(payload)
        ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        tenant = str(payload.get("tenant_id", "demo_public"))
        receipt: dict[str, Any] = {
            "schema_version": 1,
            "request_id": str(uuid4()),
            "payload": payload,
            "sha256": sha,
            "blake3": b3,
            "chain_position": MCPHandler._chain,
            "timestamp": ts,
            "tenant_id": tenant,
            "event_type": str(payload.get("event_type", "unknown")),
            "device_id": str(payload.get("device_id", "DEV-001")),
            "signature": "mock_ed25519_signature",
        }
        MCPHandler._receipts[f"{sha}:{b3}"] = receipt
        return receipt


def _jsonrpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), MCPHandler)
    print(f"Mock RNA MCP: http://{HOST}:{PORT}/mcp  (GET /health for warm checks)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
