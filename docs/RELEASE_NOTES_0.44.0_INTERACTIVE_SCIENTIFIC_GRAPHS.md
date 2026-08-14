# Sustainable Catalyst Lab v0.44.0

## Interactive Scientific Graph Engine & Publication Graphics

Lab v0.44.0 promotes scientific visualization from a static rendering layer into a shared interactive research instrument used by Model Studio and Numerical Visualization. The release preserves the existing governed modeling, diagnostics, comparison, uncertainty, provenance, and platform-compatibility boundaries while improving how scientific evidence can be inspected and exported.

### Shared Scientific Visualization Engine v0.44.0

- wheel and toolbar zoom
- drag panning
- keyboard pan, zoom, and reset
- crosshair coordinate inspection
- focusable scatter points and hover details
- click-to-hide / restore series
- numerical axes, gridlines, legends, and responsive SVG
- confidence ribbons from `yLow` / `yHigh` point bounds
- vertical error bars from `yLow` / `yHigh` point bounds
- vertical and horizontal reference annotations plus point markers
- accessible data-table fallback

### Publication graphics

Model Studio now exposes publication metadata for subtitle, caption, source, method, notes, aspect ratio, grid visibility, and legend visibility. The renderer provides local export controls for SVG, high-resolution 2× PNG, CSV, and JSON. The export workflow does not require an external charting service and does not upload figure data.

### Contract changes

- `sc-lab-model-studio-model/0.44.0`
- `sc-lab-scientific-graph/0.44.0`
- `sc-lab-model-studio-bundle/0.44.0`
- `sc-lab-model-studio-policy/0.44.0`
- publication figure schema v0.44.0

The v0.43 diagnostics, cross-validation, and scientific model-comparison contracts remain compatible. The v0.42 safe equation grammar remains the declarative execution boundary.

### Security and governance boundaries

- arbitrary code: disabled
- arbitrary Python / JavaScript / shell execution: disabled
- arbitrary-formula fitting: disabled
- safe declarative expression preview: enabled
- registered calibration forms: enabled
- browser-local figure export: enabled
- platform compatibility: 1.0.0
- WordPress feature release: 0.44.0
