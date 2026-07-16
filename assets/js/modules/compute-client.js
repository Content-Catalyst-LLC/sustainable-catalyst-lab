(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};

  function config() {
    const root = w.SCLabConfig || {};
    return Object.assign({ enabled:false, configured:false, timeoutSeconds:20, jobTimeoutSeconds:120, jobMaxAttempts:2, jobPollMs:1200, endpoints:{} }, root.compute || {});
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
  function withQuery(url, query = {}) {
    const target = new URL(url, window.location.href);
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') target.searchParams.set(key, String(value));
    });
    return target.toString();
  }

  const api = {
    config,
    isConfigured() { const c = config(); return !!(c.enabled && c.configured && endpoint('status')); },
    status() { return request(endpoint('status')); },
    capabilities() { return request(endpoint('capabilities')); },
    coreMethods() { return request(endpoint('coreMethods')); },
    runCore(payload) { return request(endpoint('coreRun'), { method:'POST', body:payload, timeoutMs:125000 }); },
    governanceHealth() { return request(endpoint('governanceHealth')); },
    governancePolicies() { return request(endpoint('governancePolicies')); },
    governanceRecommend(payload) { return request(endpoint('governanceRecommend'), { method:'POST', body:payload, timeoutMs:65000 }); },
    governanceCompare(payload) { return request(endpoint('governanceCompare'), { method:'POST', body:payload, timeoutMs:125000 }); },
    visualizationHealth() { return request(endpoint('visualizationHealth')); },
    visualizationProfiles() { return request(endpoint('visualizationProfiles')); },
    visualizationSpec(payload) { return request(endpoint('visualizationSpec'), { method:'POST', body:payload, timeoutMs:65000 }); },
    visualizationCsv(payload) { return request(endpoint('visualizationCsv'), { method:'POST', body:payload, timeoutMs:65000 }); },
    reproducibilityHealth() { return request(endpoint('reproducibilityHealth')); },
    reproducibilityEnvironment() { return request(endpoint('reproducibilityEnvironment')); },
    reproducibilityManifest(payload) { return request(endpoint('reproducibilityManifest'), { method:'POST', body:payload, timeoutMs:65000 }); },
    reproducibilityVerify(payload) { return request(endpoint('reproducibilityVerify'), { method:'POST', body:payload, timeoutMs:65000 }); },
    reproducibilityCompare(payload) { return request(endpoint('reproducibilityCompare'), { method:'POST', body:payload, timeoutMs:65000 }); },
    languages() { return request(endpoint('languages')); },
    methods() { return request(endpoint('methods')); },
    execute(payload) { return request(endpoint('execute'), { method:'POST', body:payload }); },
    compare(payload) { return request(endpoint('compare'), { method:'POST', body:payload, timeoutMs:65000 }); },
    validateReport(payload) { return request(endpoint('reportValidate'), { method:'POST', body:payload, timeoutMs:65000 }); },
    reportPdf(payload) { return request(endpoint('reportPdf'), { method:'POST', body:payload, timeoutMs:65000 }); },
    validateHandoff(packet) { return request(endpoint('handoffValidate'), { method:'POST', body:{ packet }, timeoutMs:65000 }); },
    queueExecute(payload, options = {}) { const c=config(); return request(endpoint('jobs'), { method:'POST', body:Object.assign({ operation:'execute', execute:payload, timeoutSeconds:c.jobTimeoutSeconds, maxAttempts:c.jobMaxAttempts }, options) }); },
    queueCompare(payload, options = {}) { const c=config(); return request(endpoint('jobs'), { method:'POST', body:Object.assign({ operation:'compare', compare:payload, timeoutSeconds:c.jobTimeoutSeconds, maxAttempts:c.jobMaxAttempts }, options), timeoutMs:65000 }); },
    queueCore(payload, options = {}) { const c=config(); return request(endpoint('jobs'), { method:'POST', body:Object.assign({ operation:'core_run', request:payload, timeoutSeconds:c.jobTimeoutSeconds, maxAttempts:c.jobMaxAttempts }, options) }); },
    listJobs(query = {}) { return request(withQuery(endpoint('jobs'), query)); },
    job(jobId) { return request(jobUrl(jobId)); },
    cancel(jobId) { return request(`${jobUrl(jobId)}/cancel`, { method:'POST', body:{} }); },
    retry(jobId) { return request(`${jobUrl(jobId)}/retry`, { method:'POST', body:{} }); },
    pause(jobId) { return request(`${jobUrl(jobId)}/pause`, { method:'POST', body:{} }); },
    resume(jobId) { return request(`${jobUrl(jobId)}/resume`, { method:'POST', body:{} }); },
    checkpoints(jobId, limit = 20) { return request(withQuery(`${jobUrl(jobId)}/checkpoints`, { limit })); },
    cacheStatus() { return request(endpoint('cacheStatus')); },
    purgeCache() { return request(endpoint('cachePurge'), { method:'DELETE' }); },
    queueStatus() { return request(endpoint('queueStatus')); },
    workers() { return request(endpoint('workers')); },
    benchmarks() { return request(endpoint('benchmarks')); },
    benchmark(benchmarkId) { return request(`${endpoint('benchmarks').replace(/\/$/, '')}/${encodeURIComponent(benchmarkId)}`); },
    runBenchmark(benchmarkId) { return request(endpoint('benchmarkRun'), { method:'POST', body:{ benchmarkId }, timeoutMs:125000 }); },
    runBenchmarkSuite(benchmarkIds = []) { return request(endpoint('benchmarkSuite'), { method:'POST', body:{ benchmarkIds }, timeoutMs:125000 }); },
    runBenchmarkConvergence(benchmarkId) { return request(endpoint('benchmarkConvergence'), { method:'POST', body:{ benchmarkId }, timeoutMs:125000 }); },
    async poll(jobId, options = {}) {
      const interval = Math.max(500, Number(options.intervalMs || config().jobPollMs || 1200));
      const deadline = Date.now() + Math.max(5000, Number(options.timeoutMs || 180000));
      while (Date.now() < deadline) {
        const record = await api.job(jobId);
        options.onUpdate?.(record);
        const state = String(record.status || record.state || '').toLowerCase();
        if (['finished','completed','succeeded','failed','cancelled','canceled','timed_out','paused'].includes(state)) return record;
        await new Promise(resolve => setTimeout(resolve, interval));
      }
      const error = new Error('The execution job did not finish before the polling timeout.');
      error.code = 'job_poll_timeout';
      throw error;
    }
  };

  Lab.ComputeClient = api;
})(window);
