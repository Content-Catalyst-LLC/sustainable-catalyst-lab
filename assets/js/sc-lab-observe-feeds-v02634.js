(function (W, D) {
  'use strict';

  if (W.__SCLabObserveFeedsV02634) return;
  W.__SCLabObserveFeedsV02634 = true;

  const VERSION = '0.26.3.4';
  const MODULES = new Set(['space-telescopes', 'marine-biology']);
  const state = { module: null, ready: false, loading: false, mode: null, records: [], errors: [], lastQuery: null };
  let activeController = null;

  const cfg = () => W.SCLabObserveFeedsConfigV02634 || {};
  const esc = (value) => String(value ?? '').replace(/[&<>'"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const key = (value) => String(value || '').trim().toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '');
  const canonical = (value) => {
    const module = key(value);
    if (['astronomy-observations', 'space-observations', 'space'].includes(module)) return 'space-telescopes';
    if (['marine', 'marine-science', 'ocean-biology'].includes(module)) return 'marine-biology';
    return module;
  };

  function app() { return D.querySelector('.sc-lab-app'); }
  function recordError(scope, error) {
    const item = { at: new Date().toISOString(), scope, message: error instanceof Error ? error.message : String(error || 'Unknown error') };
    state.errors.push(item);
    if (state.errors.length > 30) state.errors.shift();
    W.SCLabRuntimeV02631?.recordError?.(`observe-v02634:${scope}`, error);
    return item;
  }

  function projectStore(root, Lab) {
    if (root?._scLabProjects?.add) return root._scLabProjects;
    if (Lab.Projects?.add) return Lab.Projects;
    if (typeof Lab.Projects === 'function') {
      try { root._scLabProjects = new Lab.Projects(); return root._scLabProjects; }
      catch (error) { recordError('projects', error); }
    }
    return null;
  }

  function elements(root, module) {
    const marine = module === 'marine-biology';
    return {
      marine,
      button: root.querySelector(marine ? '[data-marine-load]' : '[data-space-load]'),
      target: root.querySelector(marine ? '[data-marine-results]' : '[data-space-results]'),
      summary: root.querySelector(marine ? '[data-marine-summary]' : '[data-space-summary]'),
      chart: marine ? root.querySelector('[data-marine-chart]') : null,
      dataset: root.querySelector(marine ? '[data-marine-dataset]' : '[data-space-dataset]'),
      query: root.querySelector(marine ? '[data-marine-query]' : '[data-space-query]'),
      telescope: marine ? null : root.querySelector('[data-space-telescope]'),
      limit: root.querySelector(marine ? '[data-marine-limit]' : '[data-space-limit]')
    };
  }

  function ensureStatus(root, el) {
    let status = root.querySelector('[data-observe-status-v02634]');
    if (status) return status;
    status = D.createElement('div');
    status.className = 'sc-lab-observe-status-v02634';
    status.dataset.observeStatusV02634 = '';
    status.dataset.state = 'idle';
    status.innerHTML = '<strong data-observe-status-title>Preparing source</strong><span data-observe-status-copy>The Lab is connecting to the scientific source.</span><span class="sc-lab-observe-mode-v02634" data-observe-status-mode>pending</span><div class="sc-lab-observe-actions"><button type="button" class="sc-lab-button" data-observe-retry-v02634>Retry</button><button type="button" class="sc-lab-button" data-observe-health-v02634>Source status</button></div>';
    (el.summary?.parentNode || el.target?.parentNode || root).insertBefore(status, el.target || null);
    return status;
  }

  function setStatus(status, stateName, title, copy, mode) {
    if (!status) return;
    status.dataset.state = stateName;
    const titleNode = status.querySelector('[data-observe-status-title]');
    const copyNode = status.querySelector('[data-observe-status-copy]');
    const modeNode = status.querySelector('[data-observe-status-mode]');
    if (titleNode) titleNode.textContent = title;
    if (copyNode) copyNode.textContent = copy;
    if (modeNode) modeNode.textContent = mode || stateName;
  }

  function skeleton(target) {
    if (!target) return;
    target.innerHTML = '<div class="sc-lab-observe-skeleton-v02634" aria-label="Loading scientific records"><span></span><span></span><span></span></div>';
  }

  function timeoutFetch(url, options = {}, timeoutMs = 18000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    return fetch(url, { ...options, signal: controller.signal }).finally(() => clearTimeout(timer));
  }

  function params(root, module, el) {
    const limit = Math.max(1, Math.min(30, Number(el.limit?.value || (module === 'marine-biology' ? 25 : 18))));
    if (module === 'marine-biology') {
      const q = String(el.query?.value || 'Cetacea').trim() || 'Cetacea';
      return { source: 'obis-marine', q, limit, proxyParams: { scientificName: q, limit }, directUrl: `https://api.obis.org/v3/occurrence?${new URLSearchParams({ scientificname: q, size: String(limit) })}` };
    }
    const telescope = String(el.telescope?.value || 'all');
    const topic = String(el.query?.value || 'nebula galaxy exoplanet').trim();
    const q = `${telescope === 'all' ? '' : `${telescope} `}${topic}`.trim() || 'JWST Hubble nebula galaxy';
    return { source: 'nasa-space-telescopes', q, limit, proxyParams: { q, limit }, directUrl: `https://images-api.nasa.gov/search?${new URLSearchParams({ q, media_type: 'image' })}` };
  }

  function normalizeNasa(data, limit) {
    return (data?.collection?.items || []).slice(0, limit).map((item, index) => {
      const meta = item?.data?.[0] || {};
      const link = item?.links?.[0]?.href || '';
      const id = meta.nasa_id || `nasa-${index}`;
      return {
        id, source: 'NASA Image and Video Library', domain: 'Astronomy', type: 'space_telescope_release',
        title: meta.title || 'Space telescope release', summary: meta.description_508 || meta.description || '',
        observedAt: meta.date_created || null, retrievedAt: new Date().toISOString(),
        url: `https://images.nasa.gov/details/${encodeURIComponent(id)}`, thumbnail: link,
        keywords: meta.keywords || [], freshness: 'browser-direct', license: 'NASA media usage guidelines'
      };
    });
  }

  function normalizeObis(data, limit) {
    const rows = data?.results || data?.data || [];
    return rows.slice(0, limit).map((row, index) => {
      const name = row.scientificName || row.species || 'Marine occurrence';
      const location = [row.locality, row.country].filter(Boolean).join(', ');
      return {
        id: row.id || row.occurrenceID || `obis-${index}`, source: 'OBIS', domain: 'Marine biology', type: 'marine_occurrence',
        title: name, summary: location || 'Marine biodiversity occurrence', observedAt: row.eventDate || row.date_mid || null,
        retrievedAt: new Date().toISOString(), url: 'https://obis.org/', freshness: 'browser-direct', license: 'Record-level OBIS dataset terms',
        location: { longitude: row.decimalLongitude ?? null, latitude: row.decimalLatitude ?? null, depthM: row.minimumDepthInMeters ?? row.depth ?? null },
        taxonomy: { scientificName: name, kingdom: row.kingdom || null, phylum: row.phylum || null }
      };
    });
  }

  async function viaWordPress(query, force) {
    const base = cfg().proxyBase || `${W.SCLabConfig?.restBase || '/wp-json/sc-lab/v1/'}observe/v02634/source/`;
    const url = `${base}${encodeURIComponent(query.source)}?${new URLSearchParams({ ...query.proxyParams, force: force ? '1' : '0' })}`;
    const response = await timeoutFetch(url, { headers: { 'X-WP-Nonce': cfg().nonce || W.SCLabConfig?.nonce || '' } }, Number(cfg().timeoutMs || 18000));
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.message || `WordPress feed proxy returned HTTP ${response.status}`);
    return body;
  }

  async function viaBrowser(query) {
    const response = await timeoutFetch(query.directUrl, { headers: { Accept: 'application/json' } }, Number(cfg().timeoutMs || 18000));
    if (!response.ok) throw new Error(`Direct source returned HTTP ${response.status}`);
    const body = await response.json();
    const records = query.source === 'obis-marine' ? normalizeObis(body, query.limit) : normalizeNasa(body, query.limit);
    return { ok: true, mode: records.length ? 'browser-direct' : 'browser-direct-empty', records, message: records.length ? `${records.length} records loaded directly from the source.` : 'The direct source returned zero records.', sourceUrl: query.directUrl };
  }

  function fallbackRender(target, records) {
    target.innerHTML = '';
    records.forEach((record) => {
      const card = D.createElement('article');
      card.className = 'sc-lab-feed-card';
      const image = record.thumbnail ? `<img loading="lazy" src="${esc(record.thumbnail)}" alt="">` : '';
      card.innerHTML = `${image}<div class="sc-lab-feed-card-body"><span class="sc-lab-feed-domain">${esc(record.domain || 'Science')}</span><h4>${esc(record.title || 'Scientific record')}</h4><p>${esc(String(record.summary || '').slice(0, 330))}</p><div class="sc-lab-feed-meta">${esc(record.source || 'Source')} · ${esc(record.observedAt || 'Date unavailable')}</div></div><div class="sc-lab-card-actions">${record.url ? `<a class="sc-lab-button" href="${esc(record.url)}" target="_blank" rel="noopener">Open source</a>` : ''}</div>`;
      target.appendChild(card);
    });
  }

  function renderRecords(root, Lab, projects, el, records) {
    if (Lab.Feeds?.render) Lab.Feeds.render(el.target, records, projects, root);
    else fallbackRender(el.target, records);
  }

  function renderMarineChart(el, Lab, records) {
    if (!el.chart) return;
    const points = Lab.Observations?.depthSeries ? Lab.Observations.depthSeries(records) : records.map((record) => ({ depth: Number(record.location?.depthM) })).filter((point) => Number.isFinite(point.depth));
    if (!points.length) { el.chart.innerHTML = '<div class="sc-lab-data-note">Records loaded, but no depth values were supplied.</div>'; return; }
    const max = Math.max(...points.map((point) => Number(point.depth) || 0), 1);
    el.chart.innerHTML = `<svg viewBox="0 0 700 140" role="img" aria-label="Marine occurrence depth series"><line x1="35" y1="15" x2="35" y2="120" stroke="#89949d"/><line x1="35" y1="120" x2="680" y2="120" stroke="#89949d"/>${points.map((point, index) => `<circle cx="${35 + index * (640 / Math.max(points.length - 1, 1))}" cy="${15 + (Number(point.depth) || 0) / max * 100}" r="3" fill="#7d1128"/>`).join('')}<text x="5" y="18" font-size="10">0 m</text><text x="2" y="120" font-size="10">${max.toFixed(0)} m</text></svg>`;
  }

  function renderUnavailable(el, query, proxyError, directError) {
    const sourceName = query.source === 'obis-marine' ? 'OBIS' : 'NASA Image and Video Library';
    el.target.innerHTML = `<div class="sc-lab-observe-empty-v02634"><strong>${esc(sourceName)} could not be reached.</strong><p>The panel is working, but neither the WordPress proxy nor the browser-direct fallback returned data.</p><p><strong>WordPress:</strong> ${esc(proxyError || 'No diagnostic supplied.')}</p><p><strong>Browser:</strong> ${esc(directError || 'No diagnostic supplied.')}</p><p><a class="sc-lab-button" href="${esc(query.directUrl)}" target="_blank" rel="noopener">Open source endpoint</a></p></div>`;
  }

  function summaryText(module, records, Lab) {
    if (module === 'marine-biology') {
      const taxa = Lab.Observations?.taxonSummary ? Lab.Observations.taxonSummary(records).slice(0, 6) : [];
      return `${records.length} occurrences${taxa.length ? ` · ${taxa.map(([name, count]) => `${name}: ${count}`).join(' · ')}` : ''}`;
    }
    const groups = {};
    records.forEach((record) => {
      const telescope = Lab.Observations?.telescope ? Lab.Observations.telescope(record) : 'Space observation';
      groups[telescope] = (groups[telescope] || 0) + 1;
    });
    return Object.entries(groups).map(([name, count]) => `${name}: ${count}`).join(' · ') || `${records.length} observations`;
  }

  async function run(force = false) {
    if (!activeController || state.loading) return [];
    const { root, module, Lab, projects, el, status } = activeController;
    const query = params(root, module, el);
    state.loading = true;
    state.lastQuery = query;
    state.records = [];
    el.button.disabled = true;
    if (el.dataset) el.dataset.disabled = true;
    skeleton(el.target);
    setStatus(status, 'loading', module === 'marine-biology' ? 'Loading OBIS observations' : 'Loading NASA observations', 'Trying the WordPress scientific-feed proxy first.', 'wordpress');
    if (el.summary) el.summary.textContent = 'Loading live scientific records…';

    let payload = null;
    let proxyError = '';
    let directError = '';
    try {
      const proxyPayload = await viaWordPress(query, force);
      if (proxyPayload.ok && Array.isArray(proxyPayload.records) && proxyPayload.records.length) {
        payload = proxyPayload;
      } else {
        proxyError = proxyPayload.message || 'The WordPress proxy returned no records.';
        payload = proxyPayload;
      }
    } catch (error) {
      proxyError = error.message || String(error);
      recordError('wordpress-proxy', error);
    }
    if (!Array.isArray(payload?.records) || !payload.records.length) {
      setStatus(status, 'loading', 'Trying browser-direct source access', proxyError || 'The WordPress proxy returned no records.', 'direct');
      try { payload = await viaBrowser(query); }
      catch (direct) { directError = direct.message || String(direct); recordError('browser-direct', direct); }
    }

    const records = Array.isArray(payload?.records) ? payload.records : [];
    if (records.length) {
      state.records = records;
      state.mode = payload.mode || 'live';
      renderRecords(root, Lab, projects, el, records);
      if (module === 'marine-biology') renderMarineChart(el, Lab, records);
      if (el.summary) el.summary.textContent = summaryText(module, records, Lab);
      if (el.dataset) el.dataset.disabled = false;
      setStatus(status, 'ready', 'Scientific records loaded', payload.message || `${records.length} records returned.`, state.mode);
    } else if (payload?.ok && payload.mode?.includes('empty')) {
      state.mode = payload.mode;
      el.target.innerHTML = `<div class="sc-lab-observe-empty-v02634"><strong>No records matched this query.</strong><p>Try a broader taxon, telescope, target, or topic.</p><p><a class="sc-lab-button" href="${esc(query.directUrl)}" target="_blank" rel="noopener">Open source query</a></p></div>`;
      if (el.summary) el.summary.textContent = 'The source returned zero matching records.';
      setStatus(status, 'ready', 'No matching records', 'The connector responded successfully, but the query returned no data.', 'empty');
    } else {
      state.mode = 'unavailable';
      renderUnavailable(el, query, proxyError || payload?.message, directError);
      if (el.summary) el.summary.textContent = 'Scientific source unavailable. See the diagnostic below.';
      setStatus(status, 'error', 'Scientific source unavailable', 'The panel is active and can be retried; diagnostics are shown below.', 'error');
    }

    state.loading = false;
    state.ready = true;
    el.button.disabled = false;
    return state.records;
  }

  async function showHealth(status) {
    setStatus(status, 'loading', 'Checking connector health', 'Reading the current WordPress connector state.', 'health');
    try {
      const response = await timeoutFetch(cfg().healthUrl || `${W.SCLabConfig?.restBase || '/wp-json/sc-lab/v1/'}observe/v02634/health`, {}, 10000);
      const body = await response.json();
      const source = state.module === 'marine-biology' ? body.sources?.['obis-marine'] : body.sources?.['nasa-space-telescopes'];
      setStatus(status, source?.status === 'error' ? 'error' : 'ready', 'Connector health', `${source?.status || 'unknown'} · ${source?.message || 'No connector message.'}`, 'health');
    } catch (error) {
      setStatus(status, 'error', 'Health check failed', error.message || String(error), 'health');
    }
  }

  function saveDataset() {
    if (!activeController || !state.records.length) return;
    const { module, Lab, projects, el } = activeController;
    if (!projects?.add || !Lab.Datasets?.fromRecords) return;
    const title = module === 'marine-biology' ? 'Marine biodiversity occurrences' : 'Space telescope observations';
    const source = module === 'marine-biology' ? 'OBIS' : 'NASA Image and Video Library';
    const dataset = Lab.Datasets.fromRecords(state.records, { title, source });
    projects.add('datasets', dataset, `Dataset saved: ${title}`);
    if (el.summary) el.summary.textContent = `${state.records.length} records saved as a project dataset.`;
  }

  function mount() {
    const root = app();
    if (!root) return false;
    const module = canonical(root.dataset.initialModule || root.dataset.activeModule || 'overview');
    if (!MODULES.has(module)) return false;
    if (root.dataset.scLabObserveFeedsReady === VERSION) return true;

    const Lab = W.SCLab || {};
    const el = elements(root, module);
    if (!el.button || !el.target) {
      recordError('markup', new Error(`Required ${module} controls were not found.`));
      return false;
    }
    const projects = projectStore(root, Lab);
    const status = ensureStatus(root, el);
    activeController = { root, module, Lab, projects, el, status };
    state.module = module;

    el.button.addEventListener('click', () => run(true));
    el.dataset?.addEventListener('click', saveDataset);
    status.querySelector('[data-observe-retry-v02634]')?.addEventListener('click', () => run(true));
    status.querySelector('[data-observe-health-v02634]')?.addEventListener('click', () => showHealth(status));
    root.dataset.scLabObserveFeedsReady = VERSION;
    root.dataset.scLabObserveController = VERSION;
    state.ready = true;
    setStatus(status, 'loading', 'Preparing scientific source', 'An initial live query will run automatically.', 'starting');
    setTimeout(() => run(false), 0);
    D.dispatchEvent(new CustomEvent('sc-lab:observe-feed-ready', { detail: { module, version: VERSION } }));
    return true;
  }

  function status() {
    return { version: VERSION, module: state.module, ready: state.ready, loading: state.loading, mode: state.mode, recordCount: state.records.length, lastQuery: state.lastQuery, errors: state.errors.slice(-10) };
  }

  W.SCLabObserveFeedsV02634 = { VERSION, canonical, normalizeNasa, normalizeObis, mount, run, status };
  W.SCLab = W.SCLab || {};
  W.SCLab.ObserveFeedsV02634 = W.SCLabObserveFeedsV02634;
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', mount, { once: true });
  else mount();
  D.addEventListener('sc-lab:module-opened', mount);
})(window, document);
