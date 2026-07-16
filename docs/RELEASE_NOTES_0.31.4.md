# Sustainable Catalyst Lab v0.31.4 Release Notes

## Dispatcher Operations, Dead-Letter Recovery, and Observability

v0.31.4 turns the persistent distributed dispatcher into an operable production queue. It adds normalized failure classification, bounded exponential retry backoff, a durable dead-letter lifecycle, administrator replay and cancellation, combined event timelines, queue metrics, and SQLite diagnostics.

### Added

- Eleven normalized dispatcher failure classes with explicit retry and severity policies.
- Bounded exponential backoff with configurable base and maximum delays.
- `retrying` and `dead-lettered` queue states with attempt-exhaustion handling.
- Durable failure class, failure code, retryability, dead-letter timestamp, and operator-note fields.
- Append-only operator-action records for replay and cancellation.
- Single and bulk dead-letter replay, with optional attempt reset.
- Per-item inspection and combined queue/contract/lease/operator timeline.
- Queue-depth, age, lease, throughput, failure-distribution, and operator-action metrics.
- SQLite integrity, foreign-key, WAL, journal-mode, size, schema, and path diagnostics.
- Administrator-only WordPress operations proxy routes and a new Dispatcher Operations panel.
- v0.31.4 JSON contracts, deployment variables, tests, documentation, and release metadata.

### Compatibility

The release is cumulative over v0.31.0-v0.31.3. Existing v0.31.1 SQLite dispatcher databases migrate in place to schema version 3 by adding nullable failure and operator fields plus the operator-actions table. Existing queue, contract, worker, credential, artifact, and execution records remain valid.

### Storage note

The default Render blueprint still declares no paid persistent disk. Dispatcher and artifact paths under `/app/data` are instance-local unless a persistent disk is mounted and the corresponding status variables are set accurately.
