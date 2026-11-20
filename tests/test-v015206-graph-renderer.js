#!/usr/bin/env node
// SC-LAB-UI-02: independent source/manifest guard for real Graph Studio renderer.
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const vm=require('node:vm');
const read=p=>fs.readFileSync(p,'utf8');
const php=read('includes/class-sc-lab-production-safe-boot-v015206.php');
const js=read('assets/js/sc-lab-safe-bootstrap-v015206.js');
const engine=read('assets/js/modules/scientific-visualization-engine-v0440.js');
const graph=read('assets/js/modules/graph-studio-v0470.js');
const manifest=JSON.parse(read('build/sc-lab-release-manifest.json'));
for(const p of ['assets/js/sc-lab-safe-bootstrap-v015206.js','includes/class-sc-lab-production-safe-boot-v015206.php']){
  assert.equal(manifest.wordpressCriticalFiles[p],
    crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),p+' critical hash');
}
assert.equal(manifest.releaseVersion,'0.163.1.9','release must remain compatible with Research Bridge 0.6.1');
for(const p of ['sc-lab-safe-bootstrap-v015206.js','sc-lab-graph-engine-v0440','sc-lab-graph-controller-v0470',
 'assets/js/modules/scientific-visualization-engine-v0440.js','assets/js/modules/graph-studio-v0470.js']){
 assert.ok(php.includes(p),'missing safe asset '+p);
}
assert.ok(php.includes("'sc-lab-graph-controller-v0470'),"),'Graph controller must precede safe boot');
assert.ok(!php.includes("wp_enqueue_script('sc-lab-app'"),'legacy megabundle must stay off');
for(const s of [js,engine,graph])new vm.Script(s);
assert.ok(js.includes("item.style.setProperty('display', 'none', 'important')"),'panels must not stack');
assert.ok(js.includes("item.style.removeProperty('display')"),'selected panel visible');
assert.ok(js.includes("graph.status().mounted"),'Graph's real status must survive safe boot');
assert.ok(js.includes("graph.mount()"),'selected Graph mounts on activation');
assert.ok(engine.includes('Lab.ScientificVisualizationEngineV0440={'),'real SVG engine exported');
assert.ok(graph.includes('Lab.GraphStudioV0470={'),'real Graph Studio controller exported');
assert.ok(graph.includes("render(q('canvas'),state.graph)"),'Graph invokes actual scientific engine');
assert.ok(read('tests/chromium-lab-graph-renderer.html').includes("svg[data-sve-version]"),
  'browser fixture must assert real SVG canvas');
assert.ok(read('scripts/run_chromium_lab_frontdoor.py').includes('chromium-lab-graph-renderer.html'),
  'real browser runner must cover Graph render');
console.log('PASS - SC-LAB-UI-02 scoped SVG renderer, exclusive module visibility, immutable manifest, browser coverage');
