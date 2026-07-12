# Sustainable Catalyst Lab v0.7.0

Sustainable Catalyst Lab is a modular, substance-first scientific workspace for WordPress. Version 0.7.0 adds a first-class **Materials Science and Characterization Laboratory** while preserving the scientific feeds, climate maps, chemistry, spectrometry, physics, biology, astronomy, project, experiment, notebook, and data-connected documentation systems introduced in earlier releases.

## Materials Laboratory

The Materials Laboratory contains eleven work areas:

- Mechanical behavior
- Thermal transport and calorimetry
- Electrical and dielectric properties
- Magnetic behavior
- Optical characterization
- Crystallography and X-ray diffraction
- Phase analysis and diffusion
- Corrosion and electrochemistry
- Polymers
- Composites
- Microscopy and image-derived measurements
- Numerical validation

The release includes 49 analytical methods and 10 deterministic benchmark cases. Analyses can be saved to materials-specific project collections, added to the notebook, included in generated documentation, and connected to experiments.

## Representative methods

- Engineering and true stress–strain relations
- Elastic-constant conversion, resilience, fracture intensity, fatigue, and creep
- Thermal expansion, conduction, diffusivity, thermal-shock screening, and DSC integration
- Resistivity, Hall effect, dielectric capacitance, and intrinsic carrier density
- Curie–Weiss susceptibility, magnetic moment, hysteresis loss, and energy product
- Optical reflectance, absorption coefficient, Tauc band-gap fitting, and optical path length
- Bragg spacing, cubic lattice analysis, Scherrer crystallite size, and crystal density
- Lever rule, Gibbs phase rule, Arrhenius diffusion, and diffusion length
- Weight-loss corrosion, Faradaic penetration, and Stern–Geary current density
- Polymerization, glass-transition blending, DSC crystallinity, viscoelastic relaxation
- Composite rule-of-mixtures, Halpin–Tsai modulus, and density
- Particle statistics, area fraction, grain intercept, spatial calibration, and Abbe resolution

## WordPress installation

Upload `sustainable-catalyst-lab-plugin-v0.7.0.zip` through **Plugins → Add New Plugin → Upload Plugin**, replace the current plugin, activate it, and keep this shortcode on the Lab page:

```text
[sc_lab_app]
```

A focused Materials Laboratory shortcode is also available:

```text
[sc_lab_materials]
```

## Project compatibility

The original browser-storage keys remain unchanged. Projects from v0.1.x through v0.6.0 are normalized in place to schema version `0.7.0`. No destructive migration is performed.

## Validation

Run:

```bash
chmod +x scripts/test_release.sh
./scripts/test_release.sh
```

The release suite validates PHP and JavaScript syntax, WordPress template rendering, the periodic table, chemistry, spectrometry, physics, biology, astronomy, materials methods, deterministic benchmark cases, project collections, and schema migration.

## Review boundary

The Materials Laboratory supports research, education, screening calculations, experiment planning, and technical documentation. Results do not replace calibrated instrument methods, certified mechanical testing, qualified microscopy, assessed phase-diagram databases, standards-based corrosion testing, or professional engineering review.
