'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const file = path.join(__dirname, '..', 'assets', 'js', 'modules', 'electrical-embedded-lab.js');
const context = {
  window: { SCLab: { util: { esc: value => String(value), now: () => '2026-07-12T00:00:00Z', fingerprint: value => `fp-${JSON.stringify(value).length}` } } },
  console, CustomEvent: function CustomEvent() {}
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(file, 'utf8'), context, { filename: file });
const E = context.window.SCLab.ElectricalEmbedded;
assert(E && E.VERSION === '0.10.0', 'Electrical Lab version failed');
assert(E.definitions.length >= 45, 'Electrical method catalog is incomplete');
assert(E.definitions.some(item => item.id === 'electrical.series-rlc'), 'RLC method missing');
assert(E.definitions.some(item => item.id === 'embedded.i2c-pullup'), 'I2C method missing');
assert(E.definitions.some(item => item.id === 'power.thermal-junction'), 'Thermal validation method missing');
const ohm = E.run('electrical.ohms-law', { voltage: 12, resistance: 6 });
assert(ohm.outputs.current === 2 && ohm.outputs.power === 24, "Ohm's law failed");
const parallel = E.run('electrical.resistors-parallel', { resistances: '100,100' });
assert(Math.abs(parallel.outputs.equivalentResistance - 50) < 1e-9, 'Parallel resistance failed');
const adc = E.run('embedded.adc-quantization', { bits: 10, reference: 3.3, inputVoltage: 1.65 });
assert(adc.outputs.levels === 1024 && adc.outputs.code >= 511 && adc.outputs.code <= 512, 'ADC quantization failed');
const pwm = E.run('embedded.pwm-average', { supply: 12, duty: 25, frequency: 1000 });
assert(pwm.outputs.averageVoltage === 3 && pwm.outputs.rmsVoltage === 6, 'PWM calculation failed');
const suite = E.runBenchmarks();
assert(suite.length >= 10 && suite.every(item => item.passed), 'Electrical benchmark suite failed');
const profile = E.makeDeviceProfile({ board: 'esp32', name: 'Environmental node', supplyVoltage: 3.3 });
assert(profile.schema === 'sc-lab-embedded-device/1.0' && profile.boardId === 'esp32', 'Device profile failed');
const interfaceRecord = E.validateInterface({ sourceVoltage: 3.3, targetVoltage: 3.3 });
assert(interfaceRecord.status === 'PASS_SCREENING', 'Interface validation failed');
assert(Object.keys(E.firmwareTemplates).length >= 4, 'Firmware templates missing');
console.log(`Lab v0.10.0 electrical tests passed: ${E.definitions.length} methods, ${suite.length} benchmarks.`);
