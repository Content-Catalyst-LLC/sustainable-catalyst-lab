# Sustainable Catalyst Lab v0.27.2

## Long-Running Numerical Jobs and Checkpoint Recovery

This release adds checkpoint-aware execution to the governed Python Compute Core. Parameter sweeps and bootstrap uncertainty runs can persist partial progress, pause, resume, recover after interruption, expose partial results, and complete through the existing WordPress control plane.

### Added

- Persistent checkpoint and partial-result tables
- In-place migration of existing SQLite queues
- Pause, resume, checkpoint-history, cache-status, and cache-purge endpoints
- Priority scheduling and project-level active-job limits
- Deterministic result caching
- Long Jobs & Checkpoints Lab studio and focused shortcode
- Updated queue, worker, capabilities, health, and provenance reporting
- Recovery-safe WordPress proxy controls

### Preserved

- 23 registered compute methods
- Fourteen numerical validation benchmarks
- HMAC-SHA256 authentication
- Isolated worker processes and hard cancellation/timeouts
- All recovered scientific domain extensions
- v0.26.6 production recovery and v0.27.1 validation layers
