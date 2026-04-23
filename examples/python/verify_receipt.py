#!/usr/bin/env python3
"""Standalone CLI: delegates to repo verifier/verify.py (same behavior)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    verify_py = ROOT / "verifier" / "verify.py"
    if not verify_py.is_file():
        print("FAIL: verifier/verify.py not found", file=sys.stderr)
        sys.exit(1)
    args = [sys.executable, str(verify_py), *sys.argv[1:]]
    raise SystemExit(subprocess.call(args))


if __name__ == "__main__":
    main()
