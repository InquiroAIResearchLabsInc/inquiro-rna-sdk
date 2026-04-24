# Go examples

<<<<<<< HEAD
Requires Go 1.22+.

- `go run client.go` — JSON-RPC demo of all five tools (set `RNA_URL` or pass `--mock`).
- `go run verify_receipt.go path/to/merged.json` — verify dual-hash binding (`github.com/zeebo/blake3`).

Do not run `go build .` in this directory: both files are separate `main` programs; invoke `go run` with a single file.
=======
Per self-service v2: **client** is SHA-256 only (stdlib `crypto/sha256`). Full BLAKE3 verification is in **verify_receipt** using [github.com/zeebo/blake3](https://github.com/zeebo/blake3) (not in the Go standard library).

## Setup

```bash
go mod download
```

## `client`

Prints a demo canonical JSON line and the SHA-256 of the `identity_verified`-shaped struct.

```bash
go run ./client
go run ./client -v   # also print the JSON
```

## `verify_receipt`

Recomputes SHA-256 and BLAKE3 of the `payload` object in a saved receipt and compares to `sha256` / `blake3` fields. Accepts the same file shapes as [`verifier/verify.py`](../../verifier/verify.py) (inline receipt, `receipt`, or `result.receipt`).

```bash
go run ./verify_receipt /path/to/receipt.json
```

**Note:** The canonical JSON of `payload` must match the Python `canonical_payload.canonical_bytes` (sorted object keys, compact separators). For production verification, the Python verifier is the reference implementation.
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
