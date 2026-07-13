# Electrical, Electronics, and Embedded Systems Architecture

Lab v0.10.0 organizes the domain into seven coordinated work areas:

1. **DC circuits** — resistive networks, equivalents, bridges, and first-order transients.
2. **AC and power systems** — complex impedance, resonance, filters, transformers, power factor, and balanced three-phase screening.
3. **Analog electronics** — diode, transistor, op-amp, instrumentation, and interface calculations.
4. **Digital logic** — voltage margins, pull networks, propagation timing, and debounce.
5. **Embedded systems** — ADC, PWM, timers, UART, I²C, SPI, CAN, sensor scaling, and energy budgets.
6. **Power and thermal** — regulator loss, converter duty, ripple, and junction-temperature screening.
7. **Signals and validation** — sampling, alias screening, ENOB, acquisition loading, deterministic benchmarks, and evidence records.

Each analysis carries a method identifier, release version, equation, assumptions, inputs, outputs, warnings, timestamps, and fingerprints. Saved records can be visualized, included in reports, placed into notebook entries, exported with the workspace, and handed to Decision Studio.

## Device and firmware records

Device profiles store board identity, logic voltage, supported interfaces, firmware target, sensors, actuators, and an audit fingerprint. Firmware artifacts are source records, not automatically flashed binaries. Hardware work must retain pin assignments, voltage domains, current limits, protections, component tolerances, board revisions, compiler/toolchain versions, and physical test results.

## Validation model

A calculation may pass deterministic software benchmarks and still fail in hardware because of parasitics, layout, grounding, EMI/EMC, thermal conditions, tolerances, connector errors, firmware timing, or undocumented operating conditions. Lab therefore labels calculations as screening outputs and keeps hardware-validation records separate from calculations.
