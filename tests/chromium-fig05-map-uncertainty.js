// SC-FIG-05.3 Chromium harness (map): a value layer and a runtime-bound uncertainty layer over the same
// synthetic fields, toggled with the layer checkboxes; the legend names the uncertainty kind and unit and the
// field the run reported nothing for; the static export receipt binds the uncertainty record.
(async function () {
  'use strict';
  var log = [], failures = [], DIR = 'fixtures/fig05-uncertainty/';
  var integrity = decodeURIComponent((location.hash.match(/integrity=([^&]+)/) || [])[1] || '');
  var WORKER = '../assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp-worker.js';
  var violations = [];
  document.addEventListener('securitypolicyviolation', function (e) { violations.push(e.violatedDirective + ' ' + e.blockedURI); });
  function check(cond, msg) { log.push((cond ? 'ok   ' : 'FAIL ') + msg); if (!cond) { failures.push(msg); } document.getElementById('cert-log').textContent = log.join('\n'); }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  async function until(fn, ms) { for (var t = 0; t < (ms || 30000); t += 100) { if (fn()) { return true; } await wait(100); } return false; }
  async function text(path) { return (await fetch(path)).text(); }
  function file(name, t) { return { name: name, bytes: new TextEncoder().encode(t) }; }
  var api = window.SCLabFigureBundleRenderer, G = window.SCLabMapLibreFIG04;
  try {
    check(!!(api && G && window.maplibregl), 'modules and MapLibre loaded');
    var bundleText = await text(DIR + 'map.bundle.json'), viewText = await text(DIR + 'map.view.json');
    var bundle = JSON.parse(bundleText), view = JSON.parse(viewText);
    var out = document.getElementById('main-out').appendChild(document.createElement('div'));
    out.id = 'map';
    var res = await api.render(out, [file('map.bundle.json', bundleText), file('map.view.json', viewText)], undefined,
      { maplibre: { workerUrl: WORKER, workerIntegrity: integrity } });
    var slot = out.querySelector('[data-view-state]');
    check(res.state === 'rendered' && slot.getAttribute('data-view-state') === 'rendered-maplibre', 'bundle verified and view rendered-maplibre: ' + res.state + ' ' + (slot && slot.getAttribute('data-view-state')) + ' ' + (slot && slot.getAttribute('data-map-state')) + ' ' + (slot ? slot.textContent : out.textContent).slice(0, 400));
    check(await until(function () { return slot.getAttribute('data-map-state') === 'ready'; }), 'map loaded: ' + slot.getAttribute('data-map-state'));
    var canvas = slot.querySelector('canvas.maplibregl-canvas');
    check(!!canvas && canvas.width > 100, 'WebGL canvas drawn');

    var us = out.querySelector('[data-uncertainty-status]');
    check(us && us.getAttribute('data-uncertainty-status') === 'runtime-computed', 'card states runtime-computed uncertainty');
    var lu = slot.querySelector('[data-legend-layer="soc-uncertainty"]');
    check(lu && lu.getAttribute('data-legend-encode') === 'uncertainty', 'uncertainty layer has its own legend entry');
    var classes = Array.prototype.map.call(lu.querySelectorAll('li'), function (li) { return li.textContent; });
    check(classes.join('|') === '< 0.8 g kg-1|0.8 to < 1.2 g kg-1|1.2 to < 1.8 g kg-1|≥ 1.8 g kg-1|uncertainty not reported (none drawn or imputed)', 'uncertainty classes with units: ' + classes.join('|'));
    check(/Soil organic carbon ± standard deviation \(g kg-1\)/.test(lu.textContent) && /1 object\(s\) have no reported uncertainty/.test(lu.textContent), 'legend names the kind, unit and the unreported field');
    var sw = Array.prototype.map.call(lu.querySelectorAll('li .sc-lab-fig04-swatch'), function (s) { return getComputedStyle(s).backgroundColor; });
    check(sw.length >= 4 && sw[0] === 'rgb(0, 34, 78)', 'cividis swatches drawn through CSSOM: ' + sw.slice(0, 2).join(' '));

    // Toggle value <-> uncertainty with the existing layer checkboxes.
    var tv = slot.querySelector('[data-layer-toggle="soc-value"]'), tu = slot.querySelector('[data-layer-toggle="soc-uncertainty"]');
    check(tv && tu && tv.checked && tu.checked, 'both layers listed with checkboxes');
    tv.click(); await wait(300);
    check(!tv.checked && tu.checked, 'value layer hidden; uncertainty layer shown');
    var table = Array.prototype.filter.call(slot.querySelectorAll('table'), function (t) { return /standard deviation/.test(t.textContent); })[0];
    check(table && table.querySelectorAll('tbody tr').length === 6 && /not reported/.test(table.textContent), 'accessible table: six fields, one uncertainty not reported');

    // Static export receipt binds the runtime uncertainty record.
    var runExport = res.exports && res.exports[res.exports.length - 1];
    if (typeof runExport === 'function') {
      var x = await runExport();
      var rc = x && x.receipt && x.receipt.receipt;
      check(rc && rc.calculations[0].uncertaintySha256 === bundle.calculationRefs[0].uncertaintySha256, 'export receipt binds the uncertainty record hash');
      check(rc && rc.state.visibleLayers.join() === 'soc-uncertainty' && /± standard deviation/.test(JSON.stringify(rc.legend)), 'receipt records the uncertainty layer and its legend');
      window.__fig05 = { exportB64: btoa(Array.prototype.map.call(x.png, function (c) { return String.fromCharCode(c); }).join('')) };
    } else {
      check(false, 'static export control not offered');
    }

    // Refusals at render time.
    var tOut = document.getElementById('main-out').appendChild(document.createElement('div'));
    var b2 = JSON.parse(bundleText); delete b2.calculationRefs[0].uncertaintySha256;
    var r2 = await api.render(tOut, [file('b.json', JSON.stringify(b2)), file('v.json', viewText)]);
    check(r2.state === 'refused' && /bound to a Workspace run/.test(tOut.textContent), 'unbound uncertainty layer refused');
    var F = window.SCLabPlotlyPreviewFIG02A;
    var dText = viewText.replace('"#00224e"', '"#d73027"');
    var b3 = JSON.parse(bundleText); b3.artifacts[0].sha256 = b3.rendering.visualizationSpecSha256 = await F.sha256Hex(F.canonical(F.parseLexical(dText)));
    var r3 = await api.render(tOut, [file('b.json', JSON.stringify(b3)), file('v.json', dText)]);
    check(r3.state === 'refused' && /ordered run/.test(tOut.textContent), 'non-sequential (diverging) uncertainty colours refused');
    tOut.remove();

    var res2 = performance.getEntriesByType('resource').map(function (e) { return e.name; });
    var foreign = res2.filter(function (u) { return !(u.indexOf(location.origin) === 0 || /^(blob|data):/.test(u)); });
    check(!foreign.length, 'every resource is same-origin: ' + foreign.join(' '));
    check(!violations.length, 'no CSP violations: ' + violations.join('; '));
  } catch (e) {
    check(false, 'exception: ' + (e && e.stack || JSON.stringify(e)));
  }
  document.body.setAttribute('data-cert', failures.length ? 'fail' : 'pass');
}());
