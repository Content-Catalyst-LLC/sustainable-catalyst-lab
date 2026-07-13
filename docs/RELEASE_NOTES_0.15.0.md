# Sustainable Catalyst Lab v0.15.0 — Sustainable Cities and Urban Resilience

Version 0.15.0 adds a first-class Sustainable Cities and Urban Resilience workspace with 48 auditable methods and 22 deterministic browser benchmarks.

It also repairs the Civil Engineering and Infrastructure Systems interface. The civil catalog already contained all 48 formulas, but its original v0.12 browser module depended on fragile central enqueue and initialization hooks. v0.15.0 adds a standalone, self-registering repair layer that:

- loads on both `[sc_lab_app]` and `[sc_lab_civil_infrastructure]`
- auto-initializes every civil workspace mount
- overrides the earlier fragile focused shortcode at late priority
- displays the named engineering formula prominently
- displays each executable output expression and unit
- validates that every one of the 48 civil methods has a formula and output expression
- preserves project, notebook, visualization, and validation handoffs

## Sustainable Cities workspaces

- Urban metabolism and resource flows
- Climate mitigation and decarbonization
- Climate adaptation and hazards
- Infrastructure resilience and continuity
- Equity and social resilience
- Integrated scenarios and governance

## Focused shortcodes

- `[sc_lab_sustainable_cities_resilience]`
- `[sc_lab_civil_infrastructure]`

The main `[sc_lab_app]` interface receives the Sustainable Cities module and the Civil formula-interface repair automatically.

## Project schema

The project schema advances to `0.15.0` and adds:

- `sustainableCitiesResilienceAnalyses`
- `sustainableCityResilienceRecords`
- `sustainableCitiesValidationRecords`
- `urbanMetabolismRecords`
- `decarbonizationRecords`
- `climateAdaptationRecords`
- `infrastructureContinuityRecords`
- `socialResilienceRecords`
- `cityScenarioRecords`

## Responsible-use boundary

The Sustainable Cities methods support transparent screening, education, comparative analysis, documentation, and scenario design. They do not replace adopted plans, official inventories, calibrated hazard and travel models, infrastructure engineering, public-health or clinical assessment, environmental review, public engagement, legal requirements, or qualified professional judgment.

The Civil methods remain screening tools and do not replace design codes, site investigation, calibrated engineering models, detailed load combinations, permitting, inspection, construction documents, or licensed engineering judgment.
