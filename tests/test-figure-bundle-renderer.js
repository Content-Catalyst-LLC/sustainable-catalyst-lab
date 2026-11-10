'use strict';
// SC-FIG-01 generic sc.figure-bundle.v1 renderer: package verification contract.
// Synthetic packages in tests/fixtures/figure-bundle-generic (derived from the amd64 Workbench staging body).
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
const R = require(path.join(root, 'assets/js/modules/graph-studio-figure-bundle-renderer.js'));
const dir = path.join(__dirname, 'fixtures/figure-bundle-generic');
const jsText = fs.readFileSync(path.join(root, 'assets/js/modules/graph-studio-figure-bundle-renderer.js'), 'utf8');
function ok(value, message) { if (!value) { console.error('FAIL - ' + message); process.exit(1); } }
const read = (name) => ({ name, bytes: new Uint8Array(fs.readFileSync(path.join(dir, name))) });
const text = (name, mutate) => {
  const t = mutate(fs.readFileSync(path.join(dir, name), 'utf8'));
  return { name, bytes: new Uint8Array(Buffer.from(t, 'utf8')) };
};
const bundleWith = (name, edit) => {
  const b = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
  edit(b);
  return { name, bytes: new Uint8Array(Buffer.from(JSON.stringify(b, null, 1), 'utf8')) };
};

async function refused(files, needle, label, opts) {
  try {
    await R.verifyPackage(files, '3.3.1', opts && opts.expected);
  } catch (reasons) {
    ok(Array.isArray(reasons) && reasons.some((r) => r.includes(needle)), label + ' refusal reason: ' + JSON.stringify(reasons));
    return;
  }
  ok(false, label + ' should be refused');
}

(async () => {
  const source = JSON.parse(fs.readFileSync(path.join(dir, 'SOURCE.json'), 'utf8'));
  for (const [file, sha] of Object.entries(source.files)) {
    ok(crypto.createHash('sha256').update(fs.readFileSync(path.join(dir, file))).digest('hex') === sha, file + ' matches SOURCE.json');
  }
  ok(!/innerHTML|insertAdjacentHTML|document\.write|eval\(|fetch\(|XMLHttpRequest/.test(jsText), 'module never injects HTML, evaluates code or fetches');

  // 1. Bundle + Plotly spec: verified by canonical-JSON hash (the file is producer-formatted, not byte-identical).
  const pts = await R.verifyPackage([read('points.bundle.json'), read('points.plotly.json')], '3.3.1');
  ok(pts.views.length === 1 && pts.views[0].state === 'rendered-plotly' && pts.views[0].hashMode === 'canonical-json', 'points renders through the canonical-JSON hash');
  ok(pts.views[0].artifact.sha256 === source.specSha256, 'points view is the Workbench spec hash');
  ok(pts.bundleSha256 === source.files['points.bundle.json'], 'bundle byte hash reported');
  // Pinning the registered bundle hash (Workspace output / Research object) works both ways.
  await R.verifyPackage([read('points.bundle.json'), read('points.plotly.json')], '3.3.1', source.files['points.bundle.json']);
  await refused([read('points.bundle.json'), read('points.plotly.json')], 'registered hash', 'bundle not matching registered hash', { expected: '1'.repeat(64) });

  // 2. Mixed views: Plotly drawn, PNG static fallback (raw bytes), Vega-Lite unsupported, SVG missing.
  const mixed = await R.verifyPackage([read('mixed.bundle.json'), read('points.plotly.json'), read('static.png'), read('view.vega-lite.json')], '3.3.1');
  const states = mixed.views.map((v) => v.state + ':' + (v.hashMode || '-'));
  ok(JSON.stringify(states) === JSON.stringify(['rendered-plotly:canonical-json', 'static-png:raw-bytes', 'unsupported:raw-bytes', 'missing:-']), 'mixed view states ' + JSON.stringify(states));

  // 3. Referenced view not supplied: metadata-only, nothing drawn.
  const only = await R.verifyPackage([read('points.bundle.json')], '3.3.1');
  ok(only.views[0].state === 'missing', 'bundle alone is metadata-only');

  // Integrity refusals.
  await refused([read('points.bundle.json'), text('points.plotly.json', (t) => t.replace('5.0,', '5.1,'))], 'not referenced', 'tampered spec value');
  await refused([read('points.bundle.json'), read('points.plotly.json'), read('static.png')], 'not referenced', 'stray file');
  const fakePng = { name: 'static.png', bytes: new Uint8Array(Buffer.from('not a png')) };
  await refused([bundleWith('mixed.bundle.json', (b) => { b.artifacts[1].sha256 = crypto.createHash('sha256').update(fakePng.bytes).digest('hex'); }), fakePng],
    'not a PNG', 'image/png with non-PNG bytes');
  await refused([read('points.plotly.json')], 'exactly one', 'no bundle');
  await refused([read('points.bundle.json'), read('mixed.bundle.json')], 'exactly one', 'two bundles');

  // Content policy on the spec (hash re-pinned so only the policy can refuse it).
  const injected = JSON.parse(fs.readFileSync(path.join(dir, 'points.plotly.json'), 'utf8'));
  injected.layout.images = [];
  const injectedBytes = new Uint8Array(Buffer.from(JSON.stringify(injected), 'utf8'));
  await refused([bundleWith('points.bundle.json', (b) => { b.artifacts[0].sha256 = crypto.createHash('sha256').update(injectedBytes).digest('hex'); delete b.rendering.visualizationSpecSha256; }),
    { name: 'spec.json', bytes: injectedBytes }], 'layout.images', 'layout.images in a re-pinned spec');
  try { await R.verifyPackage([read('points.bundle.json'), read('points.plotly.json')], '2.35.2'); ok(false, 'wrong plotly.js accepted'); }
  catch (r) { ok(r.some((m) => m.includes('loaded plotly.js is 2.35.2')), 'wrong loaded plotly.js refused'); }

  // Bundle validation and scientific-honesty rules.
  await refused([bundleWith('points.bundle.json', (b) => { b.evidenceClass = 'observed'; }), read('points.plotly.json')], 'no promotion to observed', 'literature-derived relabelled observed');
  await refused([bundleWith('points.bundle.json', (b) => { b.scientificContext.measurementStatus = 'observed'; }), read('points.plotly.json')], 'no promotion to observed', 'measurement status promoted');
  await refused([bundleWith('points.bundle.json', (b) => { b.evidenceClass = 'measured'; }), read('points.plotly.json')], 'evidenceClass', 'unknown evidence class');
  await refused([bundleWith('points.bundle.json', (b) => { b.scientificContext.limitations = []; }), read('points.plotly.json')], 'limitation', 'no limitations');
  await refused([bundleWith('points.bundle.json', (b) => { b.sourceRefs = []; }), read('points.plotly.json')], 'sourceRefs', 'no sources');
  await refused([bundleWith('points.bundle.json', (b) => { b.title = '<a href=x>t</a> title'; }), read('points.plotly.json')], 'forbidden markup', 'markup in bundle');
  await refused([bundleWith('points.bundle.json', (b) => { b.rendering.visualizationSpecSha256 = 'f'.repeat(64); }), read('points.plotly.json')], 'visualizationSpecSha256', 'spec hash not among artifacts');
  await refused([bundleWith('points.bundle.json', (b) => { b.provenance.reproducibility = 'certified'; }), read('points.plotly.json')], 'provenance', 'unknown reproducibility');
  await refused([{ name: 'big.json', bytes: new Uint8Array(8 * 1024 * 1024 + 1) }], '8 MiB', 'oversized file');
  console.log('PASS - SC-FIG-01 generic sc.figure-bundle.v1 renderer package contract');
})().catch((e) => { console.error('FAIL - ' + (e && e.stack || e)); process.exit(1); });
