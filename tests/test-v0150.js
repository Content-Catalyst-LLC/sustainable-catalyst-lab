const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(
    __dirname,
    '../assets/js/modules/sustainable-cities-resilience-lab.js'
  ),
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

const Lab = context.window.SCLab.SustainableCitiesResilienceLab;

if (!Lab || Lab.VERSION !== '0.15.0') {
  throw new Error('SustainableCitiesResilienceLab export/version failed.');
}

if (Lab.definitions.length !== 48) {
  throw new Error(`Expected 48 methods, found ${Lab.definitions.length}.`);
}

const rows = Lab.runBenchmarks();
const failed = rows.filter((row) => !row.passed);

if (failed.length) {
  throw new Error(JSON.stringify(failed, null, 2));
}

const record = Lab.run('sc.energy_per_capita', {
  annualEnergyMWh: 8000,
  population: 1000,
});

if (record.outputs.energyMWhPerCapitaYear !== 8) {
  throw new Error('Energy-per-capita calculation failed.');
}

if (!source.includes('Engineering formula')) {
  throw new Error('Visible formula interface marker is missing.');
}

console.log(
  `Sustainable cities/resilience JS tests passed: ${Lab.definitions.length} methods, ${rows.length} benchmarks.`
);
