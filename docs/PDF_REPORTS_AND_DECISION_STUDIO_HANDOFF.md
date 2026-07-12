# PDF Reports and Decision Studio Handoff

## Shared report architecture

Version 0.9.4 uses one structured report contract across the browser, WordPress proxy, Render service, project records, downloadable JSON, and Decision Studio handoff.

```text
Scientific calculation
→ sc-lab-analysis/1.0
→ sc-lab-report/1.0
├── browser selectable-text PDF
├── Render ReportLab vector PDF
├── project report record
└── Decision Studio packet 2.0
```

## Report contract

A report contains:

- report identity, type, title, subtitle, and page size
- project context
- executive summary
- one to twelve structured analyses
- figure and table references
- audit configuration and deterministic fingerprint

Each analysis can include:

- method and version
- domain and validation state
- equation or method statement
- nested inputs and outputs with units
- chart specification and source data
- assumptions, warnings, sources, and evidence
- validation details
- code and runtime metadata
- analysis audit fingerprints
- optional dimensional-scene references

## PDF engines

### Browser engine

The browser engine creates a downloadable PDF without requiring the Render backend. Text remains selectable and the report contract can be exported alongside it.

### Render engine

The Render engine uses ReportLab to compose multi-page PDFs with vector tables and charts. It returns:

```text
status
filename
mimeType
byteLength
pageCount
reportFingerprint
pdfFingerprint
engine
dataBase64
```

## Figure behavior

The backend currently renders line, scatter, and bar specifications directly as vector PDF drawings. Existing SVG, PNG, dimensional scene, and analysis-package exports remain available through Visualization Studio. Decision Studio packets retain both rendered figures and their underlying chart or scene specifications.

## Decision Studio packet 2.0

The packet schema supports:

```text
scientific-analysis
scientific-report
```

A report handoff can preserve:

- origin application and version
- report contract
- all selected analyses
- figures and chart specifications
- structured tables
- projected 3D/4D scenes and original vertices/edges
- evidence and sources
- claims, assumptions, uncertainties, and warnings
- validation and review states
- runtime and language information
- project and audit metadata

## WordPress proxy

The browser calls same-origin WordPress REST routes. WordPress sanitizes and bounds the payload, then sends it to Render with the server-side API key. The key is never localized into the public application.

## Project records

```text
reports
reportFigures
reportExports
decisionStudioHandoffs
```

Reports and handoffs can be restored through the existing project and workspace backup system. Reset scopes include these collections when analysis history or the full workspace is cleared.

## Validation expectations

- Report title and at least one analysis are required.
- A report can contain at most twelve analyses.
- Page size must be LETTER or A4.
- Report type must be one of the four registered values.
- Every analysis must include `methodId` and object-shaped inputs.
- Handoff packets are capped at two megabytes.
- Backend PDFs receive deterministic report and PDF fingerprints.
- Generated reports preserve the supplied audit record but do not independently certify the interpretation.
