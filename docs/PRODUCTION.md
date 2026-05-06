# Production

## What changes from demo to production

- **Dedicated tenant** with a unique `receipt_namespace` and isolation flags
- **Your Ed25519 key pair** for partner signatures (generate securely; never commit private keys)
- **Rate limits** — per-minute and per-day caps per tenant configuration
- **Persistent Merkle chain** — backed by durable storage (not ephemeral demo containers)
- **SLA** — agreed availability and support for pilot customers

## How to request production / pilot

Use the [contact form](https://inquiroresearchlabs.ai/contact/) to start a pilot conversation. A tenant, keys, and limits are provisioned out-of-band.

## Operational checklist

- Store merged verification JSON or full RPC responses according to your retention policy
- Run [../.github/workflows/ci.yml](../.github/workflows/ci.yml) (or equivalent) on every release branch
- Use a dedicated uptime monitor (UptimeRobot, Better Uptime, etc.) to track live API health
