#!/usr/bin/env python3
"""
Example: submit an attestation and verify the returned receipt.
Pass --tamper-test to run tamper-detection self-check (exits 0 on WORKING).
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import blake3  # noqa: E402

from canonical_payload import canonical_bytes  # noqa: E402
from verifier.verify import verify_receipt_data  # noqa: E402

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


def run_tamper_test() -> int:
    payload = {"device_id": "SMOKE-001", "event_type": "test", "tenant_id": "demo_public"}
    data = canonical_bytes(payload)
    sha = hashlib.sha256(data).hexdigest()
    b3 = blake3.blake3(data).hexdigest()

    valid_receipt = {"payload": payload, "sha256": sha, "blake3": b3}
    ok, msg = verify_receipt_data(valid_receipt)
    if not ok:
        print(f"FAIL: valid receipt rejected: {msg}", file=sys.stderr)
        return 1

    tampered = {
        "payload": {**payload, "device_id": "TAMPERED"},
        "sha256": sha,
        "blake3": b3,
    }
    ok, _ = verify_receipt_data(tampered)
    if ok:
        print("FAIL: tampered receipt was accepted — tamper detection broken", file=sys.stderr)
        return 1

    print("Tamper detection: WORKING")
    return 0


def main() -> int:
    if "--tamper-test" in sys.argv:
        return run_tamper_test()

    payload = {
        "event_type": "identity_verified",
        "device_id": "DEV-001",
        "tenant_id": "demo_public",
        "metadata": {"source": "sdk-example", "version": 1},
    }
    try:
        resp = submit(payload)
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    result = resp.get("result", resp)
    receipt = result.get("receipt", result)
    ok, msg = verify_receipt_data(receipt)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
