#!/usr/bin/env python3
"""Print base64( canonical_bytes(payload) ) for a receipt or API response file. One line (stderr used for errors)."""
from __future__ import annotations

import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from canonical_payload import canonical_bytes  # noqa: E402
from verifier.verify import _extract_receipt  # noqa: E402
from verifier.verify import _load_doc  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: payload_canonical_b64.py <receipt.json>", file=sys.stderr)
        return 1
    p = Path(sys.argv[1])
    doc = _load_doc(p.read_text(encoding="utf-8"))
    r = _extract_receipt(doc)
    pl = r.get("payload")
    if not isinstance(pl, dict):
        print("no payload", file=sys.stderr)
        return 1
    b = canonical_bytes(pl)
    print(base64.b64encode(b).decode("ascii"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
