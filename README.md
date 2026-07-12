# Sustainable Catalyst Lab v0.4.1

Sustainable Catalyst Lab is a modular, substance-first scientific workspace for WordPress. Version 0.4.1 strengthens the Physics Laboratory with explicit method metadata, domain validation, numerical benchmark cases, improved plots, comparison baselines, uncertainty propagation, and reproducible validation records.

## Major scientific modules

- Live scientific signals from Earth, natural-event, space, marine, PubMed, and arXiv sources.
- Climate and Earth-observation map workspace.
- Scientific Dataset Inspector and source registry.
- Complete 118-element periodic table.
- Chemistry Laboratory with composition, reactions, solutions, acid–base, thermochemistry, electrochemistry, kinetics, and calibration.
- Spectrometry Studio with raw-data preservation, baseline correction, smoothing, normalization, derivatives, conversions, peak characterization, calibration, plotting, and export.
- Physics Laboratory covering mechanics, waves, thermodynamics, fluids, optics, electromagnetism, circuits, quantum physics, nuclear physics, particle physics, detectors, and measurement.
- Experiments, evidence, hypotheses, decisions, notebook records, project activity, and data-connected documentation.

## Physics v0.4.1 additions

- Method registry with equations, SI/natural-unit declarations, assumptions, and output descriptions.
- Per-run validation states: `VALIDATED`, `WARNING`, and `INVALID`.
- Physical-domain checks for trajectory angles, pendulum amplitude, ideal-gas limits, relativistic speeds, detector time of flight, waveguide cutoff, quantum numbers, binding energy, and other method boundaries.
- Nine deterministic benchmark cases spanning mechanics, electromagnetism, circuits, photon physics, nuclear decay, and particle decay.
- Improved accessible SVG plots with grid lines, axes, zero lines, logarithmic frequency support, legends, baseline comparison, SVG export, and CSV export.
- Power-law uncertainty propagation.
- Uncertainty-weighted mean, chi-square, reduced chi-square, and Birge ratio.
- Project collection for validation reports.

## Installation

Upload `sustainable-catalyst-lab-plugin-v0.4.1.zip` through **Plugins → Add New → Upload Plugin**, replace the current plugin, activate it, and keep this shortcode on the Lab page:

```text
[sc_lab_app]
```

Focused interfaces remain available:

```text
[sc_lab_periodic_table]
[sc_lab_stoichiometry]
[sc_lab_spectrometry]
[sc_lab_climate_map]
[sc_lab_physics]
```

## Compatibility

The original browser-storage keys remain unchanged. Projects from v0.1.x through v0.4.0 are normalized in place to schema version `0.4.1`. No destructive migration is performed.

## Scientific boundaries

Validation in this release tests numerical implementation and stated model constraints. It does not certify experimental apparatus, engineering safety, radiation practice, high-voltage systems, RF exposure, regulatory compliance, or fitness for safety-critical use. Results require review against accepted methods, calibrated instruments, uncertainty budgets, source data, and qualified professional judgment where applicable.
