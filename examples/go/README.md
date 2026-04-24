# Go examples

Per self-service v2: **client** is SHA-256 only (stdlib `crypto/sha256`). Full BLAKE3 verification is in **verify-receipt** using [github.com/zeebo/blake3](https://github.com/zeebo/blake3) (not in the Go standard library).

## Setup

```bash
cd examples/go
go mod download
```

## `client`

Prints a demo canonical JSON line and the SHA-256 of the `identity_verified`-shaped struct.

```bash
go run ./cmd/client
go run ./cmd/client -v   # also print the JSON
```

## `verify-receipt`

Recomputes SHA-256 and BLAKE3 of the `payload` object in a saved receipt and compares to `sha256` / `blake3` fields. Accepts the same file shapes as [`verifier/verify.py`](../../verifier/verify.py) (inline receipt, `receipt`, or `result.receipt`).

```bash
go run ./cmd/verify-receipt /path/to/receipt.json
```

**Note:** The canonical JSON of `payload` must match the Python `canonical_payload.canonical_bytes` (sorted object keys, compact separators). For production verification, the Python verifier is the reference implementation.
