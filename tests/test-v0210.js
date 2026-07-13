'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

global.window = {
  SCLab: {},
  localStorage: {
    getItem: () => null,
    setItem: () => {},
  },
};

global.CustomEvent = class CustomEvent {
  constructor(name, options = {}) {
    this.type = name;
    this.detail = options.detail;
  }
};

global.document = {
  readyState: 'complete',
  querySelectorAll: () => [],
  addEventListener: () => {},
  dispatchEvent: () => {},
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/'
      + 'biochemistry-molecular-analysis.js'
  )
);

const moduleApi =
  global.window.SCLab.BiochemistryMolecularAnalysis;

assert.ok(moduleApi, 'Biochemistry module export');
assert.equal(moduleApi.VERSION, '0.21.0');
assert.equal(moduleApi.definitions.length, 48);
assert.equal(moduleApi.benchmarks.length, 48);

for (const method of moduleApi.definitions) {
  assert.ok(method.id.startsWith('bc.'));
  assert.ok(method.title);
  assert.ok(method.category);
  assert.ok(method.equation);
  assert.ok(method.inputs.length >= 1);
  assert.ok(Object.keys(method.outputs).length >= 1);
}

const result = moduleApi.run(
  'bc.michaelis_menten',
  {
    vmax: 100,
    substrate: 2,
    km: 0.5,
  }
);

assert.equal(result.methodId, 'bc.michaelis_menten');
assert.equal(result.outputs.velocity, 80);
assert.equal(
  result.schema,
  'sc-lab-biochemistry-analysis/1.0'
);

const dna = moduleApi.run(
  'bc.dsdna_a260_concentration',
  {
    absorbance260: 0.2,
    dilutionFactor: 10,
  }
);

assert.equal(dna.outputs.dnaConcentrationUgMl, 100);

const report = moduleApi.runBenchmarks();

assert.equal(report.total, 48);
assert.equal(report.passed, 48);
assert.equal(report.failed, 0);

console.log(
  'Lab v0.21.0 JS tests passed: '
    + `${moduleApi.definitions.length} methods, `
    + `${report.passed} benchmarks.`
);
