#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const read = (relative) => fs.readFileSync(path.join(root, relative), 'utf8');
const exists = (relative) => fs.existsSync(path.join(root, relative));

const required = [
  'assets/js/modules/release-v095.js',
  'assets/css/sc-lab-v095.css',
  'contracts/report-composition.schema.json',
  'contracts/restore-validation.schema.json',
  'contracts/accessibility-audit.schema.json',
  'docs/RELEASE_NOTES_0.9.5.md',
  'docs/REPORT_COMPOSER_ACCESSIBILITY_RESTORE_VALIDATION.md'
];
required.forEach((file) => assert(exists(file), `Missing ${file}`));

const main = read('sustainable-catalyst-lab.php');
assert(
  /Version:\s+\d+\.\d+\.\d+/.test(main),
  'Valid plugin header version is missing'
);
assert(
  /define\(\s*['"]SC_LAB_VERSION['"]\s*,\s*['"]\d+\.\d+\.\d+['"]\s*\)/.test(main),
  'Valid runtime version constant is missing'
);

const plugin = read('includes/class-sc-lab-plugin.php');
assert(plugin.includes("'release-v095'"), 'v0.9.5 JavaScript module is not enqueued');
assert(plugin.includes("'sc-lab-v095'"), 'v0.9.5 stylesheet is not enqueued');
assert(plugin.includes('sc_lab_report_composer'), 'Report Composer focused shortcode is missing');


const projectsModule = read('assets/js/modules/projects.js');
assert(
  projectsModule.includes('schemaVersion'),
  'Project schemaVersion marker is missing'
);
['reportPackages', 'restorePreflights', 'migrationValidationRecords'].forEach((key) => assert(projectsModule.includes(`'${key}'`), `Project registry missing ${key}`));

const js = read('assets/js/modules/release-v095.js');
new Function(js);
assert(!/(^|[^A-Za-z0-9_$])w\.SCLabV095/.test(js), 'Undefined window alias detected in v0.9.5 module');
assert(js.includes('workspaceContentFingerprint'), 'Restore integrity fingerprint helper is missing');
[
  'Report Composer',
  'sc-lab-report-composition/1.0',
  'sc-lab-accessibility-audit/1.0',
  'sc-lab-restore-validation/1.0',
  'automatic-pre-replace-safety-backup',
  'Alt+Up/Alt+Down',
  'sc-lab-report-package/1.0',
  'sourceSha256',
  'Type REPLACE',
  'runLegacyMigrationValidation',
  'reportRevisions',
  'reportPackages',
  'restorePreflights',
  'restoreReceipts',
  'accessibilityAudits',
  'migrationValidationRecords'
].forEach((marker) => assert(js.includes(marker), `Missing JavaScript marker: ${marker}`));

[
  'contracts/report-composition.schema.json',
  'contracts/restore-validation.schema.json',
  'contracts/accessibility-audit.schema.json',
  'contracts/project.schema.json',
  'contracts/report.schema.json'
].forEach((file) => JSON.parse(read(file)));

const projectSchema = JSON.parse(read('contracts/project.schema.json'));
const projectProperties = projectSchema.properties || {};
['reportDrafts', 'reportRevisions', 'reportPackages', 'restorePreflights', 'restoreReceipts', 'accessibilityAudits', 'migrationValidationRecords']
  .forEach((key) => assert(projectProperties[key], `Project schema missing ${key}`));

const reportSchema = JSON.parse(read('contracts/report.schema.json'));
assert((reportSchema.properties || {}).composition, 'Report schema missing composition property');

const ignore = read('.gitignore');
['__pycache__/', '*.py[cod]', '.pytest_cache/'].forEach((marker) => assert(ignore.includes(marker), `.gitignore missing ${marker}`));

console.log('Lab v0.9.5 structural tests passed.');
