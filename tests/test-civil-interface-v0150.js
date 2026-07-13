const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(
    __dirname,
    '../assets/js/modules/civil-infrastructure-lab-v0150.js'
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

const Lab = context.window.SCLab.CivilInfrastructureLab;

if (!Lab || Lab.VERSION !== '0.15.0') {
  throw new Error('CivilInfrastructureLab repair export/version failed.');
}

if (Lab.definitions.length !== 48) {
  throw new Error(`Expected 48 civil methods, found ${Lab.definitions.length}.`);
}

const missingFormula = Lab.definitions.filter(
  (method) => !method.equation || !String(method.equation).trim()
);

if (missingFormula.length) {
  throw new Error(
    `Civil methods without visible equations: ${missingFormula.map((item) => item.id).join(', ')}`
  );
}

const rows = Lab.runBenchmarks();
const failed = rows.filter((row) => !row.passed);

if (failed.length) {
  throw new Error(JSON.stringify(failed, null, 2));
}

if (
  !source.includes('Engineering formula')
  || !source.includes('Executable formula expressions')
  || !source.includes('autoInit')
  || !source.includes("querySelectorAll('[data-civil-infrastructure-root]')")
) {
  throw new Error('Civil interface repair markers are incomplete.');
}

const record = Lab.run('ci.uniform_beam_moment', {
  loadNPerM: 10,
  spanM: 4,
});

if (record.outputs.maxMomentNm !== 20) {
  throw new Error('Civil formula execution failed.');
}

console.log(
  `Civil interface repair tests passed: ${Lab.definitions.length} formulas, ${rows.length} benchmarks.`
);
