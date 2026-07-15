## 0.28.1 — Dataset Registry and Scientific Data Management
- Dataset registry, data dictionaries, units, validation, source/license metadata, lineage, profiling, and import support.

## 0.28.0 — Project and Workspace Data Architecture
- Shared schema 0.28.0, canonical records, migration, search, relationships, checkpoints, and project bundles.

## 0.27.4.1 — WordPress Integrity Manifest Scope Repair

- Separates WordPress plugin integrity hashes from Python backend/source-bundle hashes.
- Prevents backend-only files from being reported as missing from the WordPress plugin ZIP.
- Preserves v0.27.4 scientific visualization and the deployed Python Compute Core unchanged.
- Adds explicit integrity scope and verified/excluded file counts to runtime health.

## 0.27.4 — Scientific Visualization for Numerical Results

- Added eight governed numerical visualization profiles.
- Added accessible SVG, PNG, CSV, and JSON result exports.
- Added uncertainty histograms, sensitivity tornado charts, parameter sweeps, spectra, convergence plots, and heatmaps.
- Added a dedicated WordPress Scientific Visualization workspace and backend visualization API.

# Changelog

## 0.27.3 — Numerical Precision and Solver Governance

- Added four precision profiles and user-selectable tolerance governance.
- Added automatic recommendations and registered manual solver selection.
- Added condition-number diagnostics and least-squares fallback for ill-conditioned systems.
- Added IEEE-754 binary64 reporting, convergence warnings, unit-aware validation, uncertainty standards, and reference-method comparisons.
- Added the Numerical Precision and Solver Governance Lab workspace and WordPress/Python health endpoints.

## 0.27.2 — Long-Running Numerical Jobs and Checkpoint Recovery

- Added checkpointed execution for parameter sweeps and bootstrap uncertainty runs.
- Added persisted partial results, checkpoint history, progress, ETA, pause, resume, and restart recovery.
- Added priority scheduling, project-level active-job limits, and deterministic result caching.
- Added queue schema 1.1, worker schema 1.1, and long-job result contract.
- Added Analyze → Long Jobs & Checkpoints and `[sc_lab_long_jobs]`.
- Preserved the 23-method registry, fourteen numerical benchmarks, HMAC authentication, and domain extensions.

## 0.27.1 — Numerical Validation and Benchmark Library

- Added a dedicated Numerical Validation Library under Analyze and the `[sc_lab_numerical_validation]` focused shortcode.
- Added fourteen governed known-answer benchmarks spanning root finding, quadrature, interpolation, ODE integration, eigen analysis, bounded and linear optimization, FFT recovery, Monte Carlo propagation, bootstrap stability, sensitivity analysis, parameter sweeps, linear systems, and sampled integration.
- Added exact, tolerance, residual, sequence, monotonicity, deterministic-seed, named-derivative, and unit-aware acceptance rules.
- Added convergence diagnostics for root-finding and ODE fixtures with tolerance-level error and runtime reporting.
- Added independent browser-reference comparisons for supported fixtures and retained Python Compute Core provenance for every result.
- Added benchmark catalog, selected-run, full-suite, convergence, health, report export, and WordPress proxy endpoints.
- Preserved all 23 registered backend methods, the persistent queue, v0.27.0 Numerical Methods Studio, and v0.26.6 production-recovery protections.

## 0.27.0 — Scientific Computing and Numerical Methods

- Added a dedicated Numerical Methods Studio under Analyze and the `[sc_lab_numerical_methods]` focused shortcode.
- Added twelve governed Python methods for bracketed root finding, adaptive quadrature, interpolation, first-order ODEs, eigen analysis, bounded optimization, linear programming, FFT spectra, Monte Carlo uncertainty propagation, bootstrap confidence intervals, local sensitivity, and parameter sweeps.
- Added automatic synchronous or persistent-queued execution through the existing Compute Core and v0.26.1 worker architecture.
- Added governed examples, JSON input and parameter editors, queue cancellation, project saving, accessible plots, raw result inspection, reproducibility provenance, and JSON export.
- Added numerical catalog, result, and health contracts plus method and backend validation.
- Added deterministic numerical benchmarks and preserved all v0.26.6 production-recovery, interface, feed, lifecycle, and functional-validation protections.
- Kept public arbitrary-code execution disabled and enforced registered-method, input-size, runtime, and worker boundaries.

## 0.26.6 — Production Stability and Recovery

- Added a true in-memory Safe Start that does not load or modify persisted projects.
- Added early project-storage validation, oversized-record detection, and session quarantine for damaged JSON.
- Added DOM, storage, JavaScript heap-growth, long-task, and runtime-error budgets.
- Added persistent compute-job tracking and reconciliation after page reload.
- Added backend interruption, offline, online, and automatic retry states.
- Added privacy-preserving incident bundle export.
- Added Settings → Lab Production Readiness with isolated lifecycle and repeated-switch stress tests.
- Added a versioned production-readiness report schema and REST health endpoints.

## 0.26.5 — Mobile, Accessibility, and Interface Reliability

- Added responsive phone, tablet, and landscape layouts across the isolated Lab lifecycle.
- Added 44-pixel touch targets, mobile navigation focus management, a navigation scrim, Escape-key close, and scroll locking.
- Added skip navigation, visible focus, keyboard tab navigation, accessible names, live regions, table semantics, dialog semantics, and visualization labels.
- Added reduced-motion, increased-contrast, forced-colors, and print reliability.
- Added Settings → Lab Interface Health with phone, tablet, and desktop audits and exportable `sc-lab-interface-health/1.0` reports.

# Changelog

## 0.26.4 — Cross-Laboratory Functional Validation

- Added browser-driven validation for all 41 laboratory panels.
- Added priority action/output checks for 14 core scientific and engineering laboratories.
- Added a Settings → Lab Functional Health dashboard with run, stop, export, and server-health controls.
- Added separate classifications for controller defects, calculation failures, optional backends, and unavailable scientific sources.
- Added saved JSON health reports and a versioned report schema.


## 0.26.3.4 — Scientific Feed Rendering and Observe Data Reliability

- Automatically runs the initial NASA and OBIS queries when their Observe panels mount.
- Adds visible loading, ready, empty, disabled, and source-error states so feed panels cannot appear blank.
- Adds a governed WordPress feed endpoint with connector diagnostics and cache-aware responses.
- Falls back to direct browser access for NASA Image Library and OBIS when WordPress outbound HTTP fails.
- Adds request timeouts, retry controls, source-health controls, and transparent proxy/direct mode labels.
- Improves upstream request retry behavior and release-aware user-agent metadata.
- Preserves dataset saving and provenance for both proxy and browser-direct records.

## 0.26.3.3 — Observe and Domain Module Activation Repair

- Adds a dedicated Observe controller for scientific feeds, Climate Maps, Space & Astronomy Observations, and Marine Biology.
- Stops the legacy global initializer from double-binding active Observe controls.
- Renames the Analyze route to Astronomy calculations and adds a canonical Astronomy observations route to Space observations.
- Adds explicit Microbiology dependencies, active-project injection, fallback mounting, and visible bootstrap errors.
- Fixes the v0.26.3 runtime error reporter typo that could throw while reporting a missing controller.
- Adds module-level readiness markers and a v0.26.3.3 activation health endpoint.
- Browser-validates Climate Maps, Marine Biology, Space observations, Astronomy calculations, and Microbiology calculations.

## 0.26.3.2 — Installation, Version, and Asset Integrity Patch

- Adds canonical plugin-path and bootstrap verification.
- Adds duplicate plugin-copy and partial-install detection.
- Adds a generated build manifest with source commit, build fingerprint, and critical SHA-256 hashes.
- Adds canonical `/wp-json/sc-lab/v1/runtime/health` and manifest endpoints.
- Applies SHA-256 query versions through loader filters instead of rewriting legacy asset methods.
- Unifies public plugin, release, panel-runtime, compute-core, and asset reporting.
- Adds route checks for Marine Biology, Climate Maps, and Evidence & Decisions.
- Adds explicit rollback guidance and idempotent installer recovery.

# Changelog

## 0.26.3.1 — Panel Alias and Compatibility Routing Repair

- Maps `marine` to `marine-biology`, `climate` to `climate-maps`, and `evidence` to `evidence-decisions`.
- Canonicalizes query URLs, navigation controls, and application module lookups.
- Suppresses only false compatibility warnings backed by the canonical module manifest.
- Keeps genuine missing-panel conditions in runtime diagnostics.
- Adds SHA-256 asset cache busting and duplicate-plugin-folder diagnostics.

## 0.26.3 — Cross-Laboratory Calculator Activation and Runtime Repair

- Fixes the missing-element select proxy so shared calculator initialization no longer stops on `HTMLSelectElement.add()`.
- Initializes domain controllers only when their active laboratory panel exists.
- Adds per-controller error boundaries so one module cannot prevent later laboratories from mounting.
- Adds the v0.26.3 runtime health endpoint, browser diagnostics API, and public plugin/asset version reporting.
- Uses file modification timestamps for cache-busting core and runtime assets.
- Adds resilient project storage with an in-memory fallback when browser storage is unavailable.
- Preserves isolated full-page module teardown to release listeners, timers, observers, workers, and chart state.
- Browser-validates Astronomy, Marine Biology, Earth Systems, Physics, Biology, and the shared calculator registry.

## 0.26.1 — Job Queue and Worker Reliability

- Replaces the process-local thread pool with a SQLite WAL-backed persistent queue.
- Runs calculations in isolated child processes for hard cancellation and timeout enforcement.
- Recovers interrupted `running` jobs to the queue when the same database reopens.
- Adds bounded retries, exponential backoff, manual retry, and structured failure records.
- Adds idempotency-key and active-request deduplication.
- Adds job listing, progress, queue status, and worker health endpoints.
- Adds a WordPress queue monitor and browser client methods for list, retry, cancel, queue status, and worker health.
- Adds deployment controls for worker count, queue capacity, retention, timeouts, and database location.
- Preserves the v0.26.0 registered-method, HMAC, provenance, report, handoff, and legacy-router contracts.

## 0.26.0 — Python Compute Core Foundation

- Promotes FastAPI/Python into the governed core compute plane.
- Adds canonical capability, method registry, method detail, and compute-run contracts.
- Adds HMAC-SHA256 request signing between WordPress and FastAPI.
- Adds deterministic provenance manifests with package versions and checksums.
- Adds ten registered foundation methods across mechanics, biology, energy, statistics, numerical analysis, and simulation.
- Preserves legacy execute, compare, report, handoff, job, and recovered domain-router compatibility.
- Adds a deployable Docker/Render backend, automated tests, and an extension failure boundary.

## 0.25.5 — Module Lifecycle and Memory Management

- Isolates the public application to one laboratory per browser lifecycle.
- Performs a complete browser teardown when switching laboratories.
- Adds lifecycle scopes for timers, animation frames, observers, listeners, abort controllers, and custom cleanup callbacks.
- Gates advanced module assets so inactive laboratories do not start observers or timers.
- Adds DOM and JavaScript heap diagnostics, duplicate-runtime protection, pagehide cleanup, and safe-start recovery.
- Makes the legacy application initializer null-safe when inactive panels are absent.

## 0.25.3 — Calibration, Validation, and Chain of Custody

- Added eight instrumentation validation profiles.
- Added eight acceptance states and eight deviation types.
- Added 16 deterministic calibration/readiness methods.
- Added SHA-256 component manifests.
- Added parent-linked custody events and tamper verification.
- Added calibration, maintenance, quality, and linkage review.
- Added weighted validation scores and release dispositions.
- Added exportable validation dossiers.
- Added WordPress and FastAPI validation/custody routes.
- Preserved explicit non-GMP and non-clinical boundaries.

## 0.25.2 — Live Sensor and Instrument Visualization

- Added eight live instrumentation visualization modes.
- Added 16 deterministic analysis methods and benchmarks.
- Added bounded multi-channel stream buffers.
- Added threshold, warning, action, and gap events.
- Added rolling statistics, smoothing, downsampling, alignment, and dashboard summaries.
- Added pause, replay, import, and connection-state flows.
- Added synchronized SVG dashboards and JSON/CSV/SVG exports.
- Added project, notebook, and provenance handoffs.
- Added WordPress and FastAPI live-analysis routes.
- Preserved explicit local-first and non-clinical boundaries.

## 0.25.1 — Instrumentation Production Reliability

- Added unconditional v0.25.0 asset activation.
- Added canonical instrumentation panel and root recovery.
- Added missing-panel/root creation and duplicate suppression.
- Added stale marker and placeholder cleanup.
- Added startup, navigation, history, focus, visibility, connectivity, resize, orientation, hash, and mutation recovery.
- Added browser repair/open/health/status APIs.
- Added WordPress and FastAPI production-health routes.
- Added mobile, output, and long-table reliability.
- Preserved 48 methods, 48 benchmarks, eight categories, nine record types, eight connection profiles, and eight quality flags.

## 0.25.0 — Laboratory Data and Instrumentation Platform

- Added 48 methods and 48 benchmarks across eight instrumentation categories.
- Added nine record types and eight connection profiles.
- Added normalized measurement ingestion and quality flags.
- Added SHA-256 record manifests and custody-chain verification.
- Added WordPress and FastAPI routes, UI, examples, and mobile reliability.
- Preserved explicit research-only and non-clinical boundaries.

## 0.24.3 — Genomic Validation and Sequence Provenance

- Completed the v0.24.0–v0.24.3 genomics chain.
- Added 48 sequence-analysis methods and 48 benchmarks.
- Added production activation and genomic visualization.
- Added eight validation profiles and six provenance event types.
- Added dataset manifests, reference context, pipeline records, sequence and variant fingerprints.
- Added hash-linked ledgers, tamper detection, and reproducibility dossiers.
- Added WordPress and FastAPI routes.
- Preserved non-clinical and non-diagnostic boundaries.

## 0.23.2 — Biosignal Visualization, Annotation, and Comparative Analysis

- Added eight biosignal visualization and comparison modes.
- Added 16 deterministic cross-runtime analysis methods and benchmarks.
- Added synchronized multi-channel and raw/filtered SVG plots.
- Added event, artifact, region, note, quality, and intervention annotations.
- Added lag scanning, alignment, correlation, MAE, RMSE, normalized RMSE, and run comparison.
- Added multi-channel CSV import and SVG, CSV, and JSON exports.
- Added project, notebook, and v0.22.3 provenance handoffs.
- Added WordPress and FastAPI analysis routes.
- Added mobile chart and control fallback.

## 0.23.1 — Biosignal Production Activation and Interface Reliability

- Added unconditional public biosignal asset activation.
- Added canonical panel and root recovery.
- Added missing-mount creation and duplicate suppression.
- Added stale render-marker and placeholder cleanup.
- Added controlled startup and navigation retries.
- Added page, focus, visibility, history, and mutation recovery.
- Added browser health and explicit repair/open controls.
- Added WordPress and FastAPI production-health routes.
- Added mobile control, output, chart, and overflow hardening.
- Preserved 48 methods, 48 benchmarks, eight categories, and non-clinical responsible-use boundaries.

## 0.23.0 — Biomedical Engineering and Biosignals

- Added 48 biomedical and biosignal methods.
- Added 48 deterministic cross-runtime benchmarks.
- Added acquisition and sampling calculations.
- Added ECG, PPG, respiration, EMG, and EEG tools.
- Added filtering and signal-quality calculations.
- Added waveform feature analysis and SVG plots.
- Added CSV batch execution with row isolation.
- Added project, notebook, and provenance handoffs.
- Added WordPress and FastAPI routes.
- Added explicit non-diagnostic and non-clinical responsible-use boundaries.

## 0.22.3 — Bioprocess Validation and Batch Provenance

- Added eight batch-validation profiles.
- Added CPP and CQA conformance decisions.
- Added cross-batch consistency calculations.
- Added control-performance and excursion review.
- Added hold-time and release-readiness checks.
- Added SHA-256 batch provenance records.
- Added parent-linked ledger verification and tamper detection.
- Added validation dossier creation and export.
- Added WordPress and FastAPI routes.

## 0.22.2 — Bioprocess Monitoring, Control, and Visualization

- Added eight standard process-monitoring channels.
- Added rolling statistics and excursion detection.
- Added six PID-style controller simulations.
- Added phase markers and multi-run comparison.
- Added CSV workflows, SVG charts, and JSON exports.
- Added WordPress and FastAPI monitoring routes.
- Added validation and provenance handoffs.

## 0.22.1 — Bioprocess Production Activation and Interface Reliability

- Added unconditional bioprocess production activation.
- Added canonical panel and root-mount repair.
- Added duplicate-root and stale-marker cleanup.
- Added startup, navigation, page-restoration, and MutationObserver retries.
- Added browser, WordPress, and FastAPI health checks.
- Added mobile and overflow reliability improvements.

## 0.22.0 — Biotechnology and Bioprocess Engineering

- Added 48 deterministic bioprocess methods and benchmarks.
- Added batch, fed-batch, and continuous simulations.
- Added oxygen transfer, mixing, heat, and scale-up calculations.
- Added CSV batch monitoring and provenance handoffs.
- Added WordPress and FastAPI bioprocess routes.

## 0.21.3 — Molecular Analysis Validation and Provenance

- Added eight molecular-analysis validation protocols.
- Added explicit acceptance thresholds and pass/fail dossiers.
- Added precision, recovery, linearity, LOD/LOQ, blank, control, robustness, and inter-run checks.
- Added SHA-256 payload and record fingerprints.
- Added parent-hash provenance chains and verification.
- Added analyst, instrument, source, and evidence metadata.
- Added deliberate tamper-detection tests.
- Added WordPress and FastAPI validation/provenance routes.

## 0.21.2 — Biochemistry Visualization and Batch Analysis

- Added seven native SVG visualization profiles.
- Added standard-curve regression and R².
- Added CSV batch execution for all 48 methods.
- Added mean, sample SD, CV, range, and review flags.
- Added row-level failure isolation and CSV/JSON export.
- Added WordPress and FastAPI batch routes.
- Preserved the v0.21.0 analysis catalog and benchmarks.

## 0.21.1 — Biochemistry Production Activation and Interface Reliability

- Activated Biochemistry assets reliably across full Lab, focused shortcode, page-builder, and cached-page paths.
- Added late-mount observation, controlled retries, stale render recovery, and canonical panel repair.
- Added browser diagnostics and a WordPress REST health endpoint.
- Hardened mobile formulas, controls, and results.
- Added a version-aware current-release validation runner.
- Preserved all 48 v0.21.0 biochemical methods and benchmarks.

## 0.21.0 — Biochemistry and Molecular Analysis

- Added 48 auditable biochemical and molecular-analysis methods.
- Added browser calculators and deterministic benchmarks.
- Added WordPress and FastAPI methods/run endpoints.
- Added project, notebook, visualization, and audit records.
- Added responsive presentation and responsible-use boundaries.

# Changelog

## 0.20.0

- Added Microbiology Laboratory with 48 methods and 48 deterministic benchmarks.
- Added formula-visible growth, culture, enumeration, environmental, antimicrobial, ecology, and laboratory quality-control analysis.
- Added WordPress and FastAPI interfaces plus project, notebook, visualization, and validation records.

## 0.19.0

- Added Rocket Propulsion and Spaceflight with 48 methods and 45 deterministic benchmarks.
- Added formula-visible propulsion, nozzle, staging, ascent, orbital, spacecraft, and mission-system analysis.
- Added WordPress and FastAPI interfaces plus project, notebook, visualization, and validation records.

## 0.18.0

- Added Aerospace Engineering and Flight Systems with 48 methods and 26 deterministic benchmarks.
- Added formula-visible aerodynamics, performance, stability, propulsion, structures, navigation, and flight-system analysis.
- Added WordPress and FastAPI interfaces plus project, notebook, visualization, and validation records.

## 0.17.0

- Added Comparative Economics and Development Systems with 48 methods and 22 deterministic benchmarks.
- Added formula-visible material-flow, product-loop, waste, symbiosis, lifecycle, and transition analysis.
- Added WordPress and FastAPI interfaces plus project, notebook, visualization, and validation records.

## 0.16.0

- Added Circular Economy and Industrial Ecology with 48 methods and 22 deterministic benchmarks.
- Added formula-visible material-flow, product-loop, waste, symbiosis, lifecycle, and transition analysis.
- Added WordPress and FastAPI interfaces plus project, notebook, visualization, and validation records.

## 0.15.0

- Added Sustainable Cities and Urban Resilience with 48 methods and 22 deterministic benchmarks.
- Added formula-visible Sustainable Cities and Civil interfaces.
- Repaired Civil and Infrastructure auto-initialization and asset loading across the main and focused Lab shortcodes.
- Added 8 Civil interface-repair benchmarks and checks that all 48 civil formulas are documented.

## 0.14.0

- Added Urban Planning and Spatial Systems with 48 methods and 21 deterministic benchmarks.
- Added standalone WordPress integration and REST proxy classes.
- Added land-use, accessibility, mobility, network, GIS, public-service, resilience, and scenario project records.

## 0.13.0

- Added Architecture and Building Performance with 48 methods and 19 deterministic benchmarks.
- Added standalone WordPress integration and REST proxy classes to reduce coupling to the central Lab plugin class.
- Added project records for envelope, daylight, IEQ, energy, water, carbon, acoustics, and resilience.

## 0.12.0

- Added Civil Engineering and Infrastructure Systems with 48 methods and 18 deterministic benchmarks.

## 0.11.0 — 2026-07-13

- Added the Mechanical and Thermal Engineering Laboratory.
- Added 48 browser/Python methods from a shared auditable method catalog.
- Added 16 deterministic reference benchmarks.
- Added statics, strength, failure, machine design, dynamics, vibration, fluid, thermodynamic, and heat-transfer records.
- Added protected `/v1/mechanical/methods` and `/v1/mechanical/run` FastAPI routes.
- Added the `[sc_lab_mechanical_thermal]` focused shortcode.

## 0.10.0 — 2026-07-12

- Added the Electrical, Electronics, and Embedded Systems Laboratory.
- Added 45 browser-executable DC, AC, analog, digital, embedded, power, thermal, and signal methods.
- Added embedded device profiles, firmware starter artifacts, logic-level interface validation, and hardware benchmark records.
- Added protected `/v1/electrical/methods` and `/v1/electrical/run` FastAPI endpoints.
- Added electrical analysis, device-profile, hardware-validation, and domain method-catalog contracts.
- Added the `[sc_lab_electrical]` focused shortcode and project collections for circuit, electronics, embedded, firmware, BOM, schematic, interface, and validation records.

## 0.9.5 — 2026-07-12

- Added four Report Composer templates, ordered sections, autosave, project drafts, and revision history.
- Added visualization semantics, keyboard focus, data-table alternatives, reduced-motion support, preview modes, and accessibility audit records.
- Added JSON/compatible-ZIP restore preflight, conflict analysis, copy/merge/replace dry runs, typed replace confirmation, automatic safety backups, fingerprints, receipts, and post-restore integrity checks.
- Added synthetic legacy-project migration validation for v0.1.x through v0.9.4-shaped records.
- Added report-composition, restore-validation, and accessibility-audit contracts.
- Removed tracked Python cache files and ignored generated caches.

## 0.9.4 - PDF Reports and Decision Studio Handoff

- Added Report Studio for technical reports, decision briefs, evidence packets, and executive summaries containing one to twelve analyses.
- Added the `sc-lab-report/1.0` and `sc-lab-report-result/1.0` contracts.
- Added browser-native selectable-text PDF generation for immediate offline reports.
- Added ReportLab vector PDF generation through the Render compute backend.
- Added vector line, bar, and scatter figures, structured input/output tables, equations, assumptions, warnings, validation, sources, runtime metadata, and audit fingerprints.
- Added protected WordPress proxy routes and FastAPI endpoints for report validation and PDF generation.
- Advanced the Decision Studio packet to `sc-decision-studio-analysis-packet/2.0`.
- Added report-aware handoffs containing analyses, charts, tables, dimensional scenes, evidence, uncertainties, validation, runtime metadata, and provenance.
- Added Report Studio project selection, preview, local PDF, Render PDF, JSON export, packet export, save, validation, and handoff controls.
- Added `reports`, `reportFigures`, `reportExports`, and `decisionStudioHandoffs` project collections.
- Added `[sc_lab_reports]` and `[sc_lab_report_studio]` focused shortcodes.
- Added regression tests for nested report fields, report endpoints, PDF bytes, handoff validation, project migration, and WordPress report markers.
- Corrected nested report-table flattening discovered during rendered-PDF inspection.
- Preserved all existing scientific engines, portable method contracts, curated multi-language execution, visualization, 3D/4D, backup, reset, and restore functionality.

## 0.9.3 - Render Compute Dispatcher and Multi-Language Execution Workers

- Added a FastAPI dispatcher, curated native-language workers, direct and queued execution, cancellation, runtime discovery, and cross-language comparison.
- Added a protected WordPress REST proxy so backend credentials are never exposed to browser JavaScript.
- Added Render Blueprint services for the compute API, RQ worker, and Key Value queue.
- Added Python, JavaScript, TypeScript, C, C++, Fortran, Rust, and Go worker targets.
- Added thread-safe subprocess execution and removed `preexec_fn` for macOS Python 3.14 compatibility.
- Added compute execution, runtime, compiler, job, benchmark, and cross-language validation project records.

## 0.9.2 — Universal Code Switcher and Method Contracts

- Added the `sc-lab-method/1.0` portable method-contract architecture.
- Added Code Studio with Python, R, Julia, JavaScript, TypeScript, SQL, C, C++, Fortran, Rust, Go, and Haskell views.
- Added nineteen portable scientific and engineering method contracts with structured inputs, units, constants, validation bounds, derived values, output expression graphs, and assumptions.
- Added generated downloadable source, method JSON, Jupyter notebook, and method-catalog exports.
- Added local portable-contract execution and numerical comparison with the current JavaScript calculator where an adapter exists.
- Added `methodContracts`, `codeArtifacts`, and `implementationComparisons` project collections.
- Added a Code action to the universal calculation toolbar and `[sc_lab_code_switcher]`.
- Added repository examples for kinetic energy, projectile motion, Michaelis–Menten kinetics, and photovoltaic output across all twelve languages.
- Added generated-source execution or compilation tests for Python, JavaScript, TypeScript, C, C++, Fortran, and Go, plus structural tests for R, Julia, Rust, SQL, and Haskell.
- Stabilized the WordPress update identity at `sustainable-catalyst-lab/sustainable-catalyst-lab.php`.
- Added the unversioned `sustainable-catalyst-lab.zip` update archive.
- Added an administrator duplicate-installation detector and nonce-protected duplicate deactivation action.
- Preserved the v0.9.1 visualization, 3D/4D, export, Decision Studio, backup, restore, and reset infrastructure.
- Preserved all v0.1.x–v0.9.1 projects through non-destructive normalization.

## 0.9.0 — Energy and Engineering Laboratory

- Added a first-class Energy and Engineering Laboratory with eleven analytical work areas and a dedicated validation workspace.
- Added 119 browser-based methods covering energy balances, solar, wind, hydro, storage, electric power, thermal systems, fuels, hydrogen, emissions, techno-economics, and reliability.
- Added explicit equations, unit-aware inputs, assumptions, warning states, project records, notebook actions, and generated-document integration for every Energy method.
- Added solar geometry, plane-of-array irradiance, PV sizing, wind resource and turbine calculations, hydropower hydraulics, and pumped-storage analysis.
- Added battery, flywheel, thermal, hydrogen, and compressed-air storage methods.
- Added three-phase power, transformer, line-loss, voltage-drop, power-factor, fault-current, reserve-margin, peak-shaving, and grid-emissions calculations.
- Added thermal transport, heat-exchanger, heat-pump, refrigeration, boiler, pipe-loss, and degree-day methods.
- Added electrolyzer, fuel-cell, hydrogen-compression, combustion-air, biogas, methane-leakage, and fuel-energy methods.
- Added lifecycle and avoided-emissions calculations, carbon payback, NPV, IRR, LCOE, LCOS, levelized hydrogen, cost of saved energy, and carbon-price breakeven.
- Added availability, Weibull reliability, expected energy not served, exact independent-unit loss-of-load probability, N−1 checks, and distribution reliability indices.
- Added 12 deterministic Energy and Engineering benchmark cases and saved validation reports.
- Added `[sc_lab_energy]`, command-search entries, quick tools, system status, documentation output, and 14 Energy-specific project collections.
- Preserved all v0.1.x–v0.8.0 projects through non-destructive normalization.

## 0.8.0 — Earth, Climate, Ocean, and Marine Systems

- Added a first-class Earth, Climate, Ocean, and Marine Systems Laboratory with ten connected work areas.
- Added 83 browser-based methods across solid Earth, atmosphere, climate, hydrology, oceanography, marine ecology, remote sensing, hazards, and carbon-cycle analysis.
- Added 12 deterministic Earth systems benchmark cases and Earth-specific project records.

## 0.7.0 — Materials Science and Characterization

- Added a first-class Materials Science and Characterization Laboratory with eleven working areas.
- Added 49 browser-based analytical methods across mechanics, thermal transport, electrical behavior, magnetism, optics, crystallography, phase analysis, diffusion, corrosion, polymers, composites, and microscopy.
- Added XRD tools for Bragg spacing, cubic lattice parameters, Scherrer crystallite size, and theoretical crystal density.
- Added mechanical-property tools for engineering and true stress–strain, elastic constants, resilience, fracture intensity, fatigue, and creep.
- Added thermal, dielectric, semiconductor, Hall-effect, magnetic, optical, and corrosion calculations.
- Added polymer, composite, particle-size, grain-size, area-fraction, and microscopy calibration workflows.
- Added method assumptions, validation states, warnings, plots where applicable, notebook routing, experiment templates, and project-specific records.
- Added ten deterministic materials benchmark cases and saved validation reports.
- Added `[sc_lab_materials]`, command-search entries, quick tools, status reporting, project documentation output, and materials-specific schema collections.
- Preserved all v0.1.x–v0.6.0 projects through non-destructive normalization.

## 0.6.0 — Astronomy and Astrophysics Laboratory

- Added a first-class Astronomy and Astrophysics Laboratory with ten scientific work areas.
- Added 42 methods spanning celestial coordinates, orbital mechanics, planetary systems, stellar physics, photometry, spectroscopy, galaxies, cosmology, and telescope imaging.
- Added ten deterministic astronomy benchmark cases and astronomy-specific project records.

## 0.5.0 — Biology and Computational Biology Laboratory

- Added a first-class Biology Laboratory with nine scientific work areas.
- Added 40 computational biology methods and eight deterministic reference cases.
- Added sequence, protein, genetic, population, ecological, physiological, and biology-validation records.

## 0.4.1 — Physics Validation and Visualization Patch

- Added method metadata, per-run validation, deterministic benchmarks, improved SVG plots, comparison/export controls, and uncertainty methods.

## 0.4.0 — Physics, Electromagnetism, and Particle Physics Laboratory

- Added the first-class Physics Laboratory with mechanics, waves, fluids, optics, electromagnetism, circuits, quantum, nuclear, particle, detector, and measurement methods.

## 0.3.0 — Chemistry Laboratory and Spectrometry Expansion

- Added the expanded Chemistry Laboratory, analytical calibration, and reproducible Spectrometry Studio.

## 0.2.0 — Live Scientific Data and Observation Workspace

- Added the Scientific Observation Board, Dataset Inspector, climate maps, telescope and marine workspaces, and source registry.

## 0.1.1 — Scientific Interface and Workspace Integration Patch

- Added workflow navigation, command search, interactive traceability, and data-driven overview.

## 0.1.0 — Scientific Workspace and Project Foundation

- Added the initial Lab application, scientific feeds, periodic table, chemistry foundations, calculators, experiments, notebook, and documentation.

### macOS / Python 3.14 execution compatibility correction

- Removed the thread-unsafe `subprocess.preexec_fn` resource limiter from native-language execution.
- Added an optional GNU `prlimit` command wrapper on Linux workers.
- Retained subprocess timeouts, isolated temporary directories, restricted environments, output limits, and Render container boundaries.
- Added a regression test covering FastAPI and in-memory threaded job execution.

## 0.27.1 — Numerical Validation and Benchmark Library

- Added fourteen known-answer numerical benchmarks.
- Added benchmark, suite, and convergence endpoints to Python Compute Core.
- Added the Numerical Validation Library panel and shortcode.
- Added analytic/browser references, tolerance controls, unit assertions, residual checks, and exportable reports.
