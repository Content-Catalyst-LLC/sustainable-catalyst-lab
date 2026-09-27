# Graph Studio Review Workspace Consolidation & Runtime Certification — v0.135.21.0

## Purpose
v0.135.21.0 consolidates the Graph Studio scientific-review runtime established across v0.135.12.0–v0.135.20.0 into a single visible review workspace and a deterministic runtime-certification contract.

## Canonical ownership
- Bootstrap: v0.135.8.3.1
- Renderer: v0.135.8.2
- Provenance: v0.135.8.5.3
- Incremental interaction: v0.135.8.5.2 behavior retained by the native provenance runtime
- Review orchestration/hydration: v0.135.21.0
- Closure/publication-readiness record: v0.135.20.0

Historical review modules remain installed and their records/APIs remain authoritative for their respective object types. v0.135.21.0 orchestrates them; it does not rewrite their history.

## Deterministic hydration
The consolidated runtime normalizes nine review collections in a fixed order: review threads, resolution records, audit records, verification bundles, revision-impact analyses, reproduction bridges, reviewer panels, cross-review syntheses, and closure packages. Records are deterministically ordered before the state digest and restore plan are created.

## Runtime certification
Certification checks collection integrity, duplicate IDs, canonical ownership, duplicate consolidation listeners, deterministic restore order, retained incremental-renderer mode, and state digest generation. Project Workspace receives a read-only certification packet.

## UI consolidation
When the v0.135.21.0 controller is active, the individual v0.135.12.0–v0.135.20.0 review toolbars are visually collapsed and replaced by one Review Workspace toolbar. Their underlying modules and records are not removed.

## Browser harness
A real Chromium harness is included at `tests/chromium-v0135210.html`. In the release-build container, the installed Chromium binary hung on even a blank headless `--dump-dom` invocation, so browser certification is not claimed from that environment. The executable JavaScript DOM/runtime fixture passed.

## Scientific boundary
Runtime certification certifies software/runtime assembly and reproducibility controls only. It does not certify scientific truth, validity, causal correctness, evidentiary weight, reviewer consensus, or publication acceptance.
