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
      + 'bioprocess-validation-provenance-v0223.js'
  )
);

const api =
  global.window.SCLab.BioprocessValidationProvenance;

assert.ok(api, 'v0.22.3 browser API');
assert.equal(api.VERSION, '0.22.3');
assert.equal(api.profiles.length, 8);
assert.equal(api.eventTypes.length, 5);

const consistency = api.evaluate(
  'cross-batch-consistency',
  [
    {
      batchId: 'B-001',
      yield: 82,
      titer: 3.9,
      cycleTime: 72,
    },
    {
      batchId: 'B-002',
      yield: 84,
      titer: 4.0,
      cycleTime: 70,
    },
    {
      batchId: 'B-003',
      yield: 83,
      titer: 4.1,
      cycleTime: 71,
    },
  ]
);

assert.equal(consistency.decision, 'pass');
assert.equal(consistency.failedCheckCount, 0);

const cpp = api.evaluate(
  'cpp-conformance',
  [
    {
      parameter: 'temperature',
      value: 37,
      low: 35,
      high: 39,
    },
    {
      parameter: 'pH',
      value: 6.2,
      low: 6.8,
      high: 7.2,
    },
  ]
);

assert.equal(cpp.decision, 'fail');
assert.equal(
  cpp.metrics.actionExcursionCount,
  1
);

const first = api.createRecord(
  {
    status: 'normal',
  },
  {
    recordId: 'record-1',
    timestamp: '2026-07-13T20:00:00.000Z',
    eventType: 'monitoring-analysis',
    batchId: 'B-001',
  }
);
const second = api.createRecord(
  consistency,
  {
    recordId: 'record-2',
    timestamp: '2026-07-13T20:05:00.000Z',
    eventType: 'validation-decision',
    batchId: 'B-001',
  },
  first.recordHash
);
const valid = api.verifyLedger([
  first,
  second,
]);

assert.equal(valid.valid, true);
assert.equal(valid.recordCount, 2);

const tampered = JSON.parse(
  JSON.stringify([first, second])
);
tampered[1].payload.decision = 'fail';

const invalid = api.verifyLedger(tampered);

assert.equal(invalid.valid, false);
assert.equal(
  invalid.results[1].payloadValid,
  false
);

const dossier = api.createDossier(
  [consistency],
  {
    batchId: 'B-001',
  },
  [first, second],
  'release'
);

assert.equal(
  dossier.summary.releaseReady,
  true
);
assert.equal(
  dossier.dossierHash.length,
  64
);

console.log(
  'Lab v0.22.3 JS tests passed: '
  + '8 profiles, 5 event types, '
  + 'validation, provenance, tamper detection, dossier.'
);
