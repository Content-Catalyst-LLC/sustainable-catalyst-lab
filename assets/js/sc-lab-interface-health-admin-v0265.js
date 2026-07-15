(function () {
  'use strict';
  var cfg = window.SCLabInterfaceHealthAdminConfigV0265 || {};
  var root = document.querySelector('[data-sc-lab-interface-admin-v0265]');
  if (!root) { return; }
  var frame = root.querySelector('[data-interface-frame]');
  var shell = root.querySelector('[data-interface-frame-shell]');
  var summary = root.querySelector('[data-interface-summary]');
  var rows = root.querySelector('[data-interface-rows]');
  var raw = root.querySelector('[data-interface-json]');
  var server = root.querySelector('[data-interface-server]');
  var reports = [];
  var viewports = {
    phone: { label: 'Phone', width: 390, height: 844 },
    tablet: { label: 'Tablet', width: 768, height: 1024 },
    desktop: { label: 'Desktop', width: 1280, height: 800 }
  };
  function esc(value) { return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]; }); }
  function setSummary(value) { summary.textContent = value; }
  function request(url, options) { return fetch(url, options || {}).then(function (response) { if (!response.ok) { throw new Error('HTTP ' + response.status); } return response.json(); }); }
  function refreshServer() {
    server.innerHTML = '<p>Checking interface runtime files…</p>';
    return request(cfg.healthUrl).then(function (data) {
      server.innerHTML = '<div class="notice ' + (data.ok ? 'notice-success' : 'notice-error') + ' inline"><p><strong>Server interface runtime:</strong> ' + esc(data.ok ? 'ready' : 'incomplete') + ' · v' + esc(data.version) + ' · release ' + esc(data.release) + '</p></div>';
    }).catch(function (error) { server.innerHTML = '<div class="notice notice-error inline"><p>' + esc(error.message) + '</p></div>'; });
  }
  function render() {
    rows.innerHTML = '';
    reports.forEach(function (report) {
      if (!report.issues.length) {
        rows.insertAdjacentHTML('beforeend', '<tr><td>' + esc(report.viewportLabel) + '</td><td>Pass</td><td>Interface audit</td><td>No issues detected.</td></tr>');
        return;
      }
      report.issues.forEach(function (issue) {
        rows.insertAdjacentHTML('beforeend', '<tr><td>' + esc(report.viewportLabel) + '</td><td><strong>' + esc(issue.severity) + '</strong></td><td>' + esc(issue.check) + '</td><td>' + esc(issue.details) + '</td></tr>');
      });
    });
    var combined = { schema: 'sc-lab-interface-health/1.0', version: cfg.version, release: cfg.release, generatedAt: new Date().toISOString(), reports: reports };
    raw.textContent = JSON.stringify(combined, null, 2);
    return combined;
  }
  function run(name) {
    var viewport = viewports[name];
    if (!viewport) { return Promise.reject(new Error('Unknown viewport.')); }
    setSummary('Loading the Lab at ' + viewport.label.toLowerCase() + ' width…');
    shell.style.width = viewport.width + 'px';
    shell.style.height = Math.min(viewport.height, 760) + 'px';
    return new Promise(function (resolve, reject) {
      var timer = window.setTimeout(function () { reject(new Error('The Lab audit frame timed out.')); }, 25000);
      frame.onload = function () {
        window.setTimeout(function () {
          try {
            var api = frame.contentWindow.SCLabInterfaceV0265;
            if (!api || typeof api.audit !== 'function') { throw new Error('The v0.26.5 interface runtime did not load in the frame.'); }
            var result = api.audit();
            result.viewportLabel = viewport.label + ' ' + viewport.width + '×' + viewport.height;
            reports = reports.filter(function (item) { return item.viewportLabel !== result.viewportLabel; });
            reports.push(result);
            render();
            setSummary(result.viewportLabel + ': ' + result.summary.status + ' · ' + result.summary.errors + ' errors · ' + result.summary.warnings + ' warnings.');
            clearTimeout(timer); resolve(result);
          } catch (error) { clearTimeout(timer); reject(error); }
        }, 1400);
      };
      frame.src = cfg.labUrl + (cfg.labUrl.indexOf('?') === -1 ? '?' : '&') + 'sc_lab_module=overview&sc_lab_interface_audit=1&sc_lab_viewport=' + encodeURIComponent(name) + '&_=' + Date.now();
    });
  }
  function runAll() {
    reports = [];
    return ['phone','tablet','desktop'].reduce(function (promise, name) { return promise.then(function () { return run(name); }); }, Promise.resolve()).then(function () {
      var combined = render();
      return request(cfg.saveUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-WP-Nonce': cfg.nonce }, body: JSON.stringify(combined) });
    }).then(function () { setSummary('All viewport audits completed and the report was saved.'); });
  }
  function download() {
    var data = render();
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob); var link = document.createElement('a');
    link.href = url; link.download = 'sustainable-catalyst-lab-interface-health-v0265.json'; link.click();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  root.addEventListener('click', function (event) {
    var target = event.target.closest('button'); if (!target) { return; }
    var action = null;
    if (target.matches('[data-interface-run-phone]')) { action = run('phone'); }
    if (target.matches('[data-interface-run-tablet]')) { action = run('tablet'); }
    if (target.matches('[data-interface-run-desktop]')) { action = run('desktop'); }
    if (target.matches('[data-interface-run-all]')) { action = runAll(); }
    if (target.matches('[data-interface-export]')) { download(); return; }
    if (target.matches('[data-interface-refresh-server]')) { refreshServer(); return; }
    if (action && action.catch) { action.catch(function (error) { setSummary('Audit failed: ' + error.message); }); }
  });
  refreshServer();
}());
