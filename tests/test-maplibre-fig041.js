'use strict';
// SC-FIG-04.1: runtime confidence intervals and declared assumptions on map calculations, the "trend
// uncertainty unavailable" notice, and the static PNG export's embedded receipt and verifier.
// SYNTHETIC Wexford fixture; synthetic interval numbers (the t quantile for df 22 at 95% is 2.0738731).
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const root = path.resolve(__dirname, '..');
globalThis.SCLabPlotlyPreviewFIG02A = require(path.join(root, 'assets/js/modules/graph-studio-plotly-preview-fig02a.js'));
globalThis.SCLabMapLibreFIG03A = require(path.join(root, 'assets/js/modules/graph-studio-maplibre-fig03a.js'));
const M = globalThis.SCLabMapLibreFIG03A;
const R = require(path.join(root, 'assets/js/modules/graph-studio-maplibre-renderer-fig04.js'));
const F = globalThis.SCLabPlotlyPreviewFIG02A;
const dir = path.join(__dirname, 'fixtures/fig04-wexford');
function ok(value, message) { if (!value) { console.error('FAIL - ' + message); process.exit(1); } }
const json = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
let checks = 0;

const HALF = 2.0738731 * 1.8857;
function withInterval(view, bundle) {
  const c = view.calculations[0];
  c.interval = { semantics: 'confidence-interval', level: 0.95, lower: c.value - HALF, upper: c.value + HALF,
    method: 'stats::confint.lm: estimate +/- qt((1 + level) / 2, df.residual) * standard error', distribution: 'Student t',
    degreesOfFreedom: 22, computedBy: 'runtime', consistency: 'estimate-plus-minus-t-standard-error' };
  c.assumptions = { declaredBy: 'model-revision', checked: false, statements: ['Independent, identically distributed errors'] };
  bundle.calculationRefs[0].intervalsSha256 = 'a'.repeat(64);
  bundle.calculationRefs[0].assumptionRefs = ['sha256:' + 'b'.repeat(64)];
}
async function errorsFor(mutate) {
  const view = json('wexford.map-view.json'), bundle = json('wexford.bundle.json');
  mutate(view, bundle);
  // Only the calculations change; the SI objects keep their exact lexical numbers (their digests depend on them).
  const raw = fs.readFileSync(path.join(dir, 'wexford.map-view.json'), 'utf8');
  const spliced = raw.replace(/"calculations": \[[\s\S]*\]\s*\}\s*$/, '"calculations": ' + JSON.stringify(view.calculations) + '\n}\n');
  ok(spliced !== raw || !view.calculations, 'calculations spliced');
  const text = F.canonical(F.parseLexical(spliced));
  bundle.artifacts[0].sha256 = bundle.rendering.visualizationSpecSha256 = await F.sha256Hex(text);
  return { reasons: await M.viewErrors(text, JSON.parse(text), bundle), view, bundle };
}
async function refused(label, mutate, needle) {
  const { reasons } = await errorsFor((v, b) => { withInterval(v, b); mutate(v, b); });
  ok(reasons.some((r) => r.includes(needle)), label + ' refused with "' + needle + '": ' + JSON.stringify(reasons));
  checks++;
}

// A tiny valid PNG (2x1 RGBA), built here so the chunk code is tested against real zlib output.
function crc(buf) { return R._png.crc32(buf); }
function chunk(type, data) {
  const b = Buffer.alloc(12 + data.length);
  b.writeUInt32BE(data.length, 0); b.write(type, 4, 'latin1'); data.copy(b, 8);
  b.writeUInt32BE(crc(b.subarray(4, 8 + data.length)), 8 + data.length);
  return b;
}
function tinyPng() {
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(2, 0); ihdr.writeUInt32BE(1, 4); ihdr[8] = 8; ihdr[9] = 6;
  const raw = Buffer.from([0, 255, 0, 0, 255, 0, 0, 255, 255]);
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}
async function sha(bytes) { return Buffer.from(await crypto.subtle.digest('SHA-256', bytes)).toString('hex'); }

(async () => {
  // 1. A runtime interval with declared assumptions is accepted when the calculationRef binds both.
  const good = await errorsFor(withInterval);
  ok(good.reasons.length === 0, 'interval + assumptions accepted: ' + JSON.stringify(good.reasons)); checks++;

  // 2. Refusals: never derived, never inconsistent, always bound.
  await refused('interval computed outside the runtime', (v) => { v.calculations[0].interval.computedBy = 'lab'; }, 'runtime confidence-interval record');
  await refused('interval that does not contain the value', (v) => { v.calculations[0].interval.lower = 1.0; }, 'runtime confidence-interval record');
  await refused('credible interval', (v) => { v.calculations[0].interval.semantics = 'credible-interval'; }, 'runtime confidence-interval record');
  await refused('level of 1', (v) => { v.calculations[0].interval.level = 1; }, 'runtime confidence-interval record');
  await refused('extra interval key', (v) => { v.calculations[0].interval.halfWidth = 3; }, 'runtime confidence-interval record');
  await refused('checked against an absent standard error', (v) => { delete v.calculations[0].uncertainty; delete v.calculations[0].uncertaintyKind; }, 'does not report');
  await refused('interval not bound by the calculationRef', (v, b) => { delete b.calculationRefs[0].intervalsSha256; }, 'intervalsSha256');
  await refused('assumptions marked as tested', (v) => { v.calculations[0].assumptions.checked = true; }, 'declared, unchecked');
  await refused('assumptions not bound', (v, b) => { b.calculationRefs[0].assumptionRefs = []; }, 'assumptionRefs');
  await refused('unknown calculation key', (v) => { v.calculations[0].trendStdError = 1; }, 'trendStdError is not allowed');

  // 3. Display text: what was reported, and "unavailable" when nothing was.
  const ref = good.bundle.calculationRefs[0];
  const lines = R.calculationLines(good.view.calculations[0], ref);
  ok(/95% confidence interval -3\.077 to 4\.744 g kg-1 yr-1/.test(lines[1]) && /Student t, df 22/.test(lines[1]) && /not an independent reproduction/.test(lines[1]), 'interval line: ' + lines[1]); checks++;
  ok(lines.some((t) => /^Assumptions declared by the model, not tested: Independent/.test(t)), 'assumptions shown as declared, not tested'); checks++;
  const bare = { label: 'Trend', value: 0.8333, unit: 'g kg-1 yr-1', method: 'lm', calculationRef: 0 };
  ok(R.calculationLines(bare, ref).some((t) => t.startsWith('Trend uncertainty unavailable')), 'no reported uncertainty -> unavailable notice'); checks++;
  ok(!R.calculationLines(bare, ref).some((t) => /±|interval \d/.test(t)), 'nothing is invented for a bare value'); checks++;
  const seOnly = Object.assign({}, bare, { uncertainty: 1.8857, uncertaintyKind: 'standard-error' });
  ok(R.calculationLines(seOnly, ref).includes('No confidence interval was reported by the run.') &&
     !R.calculationLines(seOnly, ref).some((t) => t.startsWith('Trend uncertainty unavailable')), 'standard error only: no interval derived'); checks++;

  // 4. PNG receipt embedding and verification (no network; crypto.subtle only).
  const bundle = good.bundle, spec = good.view;
  const receipt = { schema: R.exportSchema, figure: { figureId: bundle.figureId, version: bundle.version }, view: { sha256: bundle.artifacts[0].sha256 },
    sources: bundle.sourceRefs.map((s) => ({ sourceId: s.sourceId, sha256: s.sha256 || null })),
    calculations: bundle.calculationRefs.map((c) => ({ outputSha256: c.outputSha256 })),
    state: { timeStep: M.timeSteps(spec).slice(-1)[0], comparison: null, visibleLayers: spec.layers.map((l) => l.id) }, image: { width: 2, height: 1 } };
  const base = tinyPng();
  ok(R._png.chunks(base) && R._png.chunks(base).length === 3, 'synthetic PNG parses'); checks++;
  const png = R._png.withTextChunk(base, R.exportKeyword, R._png.canonical(receipt));
  const digest = await sha(png);
  const file = { schema: 'sc-lab-static-map-export-receipt/1.0', receipt, png: { fileName: 'x.png', sha256: digest, bytes: png.length } };
  const expected = { spec, bundle };
  let v = await R.verifyExport(png, file, expected);
  ok(v.ok && v.sha256 === digest, 'exported PNG verifies: ' + JSON.stringify(v.errors)); checks++;
  ok(zlib.inflateSync(Buffer.from(R._png.chunks(png)[1].data)).length === 9, 'image data unchanged by the receipt chunk'); checks++;

  const flip = Buffer.from(png); flip[flip.length - 20] ^= 1;
  v = await R.verifyExport(flip, file, expected);
  ok(!v.ok && v.errors.some((e) => /CRC|well-formed/.test(e)), 'flipped byte refused: ' + JSON.stringify(v.errors)); checks++;

  const forged = Object.assign({}, receipt, { view: { sha256: 'c'.repeat(64) } });
  const forgedPng = R._png.withTextChunk(base, R.exportKeyword, R._png.canonical(forged));
  v = await R.verifyExport(forgedPng, { receipt: forged, png: { sha256: await sha(forgedPng), bytes: forgedPng.length } }, expected);
  ok(!v.ok && v.errors.includes('receipt names a different view'), 'consistent but forged receipt refused against the verified bundle'); checks++;
  v = await R.verifyExport(forgedPng, file, expected);
  ok(!v.ok && v.errors.includes('PNG SHA-256 differs from the receipt') && v.errors.includes('embedded receipt differs from the receipt file'), 'swapped PNG refused'); checks++;

  const twice = R._png.withTextChunk(png, R.exportKeyword, R._png.canonical(receipt));
  v = await R.verifyExport(twice, null, expected);
  ok(!v.ok && v.errors.includes('PNG must carry exactly one embedded receipt'), 'duplicate receipt refused'); checks++;
  v = await R.verifyExport(base, null, expected);
  ok(!v.ok && v.errors.includes('PNG must carry exactly one embedded receipt'), 'PNG without receipt refused'); checks++;
  v = await R.verifyExport(Buffer.concat([png, Buffer.from([0])]), null, expected);
  ok(!v.ok && v.errors.some((e) => /well-formed/.test(e)), 'trailing bytes after IEND refused'); checks++;
  const badLayer = Object.assign({}, receipt, { state: Object.assign({}, receipt.state, { visibleLayers: ['eo-sentinel'] }) });
  v = await R.verifyExport(R._png.withTextChunk(base, R.exportKeyword, R._png.canonical(badLayer)), null, expected);
  ok(!v.ok && v.errors.includes('receipt lists layers the view does not have'), 'unknown layer in receipt refused'); checks++;
  const badSize = Object.assign({}, receipt, { image: { width: 1200, height: 900 } });
  v = await R.verifyExport(R._png.withTextChunk(base, R.exportKeyword, R._png.canonical(badSize)), null, expected);
  ok(!v.ok && v.errors.includes('image size differs from the receipt'), 'receipt for a different image size refused'); checks++;
  let threw = false;
  try { R._png.withTextChunk(base, R.exportKeyword, 'non-ascii é'); } catch (e) { threw = true; }
  ok(threw, 'non-ASCII receipt text is not embedded'); checks++;

  // 5. Scoped CSS: every selector in the FIG-04 stylesheet is under .sc-lab-fig04-, so theme and core forms are untouched.
  const css = fs.readFileSync(path.join(root, 'assets/css/sc-lab-graph-studio-maplibre-fig04.css'), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
  const selectors = [];
  css.replace(/([^{}@]+)\{[^{}]*\}/g, (m, sel) => { sel.split(',').forEach((x) => selectors.push(x.trim())); return m; });
  const loose = selectors.filter((x) => x && !x.startsWith('.sc-lab-fig04-'));
  ok(selectors.length > 20 && loose.length === 0, 'every FIG-04 selector is scoped: ' + JSON.stringify(loose)); checks++;
  ok(/\.sc-lab-fig04-controls input\[type="checkbox"\][^{]*\{[^}]*width: 1\.125rem/.test(css) && /min-height: 2\.75rem/.test(css) && /:focus-visible/.test(css), 'checkbox size, 44px targets and focus-visible present'); checks++;

  console.log('PASS - SC-FIG-04.1 intervals, unavailable notice, PNG receipt and scoped CSS (' + checks + ' checks)');
})().catch((e) => { console.error('FAIL - ' + (e && e.stack || e)); process.exit(1); });
