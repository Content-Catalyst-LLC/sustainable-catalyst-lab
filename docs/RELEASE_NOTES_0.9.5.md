# Sustainable Catalyst Lab v0.9.5
## Report Composer, Visualization Accessibility, and Data-Restore Validation

Version 0.9.5 completes the cross-cutting v0.9.x infrastructure sequence layered over the Energy and Engineering Systems Laboratory. It adds structured report composition, accessible scientific-visualization controls and audit records, and a validation-first workspace restore path. The domain roadmap continues with v0.10.0 Electrical, Electronics, and Embedded Systems.

## Report Composer

The existing v0.9.4 PDF Report Studio remains the rendering and Decision Studio handoff engine. The new Report Composer adds:

- Technical report, experiment report, analysis brief, and decision brief templates
- Reorderable, removable, and selectively included report sections
- Keyboard reordering with Alt+Up and Alt+Down
- Drag-and-drop section ordering
- Editable section titles and narrative blocks
- Browser autosave scoped to the active project
- Project-backed report drafts and revision history
- Composition JSON exports with deterministic fingerprints
- Self-contained report-package ZIP exports
- One-click application to the existing local and Render PDF workflow

Supported section types include cover page, executive summary, methods, assumptions, results, figures, tables, validation, limitations, sources, appendices, and audit record.

Focused shortcode:

```text
[sc_lab_report_composer]
```

Existing `[sc_lab_reports]` and `[sc_lab_report_studio]` shortcodes remain supported.

## Visualization accessibility

The visualization layer now adds or validates:

- Keyboard focus for SVG, canvas, and structured chart regions
- Accessible chart names and SVG title/description elements
- Polite live regions for status messages
- Data-table alternatives when structured chart rows are available
- Reduced-motion behavior based on system preferences
- High-contrast and grayscale preview controls
- Automated accessibility audit records saved to the active project
- Exportable accessibility-audit JSON
- Print, forced-color, mobile, and zoom-aware CSS

Automated checks do not claim WCAG conformance and do not replace manual screen-reader, keyboard, contrast, browser-zoom, mobile, and print review.

## Data-restore validation

Workspace restore now includes a validation-first path for JSON and compatible ZIP packages:

- Schema and collection-type checks
- Duplicate project-ID detection
- Current-versus-incoming conflict analysis
- Copy, merge, and replace dry-run impact summaries
- Deterministic workspace fingerprints plus SHA-256 source checksums when Web Crypto is available
- Blocking errors and review warnings
- Typed `REPLACE` confirmation for destructive replacement
- Automatic downloadable safety backup before replace mode
- Restore preflight records and receipts
- Before/after collection counts and post-restore integrity verification
- Synthetic migration validation across v0.1.x through v0.9.4-shaped project records

The original stable local-storage keys remain unchanged:

```text
scLabProjectsV010
scLabActiveProjectV010
```

## New project collections

```text
reportDrafts
reportRevisions
reportPackages
restorePreflights
restoreReceipts
accessibilityAudits
migrationValidationRecords
```

## New contracts

```text
contracts/report-composition.schema.json
contracts/restore-validation.schema.json
contracts/accessibility-audit.schema.json
```

## Compatibility

The release preserves:

- `sustainable-catalyst-lab/sustainable-catalyst-lab.php`
- `[sc_lab_app]`
- `[sc_lab_reports]`
- `[sc_lab_report_studio]`
- Report API and Decision Studio packet contracts introduced in v0.9.4
- Existing compute, code switching, visualizations, dimensional scenes, projects, notes, observations, exports, and workspace backups

## Housekeeping

Python bytecode and pytest caches are removed from the repository and excluded through `.gitignore`. The installer uses `~/Downloads/sc-lab-v095-node`, without a leading period, so npm receives a valid package name.
