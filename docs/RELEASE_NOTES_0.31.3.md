# Sustainable Catalyst Lab v0.31.3 — Distributed Artifact, Result, and Checkpoint Transport

Version 0.31.3 adds the governed data plane required by distributed scientific execution. Secure workers no longer need to receive every input or return every result inside queue JSON. The coordinator now manages verified, resumable, content-addressed artifacts with project, queue, contract, worker, and receipt provenance.

## Included

- Content-addressed SHA-256 blob storage with SQLite WAL metadata
- Resumable sequential chunk upload sessions
- Per-chunk and final integrity verification
- Upload quarantine on size or hash mismatch
- Artifact deduplication, ranged reads, manifests, audit history, and retention cleanup
- Administrator artifact APIs
- Worker-scoped upload APIs
- Active-lease-bound worker input download grants
- JSON, text, and base64-binary input materialization
- Automatic large-result externalization from worker completion receipts
- Checkpoint, result, input, log, report, dataset, and provenance artifact kinds
- WordPress Artifact Transport operations panel
- Deployment settings and explicit instance-local versus persistent-disk reporting
- Direct upgrade support from Lab v0.31.0, v0.31.1, or v0.31.2

## Security boundaries

- No arbitrary remote fetch
- No callback URLs
- No executable artifacts
- No arbitrary source code or shell commands
- Worker credentials remain worker-scoped
- Input downloads require an active lease grant
- Every finalized artifact is verified by SHA-256

## Release sequence

- v0.31.0 — Distributed Compute Dispatcher
- v0.31.1 — Persistent Queue Infrastructure
- v0.31.2 — Secure Worker Agent Runtime and Pull-Based Execution
- v0.31.3 — Distributed Artifact, Result, and Checkpoint Transport
