# Security Review — Inquiro RNA SDK

## Scope

This document covers the public SDK components: mock MCP server, verifier, payload samples, and language examples. It does **not** cover the production RNA ledger service.

## §6 Threat Model

| Asset | Threat | Control |
|---|---|---|
| Receipt integrity | Payload tampering post-issue | Dual-hash (SHA-256 + BLAKE3); verifier detects any byte change |
| Hash algorithm weakness | Single-algorithm collision | Two independent algorithms required; both must match |
| Replay attack | Resubmitting a captured receipt | `request_id` (UUID v4) + `chain_position` must be unique per ledger |
| Mock vs production confusion | Treating mock receipts as production | Docstring and README label mock as PROTOCOL TESTING ONLY |
| Secret exposure | Internal strings in public repo | CI gate scans for forbidden patterns before every push |
| Dependency supply chain | Malicious `blake3` or `zeebo/blake3` update | Pin versions in requirements.txt / go.mod; review on bump |
| MCP hook injection | Malicious MCP server in cloned repo config | Users must review `.claude/settings.json` before enabling MCP servers from untrusted repos |

## §6.1 What the Mock Is Not

- **Not** an Ed25519 signer — `signature` field is the literal string `"mock_ed25519_signature"`.
- **Not** a Merkle ledger — `chain_position` is an in-process counter that resets on server restart.
- **Not** a tenant isolator — `tenant_id` echoes input; no access control is enforced.
- **Not** persistent — receipts exist only in process memory; all state is lost on restart.

## §6.2 Verifier Security Properties

The verifier (`verifier/verify.py`, `verifier/verify.js`) provides:

- **Tamper detection**: recomputes SHA-256 and BLAKE3 over canonical JSON of `payload`; any byte change to the payload produces a different hash and causes exit 1.
- **Canonical form**: `json.dumps(sort_keys=True, separators=(",", ":"))` — deterministic across all conforming Python/JS implementations.
- **No network calls**: verifier is fully offline; it reads only the receipt file provided.

The verifier does **not** verify Ed25519 signatures, Merkle proofs, or chain continuity — those are production-ledger concerns outside the scope of this SDK.

## §6.3 Dependency Inventory

| Dependency | Version | Purpose | Risk |
|---|---|---|---|
| `blake3` (Python) | ≥ 0.4.0 | BLAKE3 hashing | Low — pure Rust binding, no network access |
| `blake3` (npm) | ≥ 0.4.0 | BLAKE3 hashing in verify.js | Low |
| `github.com/zeebo/blake3` | v0.2.4 | BLAKE3 hashing in Go examples | Low |

No other third-party runtime dependencies.

## §6.4 Secrets Scanning

Gate B runs before every push. The CI workflow (`verify-receipts.yml`) scans for a set of internal strings that must not appear in the public repository. All patterns must return zero results or the workflow fails.

## §6.5 Responsible Disclosure

Report security issues to **security@inquiroresearchlabs.ai**. Do not open a public GitHub issue for vulnerabilities.
