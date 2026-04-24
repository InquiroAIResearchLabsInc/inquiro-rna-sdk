#!/usr/bin/env python3
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


if __name__ == "__main__":
    main()
