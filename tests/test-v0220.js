'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

global.window = {
  SCLab: {},
  setTimeout: () => 0,
  localStorage: {
    getItem: () => null,
    setItem: () => {},
  },
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/'
      + 'biotechnology-bioprocess-engineering-v0220.js'
  )
);

const api = global.window.SCLab.BiotechnologyBioprocessEngineering;

assert.ok(api, 'Bioprocess API export');
assert.equal(api.VERSION, '0.22.0');
assert.equal(api.definitions.length, 48);
assert.equal(api.benchmarks.length, 48);

const benchmarkResults = api.runBenchmarks();
const failed = benchmarkResults.filter((result) => !result.passed);

assert.deepEqual(failed, []);

const growth = api.run('bp.exponential_biomass', {
  x0: 1,
  mu: 0.35,
  time: 8,
});

assert.ok(Math.abs(growth.outputs.result - 16.444646771097048) < 1e-10);

const batch = api.batchRun(
  'bp.batch_productivity',
  [
    'sample,product_concentration,batch_time',
    'run-1,18,36',
    'run-2,19,36',
    'run-3,17,36',
  ].join('\n')
);

assert.equal(batch.rowCount, 3);
assert.equal(batch.successCount, 3);
assert.equal(batch.errorCount, 0);
assert.equal(batch.statistics.n, 3);

const batchSimulation = api.simulateBatch({
  x0: 1,
  mu: 0.3,
  time: 24,
  substrate0: 40,
  yieldXs: 0.5,
  yieldPs: 0.2,
});

assert.equal(batchSimulation.points.length, 41);
assert.equal(batchSimulation.mode, 'batch');
assert.ok(batchSimulation.summary.biomass > 1);
assert.ok(batchSimulation.summary.substrate >= 0);

const fedBatch = api.simulateFedBatch({
  initialVolume: 5,
  initialFeedRate: 0.05,
  muSet: 0.15,
  feedConcentration: 500,
  x0: 2,
  time: 24,
});

assert.equal(fedBatch.points.length, 41);
assert.ok(fedBatch.summary.volume > 5);
assert.ok(fedBatch.summary.feedRate > 0.05);

const continuous = api.simulateContinuous({
  volume: 10,
  flowRate: 1.5,
  muMax: 0.5,
  ks: 0.5,
  feedSubstrate: 20,
  yieldXs: 0.5,
  productConcentration: 12,
});

assert.equal(continuous.mode, 'continuous');
assert.equal(continuous.summary.washout, false);
assert.ok(continuous.summary.biomass > 0);

console.log(
  'Lab v0.22.0 JS tests passed: '
  + `${api.definitions.length} methods, `
  + `${api.benchmarks.length} benchmarks, `
  + '3 reactor modes.'
);
