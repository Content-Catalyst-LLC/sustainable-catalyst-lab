(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};
  const R = 8.31446261815324;
  const F = 96485.33212;
  const LN10 = Math.log(10);

  function n(value, name) {
    const out = Number(value);
    if (!Number.isFinite(out)) throw new Error(`Invalid ${name}`);
    return out;
  }
  function positive(value, name) {
    const out = n(value, name);
    if (out <= 0) throw new Error(`${name} must be greater than zero`);
    return out;
  }
  function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
  function quadraticPositive(a, b, c) {
    const disc = b * b - 4 * a * c;
    if (disc < 0) throw new Error('No real equilibrium solution');
    const roots = [(-b + Math.sqrt(disc)) / (2 * a), (-b - Math.sqrt(disc)) / (2 * a)];
    const valid = roots.filter(x => x >= 0);
    if (!valid.length) throw new Error('No physically meaningful equilibrium solution');
    return Math.min(...valid);
  }

  function concentration(values) {
    const moles = n(values.moles, 'moles');
    const solutionL = positive(values.solutionL, 'solution volume');
    const soluteG = Number(values.soluteG);
    const solventKg = Number(values.solventKg);
    const solutionG = Number(values.solutionG);
    const molarity = moles / solutionL;
    const result = { molarityMolL: molarity };
    if (Number.isFinite(solventKg) && solventKg > 0) result.molalityMolKg = moles / solventKg;
    if (Number.isFinite(soluteG) && Number.isFinite(solutionG) && solutionG > 0) result.massPercent = 100 * soluteG / solutionG;
    if (Number.isFinite(soluteG)) result.gramsPerLiter = soluteG / solutionL;
    return result;
  }

  function strongAcidBase(values) {
    const concentration = positive(values.concentration, 'concentration');
    const equivalents = positive(values.equivalents || 1, 'equivalents');
    const type = String(values.type || 'acid').toLowerCase();
    const ion = concentration * equivalents;
    if (type === 'acid') return { hydrogenIonMolL: ion, pH: -Math.log10(ion), pOH: 14 + Math.log10(ion) };
    const pOH = -Math.log10(ion);
    return { hydroxideIonMolL: ion, pOH, pH: 14 - pOH };
  }

  function weakAcid(values) {
    const c0 = positive(values.concentration, 'initial concentration');
    const ka = positive(values.ka, 'Ka');
    const x = quadraticPositive(1, ka, -ka * c0);
    return { hydrogenIonMolL: x, pH: -Math.log10(x), percentIonized: 100 * x / c0, approximationRatio: x / c0 };
  }

  function weakBase(values) {
    const c0 = positive(values.concentration, 'initial concentration');
    const kb = positive(values.kb, 'Kb');
    const x = quadraticPositive(1, kb, -kb * c0);
    const pOH = -Math.log10(x);
    return { hydroxideIonMolL: x, pOH, pH: 14 - pOH, percentIonized: 100 * x / c0, approximationRatio: x / c0 };
  }

  function buffer(values) {
    const pKa = n(values.pKa, 'pKa');
    const acid = positive(values.acid, 'acid amount');
    const base = positive(values.base, 'base amount');
    return { pH: pKa + Math.log10(base / acid), ratioBaseToAcid: base / acid };
  }

  function titration(values) {
    const analyteType = String(values.analyteType || 'acid').toLowerCase();
    const analyteC = positive(values.analyteC, 'analyte concentration');
    const analyteMl = positive(values.analyteMl, 'analyte volume');
    const titrantC = positive(values.titrantC, 'titrant concentration');
    const titrantMl = Math.max(0, n(values.titrantMl, 'titrant volume'));
    const analyteEq = analyteC * analyteMl / 1000;
    const titrantEq = titrantC * titrantMl / 1000;
    const totalL = (analyteMl + titrantMl) / 1000;
    const diff = analyteEq - titrantEq;
    let pH;
    if (Math.abs(diff) < 1e-14) pH = 7;
    else if ((analyteType === 'acid' && diff > 0) || (analyteType === 'base' && diff < 0)) pH = -Math.log10(Math.abs(diff) / totalL);
    else pH = 14 + Math.log10(Math.abs(diff) / totalL);
    return {
      equivalenceVolumeMl: analyteEq / titrantC * 1000,
      totalVolumeMl: analyteMl + titrantMl,
      excessEquivalents: Math.abs(diff),
      pH: clamp(pH, 0, 14),
      model: 'strong monoprotic acid/base at 25 °C'
    };
  }

  function solubility(values) {
    const ksp = positive(values.ksp, 'Ksp');
    const cationStoich = positive(values.cationStoich || 1, 'cation coefficient');
    const anionStoich = positive(values.anionStoich || 1, 'anion coefficient');
    const power = cationStoich + anionStoich;
    const factor = Math.pow(cationStoich, cationStoich) * Math.pow(anionStoich, anionStoich);
    const s = Math.pow(ksp / factor, 1 / power);
    return { molarSolubilityMolL: s, cationMolL: cationStoich * s, anionMolL: anionStoich * s };
  }

  function calorimetry(values) {
    const massG = positive(values.massG, 'mass');
    const specificHeat = positive(values.specificHeat, 'specific heat');
    const initialC = n(values.initialC, 'initial temperature');
    const finalC = n(values.finalC, 'final temperature');
    const qJ = massG * specificHeat * (finalC - initialC);
    return { deltaTemperatureC: finalC - initialC, heatJ: qJ, heatKJ: qJ / 1000 };
  }

  function gibbs(values) {
    const deltaHkJ = n(values.deltaHkJ, 'ΔH');
    const deltaSJmolK = n(values.deltaSJmolK, 'ΔS');
    const temperatureK = positive(values.temperatureK, 'temperature');
    const deltaGkJ = deltaHkJ - temperatureK * deltaSJmolK / 1000;
    return { deltaGkJmol: deltaGkJ, spontaneousUnderConditions: deltaGkJ < 0, equilibriumConstant: Math.exp(-deltaGkJ * 1000 / (R * temperatureK)) };
  }

  function hess(steps) {
    if (!Array.isArray(steps) || !steps.length) throw new Error('Provide one or more Hess-law steps');
    const normalized = steps.map((step, index) => ({
      label: step.label || `Step ${index + 1}`,
      multiplier: n(step.multiplier ?? 1, `step ${index + 1} multiplier`),
      deltaHkJ: n(step.deltaHkJ, `step ${index + 1} ΔH`)
    }));
    return { steps: normalized, netDeltaHkJ: normalized.reduce((sum, step) => sum + step.multiplier * step.deltaHkJ, 0) };
  }

  function nernst(values) {
    const eStandard = n(values.eStandard, 'standard cell potential');
    const temperatureK = positive(values.temperatureK || 298.15, 'temperature');
    const electrons = positive(values.electrons, 'electron count');
    const q = positive(values.reactionQuotient, 'reaction quotient');
    const eCell = eStandard - R * temperatureK / (electrons * F) * Math.log(q);
    return { cellPotentialV: eCell, deltaGJmol: -electrons * F * eCell, equilibriumConstantFromStandard: Math.exp(electrons * F * eStandard / (R * temperatureK)) };
  }

  function electrolysis(values) {
    const currentA = positive(values.currentA, 'current');
    const timeS = positive(values.timeS, 'time');
    const electrons = positive(values.electrons, 'electron count');
    const molarMassGmol = positive(values.molarMassGmol, 'molar mass');
    const chargeC = currentA * timeS;
    const molElectrons = chargeC / F;
    const molProduct = molElectrons / electrons;
    return { chargeC, molElectrons, molProduct, productMassG: molProduct * molarMassGmol };
  }

  function arrhenius(values) {
    const preExponential = positive(values.preExponential, 'pre-exponential factor');
    const activationEnergyKJ = positive(values.activationEnergyKJ, 'activation energy');
    const temperatureK = positive(values.temperatureK, 'temperature');
    return { rateConstant: preExponential * Math.exp(-activationEnergyKJ * 1000 / (R * temperatureK)) };
  }

  function integratedRate(values) {
    const order = Number(values.order);
    const k = positive(values.k, 'rate constant');
    const a0 = positive(values.initialConcentration, 'initial concentration');
    const time = Math.max(0, n(values.time, 'time'));
    let concentration;
    if (order === 0) concentration = a0 - k * time;
    else if (order === 1) concentration = a0 * Math.exp(-k * time);
    else if (order === 2) concentration = 1 / (1 / a0 + k * time);
    else throw new Error('Order must be 0, 1, or 2');
    return { order, concentration: Math.max(0, concentration), fractionRemaining: Math.max(0, concentration) / a0 };
  }

  function percentComposition(formula) {
    if (!Lab.Stoichiometry) throw new Error('Stoichiometry engine unavailable');
    const result = Lab.Stoichiometry.molarMass(formula);
    const composition = {};
    Object.entries(result.composition).forEach(([symbol, count]) => {
      const atomicMass = Lab.Stoichiometry.atomicMass(symbol);
      composition[symbol] = { atoms: count, massContribution: atomicMass * count, percentByMass: 100 * atomicMass * count / result.molarMass };
    });
    return { formula, molarMass: result.molarMass, composition };
  }

  function empiricalFormula(values) {
    const rows = Array.isArray(values) ? values : [];
    if (!rows.length) throw new Error('Provide element masses or percentages');
    const moleRows = rows.map(row => {
      const symbol = String(row.symbol || '').trim();
      const amount = positive(row.amount, `${symbol || 'element'} amount`);
      const atomicMass = Lab.Stoichiometry.atomicMass(symbol);
      return { symbol, amount, moles: amount / atomicMass };
    });
    const min = Math.min(...moleRows.map(row => row.moles));
    const ratios = moleRows.map(row => ({ ...row, ratio: row.moles / min }));
    let multiplier = 1;
    for (let m = 1; m <= 12; m++) {
      if (ratios.every(row => Math.abs(row.ratio * m - Math.round(row.ratio * m)) < 0.05)) { multiplier = m; break; }
    }
    const subscripts = ratios.map(row => ({ symbol: row.symbol, subscript: Math.max(1, Math.round(row.ratio * multiplier)) }));
    const formula = subscripts.map(row => row.symbol + (row.subscript === 1 ? '' : row.subscript)).join('');
    return { formula, multiplier, ratios, subscripts };
  }

  function molecularFormula(values) {
    const empirical = String(values.empiricalFormula || '').trim();
    const molecularMass = positive(values.molecularMass, 'molecular mass');
    const empiricalMass = Lab.Stoichiometry.molarMass(empirical).molarMass;
    const multiple = Math.max(1, Math.round(molecularMass / empiricalMass));
    const composition = Lab.Stoichiometry.parseFormula(empirical);
    return { empiricalFormula: empirical, empiricalMass, molecularMass, multiple, molecularFormula: Object.entries(composition).map(([s, c]) => s + (c * multiple === 1 ? '' : c * multiple)).join('') };
  }

  function linearRegression(points) {
    if (!Array.isArray(points) || points.length < 2) throw new Error('At least two calibration points are required');
    const rows = points.map((p, i) => ({ x: n(p.x, `x${i + 1}`), y: n(p.y, `y${i + 1}`) }));
    const count = rows.length;
    const sx = rows.reduce((s, p) => s + p.x, 0), sy = rows.reduce((s, p) => s + p.y, 0);
    const sxx = rows.reduce((s, p) => s + p.x * p.x, 0), sxy = rows.reduce((s, p) => s + p.x * p.y, 0);
    const denominator = count * sxx - sx * sx;
    if (Math.abs(denominator) < 1e-15) throw new Error('Calibration x values must vary');
    const slope = (count * sxy - sx * sy) / denominator;
    const intercept = (sy - slope * sx) / count;
    const meanY = sy / count;
    const ssTot = rows.reduce((s, p) => s + (p.y - meanY) ** 2, 0);
    const ssRes = rows.reduce((s, p) => s + (p.y - (slope * p.x + intercept)) ** 2, 0);
    const residualSD = count > 2 ? Math.sqrt(ssRes / (count - 2)) : 0;
    return { count, slope, intercept, rSquared: ssTot === 0 ? 1 : 1 - ssRes / ssTot, residualSD, points: rows };
  }

  function calibration(values) {
    const regression = linearRegression(values.points);
    const signal = n(values.unknownSignal, 'unknown signal');
    if (Math.abs(regression.slope) < 1e-15) throw new Error('Calibration slope is zero');
    const concentration = (signal - regression.intercept) / regression.slope;
    return { ...regression, unknownSignal: signal, estimatedConcentration: concentration, lod: 3.3 * regression.residualSD / Math.abs(regression.slope), loq: 10 * regression.residualSD / Math.abs(regression.slope) };
  }

  Lab.ChemistryLab = {
    constants: { R, F }, concentration, strongAcidBase, weakAcid, weakBase, buffer, titration,
    solubility, calorimetry, gibbs, hess, nernst, electrolysis, arrhenius, integratedRate,
    percentComposition, empiricalFormula, molecularFormula, linearRegression, calibration
  };
})(window);
