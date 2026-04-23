#!/usr/bin/env python3
"""Print base64( canonical_bytes(payload) ) for a receipt or API response file. One line."""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

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
    raise ValueError("Could not find receipt object")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: payload_canonical_b64.py <receipt.json>", file=sys.stderr)
        return 1
    p = Path(sys.argv[1])
    try:
        doc = _load_doc(p.read_text(encoding="utf-8"))
        r = _extract_receipt(doc)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"read/extract: {e}", file=sys.stderr)
        return 1
    pl = r.get("payload")
    if not isinstance(pl, dict):
        print("no dict payload in receipt", file=sys.stderr)
        return 1
    b = canonical_bytes(pl)
    print(base64.b64encode(b).decode("ascii"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
