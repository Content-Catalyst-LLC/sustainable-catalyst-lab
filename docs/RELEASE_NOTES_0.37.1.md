# Sustainable Catalyst Lab v0.37.1 Release Notes

## Manuscript, Report, Notebook, and Methods Assembly

Sustainable Catalyst Lab v0.37.1 extends the v0.37.0 reproducibility and publication layer with a governed research-document assembly studio.

### New capabilities

- Reusable workspace section library with revision numbers and SHA-256 content identities.
- Immutable section snapshots inside assemblies, so later library edits do not silently rewrite prior drafts.
- Manuscript, technical report, output-only notebook, methods supplement, and research dossier document types.
- IMRaD, technical-report, methods-supplement, reproducibility-dossier, notebook-narrative, and custom templates.
- Structured methods narratives generated from sealed reproducibility-package methods and environment records.
- Cross-format Markdown, escaped HTML, JATS-lite XML, Jupyter Notebook, methods Markdown, BibTeX, and JSON exports.
- Validation gates, immutable assembly sealing, export hashes, and parent-revision lineage.
- New Manuscript, Report, Notebook & Methods Assembly WordPress workspace.

### Safety boundary

Notebook exports contain narrative and stored result cells only. The release rejects arbitrary code, shell commands, executable expressions, callbacks, credentials, private keys, binary payloads, and embedded restricted dataset bytes.
