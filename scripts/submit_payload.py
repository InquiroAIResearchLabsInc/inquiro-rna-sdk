#!/usr/bin/env python3
"""POST submit_attestation (JSON-RPC) for a payloads/*.json file. Writes raw HTTP body to stdout."""
from __future__ import annotations

import json
import subprocess
import sys


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: submit_payload.py <mcp_url> <attestation.json> <out_response.json>", file=sys.stderr)
        sys.exit(1)
    url, att_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    att = json.loads(open(att_path, encoding="utf-8").read())
    body = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {"name": "submit_attestation", "arguments": att},
    }
    with open(out_path, "w", encoding="utf-8") as out:
        subprocess.run(
            [
                "curl",
                "-sf",
                "-X",
                "POST",
                url,
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(body),
            ],
            check=True,
            stdout=out,
            text=True,
        )


if __name__ == "__main__":
    main()
