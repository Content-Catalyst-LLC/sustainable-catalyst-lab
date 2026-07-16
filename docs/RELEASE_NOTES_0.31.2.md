# Sustainable Catalyst Lab v0.31.2 — Secure Worker Agent Runtime and Pull-Based Execution

Version 0.31.2 completes the first operational distributed-compute path in Sustainable Catalyst Lab. Trusted local, Raspberry Pi, server, and institutional nodes can now enroll as pull-based workers, claim compatible queue leases, verify signed contracts, execute registered Lab methods, renew leases, and return reproducible completion receipts.

## Added

- Standalone `python3 -m worker_agent` runtime
- Token-gated enrollment and one-time worker-scoped credentials
- Credential hashing, rotation, revocation, quarantine, and last-use tracking
- Worker-scoped heartbeat, claim, acknowledgement, renewal, release, completion, and rotation APIs
- Local HMAC dispatch-contract verification
- Registered-method-only governed execution
- Automatic lease renewal for long calculations
- Idempotent, hash-bearing execution receipts with compute provenance
- macOS launchd and Linux systemd service examples
- WordPress Secure Worker Agents operations panel
- Worker-agent policies, schemas, health checks, and functional validation

## Security boundaries

Workers cannot submit arbitrary source code, shell commands, executable payloads, callback URLs, dynamic imports, or unknown request fields. Contract ownership and lease ownership are checked by the coordinator, and the local worker verifies the contract signature, target worker, and expiration before execution.

## Deployment note

The corrected Render configuration sets the dispatcher database path to `/app/data/sc-lab-dispatcher.sqlite3` and reports whether a persistent disk is mounted. The release does not automatically add a paid Render disk. Queue durability across instance replacement still requires a persistent disk or future external database support.

## Release lineage correction

- v0.31.0 — Distributed Compute Dispatcher
- v0.31.1 — Persistent Queue Infrastructure
- v0.31.2 — Secure Worker Agent Runtime and Pull-Based Execution
