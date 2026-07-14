'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

global.window = {
  SCLab: {
    LaboratoryDataInstrumentation: {
      VERSION: '0.25.0',
      catalog: {
        methods: Array.from(
          { length: 48 },
          (_, index) => ({ id: index })
        ),
        benchmarks: Array.from(
          { length: 48 },
          (_, index) => ({ id: index })
        ),
      },
    },
    InstrumentationProduction: {
      VERSION: '0.25.1',
    },
    InstrumentationLiveVisualization: {
      VERSION: '0.25.2',
      contract: {
        modes: Array.from(
          { length: 8 },
          (_, index) => ({ id: index })
        ),
      },
    },
  },
  setTimeout: () => 0,
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/'
      + 'instrumentation-validation-custody-v0253.js'
  )
);

const api =
  global.window.SCLab.InstrumentationValidationCustody;

(async () => {
  assert.ok(api, 'Validation/custody API');
  assert.equal(api.VERSION, '0.25.3');
  assert.equal(api.contract.validationProfiles.length, 8);
  assert.equal(api.contract.acceptanceStates.length, 8);
  assert.equal(api.contract.provenanceEventTypes.length, 8);
  assert.equal(api.contract.deviationTypes.length, 8);
  assert.equal(api.contract.analysisMethods.length, 16);
  assert.equal(api.contract.benchmarks.length, 16);

  for (const benchmark of api.contract.benchmarks) {
    const result = api.execute(
      benchmark.methodId,
      benchmark.inputs
    );
    assert.deepEqual(
      result.value,
      benchmark.expected,
      benchmark.methodId
    );
  }

  const manifest = await api.createManifest(
    {
      instrument: {
        id: 'INST-1',
        model: 'SC-100',
      },
      calibration: {
        status: 'accepted',
      },
    },
    {
      projectId: 'PROJECT-1',
    }
  );

  assert.equal(manifest.manifestHash.length, 64);
  assert.equal(
    Object.keys(manifest.componentHashes).length,
    2
  );

  const first = await api.createCustodyEvent({
    sampleId: 'SAMPLE-1',
    action: 'received',
    actor: 'analyst-a',
    location: 'intake',
    timestamp: 1,
  });

  const second = await api.createCustodyEvent({
    sampleId: 'SAMPLE-1',
    action: 'transferred',
    actor: 'analyst-b',
    location: 'lab',
    timestamp: 2,
    previousHash: first.eventHash,
  });

  const valid = await api.verifyCustodyChain([
    first,
    second,
  ]);

  assert.equal(valid.valid, true);

  const tampered = {
    ...second,
    location: 'unknown',
  };

  const invalid = await api.verifyCustodyChain([
    first,
    tampered,
  ]);

  assert.equal(invalid.valid, false);
  assert.ok(
    invalid.problems.includes('event-2-hash')
  );

  const dossier = await api.createDossier({
    profileResults: {
      'instrument-identity': {
        score: 100,
      },
      'calibration-acceptance': {
        score: 95,
      },
      'measurement-quality': {
        score: 92,
      },
      'custody-chain-integrity': {
        score: 100,
      },
    },
    manifest,
    custodyEvents: [first, second],
    deviations: [
      {
        type: 'review-incomplete',
        closed: false,
      },
    ],
    metadata: {
      reviewer: 'QA',
    },
  });

  assert.equal(
    dossier.disposition,
    'conditionally-accepted'
  );
  assert.equal(dossier.dossierHash.length, 64);

  const status = api.status();

  assert.equal(status.version, '0.25.3');
  assert.equal(status.preservedMethodCount, 48);
  assert.equal(status.preservedBenchmarkCount, 48);
  assert.equal(status.liveModeCount, 8);

  console.log(
    'Lab v0.25.3 JS tests passed: '
    + '8 profiles/states/events/deviations, '
    + '16 methods/benchmarks, SHA-256 manifest, '
    + 'custody verification, tamper detection, dossier.'
  );
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
