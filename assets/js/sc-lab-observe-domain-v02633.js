(function (W, D) {
  'use strict';

  if (W.__SCLabObserveDomainV02633) return;
  W.__SCLabObserveDomainV02633 = true;

  const VERSION = '0.26.3.3';
  const MODULES = new Set(['scientific-feeds', 'climate-maps']);
  const state = { module: null, ready: false, errors: [], records: [] };

  function key(value) {
    return String(value || '').trim().toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '');
  }

  function canonical(value) {
    const module = key(value);
    if (module === 'astronomy-observations' || module === 'space-observations' || module === 'space') return 'space-telescopes';
    if (module === 'marine' || module === 'marine-science' || module === 'ocean-biology') return 'marine-biology';
    if (module === 'climate' || module === 'climate-map') return 'climate-maps';
    return module;
  }

  function owns(value) {
    return MODULES.has(canonical(value));
  }

  function app() {
    return D.querySelector('.sc-lab-app');
  }

  function projectStore(root, Lab) {
    if (root && root._scLabProjects && typeof root._scLabProjects.add === 'function') return root._scLabProjects;
    if (Lab.Projects && typeof Lab.Projects.add === 'function') return Lab.Projects;
    if (typeof Lab.Projects === 'function') {
      try {
        const store = new Lab.Projects();
        if (root) root._scLabProjects = store;
        return store;
      } catch (error) {
        recordError('projects', error);
      }
    }
    return null;
  }

  function recordError(scope, error) {
    const item = {
      at: new Date().toISOString(),
      scope: String(scope || 'observe'),
      message: error instanceof Error ? error.message : String(error || 'Unknown error')
    };
    state.errors.push(item);
    if (state.errors.length > 30) state.errors.shift();
    if (W.SCLabRuntimeV02631 && typeof W.SCLabRuntimeV02631.recordError === 'function') {
      W.SCLabRuntimeV02631.recordError(`observe:${item.scope}`, error);
    }
    return item;
  }

  function statusText(target, text, isError) {
    if (!target) return;
    target.textContent = text;
    target.dataset.scLabObserveState = isError ? 'error' : 'ready';
  }

  function saveDataset(Lab, projects, title, source, records) {
    if (!projects || !Lab.Datasets || typeof Lab.Datasets.fromRecords !== 'function') return null;
    const dataset = Lab.Datasets.fromRecords(records || [], { title, source });
    projects.add('datasets', dataset, `Dataset saved: ${title}`);
    return dataset;
  }

  function mountClimate(root, Lab, projects) {
    const image = root.querySelector('[data-climate-image]');
    const renderButton = root.querySelector('[data-climate-render]');
    const date = root.querySelector('[data-climate-date]');
    const layer = root.querySelector('[data-climate-layer]');
    const region = root.querySelector('[data-climate-region]');
    const loading = root.querySelector('[data-climate-loading]');
    const metadata = root.querySelector('[data-climate-metadata]');
    const readout = root.querySelector('[data-climate-readout]');

    if (!image || !renderButton || !date || !layer || !region) return false;
    if (!Lab.ClimateMap || typeof Lab.ClimateMap.render !== 'function') {
      statusText(readout, 'Climate map controller is unavailable. Reload after clearing cached Lab assets.', true);
      throw new Error('ClimateMap controller unavailable.');
    }

    if (!date.value) date.value = new Date(Date.now() - 86400000).toISOString().slice(0, 10);

    function render() {
      try {
        const source = Lab.ClimateMap.render(image, layer.value, date.value, region.value, loading);
        if (metadata) {
          const info = Lab.ClimateMap.layers?.[layer.value] || {};
          metadata.innerHTML = `<span>Layer: ${String(info.label || layer.value)}</span><span>Date: ${date.value}</span><span>Region: ${region.value}</span><span>Unit: ${String(info.unit || 'source-defined')}</span>`;
        }
        statusText(readout, 'Map request sent. Click the map to record a coordinate.', false);
        return source;
      } catch (error) {
        statusText(readout, `Climate map error: ${error.message}`, true);
        recordError('climate-render', error);
        return '';
      }
    }

    renderButton.addEventListener('click', render);
    root.querySelector('[data-climate-opacity]')?.addEventListener('input', (event) => {
      image.style.opacity = String(Number(event.target.value || 100) / 100);
    });
    image.addEventListener('click', (event) => {
      try {
        const point = Lab.ClimateMap.coordinate(event, image, region.value);
        statusText(readout, `Selected coordinate: ${point.latitude.toFixed(4)}, ${point.longitude.toFixed(4)}`, false);
        projects?.add?.('observations', {
          title: 'Climate map coordinate', source: 'NASA GIBS', location: point,
          layer: layer.value, date: date.value
        }, `Map coordinate observed: ${point.latitude.toFixed(3)}, ${point.longitude.toFixed(3)}`);
      } catch (error) {
        statusText(readout, `Coordinate error: ${error.message}`, true);
      }
    });
    root.querySelector('[data-climate-save]')?.addEventListener('click', () => {
      const url = render();
      projects?.add?.('mapViews', { title: 'NASA GIBS climate map', layer: layer.value, date: date.value, bbox: region.value, url }, `Climate map saved: ${layer.value}`);
      statusText(readout, 'Climate map state saved to the active project.', false);
    });
    root.querySelector('[data-climate-export]')?.addEventListener('click', () => {
      const record = { source: 'NASA GIBS', layer: layer.value, date: date.value, bbox: region.value, url: render() };
      if (Lab.util?.download) Lab.util.download('lab-climate-map.json', JSON.stringify(record, null, 2), 'application/json');
    });

    root.dataset.scLabObserveReady = VERSION;
    render();
    return true;
  }

  function mountFeed(root, Lab, projects, kind) {
    const isMarine = kind === 'marine-biology';
    const isSpace = kind === 'space-telescopes';
    const isBoard = kind === 'scientific-feeds';
    const button = root.querySelector(isMarine ? '[data-marine-load]' : isSpace ? '[data-space-load]' : '[data-feed-run]');
    const target = root.querySelector(isMarine ? '[data-marine-results]' : isSpace ? '[data-space-results]' : '[data-feed-results]');
    const summary = root.querySelector(isMarine ? '[data-marine-summary]' : isSpace ? '[data-space-summary]' : '[data-feed-status]');
    if (!button || !target) return false;

    if (!Lab.Feeds || typeof Lab.Feeds.load !== 'function' || typeof Lab.Feeds.render !== 'function') {
      statusText(summary, 'Scientific feed controller is unavailable. Reload after clearing cached Lab assets.', true);
      throw new Error('Feeds controller unavailable.');
    }

    let records = [];
    async function run() {
      statusText(summary, 'Loading scientific source…', false);
      try {
        let source;
        let query;
        let limit;
        if (isMarine) {
          source = 'obis-marine';
          query = root.querySelector('[data-marine-query]')?.value || 'Cetacea';
          limit = Number(root.querySelector('[data-marine-limit]')?.value || 25);
        } else if (isSpace) {
          source = 'nasa-space-telescopes';
          const telescope = root.querySelector('[data-space-telescope]')?.value || 'all';
          query = `${telescope === 'all' ? '' : `${telescope} `}${root.querySelector('[data-space-query]')?.value || ''}`.trim();
          limit = Number(root.querySelector('[data-space-limit]')?.value || 18);
        } else {
          source = root.querySelector('[data-feed-source]')?.value || 'all-science';
          query = root.querySelector('[data-feed-query]')?.value || '';
          limit = Number(root.querySelector('[data-feed-limit]')?.value || 12);
        }

        if (source === 'all-science' && Lab.Observations?.loadBoard) {
          records = await Lab.Observations.loadBoard();
        } else {
          const response = await Lab.Feeds.load(source, query, limit);
          records = Array.isArray(response?.records) ? response.records : [];
        }
        state.records = records;
        Lab.Feeds.render(target, records, projects, root);

        if (isMarine) {
          const taxa = Lab.Observations?.taxonSummary ? Lab.Observations.taxonSummary(records).slice(0, 6) : [];
          statusText(summary, `${records.length} occurrences${taxa.length ? ` · ${taxa.map(([name, count]) => `${name}: ${count}`).join(' · ')}` : ''}`, false);
          const datasetButton = root.querySelector('[data-marine-dataset]');
          if (datasetButton) datasetButton.disabled = !records.length;
          renderMarineChart(root, Lab, records);
        } else if (isSpace) {
          const groups = {};
          records.forEach((record) => {
            const telescope = Lab.Observations?.telescope ? Lab.Observations.telescope(record) : 'Space observation';
            groups[telescope] = (groups[telescope] || 0) + 1;
          });
          statusText(summary, Object.entries(groups).map(([name, count]) => `${name}: ${count}`).join(' · ') || 'No observations returned.', false);
          const datasetButton = root.querySelector('[data-space-dataset]');
          if (datasetButton) datasetButton.disabled = !records.length;
        } else {
          statusText(summary, `${records.length} records returned.`, false);
          const datasetButton = root.querySelector('[data-feed-to-dataset]');
          if (datasetButton) datasetButton.disabled = !records.length;
          const saveButton = root.querySelector('[data-save-query]');
          if (saveButton) saveButton.disabled = !records.length;
        }
      } catch (error) {
        target.innerHTML = `<div class="sc-lab-data-note">${String(error.message || error)}</div>`;
        statusText(summary, `Source error: ${error.message || error}`, true);
        recordError(kind, error);
        records = [];
      }
      return records;
    }

    button.addEventListener('click', run);
    if (isBoard) root.querySelector('[data-feed-refresh]')?.addEventListener('click', run);

    const datasetButton = root.querySelector(isMarine ? '[data-marine-dataset]' : isSpace ? '[data-space-dataset]' : '[data-feed-to-dataset]');
    datasetButton?.addEventListener('click', () => {
      if (!records.length) return;
      const title = isMarine ? 'Marine biodiversity occurrences' : isSpace ? 'Space telescope observations' : 'Scientific observation board';
      const source = isMarine ? 'OBIS' : isSpace ? 'NASA Image and Video Library' : 'Scientific sources';
      saveDataset(Lab, projects, title, source, records);
      statusText(summary, `${records.length} records saved as a project dataset.`, false);
    });

    root.dataset.scLabObserveReady = VERSION;
    return true;
  }

  function renderMarineChart(root, Lab, records) {
    const target = root.querySelector('[data-marine-chart]');
    if (!target) return;
    const points = Lab.Observations?.depthSeries ? Lab.Observations.depthSeries(records) : [];
    if (!points.length) {
      target.innerHTML = '<div class="sc-lab-data-note">No depth values were supplied by these records.</div>';
      return;
    }
    const max = Math.max(...points.map((point) => Number(point.depth) || 0), 1);
    target.innerHTML = `<svg viewBox="0 0 700 140" role="img" aria-label="Marine occurrence depth series"><line x1="35" y1="15" x2="35" y2="120" stroke="#89949d"/><line x1="35" y1="120" x2="680" y2="120" stroke="#89949d"/>${points.map((point, index) => `<circle cx="${35 + index * (640 / Math.max(points.length - 1, 1))}" cy="${15 + (Number(point.depth) || 0) / max * 100}" r="3" fill="#7d1128"/>`).join('')}<text x="5" y="18" font-size="10">0 m</text><text x="2" y="120" font-size="10">${max.toFixed(0)} m</text></svg>`;
  }

  function mount() {
    const root = app();
    if (!root) return false;
    const module = canonical(root.dataset.initialModule || root.dataset.activeModule || 'overview');
    state.module = module;
    if (!owns(module) || root.dataset.scLabObserveReady === VERSION) return false;
    const Lab = W.SCLab || {};
    const projects = projectStore(root, Lab);
    try {
      const mounted = module === 'climate-maps'
        ? mountClimate(root, Lab, projects)
        : mountFeed(root, Lab, projects, module);
      state.ready = !!mounted;
      if (mounted) {
        root.dataset.scLabObserveController = VERSION;
        D.dispatchEvent(new CustomEvent('sc-lab:observe-ready', { detail: { module, version: VERSION } }));
      }
      return mounted;
    } catch (error) {
      recordError('mount', error);
      return false;
    }
  }

  function status() {
    return { version: VERSION, module: state.module, ready: state.ready, ownsActiveModule: owns(state.module), recordCount: state.records.length, errors: state.errors.slice(-10) };
  }

  W.SCLabObserveDomainV02633 = { VERSION, owns, canonical, mount, status };
  W.SCLab = W.SCLab || {};
  W.SCLab.ObserveDomainV02633 = W.SCLabObserveDomainV02633;
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', mount, { once: true });
  else mount();
  D.addEventListener('sc-lab:module-opened', mount);
})(window, document);
