'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

global.window = {
  SCLab: {},
  setTimeout: () => 0,
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/'
      + 'biomedical-engineering-biosignals-v0230.js'
  )
);

const api =
  global.window.SCLab.BiomedicalEngineeringBiosignals;

assert.ok(api, 'Biomedical biosignal API');
assert.equal(api.VERSION, '0.23.0');
assert.equal(api.definitions.length, 48);
assert.equal(api.benchmarks.length, 48);
assert.equal(api.categories.length, 8);

for (const benchmark of api.benchmarks) {
  const result = api.execute(
    benchmark.methodId,
    benchmark.inputs
  );

  const delta = Math.abs(
    Number(result.value)
    - Number(benchmark.expected)
  );

  assert.ok(
    delta <= Math.max(
      Number(benchmark.tolerance),
      Math.abs(Number(benchmark.expected)) * 1e-8
    ),
    `${benchmark.methodId}: ${result.value} vs ${benchmark.expected}`
  );
}

const waveform = api.analyzeSignal(
  [-1, 1, -1, 1],
  100
);

assert.equal(waveform.sampleCount, 4);
assert.equal(waveform.durationSeconds, 0.03);
assert.equal(waveform.rms, 1);
assert.equal(waveform.peakToPeak, 2);
assert.equal(waveform.zeroCrossingCount, 3);
assert.equal(waveform.zeroCrossingRate, 100);

const batch = api.batchExecute([
  {
    methodId: 'heart-rate-from-rr',
    inputs: {
      rrSeconds: 0.8,
    },
  },
  {
    methodId: 'heart-rate-from-rr',
    inputs: {
      rrSeconds: 0,
    },
  },
  {
    methodId: 'signal-quality-index',
    inputs: {
      snrDb: 20,
      missingPercent: 2,
      clippingPercent: 1,
    },
  },
]);

assert.equal(batch.rowCount, 3);
assert.equal(batch.successCount, 2);
assert.equal(batch.errorCount, 1);
assert.equal(batch.results[0].ok, true);
assert.equal(batch.results[1].ok, false);

console.log(
  'Lab v0.23.0 JS tests passed: '
  + '48 methods, 48 benchmarks, '
  + '8 categories, waveform analysis, batch isolation.'
);
