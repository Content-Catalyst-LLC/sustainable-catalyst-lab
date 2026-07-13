# Sustainable Catalyst Lab v0.20.0 — Microbiology Laboratory

Version 0.20.0 adds a first-class Microbiology Laboratory with 48 auditable methods and 48 deterministic browser benchmarks.

## Workspaces

- Microbial growth and population dynamics
- Culture systems and bioreactor kinetics
- Enumeration, microscopy, and assay quantification
- Environmental and food microbiology
- Antimicrobial and disinfection screening
- Microbial ecology and laboratory quality control

## Capabilities

The release covers exponential, logistic, and first-order population models; observed growth rates and generation times; chemostat dilution, residence time, Monod kinetics, washout margin, productivity, yield, and oxygen uptake; CFU, PFU, serial dilution, hemocytometer counts, viability, optical-density calibration, assay recovery, and Z-prime; environmental decay, log reduction, removal, surface loading, biofilm density, oxygen demand, Q10 adjustment, and source contribution; MIC fold change, fractional inhibitory concentration, time-kill change, D-value, z-value, CT, disinfectant decay, and normalized inhibition zones; relative abundance, Shannon and Simpson diversity, Bray–Curtis dissimilarity, qPCR efficiency, A260 concentration, replicate variation, and contamination rates.

## Formula-visible interface

Every method displays:

- a human-readable microbiology or laboratory equation
- every executable output expression
- input labels and units
- output labels and units
- assumptions and laboratory-screening warnings
- deterministic validation and audit metadata
- project, notebook, and visualization handoffs

## Focused shortcode

`[sc_lab_microbiology_laboratory]`

The main `[sc_lab_app]` interface also receives the workspace.

## Project schema

The project schema advances to `0.20.0` and adds:

- `microbiologyAnalyses`
- `microbiologyRecords`
- `microbiologyValidationRecords`
- `microbialGrowthRecords`
- `cultureKineticsRecords`
- `enumerationMicroscopyRecords`
- `environmentalMicrobiologyRecords`
- `antimicrobialScreeningRecords`
- `microbialEcologyRecords`
- `microbiologyAssayRecords`
- `microbiologyQcRecords`

## Responsible-use boundary

These methods support education, environmental and industrial research, laboratory documentation, quality control, and reproducible analysis. They do not replace validated laboratory protocols, biosafety review, organism-specific risk assessment, accredited testing, clinical diagnosis, treatment selection, public-health decisions, or qualified microbiology and laboratory judgment.
