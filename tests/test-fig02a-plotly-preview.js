'use strict';
// SC-FIG-01 / FIG-02A Graph Studio Plotly preview: hashing and content-policy contract.
// Uses synthetic Workbench compile responses (tests/fixtures/fig02a-preview-synthetic.json).
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
const preview = require(path.join(root, 'assets/js/modules/graph-studio-plotly-preview-fig02a.js'));
const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/fig02a-preview-synthetic.json'), 'utf8'));
const source = JSON.parse(fs.readFileSync(path.join(root, 'assets/lib/plotly-3.3.1/SOURCE.json'), 'utf8'));
const php = fs.readFileSync(path.join(root, 'includes/class-sc-lab-graph-studio-plotly-preview-fig02a.php'), 'utf8');
const jsText = fs.readFileSync(path.join(root, 'assets/js/modules/graph-studio-plotly-preview-fig02a.js'), 'utf8');
function ok(value, message) { if (!value) { console.error('FAIL - ' + message); process.exit(1); } }

// Python json.dumps(indent=1) spelling of each response, as Workbench/FastAPI would emit floats.
const raw = fs.readFileSync(path.join(__dirname, 'fixtures/fig02a-preview-synthetic.json'), 'utf8');
const texts = {};
for (const key of Object.keys(fixture.responses)) {
  const start = raw.indexOf('"' + key + '": {');
  ok(start > 0, 'fixture response ' + key);
  // Slice the balanced object for this key out of the original text (keeps number lexemes).
  let depth = 0, i = raw.indexOf('{', start), j = i;
  for (; j < raw.length; j++) {
    if (raw[j] === '"') { j++; while (raw[j] !== '"') { j += raw[j] === '\\' ? 2 : 1; } continue; }
    if (raw[j] === '{') depth++;
    if (raw[j] === '}' && --depth === 0) break;
  }
  texts[key] = raw.slice(i, j + 1);
}

function expectRefused(text, needle, label, plotlyVersion) {
  return preview.verify(text, plotlyVersion).then(
    () => ok(false, label + ' should be refused'),
    (reasons) => ok(Array.isArray(reasons) && reasons.some((r) => r.includes(needle)), label + ' refusal reason: ' + JSON.stringify(reasons)));
}

(async () => {
  // Vendored plotly.js is the pinned, byte-identical Workbench copy.
  const vendored = fs.readFileSync(path.join(root, 'assets/lib/plotly-3.3.1/plotly.min.js'));
  const digest = crypto.createHash('sha256').update(vendored).digest('hex');
  ok(digest === source.sha256, 'vendored plotly.js sha256 matches SOURCE.json');
  ok(php.includes("const PLOTLY_JS_SHA256 = '" + digest + "'"), 'PHP loader pins the vendored sha256');
  ok(vendored.slice(0, 40).toString().includes('plotly.js v3.3.1'), 'vendored plotly.js header is v3.3.1');
  ok(preview.expectedPlotlyJs === '3.3.1' && source.version === '3.3.1', 'JS module pins plotly.js 3.3.1');
  ok(!/https?:\/\/(cdn|unpkg|jsdelivr)/i.test(jsText + php), 'no CDN references');
  ok(!/innerHTML|insertAdjacentHTML|document\.write|eval\(/.test(jsText), 'module never injects HTML or evaluates code');

  // Hashes computed by Workbench (Python) recompute exactly in the browser module.
  for (const [key, text] of Object.entries(texts)) {
    const res = await preview.verify(text, '3.3.1');
    ok(res.specSha256 === fixture.responses[key].plotly.specSha256, key + ' specSha256 recomputes');
    ok(res.resultHash === fixture.responses[key].resultHash, key + ' resultHash recomputes');
  }
  // Plain JSON.stringify loses Python float spelling (5.0 -> 5); the lexeme-preserving path is required.
  const naive = await preview.sha256Hex(JSON.stringify(fixture.responses.points.plotly.figure, Object.keys(fixture.responses.points.plotly.figure).sort()));
  ok(naive !== fixture.responses.points.plotly.specSha256, 'naive JSON hashing would not match (guards the canonical path)');

  const pts = texts.points;
  ok(pts.includes('5.0,'), 'fixture keeps the Python float spelling 5.0');
  await expectRefused(pts.replace('5.0,', '5.1,'), 'mismatch', 'tampered numeric value');
  await expectRefused(pts.replace('"Study"', '"Study (edited)"'), 'mismatch', 'tampered axis title');
  await expectRefused(pts.replace('"Study"', '"<a href=x>Study</a>"'), 'forbidden markup', 'injected link');
  await expectRefused(pts.replace('"showlegend": true', '"showlegend": true, "images": []'), 'layout.images', 'layout images');
  await expectRefused(pts.replace('"showlegend": true', '"showlegend": true, "template": {}'), 'layout.template', 'layout template');
  await expectRefused(pts.replace('"type": "scatter"', '"type": "scattergl"'), 'not allowed', 'unlisted trace type');
  await expectRefused(pts.replace('"plotlyJsVersion": "3.3.1"', '"plotlyJsVersion": "2.35.2"'), 'Lab pins 3.3.1', 'compiled for another plotly.js');
  await expectRefused(pts, 'loaded plotly.js is 2.35.2', 'wrong loaded plotly.js', '2.35.2');
  await expectRefused(pts.replace('"ok": true', '"ok": false'), 'not a successful', 'failed compile result');
  await expectRefused(pts.replace('"evidenceClass": "literature-derived"', '"evidenceClass": "measured"'), 'evidenceClass', 'unknown evidence class');
  await expectRefused(pts.replace('"evidenceClass": "literature-derived"', '"evidenceClass": "observed"'), 'resultHash mismatch', 'evidence class promoted after compile');
  // Cross-system: exact HTTP bodies from the amd64 Workbench staging image (compact FastAPI JSON).
  const stagingDir = path.join(__dirname, 'fixtures/fig02a-staging-amd64');
  const staging = JSON.parse(fs.readFileSync(path.join(stagingDir, 'SOURCE.json'), 'utf8'));
  for (const [file, meta] of Object.entries(staging.files)) {
    const body = fs.readFileSync(path.join(stagingDir, file));
    ok(crypto.createHash('sha256').update(body).digest('hex') === meta.sha256, 'staging ' + file + ' bytes match SOURCE.json');
    const res = await preview.verify(body.toString('utf8'), '3.3.1');
    ok(res.response.figureBundle.evidenceClass === meta.evidenceClass, 'staging ' + file + ' evidence class ' + meta.evidenceClass);
    ok(res.specSha256 === res.response.plotly.specSha256 && res.resultHash === res.response.resultHash, 'staging ' + file + ' hashes recompute');
  }
  const stagingPoints = fs.readFileSync(path.join(stagingDir, 'points.json'), 'utf8');
  ok(JSON.parse(stagingPoints).plotly.specSha256 === fixture.responses.points.plotly.specSha256, 'amd64 staging spec hash equals macOS-generated spec hash');
  await expectRefused(stagingPoints.replace('"y":[5.0,', '"y":[5.1,'), 'mismatch', 'tampered staging value');
  const modelled = fs.readFileSync(path.join(stagingDir, 'modelled-line.json'), 'utf8');
  await expectRefused(modelled.replace('"evidenceClass":"modelled"', '"evidenceClass":"observed"'), 'mismatch', 'modelled result relabelled observed');

  await expectRefused('{"ok": true, NaN}', 'invalid JSON', 'malformed JSON');
  await expectRefused('x'.repeat(8 * 1024 * 1024 + 1), '8 MiB', 'oversized response');
  console.log('PASS - FIG-02A Graph Studio Plotly preview hashing and content-policy contract');
})().catch((e) => { console.error('FAIL - ' + (e && e.stack || e)); process.exit(1); });
