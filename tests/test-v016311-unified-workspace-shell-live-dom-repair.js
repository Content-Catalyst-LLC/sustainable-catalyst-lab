'use strict';
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const js = fs.readFileSync(path.join(root, 'assets/js/sc-lab-unified-workspace-shell-v016311.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'assets/css/sc-lab-unified-workspace-shell-v016311.css'), 'utf8');
function ok(v, m) { if (!v) { console.error('FAIL - ' + m); process.exit(1); } }
ok(js.includes("selectors: ['[data-v0710-visualizer]'"), '4D module must bind to actual v0710 visualizer root');
ok(js.includes("'[data-v01540-workspace]'"), 'notebook live DOM selector missing');
ok(js.includes("'[data-v01630-workspace]'"), 'governance live DOM selector missing');
ok(js.includes('resolveModule'), 'live DOM resolver missing');
ok(js.includes('node.contains(root)'), 'shell self-capture guard missing');
ok(js.includes("root.setAttribute('data-sc-lab-shell-bound', '1')"), 'shell bound state missing');
ok(js.includes('MutationObserver'), 'late module observer missing');
ok(css.includes('sc-lab-v016311-progressive [data-v0710-visualizer]'), '4D first-paint collapse missing');
ok(css.includes('sc-lab-v016311-progressive [data-v01630-workspace]'), 'governance first-paint collapse missing');
ok(css.includes('[data-sc-lab-shell-module].is-active'), 'active module override missing');
console.log('PASS - v0.163.1.1 JavaScript/CSS live-DOM repair static contract');
