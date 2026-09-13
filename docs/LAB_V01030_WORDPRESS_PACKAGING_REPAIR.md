# Lab v0.103.0 WordPress Packaging Repair

This additive repair records the production packaging correction for Sustainable Catalyst Lab v0.103.0.

## Defect

The original v0.103.0 WordPress release ZIP was structurally valid but incomplete. The canonical WordPress integrity manifest requires 1,162 critical plugin files. The production repair restored the complete payload and corrected the stale release identity.

Lab's Git repository is itself the WordPress plugin source tree: `assets/`, `includes/`, `contracts/`, `build/`, `sustainable-catalyst-lab.php`, and the other plugin files live at repository root. A previous repair attempt incorrectly treated `wordpress-plugin/sustainable-catalyst-lab/` as the source root; that attempt stopped before commit or push.

## Repair

- Restore the canonical root `build/sc-lab-release-manifest.json` for Lab v0.103.0 / Energy Systems v1.6.0.
- Add a manifest-driven WordPress packager that reads directly from the repository root.
- Require every file listed in `wordpressCriticalFiles` to exist and match its recorded SHA-256 digest before packaging.
- Add an independent ZIP validator that rejects missing files, hash mismatches, stale release identity, wrong archive root, or unexpected file counts.

The repaired package contains 1,163 files total: 1,162 integrity-critical WordPress files plus the canonical release manifest.

## Release lineage

This is an additive repair on `main`. The existing `v0.103.0` tag is historical release lineage and **must not be moved, deleted, or recreated**.

The already-certified production backend and WordPress runtime do not need to be redeployed solely to record this repository repair.
