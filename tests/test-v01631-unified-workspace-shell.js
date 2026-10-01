'use strict';
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const js = fs.readFileSync(path.join(root, 'assets/js/sc-lab-unified-workspace-shell-v01631.js'), 'utf8');
function ok(v, m) { if (!v) { console.error('FAIL - ' + m); process.exit(1); } }
const ids = ['four-d','notebook','batch','compute','cross-study','replication','review','research-os','programs','resources','governance'];
ids.forEach(id => ok(js.includes(`id: '${id}'`), 'missing workspace ' + id));
ok(js.includes('node.hidden = !active'), 'single visible workspace behavior missing');
ok(js.includes('overview.hidden = id !== \'overview\''), 'overview progressive visibility missing');
ok(js.includes('stage.appendChild(node)'), 'workspace stage consolidation missing');
ok(js.includes('MutationObserver'), 'late module registration missing');
ok(js.includes('sessionStorage'), 'workspace state preservation missing');
ok(js.includes('captureBoundary'), 'governance boundary consolidation missing');
console.log('PASS - v0.163.1 JavaScript workspace shell static contract');
