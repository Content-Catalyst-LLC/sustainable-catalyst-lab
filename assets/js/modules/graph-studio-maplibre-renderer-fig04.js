/*! Sustainable Catalyst Lab — MapLibre geospatial figure renderer (SC-FIG-04).
 *
 * Draws a verified sc-lab-maplibre-view (1.0 or 1.1) with the vendored MapLibre GL JS 5.24.0 CSP build.
 * The view is validated by graph-studio-maplibre-fig03a.js (Site Intelligence digests, evidence classes,
 * constant styles, no URLs) before anything here runs. Controlled network access:
 *
 * - the compiled style has one inline GeoJSON source and no glyphs, sprite, tiles or basemap;
 * - the worker script is fetched from the same origin only, its bytes are checked against the pinned
 *   SHA-384 and it is started from a blob: URL (so CSP needs worker-src blob:, and nothing unverified runs);
 * - every resource MapLibre asks for is recorded (data-map-requests); none is expected;
 * - attribution, legends, tables and feature details are built with textContent, never HTML.
 *
 * Accessible alternatives: layer checkboxes, a scientific legend with units, a labelled time slider with
 * previous and next buttons, a side-by-side comparison with a change table, calculation results with their
 * uncertainty, and the full data table. If WebGL is unavailable the map is skipped and the rest stays.
 */
(function (root, factory) {
  'use strict';
  var api = factory(root);
  if (typeof module === 'object' && module.exports) { module.exports = api; }
  else { root.SCLabMapLibreFIG04 = api; }
}(typeof self !== 'undefined' ? self : this, function (root) {
  'use strict';

  var VERSION = '0.1.0';
  var MAPLIBRE_VERSION = '5.24.0';
  var MEDIA = 'application/vnd.sc.maplibre-view.v1+json';

  function contract() {
    var c = root.SCLabMapLibreFIG03A || (typeof globalThis !== 'undefined' && globalThis.SCLabMapLibreFIG03A);
    if (!c && typeof require === 'function') { c = require('./graph-studio-maplibre-fig03a.js'); }
    if (!c) { throw ['MapLibre view contract is not loaded']; }
    return c;
  }
  function config() { return root.SCLabMapLibreFIG04Config || {}; }
  function gl() { return root.maplibregl; }

  // Library check: the vendored build, at the pinned version, with its CSP worker hook.
  function libraryErrors() {
    var m = gl();
    if (!m || typeof m.Map !== 'function' || typeof m.setWorkerUrl !== 'function') { return ['MapLibre GL JS ' + MAPLIBRE_VERSION + ' (CSP build) is not loaded']; }
    var v = typeof m.getVersion === 'function' ? m.getVersion() : m.version;
    if (v !== MAPLIBRE_VERSION) { return ['MapLibre GL JS ' + String(v) + ' is loaded, but ' + MAPLIBRE_VERSION + ' is pinned']; }
    return [];
  }

  function b64(buf) {
    var s = '', a = new Uint8Array(buf);
    for (var i = 0; i < a.length; i++) { s += String.fromCharCode(a[i]); }
    return root.btoa(s);
  }

  // Worker: same-origin bytes, checked against the pinned SHA-384, run from a blob: URL.
  var workerPromise = null;
  function prepareWorker(url, integrity) {
    if (workerPromise) { return workerPromise; }
    workerPromise = Promise.resolve().then(function () {
      var e = libraryErrors();
      if (e.length) { throw e; }
      if (typeof url !== 'string' || !/^sha384-[A-Za-z0-9+/]{64}$/.test(String(integrity))) { throw ['MapLibre worker URL and SHA-384 integrity are not configured']; }
      var abs = new URL(url, root.location.href);
      if (abs.origin !== root.location.origin) { throw ['MapLibre worker must be served from this site (' + abs.origin + ' refused)']; }
      return root.fetch(abs.href, { credentials: 'omit', cache: 'no-cache', redirect: 'error' });
    }).then(function (r) {
      if (!r.ok) { throw ['MapLibre worker could not be loaded (HTTP ' + r.status + ')']; }
      return r.arrayBuffer();
    }).then(function (buf) {
      return root.crypto.subtle.digest('SHA-384', buf).then(function (h) {
        if ('sha384-' + b64(h) !== integrity) { throw ['MapLibre worker bytes do not match the pinned SHA-384; not started']; }
        var blobUrl = URL.createObjectURL(new Blob([buf], { type: 'text/javascript' }));
        gl().setWorkerUrl(blobUrl);
        return { workerUrl: blobUrl, integrity: integrity };
      });
    });
    workerPromise.catch(function () { workerPromise = null; });
    return workerPromise;
  }

  function webglAvailable() {
    try {
      var c = root.document.createElement('canvas');
      return !!(c.getContext('webgl2') || c.getContext('webgl'));
    } catch (e) { return false; }
  }

  function el(tag, attrs, text) {
    var n = root.document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text !== undefined && text !== null) { n.textContent = String(text); }
    return n;
  }
  function swatch(color) {
    var s = el('span', { 'class': 'sc-lab-fig04-swatch', 'aria-hidden': 'true' });
    s.style.backgroundColor = color; // CSSOM, not a style attribute (strict CSP)
    return s;
  }
  function table(model) {
    var t = el('table', { 'class': 'sc-lab-fig02a-table' });
    t.appendChild(el('caption', null, model.caption));
    var head = t.appendChild(el('thead')).appendChild(el('tr'));
    model.columns.forEach(function (h) { head.appendChild(el('th', { scope: 'col' }, h)); });
    var body = t.appendChild(el('tbody'));
    model.rows.forEach(function (r) {
      var tr = body.appendChild(el('tr'));
      r.forEach(function (v, k) { tr.appendChild(el(k === 0 ? 'th' : 'td', k === 0 ? { scope: 'row' } : null, v)); });
    });
    return t;
  }
  function shortTime(iso) { return String(iso).slice(0, 10); }

  function legendBox(spec) {
    var box = el('div', { 'class': 'sc-lab-fig04-legend', role: 'group', 'aria-label': 'Map legend' });
    contract().legendModel(spec).forEach(function (g) {
      var item = box.appendChild(el('div', { 'class': 'sc-lab-fig04-legend-layer', 'data-legend-layer': g.layer }));
      item.appendChild(el('p', { 'class': 'sc-lab-fig04-legend-title' }, g.label + (g.evidenceClass ? ' — ' + g.evidenceClass : '')));
      if (g.classes) {
        item.appendChild(el('p', { 'class': 'sc-lab-fig04-legend-field' }, g.field));
        var ul = item.appendChild(el('ul'));
        g.classes.forEach(function (c) { var li = ul.appendChild(el('li')); li.appendChild(swatch(c.color)); li.appendChild(el('span', null, c.label)); });
      } else if (g.ramp) {
        item.appendChild(el('p', { 'class': 'sc-lab-fig04-legend-field' }, g.field));
        var ramp = item.appendChild(el('p', { 'class': 'sc-lab-fig04-ramp' }));
        ramp.appendChild(el('span', null, g.rampLabels[0]));
        g.ramp.forEach(function (c) { ramp.appendChild(swatch(c)); });
        ramp.appendChild(el('span', null, g.rampLabels[1]));
        item.appendChild(el('p', { 'class': 'sc-lab-fig02a-help' }, g.note));
      } else {
        var one = item.appendChild(el('p'));
        one.appendChild(swatch(g.color)); one.appendChild(el('span', null, g.geometry));
      }
    });
    return box;
  }

  function calculationsBox(spec, bundle) {
    var calcs = Array.isArray(spec.calculations) ? spec.calculations : [];
    if (!calcs.length) { return null; }
    var labels = { 'standard-error': 'standard error', 'standard-deviation': 'standard deviation', 'ci95-half-width': '95% CI half-width' };
    var dl = el('dl', { 'class': 'sc-lab-fig04-calculations', 'aria-label': 'Calculation results' });
    calcs.forEach(function (c) {
      var ref = bundle.calculationRefs[c.calculationRef];
      dl.appendChild(el('dt', null, c.label));
      dl.appendChild(el('dd', { 'data-calculation-ref': String(c.calculationRef) },
        c.value + (c.uncertainty !== undefined ? ' ± ' + c.uncertainty : '') + ' ' + c.unit +
        (c.uncertainty !== undefined ? ' (' + labels[c.uncertaintyKind] + ')' : '') + '. Method: ' + c.method +
        '. Run ' + ref.runRef + ', output SHA-256 ' + ref.outputSha256.slice(0, 16) + '…'));
    });
    return dl;
  }

  // Draws one verified view into slot. Resolves to a handle; on any failure the slot keeps the
  // legend and tables and records data-map-state="unavailable" with the reason.
  function createMap(slot, spec, bundle, options) {
    var C = contract(), opts = options || {}, requests = [];
    var v11 = spec.schema === 'sc-lab-maplibre-view/1.1';
    var steps = C.timeSteps(spec), step = v11 && spec.time ? spec.time.initial : null;
    slot.setAttribute('data-map-state', 'loading');
    slot.setAttribute('data-map-requests', '0');
    var wrap = slot.appendChild(el('div', { 'class': 'sc-lab-fig04-map-wrap' }));
    var controls = wrap.appendChild(el('div', { 'class': 'sc-lab-fig04-controls' }));
    var maps = wrap.appendChild(el('div', { 'class': 'sc-lab-fig04-maps' }));
    var main = maps.appendChild(el('div', { 'class': 'sc-lab-fig04-map', role: 'region', 'aria-label': 'Interactive map: ' + bundle.rendering.altText, 'data-map-pane': 'main' }));
    var second = null;
    var status = wrap.appendChild(el('p', { 'class': 'sc-lab-fig04-status', 'aria-live': 'polite' }));
    var detail = wrap.appendChild(el('output', { 'class': 'sc-lab-fig04-detail', 'aria-live': 'polite' }));
    wrap.appendChild(legendBox(spec));
    var calc = calculationsBox(spec, bundle);
    if (calc) { wrap.appendChild(calc); }
    var attribution = wrap.appendChild(el('p', { 'class': 'sc-lab-fig04-attribution' },
      'Data: ' + bundle.sourceRefs.map(function (s) { return s.sourceId + ' (' + (s.notes || s.licenceStatus) + ')'; }).join('; ') +
      '. No basemap or imagery. Rendered with MapLibre GL JS ' + MAPLIBRE_VERSION + '.'));
    attribution.setAttribute('data-map-attribution', 'sources');
    var tables = wrap.appendChild(el('details', { 'class': 'sc-lab-fig02a-data' }));
    tables.appendChild(el('summary', null, 'Data table (accessible alternative)'));
    tables.appendChild(table(C.tableModel(spec, bundle.rendering.caption)));
    if (v11 && spec.comparison) {
      var ct = wrap.appendChild(el('details', { 'class': 'sc-lab-fig02a-data', 'data-comparison-table': '' }));
      ct.appendChild(el('summary', null, 'Comparison table: ' + spec.comparison.label));
      ct.appendChild(table(C.comparisonModel(spec)));
    }

    // Layer selection.
    var visible = {};
    var fs = controls.appendChild(el('fieldset', { 'class': 'sc-lab-fig04-layers' }));
    fs.appendChild(el('legend', null, 'Layers'));
    spec.layers.forEach(function (l) {
      visible[l.id] = true;
      var g = (spec.legend || []).filter(function (x) { return x.layer === l.id; })[0];
      var lab = fs.appendChild(el('label'));
      var box = lab.appendChild(el('input', { type: 'checkbox', checked: '', 'data-layer-toggle': l.id }));
      lab.appendChild(el('span', null, g ? g.label : l.id));
      box.addEventListener('change', function () { setLayerVisible(l.id, box.checked); });
    });

    // Time steps.
    var range = null, prev = null, next = null, stepOut = null;
    if (v11 && spec.time) {
      var tf = controls.appendChild(el('fieldset', { 'class': 'sc-lab-fig04-time' }));
      tf.appendChild(el('legend', null, spec.time.label));
      prev = tf.appendChild(el('button', { type: 'button', 'data-time-prev': '' }, 'Previous'));
      range = tf.appendChild(el('input', { type: 'range', min: '0', max: String(steps.length - 1), step: '1',
        value: String(steps.indexOf(step)), 'aria-label': spec.time.label, 'data-time-range': '' }));
      next = tf.appendChild(el('button', { type: 'button', 'data-time-next': '' }, 'Next'));
      stepOut = tf.appendChild(el('output', { 'data-time-output': '' }));
      range.addEventListener('input', function () { setStep(steps[Number(range.value)]); });
      prev.addEventListener('click', function () { var k = steps.indexOf(step); if (k > 0) { setStep(steps[k - 1]); } });
      next.addEventListener('click', function () { var k = steps.indexOf(step); if (k < steps.length - 1) { setStep(steps[k + 1]); } });
    }
    var compareBtn = null;
    if (v11 && spec.comparison) {
      compareBtn = controls.appendChild(el('button', { type: 'button', 'aria-pressed': 'false', 'data-compare-toggle': '' },
        'Compare ' + shortTime(spec.comparison.from) + ' with ' + shortTime(spec.comparison.to)));
      compareBtn.addEventListener('click', function () { setCompare(compareBtn.getAttribute('aria-pressed') !== 'true'); });
    }

    var objectsById = {};
    spec.objects.forEach(function (o) { objectsById[o.object_id] = o; });
    var dataLayers = spec.layers.reduce(function (ids, l) { return ids.concat(C.styleLayerIds(l)); }, []);
    var mapA = null, mapB = null, syncing = false;

    function record(url) {
      requests.push(String(url));
      slot.setAttribute('data-map-requests', String(requests.length));
      return { url: url };
    }
    function newMap(container, at) {
      var M = gl();
      var cam = spec.camera || {};
      var m = new M.Map({
        container: container, style: C.compileStyle(spec, at === null ? undefined : at),
        bounds: cam.bbox || bundle.spatial.bbox, fitBoundsOptions: { padding: 24 }, maxZoom: cam.maxZoom || 14,
        attributionControl: false, transformRequest: record, cooperativeGestures: false, localIdeographFontFamily: false
      });
      m.addControl(new M.NavigationControl({ showCompass: false }), 'top-right');
      m.on('click', function (ev) {
        var hit = m.queryRenderedFeatures(ev.point, { layers: dataLayers.filter(function (id) { return !/heat/.test(m.getLayer(id) && m.getLayer(id).type || ''); }) })[0];
        var o = hit && objectsById[hit.properties.sc_object_id];
        detail.textContent = o ? describe(o) : '';
      });
      return m;
    }
    function describe(o) {
      var p = o.properties || {}, f = spec.fields || {};
      return [p.title || o.object_id].concat(Object.keys(f).filter(function (k) { return p[k] !== undefined && p[k] !== null && f[k].unit !== 'category'; }).map(function (k) {
        var u = f[k].uncertainty && p[f[k].uncertainty];
        return f[k].label + ' ' + p[k] + (typeof u === 'number' ? ' ± ' + u : '') + ' ' + (f[k].unit === '1' ? '' : f[k].unit);
      })).concat([p[spec.evidenceField], shortTime(o.observed_at || '')]).join(' · ');
    }
    function applyFilters(m, at) {
      spec.layers.forEach(function (l) {
        var filter = C.layerFilter(spec, l, at);
        C.styleLayerIds(l).forEach(function (id) { m.setFilter(id, filter); });
      });
    }
    function setLayerVisible(id, on) {
      visible[id] = !!on;
      var l = spec.layers.filter(function (x) { return x.id === id; })[0];
      [mapA, mapB].forEach(function (m) {
        if (m) { C.styleLayerIds(l).forEach(function (sid) { m.setLayoutProperty(sid, 'visibility', on ? 'visible' : 'none'); }); }
      });
      var box = fs.querySelector('[data-layer-toggle="' + id + '"]');
      if (box && box.checked !== !!on) { box.checked = !!on; }
      slot.setAttribute('data-layers-visible', Object.keys(visible).filter(function (k) { return visible[k]; }).join(','));
    }
    function setStep(s) {
      if (steps.indexOf(s) < 0) { return; }
      step = s;
      if (mapA && !(compareBtn && compareBtn.getAttribute('aria-pressed') === 'true')) { applyFilters(mapA, s); }
      range.value = String(steps.indexOf(s));
      range.setAttribute('aria-valuetext', s);
      stepOut.textContent = shortTime(s) + ' (' + (steps.indexOf(s) + 1) + ' of ' + steps.length + ')';
      prev.disabled = steps.indexOf(s) === 0; next.disabled = steps.indexOf(s) === steps.length - 1;
      slot.setAttribute('data-time-step', s);
    }
    function sync(from, to) {
      from.on('move', function () {
        if (syncing || !to) { return; }
        syncing = true; to.jumpTo({ center: from.getCenter(), zoom: from.getZoom() }); syncing = false;
      });
    }
    function setCompare(on) {
      if (!compareBtn) { return; }
      compareBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (range) { range.disabled = on; prev.disabled = on || steps.indexOf(step) === 0; next.disabled = on || steps.indexOf(step) === steps.length - 1; }
      slot.setAttribute('data-compare', on ? 'on' : 'off');
      if (!mapA) { return; }
      if (on) {
        applyFilters(mapA, spec.comparison.from);
        main.setAttribute('aria-label', 'Map at ' + shortTime(spec.comparison.from) + ': ' + bundle.rendering.altText);
        second = maps.appendChild(el('div', { 'class': 'sc-lab-fig04-map', role: 'region', 'data-map-pane': 'compare',
          'aria-label': 'Map at ' + shortTime(spec.comparison.to) + ': ' + bundle.rendering.altText }));
        maps.setAttribute('data-split', 'two');
        mapA.resize();
        mapB = newMap(second, spec.comparison.to);
        mapB.on('load', function () {
          Object.keys(visible).forEach(function (id) { if (!visible[id]) { setLayerVisible(id, false); } });
          mapB.jumpTo({ center: mapA.getCenter(), zoom: mapA.getZoom() });
          slot.setAttribute('data-compare-map', 'ready');
        });
        sync(mapA, mapB); sync(mapB, mapA);
        status.textContent = 'Comparing ' + shortTime(spec.comparison.from) + ' (left) with ' + shortTime(spec.comparison.to) + ' (right). The change table lists every matched ' + spec.comparison.match + '.';
      } else {
        if (mapB) { mapB.remove(); mapB = null; }
        if (second) { second.remove(); second = null; }
        maps.removeAttribute('data-split');
        slot.removeAttribute('data-compare-map');
        main.setAttribute('aria-label', 'Interactive map: ' + bundle.rendering.altText);
        mapA.resize();
        applyFilters(mapA, step);
        status.textContent = '';
      }
    }
    function unavailable(reason) {
      slot.setAttribute('data-map-state', 'unavailable');
      main.appendChild(el('p', { 'class': 'sc-lab-figure-bundle-unavailable', role: 'note' }, 'Interactive map not drawn: ' + reason + '. The legend and data tables above and below describe the same verified data.'));
    }

    if (range) { setStep(step); }
    slot.setAttribute('data-layers-visible', Object.keys(visible).join(','));
    var e = libraryErrors();
    if (e.length) { unavailable(e.join('; ')); return Promise.resolve({ state: 'unavailable', reasons: e }); }
    if (!webglAvailable()) { unavailable('WebGL is not available in this browser'); return Promise.resolve({ state: 'unavailable', reasons: ['no WebGL'] }); }
    var handle = {
      state: 'ready', requests: requests,
      map: function () { return mapA; }, compareMap: function () { return mapB; },
      setStep: setStep, setLayerVisible: setLayerVisible, setCompare: setCompare
    };
    var cfg = config();
    return prepareWorker(opts.workerUrl || cfg.workerUrl, opts.workerIntegrity || cfg.workerIntegrity).then(function () {
      return new Promise(function (resolve) {
        try { mapA = newMap(main, step); } catch (err) { unavailable(String(err && err.message || err)); resolve({ state: 'unavailable' }); return; }
        mapA.on('error', function (ev) { slot.setAttribute('data-map-error', String(ev && ev.error && ev.error.message || 'error').slice(0, 200)); });
        mapA.on('load', function () {
          slot.setAttribute('data-map-state', 'ready');
          resolve(handle);
        });
      });
    }, function (reasons) {
      unavailable(Array.isArray(reasons) ? reasons.join('; ') : String(reasons));
      return { state: 'unavailable', reasons: reasons };
    });

  }

  return {
    version: VERSION, maplibreVersion: MAPLIBRE_VERSION, media: MEDIA,
    viewErrors: function (text, spec, bundle) { return contract().viewErrors(text, spec, bundle); },
    libraryErrors: libraryErrors, prepareWorker: prepareWorker, createMap: createMap
  };
}));
