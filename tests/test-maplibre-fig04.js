'use strict';
// SC-FIG-04: map view 1.1 (graduated classes, heat maps, time steps, uncertainty, comparison, calculations)
// and the Earth-observation gate, on SYNTHETIC Wexford evidence produced by Site Intelligence's normaliser.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
globalThis.SCLabPlotlyPreviewFIG02A = require(path.join(root, 'assets/js/modules/graph-studio-plotly-preview-fig02a.js'));
const M = require(path.join(root, 'assets/js/modules/graph-studio-maplibre-fig03a.js'));
const dir = path.join(__dirname, 'fixtures/fig04-wexford');
function ok(value, message) { if (!value) { console.error('FAIL - ' + message); process.exit(1); } }
const viewText = fs.readFileSync(path.join(dir, 'wexford.map-view.json'), 'utf8');
const json = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
let refusals = 0;

async function refused(label, mutate, needle) {
  const view = JSON.parse(viewText), bundle = json('wexford.bundle.json');
  mutate(view, bundle);
  const reasons = await M.viewErrors(JSON.stringify(view), view, bundle);
  ok(reasons.some((r) => r.includes(needle)), label + ' refused with "' + needle + '": ' + JSON.stringify(reasons));
  refusals++;
}

(async () => {
  const source = json('SOURCE.json');
  for (const [file, sha] of Object.entries(source.files)) {
    ok(crypto.createHash('sha256').update(fs.readFileSync(path.join(dir, file))).digest('hex') === sha, file + ' matches SOURCE.json');
  }
  ok(source.synthetic === true && /^[0-9a-f]{40}$/.test(source.siteIntelligenceCommit), 'fixtures are synthetic and record the SI commit');

  // 1. Accepted, with every SI digest recomputed; the view hash is the bundle's artifact hash.
  const view = JSON.parse(viewText), bundle = json('wexford.bundle.json'), pkg = json('wexford.si-package.json');
  ok((await M.viewErrors(viewText, view, bundle)).length === 0, 'synthetic Wexford 1.1 view accepted: ' + JSON.stringify(await M.viewErrors(viewText, view, bundle)));
  const F = globalThis.SCLabPlotlyPreviewFIG02A;
  ok((await F.sha256Hex(F.canonical(F.parseLexical(viewText)))) === bundle.artifacts[0].sha256, 'view canonical hash matches the bundle artifact');
  const digests = pkg.components.evidence_objects.map((o) => o.content_digest).sort();
  ok(JSON.stringify(view.objects.map((o) => o.content_digest).sort()) === JSON.stringify(digests), 'view objects are exactly the sealed SI package objects');
  ok(bundle.spatial.siPackage.package_digest === pkg.package_digest, 'bundle pins the SI package digest');

  // 2. Time steps and per-step filtering.
  const steps = M.timeSteps(view);
  ok(steps.length === 4 && steps[3] === view.time.initial, 'four quarterly steps, initial is the latest');
  const style = M.compileStyle(view);
  const feats = style.sources['sc-evidence'].data.features;
  ok(feats.length === 56 && feats.every((f) => f.properties.sc_time === view.objects.find((o) => o.object_id === f.id).observed_at), 'every feature carries its SI observed_at as sc_time');
  ok(style.layers.filter((l) => l.filter).every((l) => JSON.stringify(l.filter).includes(JSON.stringify(['==', ['get', 'sc_time'], steps[3]]))), 'every data layer starts on the initial step');
  const early = M.compileStyle(view, steps[0]);
  ok(JSON.stringify(early.layers[1].filter).includes(steps[0]), 'compiling for another step filters to it');
  ok(!/https?:|\{z\}|tiles|url|glyphs|sprite/i.test(JSON.stringify(style)), 'style references no URL, tiles, glyphs or sprite');

  // 3. Graduated classes and heat map compiled from constants.
  const fill = style.layers.find((l) => l.id === 'field-soc');
  ok(JSON.stringify(fill.paint['fill-color']) === JSON.stringify(['case', ['==', ['typeof', ['get', 'soc']], 'number'],
    ['step', ['to-number', ['get', 'soc']], '#edf8e9', 26, '#bae4b3', 29, '#74c476', 32, '#238b45'], '#bdbdbd']), 'graduated SOC classes with a not-reported colour');
  const heat = style.layers.find((l) => l.id === 'nitrate-heat');
  ok(heat.type === 'heatmap' && JSON.stringify(heat.filter).includes('"Point","MultiPoint"') && heat.paint['heatmap-radius'] === 40, 'heat map over points only');
  ok(JSON.stringify(heat.paint['heatmap-weight']) === JSON.stringify(['interpolate', ['linear'], ['to-number', ['get', 'nitrate_n'], 0], 0, 0, 15, 1]), 'heat-map weight scaled 0..max on the declared field');
  ok(M.styleLayerIds(view.layers[0]).join() === 'field-soc,field-soc-outline' && M.styleLayerIds(view.layers[1]).join() === 'nitrate-heat', 'style layer ids per view layer');

  // 4. Scientific legend.
  const legend = M.legendModel(view);
  ok(legend.length === 3 && legend[0].field === 'Soil organic carbon (g kg-1)', 'legend names the classified field with its unit');
  ok(legend[0].classes.map((c) => c.label).join('|') === '< 26 g kg-1|26 to < 29 g kg-1|29 to < 32 g kg-1|≥ 32 g kg-1|not reported', 'legend class bounds with units and not reported');
  ok(legend[1].ramp[0] === '#fcfdbf' && legend[1].ramp[4] === '#000004' && JSON.stringify(heat.paint['heatmap-color']).includes('"heatmap-density"],0,"rgba(0,0,0,0)",0.2,"#fcfdbf"'), 'heat ramp runs light (low) to dark (high), same order in legend and style');
  ok(legend[1].ramp.length === 5 && /not interpolated values/.test(legend[1].note) && legend[1].field === 'Nitrate-N (mg L-1)', 'heat-map legend explains what the density means');
  ok(legend.every((g) => g.evidenceClass === 'modelled'), 'legend states each layer\'s evidence class');

  // 5. Accessible table with uncertainty, and the comparison with propagated uncertainty.
  const t = M.tableModel(view, bundle.title);
  ok(t.rows.length === 56 && t.columns.includes('Soil organic carbon ± standard error (g kg-1)') && t.columns.includes('Soil pH'), 'table has uncertainty columns next to their fields');
  const phCol = t.columns.indexOf('Soil pH');
  ok(t.rows.filter((r) => r[phCol] === 'not reported').length === 1 + 32, 'missing pH (one field) and point rows read "not reported"');
  const cmp = M.comparisonModel(view);
  ok(cmp.rows.length === 6 && cmp.unmatched === 0 && cmp.columns.length === 5, 'comparison matches all six fields');
  const f1a = view.objects.find((o) => o.observed_at === steps[0] && o.properties.field_id === 'WX-F1').properties;
  const f1b = view.objects.find((o) => o.observed_at === steps[3] && o.properties.field_id === 'WX-F1').properties;
  const r1 = cmp.rows.find((r) => r[0] === 'WX-F1');
  ok(Math.abs(Number(r1[3]) - (f1b.soc - f1a.soc)) < 1e-9 && Math.abs(Number(r1[4]) - Math.hypot(f1a.soc_se, f1b.soc_se)) < 1e-6, 'change and root-sum-square uncertainty computed per field');
  ok(/independence assumed/.test(cmp.columns[4]), 'propagation assumption is stated in the column');

  // 6. Earth-observation gate: nothing approved; candidates named; a test-only registry shows what passes.
  ok(M.approvedProviders().length === 0 && Object.keys(M.eoCandidates()).length === 3, 'no EO provider approved; three candidates described');
  ok(Object.values(M.eoCandidates()).every((c) => c.status === 'candidate-not-approved'), 'every candidate is not approved');
  const s2 = { id: 's2-ndvi', provider: 'copernicus-sentinel-2-l2a', tiles: ['https://tiles.example.test/s2/{z}/{x}/{y}.png'],
    attribution: 'Contains modified Copernicus Sentinel data 2026',
    provenance: { productId: 'S2X_SYNTHETIC', acquiredAt: '2026-06-01T11:00:00Z', processingBaseline: 'N0000', tileManifestSha256: 'a'.repeat(64) } };
  ok(M.eoLayerErrors(s2, bundle).some((r) => /is not approved .*candidate.*no imagery is fetched/.test(r)), 'Sentinel-2 refused while unapproved');
  const testReg = { 'copernicus-sentinel-2-l2a': { hosts: ['tiles.example.test'], attribution: 'Contains modified Copernicus Sentinel data' } };
  const eoBundle = JSON.parse(JSON.stringify(bundle));
  eoBundle.sourceRefs.push({ sourceId: 'copernicus-sentinel-2-l2a', licenceStatus: 'verified-for-use' });
  ok(M.eoLayerErrors(s2, eoBundle, testReg).length === 0, 'with a test-only approved registry and verified licence, the layer passes');
  ok(M.eoLayerErrors(Object.assign({}, s2, { tiles: ['https://evil.example.test/{z}/{x}/{y}.png'] }), eoBundle, testReg).some((r) => /approved hosts/.test(r)), 'unapproved host refused');
  ok(M.eoLayerErrors(Object.assign({}, s2, { provenance: {} }), eoBundle, testReg).length >= 4, 'missing product provenance refused');
  ok(M.eoLayerErrors(s2, bundle, testReg).some((r) => /licence is not verified-for-use/.test(r)), 'uncited licence refused');

  // 7. Refusals.
  await refused('Sentinel layer in a view', (v) => { v.rasterLayers = [s2]; }, 'is not approved');
  await refused('expression as a class colour', (v) => { v.layers[0].classify.colors[1] = ['get', 'x']; }, 'classify.colors must be');
  await refused('descending breaks', (v) => { v.layers[0].classify.breaks = [29, 26, 32]; }, 'ascending numbers');
  await refused('classify on an undeclared field', (v) => { v.layers[0].classify.field = 'yield'; }, 'is not a declared field');
  await refused('classify on a text field', (v) => { v.layers[0].classify.field = 'field_id'; }, 'must be numeric');
  await refused('heat map without a ramp', (v) => { v.layers[1].ramp = 'rainbow'; }, 'ramp must be one of');
  await refused('heat map weight with no max', (v) => { delete v.layers[1].weight.max; }, 'positive max');
  await refused('heat map radius out of range', (v) => { v.layers[1].style.radius = 500; }, 'bounded number');
  await refused('heatmap in a 1.0 view', (v) => { v.schema = 'sc-lab-maplibre-view/1.0'; ['time', 'comparison', 'calculations'].forEach((k) => delete v[k]); }, 'needs an id and geometry');
  await refused('time steps invented', (v) => { v.time.steps = v.time.steps.slice(0, 3).concat(['2027-01-01T00:00:00+00:00']); }, 'distinct observed_at values');
  await refused('time initial outside steps', (v) => { v.time.initial = '2030-01-01T00:00:00+00:00'; }, 'time.initial');
  await refused('comparison reversed', (v) => { const f = v.comparison.from; v.comparison.from = v.comparison.to; v.comparison.to = f; }, 'earlier first');
  await refused('uncertainty without a kind', (v) => { delete v.fields.soc.uncertaintyKind; }, 'needs a property name and a kind');
  await refused('calculation with no bundle ref', (v) => { v.calculations[0].calculationRef = 3; }, 'calculationRef with an output hash');
  await refused('calculation without a unit', (v) => { v.calculations[0].unit = ''; }, 'needs label, numeric value, unit and method');
  await refused('source licence restricted', (v, b) => { b.sourceRefs[1].licenceStatus = 'restricted'; }, 'not verified-for-use');
  await refused('observed promoted', (v) => { v.objects[0].properties.evidence_class = 'observed'; }, 'no promotion to observed');
  await refused('value edited after SI sealed it', (v) => { v.objects[5].properties.soc = 99; }, 'does not match its Site Intelligence digest');
  await refused('URL smuggled into a calculation', (v) => { v.calculations[0].method = 'see https://x.test'; }, 'contains a URL');
  await refused('object outside the bundle bbox', (v, b) => { b.spatial.bbox = [-6.5, 52.3, -6.36, 52.44]; }, 'outside the bundle bbox');
  // 8. Generic sc.figure-bundle.v1 renderer: MapLibre views verify only when the FIG-04 modules are loaded.
  const R = require(path.join(root, 'assets/js/modules/graph-studio-figure-bundle-renderer.js'));
  const file = (name, text) => ({ name, bytes: new Uint8Array(Buffer.from(text !== undefined ? text : fs.readFileSync(path.join(dir, name)))) });
  let off = await R.verifyPackage([file('wexford.bundle.json'), file('wexford.map-view.json')]);
  ok(off.views[0].state === 'unsupported', 'without FIG-04 loaded a MapLibre view stays unsupported (integrity verified, nothing drawn)');
  globalThis.SCLabMapLibreFIG03A = M;
  globalThis.SCLabMapLibreFIG04 = require(path.join(root, 'assets/js/modules/graph-studio-maplibre-renderer-fig04.js'));
  const on = await R.verifyPackage([file('wexford.bundle.json'), file('wexford.map-view.json')]);
  ok(on.views[0].state === 'rendered-maplibre' && on.views[0].hashMode && on.views[0].spec.objects.length === 56, 'with FIG-04 loaded the view verifies as rendered-maplibre');
  const tampered = JSON.parse(viewText); tampered.objects[3].properties.soc = 1;
  const tb = json('wexford.bundle.json');
  const F2 = globalThis.SCLabPlotlyPreviewFIG02A;
  const tText = JSON.stringify(tampered);
  tb.artifacts[0].sha256 = await F2.sha256Hex(F2.canonical(F2.parseLexical(tText)));
  tb.rendering.visualizationSpecSha256 = tb.artifacts[0].sha256;
  const refusedPkg = await R.verifyPackage([file('b.json', JSON.stringify(tb)), file('v.json', tText)]).then(() => null, (r) => r);
  ok(Array.isArray(refusedPkg) && refusedPkg.some((r) => /Site Intelligence digest/.test(r)), 're-hashed bundle around an edited object is still refused by the SI digest');
  const fake = await R.verifyPackage([file('wexford.bundle.json'), file('v.json', viewText.replace('"soc": 28.25', '"soc": 28.3'))]).then((x) => x.views[0].state, (r) => r);
  ok(fake === 'missing' || Array.isArray(fake), 'a view whose bytes are not the bundle artifact is not drawn');
  const G = globalThis.SCLabMapLibreFIG04;
  ok(G.libraryErrors().length === 1 && /not loaded/.test(G.libraryErrors()[0]), 'renderer reports MapLibre missing rather than drawing');
  const rText = fs.readFileSync(path.join(root, 'assets/js/modules/graph-studio-maplibre-renderer-fig04.js'), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
  ok(!/innerHTML|insertAdjacentHTML|outerHTML|document\.write|\beval\(|new Function|setHTML|https?:\/\/|setAttribute\('style'/.test(rText), 'renderer injects no HTML, evaluates no code, names no URL and sets no style attribute');
  ok(/abs\.origin !== root\.location\.origin/.test(rText) && /SHA-384/.test(rText) && /setWorkerUrl\(blobUrl\)/.test(rText), 'worker is same-origin, hash-checked and started from a blob URL');

  console.log('PASS - SC-FIG-04 MapLibre view 1.1 contract (' + refusals + ' refusals; 56 SI objects; EO gate closed)');
})().catch((e) => { console.error('FAIL - ' + (e && e.stack || e)); process.exit(1); });
