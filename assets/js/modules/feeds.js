(function (w, d) {
  'use strict';

  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;

  function url(source, params = {}) {
    const base = (w.SCLabConfig?.restBase || '/wp-json/sc-lab/v1/') + `feeds/${encodeURIComponent(source)}`;
    return `${base}?${new URLSearchParams(params).toString()}`;
  }

  function queryParams(source, q, limit) {
    const params = { limit };
    if (q) {
      if (source === 'obis-marine') params.scientificName = q;
      else params.q = q;
    }
    return params;
  }

  async function load(source, q = '', limit = 12) {
    return U.fetchJson(url(source, queryParams(source, q, limit)), {
      headers: { 'X-WP-Nonce': w.SCLabConfig?.nonce || '' }
    });
  }

  function recordMeta(record) {
    const location = record.location || {};
    return [
      ['Source', record.source || 'Unknown'],
      ['Domain', record.domain || 'Science'],
      ['Observed', U.fmt(record.observedAt)],
      ['Retrieved', U.fmt(record.retrievedAt)],
      ['Latitude', location.latitude ?? '—'],
      ['Longitude', location.longitude ?? '—'],
      ['Record ID', record.id || '—']
    ];
  }

  function inspectRecord(record, root) {
    const dialog = root.querySelector('[data-record-dialog]');
    if (!dialog || typeof dialog.showModal !== 'function') {
      w.alert(`${record.title}\n\n${record.summary || record.abstract || ''}`);
      return;
    }

    dialog.querySelector('[data-dialog-source]').textContent = `${record.source || 'Scientific source'} / ${record.domain || 'Record'}`;
    dialog.querySelector('[data-dialog-title]').textContent = record.title || 'Scientific record';
    dialog.querySelector('[data-dialog-summary]').textContent = record.summary || record.abstract || 'No summary supplied by the source.';
    dialog.querySelector('[data-dialog-meta]').innerHTML = recordMeta(record)
      .map(([key, value]) => `<div><dt>${U.esc(key)}</dt><dd>${U.esc(value)}</dd></div>`)
      .join('');

    const sourceLink = dialog.querySelector('[data-dialog-open-source]');
    sourceLink.href = record.url || '#';
    sourceLink.hidden = !record.url;

    const siteLink = dialog.querySelector('[data-dialog-site-intelligence]');
    const latitude = record.location?.latitude;
    const longitude = record.location?.longitude;
    const route = w.SCLabConfig?.routes?.siteIntelligence;
    if (route && Number.isFinite(Number(latitude)) && Number.isFinite(Number(longitude))) {
      const destination = new URL(route, w.location.href);
      destination.searchParams.set('lat', latitude);
      destination.searchParams.set('lon', longitude);
      destination.searchParams.set('source', record.source || 'Lab');
      destination.searchParams.set('record', record.id || '');
      siteLink.href = destination.toString();
      siteLink.hidden = false;
    } else {
      siteLink.hidden = true;
    }

    dialog.showModal();
  }

  function saveEvidence(record, projects, root) {
    projects.add('evidence', {
      title: record.title,
      summary: record.summary || record.abstract || '',
      source: record.source,
      url: record.url,
      observedAt: record.observedAt,
      retrievedAt: record.retrievedAt,
      record,
      status: 'unreviewed'
    }, `Evidence saved: ${record.title}`);
    U.toast(root, 'Saved to evidence inbox.');
  }

  function citeNotebook(record, projects, root) {
    projects.add('notes', {
      type: 'source-citation',
      title: record.title,
      body: `Source: ${record.source}\nURL: ${record.url || ''}\nObserved: ${record.observedAt || ''}\nRetrieved: ${record.retrievedAt || ''}\n\n${record.summary || record.abstract || ''}`,
      tags: ['source', String(record.domain || 'science').toLowerCase()]
    }, `Notebook citation added: ${record.title}`);
    U.toast(root, 'Citation added to notebook.');
  }

  function createExperiment(record, projects, root) {
    projects.add('experiments', {
      title: `Investigate: ${record.title}`,
      question: `What can be learned or tested from this ${record.domain || 'scientific'} record?`,
      hypothesis: '',
      method: `Review the source record, identify measurable variables, define controls or comparison data, and document the analysis method.\n\nSource: ${record.url || record.source}`,
      status: 'planned',
      sourceRecord: record
    }, `Experiment created from scientific signal: ${record.title}`);
    U.toast(root, 'Experiment created from signal.');
  }

  function card(record, projects, root, options = {}) {
    const el = d.createElement('article');
    el.className = options.compact ? 'sc-lab-signal-row' : 'sc-lab-feed-card';

    if (options.compact) {
      el.innerHTML = `
        <div class="sc-lab-signal-source">${U.esc(record.source || 'Source')}</div>
        <div class="sc-lab-signal-copy"><strong>${U.esc(record.title)}</strong><span>${U.esc(record.domain || 'Science')} · ${U.esc(U.fmt(record.observedAt))}</span></div>
        <div class="sc-lab-signal-actions"><button class="sc-lab-text-button" data-inspect>Inspect</button><button class="sc-lab-text-button" data-save-evidence>Save</button></div>`;
    } else {
      const image = record.thumbnail ? `<img loading="lazy" src="${U.esc(record.thumbnail)}" alt="">` : '';
      const sourceLink = record.url ? `<a class="sc-lab-text-button" href="${U.esc(record.url)}" target="_blank" rel="noopener">Open source</a>` : '';
      el.innerHTML = `
        ${image}
        <div class="sc-lab-feed-card-body">
          <span class="sc-lab-feed-domain">${U.esc(record.domain || 'Science')}</span>
          <h4>${U.esc(record.title)}</h4>
          <p>${U.esc((record.summary || record.abstract || '').slice(0, 330))}</p>
          <div class="sc-lab-feed-meta">${U.esc(record.source)} · ${U.esc(U.fmt(record.observedAt))}</div>
        </div>
        <div class="sc-lab-card-actions">
          <button class="sc-lab-button" data-inspect>Inspect</button>
          ${sourceLink}
          <button class="sc-lab-button" data-save-evidence>Save evidence</button>
          <button class="sc-lab-button" data-cite-note>Notebook</button>
          <button class="sc-lab-button sc-lab-button-primary" data-create-experiment>Create experiment</button>
        </div>`;
    }

    el.querySelector('[data-inspect]')?.addEventListener('click', () => inspectRecord(record, root));
    el.querySelector('[data-save-evidence]')?.addEventListener('click', () => saveEvidence(record, projects, root));
    el.querySelector('[data-cite-note]')?.addEventListener('click', () => citeNotebook(record, projects, root));
    el.querySelector('[data-create-experiment]')?.addEventListener('click', () => createExperiment(record, projects, root));
    return el;
  }

  function render(target, records, projects, root, options = {}) {
    target.innerHTML = '';
    if (!records?.length) {
      target.innerHTML = '<div class="sc-lab-data-note">No records returned.</div>';
      return;
    }
    records.forEach(record => target.appendChild(card(record, projects, root, options)));
  }

  Lab.Feeds = { load, render, card, inspectRecord, saveEvidence, citeNotebook, createExperiment };
})(window, document);
