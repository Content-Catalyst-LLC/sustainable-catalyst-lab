# Sustainable Catalyst Lab v0.63.0 — Scientific Literature, Citation Graph & Source-to-Claim Provenance

## Release intent

v0.63.0 extends the v0.62 scientific claims/evidence line outward to literature and archival sources. Researchers can register bounded bibliographic metadata, review source applicability, connect literature records to explicit scientific claims, preserve contradictory/non-replication findings, and record source-to-source citation relations.

This release evaluates **provenance and review state**, not literature truth. It does not fetch literature during evaluation, infer bibliometric authority, treat citation counts as quality, verify retractions automatically, generate claims from papers, or certify scientific conclusions.

## Added

- `sc-lab-scientific-literature-source/0.63.0` governed source record.
- `sc-lab-scientific-literature-review/0.63.0` human source-review record.
- `sc-lab-source-claim-provenance/0.63.0` source-to-claim provenance link.
- `sc-lab-scientific-citation-graph/0.63.0` source-to-source relation edge.
- `sc-lab-scientific-literature-provenance-packet/0.63.0` deterministic metadata-only provenance packet.
- Literature source types for journal articles, preprints, reports, datasets, books/chapters, theses, conference papers, standards, government publications, repository records, archive records, and other governed records.
- Bibliographic identifiers for DOI, PMID/PMCID, arXiv, ISBN/ISSN, Handle/URI, and Research Library record references.
- Source status and declared peer-review state.
- Human source review decisions: include, include with caution, exclude, reopen.
- Source-to-claim roles: supports, contradicts, contextualizes, methodological background, uncertainty, limitation, replication, and non-replication.
- Citation graph relations including cites, supports, contradicts, extends, replicates, fails to replicate, corrects, retracts, uses data from, uses method from, and related.
- Explicit unresolved-source and unresolved-citation-edge detection.
- Duplicate identifier groups are surfaced but never auto-merged.
- Orphan literature sources are visible instead of hidden.
- Contradictory/non-replication literature requires a qualified v0.62 claim review before the literature layer reaches `traceable`.
- Project persistence in `scientificLiteratureSourcesV0630`, `scientificLiteratureClaimLinksV0630`, and `scientificCitationEdgesV0630`.
- Final metadata-only evidence saved to `analysisPackets` as `scientific-literature-provenance-v0630`.

## Provenance gates

- `literature-unlinked` — claims exist without literature provenance links.
- `needs-source` — a source-to-claim link or citation edge has an unresolved source reference.
- `needs-source-review` — linked sources exist but have not been human-reviewed for inclusion/applicability.
- `contested` — reviewed contradictory/non-replication literature exists and the claim is not yet qualified.
- `traceable` — literature/source lineage is explicit and reviewed.

A `traceable` result is not a truth score, authority ranking, systematic-review completeness claim, or scientific certification.

## Governance boundaries

The following remain disabled:

- automatic literature truth scoring;
- automatic bibliometric authority ranking;
- automatic retraction/correction verification;
- automatic claim inference from literature;
- automatic scientific certification;
- automatic publication;
- network fetching during provenance evaluation;
- raw/full-text document ingestion into the provenance packet;
- arbitrary code/callback execution.

Source retraction/correction and peer-review states are declared metadata unless a separate governed connector verifies them. Citation counts do not imply authority. Contradicting evidence and non-replication records remain visible.

## Interface

The feature is contextual inside the existing Scientific Workflows workspace, immediately after the v0.62 claims/evidence section. The six primary rail destinations, Graph Studio front door, and Prototyping Workbench / Decision Studio / Site Intelligence application row remain unchanged. No `MutationObserver` was introduced.

## Certification

The release gate extends the v0.62 scientific/security/runtime line with focused v0.63 literature-provenance tests, browser/PHP integration checks, FastAPI route assertions, WordPress runtime-integrity verification, syntax checks, and a complete SHA-256 source manifest.
