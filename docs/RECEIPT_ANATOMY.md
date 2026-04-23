# Receipt anatomy

## JSON-RPC envelope

HTTP responses follow JSON-RPC 2.0. For `tools/call`, the `result` object includes:

- `content`: MCP content array; `content[0].text` is a JSON string of the tool result
- Lifted fields: production HTTP may duplicate tool fields (`receipt_hash`, `chain_position`, `accepted`) on `result` for convenience

## submit_attestation tool result

| Field | Meaning |
|-------|---------|
| `receipt_hash` | Dual hash `sha256_hex:blake3_hex` (129 characters) over the canonical attestation body |
| `chain_position` | Merkle chain sequence position |
| `accepted` | Whether the attestation was accepted |

## verify_receipt tool result

| Field | Meaning |
|-------|---------|
| `valid` | Whether the receipt validates for the tenant / ledger |
| `chain_intact` | Chain integrity signal |
| `timestamp` | Verification timestamp |
| `receipt_type` | Receipt category (e.g. `attestation`) |

## query_flight_summary / get_flight_health

These tools return summary metrics. The `topology` field is a **public API enum** (`open`, `closed`, or `hybrid`) from the production sanitizer whitelist — not internal documentation.

## Canonicalization (client verification)

The attestation body hashed for `receipt_hash` is the JSON object with keys:

`device_id`, `event_type`, `payload`, `signature`, `timestamp`

serialized with **sorted keys**, **no insignificant whitespace**, UTF-8, using `separators=(',', ':')` (Python) or equivalent. Anyone with the same attestation JSON can recompute SHA256 and BLAKE3 and compare to the two halves of `receipt_hash`.

See [verifier/README.md](../verifier/README.md) for CLI usage.
