'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

const catalog = {
  methods: Array.from({ length: 48 }, (_, index) => ({ id: `method-${index + 1}` })),
  benchmarks: Array.from({ length: 48 }, (_, index) => ({ id: `benchmark-${index + 1}` })),
  categories: Array.from({ length: 8 }, (_, index) => ({ id: `category-${index + 1}` })),
  recordTypes: Array.from({ length: 9 }, (_, index) => `record-${index + 1}`),
  connectionProfiles: Array.from({ length: 8 }, (_, index) => ({ id: `connection-${index + 1}` })),
  qualityFlags: Array.from({ length: 8 }, (_, index) => `quality-${index + 1}`),
};

global.window = {
  SCLab: {
    LaboratoryDataInstrumentation: {
      VERSION: '0.25.0',
      catalog,
      init: () => false,
      render: () => false,
      status: () => ({
        version: '0.25.0',
        methodCount: 48,
        benchmarkCount: 48,
        categoryCount: 8,
        recordTypeCount: 9,
        connectionProfileCount: 8,
      }),
    },
  },
  setTimeout: () => 0,
  clearTimeout: () => {},
  addEventListener: () => {},
  location: { hash: '' },
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/instrumentation-production-v0251.js'
  )
);

const api = global.window.SCLab.InstrumentationProduction;
assert.ok(api, 'Production API export');
assert.equal(api.VERSION, '0.25.1');
assert.equal(api.ENGINE_VERSION, '0.25.0');
assert.equal(typeof api.repair, 'function');
assert.equal(typeof api.open, 'function');
assert.equal(typeof api.health, 'function');
assert.equal(typeof api.status, 'function');
assert.equal(typeof api.scheduleRepair, 'function');

const health = api.health();
assert.equal(health.release, '0.25.1');
assert.equal(health.engineRelease, '0.25.0');
assert.equal(health.methodCount, 48);
assert.equal(health.benchmarkCount, 48);
assert.equal(health.categoryCount, 8);
assert.equal(health.recordTypeCount, 9);
assert.equal(health.connectionProfileCount, 8);
assert.equal(health.qualityFlagCount, 8);
assert.equal(health.contractReady, true);
assert.equal(health.panelFound, false);
assert.equal(health.status, 'repair-required');

console.log(
  'Lab v0.25.1 JS structural tests passed: production API, '
  + '48/48/8/9/8/8 contract, recovery and health diagnostics.'
);
