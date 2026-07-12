# Sustainable Catalyst Lab v0.8.0

Sustainable Catalyst Lab is a modular, substance-first scientific workspace for WordPress. Version 0.8.0 adds a first-class **Earth, Climate, Ocean, and Marine Systems Laboratory** while preserving the scientific feeds, climate maps, chemistry, spectrometry, physics, biology, astronomy, materials, project, experiment, notebook, and data-connected documentation systems introduced in earlier releases.

## Earth Systems Laboratory

The new laboratory contains ten connected work areas:

- Solid Earth and geophysics
- Atmosphere and meteorology
- Climate analysis
- Hydrology and groundwater
- Physical oceanography
- Marine systems and ecology
- Remote sensing
- Natural and environmental hazards
- Carbon cycle and stock accounting
- Numerical validation

The release includes 83 browser-based analytical methods and 12 deterministic benchmark cases. Analyses can be saved to Earth-specific project collections, added to the notebook, linked to experiments, routed into generated documentation, and used alongside existing feed, map, observation, and dataset records.

## Representative methods

- Plate-motion displacement, seismic moment, moment magnitude, earthquake energy, geothermal gradient, lithostatic pressure, and Airy isostasy
- Barometric pressure, hypsometric thickness, dry-adiabatic change, vapor pressure, relative humidity, dew point, potential temperature, wind power, CO₂ forcing, and atmospheric scale height
- Climate anomalies, linear trends, heating and cooling degree days, forcing-based warming, planetary equilibrium temperature, carbon-budget duration, aridity, and steric sea-level change
- Catchment water balance, rational runoff, Manning discharge, Darcy flow, aquifer storage, Horton infiltration, Gumbel return levels, sediment transport, reservoir residence, groundwater velocity, and soil-water storage
- Seawater density screening, hydrostatic pressure, deep- and shallow-water waves, tsunami travel, mixed-layer heat, geostrophic velocity, Ekman transport, salinity mixing, and dissolved-oxygen inventory
- Marine diversity, species-area scaling, Q10 metabolism, trophic transfer, fishery balance, primary production, benthic flux, occupancy detection, eDNA decay, and bioaccumulation
- NDVI, NDWI, NBR, EVI, broadband albedo, brightness temperature, TOA reflectance, classification metrics, mapped area, radiometric calibration, and emissivity-corrected surface temperature
- Hazard recurrence, landslide factor of safety, ash settling, wind-driven surge setup, coastal runup, advection-dispersion, and spill-area screening
- Atmospheric CO₂ mass change, emissions-to-ppm conversion, ecosystem and soil carbon stocks, sequestration, methane CO₂-equivalent, and ocean carbon flux

## WordPress installation

Upload `sustainable-catalyst-lab-plugin-v0.8.0.zip` through **Plugins → Add New Plugin → Upload Plugin**, replace the current plugin, activate it, and keep this shortcode on the Lab page:

```text
[sc_lab_app]
```

A focused Earth Systems Laboratory shortcode is also available:

```text
[sc_lab_earth_systems]
```

## Project compatibility

The original browser-storage keys remain unchanged. Projects from v0.1.x through v0.7.0 are normalized in place to schema version `0.8.0`. No destructive migration is performed.

## Validation

Run:

```bash
chmod +x scripts/test_release.sh
./scripts/test_release.sh
```

The release suite validates PHP and JavaScript syntax, WordPress template rendering, the periodic table, chemistry, spectrometry, physics, biology, astronomy, materials, Earth systems methods, deterministic benchmark cases, project collections, and schema migration.

## Review boundary

The Earth Systems Laboratory supports research, education, screening calculations, experiment planning, environmental observation, and technical documentation. Results do not replace authoritative climate products, calibrated field measurements, TEOS-10 oceanographic calculations, geotechnical or coastal engineering analysis, regulatory assessments, operational forecasting, or professional scientific review.
