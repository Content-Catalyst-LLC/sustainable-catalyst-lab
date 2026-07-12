# Sustainable Catalyst Lab v0.9.4
## PDF Reports and Decision Studio Handoff

Version 0.9.4 turns saved scientific analyses into structured, selectable-text PDF reports and formal Decision Studio handoff packets. It preserves the calculations, figures, equations, assumptions, warnings, validation, sources, code/runtime metadata, dimensional scenes, and audit fingerprints required to review how a report was produced.

## Report Studio

The new Report Studio can combine one to twelve analyses into:

- Technical reports
- Decision briefs
- Evidence packets
- Executive summaries

Controls include:

- Load the current calculation
- Select saved project analyses
- Compose and preview a report
- Edit title, subtitle, executive summary, type, and page size
- Include or omit the audit appendix
- Download a local browser PDF
- Request a Render vector PDF
- Export report JSON
- Export a Decision Studio packet
- Validate the report or handoff
- Save report, figure, and export records to the active project
- Send the complete structured packet to Decision Studio

## Two PDF engines

### Local browser PDF

The browser can create an immediate selectable-text PDF without the Render backend. This preserves local/offline operation and gives every supported calculation a report path.

### Render ReportLab PDF

The optional Render service creates a multi-page vector PDF containing:

- Cover metadata and executive summary
- Method identity and validation state
- Equations
- Nested input and output tables with units
- Vector line, scatter, and bar figures
- Assumptions
- Warnings and limitations
- Validation details
- Sources
- Code, compiler, runtime, and execution metadata
- Analysis and report audit fingerprints
- Page numbering and institutional report styling

The response includes report and PDF fingerprints, filename, byte length, page count, engine metadata, and base64 PDF content.

## Decision Studio handoff 2.0

The handoff schema advances to:

```text
sc-decision-studio-analysis-packet/2.0
```

The packet can retain:

- Full report contract
- Selected analyses
- Chart specifications and figure records
- Tables
- 3D and projected 4D scene specifications
- Evidence and sources
- Claims, assumptions, uncertainties, and warnings
- Validation and review state
- Language, compiler, runtime, and execution metadata
- Project context
- Deterministic packet and analysis fingerprints

Decision Studio receives structured content rather than only a screenshot.

## New endpoints

FastAPI:

```text
POST /v1/reports/validate
POST /v1/reports/pdf
POST /v1/handoffs/decision-studio/validate
```

Same-origin WordPress proxy:

```text
POST /wp-json/sc-lab/v1/compute/reports/validate
POST /wp-json/sc-lab/v1/compute/reports/pdf
POST /wp-json/sc-lab/v1/compute/handoffs/decision-studio/validate
```

The Render API key remains server-side in WordPress and is not exposed to browser JavaScript.

## New contracts and project records

Contracts:

```text
contracts/report.schema.json
contracts/report-result.schema.json
contracts/decision-studio-packet.schema.json
```

Project collections:

```text
reports
reportFigures
reportExports
decisionStudioHandoffs
```

Projects from v0.1.x through v0.9.3 migrate non-destructively to schema version `0.9.4` using the original storage keys.

## Shortcodes

```text
[sc_lab_app]
[sc_lab_reports]
[sc_lab_report_studio]
```

Existing focused visualization, workspace-data, code-switcher, and discipline shortcodes remain available.

## Rendered-PDF validation correction

Visual inspection of a real multi-page report exposed a nested-field flattening defect that source-only tests did not reveal. The release now correctly renders nested input values, units, outputs, validation records, runtime metadata, and audit fields. Positive-only plots also retain a zero baseline instead of creating a misleading negative range.

## Validation completed

- PHP syntax and structural tests passed
- JavaScript syntax and numerical tests passed
- WordPress template rendering passed
- 24 backend compute and report tests passed
- Browser report-contract and PDF tests passed
- ReportLab PDF generation passed
- Report and PDF fingerprint generation passed
- Nested report-field regression test passed
- Report validation endpoint passed
- PDF endpoint and base64 round trip passed
- Decision Studio packet validation passed
- WordPress report-proxy markers passed
- Report shortcodes and template controls passed
- Project migration and new report collections passed
- 118 periodic-table elements retained
- 34 general scientific calculators retained
- 37 Physics methods retained
- 40 Biology methods retained
- 42 Astronomy methods retained
- 49 Materials methods retained
- 83 Earth Systems methods retained
- 119 Energy and Engineering methods retained
- 61 inherited discipline benchmarks passed
- Nineteen portable method contracts retained
- Generated Python, JavaScript, TypeScript, C, C++, Fortran, and Go checks passed
- 3D/4D visualization, workspace backup, reset, and restore regression tests passed
- A six-page sample PDF was rendered at 180 DPI and visually inspected for clipping, overlap, broken glyphs, table population, chart output, and page numbering

## Remaining live checks

A final WordPress and Render deployment check remains necessary for browser downloads, Report Studio selection behavior, larger report payloads, mobile layout, Astra interaction, backend cold starts, Decision Studio route behavior, and real project reports.
