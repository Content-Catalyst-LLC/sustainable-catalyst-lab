# Persistent Queue Infrastructure v0.31.1

SQLite-WAL persistence for dispatcher workers, workloads, leases, contracts, and event history. Atomic `BEGIN IMMEDIATE` claims prevent two coordinators from leasing the same workload. Expired leases are requeued until their maximum attempt count is reached.

This layer is distinct from the v0.27.x numerical job queue and governs distributed dispatch records. Durable behavior across Render replacements requires `SC_LAB_DISPATCHER_DB_PATH` to point at a persistent disk.
