# Universal Visualization and Export

Version 0.9.1 introduces a shared analytical result contract and export engine. Individual discipline tools do not implement their own download logic. The application captures completed calculations, normalizes them into `sc-lab-analysis/1.0`, infers a chart specification, and attaches the same export toolbar.

## Outputs

- Accessible SVG with title and description
- High-resolution browser-generated PNG
- Single-figure PDF containing a rasterized high-resolution figure
- CSV chart data
- Structured analysis JSON
- Analysis-package ZIP containing JSON, SVG, PNG, PDF, CSV, audit metadata, and a Decision Studio packet
- Project visualization record
- Notebook entry
- Decision Studio packet

The PDF in v0.9.1 is a single-figure export. Structured multi-page reports remain a later Decision Studio and reporting release.

## Automatic capture

Buttons whose data attribute ends in `Run` are captured after execution. The capture adapter records visible form inputs, the structured result, equation text, assumptions, validation state, existing SVG output, project identity, and fingerprints.

## Themes

Scientific Light, Institutional, Publication, Scientific Dark, and Accessibility themes are available. SVG remains the canonical visual representation. PNG and PDF derive from the same SVG so figure content remains consistent across formats.

## Analysis packages

An analysis package contains:

```text
analysis.json
chart.svg
chart.png
analysis.pdf
chart-data.csv
audit.json
decision-studio-packet.json
scene.json                 # when a 3D or 4D scene is present
README.md
```
