# Sustainable Catalyst Lab v0.5.0

Sustainable Catalyst Lab is a modular, substance-first scientific workspace for WordPress. Version 0.5.0 adds a first-class Biology and Computational Biology Laboratory while preserving the live scientific data, chemistry, spectrometry, physics, project, notebook, and documentation systems introduced in earlier releases.

## Major scientific modules

- Live Earth, natural-event, space, marine, PubMed, and arXiv signals.
- Climate and Earth-observation maps.
- Scientific Dataset Inspector and source registry.
- Complete 118-element periodic table.
- Chemistry Laboratory and reproducible Spectrometry Studio.
- Physics Laboratory with validation, visualization, uncertainty, particle physics, electromagnetism, circuits, quantum, and nuclear tools.
- Biology and Computational Biology Laboratory with forty methods across cellular systems, enzyme kinetics, genetics, sequence analysis, proteins, population genetics, ecology, physiology, and measurement.
- Experiments, evidence, hypotheses, decisions, notebook records, project activity, and data-connected documentation.

## Biology v0.5.0 additions

- DNA/RNA composition, reverse complement, transcription, translation, ORF finding, motif search, and k-mer profiling.
- Needleman–Wunsch global alignment and Smith–Waterman local alignment with browser-size limits.
- Primer screening, qPCR ΔΔCt, gel migration, consensus sequences, and genetic count chi-square.
- Protein mass, composition, hydropathy profiles, membrane-segment screening, and approximate isoelectric point.
- Michaelis–Menten, Hill response, and simplified competitive, noncompetitive, uncompetitive, and mixed inhibition models.
- Hardy–Weinberg frequencies, one-generation selection, drift expectations, and Jukes–Cantor distance.
- Shannon and Simpson diversity, logistic growth, Lotka–Volterra simulation, mark–recapture, and allometric scaling.
- Diffusion, osmosis, membrane Nernst potential, microbial growth, cardiac output, oxygen content, and dose-response tools.
- Serial dilution, CFU estimation, deterministic bootstrap intervals, eight numerical benchmarks, validation warnings, project records, and notebook routing.

## Installation

Upload `sustainable-catalyst-lab-plugin-v0.5.0.zip` through **Plugins → Add New → Upload Plugin**, replace the current plugin, activate it, and keep this shortcode on the Lab page:

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
[sc_lab_biology]
```

## Compatibility

The original browser-storage keys remain unchanged. Projects from v0.1.x through v0.4.1 are normalized in place to schema version `0.5.0`. No destructive migration is performed.

## Scientific boundaries

The Biology Laboratory supports research planning, education, exploratory analysis, and reproducible computational workflows. Sequence screening, primer estimates, protein-property estimates, population models, physiological calculations, and biological validation states do not constitute clinical, diagnostic, biosafety, taxonomic, ecological, or regulatory certification. Results require appropriate controls, validated methods, calibrated instruments, authoritative databases, uncertainty analysis, and qualified review.
