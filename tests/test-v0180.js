const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(
    __dirname,
    '../assets/js/modules/aerospace-engineering-flight-systems-lab.js'
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

const Lab = context.window.SCLab.AerospaceEngineeringFlightSystemsLab;

if (!Lab || Lab.VERSION !== '0.18.0') {
  throw new Error('AerospaceEngineeringFlightSystemsLab export/version failed.');
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

const record = Lab.run('af.dynamic_pressure', {
  densityKgM3: 1,
  trueAirspeedMps: 10,
});

if (record.outputs.dynamicPressurePa !== 50) {
  throw new Error('Dynamic-pressure calculation failed.');
}

if (
  !source.includes('Aeronautical or flight-systems formula')
  || !source.includes('Executable output expressions')
  || !source.includes('autoInit')
) {
  throw new Error('Formula-visible interface markers are missing.');
}

console.log(
  `Aerospace engineering/flight systems JS tests passed: ${Lab.definitions.length} methods, ${rows.length} benchmarks.`
);
