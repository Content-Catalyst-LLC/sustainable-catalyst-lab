# Report Composer, Accessibility, and Restore Validation

## Architecture

Lab v0.9.5 is an incremental browser-side workflow and reliability release layered over the v0.9.4 reporting, PDF, compute, and Decision Studio handoff architecture. It does not replace the ReportLab PDF service or the Decision Studio packet validator.

The new module is loaded after the existing workspace modules:

```text
assets/js/modules/release-v095.js
```

It progressively enhances these existing workspaces:

```text
[data-lab-module="report-studio"]
[data-lab-module="visualization-studio"]
[data-lab-module="workspace-data"]
```

The stable project storage keys are preserved, while the project model advances to schema version `0.9.5` and gains new collections for drafts, revisions, packages, audits, preflights, receipts, and migration validation.

## Report composition contract

A composition stores template identity, title metadata, an ordered list of enabled or disabled sections, narrative text, revision number, and timestamps. Applying a composition populates the v0.9.4 Report Studio fields and dispatches:

```text
sc-lab-report-composition-applied
```

Consumers can listen for this event to map section ordering into later server-side report renderers. The ZIP package uses stored ZIP entries for broad compatibility and contains:

```text
manifest.json
report-composition.json
project-context.json
```

Narrative editing does not rewrite source analyses, figures, calculations, or evidence records.

## Accessibility audit boundary

The automated audit checks structural conditions that can be inspected in the browser. It adds chart names, SVG title and description nodes, keyboard focus, live-region semantics, and data-table alternatives when structured data is available.

It does not assert WCAG conformance. The saved record explicitly requires manual testing for:

- Full keyboard operation
- Screen-reader interpretation
- Browser zoom and large text
- Color contrast
- Forced-color mode
- Reduced motion
- Mobile layouts
- Printed and grayscale figures

## Restore safety model

Restore follows this order:

1. Read JSON or a supported ZIP workspace entry.
2. Validate structure and collection types.
3. Calculate a source SHA-256 checksum when supported.
4. Compare incoming project IDs with current projects.
5. Calculate copy, merge, or replace dry-run impact.
6. Block on structural errors.
7. Require typed `REPLACE` authorization for destructive replacement.
8. Download a current-workspace safety backup before replacement.
9. Apply the selected semantics.
10. Re-read storage and calculate the post-restore fingerprint.
11. Save and download a restore receipt.

ZIP preflight supports stored entries and deflated entries in browsers that expose `DecompressionStream('deflate-raw')`. JSON remains the universal restore format.

## Migration validation

The migration validation command creates non-destructive synthetic fixtures representing v0.1.x through v0.9.4-era project shapes. Each fixture is normalized into the v0.9.5 collection model and checked for stable project identity, preserved notes, complete array collections, and the v0.9.5 target schema. The result is saved as a `migrationValidationRecords` project record and exported as JSON.

## Responsible use

Accessibility audits are review aids rather than compliance certifications. Restore receipts document browser-local data operations but do not replace independent archival backups. Replace mode remains intentionally explicit and guarded because browser-local project data may not be recoverable without a valid backup.
