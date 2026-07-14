'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

const intervals = new Set();

global.window = {
  SCLab: {
    LaboratoryDataInstrumentation: {
      VERSION: '0.25.0',
      catalog: {
        methods: Array.from({ length: 48 }, (_, index) => ({ id: index })),
        benchmarks: Array.from({ length: 48 }, (_, index) => ({ id: index })),
      },
    },
    InstrumentationProduction: {
      VERSION: '0.25.1',
    },
  },
  setTimeout: (callback) => {
    callback();
    return 1;
  },
  setInterval: (callback) => {
    intervals.add(callback);
    return callback;
  },
  clearInterval: (handle) => intervals.delete(handle),
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/instrumentation-live-visualization-v0252.js'
  )
);

const api = global.window.SCLab.InstrumentationLiveVisualization;

assert.ok(api, 'Live visualization API');
assert.equal(api.VERSION, '0.25.2');
assert.equal(api.contract.modes.length, 8);
assert.equal(api.contract.analysisMethods.length, 16);
assert.equal(api.contract.benchmarks.length, 16);
assert.equal(api.contract.channelTemplates.length, 8);
assert.equal(api.contract.connectionStates.length, 8);
assert.equal(api.contract.eventTypes.length, 8);

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

const buffer = new api.StreamBuffer({
  maximumPoints: 2,
  maximumAgeSeconds: 100,
});
buffer.setConnectionState('online');
buffer.ingestBatch([
  { timestamp: 1, channel: 'temperature', value: 20 },
  { timestamp: 2, channel: 'temperature', value: 21 },
  { timestamp: 3, channel: 'temperature', value: 22 },
]);
assert.equal(buffer.records.length, 2);
assert.deepEqual(
  buffer.records.map((record) => record.value),
  [21, 22]
);

const snapshot = api.buildSnapshot(
  [
    { timestamp: 1, channel: 'temperature', value: 20 },
    { timestamp: 2, channel: 'temperature', value: 26 },
    { timestamp: 9, channel: 'temperature', value: 21 },
  ],
  {
    temperature: {
      warningLow: 10,
      warningHigh: 20,
      actionLow: 5,
      actionHigh: 25,
    },
  },
  3,
  'online'
);
assert.equal(snapshot.summary.channelCount, 1);
assert.deepEqual(
  [...new Set(snapshot.events.map((event) => event.type))].sort(),
  ['action', 'gap', 'warning']
);

const csv = api.parseCsv(
  'timestamp,channel,value,unit,qualityFlags\n'
  + '1,temperature,22,°C,\n'
  + '2,pressure,100,kPa,review-required'
);
assert.equal(csv.length, 2);
assert.equal(csv[1].qualityFlags[0], 'review-required');

const svg = api.chartSvg(
  csv,
  ['temperature', 'pressure'],
  []
);
assert.match(svg, /sc-live-svg/);
assert.match(svg, /polyline/);

const status = api.status();
assert.equal(status.version, '0.25.2');
assert.equal(status.preservedMethodCount, 48);
assert.equal(status.preservedBenchmarkCount, 48);

console.log(
  'Lab v0.25.2 JS tests passed: '
  + '8 modes, 16 methods/benchmarks, 8 channels/states/events, '
  + 'bounded buffering, threshold/gap events, CSV and SVG.'
);
