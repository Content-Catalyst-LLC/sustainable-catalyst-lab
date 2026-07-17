# Closed-Loop Simulation and Instrument Campaigns — v0.33.2

This release adds a governed closed-loop layer above adaptive campaigns, workflows, the distributed dispatcher, secure workers, and artifact transport.

- Adds simulation, instrument, and hybrid loop modes.
- Converts campaign proposals into typed, reviewable command envelopes.
- Ingests instrument measurements as campaign observations.
- Adds optional HMAC-SHA256 measurement signatures and SHA-256 deduplication.
- Adds signal limits, setpoint limits, maximum step deltas, emergency-stop signals, operator approval, and failure thresholds.
- Persists cycles, commands, measurements, safety results, and timelines in SQLite WAL.
- Adds authenticated FastAPI routes and administrator-only WordPress proxies.
- Adds the Closed-Loop Campaigns operations panel and brings the Lab to 64 registered panels.

Lab does not directly drive physical devices or expose arbitrary callbacks. A separately governed gateway remains responsible for hardware communication.
