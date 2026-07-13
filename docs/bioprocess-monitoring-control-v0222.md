# Bioprocess Monitoring, Control, and Visualization

Sustainable Catalyst Lab v0.22.2 adds operational time-series analysis above the validated v0.22.0 scientific engine and v0.22.1 production activation layer.

## Capabilities
- Eight standard process channels
- CSV time-series import and sample datasets
- Rolling mean, sample standard deviation, and CV
- Low/high limit, rate-of-change, missing-data, and rolling-CV flags
- Process phase markers
- Native SVG trend charts
- PID-style simulations for six common controller contexts
- Multi-run comparison with mean, final value, range, and area under the curve
- JSON exports and v0.21.3 provenance handoff
- WordPress and FastAPI routes

## Endpoints
`GET /wp-json/sc-lab/v1/compute/bioprocess/monitoring/profiles`
`POST /wp-json/sc-lab/v1/compute/bioprocess/monitoring/analyze`
`POST /wp-json/sc-lab/v1/compute/bioprocess/control/simulate`
`POST /wp-json/sc-lab/v1/compute/bioprocess/monitoring/compare`

FastAPI uses the equivalent `/v1/bioprocess/...` paths.

## Boundary
The module does not control equipment, validate sensors, establish GMP compliance, or replace qualified operators and controlled procedures.
