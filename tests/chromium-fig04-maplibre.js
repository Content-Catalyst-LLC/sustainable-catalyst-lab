// SC-FIG-04 Chromium harness: draws the synthetic Wexford view through the generic renderer and exercises
// layer selection, legend, time steps, comparison, integrity and Earth-observation refusals.
(async function () {
  'use strict';
  var log = [], failures = [], DIR = 'fixtures/fig04-wexford/';
  var integrity = decodeURIComponent((location.hash.match(/integrity=([^&]+)/) || [])[1] || '');
  var WORKER = '../assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp-worker.js';
  var violations = [];
  document.addEventListener('securitypolicyviolation', function (e) { violations.push(e.violatedDirective + ' ' + e.blockedURI); });
  function check(cond, msg) { log.push((cond ? 'ok   ' : 'FAIL ') + msg); if (!cond) { failures.push(msg); } document.getElementById('cert-log').textContent = log.join('\n'); }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  async function until(fn, ms) { for (var t = 0; t < (ms || 30000); t += 100) { if (fn()) { return true; } await wait(100); } return false; }
  async function text(path) { return (await fetch(path)).text(); }
  function file(name, t) { return { name: name, bytes: new TextEncoder().encode(t) }; }
  var api = window.SCLabFigureBundleRenderer;
  var F = window.SCLabPlotlyPreviewFIG02A, C = window.SCLabMapLibreFIG03A, G = window.SCLabMapLibreFIG04;
  try {
    check(!!(F && C && G && window.maplibregl), 'modules and MapLibre loaded');
    check(G.libraryErrors().length === 0, 'MapLibre 5.24.0 CSP build recognised: ' + G.libraryErrors().join());
    var bundleText = await text(DIR + 'wexford.bundle.json'), viewText = await text(DIR + 'wexford.map-view.json');
    var view = JSON.parse(viewText), bundle = JSON.parse(bundleText);
    check(!!api, 'generic renderer API found');

    // 1. A worker whose pinned hash is wrong is never started; the map is reported unavailable, tables stay.
    var bad = document.getElementById('main-out').appendChild(document.createElement('div'));
    var r0 = await api.render(bad, [file('b.json', bundleText), file('v.json', viewText)], undefined,
      { maplibre: { workerUrl: WORKER, workerIntegrity: 'sha384-' + 'A'.repeat(64) } });
    var slot0 = bad.querySelector('[data-view-state]');
    check(slot0 && slot0.getAttribute('data-map-state') === 'unavailable' && /do not match the pinned SHA-384/.test(bad.textContent), 'wrong worker hash: worker not started, map unavailable');
    check(bad.querySelectorAll('table').length === 2 && bad.querySelector('.sc-lab-fig04-legend'), 'legend and tables still shown without the map');
    bad.remove();

    // 2. Verified render.
    var out = document.getElementById('main-out').appendChild(document.createElement('div'));
    out.id = 'wexford';
    var res = await api.render(out, [file('wexford.bundle.json', bundleText), file('wexford.map-view.json', viewText)], undefined,
      { maplibre: { workerUrl: WORKER, workerIntegrity: integrity } });
    var slot = out.querySelector('[data-view-state]');
    check(res.state === 'rendered' && slot.getAttribute('data-view-state') === 'rendered-maplibre', 'bundle verified and view rendered-maplibre');
    check(slot.getAttribute('data-map-state') === 'ready', 'map loaded (data-map-state ready): ' + slot.getAttribute('data-map-state') + ' ' + out.textContent.slice(0, 200));
    var canvas = slot.querySelector('canvas.maplibregl-canvas');
    check(!!canvas && canvas.width > 100, 'WebGL canvas drawn');
    check(slot.querySelector('[role=region][aria-label^="Interactive map"]'), 'map region labelled with the alt text');
    var maps = Array.prototype.slice.call(slot.querySelectorAll('.maplibregl-map'));
    check(maps.length === 1, 'one map before comparison');

    // Legend.
    var legend = slot.querySelector('.sc-lab-fig04-legend');
    var classes = Array.prototype.map.call(legend.querySelectorAll('[data-legend-layer="field-soc"] li'), function (li) { return li.textContent; });
    check(classes.join('|') === '< 26 g kg-1|26 to < 29 g kg-1|29 to < 32 g kg-1|≥ 32 g kg-1|not reported', 'graduated legend with units: ' + classes.join('|'));
    check(/not interpolated values/.test(legend.querySelector('[data-legend-layer="nitrate-heat"]').textContent), 'heat-map legend states it is a density, not interpolated values');
    check(legend.querySelectorAll('.sc-lab-fig04-swatch').length === 5 + 5 + 1, 'legend swatches drawn through CSSOM (strict CSP)');
    check(/modelled/.test(legend.textContent), 'legend states the evidence class');

    // Time controls.
    var steps = C.timeSteps(view);
    check(slot.getAttribute('data-time-step') === steps[3], 'starts on the latest quarter');
    slot.querySelector('[data-time-prev]').click(); await wait(300);
    check(slot.getAttribute('data-time-step') === steps[2] && /3 of 4/.test(slot.querySelector('[data-time-output]').textContent), 'previous moves one quarter back');
    var range = slot.querySelector('[data-time-range]');
    range.value = '0'; range.dispatchEvent(new Event('input')); await wait(300);
    check(slot.getAttribute('data-time-step') === steps[0] && slot.querySelector('[data-time-prev]').disabled, 'slider jumps to the first quarter; previous disabled');
    check(range.getAttribute('aria-valuetext') === steps[0], 'slider announces the step');

    window.__fig04 = {};

    // Layer selection.
    var toggle = slot.querySelector('[data-layer-toggle="nitrate-heat"]');
    toggle.click(); await wait(200);
    check(slot.getAttribute('data-layers-visible') === 'field-soc,nitrate-sites', 'unchecking the heat map hides it: ' + slot.getAttribute('data-layers-visible'));
    toggle.click(); await wait(200);
    check(slot.getAttribute('data-layers-visible') === 'field-soc,nitrate-heat,nitrate-sites', 'checking it again shows it');

    // Comparison.
    var cmp = slot.querySelector('[data-compare-toggle]');
    cmp.click();
    check(await until(function () { return slot.getAttribute('data-compare-map') === 'ready'; }, 30000), 'comparison map loaded');
    check(slot.querySelectorAll('.maplibregl-map').length === 2 && slot.querySelector('.sc-lab-fig04-maps').getAttribute('data-split') === 'two', 'two maps side by side');
    check(range.disabled && cmp.getAttribute('aria-pressed') === 'true', 'time slider disabled while comparing');
    var ctab = slot.querySelector('[data-comparison-table] table');
    check(ctab && ctab.querySelectorAll('tbody tr').length === 6 && /independence assumed/.test(ctab.textContent), 'comparison table: six fields with propagated uncertainty');
    await wait(800);
    window.__fig04.ready = true;
    // The driver takes a screenshot here, then sets __fig04.continue.
    await until(function () { return window.__fig04.continue; }, 60000);
    cmp.click(); await wait(300);
    check(slot.querySelectorAll('.maplibregl-map').length === 1 && !range.disabled, 'comparison off restores one map and the time slider');

    // Calculations and table.
    check(/g kg-1 yr-1 \(standard error\)/.test(slot.querySelector('.sc-lab-fig04-calculations').textContent), 'calculation result with unit and standard error');
    var dataTable = slot.querySelector('details:not([data-comparison-table]) table');
    check(dataTable.querySelectorAll('tbody tr').length === 56 && /± standard error/.test(dataTable.textContent), 'accessible table: 56 objects with uncertainty');
    check(slot.getAttribute('data-map-requests') === '0', 'MapLibre requested no resource (no tiles, glyphs, sprites)');
    check(/No basemap or imagery/.test(slot.querySelector('[data-map-attribution]').textContent), 'attribution names sources and no basemap');

    // SC-FIG-04.1 static PNG export: with fetch and XHR disabled, at a chosen step with one layer hidden.
    var runExport = res.exports[res.exports.length - 1];
    check(typeof runExport === 'function' && slot.querySelector('[data-export-png]') && !slot.querySelector('[data-export-png]').disabled, 'PNG export control offered once the map is ready');
    slot.querySelector('[data-time-next]').click(); await wait(300);
    slot.querySelector('[data-layer-toggle="nitrate-heat"]').click(); await wait(300);
    var resBefore = performance.getEntriesByType('resource').length;
    var realFetch = window.fetch, realXhr = window.XMLHttpRequest;
    window.fetch = function () { throw new Error('network used during export'); };
    window.XMLHttpRequest = function () { throw new Error('network used during export'); };
    var x;
    try { x = await runExport(); } finally { window.fetch = realFetch; window.XMLHttpRequest = realXhr; }
    check(x && x.png && !x.refused, 'export completed without network: ' + JSON.stringify(x && x.refused));
    check(performance.getEntriesByType('resource').length === resBefore && slot.getAttribute('data-map-requests') === '0', 'export fetched nothing');
    check(slot.getAttribute('data-export-state') === 'verified' && slot.getAttribute('data-export-sha256') === x.sha256, 'export verified against this figure');
    check(slot.querySelectorAll('[data-export-download]').length === 2 && /SHA-256 [0-9a-f]{64}/.test(slot.querySelector('[data-export-status]').textContent), 'PNG and receipt offered as links with the hash announced');
    var rc = x.receipt.receipt;
    check(rc.state.timeStep === steps[1] && rc.state.comparison === null && rc.state.visibleLayers.join() === 'field-soc,nitrate-sites', 'receipt records step and visible layers: ' + JSON.stringify(rc.state));
    check(rc.figure.bundleSha256 === res.bundleSha256 && rc.view.sha256 === bundle.artifacts[0].sha256 && rc.state.networkRequests === 0, 'receipt bound to bundle bytes and view');
    check(rc.legend.map(function (g) { return g.layer; }).join() === 'field-soc,nitrate-sites' && /g kg-1/.test(JSON.stringify(rc.legend)), 'legend of visible layers with units in the receipt');
    check(/g kg-1 yr-1 \(standard error\)/.test(rc.calculationText.join(' ')) && /No confidence interval was reported/.test(rc.calculationText.join(' ')), 'calculation text: standard error, no interval invented');
    check(/No basemap or imagery/.test(rc.attribution) && rc.units, 'attribution and units in the receipt');
    var v1 = await G.verifyExport(x.png, x.receipt, { spec: view, bundle: bundle, bundleSha256: res.bundleSha256 });
    check(v1.ok && v1.sha256 === x.sha256, 'independent verifyExport passes: ' + v1.errors.join('; '));
    var bmp = await createImageBitmap(new Blob([x.png], { type: 'image/png' }));
    check(bmp.width === rc.image.width && bmp.height === rc.image.height && bmp.width === 1200, 'PNG decodes at the receipt size ' + bmp.width + 'x' + bmp.height);
    var cv = document.createElement('canvas'); cv.width = bmp.width; cv.height = bmp.height;
    var cx = cv.getContext('2d'); cx.drawImage(bmp, 0, 0);
    var px = cx.getImageData(24, 90, 1152, 500).data, coloured = 0;
    for (var i = 0; i < px.length; i += 4) { if (Math.abs(px[i] - px[i + 1]) > 30 || Math.abs(px[i + 1] - px[i + 2]) > 30) { coloured++; } }
    check(coloured > 2000, 'map frame drawn into the PNG (' + coloured + ' coloured pixels)');
    var flipped = x.png.slice(); flipped[Math.floor(flipped.length / 2)] ^= 1;
    var v2 = await G.verifyExport(flipped, x.receipt, { spec: view, bundle: bundle, bundleSha256: res.bundleSha256 });
    check(!v2.ok, 'tampered PNG refused: ' + v2.errors.join('; '));
    var forged = JSON.parse(JSON.stringify(x.receipt)); forged.receipt.state.timeStep = steps[0];
    var v3 = await G.verifyExport(x.png, forged, { spec: view, bundle: bundle, bundleSha256: res.bundleSha256 });
    check(!v3.ok && v3.errors.indexOf('embedded receipt differs from the receipt file') >= 0, 'edited receipt file refused');
    var v4 = await G.verifyExport(x.png, x.receipt, { spec: view, bundle: bundle, bundleSha256: 'f'.repeat(64) });
    check(!v4.ok && v4.errors.indexOf('receipt names different bundle bytes') >= 0, 'export checked against other bundle bytes refused');
    window.__fig04.exportB64 = btoa(Array.prototype.map.call(x.png, function (c) { return String.fromCharCode(c); }).join(''));
    window.__fig04.exportReceipt = x.receipt;
    slot.querySelector('[data-layer-toggle="nitrate-heat"]').click(); await wait(200);
    // Comparison export: both maps, labelled left and right.
    cmp.click();
    await until(function () { return slot.getAttribute('data-compare-map') === 'ready'; }, 30000); await wait(800);
    var xc = await runExport();
    check(xc && xc.receipt && xc.receipt.receipt.state.comparison && xc.receipt.receipt.state.comparison.to === steps[3] && /^Comparison/.test(xc.receipt.receipt.state.description), 'comparison export records both steps');
    window.__fig04.compareB64 = btoa(Array.prototype.map.call(xc.png, function (c) { return String.fromCharCode(c); }).join(''));
    cmp.click(); await wait(300);

    // 3. Integrity: an edited object, re-hashed into the bundle, is refused by the SI digest.
    var tampered = JSON.parse(viewText); tampered.objects[2].properties.soc = 50;
    var tText = JSON.stringify(tampered), tb = JSON.parse(bundleText);
    tb.artifacts[0].sha256 = await F.sha256Hex(F.canonical(F.parseLexical(tText)));
    tb.rendering.visualizationSpecSha256 = tb.artifacts[0].sha256;
    var tOut = document.getElementById('main-out').appendChild(document.createElement('div'));
    var r2 = await api.render(tOut, [file('b.json', JSON.stringify(tb)), file('v.json', tText)]);
    check(r2.state === 'refused' && /Site Intelligence digest/.test(tOut.textContent) && !tOut.querySelector('canvas'), 'edited SI object refused; nothing drawn');
    // Bytes that do not match the bundle artifact are not drawn.
    var r3 = await api.render(tOut, [file('b.json', bundleText), file('v.json', tText)]);
    check(r3.state !== 'rendered', 'view bytes not matching the bundle are not drawn: ' + r3.state);

    // 4. Earth observation: a Sentinel-2 layer is refused (no provider approved, nothing fetched).
    var eo = JSON.parse(viewText);
    eo.rasterLayers = [{ id: 's2', provider: 'copernicus-sentinel-2-l2a', tiles: [location.origin + '/tiles/{z}/{x}/{y}.png'], attribution: 'Contains modified Copernicus Sentinel data',
      provenance: { productId: 'x', acquiredAt: 'x', processingBaseline: 'x', tileManifestSha256: 'a'.repeat(64) } }];
    var eText = JSON.stringify(eo), eb = JSON.parse(bundleText);
    eb.artifacts[0].sha256 = await F.sha256Hex(F.canonical(F.parseLexical(eText)));
    eb.rendering.visualizationSpecSha256 = eb.artifacts[0].sha256;
    var r4 = await api.render(tOut, [file('b.json', JSON.stringify(eb)), file('v.json', eText)]);
    check(r4.state === 'refused' && /not approved/.test(tOut.textContent), 'Sentinel-2 raster layer refused (no approved provider)');
    // 5. Restricted source licence refused.
    var rb = JSON.parse(bundleText); rb.sourceRefs[1].licenceStatus = 'restricted';
    var r5 = await api.render(tOut, [file('b.json', JSON.stringify(rb)), file('v.json', viewText)]);
    check(r5.state === 'refused' && /not verified-for-use/.test(tOut.textContent), 'restricted source licence refused');
    tOut.remove();

    var res2 = performance.getEntriesByType('resource').map(function (e) { return e.name; });
    var foreign = res2.filter(function (u) { return !(u.indexOf(location.origin) === 0 || /^(blob|data):/.test(u)); });
    check(!foreign.length, 'every resource is same-origin: ' + foreign.join(' '));
    check(!res2.some(function (u) { return /tiles\//.test(u); }), 'no tile request was made');
    check(!violations.length, 'no CSP violations: ' + violations.join('; '));
  } catch (e) {
    check(false, 'exception: ' + (e && e.stack || JSON.stringify(e)));
  }
  document.body.setAttribute('data-cert', failures.length ? 'fail' : 'pass');
  window.__fig04 = window.__fig04 || {};
  window.__fig04.log = log;
}());
