# Sustainable Catalyst Lab v0.4.0

A modular, substance-first scientific workspace for WordPress. Lab coordinates scientific observations, calculations, experiments, evidence, notebooks, datasets, and data-connected technical documentation while routing deeper work into Sustainable Catalyst Prototyping Workbench, Decision Studio, and Site Intelligence.

## Major laboratory modules

- Live scientific observation board with USGS, NASA EONET, NASA space releases, OBIS, PubMed, and arXiv connectors.
- NASA GIBS climate and Earth-observation map workspace.
- Scientific Dataset Inspector with CSV/JSON import, filtering, summaries, plots, and project export.
- Chemistry Laboratory with the complete periodic table, composition, reactions, solutions, acid–base chemistry, thermochemistry, electrochemistry, kinetics, analytical calibration, and Spectrometry Studio.
- Physics Laboratory with mechanics, waves, thermodynamics, fluids, optics, electromagnetism, circuits, quantum physics, nuclear physics, particle physics, detector analysis, and uncertainty.
- Browser-local projects, observations, evidence, hypotheses, decisions, experiments, notebook entries, calculations, activity, and structured documentation.

## Physics v0.4.0

The Physics Laboratory includes 35 numerical methods and a structured 20-record particle reference. Major capabilities include:

- Uniform acceleration, projectile trajectories, pendula, springs, waves, acoustics, ideal gases, fluid flow, and Bernoulli analysis.
- Refraction, thin lenses, diffraction, photon quantities, and optical records.
- Coulomb interactions, multiple-charge electric fields, capacitor networks, magnetic fields, Lorentz motion, induction, electromagnetic propagation, skin depth, and waveguide cutoff.
- Series RLC analysis, AC power, resonance sweeps, and RC filter response.
- de Broglie wavelengths, particle-in-a-box levels, tunneling estimates, and hydrogen transitions.
- Radioactive decay, activity, nuclear mass defect, and binding energy.
- Relativistic kinematics, invariant-mass reconstruction, two-body decays, track momentum, time of flight, event significance, and cross-section estimates.

## Installation

Upload `sustainable-catalyst-lab-plugin-v0.4.0.zip` through **Plugins → Add New Plugin → Upload Plugin**, replace the prior version, activate it, and retain this page shortcode:

```text
[sc_lab_app]
```

Focused interfaces are also available:

```text
[sc_lab_periodic_table]
[sc_lab_stoichiometry]
[sc_lab_spectrometry]
[sc_lab_climate_map]
[sc_lab_physics]
```

## Project compatibility

The browser storage keys introduced in v0.1.0 remain unchanged. Existing projects are normalized non-destructively to schema version `0.4.0` and gain these collections:

```text
physicsRecords
waveforms
circuitAnalyses
fieldModels
particleEvents
detectorAnalyses
nuclearRecords
opticalAnalyses
```

## Scientific boundaries

The Lab supports research, education, exploratory analysis, and early prototyping. Numerical results, field models, circuit models, radiation calculations, detector analyses, and generated documentation require validation against authoritative sources, calibrated instruments, accepted uncertainty methods, applicable standards, and qualified professional review where appropriate.
