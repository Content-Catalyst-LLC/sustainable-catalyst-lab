# Sustainable Catalyst Lab v0.136.0.1
## Release Manifest Integrity Synchronization Repair

This repair release corrects the WordPress integrity warning discovered after v0.136.0.

The v0.136.0 WordPress package contained two files whose final packaged SHA-256 values no longer matched the manifest: `sustainable-catalyst-lab.php` and `CHANGELOG.md`. v0.136.0.1 updates the product release markers, extends the canonical release parser for four-part numeric repair versions, and regenerates all WordPress critical-file hashes from the finalized source tree.

No scientific-review, reproduction, dependency-analysis, renderer, provenance, or backend feature semantics are changed.
