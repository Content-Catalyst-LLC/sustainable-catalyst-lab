const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(
    __dirname,
    '../assets/js/modules/microbiology-laboratory.js'
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

const Lab = context.window.SCLab.MicrobiologyLaboratory;

if (!Lab || Lab.VERSION !== '0.20.0') {
  throw new Error('MicrobiologyLaboratory export/version failed.');
}

if (Lab.definitions.length !== 48) {
  throw new Error(`Expected 48 methods, found ${Lab.definitions.length}.`);
}

const missing = Lab.definitions.filter(
  (method) => !method.equation || !String(method.equation).trim()
);

if (missing.length) {
  throw new Error(
    `Methods without visible formulas: ${missing.map((item) => item.id).join(', ')}`
  );
}

const rows = Lab.runBenchmarks();
const failed = rows.filter((row) => !row.passed);

if (failed.length) {
  throw new Error(JSON.stringify(failed, null, 2));
}

const record = Lab.run('mb.generation_time', {
  specificGrowthRatePerHour: Math.log(2),
});

if (Math.abs(record.outputs.generationTimeHours - 1) > 1e-8) {
  throw new Error('Generation-time calculation failed.');
}

if (
  !source.includes('Microbiology or laboratory formula')
  || !source.includes('Executable output expressions')
  || !source.includes('autoInit')
) {
  throw new Error('Formula-visible interface markers are missing.');
}

console.log(
  `Microbiology laboratory JS tests passed: ${Lab.definitions.length} methods, ${rows.length} benchmarks.`
);
