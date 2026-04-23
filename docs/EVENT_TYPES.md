# Event types

Inquiro RNA accepts these attestation `event_type` values in public examples:

| event_type | Description | Example payload |
|------------|-------------|-----------------|
| `identity_verified` | Identity / custody verification checkpoint | [payloads/identity_verified.json](../payloads/identity_verified.json) |
| `custody_transferred` | Custody handoff between handlers | [payloads/custody_transferred.json](../payloads/custody_transferred.json) |
| `seal_intact` | Seal / tamper-evident state OK | [payloads/seal_intact.json](../payloads/seal_intact.json) |
| `seal_broken` | Tamper detected | [payloads/seal_broken.json](../payloads/seal_broken.json) |
| `delivery_confirmed` | Delivery completed and confirmed | [payloads/delivery_confirmed.json](../payloads/delivery_confirmed.json) |

## Required attestation fields

Each `payloads/*.json` file is a top-level object with:

- `event_type` (string)
- `device_id` (string)
- `payload` (object) — event-specific fields
- `timestamp` (ISO 8601 string)
- `signature` (base64 string; demo placeholder in samples)

## What the receipt proves

Each successful `submit_attestation` returns a `receipt_hash` (`sha256_hex:blake3_hex`) that binds the canonical serialization of those five fields. Independent verification recomputes the dual hash from the same attestation body.

## Regulatory framing (high level)

Immutable, time-stamped, independently verifiable records support audit and authenticity requirements in many jurisdictions; consult counsel for your use case (e.g. FRE 901(b)(9) discussion in the main README).
