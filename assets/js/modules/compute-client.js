(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};

  function config() {
    const root = w.SCLabConfig || {};
    return Object.assign({ enabled:false, configured:false, timeoutSeconds:20, endpoints:{} }, root.compute || {});
  }

  function errorMessage(body, response) {
    if (body?.error?.message) return body.error.message;
    if (typeof body?.detail === 'string') return body.detail;
    if (Array.isArray(body?.detail)) return body.detail.map(item => item.msg || JSON.stringify(item)).join('; ');
    if (body?.message) return body.message;
    return `Compute request failed with HTTP ${response.status}.`;
  }

  async function request(url, options = {}) {
    if (!url) throw new Error('The WordPress compute endpoint is not configured.');
    const controller = new AbortController();
    const timeout = Math.max(5000, Math.min(65000, Number(options.timeoutMs || (config().timeoutSeconds * 1000 + 5000))));
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(url, {
        method: options.method || 'GET',
        credentials: 'same-origin',
        headers: Object.assign({
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-WP-Nonce': w.SCLabConfig?.nonce || ''
        }, options.headers || {}),
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
        signal: controller.signal
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        const error = new Error(errorMessage(body, response));
        error.status = response.status;
        error.code = body?.error?.code || body?.code || 'compute_request_failed';
        error.details = body?.error?.details || body?.data || null;
        throw error;
      }
      return body;
    } catch (error) {
      if (error?.name === 'AbortError') {
        const timeoutError = new Error('The compute request timed out.');
        timeoutError.code = 'compute_timeout';
        throw timeoutError;
      }
      throw error;
    } finally {
      clearTimeout(timer);
    }
  }

  function endpoint(name) { return config().endpoints?.[name] || ''; }
  function jobUrl(jobId) { return `${endpoint('jobs').replace(/\/$/, '')}/${encodeURIComponent(jobId)}`; }

  const api = {
    config,
    isConfigured() { const c = config(); return !!(c.enabled && c.configured && endpoint('status')); },
    status() { return request(endpoint('status')); },
    languages() { return request(endpoint('languages')); },
    methods() { return request(endpoint('methods')); },
    execute(payload) { return request(endpoint('execute'), { method:'POST', body:payload }); },
    compare(payload) { return request(endpoint('compare'), { method:'POST', body:payload, timeoutMs:65000 }); },
    queueExecute(payload) { return request(endpoint('jobs'), { method:'POST', body:{ operation:'execute', execute:payload } }); },
    queueCompare(payload) { return request(endpoint('jobs'), { method:'POST', body:{ operation:'compare', compare:payload }, timeoutMs:65000 }); },
    job(jobId) { return request(jobUrl(jobId)); },
    cancel(jobId) { return request(jobUrl(jobId), { method:'DELETE' }); },
    async poll(jobId, options = {}) {
      const interval = Math.max(500, Number(options.intervalMs || 1200));
      const deadline = Date.now() + Math.max(5000, Number(options.timeoutMs || 180000));
      while (Date.now() < deadline) {
        const record = await api.job(jobId);
        options.onUpdate?.(record);
        const state = String(record.status || record.state || '').toLowerCase();
        if (['finished','completed','succeeded','failed','cancelled','canceled'].includes(state)) return record;
        await new Promise(resolve => setTimeout(resolve, interval));
      }
      const error = new Error('The execution job did not finish before the polling timeout.');
      error.code = 'job_poll_timeout';
      throw error;
    }
  };

  Lab.ComputeClient = api;
})(window);
