'use strict';
// SC-FIG-02B Vega-Lite views: grammar policy, usermeta.sc scientific contract, table model and the
// Python <-> JavaScript canonical dataset hash. Drawing, SVG export and SVG policy run in the Chromium harness.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
globalThis.SCLabPlotlyPreviewFIG02A = require(path.join(root, 'assets/js/modules/graph-studio-plotly-preview-fig02a.js'));
const V = require(path.join(root, 'assets/js/modules/graph-studio-vega-lite-fig02b.js'));
const dir = path.join(__dirname, 'fixtures/fig02b-vega-lite');
const jsText = fs.readFileSync(path.join(root, 'assets/js/modules/graph-studio-vega-lite-fig02b.js'), 'utf8')
  .replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, ''); // code only, not comments
function ok(value, message) { if (!value) { console.error('FAIL - ' + message); process.exit(1); } }
const readText = (name) => fs.readFileSync(path.join(dir, name), 'utf8');
const json = (name) => JSON.parse(readText(name));

async function refused(label, mutate, needle) {
  const view = json('erw.vega-lite.json'), bundle = json('erw.bundle.json');
  mutate(view, bundle);
  const reasons = await V.viewErrors(JSON.stringify(view), view, bundle);
  ok(reasons.some((r) => r.includes(needle)), label + ' refused with "' + needle + '": ' + JSON.stringify(reasons));
}

(async () => {
  const source = json('SOURCE.json');
  for (const [file, sha] of Object.entries(source.files)) {
    ok(crypto.createHash('sha256').update(fs.readFileSync(path.join(dir, file))).digest('hex') === sha, file + ' matches SOURCE.json');
  }
  for (const [file, sha] of Object.entries(V.vendorSha256)) {
    ok(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, 'assets/lib', file))).digest('hex') === sha, 'vendor ' + file + ' matches its pin');
    const meta = JSON.parse(fs.readFileSync(path.join(root, 'assets/lib', path.dirname(file), 'SOURCE.json'), 'utf8'));
    ok(meta.sha256 === sha && /BSD-3-Clause/.test(meta.licence), 'vendor ' + file + ' SOURCE.json agrees and records the licence');
  }
  ok(!/innerHTML|insertAdjacentHTML|document\.write|\beval\(|new Function|fetch\(|XMLHttpRequest/.test(jsText), 'module never injects HTML, evaluates code or fetches');
  ok(!/https?:\/\/(?!vega\.github\.io\/schema|www\.w3\.org)/.test(jsText), 'module names no remote origin other than schema and XML namespace identifiers');

  // 1. Both synthetic acceptance views pass; the Python generator's dataset hash equals the JS canonical hash.
  for (const [b, v] of [['erw.bundle.json', 'erw.vega-lite.json'], ['metrics.bundle.json', 'metrics.vega-lite.json']]) {
    const text = readText(v), view = JSON.parse(text), bundle = json(b);
    ok((await V.viewErrors(text, view, bundle)).length === 0, v + ' accepted for ' + b);
    ok((await V.datasetSha256FromText(text)) === view.usermeta.sc.datasetSha256, v + ' dataset hash agrees between Python and JavaScript');
    ok(bundle.artifacts.some((a) => V.isVegaLiteMedia(a.mediaType)), b + ' declares a Vega-Lite artifact');
  }

  // 2. Grammar policy.
  await refused('remote data', (v) => { v.data = { url: 'https://example.org/data.csv' }; }, 'not allowed');
  await refused('named datasets', (v) => { v.datasets = { a: [] }; }, 'not allowed');
  await refused('params', (v) => { v.params = [{ name: 'brush', select: 'interval' }]; }, 'params is not allowed');
  await refused('calculate', (v) => { v.transform = [{ calculate: 'datum.cdr * 2', as: 'x' }]; }, 'calculate is not allowed');
  await refused('string filter', (v) => { v.layer[0].transform = [{ filter: 'datum.cdr > 1' }]; }, 'filter');
  await refused('labelExpr', (v) => { v.layer[1].encoding.y.axis = { labelExpr: 'datum.label' }; }, 'is an expression');
  await refused('href channel', (v) => { v.layer[3].encoding.href = { field: 'series' }; }, 'not allowed');
  await refused('image mark', (v) => { v.layer[3].mark = 'image'; }, 'not in the allowed set');
  await refused('nested row object', (v) => { v.data.values[0].nested = { a: 1 }; }, 'flat');

  // 3. Scientific contract.
  await refused('missing profile', (v) => { v.usermeta.sc.profile = 'other'; }, 'sc-vega-lite-v1');
  await refused('field without unit', (v) => { delete v.usermeta.sc.fields.cdr; }, 'has no label and unit');
  await refused('title hiding unit', (v) => { v.layer[1].encoding.y.title = 'Uptake'; }, 'hides its unit');
  await refused('uncertainty not drawn', (v) => { v.layer.splice(0, 1); v.layer.splice(1, 1); }, 'not drawn');
  await refused('unknown uncertainty kind', (v) => { v.usermeta.sc.uncertainty.kind = 'about'; }, 'uncertainty');
  await refused('no evidence field', (v) => { delete v.usermeta.sc.evidenceField; }, 'evidenceField');
  await refused('modelled rows promoted to observed', (v) => { v.data.values.forEach((r) => { if (r.evidenceClass === 'modelled') { r.evidenceClass = 'observed'; } }); }, 'no promotion to observed');
  await refused('mixed classes not encoded', (v) => { delete v.layer[1].encoding.strokeDash; delete v.layer[3].encoding.shape; }, 'is not encoded');
  await refused('data edited after hashing', (v) => { v.data.values[0].cdr = 99; }, 'do not match usermeta.sc.datasetSha256');
  await refused('dataset unrelated to the bundle', (v, b) => { b.calculationRefs = []; b.sourceRefs.forEach((s) => { s.sha256 = 'a'.repeat(64); }); }, 'not one of the bundle sourceRefs');

  // 3b. The renderer refuses a Vega-Lite figure without alt text (accessible description is mandatory).
  globalThis.SCLabVegaLiteFIG02B = V;
  const R = require(path.join(root, 'assets/js/modules/graph-studio-figure-bundle-renderer.js'));
  const noAlt = json('erw.bundle.json');
  noAlt.rendering.altText = '';
  try {
    await R.verifyPackage([{ name: 'b.json', bytes: new Uint8Array(Buffer.from(JSON.stringify(noAlt))) },
      { name: 'v.json', bytes: new Uint8Array(fs.readFileSync(path.join(dir, 'erw.vega-lite.json'))) }], '3.3.1');
    ok(false, 'figure without alt text should be refused');
  } catch (reasons) {
    ok(Array.isArray(reasons) && reasons.some((r) => r.includes('altText')), 'figure without alt text refused: ' + JSON.stringify(reasons));
  }
  const accepted = await R.verifyPackage([{ name: 'b.json', bytes: new Uint8Array(fs.readFileSync(path.join(dir, 'erw.bundle.json'))) },
    { name: 'v.json', bytes: new Uint8Array(fs.readFileSync(path.join(dir, 'erw.vega-lite.json'))) }], '3.3.1', source.files['erw.bundle.json']);
  ok(accepted.views.map((v) => v.state).join() === 'rendered-vega-lite', 'renderer verifies the pinned ERW package as a Vega-Lite view');

  // 4. Display spec adds unit-bearing titles and drops usermeta; the table model carries units, gaps and identity.
  const met = json('metrics.vega-lite.json'), metBundle = json('metrics.bundle.json');
  const shown = V.displaySpec(met, metBundle);
  ok(shown.usermeta === undefined && shown.description === metBundle.rendering.altText, 'display spec drops usermeta and uses the bundle alt text');
  ok(JSON.stringify(shown).includes(' (%)'), 'display spec titles carry the percentage unit');
  const t = V.tableModel(met, metBundle.title);
  ok(t.rows.length === met.data.values.length && t.truncated === 0, 'table model lists every row');
  ok(t.rows.flat().filter((c) => c === 'not reported').length === 3, 'missing values shown as "not reported"');
  ok(/^Uncertainty: none reported\./.test(t.uncertainty) && t.dataset.endsWith(met.usermeta.sc.datasetSha256), 'table model states uncertainty and dataset identity');
  ok(t.columns.includes('Evidence class') || t.columns.some((c) => /evidence/i.test(c)), 'table model includes the evidence class column');

  // 5. Provenance carried into exported SVG metadata (pure part; serialisation is exercised in Chromium).
  const erw = json('erw.vega-lite.json'), erwBundle = json('erw.bundle.json');
  const p = V.provenanceFor(erwBundle, erwBundle.artifacts[0], erw);
  ok(p.schema === 'sc.figure-svg-provenance.v1' && p.figureId === erwBundle.figureId && p.evidenceClass === 'modelled', 'SVG provenance names figure and evidence class');
  ok(p.dataset.sha256 === erw.usermeta.sc.datasetSha256 && p.uncertainty.kind === 'range' && p.fields.cdr.unit === 't CO2 ha-1', 'SVG provenance keeps dataset hash, uncertainty and units');
  ok(p.viewArtifactSha256 === erwBundle.artifacts[0].sha256 && Array.isArray(p.sourceRefs) && p.sourceRefs.length > 0, 'SVG provenance keeps the view hash and source citations');
  ok(!JSON.stringify(p).includes('measured'), 'synthetic modelled provenance never describes itself as measured');

  console.log('PASS - SC-FIG-02B Vega-Lite contract (' + Object.keys(source.files).length + ' fixtures, 20 refusals)');
})().catch((e) => { console.error('FAIL - ' + (e && e.stack || JSON.stringify(e))); process.exit(1); });
