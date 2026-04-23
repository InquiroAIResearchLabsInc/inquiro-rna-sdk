# Local mock MCP server

- **Endpoint:** `POST http://localhost:8000/mcp` (JSON-RPC 2.0, or raw attestation JSON with `event_type`).
- **Health:** `GET http://localhost:8000/health`

**Hash values** are real cryptographic computations (SHA-256 + BLAKE3 over the same canonical JSON as the Python verifier). **Merkle chain** uses a simple in-memory counter starting at 1. **Signatures** are `mock_ed25519_signature`. **Tenant isolation** is not implemented.

Use the live API for production-grade receipt generation: `https://aiflightrecorder.onrender.com/mcp`.

Run (from repo root, after `pip install -r mock/requirements.txt`):

```bash
python mock/mock_server.py
```
