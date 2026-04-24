<<<<<<< HEAD
#!/usr/bin/env python3
"""
Inquiro RNA Receipt Verifier

Usage:
  python verify.py <receipt.json>        # Verify merged attestation + receipt_hash (or legacy receipt)
  python verify.py --tamper-test         # Run tamper detection test against live API

Exit codes:
  0 — receipt verified
  1 — verification failed or error
"""

from __future__ import annotations

import argparse
=======
"""
Verify RNA receipt: recompute SHA-256 and BLAKE3 of canonical attestation payload.
Usage: python verifier/verify.py <receipt.json|api-response.json>
Exit 0 on success, 1 on failure.
"""
from __future__ import annotations

>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

<<<<<<< HEAD
try:
    from blake3 import blake3 as blake3_hash

    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False


def canonical_attestation_bytes(att: dict[str, Any]) -> bytes:
    """Canonical serialization of the signed attestation body (5 fields)."""
    body = {
        "device_id": att["device_id"],
        "event_type": att["event_type"],
        "payload": att["payload"],
        "signature": att["signature"],
        "timestamp": att["timestamp"],
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def split_receipt_hash(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise ValueError("receipt_hash must be sha256_hex:blake3_hex")
    sha, b3 = value.split(":", 1)
    if len(sha) != 64 or len(b3) != 64:
        raise ValueError("receipt_hash components must be 64 hex chars each")
    return sha, b3


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_blake3(data: bytes) -> str:
    if not HAS_BLAKE3:
        raise RuntimeError(
            "blake3 not installed. Install with: pip install blake3\n"
            "SHA256 verification passed but BLAKE3 could not be verified."
        )
    return blake3_hash(data).hexdigest()


def _parse_content_text(result: dict[str, Any]) -> dict[str, Any] | None:
    content = result.get("content")
    if not isinstance(content, list) or not content:
        return None
    first = content[0]
    if not isinstance(first, dict) or first.get("type") != "text":
        return None
    text = first.get("text")
    if not isinstance(text, str):
        return None
    try:
        inner = json.loads(text)
    except json.JSONDecodeError:
        return None
    return inner if isinstance(inner, dict) else None


def _lift_tool_result(doc: dict[str, Any]) -> dict[str, Any]:
    """Normalize JSON-RPC result to tool fields (HTTP may lift fields onto result)."""
    result = doc.get("result")
    if not isinstance(result, dict):
        return doc
    lifted = dict(result)
    inner = _parse_content_text(result)
    if inner:
        for k, v in inner.items():
            lifted.setdefault(k, v)
    return lifted


def extract_verification_inputs(doc: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    Returns (attestation_dict, receipt_hash).
    Attestation must include event_type, device_id, payload, timestamp, signature.
    """
    lifted = _lift_tool_result(doc)
    receipt_hash = lifted.get("receipt_hash")
    if isinstance(receipt_hash, str) and receipt_hash and "event_type" in lifted:
        att = {
            "event_type": lifted["event_type"],
            "device_id": lifted["device_id"],
            "payload": lifted["payload"],
            "timestamp": lifted["timestamp"],
            "signature": lifted["signature"],
        }
        if not isinstance(att["payload"], dict):
            raise ValueError("payload must be an object")
        return att, receipt_hash

    if isinstance(doc.get("receipt_hash"), str) and "event_type" in doc:
        att = {
            "event_type": doc["event_type"],
            "device_id": doc["device_id"],
            "payload": doc["payload"],
            "timestamp": doc["timestamp"],
            "signature": doc["signature"],
        }
        if not isinstance(att["payload"], dict):
            raise ValueError("payload must be an object")
        return att, doc["receipt_hash"]

    raise ValueError(
        "Could not find attestation + receipt_hash. "
        "Merge API result with the source payloads/*.json attestation (see docs/QUICKSTART.md)."
    )


def verify_merged(att: dict[str, Any], receipt_hash: str) -> bool:
    sha256_in, blake3_in = split_receipt_hash(receipt_hash)
    canonical = canonical_attestation_bytes(att)
    computed_sha256 = compute_sha256(canonical)

    sha256_ok = computed_sha256 == sha256_in
    print(f"SHA256  receipt : {sha256_in}")
    print(f"SHA256  computed: {computed_sha256}")
    print(f"SHA256  match   : {'YES' if sha256_ok else 'NO'}")

    if HAS_BLAKE3:
        computed_blake3 = compute_blake3(canonical)
        blake3_ok = computed_blake3 == blake3_in
        print(f"BLAKE3  receipt : {blake3_in}")
        print(f"BLAKE3  computed: {computed_blake3}")
        print(f"BLAKE3  match   : {'YES' if blake3_ok else 'NO'}")
    else:
        blake3_ok = None
        print("BLAKE3          : SKIPPED (pip install blake3 to enable)")

    if sha256_ok and (blake3_ok is True or blake3_ok is None):
        print("\nVERIFIED")
        return True
    print("\nVERIFICATION FAILED")
    if not sha256_ok:
        print("  SHA256 mismatch — attestation body may have been modified")
    if blake3_ok is False:
        print("  BLAKE3 mismatch — attestation body may have been modified")
    return False


def verify_receipt(receipt_path: str) -> bool:
    with open(receipt_path, encoding="utf-8") as f:
        doc = json.load(f)
    if not isinstance(doc, dict):
        print("FAILED: top-level JSON must be an object")
        return False
    try:
        att, rh = extract_verification_inputs(doc)
    except ValueError as e:
        print(f"FAILED: {e}")
        return False
    return verify_merged(att, rh)


def tamper_test() -> None:
    import os
    import tempfile

    import requests

    print("=== Tamper Detection Test ===")
    print("Submitting test attestation to live API...")
    base = "https://aiflightrecorder.onrender.com/mcp"
    root = Path(__file__).resolve().parents[1]
    attestation = json.loads((root / "payloads" / "identity_verified.json").read_text(encoding="utf-8"))
    attestation = dict(attestation)
    attestation["device_id"] = "TAMPER-TEST-001"
    attestation["payload"] = {"test": "tamper_detection"}
    r = requests.post(
        base,
        json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {"name": "submit_attestation", "arguments": attestation},
        },
        timeout=60,
    )
    r.raise_for_status()
    api = r.json()
    result = api.get("result") or {}
    rh = result.get("receipt_hash")
    if not isinstance(rh, str):
        inner = _parse_content_text(result) if isinstance(result, dict) else None
        if isinstance(inner, dict):
            rh = inner.get("receipt_hash")
    if not isinstance(rh, str):
        print("FAILED: could not read receipt_hash from live response")
        raise SystemExit(1)
    merged = {**attestation, "receipt_hash": rh, "chain_position": result.get("chain_position"), "accepted": result.get("accepted")}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(merged, f)
        path = f.name

    print("Verifying original merged receipt...")
    if not verify_receipt(path):
        os.unlink(path)
        raise RuntimeError("Original receipt should verify")

    merged["payload"] = {"test": "TAMPERED"}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f)

    print("Verifying tampered receipt (should FAIL)...")
    if verify_receipt(path):
        os.unlink(path)
        raise RuntimeError("Tampered receipt should NOT verify")
    print("\nTamper detection: WORKING")
    os.unlink(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", nargs="?", help="Path to merged receipt JSON")
    parser.add_argument("--tamper-test", action="store_true")
    args = parser.parse_args()

    if args.tamper_test:
        tamper_test()
        sys.exit(0)

    if not args.receipt:
        print("Usage: python verify.py <receipt.json>")
        sys.exit(1)

    ok = verify_receipt(args.receipt)
    sys.exit(0 if ok else 1)
=======
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import blake3  # noqa: E402

from canonical_payload import canonical_bytes  # noqa: E402


def _load_doc(raw: str) -> dict[str, Any]:
    doc = json.loads(raw)
    if not isinstance(doc, dict):
        raise ValueError("Top-level JSON must be an object")
    return doc


def _extract_receipt(doc: dict[str, Any]) -> dict[str, Any]:
    if "receipt" in doc and isinstance(doc["receipt"], dict):
        return doc["receipt"]
    r = doc.get("result")
    if isinstance(r, dict) and "receipt" in r and isinstance(r["receipt"], dict):
        return r["receipt"]
    if "sha256" in doc and "blake3" in doc and "payload" in doc:
        return doc
    if (
        "result" in doc
        and isinstance(doc["result"], dict)
        and "sha256" in doc["result"]
        and "payload" in doc["result"]
    ):
        return doc["result"]
    raise ValueError("Could not find receipt object (expected receipt.payload, result.receipt, or inline sha256/blake3/payload)")


def verify_receipt_data(receipt: dict[str, Any]) -> tuple[bool, str]:
    pl = receipt.get("payload")
    if not isinstance(pl, dict):
        return False, "receipt missing dict payload"
    expected_sha = receipt.get("sha256")
    expected_b3 = receipt.get("blake3")
    if not isinstance(expected_sha, str) or not isinstance(expected_b3, str):
        return False, "receipt missing sha256 or blake3 string fields"
    data = canonical_bytes(pl)
    got_sha = hashlib.sha256(data).hexdigest()
    got_b3 = blake3.blake3(data).hexdigest()
    if got_sha == expected_sha and got_b3 == expected_b3:
        return True, f"VERIFIED: dual hash matches (sha256={got_sha[:12]}...)"
    parts = []
    if got_sha != expected_sha:
        parts.append(f"SHA256 mismatch (expected {expected_sha}, got {got_sha})")
    if got_b3 != expected_b3:
        parts.append(f"BLAKE3 mismatch (expected {expected_b3}, got {got_b3})")
    return False, "FAILED: " + "; ".join(parts)


def main() -> int:
    argv = [a for a in sys.argv[1:] if a not in ("--all",)]
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: python verifier/verify.py <receipt.json>", file=sys.stderr)
        return 1
    path = Path(argv[0])
    if not path.is_file():
        print(f"FAIL: not a file: {path}", file=sys.stderr)
        return 1
    try:
        doc = _load_doc(path.read_text(encoding="utf-8"))
        receipt = _extract_receipt(doc)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    ok, msg = verify_receipt_data(receipt)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
