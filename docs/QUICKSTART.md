# Quickstart

## 1. Prerequisites

- `curl`
- Python 3.12+ (`python3`, `pip`)
- Optional: Go 1.22+ for `examples/go`, Node.js 18+ for `examples/nodejs`

## 2. Your first receipt

From the repo root, submit `payloads/identity_verified.json` via JSON-RPC:

```bash
python3 scripts/submit_payload.py https://aiflightrecorder.onrender.com/mcp payloads/identity_verified.json /tmp/receipt.json
python3 -m json.tool < /tmp/receipt.json
```

## 3. Verify your receipt

Merge the API response with the attestation file, then verify dual-hash binding:

```bash
python3 scripts/merge_attestation_response.py payloads/identity_verified.json /tmp/receipt.json /tmp/merged.json
python verifier/verify.py /tmp/merged.json
```

## 4. Try all event types

Loop `payloads/*.json` through the same submit → merge → `verifier/verify.py` flow, or run:

```bash
RNA_URL=http://localhost:8000/mcp bash examples/curl/02-submit-attestation.sh
```

(Use mock or live by setting `RNA_URL`.)

## 5. Integrate into your CI

Copy [.github/workflows/verify-receipts.yml](../.github/workflows/verify-receipts.yml) into your repository. It submits each payload to the live API and runs the verifier plus a tamper test.

## 6. Run locally with the mock server

See [mock/README.md](../mock/README.md). Start the mock, set `RNA_URL=http://localhost:8000/mcp`, and run `examples/curl/*.sh`.

## 7. Request a pilot tenant

[Contact Inquiro](https://inquiroresearchlabs.ai/contact/) for a dedicated tenant, Ed25519 keys, and SLA.
