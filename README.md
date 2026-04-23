# Inquiro RNA SDK

Receipts-native architecture for autonomous AI systems.
Every AI decision emits a cryptographic receipt at compute-time.
Dual-hash (SHA256 + BLAKE3). Merkle chained. Court-admissible under FRE 901(b)(9).

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/inquiroairesearchlabsinc/inquiro-rna-sdk)
[![MIT License](https://img.shields.io/badge/license-MIT-amber)](LICENSE)
[![Try in Browser](https://img.shields.io/badge/try-live_sandbox-amber)](https://inquiroresearchlabs.ai/developers/sandbox/)

Read [`CLAUDEME.md`](CLAUDEME.md) (Inquiro execution standard) first.

---

## Your first receipt in 60 seconds

No account. No setup. Paste this into a terminal (wraps `payloads/identity_verified.json` as JSON-RPC `submit_attestation`):

```bash
python3 -c "import json,pathlib; p=pathlib.Path('payloads/identity_verified.json'); a=json.loads(p.read_text()); r={'jsonrpc':'2.0','id':'1','method':'tools/call','params':{'name':'submit_attestation','arguments':a}}; print(json.dumps(r))" \
  | curl -s -X POST https://aiflightrecorder.onrender.com/mcp -H "Content-Type: application/json" -d @- \
  | python -m json.tool
```

You'll receive a dual-hash receipt. Merge the response with the payload and verify:

```bash
python3 scripts/submit_payload.py https://aiflightrecorder.onrender.com/mcp payloads/identity_verified.json /tmp/r.json
python3 scripts/merge_attestation_response.py payloads/identity_verified.json /tmp/r.json /tmp/merged.json
python verifier/verify.py /tmp/merged.json
```

---

## What you just received

See [docs/RECEIPT_ANATOMY.md](docs/RECEIPT_ANATOMY.md).

---

## Three ways to integrate

### 1. Run locally with the mock server (15 minutes)

Tests MCP protocol flow without consuming live API calls.
Note: Mock hashes are not real — for protocol testing only.
See [mock/README.md](mock/README.md) for setup.

### 2. Open in Codespaces (2 minutes, zero local install)

Click the badge above. Full environment pre-configured.
Mock server starts automatically. First smoke test runs on open.

### 3. Hit the live API directly

See [examples/curl/](examples/curl/) for working request examples.
See [docs/QUICKSTART.md](docs/QUICKSTART.md) for a step-by-step guide.

---

## Event types

[docs/EVENT_TYPES.md](docs/EVENT_TYPES.md)

## Receipt anatomy

[docs/RECEIPT_ANATOMY.md](docs/RECEIPT_ANATOMY.md)

## Moving to production

[docs/PRODUCTION.md](docs/PRODUCTION.md)

---

## Ready for a pilot?

Dedicated tenant. Your Ed25519 key pair. Unlimited rate limits. SLA.
[Request a pilot conversation →](https://inquiroresearchlabs.ai/contact/)

---

MIT License. Built by [Inquiro AI Research Labs](https://inquiroresearchlabs.ai).
