'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

const method = {
  id: 'bc.michaelis_menten',
  title: 'Michaelis–Menten velocity',
  category: 'Enzyme kinetics',
  inputs: [
    {
      key: 'vmax',
      label: 'Vmax',
      default: 100,
    },
    {
      key: 'substrate',
      label: 'Substrate',
      default: 2,
    },
    {
      key: 'km',
      label: 'Km',
      default: 0.5,
    },
  ],
  outputs: {
    velocity: {
      label: 'Velocity',
      unit: 'rate',
    },
  },
};

global.window = {
  SCLab: {
    BiochemistryMolecularAnalysis: {
      VERSION: '0.21.0',
      definitions: [method],
      run(methodId, inputs) {
        if (methodId !== method.id) {
          throw new Error('Unknown method');
        }

        const vmax = Number(inputs.vmax);
        const substrate = Number(inputs.substrate);
        const km = Number(inputs.km);

        if (
          !Number.isFinite(vmax)
          || !Number.isFinite(substrate)
          || !Number.isFinite(km)
        ) {
          throw new Error('Invalid inputs');
        }

        return {
          inputs: {
            vmax,
            substrate,
            km,
          },
          outputs: {
            velocity:
              (vmax * substrate)
              / (km + substrate),
          },
          warnings: [],
        };
      },
    },
  },
  localStorage: {
    getItem: () => null,
    setItem: () => {},
  },
  setTimeout: () => 0,
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/'
      + 'biochemistry-visualization-batch-v0212.js'
  )
);

const api =
  global.window.SCLab.BiochemistryVisualizationBatch;

assert.ok(api, 'Visualization/batch export');
assert.equal(api.VERSION, '0.21.2');
assert.equal(api.presets.length, 7);

const parsed = api.parseCsv(
  'sample,vmax,substrate,km\n'
  + 'sample-1,100,2,0.5\n'
  + 'sample-2,100,3,0.5'
);

assert.equal(parsed.length, 2);
assert.equal(parsed[0].sample, 'sample-1');

const summary = api.summarize([10, 11, 9]);

assert.equal(summary.n, 3);
assert.equal(summary.mean, 10);
assert.equal(summary.standardDeviation, 1);
assert.equal(summary.status, 'screened');

const regression = api.linearRegression([
  { x: 0, y: 1 },
  { x: 1, y: 3 },
  { x: 2, y: 5 },
]);

assert.equal(regression.slope, 2);
assert.equal(regression.intercept, 1);
assert.equal(regression.rSquared, 1);

const kinetics = api.generatePresetData(
  api.presets.find(
    (preset) => preset.id === 'michaelis-menten'
  ),
  {
    vmax: 100,
    km: 0.5,
    xMax: 5,
  }
);

assert.equal(kinetics.series.length, 1);
assert.equal(kinetics.series[0].points.length, 41);
assert.equal(kinetics.series[0].points[0].y, 0);

const batch = api.batchRun(
  'bc.michaelis_menten',
  [
    'sample,vmax,substrate,km',
    'sample-1,100,2,0.5',
    'sample-2,100,3,0.5',
    'sample-3,100,1,0.5',
  ].join('\n')
);

assert.equal(batch.version, '0.21.2');
assert.equal(batch.analysisEngineVersion, '0.21.0');
assert.equal(batch.rowCount, 3);
assert.equal(batch.successCount, 3);
assert.equal(batch.errorCount, 0);
assert.equal(batch.statistics.velocity.n, 3);
assert.ok(
  Number.isFinite(
    batch.statistics.velocity.mean
  )
);

console.log(
  'Lab v0.21.2 JS tests passed: '
  + `${api.presets.length} visualization presets, `
  + `${batch.rowCount} batch rows.`
);
