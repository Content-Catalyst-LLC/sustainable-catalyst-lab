# Sustainable Catalyst Lab v0.28.1 — Dataset Registry and Scientific Data Management

v0.28.1 adds a browser-local, project-scoped dataset registry on top of the v0.28.0 workspace architecture.

## Dataset records

Each registered dataset can contain a data dictionary, variable units and roles, validation state, browser and Python profile statistics, source and license metadata, provenance, and derived-from relationships.

## Import support

- CSV: parsed in the browser
- JSON records: parsed in the browser
- GeoJSON FeatureCollection: feature properties are tabularized and geometry metadata is preserved
- NetCDF: metadata-only registration in this release
- Existing Lab tabular datasets: normalized into the registry

The browser registry does not upload project datasets automatically. The Python Compute Core accepts bounded inline rows for governed profiling, but it is not the permanent dataset database.
