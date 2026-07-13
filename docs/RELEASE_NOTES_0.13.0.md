# Sustainable Catalyst Lab v0.13.0 — Architecture and Building Performance

Version 0.13.0 adds a first-class Architecture and Building Performance workspace with 48 auditable methods and 19 deterministic browser benchmarks.

## Workspaces

- Geometry and program
- Envelope and thermal performance
- Solar and daylight systems
- Ventilation and indoor environmental quality
- Building energy and HVAC
- Water, carbon, acoustics, and passive resilience

## Integration

The release uses standalone WordPress integration and REST proxy classes rather than extending the central Lab plugin and REST classes. This reduces release coupling and makes future domain overlays less dependent on the internal layout of earlier versions.

Focused shortcode:

`[sc_lab_architecture_building]`

The main `[sc_lab_app]` interface also receives the Architecture and Building Performance module.

## Analysis records

The release adds project collections for:

- `architectureBuildingAnalyses`
- `buildingPerformanceRecords`
- `buildingPerformanceValidationRecords`
- `buildingEnvelopeRecords`
- `daylightRecords`
- `indoorEnvironmentalQualityRecords`
- `buildingEnergyRecords`

## Responsible-use boundary

The methods are transparent screening and educational calculations. They do not replace whole-building simulation, calibrated energy models, hygrothermal analysis, daylight or glare simulation, detailed acoustic models, code compliance, commissioning, field verification, permitting, or licensed architectural and engineering judgment.
