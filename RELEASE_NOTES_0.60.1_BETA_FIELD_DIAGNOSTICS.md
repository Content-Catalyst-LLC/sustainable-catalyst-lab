# Sustainable Catalyst Lab v0.60.1 — Beta Field Diagnostics, Integration Soak & Runtime Repair

v0.60.1 is the first stabilization build after the Integrated Scientific Research Beta milestone. It does not add another scientific modeling surface. Instead, it adds a bounded field-diagnostics layer for exercising the live WordPress ↔ Python compute path and localizing cross-studio runtime failures before the beta line expands further.

## Runtime snapshot and integration probe

The release adds a metadata-only runtime snapshot containing release/platform lines, active-module state, WordPress REST and compute reachability, project/local/session storage availability, integrity state, and the established Lab presentation contract. Raw datasets, model inputs, credentials, tokens, cookies, and arbitrary source content are explicitly rejected by the backend diagnostic normalizer.

The integration probe evaluates release alignment, manifest/runtime integrity, REST reachability, compute reachability, project persistence, the six-destination rail, three related application cards, Graph Studio/workflow availability, and the integrated beta capability line. Failures are localized to explicit domains with non-destructive repair hints.

## Bounded integration soak

The browser can run a user-initiated four-cycle soak over five governed endpoints: beta diagnostics, integrated beta, scientific audit, compute hardening, and Scientific Workflow Composer. The backend summarizes endpoint success rate, mean/p50/p95/max latency, flapping, complete cross-studio cycles, transient recovery, and eight bounded stabilization scenarios.

The soak does not run continuously and does not create background monitoring. It is capped at 80 endpoint observations per analysis.

## Diagnostic evidence

A tamper-evident diagnostic packet records only snapshot/probe/soak hashes, pass/warn/fail states, failure domains, repair guidance, and explicit safety boundaries. It can be verified and saved into project `analysisPackets` without copying raw scientific data.

Automatic repair, scientific-state mutation, external telemetry, publication, or scientific certification remain disabled. Human review is required.

## Interface and compatibility

The diagnostic controls are contextual inside the existing Scientific Workflows workspace. v0.60.1 preserves the v0.48.3 six-destination rail, Graph Studio front door, and Prototyping Workbench / Decision Studio / Site Intelligence application row. Internal platform compatibility remains v1.0.0.
