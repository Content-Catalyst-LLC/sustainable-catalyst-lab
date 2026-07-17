# Closed-Loop Simulation and Instrument Campaigns — v0.33.2

Sustainable Catalyst Lab v0.33.2 connects adaptive experiment campaigns to repeated simulation and instrument-observation cycles without turning the Lab coordinator into an unrestricted device controller.

## Architecture

A closed-loop definition references an existing adaptive experiment campaign. Simulation loops reconcile completed workflow-backed trials into durable cycles. Instrument loops convert campaign proposals into typed command envelopes, optionally require operator approval, and accept signed or manually authenticated measurement envelopes. Hybrid loops alternate simulation evidence and instrument observations under the same campaign objective and provenance chain.

## Safety boundary

The coordinator never executes arbitrary Python, shell commands, callback URLs, or raw device instructions. It stores and emits declarative parameter setpoints only. Physical transport remains the responsibility of a separately governed gateway. The gateway returns measurement envelopes through authenticated API routes.

Safety controls include signal ranges, parameter ranges, maximum step deltas, emergency-stop signals, command approval, consecutive-failure limits, measurement deduplication, canonical SHA-256 payload hashes, and optional HMAC-SHA256 signatures.

## Durable records

SQLite WAL storage preserves loop definitions, cycles, commands, measurements, safety decisions, objective observations, campaign trial links, workflow run links, operator actions, and event timelines. Deployment health distinguishes instance-local storage from a mounted persistent disk.
