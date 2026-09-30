# Lab v0.152.0.7 — Interactive 4D Scientific Front Door & Compute Runtime Reconnection

## Purpose
Restore the four-dimensional scientific front door as a bounded first-class Lab runtime without reactivating the historical all-at-once JavaScript fleet.

## Runtime architecture
- Retains the v0.152.0.6 safe navigation shell and full-panel DOM.
- Allows exactly two executable Lab front-door scripts: the v0.152.0.7 safe shell and the v0.152.0.7 bounded 4D runtime.
- Keeps the v0.152.0.4 optional mega-bundle, legacy individual modules, v0.48 presentation runtime, and v0.26.6 production-budget monitor out of the canonical front-door execution path.
- Connects directly to existing WordPress proxy routes for Python Compute Core health, capabilities, and registered compute execution.

## 4D functionality
The landing visualization provides W hyperslicing, XW/YW 4D-plane rotation, animated W sweep, projected tesseract context, vector, uncertainty and contour overlays, pointer inspection, PNG export and reproducible JSON state export. Six bounded browser demonstrations are provided: nonlinear response, dynamic system, uncertainty, sensitivity, ensemble and spatiotemporal fields.

## Compute-backed mode
`Run compute sweep` explicitly invokes the registered `simulation.parameter_sweep` Python method using the logistic-growth model. Returned sweep rows are normalized into the fourth-dimension response mapping. Compute is never launched merely by opening the Lab page. Health and capability checks are read-only.

## Scientific boundary
Browser demonstrations are illustrative. The compute-backed sweep is a real registered computation, but its 4D surface is a visualization mapping rather than observational evidence, causal proof, scientific validation, or a forecast.
