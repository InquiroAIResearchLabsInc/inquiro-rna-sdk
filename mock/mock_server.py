"""
<<<<<<< HEAD
Inquiro RNA Mock MCP Server

IMPORTANT: This mock server is for MCP PROTOCOL TESTING ONLY.
It is NOT suitable for cryptographic verification testing.

Hash values returned by this mock are randomly generated and have
no cryptographic relationship to the submitted event data.
Session verify_receipt only recognizes hashes issued in this process;
it does not recompute hashes from payload data.

Use the live API at https://aiflightrecorder.onrender.com for:
- Real SHA256 + BLAKE3 dual-hash computation
- Actual Merkle chain position assignment
- Ed25519 signature generation
- Cryptographic receipt verification

This mock exists to let you test MCP JSON-RPC protocol flow,
client connectivity, and your integration code structure
without consuming live API calls.
"""

=======
PROTOCOL TESTING ONLY — not suitable for cryptographic verification in production.
Local MCP HTTP mock: real SHA-256 + BLAKE3 over canonical attestation JSON.
Merkle position, Ed25519 signature, and tenant isolation are mocked per SDK spec.
"""
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
from __future__ import annotations

import hashlib
import json
<<<<<<< HEAD
import os
import sys
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
=======
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
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2

HOST = "0.0.0.0"
PORT = 8000

<<<<<<< HEAD
_session_receipts: dict[str, dict[str, Any]] = {}
_chain_position = 0


def _fake_receipt_hash() -> str:
    data = str(uuid.uuid4()).encode()
    sha = hashlib.sha256(data).hexdigest()
    b3 = hashlib.sha256(b"mock:" + data).hexdigest()
    return f"{sha}:{b3}"


def _next_chain_position() -> int:
    global _chain_position
    _chain_position += 1
    return _chain_position


MOCK_TOOLS: list[dict[str, Any]] = [
    {
        "name": "submit_attestation",
        "description": "Submit an identity verification attestation event",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_type": {"type": "string"},
                "payload": {"type": "object"},
                "device_id": {"type": "string"},
                "timestamp": {"type": "string"},
                "signature": {"type": "string"},
            },
            "required": ["event_type", "payload", "device_id", "timestamp", "signature"],
=======

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
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
        },
    },
    {
        "name": "verify_receipt",
<<<<<<< HEAD
        "description": "Verify a receipt by its dual hash",
        "inputSchema": {
            "type": "object",
            "properties": {"receipt_hash": {"type": "string"}},
=======
        "description": "Look up a receipt by its dual hash (sha256hex:blake3hex); returns valid true/false",
        "inputSchema": {
            "type": "object",
            "properties": {
                "receipt_hash": {
                    "type": "string",
                    "description": "64-hex SHA-256 + colon + 64-hex BLAKE3",
                },
            },
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
            "required": ["receipt_hash"],
        },
    },
    {
        "name": "query_flight_summary",
<<<<<<< HEAD
        "description": "Get a summary of a flight's decision and attestation activity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "flight_id": {"type": "string"},
                "time_range": {"type": "object"},
            },
            "required": ["flight_id"],
=======
        "description": "Return chain length and all in-memory receipts",
        "inputSchema": {
            "type": "object",
            "properties": {},
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
        },
    },
    {
        "name": "verify_chain_segment",
<<<<<<< HEAD
        "description": "Verify integrity of a chain segment between two receipt hashes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_hash": {"type": "string"},
                "end_hash": {"type": "string"},
            },
            "required": ["start_hash", "end_hash"],
=======
        "description": "Verify receipts within a chain position range",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start": {"type": "integer", "description": "First chain_position (inclusive)"},
                "end": {"type": "integer", "description": "Last chain_position (inclusive)"},
            },
            "required": ["start", "end"],
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
        },
    },
    {
        "name": "get_flight_health",
<<<<<<< HEAD
        "description": "Get the current health status of a flight",
        "inputSchema": {
            "type": "object",
            "properties": {"flight_id": {"type": "string"}},
            "required": ["flight_id"],
=======
        "description": "Return mock server health and chain statistics",
        "inputSchema": {
            "type": "object",
            "properties": {},
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
        },
    },
]


<<<<<<< HEAD
def _tool_submit_attestation(args: dict[str, Any]) -> dict[str, Any]:
    receipt_hash = _fake_receipt_hash()
    out = {
        "receipt_hash": receipt_hash,
        "chain_position": _next_chain_position(),
        "accepted": True,
    }
    _session_receipts[receipt_hash] = dict(out)
    return out


def _tool_verify_receipt(args: dict[str, Any]) -> dict[str, Any]:
    receipt_hash = str(args.get("receipt_hash", ""))
    if receipt_hash in _session_receipts:
        return {
            "valid": True,
            "chain_intact": True,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "receipt_type": "attestation",
        }
    return {
        "valid": False,
        "chain_intact": False,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "receipt_type": "attestation",
    }


def _tool_query_flight_summary(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_count": 12,
        "attestation_count": 4,
        "override_count": 0,
        "chain_status": "intact",
        "topology": "hybrid",
    }


def _tool_verify_chain_segment(args: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "intact": True,
        "receipt_count": 16,
        "time_span": f"{now}/{now}",
        "gap_count": 0,
    }


def _tool_get_flight_health(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "topology": "hybrid",
        "health_tier": "GREEN",
        "decision_quality": 0.95,
    }


MOCK_HANDLERS: dict[str, Any] = {
    "submit_attestation": _tool_submit_attestation,
    "verify_receipt": _tool_verify_receipt,
    "query_flight_summary": _tool_query_flight_summary,
    "verify_chain_segment": _tool_verify_chain_segment,
    "get_flight_health": _tool_get_flight_health,
}


def _jsonrpc_result_with_lift(req_id: Any, tool_result: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(tool_result, separators=(",", ":"), ensure_ascii=False)
    result: dict[str, Any] = {
        "content": [{"type": "text", "text": text}],
        **tool_result,
    }
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _handle_jsonrpc(req: dict[str, Any]) -> dict[str, Any]:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "inquiro-rna-mock", "version": "public_mock_v1"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MOCK_TOOLS}}

    if method == "tools/call":
        if not isinstance(params, dict):
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Invalid params"}}
        name = params.get("name", "")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        handler = MOCK_HANDLERS.get(name)
        if handler is None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": "Tool not found"},
            }
        tool_result = handler(arguments)
        return _jsonrpc_result_with_lift(req_id, tool_result)

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"status": "ok"}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}


def _cors_headers(handler: BaseHTTPRequestHandler) -> None:
    origin = os.environ.get("ALLOWED_ORIGIN", "http://localhost:3000")
    handler.send_header("Access-Control-Allow-Origin", origin)
    handler.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, X-Partner-Key")
    handler.send_header("Access-Control-Max-Age", "86400")


class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"[mock] {self.address_string()} {fmt % args}\n")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        _cors_headers(self)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/health":
            body = json.dumps({"status": "ok"}, separators=(",", ":")).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            _cors_headers(self)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            b = b'{"error":"not_found"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            _cors_headers(self)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
=======
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
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path != "/mcp":
<<<<<<< HEAD
            b = b'{"error":"not_found"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            _cors_headers(self)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
=======
            self._send_json(404, {"error": "not_found", "path": self.path})
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else b"{}"
        try:
            req = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as e:
<<<<<<< HEAD
            err = json.dumps({"error": "invalid_json", "detail": str(e)}).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            _cors_headers(self)
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)
            return
        if not isinstance(req, dict) or req.get("jsonrpc") != "2.0":
            err = b'{"error":"bad_request","detail":"Expected JSON-RPC 2.0"}'
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            _cors_headers(self)
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)
            return
        resp = _handle_jsonrpc(req)
        out = json.dumps(resp, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        _cors_headers(self)
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)


def main() -> None:
    httpd = HTTPServer((HOST, PORT), MCPHandler)
    print(f"Inquiro RNA mock MCP: http://{HOST}:{PORT}/mcp (GET /health)", flush=True)
=======
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
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
