"""
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

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

HOST = "0.0.0.0"
PORT = 8000

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
        },
    },
    {
        "name": "verify_receipt",
        "description": "Verify a receipt by its dual hash",
        "inputSchema": {
            "type": "object",
            "properties": {"receipt_hash": {"type": "string"}},
            "required": ["receipt_hash"],
        },
    },
    {
        "name": "query_flight_summary",
        "description": "Get a summary of a flight's decision and attestation activity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "flight_id": {"type": "string"},
                "time_range": {"type": "object"},
            },
            "required": ["flight_id"],
        },
    },
    {
        "name": "verify_chain_segment",
        "description": "Verify integrity of a chain segment between two receipt hashes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_hash": {"type": "string"},
                "end_hash": {"type": "string"},
            },
            "required": ["start_hash", "end_hash"],
        },
    },
    {
        "name": "get_flight_health",
        "description": "Get the current health status of a flight",
        "inputSchema": {
            "type": "object",
            "properties": {"flight_id": {"type": "string"}},
            "required": ["flight_id"],
        },
    },
]


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

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path != "/mcp":
            b = b'{"error":"not_found"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            _cors_headers(self)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else b"{}"
        try:
            req = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as e:
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
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
