# Sustainable Catalyst Lab v0.26.3.1 — Panel Alias and Compatibility Routing Repair

This patch normalizes historical module identifiers before panel lookup and navigation. The aliases `marine`, `climate`, and `evidence` now resolve to `marine-biology`, `climate-maps`, and `evidence-decisions`.

The runtime publishes a canonical module manifest, classifies requested identifiers as canonical, alias, or missing, canonicalizes navigation controls, redirects old query URLs, and suppresses only compatibility warnings that refer to a valid alias whose canonical panel is present in the manifest. Genuine missing-panel diagnostics remain visible in runtime diagnostics.

Asset versions use SHA-256 content hashes, and the health endpoint reports possible duplicate plugin folders.
