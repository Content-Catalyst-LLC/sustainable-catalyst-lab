# Sustainable Catalyst Lab v0.9.2

Sustainable Catalyst Lab is a modular scientific and engineering workspace for WordPress. Version 0.9.2 adds the **Universal Code Switcher and Portable Method Contract layer** while retaining the complete Chemistry, Physics, Biology, Astronomy, Materials, Earth Systems, Energy, observation, dataset, visualization, 3D/4D, project, notebook, export, backup, and reset systems from earlier releases.

## Stable WordPress plugin identity

Use the unversioned WordPress archive:

```text
sustainable-catalyst-lab.zip
```

The archive always contains exactly:

```text
sustainable-catalyst-lab/
└── sustainable-catalyst-lab.php
```

WordPress identifies a plugin by this folder and bootstrap-file path. Uploading a repository ZIP, a release bundle, or a versioned root directory can create a second plugin instance.

Version 0.9.2 adds an administrator duplicate detector under:

```text
Settings → Sustainable Catalyst Lab → Plugin installation identity
```

It lists other installed copies with the same plugin name or text domain and provides a nonce-protected action that deactivates duplicate instances without deleting their folders or browser project data.

## Universal Code Switcher

The new Code Studio supports twelve language views:

```text
Python
R
Julia
JavaScript
TypeScript
SQL
C
C++
Fortran
Rust
Go
Haskell
```

For each portable method, users can:

- Change language without changing the scientific method contract
- Inspect generated source
- Run the portable method contract locally
- Compare the contract result with the current JavaScript calculator
- Download the selected source file
- Download the method JSON contract
- Download a Python Jupyter notebook
- Download the complete method catalog
- Save method contracts and source artifacts to the active Lab project

JavaScript is browser-runnable in this release. The other language implementations are source-generating, downloadable, and repository-testable; secured server execution is reserved for the v0.9.3 Render Compute Dispatcher.

## Portable method contracts

A portable method is represented once as a language-independent expression graph:

```text
Method identity and version
Inputs and units
Constants
Validation bounds
Derived variables
Output expressions
Assumptions
Supported languages
```

The same contract is rendered into all twelve language targets. This prevents scientific logic from drifting independently between handwritten implementations.

Version 0.9.2 includes nineteen portable reference contracts spanning:

- Mechanics and projectile motion
- Thermodynamics
- Astronomy
- Fluids
- Biology and enzyme kinetics
- Population growth
- Materials and diffusion
- Electrical resistance
- Earth science
- Hydropower
- Photovoltaics
- Wind power
- Battery energy and runtime

The repository also includes complete multi-language example folders for kinetic energy, projectile motion, Michaelis–Menten kinetics, and photovoltaic output.

## Project-model additions

```text
methodContracts
codeArtifacts
implementationComparisons
```

Existing project keys remain unchanged:

```text
scLabProjectsV010
scLabActiveProjectV010
```

Projects from v0.1.x through v0.9.1 are normalized non-destructively to schema version `0.9.2`.

## Existing universal visualization and workspace features

Version 0.9.2 retains:

- Universal analysis contracts
- SVG, high-resolution PNG, PDF, CSV, and JSON exports
- Complete analysis-package ZIPs
- Decision Studio packets
- Interactive 3D and projected 4D scenes
- Cube, tesseract, 4-simplex, and 16-cell presets
- Workspace JSON and ZIP backup
- Selective note, observation, analysis, project, and factory reset
- Restore-as-copy, merge, and replace modes

The calculation toolbar now includes a **Code** action that routes a supported analysis directly into Code Studio.

## Shortcodes

Main application:

```text
[sc_lab_app]
```

Focused infrastructure interfaces:

```text
[sc_lab_visualization]
[sc_lab_workspace_data]
[sc_lab_code_switcher]
```

All existing focused discipline shortcodes remain available.

## Contracts

```text
contracts/project.schema.json
contracts/analysis.schema.json
contracts/scene.schema.json
contracts/decision-studio-packet.schema.json
contracts/method.schema.json
contracts/method-catalog.json
```

## Validation

Run:

```bash
chmod +x scripts/test_release.sh
./scripts/test_release.sh
```

The release suite validates:

- PHP and JavaScript syntax
- WordPress template rendering
- Stable plugin slug and bootstrap markers
- Duplicate-installation detector markers
- All inherited scientific engines and 61 deterministic discipline benchmarks
- Nineteen portable method contracts
- Twelve language generators including Rust
- Portable-contract parity with current JavaScript methods
- Python, JavaScript, TypeScript, C, C++, Fortran, and Go generated-source execution or compilation in the packaging environment
- Source markers for R, Julia, Rust, SQL, and Haskell
- Visualization, PDF, 3D/4D, backup, reset, restore, migration, and Decision Studio packet tests

## Boundaries

- Generated implementations are transparent reference code, not a claim that every discipline method already has cross-language parity.
- v0.9.2 provides nineteen portable methods; the catalog expands incrementally as methods receive explicit expression contracts and reference tests.
- R, Julia, Rust, SQL, and Haskell source is generated and structurally tested here, but those runtimes were unavailable in the packaging environment.
- Arbitrary public code execution is not enabled. The future Render dispatcher will execute only curated, versioned repository methods inside restricted workers.
