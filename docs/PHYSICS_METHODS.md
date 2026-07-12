# Physics Laboratory Methods and Validation

## Constants

The browser modules use explicit SI constants for the speed of light, Planck constant, reduced Planck constant, elementary charge, electron/proton/neutron masses, vacuum permittivity and permeability, gravitation, standard gravity, Boltzmann constant, gas constant, Stefan–Boltzmann constant, Avogadro constant, and atomic mass unit.

Each saved v0.4.1 physics result identifies the embedded constants version and records the method equation, declared units, assumptions, validation state, checks, warnings, and timestamp.

## Method groups

### Mechanics and waves

Uniform-acceleration kinematics, projectile motion, finite-amplitude pendulum correction, Hooke oscillator quantities, sinusoidal wave generation, and acoustic intensity level.

### Thermodynamics and fluids

Ideal-gas state, monatomic internal energy, first-law bookkeeping, Carnot limits, Reynolds number, flow-regime classification, hydrostatic/dynamic pressure, and Bernoulli pressure relation.

### Optics

Snell refraction, total internal reflection, thin-lens imaging, magnification, diffraction scale, Rayleigh resolution, and photon spectral quantities.

### Electromagnetism

Coulomb force and energy, point-charge field superposition, capacitor networks, magnetic fields for ideal conductors/coils/solenoids, Lorentz force and orbit, Faraday induction, wave propagation, intrinsic impedance, skin depth, isotropic power density, and rectangular-waveguide cutoff.

### Circuits and signals

Series RLC impedance, phase, current, real/reactive/apparent power, power factor, resonance, logarithmic frequency sweeps, and first-order RC filter response.

### Quantum and nuclear physics

Relativistic de Broglie wavelength, particle-in-a-box energy levels, rectangular-barrier tunneling approximation, hydrogen transitions, radioactive decay/activity, and nuclear binding energy.

### Particle and detector physics

Relativistic energy/momentum, invariant-mass reconstruction, two-body decay kinematics, charged-track transverse momentum, time of flight, background subtraction, approximate event significance, and cross-section estimation.

### Measurement and validation

Independent uncertainty combination, power-law uncertainty propagation, uncertainty-weighted means, chi-square consistency, reduced chi-square, Birge ratio, and deterministic implementation benchmarks.

## Validation states

- **VALIDATED** — all implemented internal checks pass and no method-boundary warnings were generated.
- **WARNING** — the computation completed, but one or more assumptions, approximations, or supplied domains require review.
- **INVALID** — a physical constraint or numerical integrity check failed. The result should not be used without correcting the input/model issue.

A validation state is not a certification. It addresses only the implemented model and supplied inputs.

## Numerical benchmark suite

The release includes deterministic reference cases for:

1. Uniform-acceleration final velocity.
2. Uniform-acceleration displacement.
3. Ideal 45-degree projectile range.
4. One-meter small-angle pendulum period.
5. Coulomb-force reference case.
6. Series-RLC resonance phase.
7. 500 nm photon energy.
8. Two elapsed half-lives.
9. Massless two-body decay in the parent rest frame.

The suite is accessible from the Physics panel and can be stored in `physicsValidationRecords` or exported as JSON.

## Visualization

Physics plots support labelled axes, numerical ticks, grid lines, zero references where relevant, logarithmic frequency axes, legends, comparison baselines, SVG export, and CSV series export. These plots visualize the analytical methods; they are not substitutes for instrument traces or validated simulation packages.

## Method boundaries

The methods are analytical and educational models. They do not replace finite-element electromagnetic solvers, SPICE, certified RF exposure analysis, radiation transport, detector simulation, accelerator software, safety engineering, metrology accreditation, or standards-compliant verification.
