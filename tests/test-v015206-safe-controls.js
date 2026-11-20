#!/usr/bin/env node
/* SC-LAB-UI-01: fail the release if bounded safe controls or their integrity pins regress. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const js = read('assets/js/sc-lab-safe-bootstrap-v015206.js');
const php = read('includes/class-sc-lab-production-safe-boot-v015206.php');
const template = read('templates/lab-app.php');
const project = read('assets/js/modules/projects.js');
const workspace = read('assets/js/modules/workspace.js');
const manifest = JSON.parse(read('build/sc-lab-release-manifest.json'));

new vm.Script(js, { filename: 'sc-lab-safe-bootstrap-v015206.js' });
for (const file of ['assets/js/sc-lab-safe-bootstrap-v015206.js',
                    'includes/class-sc-lab-production-safe-boot-v015206.php',
                    'templates/lab-app.php']) {
  const digest = crypto.createHash('sha256').update(fs.readFileSync(path.join(root, file))).digest('hex');
  assert.equal(manifest.wordpressCriticalFiles[file], digest, 'WordPress release hash: ' + file);
}
for (const fragment of ["'assets/js/modules/core.js'",
                        "'assets/js/modules/projects.js'",
                        "'assets/js/modules/workspace.js'",
                        "'sc-lab-safe-projects-v015206'",
                        "'sc-lab-safe-workspace-v015206'"]) {
  assert.ok(php.includes(fragment), 'safe dependency missing ' + fragment);
}
for (const forbidden of ['sc-lab-optional-bundle-v015204.js', 'sc-lab-bootstrap-v015204.js']) {
  assert.ok(!php.includes("wp_enqueue_script('" + forbidden), 'unexpected legacy critical/optional bootstrap');
}
for (const fragment of ['new w.SCLab.Projects()', "store.add('experiments'", "store.add('notes'",
                        'function renderCommandResults(', 'function selectCommand(',
                        'function recordList(', "'[data-open-module], [data-lab-module-button]'",
                        "event.target.closest('[data-command-action]')",
                        "'[data-lab-command-open], [data-v0483-search]'"]) {
  assert.ok(js.includes(fragment), 'missing bounded behavior: ' + fragment);
}
assert.ok(project.includes("const KEY = 'scLabProjectsV010'"), 'canonical project model not pinned');
assert.ok(workspace.includes('Lab.Workspace='), 'canonical command index not pinned');
assert.ok(template.includes('data-lab-command-open aria-label="Open Lab command search"'),
  'shortcut must be accessible to pointer and keyboard');
assert.ok(js.includes("notify(root, 'Workspace unavailable in this Lab view: ' + id)"),
  'missing explicit unavailable workspace state');
assert.ok(js.includes("    }, true);\n\n    const search"),
  'navigation must capture before descendant event handlers stop propagation');
assert.ok(!js.includes('localStorage.setItem('), 'no new shadow project storage');
assert.ok(!js.includes('fetch('), 'safe-boot record actions must not make server writes');
assert.ok(read('tests/chromium-lab-safe-controls.html').includes('data-cert="running"'),
  'real-browser fixture missing');
console.log('PASS - SC-LAB-UI-01 safe actions, navigation, search, bounded dependencies and three manifest hashes');
