# Sustainable Catalyst Lab v0.26.4 — Cross-Laboratory Functional Validation

v0.26.4 adds a browser-driven functional-health system. It loads each laboratory in the same isolated single-panel lifecycle used by the public Lab, confirms the panel and controller, invokes a safe primary action where available, inspects the rendered result, and captures runtime errors.

## Status model

- `functional`: panel, controller, action, and output passed.
- `functional_with_errors`: result passed but runtime errors were captured.
- `external_source_unavailable`: the interface worked but an upstream source did not.
- `backend_required`: the interface requires an optional backend or feature.
- `panel_missing`, `controller_missing`, `action_missing`, `output_missing`: activation defects.
- `calculation_failed`, `result_not_observed`: functional defects.

## Admin workflow

Open **Settings → Lab Functional Health**. Run the priority suite or all 41 panels. The resulting report is saved in WordPress and can be exported as JSON. Each check runs in a separate same-origin frame so module state and errors do not leak between laboratories.

## REST endpoints

- `/wp-json/sc-lab/v1/functional/v0264/registry`
- `/wp-json/sc-lab/v1/functional/v0264/server-health`
- `/wp-json/sc-lab/v1/functional/v0264/reports/latest` (administrator)
