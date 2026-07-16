# Dispatcher Operations, Dead-Letter Recovery, and Observability v0.31.4

Sustainable Catalyst Lab v0.31.4 adds the production operations layer for the persistent distributed dispatcher. It classifies failures, applies bounded retries, preserves terminal work in a dead-letter queue, and gives administrators evidence-based recovery controls without deleting the original workload or its event history.

## Failure lifecycle

Every failed completion, lease release, or expired lease receives a normalized failure classification. Temporary worker, capacity, artifact-transport, lease-timeout, and coordinator failures are retryable by default. Input-validation, missing-method, security-policy, quarantined-worker, and operator-cancelled failures are terminal by default.

Retryable work enters `retrying` with bounded exponential backoff. The delay begins at `SC_LAB_DISPATCHER_RETRY_BASE_DELAY_SECONDS` and cannot exceed `SC_LAB_DISPATCHER_RETRY_MAX_DELAY_SECONDS`. A retryable failure moves to `dead-lettered` when its attempt limit is exhausted. Non-retryable failures move there immediately.

## Dead-letter recovery

Dead-letter records retain the original normalized workload, workload hash, attempts, failure class and code, error summary, worker/lease context, timestamps, and operator note. Administrators can:

- inspect one queue item and its combined queue, contract, lease, and operator-action timeline;
- replay one or up to 250 selected terminal items;
- reset attempts during replay or retain prior attempt history;
- cancel queued, retrying, leased, running, failed, or dead-lettered work with a reason;
- run lease-expiration and stale-worker recovery;
- filter dead letters by normalized failure class.

Hard deletion is intentionally excluded. Recovery creates append-only operator and dispatcher events so a replay never erases the earlier failure.

## Observability

The operations metrics endpoint reports queue counts, ready depth, oldest-ready age, active and soon-expiring leases, completion throughput for one-hour and 24-hour windows, dead letters created in the last hour, failure-class distribution, and operator-action count.

Database diagnostics report SQLite integrity, foreign-key violations, WAL and shared-memory sizes, database size, journal mode, schema version, and whether the configured path appears instance-local. These checks diagnose the dispatcher store; they do not claim that instance-local Render storage survives replacement.

## Security boundaries

The Python coordinator operations routes require the configured compute API key. WordPress same-origin recovery, replay, cancellation, diagnostics, and dead-letter routes require `manage_options`. Workers cannot invoke operator actions through worker-scoped credentials.

The release continues to reject arbitrary code, executable payloads, arbitrary callback URLs, and unregistered methods.

## Configuration

```bash
SC_LAB_DISPATCHER_RETRY_BASE_DELAY_SECONDS=15
SC_LAB_DISPATCHER_RETRY_MAX_DELAY_SECONDS=900
```

The maximum delay is normalized to at least the base delay. Per-workload attempt limits remain bounded by the dispatcher maximum-attempt policy.

## Public health and administration

Public WordPress health/schema routes describe whether the v0.31.4 files and contracts are present. Operational queue data and actions remain administrator-only.
