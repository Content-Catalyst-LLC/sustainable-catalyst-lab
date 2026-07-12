const fs = require('fs');
const vm = require('vm');
const path = require('path');
const root = path.resolve(__dirname, '..');
const context = {
  window: {},
  console,
  setTimeout,
  clearTimeout,
  Blob: function () {},
  URL: { createObjectURL() { return ''; }, revokeObjectURL() {} }
};
context.window.window = context.window;
vm.createContext(context);
function load(file) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, { filename: file });
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
load('assets/js/modules/core.js');
load('assets/js/modules/stoichiometry.js');
load('assets/js/modules/spectrometry.js');
load('assets/js/modules/calculators.js');
load('assets/js/modules/datasets.js');
load('assets/js/modules/observations.js');
load('assets/js/modules/workspace.js');

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

const Spectrometry = context.window.SCLab.Spectrometry;
const points = Spectrometry.parse('400,0\n450,1\n500,0');
assert(Spectrometry.peaks(points).length === 1, 'Peak detection failed');
assert(Math.abs(Spectrometry.integrate(points) - 50) < 1e-9, 'Integration failed');

const Calculators = context.window.SCLab.Calculators;
assert(Calculators.definitions.length >= 30, 'Expected at least 30 calculators');
assert(Math.abs(Calculators.run('photon', { wavelengthNm: 500 }).electronVolts - 2.47968) < 0.001, 'Photon calculator failed');
assert(Math.abs(Calculators.run('michaelis', { vmax: 100, substrate: 8, km: 2 }).rate - 80) < 1e-9, 'Michaelis-Menten failed');

const Workspace = context.window.SCLab.Workspace;
assert(Workspace.modules.length >= 15, 'Expected grouped module catalog');
assert(Workspace.quickTools.length >= 9, 'Expected quick scientific tools');
const search = Workspace.search('stoichiometry', Calculators.definitions);
assert(search.length && search[0].id === 'stoichiometry', 'Command search failed');
const trace = Workspace.traceCounts({ evidence: [{ source: 'USGS' }, { source: 'NASA' }], hypotheses: [], calculations: [1], experiments: [1, 2], decisions: [], documents: [] });
assert(trace[0].value === 2 && trace[5].value === 1 && trace[6].value === 2, 'Traceability counts failed');
assert(Workspace.projectTotal({ evidence: [1], experiments: [], hypotheses: [], decisions: [], notes: [1], calculations: [], documents: [], maps: [] }) === 2, 'Project total failed');

const D=context.window.SCLab.Datasets;const ds=D.parseCSV('x,y\n1,2\n3,4');assert(ds.rows.length===2&&D.summary(ds).numeric.y.mean===3,'Dataset inspector failed');const O=context.window.SCLab.Observations;assert(O.telescope({title:'JWST deep field'})==='JWST','Telescope classification failed');console.log(`JS tests passed: ${elements.length} elements, ${Calculators.definitions.length} calculators, ${Workspace.modules.length} modules.`);
