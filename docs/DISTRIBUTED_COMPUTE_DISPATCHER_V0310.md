# Sustainable Catalyst Lab v0.31.0 — Distributed Compute Dispatcher

This release introduces a governed coordinator for heterogeneous compute workers. Worker registrations advertise registered method support, packages, memory, concurrency, checkpoint capability, architecture, tags, project allowlists, and current load. Workloads remain method-registry bound. The coordinator routes by capability, load, preference, resource requirements, and quarantine state, then issues signed time-bounded dispatch contracts.

The initial coordinator registry is process-local and intentionally does not accept arbitrary callback URLs. Worker agents poll or receive contracts through governed adapters. Durable cross-deployment worker state is reserved for the persistent dispatcher release.
