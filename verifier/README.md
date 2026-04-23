# Verifiers

Two independent verifiers ship with this SDK:

- **`verify.py`** — Python CLI (recommended for CI). Requires `blake3` and matches the live API canonical attestation body.
- **`verify.js`** — JavaScript module + Node CLI. Uses `@noble/hashes` for BLAKE3 and `crypto` for SHA256.

## Canonical JSON

The attestation body includes exactly these keys (sorted when serialized):

`device_id`, `event_type`, `payload`, `signature`, `timestamp`

Serialization: UTF-8, `sort_keys=True` (Python) or lexicographic key order at every object level, no insignificant whitespace, separators `,` and `:` only.

## Input format

Pass a **merged** JSON file: the original `payloads/*.json` attestation **plus** `receipt_hash` (and optional `chain_position`, `accepted`) from the API. Build it with:

```bash
python3 scripts/merge_attestation_response.py payloads/identity_verified.json /tmp/api.json /tmp/merged.json
```

## CLI usage

```bash
pip install blake3
python verify.py /tmp/merged.json
```

```bash
cd verifier && npm install && node verify.js /tmp/merged.json
```

## Meaning of results

- **VERIFIED / verified: true** — SHA256 and BLAKE3 (when enabled) match `receipt_hash` for the canonical attestation bytes.
- **FAILED** — Any mismatch means the attestation body does not match the receipt (tamper or wrong merge).

See [docs/RECEIPT_ANATOMY.md](../docs/RECEIPT_ANATOMY.md).
