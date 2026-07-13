const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(__dirname, '../assets/js/modules/architecture-building-lab.js'),
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

const Lab = context.window.SCLab.ArchitectureBuildingLab;

if (!Lab) {
  throw new Error('ArchitectureBuildingLab export is missing.');
}

if (Lab.VERSION !== '0.13.0') {
  throw new Error(`Expected version 0.13.0, found ${Lab.VERSION}.`);
}

if (Lab.definitions.length !== 48) {
  throw new Error(`Expected 48 methods, found ${Lab.definitions.length}.`);
}

const rows = Lab.runBenchmarks();
const failed = rows.filter((row) => !row.passed);

if (failed.length) {
  throw new Error(JSON.stringify(failed, null, 2));
}

const record = Lab.run('ab.energy_use_intensity', {
  annualEnergyKWh: 100000,
  floorAreaM2: 1000,
});

if (record.outputs.euiKWhM2Year !== 100) {
  throw new Error('Energy-use-intensity calculation failed.');
}

if (
  record.schema !==
  'sc-lab-architecture-building-analysis/1.0'
) {
  throw new Error('Architecture/building contract schema failed.');
}

console.log(
  `Architecture/building JS tests passed: ${Lab.definitions.length} methods, ${rows.length} benchmarks.`
);
