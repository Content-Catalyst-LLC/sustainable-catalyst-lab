/*! Sustainable Catalyst Lab — FIG-03A MapLibre adapter preparation (contract and style compiler only).
 *
 * Not loaded by WordPress and draws nothing yet: MapLibre GL JS is not vendored. This module fixes the
 * contract the future map view must satisfy, using Site Intelligence's existing interchange object
 * (sc-site-intelligence-spatial-evidence-object/2.0) unchanged:
 *
 * - every object's SI content digest is recomputed from the file's own number spellings and must match;
 * - geometry is WGS84 (EPSG:4326) as SI normalised it, with the bbox SI derived; Lab never reprojects,
 *   and an object whose source CRS differs must carry SI's recorded transformation;
 * - vector geometry only (no RasterFootprint: rasters would need tiles);
 * - no basemap, tiles, glyphs, sprites or any URL: the provider allow-list is empty until a provider
 *   has approved provenance, so the compiled style contains one inline GeoJSON source and nothing else;
 * - styles are constants (colours, widths), never MapLibre expressions supplied by the author;
 * - every object carries an evidence class; observed objects only in an observed bundle;
 * - the accessible table lists every object with its source, licence, time and units.
 */
(function (root, factory) {
  'use strict';
  var api = factory(root);
  if (typeof module === 'object' && module.exports) { module.exports = api; }
  else { root.SCLabMapLibreFIG03A = api; }
}(typeof self !== 'undefined' ? self : this, function (root) {
  'use strict';

  var VERSION = '0.0.1-prep';
  var VIEW_SCHEMA = 'sc-lab-maplibre-view/1.0';
  var MEDIA = 'application/vnd.sc.maplibre-view.v1+json';
  var SI_OBJECT = 'sc-site-intelligence-spatial-evidence-object/2.0';
  var CRS = 'EPSG:4326';
  var PROVIDERS = {}; // No basemap or tile provider is approved yet.
  var GEOMETRY = { point: ['Point', 'MultiPoint'], line: ['LineString', 'MultiLineString'], polygon: ['Polygon', 'MultiPolygon'] };
  var EVIDENCE = ['observed', 'literature-derived', 'modelled', 'hypothetical', 'conceptual', 'status-only'];
  var TOP_KEYS = ['schema', 'title', 'objects', 'evidenceField', 'fields', 'layers', 'legend', 'basemap', 'camera'];
  var STYLE_KEYS = { point: ['color', 'radius', 'opacity', 'strokeColor', 'strokeWidth'],
    line: ['color', 'width', 'opacity'], polygon: ['color', 'opacity', 'outlineColor', 'outlineWidth'] };
  var COLOR = /^#[0-9a-fA-F]{6}$/;
  var ID = /^[a-z][a-z0-9-]{0,47}$/;
  var FIELD = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/;
  var URLISH = /(?:^|[^a-z])(?:https?|ftp|file|data|blob|javascript|mapbox|pmtiles):|\{[xyz]\}|\/\//i;
  var MAX_OBJECTS = 5000;

  function lib() {
    var f = root.SCLabPlotlyPreviewFIG02A || (typeof globalThis !== 'undefined' && globalThis.SCLabPlotlyPreviewFIG02A);
    if (!f) { throw new Error('FIG-02A primitives are required'); }
    return f;
  }
  function isObj(v) { return v !== null && typeof v === 'object' && !Array.isArray(v); }
  function has(list, v) { return list.indexOf(v) >= 0; }
  function num(v, lo, hi) { return typeof v === 'number' && isFinite(v) && v >= lo && v <= hi; }

  // ------------------------------------------------------------------
  // Site Intelligence evidence objects
  // ------------------------------------------------------------------
  function member(node, key) {
    if (!node || node.t !== 'o') { return null; }
    for (var j = 0; j < node.v.length; j++) { if (node.v[j][0] === key) { return node.v[j][1]; } }
    return null;
  }

  // SI digest: "sha256:" + SHA-256 of canonical JSON of the object without content_digest.
  function siDigest(objectNode) {
    var F = lib();
    var basis = { t: 'o', v: objectNode.v.filter(function (kv) { return kv[0] !== 'content_digest'; }) };
    return F.sha256Hex(F.canonical(basis)).then(function (h) { return 'sha256:' + h; });
  }

  function positions(coords, out) {
    if (Array.isArray(coords) && coords.length >= 2 && typeof coords[0] === 'number' && typeof coords[1] === 'number') {
      out.push([coords[0], coords[1]]);
    } else if (Array.isArray(coords)) { coords.forEach(function (c) { positions(c, out); }); }
    return out;
  }

  function objectErrors(o, i) {
    var e = [], at = 'objects[' + i + ']';
    if (!isObj(o) || o.schema !== SI_OBJECT) { return [at + ' is not a Site Intelligence ' + SI_OBJECT]; }
    if (o.crs !== CRS) { e.push(at + ' crs must be ' + CRS + ' (Lab does not reproject)'); }
    var prov = isObj(o.provenance) ? o.provenance : {};
    if (prov.source_crs !== CRS && !(Array.isArray(prov.transformations) && prov.transformations.length)) {
      e.push(at + ' source CRS ' + prov.source_crs + ' has no recorded Site Intelligence transformation');
    }
    var g = o.geometry;
    var kinds = [].concat(GEOMETRY.point, GEOMETRY.line, GEOMETRY.polygon);
    if (!isObj(g) || !has(kinds, g.type)) { e.push(at + ' geometry ' + (g && g.type) + ' is not a supported vector type'); return e; }
    var pts = positions(g.coordinates, []);
    if (!pts.length || pts.some(function (p) { return !num(p[0], -180, 180) || !num(p[1], -90, 90); })) {
      e.push(at + ' coordinates are not WGS84 longitude/latitude');
    } else {
      var lons = pts.map(function (p) { return p[0]; }), lats = pts.map(function (p) { return p[1]; });
      var bb = [Math.min.apply(null, lons), Math.min.apply(null, lats), Math.max.apply(null, lons), Math.max.apply(null, lats)];
      if (!Array.isArray(o.bbox) || o.bbox.length !== 4 || o.bbox.some(function (v, k) { return v !== bb[k]; })) {
        e.push(at + ' bbox does not match its geometry');
      }
    }
    var src = isObj(o.source) ? o.source : {};
    if (!src.source_id) { e.push(at + ' has no source_id'); }
    if (o.visibility !== 'public') { e.push(at + ' visibility ' + o.visibility + ' is not public (private objects need the Workspace path)'); }
    if (!/^sha256:[0-9a-f]{64}$/.test(String(o.content_digest))) { e.push(at + ' has no Site Intelligence content digest'); }
    return e;
  }

  // ------------------------------------------------------------------
  // View policy
  // ------------------------------------------------------------------
  function urlErrors(value, path, out) {
    if (typeof value === 'string') {
      if (URLISH.test(value) && !/\.objects\[\d+\]\.source\.url$/.test(path)) { out.push(path + ' contains a URL or tile template'); }
    } else if (Array.isArray(value)) { value.forEach(function (v, k) { urlErrors(v, path + '[' + k + ']', out); }); }
    else if (isObj(value)) { Object.keys(value).forEach(function (k) { urlErrors(value[k], path + '.' + k, out); }); }
    return out;
  }

  function specErrors(spec, bundle) {
    var e = [];
    if (!isObj(spec) || spec.schema !== VIEW_SCHEMA) { return ['view is not ' + VIEW_SCHEMA]; }
    Object.keys(spec).forEach(function (k) { if (!has(TOP_KEYS, k)) { e.push('top-level property ' + k + ' is not allowed'); } });
    if (spec.basemap !== null && spec.basemap !== undefined) {
      var id = isObj(spec.basemap) ? spec.basemap.provider : spec.basemap;
      if (!PROVIDERS[id]) { e.push('basemap ' + JSON.stringify(id) + ' is not an approved provider (none are approved yet; no tile fetch)'); }
    }
    urlErrors(spec, 'view', e);
    var objs = spec.objects;
    if (!Array.isArray(objs) || !objs.length || objs.length > MAX_OBJECTS) { e.push('objects must hold 1 to ' + MAX_OBJECTS + ' evidence objects'); return e; }
    objs.forEach(function (o, i) { e = e.concat(objectErrors(o, i)); });
    var ids = objs.map(function (o) { return o && o.object_id; });
    if (ids.some(function (x, k) { return ids.indexOf(x) !== k; })) { e.push('object_id values must be unique'); }
    // Evidence: one class per object, never promoted to observed.
    var ef = spec.evidenceField;
    if (!FIELD.test(String(ef))) { e.push('evidenceField must name the property holding each object\'s evidence class'); return e; }
    var classes = [];
    objs.forEach(function (o, i) {
      var c = o && isObj(o.properties) ? o.properties[ef] : undefined;
      if (!has(EVIDENCE, c)) { e.push('objects[' + i + '] evidence class ' + JSON.stringify(c) + ' is not recognised'); return; }
      if (classes.indexOf(c) < 0) { classes.push(c); }
      if (c === 'observed' && bundle && bundle.evidenceClass !== 'observed') { e.push('objects[' + i + '] is observed inside a ' + bundle.evidenceClass + ' figure (no promotion to observed)'); }
    });
    // Fields shown in the table need labels and units.
    var fields = isObj(spec.fields) ? spec.fields : {};
    Object.keys(fields).forEach(function (f) {
      var d = fields[f];
      if (!FIELD.test(f) || !isObj(d) || typeof d.label !== 'string' || !d.label || typeof d.unit !== 'string' || !d.unit) { e.push('field ' + f + ' needs a label and a unit'); }
    });
    // Layers: allow-listed geometry, constant styles, filters on the evidence field only.
    var layers = spec.layers, drawn = {};
    if (!Array.isArray(layers) || !layers.length || layers.length > 12) { e.push('layers must hold 1 to 12 layers'); return e; }
    layers.forEach(function (l, i) {
      var at = 'layers[' + i + ']';
      if (!isObj(l) || !ID.test(String(l.id)) || !GEOMETRY[l.geometry]) { e.push(at + ' needs an id and geometry point, line or polygon'); return; }
      Object.keys(l).forEach(function (k) { if (!has(['id', 'geometry', 'where', 'style'], k)) { e.push(at + '.' + k + ' is not allowed'); } });
      if (l.where !== undefined && !(isObj(l.where) && l.where.property === ef && has(EVIDENCE, l.where.equals) && Object.keys(l.where).length === 2)) {
        e.push(at + '.where may only select one evidence class');
      }
      var st = isObj(l.style) ? l.style : {};
      Object.keys(st).forEach(function (k) {
        var v = st[k];
        if (!has(STYLE_KEYS[l.geometry], k)) { e.push(at + '.style.' + k + ' is not allowed for ' + l.geometry); }
        else if (/color$/i.test(k) ? !COLOR.test(String(v)) : !(k === 'opacity' ? num(v, 0, 1) : num(v, 0, 24))) {
          e.push(at + '.style.' + k + ' must be a constant (' + (/color$/i.test(k) ? '#rrggbb' : 'bounded number') + '), not an expression');
        }
      });
      objs.forEach(function (o) {
        if (o && isObj(o.geometry) && has(GEOMETRY[l.geometry], o.geometry.type) && (!l.where || (o.properties || {})[ef] === l.where.equals)) { drawn[o.object_id] = true; }
      });
    });
    var undrawn = objs.filter(function (o) { return o && !drawn[o.object_id]; }).length;
    if (undrawn) { e.push(undrawn + ' object(s) are not drawn by any layer'); }
    if (classes.length > 1 && !classes.every(function (c) { return layers.some(function (l) { return l.where && l.where.equals === c; }); })) {
      e.push('objects mix ' + classes.length + ' evidence classes but each class needs its own layer');
    }
    var legend = Array.isArray(spec.legend) ? spec.legend : [];
    layers.forEach(function (l) {
      if (!legend.some(function (g) { return g && g.layer === l.id && typeof g.label === 'string' && g.label.length > 3; })) { e.push('layer ' + l.id + ' has no legend label'); }
    });
    // Bundle: a spatial-map in EPSG:4326 whose bbox covers every object; every SI source cited.
    if (bundle) {
      var sp = bundle.spatial || {};
      if (bundle.figureType !== 'spatial-map' || sp.crs !== CRS) { e.push('bundle must be a spatial-map in ' + CRS); }
      var bb = sp.bbox;
      if (!Array.isArray(bb) || bb.length !== 4) { e.push('bundle spatial.bbox is required'); }
      else {
        objs.forEach(function (o, i) {
          var b = o && o.bbox;
          if (Array.isArray(b) && (b[0] < bb[0] || b[1] < bb[1] || b[2] > bb[2] || b[3] > bb[3])) { e.push('objects[' + i + '] lies outside the bundle bbox'); }
        });
      }
      var cited = (bundle.sourceRefs || []).map(function (s) { return s.sourceId; });
      objs.forEach(function (o, i) {
        var sid = o && o.source && o.source.source_id;
        if (sid && cited.indexOf(sid) < 0) { e.push('objects[' + i + '] source ' + sid + ' is not cited in the bundle sourceRefs'); }
      });
      if (sp.geometryStatus === 'source-verified' && bundle.sourceRefs.some(function (s) { return s.identityStatus !== 'source-hash-verified'; })) {
        e.push('geometryStatus source-verified needs hash-verified sources');
      }
    }
    return e;
  }

  // Resolves [] when acceptable (policy + every SI digest recomputed from the view's own text).
  function viewErrors(text, spec, bundle) {
    var e = specErrors(spec, bundle);
    if (e.length) { return Promise.resolve(e); }
    var objs = member(lib().parseLexical(text), 'objects');
    return Promise.all(objs.v.map(siDigest)).then(function (digests) {
      return digests.map(function (d, i) {
        return d === spec.objects[i].content_digest ? null : 'objects[' + i + '] content does not match its Site Intelligence digest';
      }).filter(Boolean);
    });
  }

  // ------------------------------------------------------------------
  // MapLibre style (v8): one inline GeoJSON source, no glyphs, sprite or URL anywhere.
  // ------------------------------------------------------------------
  function compileStyle(spec) {
    var ef = spec.evidenceField;
    var features = spec.objects.map(function (o) {
      var props = { sc_object_id: o.object_id };
      props[ef] = o.properties[ef];
      return { type: 'Feature', id: o.object_id, geometry: o.geometry, properties: props };
    });
    var layers = [{ id: 'sc-background', type: 'background', paint: { 'background-color': '#f6f6f3' } }];
    spec.layers.forEach(function (l) {
      var s = l.style || {}, types = GEOMETRY[l.geometry];
      var filter = ['all', ['in', ['geometry-type'], ['literal', types]]];
      if (l.where) { filter.push(['==', ['get', ef], l.where.equals]); }
      if (l.geometry === 'polygon') {
        layers.push({ id: l.id, type: 'fill', source: 'sc-evidence', filter: filter,
          paint: { 'fill-color': s.color || '#4d4d4d', 'fill-opacity': s.opacity === undefined ? 0.3 : s.opacity } });
        layers.push({ id: l.id + '-outline', type: 'line', source: 'sc-evidence', filter: filter,
          paint: { 'line-color': s.outlineColor || s.color || '#4d4d4d', 'line-width': s.outlineWidth === undefined ? 1 : s.outlineWidth } });
      } else if (l.geometry === 'line') {
        layers.push({ id: l.id, type: 'line', source: 'sc-evidence', filter: filter,
          paint: { 'line-color': s.color || '#4d4d4d', 'line-width': s.width === undefined ? 2 : s.width, 'line-opacity': s.opacity === undefined ? 1 : s.opacity } });
      } else {
        layers.push({ id: l.id, type: 'circle', source: 'sc-evidence', filter: filter,
          paint: { 'circle-color': s.color || '#4d4d4d', 'circle-radius': s.radius === undefined ? 5 : s.radius,
            'circle-opacity': s.opacity === undefined ? 1 : s.opacity, 'circle-stroke-color': s.strokeColor || '#ffffff',
            'circle-stroke-width': s.strokeWidth === undefined ? 1 : s.strokeWidth } });
      }
    });
    return {
      version: 8, name: spec.title,
      sources: { 'sc-evidence': { type: 'geojson', data: { type: 'FeatureCollection', features: features } } },
      layers: layers
    };
  }

  // Plain-data accessible table: one row per object.
  function tableModel(spec, caption) {
    var fields = isObj(spec.fields) ? spec.fields : {}, names = Object.keys(fields), ef = spec.evidenceField;
    var columns = ['Object', 'Geometry', 'Evidence class'].concat(names.map(function (f) {
      var d = fields[f]; return ['1', 'category'].indexOf(d.unit) >= 0 ? d.label : d.label + ' (' + d.unit + ')';
    })).concat(['Longitude, latitude (EPSG:4326 bbox centre)', 'Observed or valid time', 'Source', 'Licence', 'SI digest']);
    var rows = spec.objects.map(function (o) {
      var p = o.properties || {}, b = o.bbox, s = o.source || {};
      return [o.object_id, o.geometry.type, String(p[ef])].concat(names.map(function (f) {
        var v = p[f]; return v === null || v === undefined ? 'not reported' : String(v);
      })).concat([((b[0] + b[2]) / 2).toFixed(5) + ', ' + ((b[1] + b[3]) / 2).toFixed(5),
        o.observed_at || (o.valid_time && o.valid_time.start) || 'not reported',
        s.source_id + (s.authority && s.authority !== s.source_id ? ' (' + s.authority + ')' : ''),
        s.license || 'not recorded', o.content_digest]);
    });
    return { caption: caption, columns: columns, rows: rows };
  }

  return {
    version: VERSION, viewSchema: VIEW_SCHEMA, media: MEDIA, siObjectSchema: SI_OBJECT, crs: CRS,
    approvedProviders: function () { return Object.keys(PROVIDERS); },
    siDigest: siDigest, objectErrors: objectErrors, specErrors: specErrors, viewErrors: viewErrors,
    compileStyle: compileStyle, tableModel: tableModel
  };
}));
