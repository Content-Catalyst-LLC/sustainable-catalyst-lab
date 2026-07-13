const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(__dirname, '../assets/js/modules/urban-planning-spatial-lab.js'),
  'utf8'
);

const context = {
  window: { SCLab: {} },
  globalThis: {},
  console,
  CustomEvent: function CustomEvent(type, init) {
    this.type = type;
    this.detail = init && init.detail;
  },
};

vm.createContext(context);
vm.runInContext(source, context);

const Lab = context.window.SCLab.UrbanPlanningSpatialLab;

if (!Lab) {
  throw new Error('UrbanPlanningSpatialLab export is missing.');
}

if (Lab.VERSION !== '0.14.0') {
  throw new Error(`Expected version 0.14.0, found ${Lab.VERSION}.`);
}

if (Lab.definitions.length !== 48) {
  throw new Error(`Expected 48 methods, found ${Lab.definitions.length}.`);
}

const results = Lab.runBenchmarks();
const failed = results.filter((result) => !result.passed);

if (failed.length) {
  throw new Error(JSON.stringify(failed, null, 2));
}

const record = Lab.run('up.floor_area_ratio', {
  grossFloorAreaM2: 3000,
  siteAreaM2: 1000,
});

if (record.outputs.floorAreaRatio !== 3) {
  throw new Error('Floor-area-ratio calculation failed.');
}

if (
  record.schema !==
  'sc-lab-urban-planning-spatial-analysis/1.0'
) {
  throw new Error('Urban planning analysis schema failed.');
}

console.log(
  `Urban planning/spatial JS tests passed: ${Lab.definitions.length} methods, ${results.length} benchmarks.`
);
