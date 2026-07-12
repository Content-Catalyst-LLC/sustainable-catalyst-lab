(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const MC = Lab.MethodContracts;
  const Compute = Lab.ComputeClient;
  const PREF_KEY = 'scLabCodeSwitcherPrefsV093';
  const LEGACY_PREF_KEY = 'scLabCodeSwitcherPrefsV092';
  const DEFAULT_WORKERS = ['python','rust','c','cpp','fortran','go','javascript','typescript'];
  const esc = value => U.esc(value);
  const slug = value => String(value || 'method').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'method';

  function readPrefs() {
    const defaults = { language:'rust', methodId:'kinetic', executionMode:'local', requestMode:'direct', workers:DEFAULT_WORKERS };
    try {
      const current = localStorage.getItem(PREF_KEY);
      const legacy = localStorage.getItem(LEGACY_PREF_KEY);
      const parsed = JSON.parse(current || legacy || '{}');
      if (!current && legacy) localStorage.setItem(PREF_KEY, JSON.stringify(Object.assign({}, defaults, parsed)));
      return Object.assign({}, defaults, parsed, { workers:Array.isArray(parsed.workers) ? parsed.workers : DEFAULT_WORKERS });
    } catch (_) { return defaults; }
  }
  function savePrefs(value) { localStorage.setItem(PREF_KEY, JSON.stringify(value)); }

  function methodOptions() {
    const groups = {};
    MC.contracts.forEach(contract => (groups[contract.domain] = groups[contract.domain] || []).push(contract));
    return Object.entries(groups).sort().map(([domain, rows]) => `<optgroup label="${esc(domain)}">${rows.map(contract => `<option value="${esc(contract.id)}">${esc(contract.name)}</option>`).join('')}</optgroup>`).join('');
  }
  function languageOptions() { return Object.entries(MC.languages).map(([id, language]) => `<option value="${esc(id)}">${esc(language.label)}</option>`).join(''); }
  function fieldsHtml(contract, values = {}) { return contract.inputs.map(field => `<label>${esc(field.label)}${field.unit ? ` <small>${esc(field.unit)}</small>` : ''}<input type="number" step="any" value="${esc(values[field.id] ?? field.default)}" data-code-input="${esc(field.id)}"></label>`).join(''); }
  function collect(root) { const output = {}; root.querySelectorAll('[data-code-input]').forEach(element => { output[element.dataset.codeInput] = Number(element.value); }); return output; }
  function finiteInputs(inputs) { return Object.values(inputs).every(value => Number.isFinite(value)); }

  function localComparisonHtml(report) {
    if (!report) return '';
    return `<div class="sc-lab-code-validation ${report.passed ? 'is-passed' : 'is-failed'}"><strong>${report.passed ? 'PORTABLE CONTRACT MATCH' : 'REVIEW DIFFERENCES'}</strong><table><thead><tr><th>Output</th><th>Contract</th><th>Current JS</th><th>|Δ|</th><th>Status</th></tr></thead><tbody>${report.rows.map(row => `<tr><td>${esc(row.output)}</td><td>${esc(String(row.portable))}</td><td>${row.runtime === null ? '—' : esc(String(row.runtime))}</td><td>${row.absoluteDifference === null ? '—' : esc(String(row.absoluteDifference))}</td><td>${row.passed === null ? 'NO ADAPTER' : row.passed ? 'PASS' : 'FAIL'}</td></tr>`).join('')}</tbody></table></div>`;
  }

  function remoteComparisonHtml(report) {
    if (!report?.executions) return '<div class="sc-lab-data-note">No cross-language comparison is available.</div>';
    const rows = report.executions.map(item => {
      const validation = item.validation || {};
      const error = item.error?.message || '';
      return `<tr><td>${esc(MC.languages[item.language]?.label || item.language)}</td><td>${esc(item.status || 'UNKNOWN')}</td><td>${item.compileTimeMs == null ? '—' : esc(String(item.compileTimeMs))}</td><td>${item.executionTimeMs == null ? '—' : esc(String(item.executionTimeMs))}</td><td>${validation.passed === undefined ? '—' : validation.passed ? 'PASS' : 'FAIL'}</td><td>${esc(item.runtimeVersion || error || '—')}</td></tr>`;
    }).join('');
    return `<div class="sc-lab-code-validation ${report.passed ? 'is-passed' : 'is-failed'}"><strong>${report.passed ? 'CROSS-LANGUAGE PARITY PASSED' : 'CROSS-LANGUAGE REVIEW REQUIRED'}</strong><table><thead><tr><th>Language</th><th>State</th><th>Compile ms</th><th>Run ms</th><th>Parity</th><th>Runtime / error</th></tr></thead><tbody>${rows}</tbody></table><p class="sc-lab-data-note">Successful workers: ${esc(String(report.successfulCount || 0))} · Fingerprint: ${esc(report.comparisonFingerprint || 'not returned')}</p></div>`;
  }

  function workerHtml(registry, selected) {
    return Object.entries(MC.languages).map(([id, language]) => {
      const state = registry?.[id] || { available:false, executionMode:'source-only' };
      const checked = selected.includes(id) && state.available;
      const disabled = !state.available;
      return `<label class="sc-lab-worker-option ${state.available ? 'is-available' : 'is-unavailable'}"><input type="checkbox" value="${esc(id)}" data-code-worker ${checked ? 'checked' : ''} ${disabled ? 'disabled' : ''}><span><strong>${esc(language.label)}</strong><small>${state.available ? `AVAILABLE · ${esc(state.runtimeVersion || 'runtime detected')}` : esc(state.executionMode || 'source only')}</small></span></label>`;
    }).join('');
  }

  function normalizeBackendStatus(status, languages) {
    const registry = languages?.languages || {};
    return {
      ok: !!status?.ok,
      configured: status?.configured !== false,
      version: status?.version || 'unknown',
      queueMode: status?.queueMode || 'unknown',
      availableLanguages: status?.availableLanguages || Object.entries(registry).filter(([, value]) => value.available).map(([id]) => id),
      registry
    };
  }

  function init(root, projects) {
    const panel = root.querySelector('[data-lab-module="code-studio"]');
    if (!panel) return;
    const method = panel.querySelector('[data-code-method]');
    const language = panel.querySelector('[data-code-language]');
    const executionMode = panel.querySelector('[data-code-execution-mode]');
    const requestMode = panel.querySelector('[data-code-request-mode]');
    const fields = panel.querySelector('[data-code-fields]');
    const source = panel.querySelector('[data-code-source]');
    const meta = panel.querySelector('[data-code-meta]');
    const result = panel.querySelector('[data-code-result]');
    const validation = panel.querySelector('[data-code-validation]');
    const status = panel.querySelector('[data-code-status]');
    const backendStatus = panel.querySelector('[data-code-backend-status]');
    const backendIndicator = panel.querySelector('[data-code-backend-indicator]');
    const workers = panel.querySelector('[data-code-worker-languages]');
    const workerComparison = panel.querySelector('[data-code-worker-comparison]');
    const jobOutput = panel.querySelector('[data-code-job]');
    const cancelButton = panel.querySelector('[data-code-cancel-job]');
    const prefs = readPrefs();
    let backend = { ok:false, configured:Compute?.isConfigured?.() || false, version:'unknown', queueMode:'unknown', availableLanguages:[], registry:{} };
    let activeJobId = null;
    let lastExecution = null;
    let lastComparison = null;

    method.innerHTML = methodOptions();
    language.innerHTML = languageOptions();
    method.value = MC.byId[prefs.methodId] ? prefs.methodId : MC.contracts[0].id;
    language.value = MC.languages[prefs.language] ? prefs.language : 'rust';
    executionMode.value = prefs.executionMode === 'render' ? 'render' : 'local';
    requestMode.value = prefs.requestMode === 'queued' ? 'queued' : 'direct';

    function currentPrefs() {
      return {
        methodId:method.value,
        language:language.value,
        executionMode:executionMode.value,
        requestMode:requestMode.value,
        workers:[...panel.querySelectorAll('[data-code-worker]:checked')].map(element => element.value)
      };
    }

    function updateModeAvailability() {
      const selected = language.value;
      const available = !!backend.registry?.[selected]?.available || backend.availableLanguages.includes(selected);
      const remoteRequested = executionMode.value === 'render';
      panel.querySelector('[data-code-run]').textContent = remoteRequested ? (requestMode.value === 'queued' ? 'Queue native execution' : 'Run native worker') : 'Run portable contract';
      if (remoteRequested && !backend.ok) status.textContent = 'Render mode selected, but the compute dispatcher is unavailable. Run will use the documented local fallback.';
      else if (remoteRequested && !available) status.textContent = `${MC.languages[selected].label} source is available, but this runtime is not available on the connected worker.`;
      else if (remoteRequested) status.textContent = `${MC.byId[method.value].id} · ${MC.languages[selected].label} · native execution through the protected WordPress proxy.`;
      else status.textContent = `${MC.byId[method.value].id} · ${MC.languages[selected].label} source view · deterministic portable-contract execution in this browser.`;
      savePrefs(currentPrefs());
    }

    function render(resetInputs = true) {
      const contract = MC.byId[method.value];
      if (!contract) return;
      if (resetInputs) fields.innerHTML = fieldsHtml(contract);
      source.value = MC.generate(contract.id, language.value);
      meta.textContent = JSON.stringify({
        schema:contract.schema,
        id:contract.id,
        version:contract.version,
        domain:contract.domain,
        equation:contract.equation,
        inputs:contract.inputs,
        outputs:contract.outputs.map(({ expression, ...rest }) => rest),
        assumptions:contract.assumptions,
        language:language.value,
        localMode:MC.languages[language.value].mode,
        remoteRuntime:backend.registry?.[language.value] || null,
        dispatcherVersion:backend.version
      }, null, 2);
      result.textContent = 'Run the selected engine to calculate the current inputs.';
      validation.innerHTML = '';
      updateModeAvailability();
    }

    function showBackend() {
      const available = backend.availableLanguages.map(id => MC.languages[id]?.label || id).join(', ') || 'none reported';
      backendStatus.textContent = backend.ok
        ? `Online · API ${backend.version} · ${backend.queueMode} · workers: ${available}`
        : backend.configured ? 'Configured but unavailable. Local portable execution remains active.' : 'Not configured. Add the Render service URL and API key in WordPress settings.';
      backendIndicator.textContent = backend.ok ? 'Render online' : 'Local fallback';
      backendIndicator.classList.toggle('is-ready', backend.ok);
      workers.innerHTML = workerHtml(backend.registry, currentPrefs().workers.length ? currentPrefs().workers : prefs.workers);
      updateModeAvailability();
    }

    async function refreshBackend(showToast = false) {
      backendStatus.textContent = 'Checking the WordPress compute proxy…';
      try {
        if (!Compute?.isConfigured?.()) {
          backend = Object.assign(backend, { ok:false, configured:false, registry:{}, availableLanguages:[] });
          showBackend();
          return backend;
        }
        const [health, languageData] = await Promise.all([Compute.status(), Compute.languages()]);
        backend = normalizeBackendStatus(health, languageData);
        showBackend();
        if (showToast) U.toast(root, 'Compute dispatcher status refreshed.');
      } catch (error) {
        backend = Object.assign(backend, { ok:false, configured:true, registry:{}, availableLanguages:[] });
        backendStatus.textContent = `Unavailable · ${error.message}`;
        showBackend();
        if (showToast) U.toast(root, 'Compute dispatcher is unavailable; local fallback remains active.');
      }
      return backend;
    }

    function saveExecution(record, activity) {
      projects.add('codeExecutions', record, activity);
      if (record.runtimeVersion) projects.add('runtimeRecords', { type:'runtime', language:record.language, runtimeVersion:record.runtimeVersion, environment:record.environment || null, executionId:record.outputFingerprint || null }, `Runtime recorded: ${record.language}`);
      if (record.compileTimeMs != null) projects.add('compilerRecords', { type:'compiler-run', language:record.language, runtimeVersion:record.runtimeVersion, compileTimeMs:record.compileTimeMs, sourceFingerprint:record.sourceFingerprint }, `Compiler record saved: ${record.language}`);
    }

    function localExecution(inputs, fallbackReason = null) {
      const outputs = MC.evaluate(method.value, inputs);
      const record = {
        schema:'sc-lab-execution/1.0', serviceVersion:'0.9.3', methodId:method.value,
        methodVersion:MC.byId[method.value].version, language:'javascript', runtime:'browser-portable-contract',
        status:'VALIDATED', requestedLanguage:language.value, inputs, outputs,
        inputFingerprint:U.fingerprint({ methodId:method.value, inputs }), outputFingerprint:U.fingerprint(outputs),
        warnings:fallbackReason ? [`Render fallback: ${fallbackReason}`] : [], executedAt:new Date().toISOString()
      };
      lastExecution = record;
      result.textContent = JSON.stringify(record, null, 2);
      saveExecution(record, `Local code execution: ${method.value}`);
      return record;
    }

    async function remoteExecution(inputs) {
      const payload = { methodId:method.value, language:language.value, inputs, timeoutSeconds:Math.min(20, Number(w.SCLabConfig?.compute?.timeoutSeconds || 8)), includeSource:false };
      if (!backend.ok) return localExecution(inputs, 'compute dispatcher unavailable');
      if (!backend.registry?.[language.value]?.available && !backend.availableLanguages.includes(language.value)) throw new Error(`${MC.languages[language.value].label} is not available on the connected worker.`);
      result.textContent = requestMode.value === 'queued' ? 'Submitting execution job…' : 'Running curated implementation…';
      if (requestMode.value === 'queued') {
        const queued = await Compute.queueExecute(payload);
        activeJobId = queued.jobId;
        cancelButton.disabled = false;
        jobOutput.textContent = JSON.stringify(queued, null, 2);
        projects.add('executionJobs', queued, `Execution job queued: ${method.value} · ${language.value}`);
        const finalJob = await Compute.poll(activeJobId, { onUpdate:record => { jobOutput.textContent = JSON.stringify(record, null, 2); } });
        activeJobId = null; cancelButton.disabled = true;
        if (String(finalJob.status).toLowerCase() !== 'finished' || !finalJob.result) throw new Error(finalJob.error?.message || `Job ended with status ${finalJob.status}.`);
        lastExecution = finalJob.result;
      } else {
        lastExecution = await Compute.execute(payload);
      }
      result.textContent = JSON.stringify(lastExecution, null, 2);
      saveExecution(lastExecution, `Native code execution: ${method.value} · ${language.value}`);
      U.toast(root, `${MC.languages[language.value].label} execution completed.`);
      return lastExecution;
    }

    async function runSelected() {
      const inputs = collect(panel);
      if (!finiteInputs(inputs)) { result.textContent = 'Error: Every input must be a finite number.'; return; }
      validation.innerHTML = '';
      try {
        if (executionMode.value === 'render') await remoteExecution(inputs);
        else localExecution(inputs);
      } catch (error) {
        result.textContent = JSON.stringify({ status:'FAILED', code:error.code || 'execution_failed', message:error.message, details:error.details || null }, null, 2);
        U.toast(root, 'Execution did not complete.');
      }
    }

    async function compareWorkers() {
      const selected = [...panel.querySelectorAll('[data-code-worker]:checked')].map(element => element.value).slice(0, 8);
      if (!selected.length) { workerComparison.innerHTML = '<div class="sc-lab-data-note">Select at least one available worker.</div>'; return; }
      if (!backend.ok) { workerComparison.innerHTML = '<div class="sc-lab-data-note">The Render dispatcher is unavailable. Cross-language comparison requires the backend.</div>'; return; }
      const payload = { methodId:method.value, languages:selected, inputs:collect(panel), timeoutSeconds:Math.min(20, Number(w.SCLabConfig?.compute?.timeoutSeconds || 8)), includeSource:false, absoluteTolerance:1e-10, relativeTolerance:1e-9 };
      workerComparison.innerHTML = '<div class="sc-lab-data-note">Executing and comparing curated implementations…</div>';
      try {
        if (requestMode.value === 'queued') {
          const queued = await Compute.queueCompare(payload);
          activeJobId = queued.jobId; cancelButton.disabled = false; jobOutput.textContent = JSON.stringify(queued, null, 2);
          projects.add('executionJobs', queued, `Language comparison queued: ${method.value}`);
          const finalJob = await Compute.poll(activeJobId, { timeoutMs:240000, onUpdate:record => { jobOutput.textContent = JSON.stringify(record, null, 2); } });
          activeJobId = null; cancelButton.disabled = true;
          if (String(finalJob.status).toLowerCase() !== 'finished' || !finalJob.result) throw new Error(finalJob.error?.message || `Job ended with status ${finalJob.status}.`);
          lastComparison = finalJob.result;
        } else lastComparison = await Compute.compare(payload);
        workerComparison.innerHTML = remoteComparisonHtml(lastComparison);
        projects.add('languageComparisons', lastComparison, `Languages compared: ${method.value}`);
        projects.add('crossLanguageValidationRecords', { type:'cross-language-validation', methodId:method.value, passed:lastComparison.passed, comparisonFingerprint:lastComparison.comparisonFingerprint, languages:selected, report:lastComparison }, `Cross-language validation: ${method.value}`);
        U.toast(root, 'Cross-language comparison completed.');
      } catch (error) {
        workerComparison.innerHTML = `<div class="sc-lab-code-validation is-failed"><strong>COMPARISON FAILED</strong><p>${esc(error.message)}</p></div>`;
      }
      savePrefs(currentPrefs());
    }

    method.addEventListener('change', () => render(true));
    language.addEventListener('change', () => render(false));
    executionMode.addEventListener('change', updateModeAvailability);
    requestMode.addEventListener('change', updateModeAvailability);
    panel.querySelector('[data-code-render]').addEventListener('click', () => render(false));
    panel.querySelector('[data-code-run]').addEventListener('click', runSelected);
    panel.querySelector('[data-code-backend-refresh]').addEventListener('click', () => refreshBackend(true));
    panel.querySelector('[data-code-compare-workers]').addEventListener('click', compareWorkers);
    workers.addEventListener('change', () => savePrefs(currentPrefs()));
    cancelButton.addEventListener('click', async () => {
      if (!activeJobId) return;
      try { const record = await Compute.cancel(activeJobId); jobOutput.textContent = JSON.stringify(record, null, 2); projects.add('executionJobs', record, `Execution job cancellation requested: ${activeJobId}`); }
      catch (error) { jobOutput.textContent = `Cancellation failed: ${error.message}`; }
      activeJobId = null; cancelButton.disabled = true;
    });

    panel.querySelector('[data-code-validate]').addEventListener('click', () => {
      try {
        const report = MC.validateAgainstRuntime(method.value, collect(panel));
        validation.innerHTML = localComparisonHtml(report);
        projects.add('implementationComparisons', { type:'portable-contract-validation', methodId:method.value, report }, `Method contract validated: ${method.value}`);
      } catch (error) { validation.innerHTML = `<div class="sc-lab-data-note">${esc(error.message)}</div>`; }
    });
    panel.querySelector('[data-code-download]').addEventListener('click', () => { const contract = MC.byId[method.value], selected = MC.languages[language.value]; U.download(`${slug(contract.id)}.${selected.extension}`, source.value, 'text/plain'); });
    panel.querySelector('[data-code-contract]').addEventListener('click', () => { const contract = MC.byId[method.value]; U.download(`${slug(contract.id)}-method.json`, JSON.stringify(contract, null, 2), 'application/json'); });
    panel.querySelector('[data-code-notebook]').addEventListener('click', () => { const contract = MC.byId[method.value]; U.download(`${slug(contract.id)}.ipynb`, JSON.stringify(MC.notebook(contract.id), null, 2), 'application/x-ipynb+json'); });
    panel.querySelector('[data-code-catalog]').addEventListener('click', () => U.download('sustainable-catalyst-lab-method-catalog-v0.9.3.json', JSON.stringify(MC.manifest(), null, 2), 'application/json'));
    panel.querySelector('[data-code-save]').addEventListener('click', () => {
      const contract = MC.byId[method.value];
      projects.add('methodContracts', { type:'portable-method-contract', methodId:contract.id, contract }, `Method contract saved: ${contract.id}`);
      projects.add('codeArtifacts', { type:'generated-source', methodId:contract.id, language:language.value, filename:`${slug(contract.id)}.${MC.languages[language.value].extension}`, source:source.value }, `Code artifact saved: ${contract.id} · ${language.value}`);
      if (lastExecution) projects.add('benchmarkRuns', { type:'saved-execution-snapshot', methodId:contract.id, execution:lastExecution }, `Execution snapshot saved: ${contract.id}`);
      U.toast(root, 'Method contract, source, and current execution snapshot saved.');
    });
    panel.querySelector('[data-code-copy]').addEventListener('click', async () => { try { await navigator.clipboard.writeText(source.value); U.toast(root, 'Code copied.'); } catch (_) { source.select(); document.execCommand('copy'); U.toast(root, 'Code copied.'); } });
    root.addEventListener('sc-lab:open-code', event => { const id = event.detail?.methodId; method.value = MC.byId[id] ? id : method.value; root.querySelector('[data-lab-module-button="code-studio"]')?.click(); setTimeout(() => render(true), 20); });

    render(true);
    refreshBackend(false);
  }

  Lab.CodeSwitcher = { init };
})(window);
