'use strict';
// SC-FIG-05.3: Lab draws an interval ribbon, ensemble fan or map uncertainty layer only from a runtime record it
// was given and verified; otherwise it refuses, or shows uncertainty as unavailable. SYNTHETIC fixtures produced
// by the real pipeline (tests/fixtures/fig05-uncertainty/build_fixtures.py).
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
globalThis.SCLabPlotlyPreviewFIG02A = require(path.join(root, 'assets/js/modules/graph-studio-plotly-preview-fig02a.js'));
globalThis.SCLabMapLibreFIG03A = require(path.join(root, 'assets/js/modules/graph-studio-maplibre-fig03a.js'));
const F = globalThis.SCLabPlotlyPreviewFIG02A;
const M = globalThis.SCLabMapLibreFIG03A;
const B = require(path.join(root, 'assets/js/modules/graph-studio-figure-bundle-renderer.js'));
const dir = path.join(__dirname, 'fixtures/fig05-uncertainty');
const read = (n) => fs.readFileSync(path.join(dir, n), 'utf8');
const json = (n) => JSON.parse(read(n));
let checks = 0;
function ok(value, message) { if (!value) { console.error('FAIL - ' + message); process.exit(1); } checks++; }
const file = (name, text) => ({ name, bytes: new TextEncoder().encode(text) });
async function rejects(p) { try { await p; return null; } catch (e) { return Array.isArray(e) ? e : [String(e)]; } }

// Type-7 quantile, written here independently of the Workspace runtime.
function q7(sorted, p) { const i = (sorted.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return lo === hi ? sorted[lo] : sorted[lo] * (hi - i) + sorted[hi] * (i - lo); }

(async function () {
  // --- 1. Compile-response preview -------------------------------------------------------------------------------
  const chartText = read('chart.compile.json');
  const v = await F.verify(chartText, '3.3.1');
  ok(v.response.uncertainty.length === 2, 'chart compile response verifies with two runtime records');
  const fills = v.response.plotly.figure.data.filter((t) => t.fill);
  ok(fills.length === 5 && fills.every((t) => t.meta.scUncertainty.recordSha256), 'five filled areas, each tied to a record hash');

  // Independent recomputation of the fan from the ensemble inputs.
  const src = json('SOURCE.json');
  const members = src.inputs.ensemble.members.map((m) => m.values);
  const steps = src.inputs.ensemble.steps;
  for (const t of fills.filter((t) => t.meta.scUncertainty.role === 'fan')) {
    const lv = t.meta.scUncertainty.level, n = steps.length;
    for (let j = 0; j < n; j++) {
      const col = members.map((m) => m[j]).sort((a, b) => a - b);
      const lower = t.y[2 * n - 1 - j], upper = t.y[j];
      if (Math.abs(lower - q7(col, (1 - lv) / 2)) > 1e-9 || Math.abs(upper - q7(col, (1 + lv) / 2)) > 1e-9) { ok(false, 'fan quantile mismatch at step ' + j + ' level ' + lv); }
    }
  }
  ok(true, 'every drawn fan bound equals an independent type-7 quantile of the synthetic ensemble');
  // Bands are symmetric Student-t intervals around the fit: check the drawn ribbons against the fit line.
  const fit = v.response.plotly.figure.data.find((t) => t.meta && t.meta.scUncertainty && t.meta.scUncertainty.role === 'fit');
  for (const t of fills.filter((t) => t.meta.scUncertainty.role === 'band')) {
    const n = fit.x.length;
    for (let j = 0; j < n; j++) {
      const hi = t.y[j], lo = t.y[2 * n - 1 - j];
      if (Math.abs((hi + lo) / 2 - fit.y[j]) > 1e-9) { ok(false, 'band not centred on the fit at ' + j); }
    }
  }
  ok(true, 'every drawn band is centred on the runtime fit');

  // Tampering with the drawn areas, their binding or the bundle status (records as verify() hashed them).
  const base = JSON.parse(chartText);
  const recs = base.uncertainty.map((u) => ({ sha256: u.recordSha256, value: u.record }));
  ok(F.uncertaintyErrors(base.plotly.figure, base.figureBundle, recs).length === 0, 'untampered areas equal their records');
  function areaRefused(label, mutate, needle, records) {
    const r = JSON.parse(chartText);
    mutate(r);
    const e = F.uncertaintyErrors(r.plotly.figure, r.figureBundle, records || recs);
    ok(e.some((x) => x.includes(needle)), label + ' refused with "' + needle + '": ' + JSON.stringify(e));
  }
  const band0 = (r) => r.plotly.figure.data.find((t) => t.meta && t.meta.scUncertainty && t.meta.scUncertainty.role === 'band');
  areaRefused('widened ribbon', (r) => { band0(r).y[0] += 0.5; }, 'does not equal the runtime record');
  areaRefused('fan level relabelled', (r) => { r.plotly.figure.data.find((t) => t.meta && t.meta.scUncertainty.role === 'fan').meta.scUncertainty.level = 0.99; }, 'does not equal the runtime record');
  areaRefused('record not supplied', () => {}, 'was not supplied', recs.slice(1));
  areaRefused('area without a record', (r) => { delete band0(r).meta; }, 'is not a runtime uncertainty record');
  areaRefused('fill on an ordinary line', (r) => { r.plotly.figure.data.find((x) => x.meta && x.meta.scUncertainty.role === 'fit').fill = 'tozeroy'; }, 'is not a runtime uncertainty record');
  areaRefused('fillcolor without fill', (r) => { r.plotly.figure.data.find((x) => x.meta && x.meta.scUncertainty.role === 'fit').fillcolor = '#0072b2'; }, 'is not a runtime uncertainty record');
  areaRefused('record not bound by the bundle', (r) => { r.figureBundle.calculationRefs[0].bandsSha256 = 'f'.repeat(64); }, 'not bound to a bundle calculationRef');
  areaRefused('bundle says unavailable', (r) => { r.figureBundle.scientificContext.uncertaintyStatus = 'unavailable'; }, 'bundle says uncertainty is unavailable');

  // A record edited in the response text, with spec and result hashes recomputed (they are unsigned): refused.
  const at = chartText.indexOf('"record"');
  const numAt = chartText.slice(at).search(/\d\.\d{6}/) + at;
  let forged = chartText.slice(0, numAt) + String((+chartText[numAt] + 1) % 10) + chartText.slice(numAt + 1);
  const tree = F.parseLexical(forged);
  const without = { t: 'o', v: tree.v.filter((kv) => kv[0] !== 'staticExport' && kv[0] !== 'resultHash') };
  forged = forged.replace(/"resultHash": "[0-9a-f]{64}"/, '"resultHash": "' + await F.sha256Hex(F.canonical(without)) + '"');
  const fe = await rejects(F.verify(forged, '3.3.1'));
  ok(fe && fe.some((e) => e.includes('does not match its recordSha256')), 'edited record in the response refused: ' + JSON.stringify(fe));

  const na = await F.verify(read('chart-unavailable.compile.json'), '3.3.1');
  ok(!na.response.plotly.figure.data.some((t) => t.fill) && na.response.uncertainty.every((u) => u.status === 'unavailable'), 'unavailable response draws no area');
  ok(na.response.plotly.figure.layout.annotations.filter((a) => /^Uncertainty unavailable/.test(a.text)).length === 2, 'both panels say uncertainty is unavailable');

  // --- 2. Bundle-path package (what Research releases) -----------------------------------------------------------
  const pkg = ['chart.bundle.json', 'chart.figure.json', 'chart.trend.bands.json', 'chart.ensemble.fan.json'].map((n) => file(n, read(n)));
  const good = await B.verifyPackage(pkg, '3.3.1');
  ok(good.views.length === 1 && good.views[0].state === 'rendered-plotly', 'bundle + figure + two runtime records verify and render');
  let errs = await rejects(B.verifyPackage(pkg.slice(0, 3), '3.3.1'));
  ok(errs && errs.some((e) => e.includes('was not supplied, so nothing is drawn')), 'fan record missing: refused, nothing drawn: ' + JSON.stringify(errs));
  const edited = JSON.parse(read('chart.trend.bands.json')); edited[0].points[1][2] -= 0.25; edited[0].points[1][3] += 0.25;
  errs = await rejects(B.verifyPackage([pkg[0], pkg[1], file('chart.trend.bands.json', JSON.stringify(edited)), pkg[3]], '3.3.1'));
  ok(errs && errs.some((e) => /not referenced by the figure bundle|was not supplied/.test(e)), 'edited band record: not the bound record, refused');
  const reordered = read('chart.trend.bands.json').replace(/\n /g, '\n    '); // whitespace only: number spellings kept
  ok((await B.verifyPackage([pkg[0], pkg[1], file('b.json', reordered), pkg[3]], '3.3.1')).views[0].state === 'rendered-plotly', 're-indented record file still verifies (canonical hash)');

  // --- 3. Map uncertainty layer ------------------------------------------------------------------------------------
  const viewText = read('map.view.json'), view = JSON.parse(viewText), mb = json('map.bundle.json');
  ok((await M.viewErrors(viewText, view, mb)).length === 0, 'map view with uncertainty layer verifies: ' + JSON.stringify(await M.viewErrors(viewText, view, mb)));
  const style = M.compileStyle(view);
  const ul = style.layers.find((l) => l.id === 'soc-uncertainty');
  ok(JSON.stringify(ul.paint['fill-color']).includes('"soc_sd"') && !JSON.stringify(ul.paint['fill-color']).includes('"soc"'), 'uncertainty layer is coloured by soc_sd');
  const legend = M.legendModel(view).find((g) => g.layer === 'soc-uncertainty');
  ok(legend.encode === 'uncertainty' && legend.field === 'Soil organic carbon ± standard deviation (g kg-1)', 'legend names the uncertainty kind and unit: ' + legend.field);
  ok(legend.classes[legend.classes.length - 1].label === 'uncertainty not reported (none drawn or imputed)' && /1 object\(s\) have no reported uncertainty/.test(legend.note), 'legend reports the field with no runtime uncertainty');
  ok(M.isRampRun(['#00224e', '#414d6b', '#7c7b78', '#bcaf6f']) && !M.isRampRun(['#d73027', '#4575b4']) && !M.isRampRun(['#414d6b', '#00224e']), 'only ordered runs of a CVD-safe sequential ramp are accepted');
  const table = M.tableModel(view, 'c');
  ok(table.columns.includes('Soil organic carbon ± standard deviation (g kg-1)') && table.rows.some((r) => r.includes('not reported')), 'table lists uncertainty and "not reported"');
  async function mapRefused(label, mutate, needle) {
    const v2 = JSON.parse(viewText), b2 = JSON.parse(JSON.stringify(mb));
    mutate(v2, b2);
    const e = M.specErrors(v2, b2);
    ok(e.some((x) => x.includes(needle)), label + ' refused with "' + needle + '": ' + JSON.stringify(e));
  }
  await mapRefused('diverging colours', (v2) => { v2.layers[1].classify.colors = ['#d73027', '#fc8d59', '#91bfdb', '#4575b4']; }, 'ordered run');
  await mapRefused('unbound uncertainty layer', (v2, b2) => { delete b2.calculationRefs[0].uncertaintySha256; }, 'bound to a Workspace run');
  await mapRefused('no declared uncertainty', (v2) => { delete v2.fields.soc.uncertainty; delete v2.fields.soc.uncertaintyKind; }, 'declares no uncertainty');
  await mapRefused('unknown encoding', (v2) => { v2.layers[1].encode = 'value-and-uncertainty'; }, 'needs encode "uncertainty"');
  await mapRefused('negative uncertainty', (v2) => { v2.objects[0].properties.soc_sd = -1; }, 'non-negative');
  // The released package: bundle, view and the runtime's own per-field record (uncertaintySha256).
  globalThis.SCLabMapLibreFIG04 = require(path.join(root, 'assets/js/modules/graph-studio-maplibre-renderer-fig04.js'));
  const recText = read('map.uncertainty.json');
  const mpkg = [file('map.bundle.json', JSON.stringify(mb)), file('map.view.json', viewText), file('map.uncertainty.json', recText)];
  ok((await B.verifyPackage(mpkg)).views[0].state === 'rendered-maplibre', 'map package with its runtime uncertainty record verifies');
  errs = await rejects(B.verifyPackage(mpkg.slice(0, 2)));
  ok(errs && errs.some((e) => e.includes('runtime uncertainty record was not supplied')), 'map without its uncertainty record: refused: ' + JSON.stringify(errs));
  const rec2 = JSON.parse(recText); rec2.values['WX-F2'] += 0.01;
  errs = await rejects(B.verifyPackage([mpkg[0], mpkg[1], file('u.json', JSON.stringify(rec2))]));
  ok(errs && errs.some((e) => /not referenced by the figure bundle|was not supplied/.test(e)), 'edited uncertainty record: not the bound record, refused');

  // --- 4. Colour-vision safety (measured) ---------------------------------------------------------------------
  // Composite the nested areas over white as Plotly does (source-over), simulate protanopia, deuteranopia and
  // tritanopia (Machado, Oliveira and Fernandes 2009, severity 1.0, linear RGB) and require CIE L* to fall
  // monotonically towards the centre with at least 3 L* units between adjacent regions, in every simulation.
  const MACHADO = {
    none: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    protan: [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    deutan: [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    tritan: [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
  };
  const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  function lstar(rgb255, sim) {
    const l = rgb255.map(lin), m = MACHADO[sim];
    const s2 = m.map((row) => Math.min(1, Math.max(0, row[0] * l[0] + row[1] * l[1] + row[2] * l[2])));
    const Y = 0.2126 * s2[0] + 0.7152 * s2[1] + 0.0722 * s2[2];
    return Y > 0.008856 ? 116 * Math.cbrt(Y) - 16 : 903.3 * Y;
  }
  function over(dst, rgba) { return dst.map((d, k) => rgba[3] * rgba[k] + (1 - rgba[3]) * d); }
  const parse = (c) => c.match(/[\d.]+/g).map(Number);
  function nestedLstars(areaTraces, sim) {
    let px = [255, 255, 255];
    const out = [lstar(px, sim)];
    areaTraces.forEach((t) => { px = over(px, parse(t.fillcolor)); out.push(lstar(px.map(Math.round), sim)); });
    return out;
  }
  for (const [label, areas] of [['band', fills.filter((t) => t.meta.scUncertainty.role === 'band')], ['fan', fills.filter((t) => t.meta.scUncertainty.role === 'fan')]]) {
    for (const sim of Object.keys(MACHADO)) {
      const L = nestedLstars(areas, sim);
      const steps = L.slice(1).map((x, k) => L[k] - x);
      ok(steps.every((d) => d >= 3), label + ' regions distinguishable by lightness under ' + sim + ': L* ' + L.map((x) => x.toFixed(1)).join(' > '));
    }
  }
  const ramp = view.layers[1].classify.colors.map((h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16)));
  for (const sim of Object.keys(MACHADO)) {
    const L = ramp.map((c) => lstar(c, sim));
    ok(L.slice(1).every((x, k) => x - L[k] >= 3), 'uncertainty ramp lightness increases class by class under ' + sim + ': ' + L.map((x) => x.toFixed(1)).join(' < '));
  }

  // "Not reported" must never read as a ramp class (unknown is not the same as large uncertainty): CIE76 colour
  // difference of at least 10 against every drawn class, under every simulation.
  function lab(rgb255, sim) {
    const l = rgb255.map(lin), m = MACHADO[sim];
    const r = m.map((row) => Math.min(1, Math.max(0, row[0] * l[0] + row[1] * l[1] + row[2] * l[2])));
    const g = (t) => (t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116);
    const X = (0.4124 * r[0] + 0.3576 * r[1] + 0.1805 * r[2]) / 0.95047, Y = 0.2126 * r[0] + 0.7152 * r[1] + 0.0722 * r[2];
    const Z = (0.0193 * r[0] + 0.1192 * r[1] + 0.9505 * r[2]) / 1.08883;
    return [116 * g(Y) - 16, 500 * (g(X) - g(Y)), 200 * (g(Y) - g(Z))];
  }
  const nrHex = legend.classes[legend.classes.length - 1].color;
  const nr = [1, 3, 5].map((i) => parseInt(nrHex.slice(i, i + 2), 16));
  for (const sim of Object.keys(MACHADO)) {
    const dE = ramp.map((c) => { const a = lab(c, sim), b = lab(nr, sim); return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]); });
    ok(dE.every((d) => d >= 10), '"not reported" ' + nrHex + ' distinct from every uncertainty class under ' + sim + ': min CIE76 ' + Math.min(...dE).toFixed(1));
  }

  console.log('SC-FIG-05.3 Lab uncertainty: ' + checks + ' checks passed');
})().catch((e) => { console.error('FAIL - ' + (e && e.stack || JSON.stringify(e))); process.exit(1); });
