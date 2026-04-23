# Inquiro RNA SDK

MIT-licensed partner kit: mock MCP server, sample attestation payloads, dual-hash receipt verifier, GitHub Actions workflows, and Go examples.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/InquiroAIResearchLabsInc/inquiro-rna-sdk)

Read [`CLAUDEME.md`](CLAUDEME.md) (Inquiro execution standard) first.

## Layout

| Path | Purpose |
|------|--------|
| [`canonical_payload.py`](canonical_payload.py) | Canonical JSON bytes (shared with mock + verifier) |
| [`mock/`](mock/) | Local HTTP MCP mock with real SHA-256 + BLAKE3 |
| [`verifier/verify.py`](verifier/verify.py) | CLI: recompute hashes, exit 0/1 |
| [`payloads/`](payloads/) | Five event-type samples |
| [`examples/go/`](examples/go/) | `client` (SHA-256) and `verify_receipt` (SHA-256 + BLAKE3 via [zeebo/blake3](https://github.com/zeebo/blake3)) |
| [`.github/workflows/verify-receipts.yml`](.github/workflows/verify-receipts.yml) | **Push/PR:** mock server + Python + Go verify |
| [`.github/workflows/verify-receipts-live-cron.yml`](.github/workflows/verify-receipts-live-cron.yml) | **Scheduled:** live Render API + verify (retries for cold start) |

## Quick start

```bash
pip install -r requirements.txt
python mock/mock_server.py   # terminal 1
curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d @payloads/identity_verified.json -o /tmp/receipt.json
python verifier/verify.py /tmp/receipt.json
```

```bash
cd examples/go
go run ./verify_receipt /path/to/receipt.json
go run ./client
```

## Codespaces / devcontainer

Open the repo in a dev container: `mock` dependencies install with `uv`, and `postStartCommand` starts the mock and runs a `tools/list` smoke test.

## CI

- **Every push/PR:** receipt generated from the **local mock** (deterministic, no network to Render).
- **Daily cron (`0 6 * * *`):** receipts from the **live** API; retries on slow/failed responses.

## Links

- Live sandbox (product): `https://inquiroresearchlabs.ai/developers/sandbox/` (when deployed)
- Live MCP: `https://aiflightrecorder.onrender.com/mcp`
