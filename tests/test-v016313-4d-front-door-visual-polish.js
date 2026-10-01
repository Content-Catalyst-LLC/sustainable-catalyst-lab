'use strict';
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const js = fs.readFileSync(path.join(root, 'assets/js/sc-lab-4d-front-door-visual-polish-v016313.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'assets/css/sc-lab-4d-front-door-visual-polish-v016313.css'), 'utf8');
function ok(value, message) { if (!value) { console.error('FAIL - ' + message); process.exit(1); } }
ok(js.includes("const STORAGE_KEY = 'sc-lab-v016313-frontdoor-panel-state'"), 'session panel state missing');
ok(js.includes(".sc-lab-v015209-explorer"), 'primary response explorer missing');
ok(js.includes(".sc-lab-v015210-analysis"), 'uncertainty panel selector missing');
ok(js.includes(".sc-lab-v015211-linked"), 'linked views panel selector missing');
ok(js.includes(".sc-lab-v015212-persistence"), 'scene persistence panel selector missing');
ok(js.includes(".sc-lab-v01530-workspace"), 'project workspace selector missing');
ok(js.includes('is-v016313-collapsed'), 'progressive panel state missing');
ok(css.includes('height:clamp(360px,30vw,440px)'), 'compact canvas sizing missing');
ok(css.includes('.sc-lab-v016313-metrics-strip'), 'compact metric strip missing');
ok(css.includes('[data-overview-signals]{display:block!important}'), 'signals retention missing');
ok(!js.includes('data-overview-refresh'), 'polish should not take over Scientific signals behavior');
console.log('PASS - v0.163.1.3 front-door visual polish JavaScript/CSS contract');
