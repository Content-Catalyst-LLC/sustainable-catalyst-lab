# Sustainable Catalyst Lab v0.139.0.1
## WordPress Release Manifest Scope & Integrity Repair

This patch fixes a packaging defect in v0.139.0 where the WordPress integrity manifest declared repository-only files as mandatory plugin files even though the WordPress ZIP intentionally excluded them. The resulting installed plugin could report `partial-or-mismatched` despite otherwise correct release files.

No scientific model, study, evidence, review, reproducibility, or publication semantics are changed. v0.139.0.1 is a release-engineering and integrity repair.
