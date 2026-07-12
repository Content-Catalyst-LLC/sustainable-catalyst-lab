const fs = require('fs');
const vm = require('vm');
const path = require('path');
const root = path.resolve(__dirname, '..');
const storage = new Map();
const localStorage = { getItem(key) { return storage.has(key) ? storage.get(key) : null; }, setItem(key, value) { storage.set(key, String(value)); }, removeItem(key) { storage.delete(key); } };
const context = {
  window: {},
  localStorage,
  console,
  setTimeout,
  clearTimeout,
  Blob: function () {},
  URL: { createObjectURL() { return ''; }, revokeObjectURL() {} }
};
context.window.window = context.window;
context.window.localStorage = localStorage;
vm.createContext(context);
function load(file) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, { filename: file });
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
load('assets/js/modules/core.js');
load('assets/js/modules/projects.js');
load('assets/js/modules/stoichiometry.js');
load('assets/js/modules/chemistry-lab.js');
load('assets/js/modules/spectrometry.js');
load('assets/js/modules/calculators.js');
load('assets/js/modules/datasets.js');
load('assets/js/modules/observations.js');
load('assets/js/modules/physics-lab.js');
load('assets/js/modules/physics-validation.js');
load('assets/js/modules/biology-lab.js');
load('assets/js/modules/workspace.js');

const ProjectModel = context.window.SCLab.ProjectModel;
const blankProject = ProjectModel.blank('Validation project');
assert(blankProject.schemaVersion === '0.5.0', 'Project schema version failed');
assert(Array.isArray(blankProject.physicsValidationRecords), 'Physics validation collection missing');
assert(Array.isArray(blankProject.biologyRecords) && Array.isArray(blankProject.sequences) && Array.isArray(blankProject.biologyValidationRecords), 'Biology project collections missing');
const elements = JSON.parse(fs.readFileSync(path.join(root, 'assets/data/elements.json'), 'utf8'));
assert(elements.length === 118, 'Expected 118 elements');

const S = context.window.SCLab.Stoichiometry;
S.setElements(elements);
let composition = S.parseFormula('H2O');
assert(composition.H === 2 && composition.O === 1, 'H2O parse failed');
composition = S.parseFormula('Al2(SO4)3');
assert(composition.Al === 2 && composition.S === 3 && composition.O === 12, 'Parenthesized formula failed');
assert(Math.abs(S.molarMass('H2O').molarMass - 18.015) < 0.02, 'Molar mass failed');
const balance = S.balanceEquation('Fe + O2 -> Fe2O3');
assert(balance.coefficients.join(',') === '4,3,2', `Equation balance failed: ${balance.coefficients}`);
const limiting = S.limitingReagent('2 H2 + O2 -> 2 H2O', { H2: 3, O2: 2 });
assert(limiting.limiting === 'H2' && Math.abs(limiting.productMoles[0].moles - 3) < 1e-9, 'Limiting reagent failed');


const Chemistry = context.window.SCLab.ChemistryLab;
const weak = Chemistry.weakAcid({ concentration: 0.1, ka: 1.8e-5 });
assert(Math.abs(weak.pH - 2.875) < 0.02, 'Weak acid equilibrium failed');
const buffer = Chemistry.buffer({ pKa: 4.76, acid: 0.1, base: 0.1 });
assert(Math.abs(buffer.pH - 4.76) < 1e-12, 'Buffer calculation failed');
const titration = Chemistry.titration({ analyteType: 'acid', analyteC: 0.1, analyteMl: 25, titrantC: 0.1, titrantMl: 25 });
assert(Math.abs(titration.pH - 7) < 1e-12, 'Strong titration equivalence failed');
const nernst = Chemistry.nernst({ eStandard: 1.1, temperatureK: 298.15, electrons: 2, reactionQuotient: 10 });
assert(nernst.cellPotentialV < 1.1 && nernst.cellPotentialV > 1.06, 'Nernst calculation failed');
const empirical = Chemistry.empiricalFormula([{ symbol: 'C', amount: 40 }, { symbol: 'H', amount: 6.7 }, { symbol: 'O', amount: 53.3 }]);
assert(empirical.formula === 'CH2O', `Empirical formula failed: ${empirical.formula}`);
const cal = Chemistry.calibration({ points: [{x:0,y:0},{x:1,y:2},{x:2,y:4}], unknownSignal: 3 });
assert(Math.abs(cal.estimatedConcentration - 1.5) < 1e-12 && cal.rSquared > 0.999, 'Chemistry calibration failed');

const Spectrometry = context.window.SCLab.Spectrometry;
const points = Spectrometry.parse('400,0\n450,1\n500,0');
assert(Spectrometry.peaks(points).length === 1, 'Peak detection failed');
assert(Math.abs(Spectrometry.integrate(points) - 50) < 1e-9, 'Integration failed');
const normalized = Spectrometry.normalize(points, 'max');
assert(Math.abs(Math.max(...normalized.map(p => p.y)) - 1) < 1e-12, 'Spectrum normalization failed');
const absorbance = Spectrometry.transmittanceToAbsorbance([{x:500,y:0.1}]);
assert(Math.abs(absorbance[0].y - 1) < 1e-12, 'Transmittance conversion failed');
const advancedPeaks = Spectrometry.peaks(Spectrometry.parse('0,0\n1,2\n2,0\n3,3\n4,0'), { minDistance: 1, minProminence: 0.5 });
assert(advancedPeaks.length === 2 && advancedPeaks.every(p => Number.isFinite(p.fwhm)), 'Advanced peak characterization failed');


const Physics = context.window.SCLab.PhysicsLab;
assert(Physics.particles.length >= 20, 'Expected particle reference records');
assert(Object.keys(Physics.tools).length >= 30, 'Expected substantive physics method registry');
const projectile = Physics.tools.projectile({ v: 20, angle: 45, y0: 0, g: 9.80665 });
assert(projectile.range > 40 && projectile.range < 42 && projectile.series.length === 80, 'Projectile model failed');
const field = Physics.tools.coulomb({ q1: 1e-6, q2: -2e-6, r: 0.25 });
assert(field.interaction === 'attractive' && field.forceMagnitude > 0, 'Coulomb calculation failed');
const rlc = Physics.tools.rlc({ R: 100, L: 0.01, C: 1e-6, frequency: 1591.549, voltage: 10 });
assert(Math.abs(rlc.phaseDegrees) < 0.1 && Math.abs(rlc.impedanceMagnitude - 100) < 0.1, 'RLC resonance failed');
const photonPhysics = Physics.tools.photon({ wavelengthNm: 500 });
assert(Math.abs(photonPhysics.energyEv - 2.47968) < 0.001, 'Physics photon method failed');
const decay = Physics.tools.decay({ halfLife: 10, time: 20, initial: 1000 });
assert(Math.abs(decay.remaining - 250) < 1e-9, 'Nuclear decay failed');
const invariant = Physics.tools.invariantMass({ fourVectors: [{E:60,px:30,py:0,pz:40},{E:50,px:-20,py:0,pz:-30}] });
assert(invariant.invariantMass > 108 && invariant.invariantMass < 110, 'Invariant mass reconstruction failed');
const twoBody = Physics.tools.twoBodyDecay({ parentMass: 125.25, mass1: 0, mass2: 0 });
assert(Math.abs(twoBody.daughterMomentum - 62.625) < 1e-9, 'Two-body decay failed');
const detector = Physics.tools.detector({ B:2, radius:1.2, charge:1, distance:3, time:1.2e-8, events:1250, background:400, efficiency:0.82, luminosity:100 });
assert(detector.transverseMomentumGeVPerC > 0.7 && detector.signalEvents === 850, 'Detector analysis failed');
const validationReport = Physics.validation.runBenchmarks();
assert(validationReport.failed === 0 && validationReport.total >= 9, 'Physics benchmark validation failed');
const detectorInvalid = Physics.tools.detector({ B:2, radius:1.2, charge:1, distance:4, time:1e-9, events:100, background:10, efficiency:0.8, luminosity:50 });
assert(detectorInvalid._validation.status === 'invalid', 'Superluminal time-of-flight should fail validation');
const propagated = Physics.tools.powerLawUncertainty({ coefficient:1, variables:[{name:'x',value:2,uncertainty:0.1,power:2},{name:'y',value:3,uncertainty:0.2,power:1}] });
assert(Math.abs(propagated.value - 12) < 1e-12 && propagated.standardUncertainty > 1.3 && propagated.standardUncertainty < 1.5, 'Power-law uncertainty propagation failed');
const weighted = Physics.tools.weightedMean({ measurements:[{value:9.8,uncertainty:0.1},{value:10,uncertainty:0.2}] });
assert(weighted.weightedMean > 9.83 && weighted.weightedMean < 9.85 && weighted.reducedChiSquare > 0, 'Weighted mean failed');


const Biology = context.window.SCLab.BiologyLab;
assert(Biology.definitions.length >= 40, 'Expected substantive biology method registry');
const seqStats = Biology.tools.sequenceStats({ sequence: 'GCGCATAT' });
assert(Math.abs(seqStats.gcPercent - 50) < 1e-12 && seqStats.length === 8, 'DNA sequence statistics failed');
const translated = Biology.tools.translate({ sequence: 'ATGGGCTAA', frame: 0, stopAtStop: 'yes' });
assert(translated.protein === 'MG*', `Translation failed: ${translated.protein}`);
const alignment = Biology.tools.globalAlignment({ sequenceA: 'GATTACA', sequenceB: 'GCATGCU', match: 1, mismatch: -1, gap: -2 });
assert(alignment.alignmentLength >= 7 && Number.isFinite(alignment.score), 'Global alignment failed');
const local = Biology.tools.localAlignment({ sequenceA: 'TGTTACGG', sequenceB: 'GGTTGACTA', match: 2, mismatch: -1, gap: -2 });
assert(local.score > 0 && local.identityPercent > 0, 'Local alignment failed');
const enzyme = Biology.tools.michaelisMenten({ vmax: 100, substrate: 8, km: 2 });
assert(Math.abs(enzyme.rate - 80) < 1e-12, 'Michaelis-Menten failed');
const qpcr = Biology.tools.qpcr({ targetSampleCt: 22, targetReferenceCt: 18, controlSampleCt: 25, controlReferenceCt: 18, efficiency: 2 });
assert(Math.abs(qpcr.relativeExpression - 8) < 1e-12, 'qPCR relative expression failed');
const diversity = Biology.tools.shannonDiversity({ counts: '1,1,1,1' });
assert(Math.abs(diversity.shannonIndex - Math.log(4)) < 1e-12, 'Shannon diversity failed');
const ecology = Biology.tools.logisticGrowth({ initial: 50, carryingCapacity: 1000, growthRate: 0.4, time: 20 });
assert(ecology.population > 900 && ecology.series.length === 101, 'Logistic growth failed');
const protein = Biology.tools.proteinStats({ sequence: 'MKWVTFISLLFLFSSAYSRGVFRR' });
assert(protein.length === 24 && protein.molecularWeightDa > 2000, 'Protein properties failed');
const biologyValidation = Biology.runBenchmarks();
assert(biologyValidation.failed === 0 && biologyValidation.total >= 8, 'Biology benchmark validation failed');

const Calculators = context.window.SCLab.Calculators;
assert(Calculators.definitions.length >= 30, 'Expected at least 30 calculators');
assert(Math.abs(Calculators.run('photon', { wavelengthNm: 500 }).electronVolts - 2.47968) < 0.001, 'Photon calculator failed');
assert(Math.abs(Calculators.run('michaelis', { vmax: 100, substrate: 8, km: 2 }).rate - 80) < 1e-9, 'Michaelis-Menten failed');

const Workspace = context.window.SCLab.Workspace;
assert(Workspace.modules.length >= 17, 'Expected grouped module catalog');
assert(Workspace.quickTools.length >= 16, 'Expected quick scientific tools');
const search = Workspace.search('stoichiometry', Calculators.definitions);
assert(search.length && search[0].id === 'stoichiometry', 'Command search failed');
const trace = Workspace.traceCounts({ evidence: [{ source: 'USGS' }, { source: 'NASA' }], hypotheses: [], calculations: [1], experiments: [1, 2], decisions: [], documents: [] });
assert(trace[0].value === 2 && trace[5].value === 1 && trace[6].value === 2, 'Traceability counts failed');
assert(Workspace.projectTotal({ evidence: [1], experiments: [], hypotheses: [], decisions: [], notes: [1], calculations: [], documents: [], maps: [] }) === 2, 'Project total failed');

const D=context.window.SCLab.Datasets;const ds=D.parseCSV('x,y\n1,2\n3,4');assert(ds.rows.length===2&&D.summary(ds).numeric.y.mean===3,'Dataset inspector failed');const O=context.window.SCLab.Observations;assert(O.telescope({title:'JWST deep field'})==='JWST','Telescope classification failed');console.log(`JS tests passed: ${elements.length} elements, ${Calculators.definitions.length} calculators, ${Object.keys(Physics.tools).length} physics methods, ${Biology.definitions.length} biology methods, ${validationReport.total + biologyValidation.total} validation benchmarks, ${Workspace.modules.length} modules.`);
