(function () {
  'use strict';

  const VERSION = '0.9.5';
  const PROJECTS_KEY = 'scLabProjectsV010';
  const ACTIVE_PROJECT_KEY = 'scLabActiveProjectV010';
  const COMPOSER_PREFIX = 'scLabReportComposerV095:';
  const RECEIPTS_KEY = 'scLabRestoreReceiptsV095';
  const COLLECTIONS = [
    'notes', 'observations', 'calculations', 'analyses', 'analysisPackets',
    'visualizations', 'dimensionalScenes', 'reports', 'reportFigures',
    'reportExports', 'decisionStudioHandoffs', 'reportDrafts',
    'reportRevisions', 'reportPackages', 'restorePreflights', 'restoreReceipts',
    'accessibilityAudits', 'migrationValidationRecords'
  ];

  const SECTION_LABELS = {
    cover: 'Cover page',
    'executive-summary': 'Executive summary',
    methods: 'Methods',
    assumptions: 'Assumptions',
    results: 'Results',
    figures: 'Figures',
    tables: 'Tables',
    validation: 'Validation',
    limitations: 'Limitations',
    sources: 'Sources',
    appendices: 'Appendices',
    audit: 'Audit record'
  };

  const TEMPLATES = {
    'technical-report': {
      label: 'Technical report',
      type: 'technical-report',
      sections: ['cover', 'executive-summary', 'methods', 'assumptions', 'results', 'figures', 'tables', 'validation', 'limitations', 'sources', 'appendices', 'audit']
    },
    'experiment-report': {
      label: 'Experiment report',
      type: 'technical-report',
      sections: ['cover', 'executive-summary', 'methods', 'results', 'figures', 'tables', 'validation', 'limitations', 'sources', 'appendices', 'audit']
    },
    'analysis-brief': {
      label: 'Analysis brief',
      type: 'executive-summary',
      sections: ['cover', 'executive-summary', 'results', 'figures', 'validation', 'limitations', 'sources', 'audit']
    },
    'decision-brief': {
      label: 'Decision brief',
      type: 'decision-brief',
      sections: ['cover', 'executive-summary', 'assumptions', 'results', 'figures', 'validation', 'limitations', 'sources', 'audit']
    }
  };

  const textEncoder = new TextEncoder();
  const textDecoder = new TextDecoder();
  let lastRestorePayload = null;
  let lastRestorePreflight = null;
  let composerTimer = null;

  function nowIso() {
    return new Date().toISOString();
  }

  function uid(prefix) {
    const random = (globalThis.crypto && globalThis.crypto.randomUUID)
      ? globalThis.crypto.randomUUID()
      : Math.random().toString(36).slice(2) + Date.now().toString(36);
    return `${prefix}-${random}`;
  }

  function clone(value) {
    return value == null ? value : JSON.parse(JSON.stringify(value));
  }

  function safeJsonParse(value, fallback) {
    try {
      return JSON.parse(value);
    } catch (error) {
      return fallback;
    }
  }

  function stableStringify(value) {
    if (value === null || typeof value !== 'object') return JSON.stringify(value);
    if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
  }

  function fingerprint(value) {
    const input = typeof value === 'string' ? value : stableStringify(value);
    let hash = 2166136261;
    for (let i = 0; i < input.length; i += 1) {
      hash ^= input.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return `fnv1a-${(hash >>> 0).toString(16).padStart(8, '0')}`;
  }

  async function sha256Hex(value) {
    const bytes = value instanceof Uint8Array ? value : textEncoder.encode(typeof value === 'string' ? value : stableStringify(value));
    if (globalThis.crypto && globalThis.crypto.subtle) {
      const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
    }
    return fingerprint(value);
  }

  const CRC_TABLE = (() => {
    const table = new Uint32Array(256);
    for (let n = 0; n < 256; n += 1) {
      let c = n;
      for (let k = 0; k < 8; k += 1) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
      table[n] = c >>> 0;
    }
    return table;
  })();

  function crc32(bytes) {
    let crc = 0xffffffff;
    for (const byte of bytes) crc = CRC_TABLE[(crc ^ byte) & 0xff] ^ (crc >>> 8);
    return (crc ^ 0xffffffff) >>> 0;
  }

  function writeUint16(target, offset, value) { new DataView(target.buffer).setUint16(offset, value, true); }
  function writeUint32(target, offset, value) { new DataView(target.buffer).setUint32(offset, value >>> 0, true); }

  function createStoredZip(files) {
    const localParts = [];
    const centralParts = [];
    let localOffset = 0;
    Object.entries(files).forEach(([name, value]) => {
      const nameBytes = textEncoder.encode(name);
      const data = value instanceof Uint8Array ? value : textEncoder.encode(String(value));
      const crc = crc32(data);
      const local = new Uint8Array(30 + nameBytes.length + data.length);
      writeUint32(local, 0, 0x04034b50); writeUint16(local, 4, 20); writeUint16(local, 6, 0);
      writeUint16(local, 8, 0); writeUint16(local, 10, 0); writeUint16(local, 12, 0);
      writeUint32(local, 14, crc); writeUint32(local, 18, data.length); writeUint32(local, 22, data.length);
      writeUint16(local, 26, nameBytes.length); writeUint16(local, 28, 0);
      local.set(nameBytes, 30); local.set(data, 30 + nameBytes.length); localParts.push(local);

      const central = new Uint8Array(46 + nameBytes.length);
      writeUint32(central, 0, 0x02014b50); writeUint16(central, 4, 20); writeUint16(central, 6, 20);
      writeUint16(central, 8, 0); writeUint16(central, 10, 0); writeUint16(central, 12, 0); writeUint16(central, 14, 0);
      writeUint32(central, 16, crc); writeUint32(central, 20, data.length); writeUint32(central, 24, data.length);
      writeUint16(central, 28, nameBytes.length); writeUint16(central, 30, 0); writeUint16(central, 32, 0);
      writeUint16(central, 34, 0); writeUint16(central, 36, 0); writeUint32(central, 38, 0); writeUint32(central, 42, localOffset);
      central.set(nameBytes, 46); centralParts.push(central); localOffset += local.length;
    });
    const centralSize = centralParts.reduce((sum, part) => sum + part.length, 0);
    const end = new Uint8Array(22);
    writeUint32(end, 0, 0x06054b50); writeUint16(end, 4, 0); writeUint16(end, 6, 0);
    writeUint16(end, 8, centralParts.length); writeUint16(end, 10, centralParts.length);
    writeUint32(end, 12, centralSize); writeUint32(end, 16, localOffset); writeUint16(end, 20, 0);
    return new Blob([...localParts, ...centralParts, end], { type: 'application/zip' });
  }

  function download(name, content, type) {
    const blob = content instanceof Blob ? content : new Blob([content], { type: type || 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function readProjects() {
    const raw = localStorage.getItem(PROJECTS_KEY);
    const parsed = safeJsonParse(raw || '[]', []);
    if (Array.isArray(parsed)) return parsed;
    if (parsed && Array.isArray(parsed.projects)) return parsed.projects;
    if (parsed && typeof parsed === 'object') return Object.values(parsed).filter((item) => item && typeof item === 'object');
    return [];
  }

  function writeProjects(projects) {
    localStorage.setItem(PROJECTS_KEY, JSON.stringify(projects));
    document.dispatchEvent(new CustomEvent('sc-lab-projects-updated', { detail: { version: VERSION } }));
  }

  function activeProjectId() {
    return localStorage.getItem(ACTIVE_PROJECT_KEY) || '';
  }

  function ensureProjectCollections(project) {
    const copyProject = project || {};
    COLLECTIONS.forEach((key) => {
      if (!Array.isArray(copyProject[key])) copyProject[key] = [];
    });
    copyProject.schemaVersion = VERSION;
    return copyProject;
  }

  function getActiveProject() {
    const projects = readProjects();
    const selected = projects.find((project) => String(project.id) === String(activeProjectId())) || projects[0] || null;
    return selected ? ensureProjectCollections(selected) : null;
  }

  function updateProject(project) {
    const projects = readProjects();
    const normalized = ensureProjectCollections(project);
    const index = projects.findIndex((item) => String(item.id) === String(normalized.id));
    if (index >= 0) projects[index] = normalized;
    else projects.push(normalized);
    writeProjects(projects);
    return normalized;
  }

  function status(target, message, kind) {
    if (!target) return;
    target.textContent = message;
    target.dataset.kind = kind || 'info';
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function defaultSection(type) {
    return {
      id: uid('section'),
      type,
      title: SECTION_LABELS[type] || type,
      enabled: true,
      content: '',
      createdAt: nowIso(),
      updatedAt: nowIso()
    };
  }

  function defaultComposer(templateId) {
    const template = TEMPLATES[templateId] || TEMPLATES['technical-report'];
    return {
      format: 'sc-lab-report-composition/1.0',
      applicationVersion: VERSION,
      id: uid('report-composition'),
      templateId: templateId || 'technical-report',
      title: 'Scientific analysis report',
      subtitle: '',
      executiveSummary: '',
      sections: template.sections.map(defaultSection),
      revision: 0,
      createdAt: nowIso(),
      updatedAt: nowIso()
    };
  }

  function composerStorageKey() {
    const project = getActiveProject();
    return `${COMPOSER_PREFIX}${project ? project.id : 'unassigned'}`;
  }

  function loadComposer() {
    const saved = safeJsonParse(localStorage.getItem(composerStorageKey()) || '', null);
    if (saved && saved.format === 'sc-lab-report-composition/1.0' && Array.isArray(saved.sections)) return saved;
    return defaultComposer('technical-report');
  }

  function saveComposerState(state) {
    state.updatedAt = nowIso();
    state.applicationVersion = VERSION;
    localStorage.setItem(composerStorageKey(), JSON.stringify(state));
  }

  function composerMarkup() {
    const templateOptions = Object.entries(TEMPLATES)
      .map(([id, item]) => `<option value="${id}">${escapeHtml(item.label)}</option>`)
      .join('');
    const sectionOptions = Object.entries(SECTION_LABELS)
      .map(([id, label]) => `<option value="${id}">${escapeHtml(label)}</option>`)
      .join('');

    return `
      <section class="sc-lab-v095-card" data-v095-report-composer aria-labelledby="sc-v095-composer-title">
        <div class="sc-lab-v095-heading-row">
          <div>
            <p class="sc-lab-v095-kicker">Lab v${VERSION}</p>
            <h3 id="sc-v095-composer-title">Report Composer</h3>
            <p>Arrange report sections, maintain drafts and revisions, and apply the composition to the existing PDF Report Studio.</p>
          </div>
          <span class="sc-lab-v095-badge">Autosave enabled</span>
        </div>
        <div class="sc-lab-v095-grid sc-lab-v095-grid-3">
          <label>Template
            <select data-v095-template>${templateOptions}</select>
          </label>
          <label>Report title
            <input type="text" data-v095-title maxlength="180">
          </label>
          <label>Subtitle
            <input type="text" data-v095-subtitle maxlength="240">
          </label>
        </div>
        <label>Executive summary
          <textarea data-v095-summary rows="4" maxlength="8000"></textarea>
        </label>
        <div class="sc-lab-v095-add-row">
          <label>Add section
            <select data-v095-add-section>${sectionOptions}</select>
          </label>
          <button type="button" class="button" data-v095-add>Insert section</button>
        </div>
        <p class="sc-lab-v095-help">Reorder with the arrow buttons, drag and drop, or focus a section and press Alt+Up/Alt+Down.</p>
        <div class="sc-lab-v095-section-list" data-v095-sections role="list" aria-label="Report sections"></div>
        <div class="sc-lab-v095-actions">
          <button type="button" class="button button-primary" data-v095-apply>Apply to Report Studio</button>
          <button type="button" class="button" data-v095-save-draft>Save draft</button>
          <button type="button" class="button" data-v095-save-revision>Save revision</button>
          <button type="button" class="button" data-v095-export>Export composition JSON</button>
          <button type="button" class="button" data-v095-export-package>Export report package ZIP</button>
        </div>
        <div class="sc-lab-v095-revisions" data-v095-revisions aria-label="Saved report revisions"></div>
        <p class="sc-lab-v095-status" data-v095-composer-status role="status" aria-live="polite"></p>
      </section>`;
  }

  function renderSections(panel, state) {
    const list = panel.querySelector('[data-v095-sections]');
    if (!list) return;
    list.innerHTML = state.sections.map((section, index) => `
      <article class="sc-lab-v095-section" role="listitem" draggable="true" tabindex="0" data-v095-section-index="${index}" aria-label="${escapeHtml(section.title)} section, position ${index + 1} of ${state.sections.length}">
        <div class="sc-lab-v095-section-head">
          <span class="sc-lab-v095-drag" aria-hidden="true">⋮⋮</span>
          <label class="sc-lab-v095-check"><input type="checkbox" data-v095-section-enabled ${section.enabled ? 'checked' : ''}> Include</label>
          <input type="text" data-v095-section-title value="${escapeHtml(section.title)}" aria-label="Section title">
          <div class="sc-lab-v095-section-actions">
            <button type="button" class="button" data-v095-up aria-label="Move ${escapeHtml(section.title)} up" ${index === 0 ? 'disabled' : ''}>↑</button>
            <button type="button" class="button" data-v095-down aria-label="Move ${escapeHtml(section.title)} down" ${index === state.sections.length - 1 ? 'disabled' : ''}>↓</button>
            <button type="button" class="button" data-v095-remove aria-label="Remove ${escapeHtml(section.title)}">Remove</button>
          </div>
        </div>
        <textarea rows="3" data-v095-section-content aria-label="${escapeHtml(section.title)} narrative">${escapeHtml(section.content || '')}</textarea>
      </article>`).join('');
  }

  function renderRevisions(panel) {
    const project = getActiveProject();
    const target = panel.querySelector('[data-v095-revisions]');
    if (!target) return;
    const revisions = project && Array.isArray(project.reportRevisions) ? project.reportRevisions.slice(-8).reverse() : [];
    if (!revisions.length) {
      target.innerHTML = '<p class="sc-lab-v095-muted">No saved revisions in the active project.</p>';
      return;
    }
    target.innerHTML = `<h4>Recent revisions</h4>${revisions.map((record) => `
      <button type="button" class="sc-lab-v095-revision" data-v095-load-revision="${escapeHtml(record.id)}">
        <strong>${escapeHtml(record.title || 'Untitled report')}</strong>
        <span>Revision ${Number(record.revision || 0)} · ${escapeHtml(new Date(record.createdAt || Date.now()).toLocaleString())}</span>
      </button>`).join('')}`;
  }

  function syncComposerForm(panel, state) {
    panel.querySelector('[data-v095-template]').value = state.templateId || 'technical-report';
    panel.querySelector('[data-v095-title]').value = state.title || '';
    panel.querySelector('[data-v095-subtitle]').value = state.subtitle || '';
    panel.querySelector('[data-v095-summary]').value = state.executiveSummary || '';
    renderSections(panel, state);
    renderRevisions(panel);
  }

  function readComposerForm(panel, state) {
    state.templateId = panel.querySelector('[data-v095-template]').value;
    state.title = panel.querySelector('[data-v095-title]').value.trim();
    state.subtitle = panel.querySelector('[data-v095-subtitle]').value.trim();
    state.executiveSummary = panel.querySelector('[data-v095-summary]').value.trim();
    panel.querySelectorAll('[data-v095-section-index]').forEach((node) => {
      const index = Number(node.dataset.v095SectionIndex);
      const section = state.sections[index];
      if (!section) return;
      section.enabled = node.querySelector('[data-v095-section-enabled]').checked;
      section.title = node.querySelector('[data-v095-section-title]').value.trim() || SECTION_LABELS[section.type] || section.type;
      section.content = node.querySelector('[data-v095-section-content]').value;
      section.updatedAt = nowIso();
    });
    return state;
  }

  function scheduleComposerSave(panel, state) {
    clearTimeout(composerTimer);
    composerTimer = setTimeout(() => {
      readComposerForm(panel, state);
      saveComposerState(state);
      status(panel.querySelector('[data-v095-composer-status]'), `Draft autosaved at ${new Date().toLocaleTimeString()}.`, 'success');
    }, 450);
  }

  function moveSection(state, from, to) {
    if (from < 0 || to < 0 || from >= state.sections.length || to >= state.sections.length || from === to) return;
    const [section] = state.sections.splice(from, 1);
    state.sections.splice(to, 0, section);
  }

  function saveProjectReportRecord(state, collection, kind) {
    const project = getActiveProject();
    if (!project) throw new Error('Create or select a Lab project before saving.');
    ensureProjectCollections(project);
    const nextRevision = collection === 'reportRevisions'
      ? Math.max(0, ...project.reportRevisions.map((item) => Number(item.revision || 0))) + 1
      : Number(state.revision || 0);
    const record = {
      ...clone(state),
      id: uid(kind),
      revision: nextRevision,
      projectId: project.id,
      createdAt: nowIso(),
      compositionFingerprint: fingerprint(state)
    };
    project[collection].push(record);
    updateProject(project);
    return record;
  }

  function applyCompositionToReportStudio(state) {
    const mappings = [
      ['[data-report-title]', state.title],
      ['[data-report-subtitle]', state.subtitle],
      ['[data-report-summary]', state.executiveSummary]
    ];
    mappings.forEach(([selector, value]) => {
      const control = document.querySelector(selector);
      if (control) {
        control.value = value || '';
        control.dispatchEvent(new Event('input', { bubbles: true }));
        control.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    const type = document.querySelector('[data-report-type]');
    const template = TEMPLATES[state.templateId] || TEMPLATES['technical-report'];
    if (type) {
      const desired = template.type;
      if ([...type.options].some((option) => option.value === desired)) type.value = desired;
      type.dispatchEvent(new Event('change', { bubbles: true }));
    }
    const enabledTypes = state.sections.filter((section) => section.enabled).map((section) => section.type);
    window.SCLabV095CurrentComposition = clone(state);
    document.dispatchEvent(new CustomEvent('sc-lab-report-composition-applied', {
      detail: { composition: clone(state), enabledSections: enabledTypes, version: VERSION }
    }));
    const composeButton = document.querySelector('[data-report-compose]');
    if (composeButton) composeButton.click();
  }

  function initComposer(panel) {
    if (!panel || panel.querySelector('[data-v095-report-composer]')) return;
    panel.insertAdjacentHTML('beforeend', composerMarkup());
    const composer = panel.querySelector('[data-v095-report-composer]');
    const state = loadComposer();
    syncComposerForm(composer, state);

    composer.addEventListener('input', () => scheduleComposerSave(composer, state));
    composer.addEventListener('change', (event) => {
      if (event.target.matches('[data-v095-template]')) {
        const templateId = event.target.value;
        const fresh = defaultComposer(templateId);
        fresh.title = state.title;
        fresh.subtitle = state.subtitle;
        fresh.executiveSummary = state.executiveSummary;
        Object.keys(state).forEach((key) => delete state[key]);
        Object.assign(state, fresh);
        syncComposerForm(composer, state);
      }
      scheduleComposerSave(composer, state);
    });

    composer.addEventListener('click', (event) => {
      const sectionNode = event.target.closest('[data-v095-section-index]');
      const index = sectionNode ? Number(sectionNode.dataset.v095SectionIndex) : -1;
      if (event.target.matches('[data-v095-add]')) {
        readComposerForm(composer, state);
        state.sections.push(defaultSection(composer.querySelector('[data-v095-add-section]').value));
        renderSections(composer, state);
        saveComposerState(state);
      } else if (event.target.matches('[data-v095-up]')) {
        readComposerForm(composer, state); moveSection(state, index, index - 1); renderSections(composer, state); saveComposerState(state);
      } else if (event.target.matches('[data-v095-down]')) {
        readComposerForm(composer, state); moveSection(state, index, index + 1); renderSections(composer, state); saveComposerState(state);
      } else if (event.target.matches('[data-v095-remove]')) {
        readComposerForm(composer, state); state.sections.splice(index, 1); renderSections(composer, state); saveComposerState(state);
      } else if (event.target.matches('[data-v095-apply]')) {
        readComposerForm(composer, state); saveComposerState(state); applyCompositionToReportStudio(state);
        status(composer.querySelector('[data-v095-composer-status]'), 'Composition applied to PDF Report Studio.', 'success');
      } else if (event.target.matches('[data-v095-save-draft]')) {
        try {
          readComposerForm(composer, state); const record = saveProjectReportRecord(state, 'reportDrafts', 'report-draft');
          status(composer.querySelector('[data-v095-composer-status]'), `Draft saved with fingerprint ${record.compositionFingerprint}.`, 'success'); renderRevisions(composer);
        } catch (error) { status(composer.querySelector('[data-v095-composer-status]'), error.message, 'error'); }
      } else if (event.target.matches('[data-v095-save-revision]')) {
        try {
          readComposerForm(composer, state); const record = saveProjectReportRecord(state, 'reportRevisions', 'report-revision');
          state.revision = record.revision; saveComposerState(state);
          status(composer.querySelector('[data-v095-composer-status]'), `Revision ${record.revision} saved.`, 'success'); renderRevisions(composer);
        } catch (error) { status(composer.querySelector('[data-v095-composer-status]'), error.message, 'error'); }
      } else if (event.target.matches('[data-v095-export]')) {
        readComposerForm(composer, state);
        download(`sc-lab-report-composition-${Date.now()}.json`, JSON.stringify({ ...state, compositionFingerprint: fingerprint(state) }, null, 2), 'application/json');
      } else if (event.target.matches('[data-v095-export-package]')) {
        readComposerForm(composer, state);
        const project = getActiveProject();
        const manifest = {
          format: 'sc-lab-report-package/1.0', applicationVersion: VERSION, createdAt: nowIso(),
          compositionId: state.id, projectId: project ? project.id : null,
          compositionFingerprint: fingerprint(state), fileCount: 3
        };
        const zip = createStoredZip({
          'manifest.json': JSON.stringify(manifest, null, 2),
          'report-composition.json': JSON.stringify(state, null, 2),
          'project-context.json': JSON.stringify(project ? {
            id: project.id, name: project.name, schemaVersion: project.schemaVersion,
            analyses: project.analyses || [], analysisPackets: project.analysisPackets || [],
            visualizations: project.visualizations || [], reports: project.reports || [],
            citations: project.citations || [], sources: project.sourceSnapshots || []
          } : {}, null, 2)
        });
        download(`sc-lab-report-package-${Date.now()}.zip`, zip, 'application/zip');
        if (project) {
          ensureProjectCollections(project);
          project.reportPackages.push({ ...manifest, id: uid('report-package') });
          updateProject(project);
        }
      } else if (event.target.matches('[data-v095-load-revision]')) {
        const project = getActiveProject();
        const record = project && project.reportRevisions.find((item) => item.id === event.target.dataset.v095LoadRevision);
        if (record) {
          Object.keys(state).forEach((key) => delete state[key]); Object.assign(state, clone(record));
          saveComposerState(state); syncComposerForm(composer, state);
          status(composer.querySelector('[data-v095-composer-status]'), `Loaded revision ${record.revision}.`, 'success');
        }
      }
    });

    let dragIndex = -1;
    composer.addEventListener('dragstart', (event) => {
      const node = event.target.closest('[data-v095-section-index]');
      if (!node) return;
      readComposerForm(composer, state);
      dragIndex = Number(node.dataset.v095SectionIndex);
      event.dataTransfer.effectAllowed = 'move';
    });
    composer.addEventListener('dragover', (event) => {
      if (event.target.closest('[data-v095-section-index]')) event.preventDefault();
    });
    composer.addEventListener('drop', (event) => {
      const node = event.target.closest('[data-v095-section-index]');
      if (!node || dragIndex < 0) return;
      event.preventDefault();
      moveSection(state, dragIndex, Number(node.dataset.v095SectionIndex));
      dragIndex = -1; renderSections(composer, state); saveComposerState(state);
    });
    composer.addEventListener('keydown', (event) => {
      const node = event.target.closest('[data-v095-section-index]');
      if (!node || !event.altKey || !['ArrowUp', 'ArrowDown'].includes(event.key)) return;
      event.preventDefault();
      readComposerForm(composer, state);
      const from = Number(node.dataset.v095SectionIndex);
      const to = event.key === 'ArrowUp' ? from - 1 : from + 1;
      moveSection(state, from, to); renderSections(composer, state); saveComposerState(state);
      const next = composer.querySelector(`[data-v095-section-index="${Math.max(0, Math.min(to, state.sections.length - 1))}"]`);
      if (next) next.focus();
    });
  }

  function labRoot() {
    return document.querySelector('[data-sc-lab-app], .sc-lab-app') || document;
  }

  function readableChartLabel(node, index) {
    return node.getAttribute('aria-label') || node.dataset.title || node.dataset.chartTitle || `Scientific visualization ${index + 1}`;
  }

  function chartRows(node) {
    const candidates = [node.dataset.chartData, node.dataset.data, node.getAttribute('data-series')].filter(Boolean);
    for (const raw of candidates) {
      const parsed = safeJsonParse(raw, null);
      if (Array.isArray(parsed)) return parsed;
      if (parsed && Array.isArray(parsed.data)) return parsed.data;
    }
    return [];
  }

  function tableForRows(rows, label) {
    if (!rows.length || !rows[0] || typeof rows[0] !== 'object') return null;
    const keys = [...new Set(rows.flatMap((row) => Object.keys(row)))].slice(0, 12);
    const details = document.createElement('details');
    details.className = 'sc-lab-v095-data-table';
    details.innerHTML = `<summary>Data table for ${escapeHtml(label)}</summary><div class="sc-lab-v095-table-wrap"><table><caption>${escapeHtml(label)} data</caption><thead><tr>${keys.map((key) => `<th scope="col">${escapeHtml(key)}</th>`).join('')}</tr></thead><tbody>${rows.slice(0, 500).map((row) => `<tr>${keys.map((key) => `<td>${escapeHtml(row[key])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    return details;
  }

  function enhanceVisualizationNode(node, index) {
    if (node.dataset.v095Accessible === 'true') return;
    const label = readableChartLabel(node, index);
    node.dataset.v095Accessible = 'true';
    node.setAttribute('tabindex', node.getAttribute('tabindex') || '0');
    node.setAttribute('role', node.getAttribute('role') || 'img');
    node.setAttribute('aria-label', label);
    if (node.tagName.toLowerCase() === 'svg') {
      let title = node.querySelector(':scope > title');
      if (!title) {
        title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        node.prepend(title);
      }
      title.textContent = label;
      let description = node.querySelector(':scope > desc');
      if (!description) {
        description = document.createElementNS('http://www.w3.org/2000/svg', 'desc');
        title.after(description);
      }
      description.textContent = node.dataset.description || 'Scientific visualization. Use the adjacent data table when available for exact values.';
    }
    const rows = chartRows(node);
    if (rows.length && !node.parentElement.querySelector(':scope > .sc-lab-v095-data-table')) {
      const table = tableForRows(rows, label);
      if (table) node.insertAdjacentElement('afterend', table);
    }
  }

  function enhanceVisualizations(root) {
    const scope = root || document;
    const nodes = [...scope.querySelectorAll('svg, canvas, [data-chart], [data-visualization-output]')];
    nodes.forEach(enhanceVisualizationNode);
    scope.querySelectorAll('button:not([aria-label]), a[role="button"]:not([aria-label])').forEach((button) => {
      const visible = button.textContent.trim();
      if (visible) button.setAttribute('aria-label', visible);
    });
    scope.querySelectorAll('[data-status], .sc-lab-status').forEach((node) => {
      if (!node.hasAttribute('role')) node.setAttribute('role', 'status');
      node.setAttribute('aria-live', node.getAttribute('aria-live') || 'polite');
    });
    return nodes;
  }

  function mediaMatches(query) {
    return Boolean(window.matchMedia && window.matchMedia(query).matches);
  }

  function runAccessibilityAudit() {
    const scope = labRoot();
    const visualNodes = enhanceVisualizations(scope);
    const missingLabels = visualNodes.filter((node) => !node.getAttribute('aria-label')).length;
    const missingDescriptions = visualNodes.filter((node) => node.tagName.toLowerCase() === 'svg' && !node.querySelector(':scope > desc')).length;
    const missingTables = visualNodes.filter((node) => chartRows(node).length && !node.parentElement.querySelector(':scope > .sc-lab-v095-data-table')).length;
    const unlabeledControls = [...scope.querySelectorAll('button, input, select, textarea')].filter((control) => {
      if (control.type === 'hidden') return false;
      if (control.getAttribute('aria-label') || control.getAttribute('aria-labelledby') || control.closest('label')) return false;
      return !String(control.textContent || '').trim();
    }).length;
    const focusableVisuals = visualNodes.filter((node) => Number(node.getAttribute('tabindex')) >= 0).length;
    const issues = missingLabels + missingDescriptions + missingTables + unlabeledControls;
    return {
      format: 'sc-lab-accessibility-audit/1.0',
      applicationVersion: VERSION,
      id: uid('accessibility-audit'),
      createdAt: nowIso(),
      summary: {
        status: issues === 0 ? 'pass' : 'review',
        issueCount: issues,
        visualizationCount: visualNodes.length,
        focusableVisualizationCount: focusableVisuals,
        missingLabels,
        missingDescriptions,
        missingDataTables: missingTables,
        unlabeledControls,
        reducedMotionRequested: mediaMatches('(prefers-reduced-motion: reduce)'),
        forcedColorsActive: mediaMatches('(forced-colors: active)')
      },
      notes: [
        'Automated checks supplement, but do not replace, keyboard, screen-reader, zoom, contrast, print, and mobile review.',
        'Data-table alternatives are generated only when structured chart data is available in the document.'
      ]
    };
  }

  function accessibilityMarkup() {
    return `
      <section class="sc-lab-v095-card" data-v095-accessibility aria-labelledby="sc-v095-accessibility-title">
        <div class="sc-lab-v095-heading-row">
          <div>
            <p class="sc-lab-v095-kicker">Validation layer</p>
            <h3 id="sc-v095-accessibility-title">Visualization accessibility</h3>
            <p>Enhance chart semantics, test keyboard access, and record an auditable accessibility review.</p>
          </div>
        </div>
        <div class="sc-lab-v095-actions">
          <button type="button" class="button button-primary" data-v095-run-a11y>Run accessibility audit</button>
          <button type="button" class="button" data-v095-contrast aria-pressed="false">High contrast preview</button>
          <button type="button" class="button" data-v095-grayscale aria-pressed="false">Grayscale preview</button>
          <button type="button" class="button" data-v095-export-a11y disabled>Export audit JSON</button>
        </div>
        <div class="sc-lab-v095-audit-results" data-v095-a11y-results aria-live="polite"></div>
      </section>`;
  }

  function initAccessibility(panel) {
    if (!panel || panel.querySelector('[data-v095-accessibility]')) return;
    panel.insertAdjacentHTML('beforeend', accessibilityMarkup());
    const card = panel.querySelector('[data-v095-accessibility]');
    let audit = null;
    card.addEventListener('click', (event) => {
      if (event.target.matches('[data-v095-run-a11y]')) {
        audit = runAccessibilityAudit();
        const summary = audit.summary;
        card.querySelector('[data-v095-a11y-results]').innerHTML = `
          <div class="sc-lab-v095-metrics">
            <div><strong>${summary.visualizationCount}</strong><span>visualizations</span></div>
            <div><strong>${summary.focusableVisualizationCount}</strong><span>keyboard focusable</span></div>
            <div><strong>${summary.missingDataTables}</strong><span>table alternatives to review</span></div>
            <div><strong>${summary.issueCount}</strong><span>automated issues</span></div>
          </div>
          <p class="sc-lab-v095-status" data-kind="${summary.status === 'pass' ? 'success' : 'warning'}">Status: ${escapeHtml(summary.status)}. Manual screen-reader, zoom, mobile, print, and contrast validation remains required.</p>`;
        card.querySelector('[data-v095-export-a11y]').disabled = false;
        const project = getActiveProject();
        if (project) {
          ensureProjectCollections(project);
          project.accessibilityAudits.push(audit);
          updateProject(project);
        }
      } else if (event.target.matches('[data-v095-contrast]')) {
        const active = document.documentElement.classList.toggle('sc-lab-v095-high-contrast');
        event.target.setAttribute('aria-pressed', String(active));
      } else if (event.target.matches('[data-v095-grayscale]')) {
        const active = document.documentElement.classList.toggle('sc-lab-v095-grayscale');
        event.target.setAttribute('aria-pressed', String(active));
      } else if (event.target.matches('[data-v095-export-a11y]') && audit) {
        download(`sc-lab-accessibility-audit-${Date.now()}.json`, JSON.stringify(audit, null, 2), 'application/json');
      }
    });
    enhanceVisualizations(panel);
  }

  function dataView(bytes) {
    return new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  }

  async function inflateRaw(bytes) {
    if (!('DecompressionStream' in globalThis)) throw new Error('This browser cannot decompress deflated ZIP entries. Export a JSON workspace backup or use a current Chromium/Firefox browser.');
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
    return new Uint8Array(await new Response(stream).arrayBuffer());
  }

  async function extractWorkspaceJsonFromZip(buffer) {
    const bytes = new Uint8Array(buffer);
    const view = dataView(bytes);
    let offset = 0;
    while (offset + 30 <= bytes.length) {
      const signature = view.getUint32(offset, true);
      if (signature !== 0x04034b50) break;
      const flags = view.getUint16(offset + 6, true);
      const method = view.getUint16(offset + 8, true);
      const compressedSize = view.getUint32(offset + 18, true);
      const filenameLength = view.getUint16(offset + 26, true);
      const extraLength = view.getUint16(offset + 28, true);
      if (flags & 0x08) throw new Error('ZIP entries using data descriptors are not supported by the browser preflight. Use the JSON backup contained in the package.');
      const nameStart = offset + 30;
      const dataStart = nameStart + filenameLength + extraLength;
      const name = textDecoder.decode(bytes.slice(nameStart, nameStart + filenameLength));
      const compressed = bytes.slice(dataStart, dataStart + compressedSize);
      if (/workspace\.json$|backup\.json$|projects\.json$/i.test(name)) {
        let output;
        if (method === 0) output = compressed;
        else if (method === 8) output = await inflateRaw(compressed);
        else throw new Error(`Unsupported ZIP compression method ${method}.`);
        return textDecoder.decode(output);
      }
      offset = dataStart + compressedSize;
    }
    throw new Error('No workspace.json, backup.json, or projects.json entry was found in the ZIP package.');
  }

  async function readBackupFile(file) {
    if (!file) throw new Error('Choose a workspace JSON or ZIP backup.');
    if (!file.size) throw new Error('The selected backup is empty.');
    if (file.size > 50 * 1024 * 1024) throw new Error('The selected backup exceeds the 50 MB browser-validation limit.');
    if (/\.zip$/i.test(file.name) || file.type === 'application/zip') {
      return extractWorkspaceJsonFromZip(await file.arrayBuffer());
    }
    return file.text();
  }

  function projectCounts(projects) {
    const totals = { projects: projects.length };
    COLLECTIONS.forEach((key) => {
      totals[key] = projects.reduce((sum, project) => sum + (Array.isArray(project[key]) ? project[key].length : 0), 0);
    });
    return totals;
  }

  function workspaceContentFingerprint(projects) {
    const normalized = clone(Array.isArray(projects) ? projects : []);
    normalized.forEach((project) => {
      if (project && typeof project === 'object') delete project.restoreReceipts;
    });
    return fingerprint(normalized);
  }

  function validateBackup(raw, mode) {
    const errors = [];
    const warnings = [];
    let payload = raw;
    if (typeof raw === 'string') {
      payload = safeJsonParse(raw, null);
      if (!payload) errors.push('The selected file is not valid JSON.');
    }
    const projects = payload && Array.isArray(payload.projects)
      ? payload.projects
      : Array.isArray(payload) ? payload : [];
    if (!projects.length) errors.push('The backup does not contain a non-empty projects array.');
    if (payload && payload.format && payload.format !== 'sc-lab-workspace/1.0') warnings.push(`Unexpected workspace format: ${payload.format}.`);
    const ids = new Set();
    const duplicateIds = [];
    projects.forEach((project, index) => {
      if (!project || typeof project !== 'object') {
        errors.push(`Project ${index + 1} is not an object.`); return;
      }
      if (!project.id) warnings.push(`Project ${index + 1} has no stable id and will receive one during restore.`);
      if (project.id && ids.has(String(project.id))) duplicateIds.push(String(project.id));
      if (project.id) ids.add(String(project.id));
      COLLECTIONS.forEach((key) => {
        if (project[key] != null && !Array.isArray(project[key])) errors.push(`Project ${project.name || project.id || index + 1}: ${key} must be an array.`);
      });
    });
    if (duplicateIds.length) errors.push(`Duplicate project identifiers in backup: ${[...new Set(duplicateIds)].join(', ')}.`);
    const current = readProjects();
    const currentIds = new Set(current.map((project) => String(project.id)));
    const conflicts = projects.filter((project) => project.id && currentIds.has(String(project.id))).map((project) => String(project.id));
    if (conflicts.length && mode === 'merge') warnings.push(`${conflicts.length} project identifier conflict(s) will be merged with incoming records taking precedence.`);
    if (mode === 'replace') warnings.push('Replace mode removes current local projects after a safety backup is downloaded.');
    const normalizedPayload = {
      format: payload && payload.format ? payload.format : 'sc-lab-workspace/1.0',
      applicationVersion: payload && payload.applicationVersion ? payload.applicationVersion : 'unknown',
      exportedAt: payload && payload.exportedAt ? payload.exportedAt : null,
      projects: clone(projects)
    };
    return {
      format: 'sc-lab-restore-validation/1.0',
      applicationVersion: VERSION,
      id: uid('restore-preflight'),
      createdAt: nowIso(),
      mode,
      status: errors.length ? 'blocked' : warnings.length ? 'review' : 'ready',
      errors,
      warnings,
      conflicts,
      incomingCounts: projectCounts(projects),
      currentCounts: projectCounts(current),
      incomingFingerprint: fingerprint(normalizedPayload),
      currentFingerprint: workspaceContentFingerprint(current),
      dryRun: {
        mode,
        currentProjectCount: current.length,
        incomingProjectCount: projects.length,
        expectedProjectCount: mode === 'replace' ? projects.length : mode === 'copy' ? current.length + projects.length : new Set([...current.map((p) => String(p.id)), ...projects.map((p) => String(p.id))]).size,
        destructive: mode === 'replace'
      },
      payload: normalizedPayload
    };
  }

  function mergeArrayById(existing, incoming) {
    const result = Array.isArray(existing) ? clone(existing) : [];
    (Array.isArray(incoming) ? incoming : []).forEach((record) => {
      const id = record && record.id != null ? String(record.id) : '';
      const index = id ? result.findIndex((item) => item && String(item.id) === id) : -1;
      if (index >= 0) result[index] = clone(record);
      else result.push(clone(record));
    });
    return result;
  }

  function normalizeIncomingProject(project, copyMode) {
    const normalized = ensureProjectCollections(clone(project || {}));
    if (!normalized.id || copyMode) normalized.id = uid('project');
    if (copyMode) normalized.name = `${normalized.name || 'Restored project'} (restored copy)`;
    normalized.schemaVersion = VERSION;
    normalized.updatedAt = nowIso();
    if (!normalized.createdAt) normalized.createdAt = nowIso();
    return normalized;
  }

  function performRestore(preflight) {
    if (!preflight || preflight.status === 'blocked') throw new Error('Restore is blocked until validation errors are resolved.');
    const before = readProjects();
    const incoming = preflight.payload.projects;
    let after;
    if (preflight.mode === 'replace') {
      const safety = {
        format: 'sc-lab-workspace/1.0', applicationVersion: VERSION, exportedAt: nowIso(), projects: before,
        workspaceFingerprint: fingerprint(before), reason: 'automatic-pre-replace-safety-backup'
      };
      download(`sc-lab-safety-backup-${Date.now()}.json`, JSON.stringify(safety, null, 2), 'application/json');
      after = incoming.map((project) => normalizeIncomingProject(project, false));
    } else if (preflight.mode === 'copy') {
      after = before.concat(incoming.map((project) => normalizeIncomingProject(project, true)));
    } else {
      after = clone(before);
      incoming.forEach((project) => {
        const normalized = normalizeIncomingProject(project, false);
        const index = after.findIndex((item) => String(item.id) === String(normalized.id));
        if (index < 0) after.push(normalized);
        else {
          const merged = { ...after[index], ...normalized };
          COLLECTIONS.forEach((key) => { merged[key] = mergeArrayById(after[index][key], normalized[key]); });
          after[index] = ensureProjectCollections(merged);
        }
      });
    }
    writeProjects(after);
    const active = activeProjectId();
    if (!after.some((project) => String(project.id) === String(active)) && after[0]) localStorage.setItem(ACTIVE_PROJECT_KEY, String(after[0].id));
    const afterFingerprint = workspaceContentFingerprint(readProjects());
    const receipt = {
      format: 'sc-lab-restore-receipt/1.0', applicationVersion: VERSION, id: uid('restore-receipt'),
      createdAt: nowIso(), mode: preflight.mode, preflightId: preflight.id,
      incomingFingerprint: preflight.incomingFingerprint, beforeFingerprint: workspaceContentFingerprint(before), afterFingerprint,
      beforeCounts: projectCounts(before), afterCounts: projectCounts(after), warnings: preflight.warnings,
      integrity: afterFingerprint === workspaceContentFingerprint(after) ? 'verified' : 'review'
    };
    const receipts = safeJsonParse(localStorage.getItem(RECEIPTS_KEY) || '[]', []);
    receipts.push(receipt);
    localStorage.setItem(RECEIPTS_KEY, JSON.stringify(receipts.slice(-100)));
    const project = getActiveProject();
    if (project) {
      ensureProjectCollections(project);
      project.restoreReceipts.push(receipt);
      updateProject(project);
    }
    return receipt;
  }

  function runLegacyMigrationValidation() {
    const versions = ['0.1.0', '0.2.0', '0.3.0', '0.4.0', '0.5.0', '0.6.0', '0.7.0', '0.8.0', '0.9.0', '0.9.1', '0.9.2', '0.9.3', '0.9.4'];
    const cases = versions.map((version, index) => {
      const fixture = {
        schemaVersion: version, id: `legacy-${index}`, name: `Legacy ${version}`,
        notes: [{ id: `note-${index}`, text: 'migration fixture' }], maps: [{ id: `map-${index}` }]
      };
      const migrated = ensureProjectCollections(clone(fixture));
      const missingCollections = COLLECTIONS.filter((key) => !Array.isArray(migrated[key]));
      return {
        sourceVersion: version, targetVersion: migrated.schemaVersion,
        status: migrated.id === fixture.id && migrated.notes.length === 1 && missingCollections.length === 0 ? 'pass' : 'fail',
        missingCollections
      };
    });
    const record = {
      format: 'sc-lab-migration-validation/1.0', applicationVersion: VERSION,
      id: uid('migration-validation'), createdAt: nowIso(),
      status: cases.every((item) => item.status === 'pass') ? 'pass' : 'fail', cases,
      fingerprint: fingerprint(cases)
    };
    const project = getActiveProject();
    if (project) {
      ensureProjectCollections(project);
      project.migrationValidationRecords.push(record);
      updateProject(project);
    }
    return record;
  }

  function restoreMarkup() {
    return `
      <section class="sc-lab-v095-card" data-v095-restore aria-labelledby="sc-v095-restore-title">
        <div class="sc-lab-v095-heading-row">
          <div>
            <p class="sc-lab-v095-kicker">Workspace integrity</p>
            <h3 id="sc-v095-restore-title">Data-restore validation</h3>
            <p>Inspect a JSON or ZIP backup, preview impact, detect conflicts, and create a restore receipt before project data changes.</p>
          </div>
        </div>
        <div class="sc-lab-v095-grid sc-lab-v095-grid-2">
          <label>Workspace backup
            <input type="file" data-v095-restore-file accept=".json,.zip,application/json,application/zip">
          </label>
          <label>Restore mode
            <select data-v095-restore-mode>
              <option value="copy">Copy — preserve all current projects</option>
              <option value="merge">Merge — reconcile matching project IDs</option>
              <option value="replace">Replace — safety backup then replace</option>
            </select>
          </label>
        </div>
        <label data-v095-replace-confirm hidden>Type REPLACE to authorize destructive replacement
          <input type="text" data-v095-replace-text autocomplete="off" spellcheck="false">
        </label>
        <div class="sc-lab-v095-actions">
          <button type="button" class="button button-primary" data-v095-preflight>Run preflight</button>
          <button type="button" class="button" data-v095-export-preflight disabled>Export preflight JSON</button>
          <button type="button" class="button" data-v095-apply-restore disabled>Apply validated restore</button>
          <button type="button" class="button" data-v095-migration>Run legacy migration validation</button>
        </div>
        <div data-v095-restore-results aria-live="polite"></div>
      </section>`;
  }

  function renderPreflight(target, preflight) {
    const list = (items) => items.length ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : '<p>None.</p>';
    target.innerHTML = `
      <div class="sc-lab-v095-metrics">
        <div><strong>${preflight.incomingCounts.projects}</strong><span>incoming projects</span></div>
        <div><strong>${preflight.currentCounts.projects}</strong><span>current projects</span></div>
        <div><strong>${preflight.conflicts.length}</strong><span>ID conflicts</span></div>
        <div><strong>${preflight.dryRun.expectedProjectCount}</strong><span>expected after restore</span></div>
      </div>
      <p class="sc-lab-v095-status" data-kind="${preflight.status === 'blocked' ? 'error' : preflight.status === 'review' ? 'warning' : 'success'}">Preflight status: ${escapeHtml(preflight.status)} · fingerprint ${escapeHtml(preflight.incomingFingerprint)}</p>
      <div class="sc-lab-v095-grid sc-lab-v095-grid-2">
        <div><h4>Errors</h4>${list(preflight.errors)}</div>
        <div><h4>Warnings</h4>${list(preflight.warnings)}</div>
      </div>`;
  }

  function initRestore(panel) {
    if (!panel || panel.querySelector('[data-v095-restore]')) return;
    panel.insertAdjacentHTML('beforeend', restoreMarkup());
    const card = panel.querySelector('[data-v095-restore]');
    card.addEventListener('click', async (event) => {
      const results = card.querySelector('[data-v095-restore-results]');
      if (event.target.matches('[data-v095-preflight]')) {
        try {
          status(results, 'Reading and validating backup…', 'info');
          const raw = await readBackupFile(card.querySelector('[data-v095-restore-file]').files[0]);
          lastRestorePayload = raw;
          lastRestorePreflight = validateBackup(raw, card.querySelector('[data-v095-restore-mode]').value);
          lastRestorePreflight.sourceSha256 = await sha256Hex(raw);
          const active = getActiveProject();
          if (active) {
            ensureProjectCollections(active);
            const savedPreflight = clone(lastRestorePreflight); delete savedPreflight.payload;
            active.restorePreflights.push(savedPreflight); updateProject(active);
          }
          renderPreflight(results, lastRestorePreflight);
          card.querySelector('[data-v095-export-preflight]').disabled = false;
          card.querySelector('[data-v095-apply-restore]').disabled = lastRestorePreflight.status === 'blocked';
        } catch (error) {
          lastRestorePreflight = null;
          results.innerHTML = `<p class="sc-lab-v095-status" data-kind="error">${escapeHtml(error.message)}</p>`;
          card.querySelector('[data-v095-apply-restore]').disabled = true;
        }
      } else if (event.target.matches('[data-v095-export-preflight]') && lastRestorePreflight) {
        const exportCopy = { ...lastRestorePreflight };
        delete exportCopy.payload;
        download(`sc-lab-restore-preflight-${Date.now()}.json`, JSON.stringify(exportCopy, null, 2), 'application/json');
      } else if (event.target.matches('[data-v095-apply-restore]') && lastRestorePreflight) {
        try {
          if (lastRestorePreflight.mode === 'replace' && card.querySelector('[data-v095-replace-text]').value.trim() !== 'REPLACE') {
            throw new Error('Type REPLACE before applying destructive replacement.');
          }
          const receipt = performRestore(lastRestorePreflight);
          results.insertAdjacentHTML('beforeend', `<p class="sc-lab-v095-status" data-kind="success">Restore completed. Receipt ${escapeHtml(receipt.id)} · post-restore integrity ${escapeHtml(receipt.integrity)}.</p>`);
          download(`sc-lab-restore-receipt-${Date.now()}.json`, JSON.stringify(receipt, null, 2), 'application/json');
          event.target.disabled = true;
        } catch (error) {
          results.insertAdjacentHTML('beforeend', `<p class="sc-lab-v095-status" data-kind="error">${escapeHtml(error.message)}</p>`);
        }
      } else if (event.target.matches('[data-v095-migration]')) {
        const record = runLegacyMigrationValidation();
        results.innerHTML = `<p class="sc-lab-v095-status" data-kind="${record.status === 'pass' ? 'success' : 'error'}">Legacy migration validation ${escapeHtml(record.status)}: ${record.cases.filter((item) => item.status === 'pass').length}/${record.cases.length} fixtures passed · ${escapeHtml(record.fingerprint)}.</p>`;
        download(`sc-lab-migration-validation-${Date.now()}.json`, JSON.stringify(record, null, 2), 'application/json');
      }
    });
    const modeControl = card.querySelector('[data-v095-restore-mode]');
    const syncReplaceConfirmation = () => {
      const replace = modeControl.value === 'replace';
      card.querySelector('[data-v095-replace-confirm]').hidden = !replace;
      if (!replace) card.querySelector('[data-v095-replace-text]').value = '';
    };
    modeControl.addEventListener('change', () => {
      syncReplaceConfirmation();
      if (lastRestorePayload) {
        const sourceSha256 = lastRestorePreflight && lastRestorePreflight.sourceSha256;
        lastRestorePreflight = validateBackup(lastRestorePayload, card.querySelector('[data-v095-restore-mode]').value);
        if (sourceSha256) lastRestorePreflight.sourceSha256 = sourceSha256;
        renderPreflight(card.querySelector('[data-v095-restore-results]'), lastRestorePreflight);
        card.querySelector('[data-v095-apply-restore]').disabled = lastRestorePreflight.status === 'blocked';
      }
    });
    syncReplaceConfirmation();
  }

  function applyMotionPreference() {
    if (!window.matchMedia) return;
    const query = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => document.documentElement.classList.toggle('sc-lab-v095-reduced-motion', query.matches);
    update();
    if (query.addEventListener) query.addEventListener('change', update);
  }

  function init() {
    applyMotionPreference();
    const reportPanel = document.querySelector('[data-lab-module="report-studio"]');
    const visualizationPanel = document.querySelector('[data-lab-module="visualization-studio"]');
    const workspacePanel = document.querySelector('[data-lab-module="workspace-data"]');
    initComposer(reportPanel);
    initAccessibility(visualizationPanel || reportPanel);
    initRestore(workspacePanel);
    enhanceVisualizations(labRoot());
  }

  let attempts = 0;
  function retryInit() {
    init();
    attempts += 1;
    if (attempts < 24 && (!document.querySelector('[data-v095-report-composer]') || !document.querySelector('[data-v095-restore]'))) {
      setTimeout(retryInit, 250);
    }
  }

  const observer = new MutationObserver((mutations) => {
    if (!mutations.some((mutation) => mutation.addedNodes.length)) return;
    init();
    const root = labRoot();
    if (root !== document) enhanceVisualizations(root);
  });

  window.SCLabV095 = Object.freeze({
    version: VERSION,
    templates: clone(TEMPLATES),
    fingerprint,
    validateBackup,
    runAccessibilityAudit,
    runLegacyMigrationValidation,
    applyCompositionToReportStudio,
    init
  });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', retryInit, { once: true });
  else retryInit();
  observer.observe(document.documentElement, { childList: true, subtree: true });
}());
