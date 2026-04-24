#!/usr/bin/env python3
<<<<<<< HEAD
"""Inquiro RNA MCP client: all 5 tools via JSON-RPC (requests)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests

DEFAULT_URL = "https://aiflightrecorder.onrender.com/mcp"


def rpc(url: str, req_id: str, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        body["params"] = params
    r = requests.post(url, json=body, timeout=60)
    if r.status_code != 200:
        print(f"HTTP {r.status_code}: {r.text[:500]}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def tools_list(url: str) -> None:
    out = rpc(url, "1", "tools/list", {})
    print(json.dumps(out, indent=2))


def tools_call(url: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    out = rpc(url, "2", "tools/call", {"name": name, "arguments": arguments})
    if "error" in out:
        print(json.dumps(out, indent=2))
        sys.exit(1)
    return out


def load_attestation(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    if not isinstance(doc, dict):
        raise ValueError("payload file must be a JSON object")
    return doc


def main() -> None:
    p = argparse.ArgumentParser(description="Inquiro RNA MCP example client")
    p.add_argument(
        "--mock",
        action="store_true",
        help="Use http://localhost:8000/mcp unless RNA_URL is set",
    )
    p.add_argument("--url", default=None, help="MCP endpoint (default: RNA_URL or live)")
    args_ns = p.parse_args()
    default = os.environ.get("RNA_URL", DEFAULT_URL)
    if args_ns.mock and args_ns.url is None:
        url = "http://localhost:8000/mcp"
    else:
        url = args_ns.url or default

    print("=== tools/list ===")
    tools_list(url)

    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    payload_path = os.path.join(root, "payloads", "identity_verified.json")
    att = load_attestation(payload_path)

    print("\n=== submit_attestation ===")
    sub = tools_call(url, "submit_attestation", att)
    print(json.dumps(sub, indent=2))

    result = sub.get("result") or {}
    rh = result.get("receipt_hash")
    if not rh and result.get("content"):
        try:
            inner = json.loads(result["content"][0]["text"])
            rh = inner.get("receipt_hash")
        except (KeyError, IndexError, json.JSONDecodeError):
            rh = None
    if not isinstance(rh, str):
        print("Could not parse receipt_hash", file=sys.stderr)
        sys.exit(1)

    print("\n=== verify_receipt ===")
    vr = tools_call(url, "verify_receipt", {"receipt_hash": rh})
    print(json.dumps(vr, indent=2))

    print("\n=== query_flight_summary ===")
    q = tools_call(
        url,
        "query_flight_summary",
        {"flight_id": "FLIGHT-DEMO-001", "time_range": {}},
    )
    print(json.dumps(q, indent=2))

    print("\n=== get_flight_health ===")
    h = tools_call(url, "get_flight_health", {"flight_id": "FLIGHT-DEMO-001"})
    print(json.dumps(h, indent=2))

    print("\n=== verify_chain_segment ===")
    c = tools_call(
        url,
        "verify_chain_segment",
        {"start_hash": rh, "end_hash": rh},
    )
    print(json.dumps(c, indent=2))
=======
"""Example: submit an attestation to the RNA mock server and print the receipt."""
from __future__ import annotations

import json
import sys
import urllib.request

BASE_URL = "http://localhost:8000/mcp"


def submit(payload: dict, url: str = BASE_URL) -> dict:
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {"name": "submit_attestation", "arguments": {"payload": payload}},
    }).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main() -> None:
    payload = {
        "event_type": "identity_verified",
        "device_id": "DEV-001",
        "tenant_id": "demo_public",
        "metadata": {"source": "sdk-example", "version": 1},
    }
    print(f"Submitting: {json.dumps(payload)}")
    try:
        resp = submit(payload)
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    result = resp.get("result", resp)
    receipt = result.get("receipt", result)
    sha = receipt.get("sha256", "?")
    b3 = receipt.get("blake3", "?")
    print(f"receipt_hash: {sha}:{b3}")
    print(json.dumps(receipt, indent=2))
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2


if __name__ == "__main__":
    main()
