# Multi-Instance Operations, Backup, Migration, and Disaster Recovery — v0.39.2

Sustainable Catalyst Lab v0.39.2 adds a recovery-oriented control plane for operating one or more Lab instances.

## Safety model

- SQLite databases are copied through the SQLite backup API for transaction-consistent snapshots.
- Every archive has a canonical SHA-256 manifest and optional HMAC signature.
- ZIP members are restricted to a safe single root; traversal paths and symlinks are rejected.
- Restore requests extract into a new staging directory and verify every file. The API never overwrites an active database, artifact store, or configuration file.
- Migration plans require a verified backup and use an idempotent execution journal.
- Cross-instance transfer envelopes bind source instance, target instance, backup identity, archive hash, and optional HMAC signature.
- Recovery drills measure backup age and elapsed staged-restore time against configured RPO and RTO targets.

## Required production configuration

Use persistent storage for the operations database, backup root, security databases, institutional governance database, and research data stores. Configure a strong `SC_LAB_BACKUP_SIGNING_SECRET` in the host secret manager. The signing secret must not be placed in WordPress, browser code, source control, or release archives.

## Deliberate limitations

v0.39.2 does not upload backups to arbitrary remote destinations, activate restored files automatically, or force-push Git branches. Remote object-storage connectors and automated failover require a separately reviewed deployment integration.
