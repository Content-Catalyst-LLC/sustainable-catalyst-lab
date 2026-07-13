'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

global.window = {
  SCLab: {
    BiotechnologyBioprocessEngineering: {
      VERSION: '0.22.0',
      definitions: Array.from(
        { length: 48 },
        (_, index) => ({ id: `method-${index + 1}` })
      ),
      benchmarks: Array.from(
        { length: 48 },
        (_, index) => ({ id: `benchmark-${index + 1}` })
      ),
      init: () => false,
      status: () => ({
        version: '0.22.0',
        methodCount: 48,
        benchmarkCount: 48,
      }),
    },
  },
  setTimeout: () => 0,
  clearTimeout: () => {},
  addEventListener: () => {},
  location: {
    hash: '',
  },
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/'
      + 'bioprocess-production-v0221.js'
  )
);

const api =
  global.window.SCLab.BioprocessProduction;

assert.ok(api, 'Production API export');
assert.equal(api.VERSION, '0.22.1');
assert.equal(api.ENGINE_VERSION, '0.22.0');
assert.equal(typeof api.repair, 'function');
assert.equal(typeof api.open, 'function');
assert.equal(typeof api.health, 'function');
assert.equal(typeof api.status, 'function');
assert.equal(typeof api.scheduleRepair, 'function');

const health = api.health();

assert.equal(health.release, '0.22.1');
assert.equal(health.engineRelease, '0.22.0');
assert.equal(health.methodCount, 48);
assert.equal(health.benchmarkCount, 48);
assert.equal(health.panelFound, false);
assert.equal(health.status, 'repair-required');

console.log(
  'Lab v0.22.1 JS structural tests passed: '
  + 'production API, 48-method engine contract, '
  + 'health diagnostics.'
);
