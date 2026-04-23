#!/usr/bin/env python3
"""Merge payloads/*.json attestation with JSON-RPC API response for verifier/verify.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _lift_result(api: dict[str, Any]) -> dict[str, Any]:
    result = api.get("result")
    if not isinstance(result, dict):
        return {}
    out = dict(result)
    content = result.get("content")
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict) and first.get("type") == "text":
            try:
                inner = json.loads(str(first["text"]))
                if isinstance(inner, dict):
                    for k, v in inner.items():
                        out.setdefault(k, v)
            except json.JSONDecodeError:
                pass
    return out


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: merge_attestation_response.py <payload.json> <api_response.json> <out.json>", file=sys.stderr)
        sys.exit(1)
    att_path = Path(sys.argv[1])
    api_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3])
    att = json.loads(att_path.read_text(encoding="utf-8"))
    api = json.loads(api_path.read_text(encoding="utf-8"))
    lifted = _lift_result(api)
    rh = lifted.get("receipt_hash")
    if not isinstance(rh, str):
        print("FAIL: no receipt_hash in API response", file=sys.stderr)
        sys.exit(1)
    merged = {
        **att,
        "receipt_hash": rh,
        "chain_position": lifted.get("chain_position"),
        "accepted": lifted.get("accepted"),
    }
    out_path.write_text(json.dumps(merged, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
