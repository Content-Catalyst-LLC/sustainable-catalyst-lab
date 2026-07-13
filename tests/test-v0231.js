'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

global.window = {
  SCLab: {
    BiomedicalEngineeringBiosignals: {
      VERSION: '0.23.0',
      definitions: Array.from(
        { length: 48 },
        (_, index) => ({
          id: `method-${index + 1}`,
        })
      ),
      benchmarks: Array.from(
        { length: 48 },
        (_, index) => ({
          id: `benchmark-${index + 1}`,
        })
      ),
      categories: Array.from(
        { length: 8 },
        (_, index) => ({
          id: `category-${index + 1}`,
        })
      ),
      init: () => false,
      status: () => ({
        version: '0.23.0',
        methodCount: 48,
        benchmarkCount: 48,
        categoryCount: 8,
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
      + 'biosignal-production-v0231.js'
  )
);

const api =
  global.window.SCLab.BiosignalProduction;

assert.ok(api, 'Production API export');
assert.equal(api.VERSION, '0.23.1');
assert.equal(api.ENGINE_VERSION, '0.23.0');
assert.equal(typeof api.repair, 'function');
assert.equal(typeof api.open, 'function');
assert.equal(typeof api.health, 'function');
assert.equal(typeof api.status, 'function');
assert.equal(typeof api.scheduleRepair, 'function');

const health = api.health();

assert.equal(health.release, '0.23.1');
assert.equal(health.engineRelease, '0.23.0');
assert.equal(health.methodCount, 48);
assert.equal(health.benchmarkCount, 48);
assert.equal(health.categoryCount, 8);
assert.equal(health.contractReady, true);
assert.equal(health.panelFound, false);
assert.equal(health.status, 'repair-required');

console.log(
  'Lab v0.23.1 JS structural tests passed: '
  + 'production API, 48-method engine contract, '
  + '8 categories, recovery and health diagnostics.'
);
