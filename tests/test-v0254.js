'use strict';
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const runtime = fs.readFileSync(path.join(root, 'assets/js/sc-lab-runtime-stability-v0254.js'), 'utf8');
const checks = [
  '__SCLabRuntimeStabilityV0254',
  'AbortController',
  'stopImmediatePropagation',
  'data-sc-lab-lazy-host',
  'sc:lab:module-unmounting',
  'sc:lab:module-mounted',
  'SCLabRuntimeV0254API',
  'panelBudget',
  'popstate'
];
const missing = checks.filter((marker) => !runtime.includes(marker));
if (missing.length) {
  throw new Error('Missing v0.25.4 JavaScript markers: ' + missing.join(', '));
}
console.log('Runtime stability JavaScript checks passed: ' + checks.length);
