(function (W, D) {
  'use strict';
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.27.0';
  const METHOD_IDS = new Set([
    'numerics.root_scalar_polynomial',
    'numerics.adaptive_quadrature_polynomial',
    'numerics.interpolation',
    'numerics.ode_first_order',
    'numerics.eigen_analysis',
    'optimization.scalar_bounded',
    'optimization.linear_program',
    'signal.fft_spectrum',
    'uncertainty.monte_carlo_propagation',
    'uncertainty.bootstrap_mean_interval',
    'sensitivity.local_finite_difference',
    'simulation.parameter_sweep'
  ]);
  const state = {
    ready: false,
    mounted: false,
    methodCount: 0,
    method: null,
    execution: null,
    jobId: null,
    lastResult: null,
    lastError: null,
    registrySource: null,
    events: []
  };
  let methods = [];
  let activeJobId = null;
  let destroyed = false;

  function panel() { return D.querySelector('[data-lab-module="numerical-methods"]'); }
  function el(name) { return panel()?.querySelector(`[data-numerical-${name}]`) || null; }
  function esc(value) { return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[ch])); }
  function event(name, detail = {}) {
    state.events.push({ at: new Date().toISOString(), name, detail });
    if (state.events.length > 80) state.events.shift();
  }
  function announce(message, tone = 'info') {
    const target = el('status');
    if (target) { target.textContent = message; target.dataset.tone = tone; }
    event('status', { message, tone });
  }
  function setBusy(busy) {
    panel()?.classList.toggle('is-computing', !!busy);
    const run = el('run'); if (run) run.disabled = !!busy;
    const cancel = el('cancel'); if (cancel) cancel.disabled = !busy || !activeJobId;
    const select = el('method'); if (select) select.disabled = !!busy;
  }
  function config() { return W.SCLabConfig || {}; }
  function endpoint(name) { return config()?.compute?.endpoints?.[name] || ''; }
  async function fetchJSON(url) {
    if (!url) throw new Error('The numerical-method catalog endpoint is not configured.');
    const response = await fetch(url, { credentials:'same-origin', headers:{'Accept':'application/json','X-WP-Nonce':config().nonce || ''} });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body?.message || body?.detail || `HTTP ${response.status}`);
    return body;
  }
  function safeJSON(value, fallback = {}) {
    try { return JSON.parse(String(value || '')); }
    catch (error) { throw new Error(`Invalid JSON: ${error.message}`); }
  }
  function pretty(value) { return JSON.stringify(value, null, 2); }
  function currentMethod() { return methods.find(row => row.id === el('method')?.value) || methods[0] || null; }
  function domainLabel(value) { return String(value || 'other').replace(/-/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase()); }
  function mergeMethods(localRows, remoteRows) {
    const local = new Map((localRows || []).filter(row => METHOD_IDS.has(row.id)).map(row => [row.id, row]));
    const remote = new Map((remoteRows || []).filter(row => METHOD_IDS.has(row.id)).map(row => [row.id, row]));
    return [...METHOD_IDS].map(id => Object.assign({}, local.get(id) || {}, remote.get(id) || {}, {
      id,
      example_inputs: remote.get(id)?.example_inputs || local.get(id)?.example_inputs || {},
      example_parameters: remote.get(id)?.example_parameters || local.get(id)?.example_parameters || {}
    })).filter(row => row.title).sort((a,b) => String(a.domain).localeCompare(String(b.domain)) || String(a.title).localeCompare(String(b.title)));
  }
  async function loadRegistry() {
    const localUrl = config()?.numerical?.catalogUrl || `${String(config().restBase || '').replace(/\/?$/, '/')}numerical/v0270/catalog`;
    const local = await fetchJSON(localUrl).catch(error => { event('local-catalog-error', { message:error.message }); return { methods:[] }; });
    let remote = { methods:[] };
    if (Lab.ComputeClient?.isConfigured?.()) {
      try { remote = await Lab.ComputeClient.coreMethods(); state.registrySource = 'python-core'; }
      catch (error) { event('remote-registry-error', { message:error.message }); state.registrySource = 'wordpress-catalog'; }
    } else state.registrySource = 'wordpress-catalog';
    methods = mergeMethods(local.methods, remote.methods);
    state.methodCount = methods.length;
    if (!methods.length) throw new Error('No governed numerical methods are available.');
    renderMethodSelector();
    state.ready = true;
    event('registry-ready', { count:methods.length, source:state.registrySource });
  }
  function renderMethodSelector() {
    const select = el('method');
    if (!select) return;
    const grouped = new Map();
    methods.forEach(method => {
      const domain = domainLabel(method.domain);
      if (!grouped.has(domain)) grouped.set(domain, []);
      grouped.get(domain).push(method);
    });
    select.innerHTML = [...grouped.entries()].map(([domain, rows]) => `<optgroup label="${esc(domain)}">${rows.map(row => `<option value="${esc(row.id)}">${esc(row.title)}</option>`).join('')}</optgroup>`).join('');
    select.value = methods.find(row => row.id === 'numerics.ode_first_order')?.id || methods[0].id;
    methodChanged();
  }
  function methodChanged() {
    const method = currentMethod();
    if (!method) return;
    state.method = method.id;
    const title = el('method-title'); if (title) title.textContent = method.title;
    const id = el('method-id'); if (id) id.textContent = `${method.id} · v${method.version || '1.0.0'}`;
    const description = el('description'); if (description) description.textContent = method.description || '';
    const assumptions = el('assumptions');
    if (assumptions) assumptions.innerHTML = (method.assumptions || []).map(value => `<li>${esc(value)}</li>`).join('') || '<li>No additional assumptions were declared.</li>';
    const packages = el('packages'); if (packages) packages.textContent = (method.packages || []).join(', ') || 'Python standard library';
    const cost = el('cost'); if (cost) cost.textContent = `${method.estimated_cost || 'light'} · ${method.recommended_execution || 'synchronous'}`;
    loadExample(false);
  }
  function loadExample(announceLoad = true) {
    const method = currentMethod(); if (!method) return;
    const inputs = el('inputs'); if (inputs) inputs.value = pretty(method.example_inputs || {});
    const parameters = el('parameters'); if (parameters) parameters.value = pretty(method.example_parameters || {});
    const execution = el('execution');
    if (execution) execution.value = method.recommended_execution === 'queued' ? 'automatic' : 'automatic';
    if (announceLoad) announce(`Loaded the governed example for ${method.title}.`, 'ready');
  }
  function payload() {
    const method = currentMethod();
    if (!method) throw new Error('Choose a numerical method.');
    const inputs = safeJSON(el('inputs')?.value || '{}');
    const parameters = safeJSON(el('parameters')?.value || '{}');
    if (!inputs || Array.isArray(inputs) || typeof inputs !== 'object') throw new Error('Inputs JSON must be an object.');
    if (!parameters || Array.isArray(parameters) || typeof parameters !== 'object') throw new Error('Parameters JSON must be an object.');
    const seedText = String(el('seed')?.value || '').trim();
    const request = {
      method: method.id,
      version: method.version || '1.0.0',
      inputs,
      parameters,
      units: {},
      requested_outputs: ['summary','values','table','chart'],
      project_id: panel()?.closest('.sc-lab-app')?._scLabProjects?.get?.()?.id || null
    };
    if (seedText !== '') {
      const seed = Number(seedText);
      if (!Number.isInteger(seed)) throw new Error('Random seed must be an integer.');
      request.random_seed = seed;
    }
    return request;
  }
  function executionMode(method) {
    const chosen = el('execution')?.value || 'automatic';
    if (chosen !== 'automatic') return chosen;
    return method.recommended_execution === 'queued' || method.estimated_cost === 'heavy' ? 'queued' : 'synchronous';
  }
  function summarize(value, depth = 0) {
    if (depth > 2) return '…';
    if (Array.isArray(value)) {
      if (value.length <= 8) return value.map(item => summarize(item, depth + 1));
      return { count:value.length, first:value.slice(0,3).map(item => summarize(item, depth+1)), last:value.slice(-2).map(item => summarize(item, depth+1)) };
    }
    if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).slice(0,30).map(([key,item]) => [key, summarize(item, depth + 1)]));
    return value;
  }
  function plotData(outputs) {
    if (Array.isArray(outputs?.time) && Array.isArray(outputs?.values)) return { x:outputs.time, y:outputs.values, xLabel:'Time', yLabel:'Value' };
    if (Array.isArray(outputs?.frequencyHz) && Array.isArray(outputs?.amplitude)) return { x:outputs.frequencyHz, y:outputs.amplitude, xLabel:'Frequency (Hz)', yLabel:'Amplitude' };
    if (Array.isArray(outputs?.query) && Array.isArray(outputs?.values)) return { x:outputs.query, y:outputs.values, xLabel:'Query', yLabel:'Interpolated value' };
    if (Array.isArray(outputs?.rows) && outputs.rows.every(row => Number.isFinite(Number(row.parameterValue)) && Number.isFinite(Number(row.output)))) return { x:outputs.rows.map(row=>row.parameterValue), y:outputs.rows.map(row=>row.output), xLabel:'Parameter', yLabel:'Output' };
    return null;
  }
  function renderPlot(outputs) {
    const target = el('plot'); if (!target) return;
    const data = plotData(outputs);
    if (!data || data.x.length < 2 || data.x.length !== data.y.length) { target.innerHTML = '<div class="sc-lab-data-note">This method returns structured numerical output without a line-series visualization.</div>'; return; }
    const pairs = data.x.map((x,index)=>[Number(x),Number(data.y[index])]).filter(pair=>pair.every(Number.isFinite));
    if (pairs.length < 2) { target.innerHTML = '<div class="sc-lab-data-note">No finite series was available for visualization.</div>'; return; }
    const sampled = pairs.length > 500 ? pairs.filter((_,index)=>index % Math.ceil(pairs.length/500) === 0 || index === pairs.length-1) : pairs;
    const xs=sampled.map(row=>row[0]), ys=sampled.map(row=>row[1]);
    const xmin=Math.min(...xs), xmax=Math.max(...xs), ymin=Math.min(...ys), ymax=Math.max(...ys);
    const Wd=760,Hd=300,L=58,R=18,T=18,B=46;
    const sx=x=>L+(x-xmin)/(xmax-xmin || 1)*(Wd-L-R);
    const sy=y=>Hd-B-(y-ymin)/(ymax-ymin || 1)*(Hd-T-B);
    const points=sampled.map(row=>`${sx(row[0]).toFixed(2)},${sy(row[1]).toFixed(2)}`).join(' ');
    target.innerHTML = `<svg viewBox="0 0 ${Wd} ${Hd}" role="img" aria-labelledby="sc-num-plot-title sc-num-plot-desc"><title id="sc-num-plot-title">Numerical method result plot</title><desc id="sc-num-plot-desc">${esc(data.yLabel)} plotted against ${esc(data.xLabel)} for ${sampled.length} sampled points.</desc><rect width="${Wd}" height="${Hd}" fill="currentColor" opacity="0.03"/><line x1="${L}" y1="${Hd-B}" x2="${Wd-R}" y2="${Hd-B}" class="sc-num-axis"/><line x1="${L}" y1="${T}" x2="${L}" y2="${Hd-B}" class="sc-num-axis"/><polyline points="${points}" class="sc-num-series"/><text x="${(L+Wd-R)/2}" y="${Hd-12}" text-anchor="middle">${esc(data.xLabel)}</text><text x="16" y="${(T+Hd-B)/2}" text-anchor="middle" transform="rotate(-90 16 ${(T+Hd-B)/2})">${esc(data.yLabel)}</text><text x="${L}" y="${Hd-B+18}">${esc(xmin.toPrecision(4))}</text><text x="${Wd-R}" y="${Hd-B+18}" text-anchor="end">${esc(xmax.toPrecision(4))}</text><text x="${L-8}" y="${T+4}" text-anchor="end">${esc(ymax.toPrecision(4))}</text><text x="${L-8}" y="${Hd-B}" text-anchor="end">${esc(ymin.toPrecision(4))}</text></svg>`;
  }
  function renderResult(result, metadata = {}) {
    state.lastResult = result;
    state.lastError = null;
    const outputs = result?.outputs || result?.result?.outputs || result?.result || {};
    const summary = el('summary');
    if (summary) summary.innerHTML = `<strong>${esc(result?.summary || metadata.summary || 'Numerical method completed.')}</strong><span>${esc(state.method || '')}</span><small>${esc(metadata.execution || state.execution || 'synchronous')} · ${esc(new Date().toLocaleString())}</small>`;
    const output = el('output'); if (output) output.textContent = pretty(summarize(outputs));
    const raw = el('raw'); if (raw) raw.textContent = pretty(result);
    const provenance = el('provenance'); if (provenance) provenance.textContent = pretty(result?.provenance || result?.result?.provenance || {});
    renderPlot(outputs);
    const save = el('save'); if (save) save.disabled = false;
    const exportButton = el('export'); if (exportButton) exportButton.disabled = false;
    D.dispatchEvent(new CustomEvent('sc-lab:numerical-result', { detail:{ method:state.method, result, version:VERSION } }));
  }
  function jobResult(record) {
    if (record?.result?.method && record.result.outputs) return record.result;
    if (record?.result?.result?.method) return record.result.result;
    return record?.result || record;
  }
  async function run() {
    if (!Lab.ComputeClient?.isConfigured?.()) {
      announce('Python Compute Core is not enabled or configured. Configure it in Lab settings before running numerical methods.', 'error');
      return;
    }
    const method = currentMethod();
    try {
      const request = payload();
      const mode = executionMode(method);
      state.execution = mode;
      state.lastError = null;
      activeJobId = null;
      setBusy(true);
      announce(mode === 'queued' ? `Queueing ${method.title}…` : `Running ${method.title}…`, 'loading');
      let result;
      if (mode === 'queued') {
        const serialized = JSON.stringify(request);
        let requestHash = 2166136261;
        for (let index = 0; index < serialized.length; index += 1) {
          requestHash ^= serialized.charCodeAt(index);
          requestHash = Math.imul(requestHash, 16777619);
        }
        const idempotency = `v0270:${method.id}:${(requestHash >>> 0).toString(16).padStart(8, '0')}`;
        const submitted = await Lab.ComputeClient.queueCore(request, { idempotencyKey:idempotency });
        activeJobId = submitted.jobId || submitted.id;
        state.jobId = activeJobId;
        if (!activeJobId) throw new Error('The compute queue did not return a job identifier.');
        announce(`Queued ${method.title}. Waiting for worker…`, 'loading');
        const final = await Lab.ComputeClient.poll(activeJobId, {
          timeoutMs: Math.max(180000, Number(config()?.compute?.jobTimeoutSeconds || 120) * 1000 + 30000),
          onUpdate(record) {
            if (destroyed) return;
            const progress = Number(record.progress || 0);
            announce(`${method.title}: ${record.progressMessage || record.status || 'running'}${progress ? ` (${progress}%)` : ''}`, 'loading');
          }
        });
        const status = String(final.status || '').toLowerCase();
        if (!['completed','finished','succeeded'].includes(status)) throw new Error(final?.error?.message || `Queued method ended with status ${status}.`);
        result = jobResult(final);
      } else result = await Lab.ComputeClient.runCore(request);
      renderResult(result, { execution:mode });
      announce(`${method.title} completed with reproducible provenance.`, 'ready');
      event('run-complete', { method:method.id, mode, jobId:activeJobId });
    } catch (error) {
      state.lastError = { message:error.message, code:error.code || null, at:new Date().toISOString() };
      const output = el('output'); if (output) output.textContent = `Error: ${error.message}`;
      announce(error.message || 'Numerical method failed.', 'error');
      event('run-error', state.lastError);
    } finally {
      activeJobId = null;
      setBusy(false);
    }
  }
  async function cancel() {
    if (!activeJobId || !Lab.ComputeClient?.cancel) return;
    try { await Lab.ComputeClient.cancel(activeJobId); announce('Cancellation requested for the queued numerical job.', 'warning'); event('job-cancelled', { jobId:activeJobId }); }
    catch (error) { announce(`Could not cancel the job: ${error.message}`, 'error'); }
  }
  function save() {
    if (!state.lastResult) return;
    const projects = panel()?.closest('.sc-lab-app')?._scLabProjects;
    if (!projects?.add) { announce('The active project store is unavailable.', 'error'); return; }
    const method = currentMethod();
    const record = { type:'numerical-method-run', methodId:method.id, methodTitle:method.title, execution:state.execution, jobId:state.jobId, request:payload(), response:state.lastResult, recordedAt:new Date().toISOString(), runtimeVersion:VERSION };
    projects.add('calculations', record, `Numerical method saved: ${method.title}`);
    announce(`${method.title} was saved to the active project.`, 'ready');
  }
  function download() {
    if (!state.lastResult) return;
    const method = currentMethod();
    const bundle = { schema:'sc-lab-numerical-method-result/1.0', version:VERSION, method:method.id, execution:state.execution, jobId:state.jobId, exportedAt:new Date().toISOString(), result:state.lastResult };
    if (Lab.util?.download) Lab.util.download(`${method.id.replace(/[^a-z0-9]+/gi,'-')}-result.json`, pretty(bundle), 'application/json');
    else {
      const blob = new Blob([pretty(bundle)], {type:'application/json'}); const link=D.createElement('a'); link.href=URL.createObjectURL(blob); link.download='numerical-method-result.json'; link.click(); setTimeout(()=>URL.revokeObjectURL(link.href),1000);
    }
  }
  function bind() {
    const root = panel(); if (!root || root.dataset.scNumericalMounted === '1') return;
    root.dataset.scNumericalMounted = '1';
    state.mounted = true;
    el('method')?.addEventListener('change', methodChanged);
    el('example')?.addEventListener('click', () => loadExample(true));
    el('run')?.addEventListener('click', run);
    el('cancel')?.addEventListener('click', cancel);
    el('save')?.addEventListener('click', save);
    el('export')?.addEventListener('click', download);
    D.addEventListener('sc-lab:module-unmounting', () => { destroyed = true; }, { once:true });
    loadRegistry().then(() => {
      announce(Lab.ComputeClient?.isConfigured?.() ? `Numerical Methods Studio ready with ${methods.length} governed Python methods.` : `Numerical catalog loaded. Configure Python Compute Core to run the ${methods.length} methods.`, Lab.ComputeClient?.isConfigured?.() ? 'ready' : 'warning');
    }).catch(error => { state.lastError = {message:error.message,at:new Date().toISOString()}; announce(error.message, 'error'); });
  }
  function status() { return Object.assign({}, state, { methodCount:methods.length, activeJobId, backendConfigured:!!Lab.ComputeClient?.isConfigured?.() }); }
  Lab.NumericalMethodsStudio = { version:VERSION, init:bind, run, cancel, status, methods:() => methods.slice() };
  W.SCLabNumericalMethodsV0270 = { status, run, cancel, loadExample:() => loadExample(true) };
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', bind, {once:true}); else bind();
})(window, document);
