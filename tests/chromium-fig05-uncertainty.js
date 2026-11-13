// SC-FIG-05.3 Chromium harness (chart): the released package (bundle + Plotly figure + runtime band and fan
// records) is verified and drawn; a missing or edited record draws nothing; the unavailable state says so.
(async function () {
  'use strict';
  var log = [], failures = [], DIR = 'fixtures/fig05-uncertainty/';
  var violations = [];
  document.addEventListener('securitypolicyviolation', function (e) { violations.push(e.violatedDirective + ' ' + e.blockedURI); });
  function check(cond, msg) { log.push((cond ? 'ok   ' : 'FAIL ') + msg); if (!cond) { failures.push(msg); } document.getElementById('cert-log').textContent = log.join('\n'); }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  async function text(name) { return (await fetch(DIR + name)).text(); }
  function file(name, t) { return { name: name, bytes: new TextEncoder().encode(t) }; }
  function q7(s, p) { var i = (s.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return lo === hi ? s[lo] : s[lo] * (hi - i) + s[hi] * (i - lo); }
  var api = window.SCLabFigureBundleRenderer, F = window.SCLabPlotlyPreviewFIG02A;
  try {
    if (document.readyState === 'loading') { await new Promise(function (r) { document.addEventListener('DOMContentLoaded', r); }); }
    check(window.Plotly && window.Plotly.version === '3.3.1' && !!api && !!F, 'vendored plotly.js 3.3.1 and Lab modules loaded');
    var names = ['chart.bundle.json', 'chart.figure.json', 'chart.trend.bands.json', 'chart.ensemble.fan.json'];
    var texts = await Promise.all(names.map(text));
    var pkg = names.map(function (n, k) { return file(n, texts[k]); });

    // 1. Verified render of the released package.
    var out = document.getElementById('main-out').appendChild(document.createElement('div'));
    out.id = 'chart';
    var res = await api.render(out, pkg);
    var slot = out.querySelector('[data-view-state]');
    check(res.state === 'rendered' && slot && slot.getAttribute('data-view-state') === 'rendered-plotly', 'package verified and drawn (rendered-plotly)');
    await wait(400);
    var gd = slot.querySelector('.js-plotly-plot');
    var fillsDrawn = gd ? Array.prototype.filter.call(gd.querySelectorAll('.scatterlayer path.js-fill'), function (p) { var d = p.getAttribute('d'); return d && d.length > 10; }).length : 0;
    check(fillsDrawn === 5, 'five uncertainty areas drawn (2 bands, 3 fan levels): ' + fillsDrawn);
    var legend = gd ? Array.prototype.map.call(gd.querySelectorAll('.legendtext'), function (t) { return t.textContent; }).join(' | ') : '';
    check(/90% prediction band \(Student t, df 10; computed by the Workspace runtime\)/.test(legend) && /90% confidence band/.test(legend), 'legend names level, distribution, df and origin of both bands');
    check(/central 95% of 40 ensemble members/.test(legend) && /central 50% of 40/.test(legend) && /ensemble median/.test(legend), 'legend names fan levels, member count and median');
    var us = out.querySelector('[data-uncertainty-status]');
    check(us && us.getAttribute('data-uncertainty-status') === 'runtime-computed' && /computed by the Workspace runtime/.test(us.textContent), 'card states uncertainty was computed by the runtime: ' + (us && us.textContent));
    check(/90% confidence band/.test(out.textContent) || legend.length > 0, 'band labels are text, not images');
    var alt = JSON.parse(texts[0]).rendering.altText;
    check(out.innerHTML.indexOf(alt.slice(0, 40)) >= 0, 'alternative text present for the chart');

    // 2. Independent recomputation in the browser: fan bounds and band centring, from the drawn figure data.
    var src = JSON.parse(await text('SOURCE.json'));
    var members = src.inputs.ensemble.members.map(function (m) { return m.values; }), n = src.inputs.ensemble.steps.length;
    var fig = JSON.parse(texts[1]), worst = 0;
    fig.data.filter(function (t) { return t.meta && t.meta.scUncertainty && t.meta.scUncertainty.role === 'fan'; }).forEach(function (t) {
      var lv = t.meta.scUncertainty.level;
      for (var j = 0; j < n; j++) {
        var col = members.map(function (m) { return m[j]; }).sort(function (a, b) { return a - b; });
        worst = Math.max(worst, Math.abs(t.y[2 * n - 1 - j] - q7(col, (1 - lv) / 2)), Math.abs(t.y[j] - q7(col, (1 + lv) / 2)));
      }
    });
    check(worst < 1e-9, 'fan bounds equal independent type-7 quantiles of the synthetic ensemble (max error ' + worst + ')');

    // 3. A package without the fan record: nothing drawn.
    var o2 = document.getElementById('main-out').appendChild(document.createElement('div'));
    var r2 = await api.render(o2, pkg.slice(0, 3));
    check(r2.state === 'refused' && !o2.querySelector('.js-plotly-plot') && /was not supplied, so nothing is drawn/.test(o2.textContent), 'missing runtime record: refused, no chart drawn');
    o2.remove();
    // 4. An edited band record (wider): not the bound record, nothing drawn.
    var edited = texts[2].replace(/("points": \[\s*\[\s*[-0-9.e]+,\s*[-0-9.e]+,\s*)([-0-9.e]+)/, function (m, a, lo) { return a + String(Number(lo) - 1); });
    var o3 = document.getElementById('main-out').appendChild(document.createElement('div'));
    var r3 = await api.render(o3, [pkg[0], pkg[1], file('chart.trend.bands.json', edited), pkg[3]]);
    check(edited !== texts[2] && r3.state === 'refused' && !o3.querySelector('.js-plotly-plot'), 'edited band record: refused, no chart drawn');
    o3.remove();
    // 5. A figure whose ribbon was widened (spec and bundle hashes recomputed): refused.
    var wfig = JSON.parse(texts[1]);
    var wb = wfig.data.filter(function (t) { return t.meta && t.meta.scUncertainty && t.meta.scUncertainty.role === 'band'; })[0];
    wb.y[0] = wb.y[0] + 0.5;
    var wText = JSON.stringify(wfig), wBundle = JSON.parse(texts[0]);
    wBundle.artifacts[0].sha256 = wBundle.rendering.visualizationSpecSha256 = await F.sha256Hex(F.canonical(F.parseLexical(wText)));
    var o4 = document.getElementById('main-out').appendChild(document.createElement('div'));
    var r4 = await api.render(o4, [file('b.json', JSON.stringify(wBundle)), file('f.json', wText), pkg[2], pkg[3]]);
    check(r4.state === 'refused' && /does not equal the runtime record/.test(o4.textContent) && !o4.querySelector('.js-plotly-plot'), 'widened ribbon refused: ' + o4.textContent.slice(0, 120));
    o4.remove();

    // 6. Unavailable: the FIG-02A preview draws the panels with the notice and no area.
    var pv = document.getElementById('main-out').appendChild(document.createElement('div'));
    pv.id = 'unavailable';
    var naText = await text('chart-unavailable.compile.json');
    var nv = await F.verify(naText, window.Plotly.version);
    var naLayout = Object.assign({}, nv.response.plotly.figure.layout, { width: undefined, autosize: true });
    await window.Plotly.newPlot(pv, nv.response.plotly.figure.data, naLayout, { staticPlot: true });
    await wait(300);
    var notes = Array.prototype.filter.call(pv.querySelectorAll('.annotation-text'), function (t) { return /^Uncertainty unavailable/.test(t.textContent); }).length;
    var naFills = Array.prototype.filter.call(pv.querySelectorAll('.scatterlayer path.js-fill'), function (p) { var d = p.getAttribute('d'); return d && d.length > 10; }).length;
    check(notes === 2 && naFills === 0, 'unavailable state: two notices, no area drawn (' + notes + ', ' + naFills + ')');

    var res2 = performance.getEntriesByType('resource').map(function (e) { return e.name; });
    var foreign = res2.filter(function (u) { return !(u.indexOf(location.origin) === 0 || /^(blob|data):/.test(u)); });
    check(!foreign.length, 'every resource is same-origin: ' + foreign.join(' '));
    check(!violations.length, 'no CSP violations: ' + violations.join('; '));
  } catch (e) {
    check(false, 'exception: ' + (e && e.stack || JSON.stringify(e)));
  }
  document.body.setAttribute('data-cert', failures.length ? 'fail' : 'pass');
}());
