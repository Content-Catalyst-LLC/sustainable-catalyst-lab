# Lab v0.140.0.1 — Scientific Research OS Release Manifest & Runtime Integrity Repair

## Defect repaired
The original v0.140.0 release manifest declared repository test files as WordPress-critical while the WordPress package intentionally excluded `tests/`. Production `/wp-json/sc-lab/v1/runtime/health` therefore reported a partial/mismatched installation even when the functional v0.140.0 plugin was installed correctly.

## Repair contract
- Product release identity becomes `0.140.0.1`.
- Scientific Research OS feature semantics remain `0.140.0`.
- `wordpressCriticalFiles` is generated only from immutable files that belong to the installed WordPress runtime surface.
- Mutable `data/` state is excluded.
- Repository/backend/package-only surfaces are independently packaged and do not participate in WordPress runtime-health hashes.
- Canonical route checks, plugin basename/folder checks, and release/platform version consistency remain enforced.
- Backend functionality is unchanged and retained as the v0.140.0 Scientific Research OS API; a v0.140.0.1 backend archive is supplied for synchronized deployment lineage.

## Upgrade gate
Do not continue to v0.141.0 until `/wp-json/sc-lab/v1/runtime/health` reports `state: verified`, `partialInstallRisk: false`, `releaseVersion: 0.140.0.1`, and `routeIntegrityVerified: true`.
