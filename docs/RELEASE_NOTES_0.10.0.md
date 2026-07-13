# Sustainable Catalyst Lab v0.10.0
## Electrical, Electronics, and Embedded Systems

Version 0.10.0 is the first domain expansion after the v0.9.x shared-infrastructure series. It adds a dedicated electrical, electronics, digital, signal, power-electronics, and embedded-systems laboratory while preserving the stable WordPress identity, project storage keys, universal visualization, code-switching, report, restore, and Decision Studio contracts.

## Laboratory capabilities

- 45 browser-executable, auditable engineering methods across DC circuits, AC networks, analog electronics, digital logic, embedded timing and buses, power conversion, thermal screening, and signal acquisition.
- Circuit methods for Ohm's law, series and parallel resistance, loaded dividers, Thévenin and Norton equivalents, RC/RL transients, Wheatstone bridges, RLC impedance, resonance, filtering, transformers, power factor, and balanced three-phase power.
- Electronics methods for LEDs, diodes, zener regulators, BJT switching, MOSFET gate drive, op-amps, instrumentation amplifiers, logic margins, timing budgets, debounce, and pull-up bounds.
- Embedded methods for ADC quantization, sensor scaling, PWM, timer setup, UART baud error, I²C pull-ups, SPI throughput, CAN loading, and battery-runtime estimation.
- Power and validation methods for linear-regulator dissipation, buck/boost duty cycles, capacitor ripple, junction temperature, Nyquist screening, ENOB/SNR, and ADC-source loading.
- Project-backed electrical, electronics, embedded, interface, device-profile, firmware, schematic, BOM, and hardware-validation collections.
- Embedded device profiles for Arduino Uno, ESP32, RP2040, STM32 Nucleo, and Raspberry Pi environments.
- Starter firmware artifacts for Arduino C++, MicroPython, Rust embedded, and Linux/Python workflows.
- Logic-level interface screening with voltage-domain and noise-margin checks.
- Eleven deterministic browser validation benchmarks and matching Python backend tests.

## Backend

Protected endpoints are added to the existing FastAPI service:

- `GET /v1/electrical/methods`
- `POST /v1/electrical/run`

The backend accepts only curated method identifiers and structured numeric inputs. It does not execute arbitrary source code or control connected hardware.

## WordPress

The main Lab application gains an **Electrical & embedded** navigation item and the focused shortcode:

```text
[sc_lab_electrical]
```

The stable plugin basename remains:

```text
sustainable-catalyst-lab/sustainable-catalyst-lab.php
```

## Boundaries

The new tools are screening, educational, and documentation systems. They do not replace component datasheets, SPICE and electromagnetic simulation, PCB signal/power-integrity analysis, electrical codes, certification testing, utility or mains-safety review, functional-safety engineering, or licensed professional review. Never connect an unverified circuit to mains voltage, high-energy batteries, medical equipment, vehicles, industrial machinery, or safety-critical systems.
