# Sustainable Catalyst Lab v0.14.0 — Urban Planning and Spatial Systems

Version 0.14.0 adds a first-class Urban Planning and Spatial Systems workspace with 48 auditable methods and 21 deterministic browser benchmarks.

## Workspaces

- Land use and development
- Accessibility and mobility
- Networks and spatial systems
- GIS and spatial analysis
- Public services and infrastructure planning
- Urban resilience, equity, and scenario analysis

## Capabilities

The release covers density, floor area ratio, land-use mix, jobs-housing balance, development capacity, impervious cover, open space, weighted travel time, cumulative and gravity accessibility, transit frequency, walksheds, intersection density, mode share, vehicle distance, network circuity and connectivity, geodesic distance, projected-area calculations, point density, suitability analysis, NDVI, NDBI, spatial entropy, location quotients, school and facility capacity, park access, district water and wastewater, solid waste, emergency response, infrastructure cost, heat-island intensity, tree canopy, community carbon, flood exposure, housing cost burden, displacement risk, population growth, and weighted scenario comparison.

## Integration

The release uses standalone WordPress integration and REST proxy classes:

- `includes/class-sc-lab-urban-planning-spatial.php`
- `includes/class-sc-lab-urban-planning-spatial-rest.php`

Focused shortcode:

`[sc_lab_urban_planning_spatial]`

The main `[sc_lab_app]` interface also receives the Urban Planning and Spatial Systems module.

## Project records

The project schema advances to `0.14.0` and adds:

- `urbanPlanningSpatialAnalyses`
- `urbanSpatialRecords`
- `urbanPlanningValidationRecords`
- `landUseRecords`
- `accessibilityRecords`
- `mobilityRecords`
- `spatialNetworkRecords`
- `gisAnalysisRecords`
- `publicServiceRecords`
- `urbanResilienceRecords`
- `spatialScenarioRecords`

## Responsible-use boundary

These methods support transparent screening, education, scenario comparison, and reproducible planning analysis. They do not replace adopted plans, legal zoning interpretation, official demographic forecasts, calibrated travel-demand models, professional GIS workflows, infrastructure engineering, environmental review, public engagement, permitting, or qualified planning and design judgment.
