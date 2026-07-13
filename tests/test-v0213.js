'use strict';

const assert = require('node:assert/strict');
const { webcrypto } = require('node:crypto');
const path = require('node:path');

global.window = {
  SCLab: {
    BiochemistryMolecularAnalysis: {
      VERSION: '0.21.0',
      definitions: [
        {
          id: 'bc.michaelis_menten',
          title: 'Michaelis–Menten velocity',
          category: 'Enzyme kinetics',
        },
      ],
    },
    BiochemistryVisualizationBatch: {
      VERSION: '0.21.2',
    },
  },
  crypto: webcrypto,
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
      + 'molecular-analysis-validation-provenance-v0213.js'
  )
);

const api =
  global.window.SCLab
    .MolecularAnalysisValidationProvenance;

assert.ok(api, 'Validation/provenance export');
assert.equal(api.VERSION, '0.21.3');
assert.equal(api.profiles.length, 8);

const precisionRows = api.parseCsv(
  [
    'value',
    '100.1',
    '99.8',
    '100.4',
    '100.0',
    '99.9',
  ].join('\n')
);

const precision = api.validateProfile(
  'precision-repeatability',
  precisionRows,
  {
    minimumReplicates: 3,
    maximumCvPercent: 10,
  }
);

assert.equal(precision.decision, 'pass');
assert.equal(precision.metrics.n, 5);
assert.ok(
  precision.metrics.coefficientOfVariationPercent
    < 1
);

const calibration = api.validateProfile(
  'calibration-linearity',
  api.parseCsv(
    [
      'concentration,signal',
      '0,1',
      '1,3',
      '2,5',
      '3,7',
      '4,9',
    ].join('\n')
  ),
  {
    minimumLevels: 5,
    minimumRSquared: 0.99,
    requirePositiveSlope: 1,
  }
);

assert.equal(calibration.decision, 'pass');
assert.equal(calibration.metrics.slope, 2);
assert.equal(calibration.metrics.intercept, 1);
assert.equal(calibration.metrics.rSquared, 1);

const failingBlank = api.validateProfile(
  'blank-background',
  api.parseCsv(
    [
      'value',
      '0.01',
      '0.02',
      '0.5',
    ].join('\n')
  ),
  {
    minimumBlanks: 3,
    maximumMean: 0.05,
    maximumSingle: 0.1,
  }
);

assert.equal(failingBlank.decision, 'fail');
assert.ok(failingBlank.failedCheckCount >= 1);

(async () => {
  const payload = {
    validation: precision,
    methodId: 'bc.michaelis_menten',
  };

  const first = await api.createProvenanceRecord(
    payload,
    {
      recordId: 'record-1',
      timestamp: '2026-07-13T18:00:00Z',
      methodId: 'bc.michaelis_menten',
      profileId: 'precision-repeatability',
      analyst: 'Reference analyst',
    },
    null
  );

  assert.equal(first.payloadHash.length, 64);
  assert.equal(first.recordHash.length, 64);

  const second = await api.createProvenanceRecord(
    {
      validation: calibration,
      methodId: 'bc.michaelis_menten',
    },
    {
      recordId: 'record-2',
      timestamp: '2026-07-13T18:05:00Z',
      methodId: 'bc.michaelis_menten',
      profileId: 'calibration-linearity',
    },
    first.recordHash
  );

  const valid = await api.verifyLedger([
    first,
    second,
  ]);

  assert.equal(valid.valid, true);
  assert.equal(valid.recordCount, 2);

  const tampered = JSON.parse(
    JSON.stringify([first, second])
  );
  tampered[0].payload.methodId = 'tampered';

  const invalid = await api.verifyLedger(tampered);

  assert.equal(invalid.valid, false);
  assert.equal(
    invalid.results[0].hashValid,
    false
  );

  console.log(
    'Lab v0.21.3 JS tests passed: '
    + `${api.profiles.length} validation profiles, `
    + 'SHA-256 ledger tamper detection.'
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
