'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

global.window = {
  SCLab: {},
  setTimeout: () => 0,
  addEventListener: () => {},
};

require(
  path.resolve(
    __dirname,
    '../assets/js/modules/'
      + 'biochemistry-production-v0211.js'
  )
);

const production =
  global.window.SCLab.BiochemistryProduction;

assert.ok(production, 'Production runtime export');
assert.equal(production.VERSION, '0.21.1');
assert.equal(typeof production.initialize, 'function');
assert.equal(typeof production.repair, 'function');
assert.equal(typeof production.open, 'function');
assert.equal(typeof production.status, 'function');
assert.equal(typeof production.health, 'function');

console.log(
  'Lab v0.21.1 JS structural tests passed.'
);
