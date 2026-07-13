(function (w) {
  'use strict';

  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util || {};
  const VERSION = '0.10.0';
  const n = value => Number(value);
  const finite = (value, name) => {
    const number = n(value);
    if (!Number.isFinite(number)) throw new Error(`${name} must be finite.`);
    return number;
  };
  const positive = (value, name) => {
    const number = finite(value, name);
    if (!(number > 0)) throw new Error(`${name} must be positive.`);
    return number;
  };
  const nonnegative = (value, name) => {
    const number = finite(value, name);
    if (!(number >= 0)) throw new Error(`${name} must be nonnegative.`);
    return number;
  };
  const percent = (value, name) => {
    const number = nonnegative(value, name);
    if (number > 100) throw new Error(`${name} must not exceed 100%.`);
    return number / 100;
  };
  const round = (value, digits = 10) => Number.isFinite(value) ? Number(value.toPrecision(digits)) : value;
  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
  const esc = value => typeof U.esc === 'function' ? U.esc(value) : String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[char]));
  const now = () => typeof U.now === 'function' ? U.now() : new Date().toISOString();
  const fingerprint = value => typeof U.fingerprint === 'function' ? U.fingerprint(value) : `local-${JSON.stringify(value).length}`;
  const list = value => (Array.isArray(value) ? value : String(value || '').split(',')).map(Number).filter(Number.isFinite);
  const TWO_PI = 2 * Math.PI;

  const f = (id, label, value, unit = '', options = {}) => ({ id, label, value, unit, ...options });
  const d = (id, name, tab, equation, fields, compute, assumptions = [], collection = 'electricalRecords') => ({
    id, name, tab, equation, fields, compute, assumptions, collection, version: VERSION
  });

  function result(outputs, warnings = [], status = 'SCREENING_ONLY', extras = {}) {
    return {
      schema: 'sc-lab-electrical-analysis/1.0',
      version: VERSION,
      outputs,
      validation: {
        status,
        warnings: [
          ...warnings,
          'Check tolerances, temperature coefficients, parasitics, transients, layout, grounding, and manufacturer limits.',
          'Safety-critical or regulated designs require qualified engineering review and physical validation.'
        ]
      },
      ...extras
    };
  }

  const definitions = [
    d('electrical.ohms-law', "Ohm's law and DC power", 'dc', 'I = V/R; P = VI', [
      f('voltage', 'Voltage', 12, 'V'), f('resistance', 'Resistance', 100, 'Ω')
    ], input => {
      const voltage = finite(input.voltage, 'Voltage');
      const resistance = positive(input.resistance, 'Resistance');
      const current = voltage / resistance;
      return result({ current: round(current), power: round(voltage * current), conductance: round(1 / resistance) });
    }, ['Assumes a linear, time-invariant resistance.']),

    d('electrical.resistors-series', 'Series resistor network', 'dc', 'R_eq = ΣRᵢ', [
      f('resistances', 'Resistances', '100,220,330', 'Ω', { type: 'text' })
    ], input => {
      const values = list(input.resistances);
      if (!values.length || values.some(value => value <= 0)) throw new Error('Enter positive resistance values.');
      return result({ equivalentResistance: round(values.reduce((sum, value) => sum + value, 0)), branchCount: values.length });
    }),

    d('electrical.resistors-parallel', 'Parallel resistor network', 'dc', '1/R_eq = Σ(1/Rᵢ)', [
      f('resistances', 'Resistances', '100,220,330', 'Ω', { type: 'text' })
    ], input => {
      const values = list(input.resistances);
      if (!values.length || values.some(value => value <= 0)) throw new Error('Enter positive resistance values.');
      return result({ equivalentResistance: round(1 / values.reduce((sum, value) => sum + 1 / value, 0)), branchCount: values.length });
    }),

    d('electrical.loaded-divider', 'Loaded voltage divider', 'dc', 'Vout = Vin(R2∥RL)/(R1 + R2∥RL)', [
      f('vin', 'Input voltage', 5, 'V'), f('r1', 'Upper resistance', 10000, 'Ω'), f('r2', 'Lower resistance', 10000, 'Ω'), f('load', 'Load resistance', 100000, 'Ω')
    ], input => {
      const vin = finite(input.vin, 'Input voltage');
      const r1 = positive(input.r1, 'Upper resistance');
      const r2 = positive(input.r2, 'Lower resistance');
      const load = positive(input.load, 'Load resistance');
      const lower = 1 / (1 / r2 + 1 / load);
      const unloaded = vin * r2 / (r1 + r2);
      const loaded = vin * lower / (r1 + lower);
      return result({ unloadedVoltage: round(unloaded), loadedVoltage: round(loaded), loadingErrorPercent: round(100 * (loaded - unloaded) / unloaded), loadedLowerResistance: round(lower) });
    }),

    d('electrical.thevenin', 'Thévenin equivalent', 'dc', 'Rth = Voc/Isc', [
      f('openCircuitVoltage', 'Open-circuit voltage', 5, 'V'), f('shortCircuitCurrent', 'Short-circuit current', 0.05, 'A')
    ], input => {
      const voltage = finite(input.openCircuitVoltage, 'Open-circuit voltage');
      const current = positive(input.shortCircuitCurrent, 'Short-circuit current');
      return result({ theveninVoltage: round(voltage), theveninResistance: round(voltage / current), maximumPowerTransfer: round(voltage * current / 4) }, ['Short-circuit current must come from a safe model or controlled test.']);
    }),

    d('electrical.norton', 'Norton equivalent', 'dc', 'Rn = Voc/Isc', [
      f('openCircuitVoltage', 'Open-circuit voltage', 5, 'V'), f('shortCircuitCurrent', 'Short-circuit current', 0.05, 'A')
    ], input => {
      const voltage = finite(input.openCircuitVoltage, 'Open-circuit voltage');
      const current = positive(input.shortCircuitCurrent, 'Short-circuit current');
      return result({ nortonCurrent: round(current), nortonResistance: round(voltage / current) });
    }),

    d('electrical.rc-charge', 'RC charge and discharge', 'dc', 'τ = RC; Vc(t)=Vs(1−e^(−t/τ))', [
      f('resistance', 'Resistance', 10000, 'Ω'), f('capacitance', 'Capacitance', 0.000001, 'F'), f('time', 'Time', 0.01, 's'), f('supply', 'Supply', 5, 'V')
    ], input => {
      const resistance = positive(input.resistance, 'Resistance');
      const capacitance = positive(input.capacitance, 'Capacitance');
      const time = nonnegative(input.time, 'Time');
      const supply = finite(input.supply, 'Supply');
      const tau = resistance * capacitance;
      return result({ timeConstant: round(tau), chargeVoltage: round(supply * (1 - Math.exp(-time / tau))), dischargeFraction: round(Math.exp(-time / tau)), cutoffFrequency: round(1 / (TWO_PI * tau)) });
    }),

    d('electrical.rl-current', 'RL current transient', 'dc', 'τ = L/R; I(t)=V/R(1−e^(−t/τ))', [
      f('resistance', 'Resistance', 10, 'Ω'), f('inductance', 'Inductance', 0.01, 'H'), f('time', 'Time', 0.002, 's'), f('supply', 'Supply', 5, 'V')
    ], input => {
      const resistance = positive(input.resistance, 'Resistance');
      const inductance = positive(input.inductance, 'Inductance');
      const time = nonnegative(input.time, 'Time');
      const supply = finite(input.supply, 'Supply');
      const tau = inductance / resistance;
      const steady = supply / resistance;
      return result({ timeConstant: round(tau), current: round(steady * (1 - Math.exp(-time / tau))), steadyCurrent: round(steady) });
    }),

    d('electrical.wheatstone', 'Wheatstone bridge', 'dc', 'Vout = Vs[R2/(R1+R2) − R4/(R3+R4)]', [
      f('supply', 'Supply', 5, 'V'), f('r1', 'R1', 1000, 'Ω'), f('r2', 'R2', 1000, 'Ω'), f('r3', 'R3', 1000, 'Ω'), f('r4', 'R4', 1010, 'Ω')
    ], input => {
      const supply = finite(input.supply, 'Supply');
      const r1 = positive(input.r1, 'R1'), r2 = positive(input.r2, 'R2'), r3 = positive(input.r3, 'R3'), r4 = positive(input.r4, 'R4');
      const left = r2 / (r1 + r2);
      const right = r4 / (r3 + r4);
      return result({ outputVoltage: round(supply * (left - right)), ratioMismatch: round(r1 / r2 - r3 / r4) });
    }),

    d('electrical.series-rlc', 'Series RLC impedance', 'ac', '|Z| = √(R² + (ωL − 1/ωC)²)', [
      f('resistance', 'Resistance', 10, 'Ω'), f('inductance', 'Inductance', 0.01, 'H'), f('capacitance', 'Capacitance', 0.000001, 'F'), f('frequency', 'Frequency', 1000, 'Hz'), f('voltage', 'RMS voltage', 1, 'V')
    ], input => {
      const resistance = nonnegative(input.resistance, 'Resistance');
      const inductance = positive(input.inductance, 'Inductance');
      const capacitance = positive(input.capacitance, 'Capacitance');
      const frequency = positive(input.frequency, 'Frequency');
      const voltage = nonnegative(input.voltage, 'RMS voltage');
      const omega = TWO_PI * frequency;
      const xl = omega * inductance;
      const xc = 1 / (omega * capacitance);
      const impedance = Math.hypot(resistance, xl - xc);
      return result({ inductiveReactance: round(xl), capacitiveReactance: round(xc), impedanceMagnitude: round(impedance), phaseDegrees: round(Math.atan2(xl - xc, resistance) * 180 / Math.PI), currentRms: round(voltage / impedance) });
    }),

    d('electrical.resonance', 'RLC resonance and Q', 'ac', 'f₀ = 1/(2π√LC); Q = √(L/C)/R', [
      f('resistance', 'Series resistance', 10, 'Ω'), f('inductance', 'Inductance', 0.01, 'H'), f('capacitance', 'Capacitance', 0.000001, 'F')
    ], input => {
      const resistance = positive(input.resistance, 'Series resistance');
      const inductance = positive(input.inductance, 'Inductance');
      const capacitance = positive(input.capacitance, 'Capacitance');
      const f0 = 1 / (TWO_PI * Math.sqrt(inductance * capacitance));
      const q = Math.sqrt(inductance / capacitance) / resistance;
      return result({ resonantFrequency: round(f0), qualityFactor: round(q), bandwidth: round(f0 / q) });
    }),

    d('electrical.rc-lowpass', 'RC low-pass response', 'ac', '|H| = 1/√(1+(f/fc)²)', [
      f('resistance', 'Resistance', 10000, 'Ω'), f('capacitance', 'Capacitance', 0.00000001, 'F'), f('frequency', 'Frequency', 1000, 'Hz')
    ], input => {
      const resistance = positive(input.resistance, 'Resistance');
      const capacitance = positive(input.capacitance, 'Capacitance');
      const frequency = positive(input.frequency, 'Frequency');
      const fc = 1 / (TWO_PI * resistance * capacitance);
      const ratio = frequency / fc;
      const magnitude = 1 / Math.sqrt(1 + ratio * ratio);
      return result({ cutoffFrequency: round(fc), magnitude: round(magnitude), gainDb: round(20 * Math.log10(magnitude)), phaseDegrees: round(-Math.atan(ratio) * 180 / Math.PI) });
    }),

    d('electrical.rc-highpass', 'RC high-pass response', 'ac', '|H| = (f/fc)/√(1+(f/fc)²)', [
      f('resistance', 'Resistance', 10000, 'Ω'), f('capacitance', 'Capacitance', 0.00000001, 'F'), f('frequency', 'Frequency', 1000, 'Hz')
    ], input => {
      const resistance = positive(input.resistance, 'Resistance');
      const capacitance = positive(input.capacitance, 'Capacitance');
      const frequency = positive(input.frequency, 'Frequency');
      const fc = 1 / (TWO_PI * resistance * capacitance);
      const ratio = frequency / fc;
      const magnitude = ratio / Math.sqrt(1 + ratio * ratio);
      return result({ cutoffFrequency: round(fc), magnitude: round(magnitude), gainDb: round(20 * Math.log10(magnitude)), phaseDegrees: round(Math.atan(1 / ratio) * 180 / Math.PI) });
    }),

    d('electrical.transformer', 'Ideal transformer and reflected load', 'ac', 'V₂/V₁ = N₂/N₁; Zref = (N₁/N₂)²ZL', [
      f('primaryTurns', 'Primary turns', 1000, ''), f('secondaryTurns', 'Secondary turns', 100, ''), f('primaryVoltage', 'Primary voltage', 120, 'V'), f('loadResistance', 'Secondary load', 10, 'Ω')
    ], input => {
      const primaryTurns = positive(input.primaryTurns, 'Primary turns');
      const secondaryTurns = positive(input.secondaryTurns, 'Secondary turns');
      const primaryVoltage = finite(input.primaryVoltage, 'Primary voltage');
      const load = positive(input.loadResistance, 'Secondary load');
      const ratio = secondaryTurns / primaryTurns;
      return result({ turnsRatio: round(ratio), secondaryVoltage: round(primaryVoltage * ratio), reflectedPrimaryLoad: round(load / (ratio * ratio)) }, ['Ideal transformer model excludes winding resistance, leakage inductance, magnetizing current, and core loss.']);
    }),

    d('electrical.ac-power-factor', 'Single-phase AC power', 'ac', 'P = VIcosφ; Q = VIsinφ', [
      f('voltage', 'RMS voltage', 120, 'V'), f('current', 'RMS current', 5, 'A'), f('powerFactor', 'Power factor', 0.8, ''), f('leading', 'Leading (+1) or lagging (−1)', -1, '')
    ], input => {
      const voltage = nonnegative(input.voltage, 'RMS voltage');
      const current = nonnegative(input.current, 'RMS current');
      const pf = finite(input.powerFactor, 'Power factor');
      if (Math.abs(pf) > 1) throw new Error('Power factor magnitude must not exceed 1.');
      const sign = finite(input.leading, 'Leading/lagging sign') >= 0 ? 1 : -1;
      const apparent = voltage * current;
      const angle = Math.acos(Math.abs(pf));
      return result({ apparentPower: round(apparent), realPower: round(apparent * Math.abs(pf)), reactivePower: round(sign * apparent * Math.sin(angle)), phaseDegrees: round(sign * angle * 180 / Math.PI) });
    }),

    d('electrical.three-phase-power', 'Balanced three-phase power', 'ac', 'P = √3 VLL IL PF', [
      f('lineVoltage', 'Line voltage', 480, 'V'), f('lineCurrent', 'Line current', 10, 'A'), f('powerFactor', 'Power factor', 0.9, '')
    ], input => {
      const voltage = nonnegative(input.lineVoltage, 'Line voltage');
      const current = nonnegative(input.lineCurrent, 'Line current');
      const pf = finite(input.powerFactor, 'Power factor');
      if (pf < 0 || pf > 1) throw new Error('Power factor must be between 0 and 1.');
      const apparent = Math.sqrt(3) * voltage * current;
      return result({ apparentPower: round(apparent), realPower: round(apparent * pf), phaseVoltageWye: round(voltage / Math.sqrt(3)) });
    }),

    d('electronics.led-resistor', 'LED series resistor', 'analog', 'R = (Vs − Vf)/I', [
      f('supply', 'Supply', 5, 'V'), f('forwardVoltage', 'LED forward voltage', 2, 'V'), f('current', 'Target current', 0.015, 'A')
    ], input => {
      const supply = positive(input.supply, 'Supply');
      const forward = nonnegative(input.forwardVoltage, 'Forward voltage');
      const current = positive(input.current, 'Target current');
      if (forward >= supply) throw new Error('Forward voltage must be below the supply voltage.');
      const resistance = (supply - forward) / current;
      return result({ resistance: round(resistance), resistorPower: round(current * current * resistance), ledPower: round(current * forward) });
    }),

    d('electronics.diode-resistor', 'Diode current-limiting resistor', 'analog', 'R = (Vs − Vf)/I', [
      f('supply', 'Supply', 12, 'V'), f('forwardVoltage', 'Forward voltage', 0.7, 'V'), f('current', 'Target current', 0.01, 'A')
    ], input => {
      const supply = positive(input.supply, 'Supply');
      const forward = nonnegative(input.forwardVoltage, 'Forward voltage');
      const current = positive(input.current, 'Target current');
      if (forward >= supply) throw new Error('Forward voltage must be below supply voltage.');
      const resistance = (supply - forward) / current;
      return result({ resistance: round(resistance), resistorPower: round(current * (supply - forward)) }, ['Constant-forward-voltage approximation only.']);
    }),

    d('electronics.zener-regulator', 'Zener shunt regulator', 'analog', 'Rs = (Vin − Vz)/(IL + Iz)', [
      f('inputVoltage', 'Input voltage', 12, 'V'), f('zenerVoltage', 'Zener voltage', 5.1, 'V'), f('loadCurrent', 'Load current', 0.02, 'A'), f('zenerCurrent', 'Desired zener current', 0.005, 'A')
    ], input => {
      const inputVoltage = positive(input.inputVoltage, 'Input voltage');
      const zenerVoltage = positive(input.zenerVoltage, 'Zener voltage');
      const loadCurrent = nonnegative(input.loadCurrent, 'Load current');
      const zenerCurrent = positive(input.zenerCurrent, 'Zener current');
      if (zenerVoltage >= inputVoltage) throw new Error('Zener voltage must be below input voltage.');
      const resistance = (inputVoltage - zenerVoltage) / (loadCurrent + zenerCurrent);
      return result({ seriesResistance: round(resistance), resistorPower: round((inputVoltage - zenerVoltage) * (loadCurrent + zenerCurrent)), zenerPower: round(zenerVoltage * zenerCurrent) }, ['Check worst-case input, load, zener knee current, and dynamic impedance.']);
    }),

    d('electronics.bjt-base-resistor', 'BJT saturated-switch base resistor', 'analog', 'RB = (Vdrive − VBE)/(IC/βforced)', [
      f('driveVoltage', 'Drive voltage', 3.3, 'V'), f('baseEmitterVoltage', 'VBE', 0.8, 'V'), f('collectorCurrent', 'Collector current', 0.1, 'A'), f('forcedBeta', 'Forced beta', 10, '')
    ], input => {
      const drive = positive(input.driveVoltage, 'Drive voltage');
      const vbe = nonnegative(input.baseEmitterVoltage, 'VBE');
      const collector = positive(input.collectorCurrent, 'Collector current');
      const beta = positive(input.forcedBeta, 'Forced beta');
      if (vbe >= drive) throw new Error('VBE must be below drive voltage.');
      const base = collector / beta;
      return result({ baseCurrent: round(base), baseResistance: round((drive - vbe) / base), drivePower: round(drive * base) }, ['Use transistor curves and switching-time requirements for final design.']);
    }),

    d('electronics.mosfet-gate-drive', 'MOSFET gate-drive timing', 'analog', 'Ig = Qg/tr; Rg ≈ (Vdrive/Ig) − Rdriver', [
      f('gateCharge', 'Total gate charge', 0.00000003, 'C'), f('riseTime', 'Desired rise time', 0.0000001, 's'), f('driveVoltage', 'Gate-drive voltage', 10, 'V'), f('driverResistance', 'Driver output resistance', 2, 'Ω')
    ], input => {
      const charge = positive(input.gateCharge, 'Gate charge');
      const rise = positive(input.riseTime, 'Rise time');
      const drive = positive(input.driveVoltage, 'Drive voltage');
      const driver = nonnegative(input.driverResistance, 'Driver resistance');
      const current = charge / rise;
      return result({ averageGateCurrent: round(current), suggestedExternalResistance: round(Math.max(0, drive / current - driver)), gateEnergyPerTransition: round(charge * drive) }, ['Gate charge is nonlinear; use the manufacturer gate-charge curve and driver peak-current limits.']);
    }),

    d('electronics.opamp-inverting', 'Inverting op-amp', 'analog', 'Av = −Rf/Rin', [
      f('inputVoltage', 'Input voltage', 0.1, 'V'), f('inputResistance', 'Input resistance', 10000, 'Ω'), f('feedbackResistance', 'Feedback resistance', 100000, 'Ω'), f('outputLimit', 'Output swing limit', 4.5, 'V')
    ], input => {
      const vin = finite(input.inputVoltage, 'Input voltage');
      const rin = positive(input.inputResistance, 'Input resistance');
      const rf = positive(input.feedbackResistance, 'Feedback resistance');
      const limit = positive(input.outputLimit, 'Output limit');
      const gain = -rf / rin;
      const ideal = gain * vin;
      return result({ gain: round(gain), idealOutput: round(ideal), limitedOutput: round(clamp(ideal, -limit, limit)), saturated: Math.abs(ideal) > limit });
    }),

    d('electronics.opamp-noninverting', 'Non-inverting op-amp', 'analog', 'Av = 1 + Rf/Rg', [
      f('inputVoltage', 'Input voltage', 0.1, 'V'), f('groundResistance', 'Ground resistance', 10000, 'Ω'), f('feedbackResistance', 'Feedback resistance', 90000, 'Ω'), f('outputLimit', 'Output swing limit', 4.5, 'V')
    ], input => {
      const vin = finite(input.inputVoltage, 'Input voltage');
      const rg = positive(input.groundResistance, 'Ground resistance');
      const rf = positive(input.feedbackResistance, 'Feedback resistance');
      const limit = positive(input.outputLimit, 'Output limit');
      const gain = 1 + rf / rg;
      const ideal = gain * vin;
      return result({ gain: round(gain), idealOutput: round(ideal), limitedOutput: round(clamp(ideal, -limit, limit)), saturated: Math.abs(ideal) > limit });
    }),

    d('electronics.instrumentation-amplifier', 'Instrumentation-amplifier gain', 'analog', 'G = 1 + K/Rg', [
      f('differentialInput', 'Differential input', 0.01, 'V'), f('gainResistance', 'Gain resistance', 1000, 'Ω'), f('gainConstant', 'Gain constant', 50000, 'Ω'), f('referenceVoltage', 'Reference voltage', 1.65, 'V')
    ], input => {
      const differential = finite(input.differentialInput, 'Differential input');
      const rg = positive(input.gainResistance, 'Gain resistance');
      const constant = positive(input.gainConstant, 'Gain constant');
      const reference = finite(input.referenceVoltage, 'Reference voltage');
      const gain = 1 + constant / rg;
      return result({ gain: round(gain), outputVoltage: round(reference + gain * differential) }, ['Gain equation is device-specific; verify the selected amplifier datasheet.']);
    }),

    d('electronics.logic-margin', 'Digital logic noise margins', 'digital', 'NMH = VOHmin − VIHmin; NML = VILmax − VOLmax', [
      f('vohMin', 'VOH minimum', 2.4, 'V'), f('vihMin', 'VIH minimum', 2, 'V'), f('vilMax', 'VIL maximum', 0.8, 'V'), f('volMax', 'VOL maximum', 0.4, 'V')
    ], input => {
      const voh = finite(input.vohMin, 'VOH minimum');
      const vih = finite(input.vihMin, 'VIH minimum');
      const vil = finite(input.vilMax, 'VIL maximum');
      const vol = finite(input.volMax, 'VOL maximum');
      return result({ highNoiseMargin: round(voh - vih), lowNoiseMargin: round(vil - vol), validOrdering: voh >= vih && vil >= vol });
    }),

    d('electronics.propagation-budget', 'Logic propagation-delay budget', 'digital', 'td,total = N·td + route + setup', [
      f('stages', 'Logic stages', 4, ''), f('delayPerStage', 'Delay per stage', 0.00000001, 's'), f('routeDelay', 'Route delay', 0.000000005, 's'), f('setupTime', 'Setup time', 0.000000005, 's')
    ], input => {
      const stages = Math.max(1, Math.round(positive(input.stages, 'Stages')));
      const stage = nonnegative(input.delayPerStage, 'Delay per stage');
      const route = nonnegative(input.routeDelay, 'Route delay');
      const setup = nonnegative(input.setupTime, 'Setup time');
      const total = stages * stage + route + setup;
      return result({ totalDelay: round(total), maximumClockFrequency: round(1 / total) }, ['Clock skew, jitter, hold time, and process-voltage-temperature corners are excluded.']);
    }),

    d('electronics.debounce-rc', 'RC switch debounce', 'digital', 'τ = RC', [
      f('resistance', 'Resistance', 10000, 'Ω'), f('capacitance', 'Capacitance', 0.000001, 'F'), f('thresholdFraction', 'Threshold fraction', 0.7, '')
    ], input => {
      const resistance = positive(input.resistance, 'Resistance');
      const capacitance = positive(input.capacitance, 'Capacitance');
      const threshold = finite(input.thresholdFraction, 'Threshold fraction');
      if (!(threshold > 0 && threshold < 1)) throw new Error('Threshold fraction must be between 0 and 1.');
      const tau = resistance * capacitance;
      return result({ timeConstant: round(tau), risingThresholdTime: round(-tau * Math.log(1 - threshold)), fallingThresholdTime: round(-tau * Math.log(threshold)) }, ['Use Schmitt-trigger input thresholds or firmware debounce for robust switching.']);
    }),

    d('electronics.pullup-resistor', 'Digital pull-up resistor bounds', 'digital', 'Rmax=(Vdd−VIH)/Ileak; Rmin=(Vdd−VOL)/Isink', [
      f('supply', 'Supply', 3.3, 'V'), f('vihMin', 'VIH minimum', 2, 'V'), f('leakage', 'Input leakage', 0.000001, 'A'), f('volMax', 'VOL maximum', 0.4, 'V'), f('sinkCurrent', 'Allowed sink current', 0.003, 'A')
    ], input => {
      const supply = positive(input.supply, 'Supply');
      const vih = finite(input.vihMin, 'VIH minimum');
      const leakage = positive(input.leakage, 'Leakage current');
      const vol = finite(input.volMax, 'VOL maximum');
      const sink = positive(input.sinkCurrent, 'Sink current');
      const maximum = (supply - vih) / leakage;
      const minimum = (supply - vol) / sink;
      return result({ minimumResistance: round(minimum), maximumResistance: round(maximum), feasible: minimum <= maximum });
    }),

    d('embedded.adc-quantization', 'ADC resolution and quantization', 'embedded', 'LSB = Vref/2ᴺ', [
      f('bits', 'Resolution', 12, 'bits'), f('reference', 'Reference voltage', 3.3, 'V'), f('inputVoltage', 'Input voltage', 1.65, 'V')
    ], input => {
      const bits = Math.round(positive(input.bits, 'Resolution'));
      if (bits > 32) throw new Error('Resolution must not exceed 32 bits.');
      const reference = positive(input.reference, 'Reference voltage');
      const voltage = nonnegative(input.inputVoltage, 'Input voltage');
      const levels = 2 ** bits;
      const lsb = reference / levels;
      const code = clamp(Math.round(voltage / lsb), 0, levels - 1);
      const quantized = code * lsb;
      return result({ levels, lsbVoltage: round(lsb), code, quantizedVoltage: round(quantized), quantizationError: round(quantized - voltage) });
    }, [], 'embeddedRecords'),

    d('embedded.sensor-scaling', 'Linear sensor calibration', 'embedded', 'y = y₀ + (x−x₀)(y₁−y₀)/(x₁−x₀)', [
      f('raw', 'Raw reading', 2048, ''), f('rawLow', 'Raw low', 0, ''), f('rawHigh', 'Raw high', 4095, ''), f('engineeringLow', 'Engineering low', 0, ''), f('engineeringHigh', 'Engineering high', 100, '')
    ], input => {
      const raw = finite(input.raw, 'Raw reading');
      const rawLow = finite(input.rawLow, 'Raw low');
      const rawHigh = finite(input.rawHigh, 'Raw high');
      const low = finite(input.engineeringLow, 'Engineering low');
      const high = finite(input.engineeringHigh, 'Engineering high');
      if (rawHigh === rawLow) throw new Error('Raw calibration points must differ.');
      const value = low + (raw - rawLow) * (high - low) / (rawHigh - rawLow);
      return result({ engineeringValue: round(value), normalizedFraction: round((raw - rawLow) / (rawHigh - rawLow)) });
    }, ['Linear two-point calibration only.'], 'embeddedRecords'),

    d('embedded.pwm-average', 'PWM average and RMS voltage', 'embedded', 'Vavg = DV; Vrms = V√D', [
      f('supply', 'Supply', 12, 'V'), f('duty', 'Duty cycle', 50, '%'), f('frequency', 'PWM frequency', 20000, 'Hz')
    ], input => {
      const supply = nonnegative(input.supply, 'Supply');
      const duty = percent(input.duty, 'Duty cycle');
      const frequency = positive(input.frequency, 'PWM frequency');
      return result({ averageVoltage: round(supply * duty), rmsVoltage: round(supply * Math.sqrt(duty)), period: round(1 / frequency), onTime: round(duty / frequency) });
    }, [], 'embeddedRecords'),

    d('embedded.timer-frequency', 'Timer compare and overflow', 'embedded', 'fout = fclk/[prescaler·(TOP+1)]', [
      f('clock', 'Clock frequency', 16000000, 'Hz'), f('prescaler', 'Prescaler', 64, ''), f('top', 'Timer TOP', 249, '')
    ], input => {
      const clock = positive(input.clock, 'Clock frequency');
      const prescaler = positive(input.prescaler, 'Prescaler');
      const top = Math.round(nonnegative(input.top, 'Timer TOP'));
      const frequency = clock / (prescaler * (top + 1));
      return result({ outputFrequency: round(frequency), period: round(1 / frequency), ticksPerPeriod: top + 1 });
    }, [], 'embeddedRecords'),

    d('embedded.uart-baud', 'UART baud-rate error', 'embedded', 'baud = fclk/(oversampling·divisor)', [
      f('clock', 'Peripheral clock', 16000000, 'Hz'), f('targetBaud', 'Target baud', 115200, 'bit/s'), f('oversampling', 'Oversampling', 16, '')
    ], input => {
      const clock = positive(input.clock, 'Peripheral clock');
      const target = positive(input.targetBaud, 'Target baud');
      const oversampling = positive(input.oversampling, 'Oversampling');
      const divisor = Math.max(1, Math.round(clock / (oversampling * target)));
      const actual = clock / (oversampling * divisor);
      const error = 100 * (actual - target) / target;
      return result({ divisor, actualBaud: round(actual), errorPercent: round(error), withinTwoPercent: Math.abs(error) <= 2 }, Math.abs(error) > 2 ? ['Baud error exceeds a common ±2% screening target.'] : [], 'SCREENING_ONLY');
    }, [], 'interfaceRecords'),

    d('embedded.i2c-pullup', 'I²C pull-up bounds', 'embedded', 'Rmin=(Vdd−VOL)/IOL; Rmax=tr/(0.8473Cb)', [
      f('voltage', 'Bus voltage', 3.3, 'V'), f('volMax', 'VOL maximum', 0.4, 'V'), f('sinkCurrent', 'Sink current', 0.003, 'A'), f('busCapacitance', 'Bus capacitance', 0.0000001, 'F'), f('riseTime', 'Allowed rise time', 0.000001, 's')
    ], input => {
      const voltage = positive(input.voltage, 'Bus voltage');
      const vol = finite(input.volMax, 'VOL maximum');
      const sink = positive(input.sinkCurrent, 'Sink current');
      const capacitance = positive(input.busCapacitance, 'Bus capacitance');
      const rise = positive(input.riseTime, 'Rise time');
      const minimum = (voltage - vol) / sink;
      const maximum = rise / (0.8473 * capacitance);
      return result({ minimumResistance: round(minimum), maximumResistance: round(maximum), feasible: minimum <= maximum }, minimum > maximum ? ['No resistor satisfies both sink-current and rise-time constraints.'] : [], 'SCREENING_ONLY');
    }, [], 'interfaceRecords'),

    d('embedded.spi-throughput', 'SPI payload throughput', 'embedded', 'payload rate = fclk·η/bits-per-payload', [
      f('clock', 'SPI clock', 8000000, 'Hz'), f('efficiency', 'Protocol efficiency', 80, '%'), f('bitsPerPayload', 'Bits per payload', 16, 'bits')
    ], input => {
      const clock = positive(input.clock, 'SPI clock');
      const efficiency = percent(input.efficiency, 'Efficiency');
      const bits = positive(input.bitsPerPayload, 'Bits per payload');
      return result({ rawBitRate: round(clock), effectiveBitRate: round(clock * efficiency), payloadsPerSecond: round(clock * efficiency / bits), bytesPerSecond: round(clock * efficiency / 8) });
    }, [], 'interfaceRecords'),

    d('embedded.can-bus-load', 'CAN bus-load estimate', 'embedded', 'load = frames·bits/frame / bitrate', [
      f('framesPerSecond', 'Frames per second', 500, 'frame/s'), f('bitsPerFrame', 'Worst-case bits per frame', 128, 'bits'), f('bitrate', 'Bus bitrate', 500000, 'bit/s')
    ], input => {
      const frames = nonnegative(input.framesPerSecond, 'Frames per second');
      const bits = positive(input.bitsPerFrame, 'Bits per frame');
      const bitrate = positive(input.bitrate, 'Bitrate');
      const load = frames * bits / bitrate;
      return result({ busLoadFraction: round(load), busLoadPercent: round(100 * load), remainingCapacityPercent: round(100 * (1 - load)) }, load > 0.7 ? ['Estimated bus load exceeds a conservative 70% screening threshold.'] : [], 'SCREENING_ONLY');
    }, ['Include arbitration, bit stuffing, retransmissions, and error frames in final analysis.'], 'interfaceRecords'),

    d('embedded.battery-runtime', 'Battery runtime with duty cycle', 'embedded', 'Iavg = Σ(DᵢIᵢ); t = capacity·derating/Iavg', [
      f('capacity', 'Battery capacity', 2000, 'mAh'), f('activeCurrent', 'Active current', 100, 'mA'), f('activeDuty', 'Active duty', 10, '%'), f('sleepCurrent', 'Sleep current', 0.1, 'mA'), f('derating', 'Usable capacity', 80, '%')
    ], input => {
      const capacity = positive(input.capacity, 'Capacity');
      const active = nonnegative(input.activeCurrent, 'Active current');
      const duty = percent(input.activeDuty, 'Active duty');
      const sleep = nonnegative(input.sleepCurrent, 'Sleep current');
      const derating = percent(input.derating, 'Usable capacity');
      const average = active * duty + sleep * (1 - duty);
      return result({ averageCurrent: round(average), runtimeHours: round(capacity * derating / average), runtimeDays: round(capacity * derating / average / 24) }, ['Battery self-discharge, pulse capability, temperature, aging, regulator loss, and cutoff voltage are excluded.']);
    }, [], 'deviceProfiles'),

    d('power.linear-regulator', 'Linear-regulator dissipation', 'power', 'Ploss = (Vin−Vout)I', [
      f('inputVoltage', 'Input voltage', 12, 'V'), f('outputVoltage', 'Output voltage', 5, 'V'), f('current', 'Load current', 0.2, 'A'), f('thetaJA', 'Thermal resistance θJA', 50, '°C/W'), f('ambient', 'Ambient temperature', 25, '°C')
    ], input => {
      const vin = positive(input.inputVoltage, 'Input voltage');
      const vout = nonnegative(input.outputVoltage, 'Output voltage');
      const current = nonnegative(input.current, 'Load current');
      const theta = positive(input.thetaJA, 'Thermal resistance');
      const ambient = finite(input.ambient, 'Ambient temperature');
      if (vout > vin) throw new Error('Output voltage cannot exceed input voltage for a linear regulator.');
      const loss = (vin - vout) * current;
      return result({ outputPower: round(vout * current), powerLoss: round(loss), efficiencyPercent: round(100 * vout / vin), estimatedJunctionTemperature: round(ambient + loss * theta) }, ['Dropout voltage, quiescent current, PCB copper area, airflow, and transient load are excluded.'], 'SCREENING_ONLY');
    }, [], 'electronicsRecords'),

    d('power.buck-duty', 'Ideal buck-converter duty cycle', 'power', 'D ≈ Vout/Vin', [
      f('inputVoltage', 'Input voltage', 12, 'V'), f('outputVoltage', 'Output voltage', 5, 'V'), f('efficiency', 'Estimated efficiency', 90, '%'), f('outputCurrent', 'Output current', 1, 'A')
    ], input => {
      const vin = positive(input.inputVoltage, 'Input voltage');
      const vout = positive(input.outputVoltage, 'Output voltage');
      const efficiency = percent(input.efficiency, 'Efficiency');
      const current = nonnegative(input.outputCurrent, 'Output current');
      if (vout >= vin) throw new Error('Buck output voltage must be below input voltage.');
      const outputPower = vout * current;
      return result({ idealDutyCycle: round(vout / vin), idealDutyPercent: round(100 * vout / vin), inputCurrentEstimate: round(outputPower / (vin * efficiency)), powerLossEstimate: round(outputPower * (1 / efficiency - 1)) }, ['Control-mode limits, switch drops, inductor ripple, minimum on-time, and stability are excluded.']);
    }, [], 'electronicsRecords'),

    d('power.boost-duty', 'Ideal boost-converter duty cycle', 'power', 'D ≈ 1 − Vin/Vout', [
      f('inputVoltage', 'Input voltage', 5, 'V'), f('outputVoltage', 'Output voltage', 12, 'V'), f('efficiency', 'Estimated efficiency', 85, '%'), f('outputCurrent', 'Output current', 0.5, 'A')
    ], input => {
      const vin = positive(input.inputVoltage, 'Input voltage');
      const vout = positive(input.outputVoltage, 'Output voltage');
      const efficiency = percent(input.efficiency, 'Efficiency');
      const current = nonnegative(input.outputCurrent, 'Output current');
      if (vout <= vin) throw new Error('Boost output voltage must exceed input voltage.');
      const outputPower = vout * current;
      const duty = 1 - vin / vout;
      return result({ idealDutyCycle: round(duty), idealDutyPercent: round(100 * duty), inputCurrentEstimate: round(outputPower / (vin * efficiency)), switchOffVoltageIdeal: round(vout) }, ['Switch current stress, diode/synchronous loss, ripple, and control-loop stability are excluded.']);
    }, [], 'electronicsRecords'),

    d('power.capacitor-ripple', 'Output-capacitor ripple estimate', 'power', 'ΔV ≈ I·D/(Cfsw) + ΔI·ESR', [
      f('loadCurrent', 'Load current', 1, 'A'), f('duty', 'Ripple duty fraction', 0.5, ''), f('capacitance', 'Capacitance', 0.00047, 'F'), f('switchingFrequency', 'Switching frequency', 100000, 'Hz'), f('rippleCurrent', 'Capacitor ripple current', 0.2, 'A'), f('esr', 'ESR', 0.05, 'Ω')
    ], input => {
      const current = nonnegative(input.loadCurrent, 'Load current');
      const duty = finite(input.duty, 'Duty fraction');
      if (duty < 0 || duty > 1) throw new Error('Duty fraction must be between 0 and 1.');
      const capacitance = positive(input.capacitance, 'Capacitance');
      const frequency = positive(input.switchingFrequency, 'Switching frequency');
      const rippleCurrent = nonnegative(input.rippleCurrent, 'Ripple current');
      const esr = nonnegative(input.esr, 'ESR');
      return result({ capacitiveRipple: round(current * duty / (capacitance * frequency)), esrRipple: round(rippleCurrent * esr), totalRippleEstimate: round(current * duty / (capacitance * frequency) + rippleCurrent * esr) });
    }, [], 'electronicsRecords'),

    d('power.thermal-junction', 'Junction-temperature estimate', 'power', 'Tj = Ta + PθJA', [
      f('ambient', 'Ambient temperature', 25, '°C'), f('power', 'Device dissipation', 1, 'W'), f('thetaJA', 'Thermal resistance θJA', 50, '°C/W'), f('junctionLimit', 'Junction limit', 150, '°C')
    ], input => {
      const ambient = finite(input.ambient, 'Ambient temperature');
      const power = nonnegative(input.power, 'Power');
      const theta = positive(input.thetaJA, 'Thermal resistance');
      const limit = finite(input.junctionLimit, 'Junction limit');
      const junction = ambient + power * theta;
      return result({ junctionTemperature: round(junction), margin: round(limit - junction), withinLimit: junction <= limit }, junction > limit ? ['Estimated junction temperature exceeds the supplied limit.'] : []);
    }, [], 'hardwareValidationRecords'),

    d('signals.nyquist', 'Sampling and alias screening', 'signals', 'fs ≥ 2fmax', [
      f('signalFrequency', 'Highest signal frequency', 1000, 'Hz'), f('sampleRate', 'Sample rate', 10000, 'sample/s')
    ], input => {
      const signal = positive(input.signalFrequency, 'Signal frequency');
      const sample = positive(input.sampleRate, 'Sample rate');
      const nyquist = sample / 2;
      const nearestAlias = Math.abs(signal - Math.round(signal / sample) * sample);
      return result({ nyquistFrequency: round(nyquist), oversamplingRatio: round(sample / (2 * signal)), satisfiesNyquist: sample >= 2 * signal, nearestAliasFrequency: round(nearestAlias) }, sample < 2 * signal ? ['The sample rate violates the Nyquist screening criterion.'] : [], 'SCREENING_ONLY');
    }, ['Anti-alias filtering and spectral content above the stated maximum frequency still require analysis.']),

    d('signals.enob-snr', 'ADC ENOB and SNR', 'signals', 'SNRideal ≈ 6.02N + 1.76 dB', [
      f('bits', 'Nominal resolution', 12, 'bits'), f('measuredSnr', 'Measured SNR', 65, 'dB')
    ], input => {
      const bits = positive(input.bits, 'Nominal resolution');
      const measured = finite(input.measuredSnr, 'Measured SNR');
      return result({ idealSnrDb: round(6.02 * bits + 1.76), effectiveNumberOfBits: round((measured - 1.76) / 6.02), snrDeficitDb: round(6.02 * bits + 1.76 - measured) });
    }),

    d('signals.sensor-divider-loading', 'Sensor divider and ADC loading', 'signals', 'Rsource = R1∥R2', [
      f('r1', 'Upper resistance', 100000, 'Ω'), f('r2', 'Lower resistance', 100000, 'Ω'), f('adcInputResistance', 'ADC input resistance', 1000000, 'Ω'), f('inputVoltage', 'Input voltage', 5, 'V')
    ], input => {
      const r1 = positive(input.r1, 'Upper resistance');
      const r2 = positive(input.r2, 'Lower resistance');
      const adc = positive(input.adcInputResistance, 'ADC input resistance');
      const vin = finite(input.inputVoltage, 'Input voltage');
      const loadedLower = 1 / (1 / r2 + 1 / adc);
      const ideal = vin * r2 / (r1 + r2);
      const loaded = vin * loadedLower / (r1 + loadedLower);
      return result({ sourceResistance: round(1 / (1 / r1 + 1 / r2)), idealVoltage: round(ideal), loadedVoltage: round(loaded), loadingErrorPercent: round(100 * (loaded - ideal) / ideal) }, ['ADC sample-and-hold acquisition time and source-capacitance effects are excluded.']);
    })
  ];

  const definitionMap = Object.fromEntries(definitions.map(item => [item.id, item]));

  function run(id, inputs) {
    const definition = definitionMap[id];
    if (!definition) throw new Error(`Unknown electrical method: ${id}`);
    const calculation = definition.compute(inputs || {});
    return {
      ...calculation,
      methodId: id,
      methodVersion: VERSION,
      title: definition.name,
      equation: definition.equation,
      assumptions: definition.assumptions,
      inputs: { ...(inputs || {}) },
      createdAt: now(),
      audit: {
        methodFingerprint: fingerprint({ id, version: VERSION, equation: definition.equation }),
        inputFingerprint: fingerprint(inputs || {}),
        outputFingerprint: fingerprint(calculation.outputs || {})
      }
    };
  }

  const benchmarks = [
    ['electrical.ohms-law', { voltage: 12, resistance: 6 }, output => Math.abs(output.current - 2) < 1e-12],
    ['electrical.resistors-series', { resistances: '10,20,30' }, output => output.equivalentResistance === 60],
    ['electrical.resistors-parallel', { resistances: '100,100' }, output => Math.abs(output.equivalentResistance - 50) < 1e-10],
    ['electrical.rc-charge', { resistance: 1000, capacitance: 0.000001, time: 0.001, supply: 5 }, output => Math.abs(output.chargeVoltage - 3.160602794) < 1e-8],
    ['electrical.resonance', { resistance: 10, inductance: 0.01, capacitance: 0.000001 }, output => Math.abs(output.resonantFrequency - 1591.549431) < 1e-5],
    ['electronics.opamp-inverting', { inputVoltage: 0.1, inputResistance: 10000, feedbackResistance: 100000, outputLimit: 4.5 }, output => output.gain === -10 && output.idealOutput === -1],
    ['embedded.adc-quantization', { bits: 10, reference: 3.3, inputVoltage: 1.65 }, output => output.levels === 1024 && output.code >= 511 && output.code <= 512],
    ['embedded.pwm-average', { supply: 12, duty: 25, frequency: 1000 }, output => output.averageVoltage === 3 && output.rmsVoltage === 6],
    ['embedded.timer-frequency', { clock: 16000000, prescaler: 64, top: 249 }, output => output.outputFrequency === 1000],
    ['power.thermal-junction', { ambient: 25, power: 1, thetaJA: 50, junctionLimit: 150 }, output => output.junctionTemperature === 75 && output.withinLimit === true],
    ['signals.nyquist', { signalFrequency: 1000, sampleRate: 10000 }, output => output.satisfiesNyquist === true && output.nyquistFrequency === 5000]
  ];

  function runBenchmarks() {
    return benchmarks.map(([id, inputs, check]) => {
      try {
        const analysis = run(id, inputs);
        return { id, passed: Boolean(check(analysis.outputs)), outputs: analysis.outputs };
      } catch (error) {
        return { id, passed: false, error: error.message };
      }
    });
  }

  const boards = {
    'arduino-uno': { name: 'Arduino Uno', logicVoltage: 5, adcBits: 10, buses: ['UART', 'I2C', 'SPI'], firmware: 'arduino-cpp' },
    'esp32': { name: 'ESP32', logicVoltage: 3.3, adcBits: 12, buses: ['UART', 'I2C', 'SPI', 'CAN', 'Wi-Fi', 'BLE'], firmware: 'esp-idf-arduino' },
    'rp2040': { name: 'Raspberry Pi Pico / RP2040', logicVoltage: 3.3, adcBits: 12, buses: ['UART', 'I2C', 'SPI', 'PIO'], firmware: 'pico-sdk-micropython' },
    'stm32-nucleo': { name: 'STM32 Nucleo', logicVoltage: 3.3, adcBits: 12, buses: ['UART', 'I2C', 'SPI', 'CAN'], firmware: 'stm32-hal' },
    'raspberry-pi': { name: 'Raspberry Pi', logicVoltage: 3.3, adcBits: 0, buses: ['UART', 'I2C', 'SPI', 'USB', 'Ethernet'], firmware: 'linux-python-cpp' }
  };

  const firmwareTemplates = {
    'arduino-cpp': `#include <Arduino.h>\nconstexpr uint8_t SENSOR_PIN = A0;\nvoid setup(){ Serial.begin(115200); }\nvoid loop(){ const int raw=analogRead(SENSOR_PIN); Serial.println(raw); delay(100); }\n`,
    'micropython': `from machine import ADC, Pin\nfrom time import sleep_ms\nsensor = ADC(Pin(26))\nwhile True:\n    print(sensor.read_u16())\n    sleep_ms(100)\n`,
    'rust-embedded': `#![no_std]\n#![no_main]\n// Select a board HAL and configure clocks, GPIO, ADC, timers, and panic behavior.\n// Keep pin assignments and electrical limits in the Lab device profile.\n`,
    'linux-python': `from pathlib import Path\n# Replace this placeholder with a supported GPIO/I2C/SPI library and explicit device permissions.\nprint({"status": "hardware adapter required", "platform": Path('/proc/device-tree/model').exists()})\n`
  };

  function makeDeviceProfile(input = {}) {
    const board = boards[input.board] || boards['esp32'];
    return {
      schema: 'sc-lab-embedded-device/1.0', version: VERSION, id: `device-${Date.now()}`,
      name: String(input.name || board.name), boardId: input.board || 'esp32', board,
      supplyVoltage: finite(input.supplyVoltage ?? board.logicVoltage, 'Supply voltage'),
      interfaces: Array.isArray(input.interfaces) ? input.interfaces : board.buses.slice(),
      sensors: Array.isArray(input.sensors) ? input.sensors : [],
      actuators: Array.isArray(input.actuators) ? input.actuators : [],
      firmwareTarget: String(input.firmwareTarget || board.firmware),
      createdAt: now(),
      audit: { fingerprint: fingerprint({ input, board, version: VERSION }) },
      boundary: 'A planning record only; verify pin multiplexing, voltage domains, current limits, protections, and board documentation.'
    };
  }

  function validateInterface(input = {}) {
    const sourceVoltage = positive(input.sourceVoltage, 'Source voltage');
    const targetVoltage = positive(input.targetVoltage, 'Target voltage');
    const sourceHigh = finite(input.sourceHigh ?? sourceVoltage * 0.8, 'Source high');
    const targetVih = finite(input.targetVih ?? targetVoltage * 0.7, 'Target VIH');
    const sourceLow = finite(input.sourceLow ?? sourceVoltage * 0.1, 'Source low');
    const targetVil = finite(input.targetVil ?? targetVoltage * 0.3, 'Target VIL');
    const overvoltage = sourceHigh > targetVoltage + 0.3;
    return {
      schema: 'sc-lab-interface-validation/1.0', version: VERSION,
      sourceVoltage, targetVoltage, highMargin: round(sourceHigh - targetVih), lowMargin: round(targetVil - sourceLow),
      highRecognized: sourceHigh >= targetVih, lowRecognized: sourceLow <= targetVil,
      overvoltageRisk: overvoltage,
      status: sourceHigh >= targetVih && sourceLow <= targetVil && !overvoltage ? 'PASS_SCREENING' : 'REVIEW_REQUIRED',
      warnings: overvoltage ? ['Source high level may exceed the target absolute-maximum input voltage. Use an appropriate level shifter or divider after engineering review.'] : []
    };
  }

  function fieldHTML(field) {
    const type = field.type || 'number';
    const step = type === 'number' ? ' step="any"' : '';
    return `<label><span>${esc(field.label)}${field.unit ? ` <small>${esc(field.unit)}</small>` : ''}</span><input type="${esc(type)}"${step} data-electrical-field="${esc(field.id)}" value="${esc(field.value)}"></label>`;
  }

  function toolHTML(definition) {
    return `<article class="sc-lab-tool sc-lab-electrical-tool" data-electrical-tool="${esc(definition.id)}">
      <div class="sc-lab-electrical-tool-head"><div><span class="sc-lab-method-id">${esc(definition.id)}</span><h4>${esc(definition.name)}</h4></div><span class="sc-lab-version-chip">v${VERSION}</span></div>
      <details class="sc-lab-electrical-method"><summary>Method, equation, and assumptions</summary><p><code>${esc(definition.equation)}</code></p><ul>${definition.assumptions.map(item => `<li>${esc(item)}</li>`).join('') || '<li>Screening-level idealized method.</li>'}</ul></details>
      <div class="sc-lab-inline-fields">${definition.fields.map(fieldHTML).join('')}</div>
      <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-electrical-run>Run analysis</button><button type="button" class="sc-lab-button" data-electrical-save>Save</button><button type="button" class="sc-lab-button" data-electrical-note>Add to notebook</button></div>
      <div class="sc-lab-electrical-result" data-electrical-result aria-live="polite"></div>
    </article>`;
  }

  function collect(card) {
    const input = {};
    card.querySelectorAll('[data-electrical-field]').forEach(element => { input[element.dataset.electricalField] = element.value; });
    return input;
  }

  function outputHTML(analysis) {
    const rows = Object.entries(analysis.outputs || {}).map(([key, value]) => `<tr><th scope="row">${esc(key)}</th><td>${esc(typeof value === 'number' ? String(round(value)) : String(value))}</td></tr>`).join('');
    const warnings = analysis.validation?.warnings || [];
    return `<div class="sc-lab-electrical-status"><strong>${esc(analysis.validation?.status || 'CALCULATED')}</strong><span>${esc(analysis.audit?.outputFingerprint || '')}</span></div><div class="sc-lab-table-wrap"><table><thead><tr><th>Output</th><th>Value</th></tr></thead><tbody>${rows}</tbody></table></div>${warnings.length ? `<details><summary>${warnings.length} validation notes</summary><ul>${warnings.map(item => `<li>${esc(item)}</li>`).join('')}</ul></details>` : ''}`;
  }

  function saveAnalysis(projects, definition, input, analysis) {
    projects.add(definition.collection, { type: definition.name, methodId: definition.id, inputs: input, result: analysis, recordedAt: now() }, `${definition.name} saved`);
    projects.add('electricalRecords', { type: definition.name, methodId: definition.id, category: definition.tab, recordedAt: now(), analysisFingerprint: analysis.audit.outputFingerprint }, `Electrical index updated: ${definition.name}`);
    if (definition.id.startsWith('embedded.')) projects.add('embeddedRecords', { type: definition.name, methodId: definition.id, recordedAt: now() }, `Embedded index updated: ${definition.name}`);
    if (definition.id.startsWith('electronics.') || definition.id.startsWith('power.')) projects.add('electronicsRecords', { type: definition.name, methodId: definition.id, recordedAt: now() }, `Electronics index updated: ${definition.name}`);
  }

  function initDeviceStudio(root, projects) {
    const boardSelect = root.querySelector('[data-electrical-board]');
    const profileTarget = root.querySelector('[data-electrical-device-output]');
    const firmwareTarget = root.querySelector('[data-electrical-firmware-output]');
    if (!boardSelect || !profileTarget) return;
    boardSelect.innerHTML = Object.entries(boards).map(([id, board]) => `<option value="${esc(id)}">${esc(board.name)}</option>`).join('');
    root.querySelector('[data-electrical-create-device]')?.addEventListener('click', () => {
      try {
        const profile = makeDeviceProfile({
          board: boardSelect.value,
          name: root.querySelector('[data-electrical-device-name]')?.value,
          supplyVoltage: root.querySelector('[data-electrical-device-voltage]')?.value
        });
        profileTarget.textContent = JSON.stringify(profile, null, 2);
        root._scElectricalDeviceProfile = profile;
      } catch (error) { profileTarget.textContent = `Error: ${error.message}`; }
    });
    root.querySelector('[data-electrical-save-device]')?.addEventListener('click', () => {
      if (!root._scElectricalDeviceProfile) root.querySelector('[data-electrical-create-device]')?.click();
      if (!root._scElectricalDeviceProfile) return;
      projects.add('deviceProfiles', root._scElectricalDeviceProfile, `Embedded device profile saved: ${root._scElectricalDeviceProfile.name}`);
      if (typeof U.toast === 'function') U.toast(root, 'Embedded device profile saved.');
    });
    root.querySelector('[data-electrical-firmware-template]')?.addEventListener('change', event => {
      firmwareTarget.textContent = firmwareTemplates[event.target.value] || '';
    });
    root.querySelector('[data-electrical-save-firmware]')?.addEventListener('click', () => {
      const templateId = root.querySelector('[data-electrical-firmware-template]')?.value || 'arduino-cpp';
      const source = firmwareTemplates[templateId] || '';
      projects.add('firmwareArtifacts', { schema: 'sc-lab-firmware-artifact/1.0', version: VERSION, language: templateId, source, createdAt: now(), fingerprint: fingerprint(source) }, `Firmware template saved: ${templateId}`);
      if (typeof U.toast === 'function') U.toast(root, 'Firmware artifact saved.');
    });
  }

  function initInterfaceStudio(root, projects) {
    const target = root.querySelector('[data-electrical-interface-output]');
    root.querySelector('[data-electrical-validate-interface]')?.addEventListener('click', () => {
      try {
        const record = validateInterface({
          sourceVoltage: root.querySelector('[data-interface-source-voltage]')?.value,
          targetVoltage: root.querySelector('[data-interface-target-voltage]')?.value
        });
        root._scElectricalInterfaceRecord = record;
        target.textContent = JSON.stringify(record, null, 2);
      } catch (error) { target.textContent = `Error: ${error.message}`; }
    });
    root.querySelector('[data-electrical-save-interface]')?.addEventListener('click', () => {
      if (!root._scElectricalInterfaceRecord) root.querySelector('[data-electrical-validate-interface]')?.click();
      if (!root._scElectricalInterfaceRecord) return;
      projects.add('interfaceRecords', { ...root._scElectricalInterfaceRecord, recordedAt: now() }, 'Electrical interface validation saved');
      if (typeof U.toast === 'function') U.toast(root, 'Interface validation saved.');
    });
  }

  function init(root, projects) {
    root.querySelectorAll('[data-electrical-grid]').forEach(grid => {
      grid.innerHTML = definitions.filter(item => item.tab === grid.dataset.electricalGrid).map(toolHTML).join('');
    });
    root.querySelectorAll('[data-electrical-tab]').forEach(button => button.addEventListener('click', () => {
      const selected = button.dataset.electricalTab;
      root.querySelectorAll('[data-electrical-tab]').forEach(item => item.classList.toggle('is-active', item === button));
      root.querySelectorAll('[data-electrical-pane]').forEach(pane => { pane.hidden = pane.dataset.electricalPane !== selected; });
    }));
    root.querySelectorAll('[data-electrical-tool]').forEach(card => {
      const definition = definitionMap[card.dataset.electricalTool];
      let current = null;
      card.querySelector('[data-electrical-run]')?.addEventListener('click', () => {
        try {
          const input = collect(card);
          const analysis = run(definition.id, input);
          current = { input, analysis };
          card.querySelector('[data-electrical-result]').innerHTML = outputHTML(analysis);
          root.dispatchEvent(new CustomEvent('sc-lab:analysis', { detail: analysis, bubbles: true }));
        } catch (error) {
          current = null;
          card.querySelector('[data-electrical-result]').innerHTML = `<div class="sc-lab-validation-error"><strong>Invalid input</strong><p>${esc(error.message)}</p></div>`;
        }
      });
      card.querySelector('[data-electrical-save]')?.addEventListener('click', () => {
        if (!current) card.querySelector('[data-electrical-run]')?.click();
        if (!current) return;
        saveAnalysis(projects, definition, current.input, current.analysis);
        if (typeof U.toast === 'function') U.toast(root, 'Electrical analysis saved.');
      });
      card.querySelector('[data-electrical-note]')?.addEventListener('click', () => {
        if (!current) card.querySelector('[data-electrical-run]')?.click();
        if (!current) return;
        projects.add('notes', { title: `${definition.name} analysis`, body: JSON.stringify(current.analysis, null, 2), tags: ['electrical-electronics-embedded', definition.tab, definition.id] }, `Notebook entry added: ${definition.name}`);
        if (typeof U.toast === 'function') U.toast(root, 'Analysis added to notebook.');
      });
    });
    root.querySelector('[data-electrical-run-benchmarks]')?.addEventListener('click', () => {
      const records = runBenchmarks();
      const passed = records.filter(item => item.passed).length;
      const suite = { schema: 'sc-lab-hardware-validation/1.0', version: VERSION, type: 'electrical-method-benchmark-suite', passed, total: records.length, status: passed === records.length ? 'PASS' : 'FAIL', records, runAt: now(), fingerprint: fingerprint(records) };
      root.querySelector('[data-electrical-benchmark-output]').textContent = JSON.stringify(suite, null, 2);
      projects.add('hardwareValidationRecords', suite, `Electrical validation suite: ${passed}/${records.length} passed`);
    });
    initDeviceStudio(root, projects);
    initInterfaceStudio(root, projects);
  }

  Lab.ElectricalEmbedded = {
    VERSION,
    definitions,
    run,
    runBenchmarks,
    boards,
    firmwareTemplates,
    makeDeviceProfile,
    validateInterface,
    init
  };
})(window);
