'use strict';
// SC-FIG-03A MapLibre adapter preparation: Site Intelligence evidence-object contract, view policy,
// style compiler and table model. Nothing is drawn (MapLibre GL JS is not vendored yet).
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
globalThis.SCLabPlotlyPreviewFIG02A = require(path.join(root, 'assets/js/modules/graph-studio-plotly-preview-fig02a.js'));
const M = require(path.join(root, 'assets/js/modules/graph-studio-maplibre-fig03a.js'));
const dir = path.join(__dirname, 'fixtures/fig03a-maplibre');
const jsText = fs.readFileSync(path.join(root, 'assets/js/modules/graph-studio-maplibre-fig03a.js'), 'utf8')
  .replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
function ok(value, message) { if (!value) { console.error('FAIL - ' + message); process.exit(1); } }
const viewText = fs.readFileSync(path.join(dir, 'soil.map-view.json'), 'utf8');
const json = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
let refusals = 0;

async function refused(label, mutate, needle) {
  const view = JSON.parse(viewText), bundle = json('soil.bundle.json');
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
  ok(/^[0-9a-f]{40}$/.test(source.siteIntelligenceCommit), 'fixtures record the Site Intelligence commit whose normaliser produced them');
  ok(!/innerHTML|insertAdjacentHTML|document\.write|\beval\(|new Function|fetch\(|XMLHttpRequest|https?:\/\//.test(jsText), 'module injects no HTML, evaluates no code, fetches nothing and names no URL');
  ok(M.approvedProviders().length === 0, 'no basemap or tile provider is approved yet');

  // 1. The synthetic view passes, including every SI digest recomputed in JavaScript.
  const view = JSON.parse(viewText), bundle = json('soil.bundle.json');
  ok((await M.viewErrors(viewText, view, bundle)).length === 0, 'synthetic SI-normalised map view accepted');
  const F = globalThis.SCLabPlotlyPreviewFIG02A;
  ok((await F.sha256Hex(F.canonical(F.parseLexical(viewText)))) === bundle.artifacts[0].sha256, 'view canonical hash matches the bundle artifact');

  // 2. Compiled style: one inline GeoJSON source; no URL, glyphs or sprite; one layer set per evidence class.
  const style = M.compileStyle(view);
  const styleText = JSON.stringify(style);
  ok(style.version === 8 && Object.keys(style.sources).join() === 'sc-evidence' && style.sources['sc-evidence'].type === 'geojson', 'style has a single inline GeoJSON source');
  ok(style.glyphs === undefined && style.sprite === undefined && !/https?:|\{z\}|tiles|url/i.test(styleText), 'style references no URL, tiles, glyphs or sprite');
  ok(style.sources['sc-evidence'].data.features.length === view.objects.length, 'every evidence object becomes one feature');
  ok(style.layers.map((l) => l.id).join() === 'sc-background,modelled-zones,modelled-zones-outline,literature-sites', 'layers compiled in order');
  ok(style.layers[3].paint['circle-color'] === '#e66101' && style.layers[1].paint['fill-opacity'] === 0.25, 'constant styles carried through');
  ok(JSON.stringify(style.sources['sc-evidence'].data.features[0].properties) === JSON.stringify({ sc_object_id: view.objects[0].object_id, evidence_class: 'modelled' }), 'features carry only the object id and evidence class');

  // 3. Accessible table.
  const t = M.tableModel(view, bundle.title);
  ok(t.rows.length === 4 && t.columns.includes('Soil organic carbon (g kg-1)') && t.columns.includes('Licence'), 'table lists every object with units and licence');
  ok(t.rows[0][t.columns.indexOf('SI digest')] === view.objects[0].content_digest && t.rows[2][2] === 'literature-derived', 'table rows carry SI digest and evidence class');

  // 4. Refusals: SI contract.
  await refused('object edited after SI normalised it', (v) => { v.objects[0].properties.soc = 99; }, 'does not match its Site Intelligence digest');
  await refused('coordinates moved', (v) => { v.objects[2].geometry.coordinates = [-7.0, 52.2]; }, 'bbox does not match');
  await refused('projected CRS', (v) => { v.objects[0].crs = 'EPSG:3857'; }, 'Lab does not reproject');
  await refused('unrecorded reprojection', (v) => { v.objects[2].provenance.source_crs = 'EPSG:2157'; v.objects[2].provenance.transformations = []; }, 'no recorded Site Intelligence transformation');
  await refused('raster footprint', (v) => { v.objects[0].geometry = { type: 'RasterFootprint', coordinates: [[-7, 52], [-6, 53]] }; }, 'not a supported vector type');
  await refused('private object', (v) => { v.objects[0].visibility = 'restricted'; }, 'is not public');
  await refused('not an SI object', (v) => { v.objects[0].schema = 'geojson'; }, 'is not a Site Intelligence');
  // View policy.
  await refused('basemap', (v) => { v.basemap = { provider: 'openstreetmap' }; }, 'not an approved provider');
  await refused('tile template', (v) => { v.legend[0].label = 'see https://tile.example/{z}/{x}/{y}.png'; }, 'contains a URL or tile template');
  await refused('style expression', (v) => { v.layers[1].style.radius = ['get', 'soc']; }, 'must be a constant');
  await refused('unknown style key', (v) => { v.layers[1].style['text-field'] = 'x'; }, 'is not allowed for point');
  await refused('free filter', (v) => { v.layers[0].where = { property: 'soc', equals: 30 }; }, 'may only select one evidence class');
  await refused('undrawn object', (v) => { v.layers.splice(1, 1); v.legend.splice(1, 1); }, 'not drawn by any layer');
  await refused('missing legend', (v) => { v.legend = []; }, 'has no legend label');
  await refused('field without unit', (v) => { v.fields.soc = { label: 'SOC' }; }, 'needs a label and a unit');
  // Evidence and bundle.
  await refused('modelled object promoted to observed', (v) => { v.objects[0].properties.evidence_class = 'observed'; }, 'no promotion to observed');
  await refused('unknown evidence class', (v) => { v.objects[3].properties.evidence_class = 'measured'; }, 'is not recognised');
  await refused('object outside bundle bbox', (v, b) => { b.spatial.bbox = [-7.0, 52.1, -6.55, 52.35]; }, 'outside the bundle bbox');
  await refused('uncited SI source', (v, b) => { b.sourceRefs[0].sourceId = 'other'; }, 'is not cited');
  await refused('not a spatial map', (v, b) => { b.figureType = 'evidence-chart'; }, 'must be a spatial-map');
  await refused('source-verified geometry without hash-verified sources', (v, b) => { b.spatial.geometryStatus = 'source-verified'; }, 'needs hash-verified sources');

  console.log('PASS - SC-FIG-03A MapLibre preparation contract (' + refusals + ' refusals; SI digests reproduced in JavaScript)');
})().catch((e) => { console.error('FAIL - ' + (e && e.stack || JSON.stringify(e))); process.exit(1); });
