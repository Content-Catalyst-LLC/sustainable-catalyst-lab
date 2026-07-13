const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(
    __dirname,
    '../assets/js/modules/circular-economy-industrial-ecology-lab.js'
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

const Lab = context.window.SCLab.CircularEconomyIndustrialEcologyLab;

if (!Lab || Lab.VERSION !== '0.16.0') {
  throw new Error('CircularEconomyIndustrialEcologyLab export/version failed.');
}

if (Lab.definitions.length !== 48) {
  throw new Error(`Expected 48 methods, found ${Lab.definitions.length}.`);
}

const missingFormula = Lab.definitions.filter(
  (method) => !method.equation || !String(method.equation).trim()
);

if (missingFormula.length) {
  throw new Error(
    `Methods without visible formulas: ${missingFormula.map((item) => item.id).join(', ')}`
  );
}

const rows = Lab.runBenchmarks();
const failed = rows.filter((row) => !row.passed);

if (failed.length) {
  throw new Error(JSON.stringify(failed, null, 2));
}

const record = Lab.run('ce.circular_material_use_rate', {
  secondaryMaterialTonnes: 25,
  totalMaterialUseTonnes: 100,
});

if (record.outputs.circularMaterialUseFraction !== 0.25) {
  throw new Error('Circular material use calculation failed.');
}

if (
  !source.includes('Accounting or engineering formula')
  || !source.includes('Executable output expressions')
  || !source.includes('autoInit')
) {
  throw new Error('Formula-visible interface markers are missing.');
}

console.log(
  `Circular economy/industrial ecology JS tests passed: ${Lab.definitions.length} methods, ${rows.length} benchmarks.`
);
