# Go examples

Requires Go 1.22+.

- `go run client.go` — JSON-RPC demo of all five tools (set `RNA_URL` or pass `--mock`).
- `go run verify_receipt.go path/to/merged.json` — verify dual-hash binding (`github.com/zeebo/blake3`).

Do not run `go build .` in this directory: both files are separate `main` programs; invoke `go run` with a single file.
