# Sustainable Catalyst Lab v0.70.0 R1 — Repository Runtime-Health Scope, Plugin Identity & Route-Alias Repair

## Repair intent

R1 repairs the promotion boundary for the certified v0.70.0 preregistration release. The v0.70.0 scientific implementation and exact packaged source passed their release gate, but the post-install repository validation incorrectly evaluated a Git checkout as if it were a live WordPress plugin installation. A checkout named `sustainable-catalyst-lab-repository` was therefore treated as a plugin-folder identity mismatch, and sibling source checkouts under `~/Downloads` were counted as duplicate installed WordPress plugins.

R1 does not change preregistration semantics, scientific gates, stored project collections, FastAPI contracts, or the WordPress-facing release number. It repairs only runtime-health context, plugin identity scope, route-alias verification, installer repository discovery, and promotion certification.

## Repaired runtime-health scope

The integrity layer now recognizes two governed validation contexts:

- `wordpress-plugin` — live WordPress runtime. Canonical plugin-folder identity remains required and duplicate-plugin detection remains strict within `WP_PLUGIN_DIR`.
- `repository-validation` — installer/source-checkout certification. The current Git checkout is the only plugin candidate considered, a checkout folder such as `sustainable-catalyst-lab-repository` is valid, and sibling development/source checkouts are not treated as installed WordPress plugins.

The health packet now exposes:

- `runtimeContext`
- `repairLine: 0.70.0-r1`
- `pluginCandidateScope`
- `routeIntegrityVerified`
- repository-aware identity fields including `folderRequired` and `sourceCheckoutFolderAccepted`

This does not weaken live WordPress duplicate-plugin safeguards.

## Plugin identity repair

Repository certification no longer requires the Git checkout directory itself to be named `sustainable-catalyst-lab`. The canonical WordPress basename remains `sustainable-catalyst-lab/sustainable-catalyst-lab.php`, while source checkout names are treated as packaging/development context rather than installed plugin identity.

In live WordPress context, the canonical plugin folder remains required and multiple `*/sustainable-catalyst-lab.php` candidates under the WordPress plugin directory still produce `duplicate-plugin-risk`.

## Route-alias repair

Runtime-health alias validation is now self-sufficient and verifies these governed compatibility routes:

- `marine` → `marine-biology`
- `climate` → `climate-maps`
- `evidence` → `evidence-decisions`
- `astronomy-observations` → `space-telescopes`

When the legacy runtime router is loaded, its canonical resolver remains authoritative. During standalone integrity certification, the integrity layer uses the same bounded compatibility contract as a fallback. A route check passes only when the alias resolves to the expected canonical slug and the canonical panel is present in `templates/lab-app.php`.

Route integrity is now part of the overall runtime-health result rather than informational-only metadata.

## Installer and promotion repair

The R1 installer:

- validates the exact packaged R1 source before repository mutation;
- adds `~/Downloads/sustainable-catalyst-lab-repository` and `~/Downloads/sustainable-catalyst-lab-repo` to explicit repository discovery candidates;
- runs the complete inherited v0.70.0 gate plus R1 repository/live-WordPress integrity contracts;
- installs the certified tree only after validation succeeds;
- reruns the R1 gate from the actual Git checkout in `repository-validation` context;
- commits only after the post-install gate passes;
- uses the repair tag `v0.70.0-r1`, leaving the WordPress plugin version at `0.70.0`.

## Preserved scientific line

Unchanged from v0.70.0:

- `scientificResearchQuestionsV0700`
- `scientificHypothesisRegistryV0700`
- `scientificPreregistrationsV0700`
- `scientificPreregistrationFreezesV0700`
- `scientificPreregistrationDeviationsV0700`
- `analysisPackets` / `recordType: preregistration-v0700`
- pre-result attestation
- immutable preregistration freeze and `planHash`
- timestamped deviation logging
- human preregistration review
- six primary Lab destinations
- Graph Studio front door
- Prototyping Workbench / Decision Studio / Site Intelligence cards
- no `MutationObserver`

Still disabled:

- automatic hypothesis validation
- automatic post-hoc preregistration
- automatic outcome reclassification
- automatic publication
- raw scientific data in preregistration packets
- participant-level data
- network fetching during evaluation
- arbitrary code execution

## Release identity

- WordPress release: `0.70.0`
- Repair line: `R1`
- Repair tag: `v0.70.0-r1`
- Platform compatibility: `1.0.0`
- Focused scientific/security/runtime Python regression line: inherited `393` assertions/tests
- Additional R1 PHP/runtime contracts: repository-scope, live WordPress duplicate detection, route-alias integrity, and repair metadata

The promotion gate must fail before Git mutation if either repository validation or live WordPress identity semantics regress.
