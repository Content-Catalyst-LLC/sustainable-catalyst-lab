(function (w, d) {
  'use strict';

  const VERSION = '0.152.0.6';
  const aliases = Object.freeze({
    climate: 'climate-maps',
    evidence: 'evidence-decisions',
    marine: 'marine-biology',
    'astronomy-observations': 'space-telescopes'
  });

  function canonical(value) {
    const raw = String(value || 'overview').trim();
    return aliases[raw] || raw || 'overview';
  }

  function all(root, selector) {
    return root && root.querySelectorAll ? Array.from(root.querySelectorAll(selector)) : [];
  }

  function findPanel(root, id) {
    return all(root, '[data-lab-module]').find(function (panel) {
      return panel.dataset && panel.dataset.labModule === id;
    }) || null;
  }


  // The production safe boot intentionally excludes the legacy application bundle.
  // Use its canonical *project module*, not a duplicate store, for bounded record actions.
  function projectStore(root) {
    if (!root._scLabProjects) {
      if (!w.SCLab || typeof w.SCLab.Projects !== 'function') {
        throw new Error('Lab project store is unavailable. No record was saved.');
      }
      root._scLabProjects = new w.SCLab.Projects();
    }
    return root._scLabProjects;
  }

  function notify(root, message) {
    const target = root.querySelector('[data-lab-toast]');
    if (target) {
      target.textContent = message;
      target.hidden = false;
    }
  }

  function projectPicker(root) {
    const select = root.querySelector('[data-lab-project-select]');
    if (!select) return;
    const store = projectStore(root);
    select.replaceChildren();
    store.items.forEach(function (p) {
      const option = d.createElement('option');
      option.value = p.id;
      option.textContent = p.name;
      select.appendChild(option);
    });
    select.value = store.activeId;
  }

  function recordList(root, kind) {
    const isExperiment = kind === 'experiments';
    const list = root.querySelector(isExperiment ? '[data-experiment-list]' : '[data-note-list]');
    if (!list) return;
    const store = projectStore(root);
    const project = store.get();
    const query = isExperiment ? '' : String(root.querySelector('[data-note-filter]')?.value || '').toLowerCase();
    const rows = (project?.[isExperiment ? 'experiments' : 'notes'] || []).filter(function (record) {
      return !query || [record.title, record.body, ...(record.tags || [])].join(' ').toLowerCase().includes(query);
    });
    list.replaceChildren();
    if (!rows.length) {
      const empty = d.createElement('p');
      empty.className = 'sc-lab-data-note';
      empty.textContent = isExperiment ? 'No experiments recorded.' : 'No notebook entries match this filter.';
      list.appendChild(empty);
      return;
    }
    rows.forEach(function (record) {
      const article = d.createElement('article');
      article.className = 'sc-lab-list-item';
      const heading = d.createElement('h5');
      heading.textContent = String(record.title || 'Untitled record');
      const detail = d.createElement('p');
      detail.textContent = String(isExperiment ? (record.question || record.method || '') : (record.body || ''));
      const date = d.createElement('time');
      date.textContent = String(record.createdAt || '');
      article.appendChild(heading);
      if (detail.textContent) article.appendChild(detail);
      article.appendChild(date);
      list.appendChild(article);
    });
  }

  function promptFields(fields) {
    const data = {};
    for (const field of fields) {
      const answer = w.prompt(field[1], field[2]);
      if (answer === null) return null;
      data[field[0]] = answer;
    }
    return data;
  }

  function createRecord(root, action) {
    const configurations = {
      experiment: [
        ['title', 'Experiment title', 'New experiment'],
        ['question', 'Research question', ''],
        ['hypothesis', 'Hypothesis', ''],
        ['method', 'Method or procedure', '']
      ],
      note: [
        ['title', 'Notebook entry title', 'Lab note'],
        ['body', 'Observation or note', ''],
        ['tagsText', 'Tags, comma separated', 'observation']
      ],
      observation: [
        ['title', 'Observation title', 'Scientific observation'],
        ['body', 'What was observed?', ''],
        ['conditions', 'Conditions, instrument, or context', '']
      ]
    };
    if (!Object.prototype.hasOwnProperty.call(configurations, action)) return;
    // Prompt on a direct user gesture; never create a draft or make a write on cancellation.
    const record = promptFields(configurations[action]);
    if (!record) return;
    if (!String(record.title).trim()) {
      notify(root, 'A record title is required. No record was saved.');
      return;
    }
    try {
      const store = projectStore(root);
      if (action === 'experiment') {
        store.add('experiments', Object.assign({}, record, { status: 'planned' }), 'Experiment created: ' + record.title);
      } else if (action === 'observation') {
        const context = record.conditions ? '\n\nConditions: ' + record.conditions : '';
        store.add('notes', { type: 'observation', title: record.title, body: record.body + context, tags: ['observation'] },
          'Observation recorded: ' + record.title);
      } else {
        store.add('notes', { type: 'observation', title: record.title, body: record.body,
          tags: record.tagsText.split(',').map(function (v) { return v.trim(); }).filter(Boolean) },
          'Notebook entry added: ' + record.title);
      }
      projectPicker(root);
      const target = action === 'experiment' ? 'experiments' : 'notebook';
      openModule(root, target, true);
      notify(root, action === 'experiment' ? 'Experiment added to this project.' : 'Notebook entry saved to this project.');
    } catch (error) {
      notify(root, 'Unable to save record: ' + String(error?.message || error));
    }
  }

  function commandItems(root, query) {
    const api = w.SCLab?.Workspace;
    const matches = api && typeof api.search === 'function' ? api.search(query, []) : [];
    // Search only panels we can actually open in the safe shell; calculators require
    // the deferred optional runtime and must not appear as executable commands.
    const seen = new Set();
    return matches.filter(function (item) {
      if (item.kind !== 'module' || !findPanel(root, canonical(item.id)) || seen.has(item.id)) return false;
      seen.add(item.id);
      return true;
    }).slice(0, 12);
  }

  function renderCommandResults(root) {
    const input = root.querySelector('[data-lab-command-input]');
    const results = root.querySelector('[data-lab-command-results]');
    if (!input || !results) return;
    const value = String(input.value || '').trim();
    results.replaceChildren();
    if (!value) { results.hidden = true; return; }
    const items = commandItems(root, value);
    items.forEach(function (item) {
      const button = d.createElement('button');
      button.type = 'button';
      button.dataset.labCommandModule = item.id;
      const label = d.createElement('span');
      label.textContent = item.label;
      const group = d.createElement('small');
      group.textContent = item.group || 'Lab';
      button.appendChild(label);
      button.appendChild(group);
      results.appendChild(button);
    });
    results.hidden = items.length === 0;
  }

  function selectCommand(root, button) {
    if (!button) return;
    const input = root.querySelector('[data-lab-command-input]');
    const results = root.querySelector('[data-lab-command-results]');
    if (input) input.value = '';
    if (results) { results.hidden = true; results.replaceChildren(); }
    openModule(root, button.dataset.labCommandModule, true);
  }

  function syncReleasePresentation(root) {
    all(d, '.sc-lab-frame__version strong').forEach(function (node) {
      node.textContent = 'v' + VERSION;
    });
    all(d, '.sc-lab-frame').forEach(function (frame) {
      frame.dataset.labReleaseVersion = VERSION;
      frame.dataset.labPresentationAuthority = 'v015206';
    });
    if (root) {
      all(root, '.sc-lab-version').forEach(function (node) {
        node.textContent = 'v' + VERSION;
      });
    }
  }

  function clearLegacyRecoveryArtifacts() {
    all(d, '.sc-lab-production-banner-v0266').forEach(function (node) {
      node.remove();
    });
    d.documentElement.classList.remove('sc-lab-production-over-budget-v0266');
    d.documentElement.classList.remove('sc-lab-production-warning-v0266');
  }

  function markDeferred(panel) {
    if (!panel) return;
    const module = panel.dataset ? panel.dataset.labModule : '';
    const selectors = {
      'graph-studio': '[data-gs-v0470-status]',
      'model-studio': '[data-ms-v0460-status]',
      experiments: '[data-exp-v0300-status]'
    };
    const selector = selectors[module];
    if (!selector) return;
    const status = panel.querySelector(selector);
    if (status) {
      status.textContent = 'Lab safe boot is stabilized. Navigation is available; advanced module execution remains deferred while panel-aware loading is introduced.';
      status.dataset.tone = 'ready';
    }
  }

  function setActiveButtons(root, id) {
    all(root, '[data-lab-module-button]').forEach(function (button) {
      const active = button.dataset.labModuleButton === id;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-current', active ? 'page' : 'false');
    });
    all(root, '[data-open-module]').forEach(function (button) {
      const on = canonical(button.dataset.openModule) === id;
      button.classList.toggle('is-active', on);
      if (button.hasAttribute('data-v0481-workspace') || button.hasAttribute('data-v0483-primary')) {
        button.setAttribute('aria-current', on ? 'page' : 'false');
      }
    });
  }

  function openModule(root, requested, updateUrl) {
    const id = canonical(requested);
    const panel = findPanel(root, id);
    if (!panel) {
      // Do not silently replace an unavailable requested workspace with Overview.
      notify(root, 'Workspace unavailable in this Lab view: ' + id);
      return false;
    }
    const selected = panel.dataset.labModule || 'overview';

    all(root, '[data-lab-module]').forEach(function (item) {
      const active = item === panel;
      item.hidden = !active;
      item.setAttribute('aria-hidden', active ? 'false' : 'true');
    });

    root.dataset.activeModule = selected;
    root.dataset.scLabRuntimeState = 'safe-ready';
    root.dataset.scLabSafeBoot = VERSION;
    setActiveButtons(root, selected);
    if (selected === 'experiments' || selected === 'notebook') {
      try { recordList(root, selected); } catch (error) { notify(root, String(error.message || error)); }
    }
    markDeferred(panel);
    syncReleasePresentation(root);
    clearLegacyRecoveryArtifacts();

    const nav = root.querySelector('[data-lab-nav]');
    const navToggle = root.querySelector('[data-lab-nav-toggle]');
    if (nav) nav.classList.remove('is-open');
    if (navToggle) navToggle.setAttribute('aria-expanded', 'false');

    if (updateUrl && w.history && w.history.replaceState) {
      try {
        const url = new URL(w.location.href);
        if (selected === 'overview') url.searchParams.delete('sc_lab_module');
        else url.searchParams.set('sc_lab_module', selected);
        url.searchParams.delete('sc_lab_safe');
        url.searchParams.delete('sc_lab_recovery');
        w.history.replaceState({}, '', url.toString());
      } catch (_) {}
    }

    try {
      root.dispatchEvent(new CustomEvent('sc-lab:safe-module-opened', { detail: { module: selected, version: VERSION } }));
    } catch (_) {}
    return true;
  }

  function wire(root) {
    if (!root || root.dataset.scLabSafeBootWired === VERSION) return;
    root.dataset.scLabSafeBootWired = VERSION;
    root.dataset.scLabRuntimeState = 'safe-initializing';

    syncReleasePresentation(root);
    clearLegacyRecoveryArtifacts();

    root.addEventListener('click', function (event) {
      const command = event.target.closest('[data-lab-command-module]');
      if (command && root.contains(command)) {
        event.preventDefault();
        selectCommand(root, command);
        return;
      }
      const shortcut = event.target.closest('[data-lab-command-open], [data-v0483-search]');
      if (shortcut && root.contains(shortcut)) {
        event.preventDefault();
        root.querySelector('[data-lab-command-input]')?.focus();
        return;
      }
      const action = event.target.closest('[data-command-action]');
      if (action && root.contains(action)) {
        event.preventDefault();
        createRecord(root, action.dataset.commandAction);
        return;
      }
      if (event.target.closest('[data-new-experiment]')) {
        event.preventDefault();
        createRecord(root, 'experiment');
        return;
      }
      if (event.target.closest('[data-new-note]')) {
        event.preventDefault();
        createRecord(root, 'note');
        return;
      }
      const projectButton = event.target.closest('[data-lab-action]');
      if (projectButton && root.contains(projectButton)) {
        const name = projectButton.dataset.labAction;
        if (name === 'new-project') {
          event.preventDefault();
          const value = w.prompt('Project name', 'New Lab Project');
          if (value !== null && value.trim()) {
            try { projectStore(root).create(value.trim()); projectPicker(root); notify(root, 'Project created.'); }
            catch (error) { notify(root, String(error.message || error)); }
          }
          return;
        }
        if (name === 'export-project') {
          event.preventDefault();
          try { projectStore(root).export(); } catch (error) { notify(root, String(error.message || error)); }
          return;
        }
        if (name === 'import-project') {
          event.preventDefault();
          root.querySelector('[data-lab-import-file]')?.click();
          return;
        }
      }
      const open = event.target.closest('[data-open-module], [data-lab-module-button]');
      if (open && root.contains(open)) {
        event.preventDefault();
        const id = open.dataset.openModule || open.dataset.labModuleButton;
        openModule(root, id, true);
        return;
      }

      const navToggle = event.target.closest('[data-lab-nav-toggle]');
      if (navToggle && root.contains(navToggle)) {
        event.preventDefault();
        const nav = root.querySelector('[data-lab-nav]');
        if (nav) {
          const next = !nav.classList.contains('is-open');
          nav.classList.toggle('is-open', next);
          navToggle.setAttribute('aria-expanded', next ? 'true' : 'false');
        }
        return;
      }

      const toolsToggle = event.target.closest('[data-v0483-tools-toggle]');
      if (toolsToggle && root.contains(toolsToggle)) {
        event.preventDefault();
        const tools = root.querySelector('[data-v0483-tools]');
        if (tools) {
          tools.hidden = !tools.hidden;
          toolsToggle.setAttribute('aria-expanded', tools.hidden ? 'false' : 'true');
        }
        return;
      }

      const toolsClose = event.target.closest('[data-v0483-tools-close]');
      if (toolsClose && root.contains(toolsClose)) {
        const tools = root.querySelector('[data-v0483-tools]');
        if (tools) tools.hidden = true;
      }
    }, true);

    const search = root.querySelector('[data-v0483-tools-search]');
    if (search) {
      search.addEventListener('input', function () {
        const q = String(search.value || '').trim().toLowerCase();
        all(root, '[data-v0483-tools-groups] [data-lab-module-button]').forEach(function (button) {
          button.hidden = !!q && !String(button.textContent || '').toLowerCase().includes(q);
        });
      });
    }

    const select = root.querySelector('[data-lab-project-select]');
    if (select) select.addEventListener('change', function () {
      try { projectStore(root).select(select.value); projectPicker(root);
        if (root.dataset.activeModule === 'experiments' || root.dataset.activeModule === 'notebook') recordList(root, root.dataset.activeModule);
      } catch (error) { notify(root, String(error.message || error)); }
    });
    const file = root.querySelector('[data-lab-import-file]');
    if (file) file.addEventListener('change', function () {
      const chosen = file.files?.[0];
      if (!chosen) return;
      chosen.text().then(function (contents) {
        projectStore(root).import(contents);
        projectPicker(root);
        notify(root, 'Project imported.');
      }).catch(function (error) { notify(root, 'Project import failed: ' + String(error.message || error)); });
      file.value = '';
    });
    const notesFilter = root.querySelector('[data-note-filter]');
    if (notesFilter) notesFilter.addEventListener('input', function () {
      try { recordList(root, 'notebook'); } catch (error) { notify(root, String(error.message || error)); }
    });
    const commandInput = root.querySelector('[data-lab-command-input]');
    if (commandInput) {
      commandInput.addEventListener('input', function () { renderCommandResults(root); });
      commandInput.addEventListener('keydown', function (event) {
        const results = root.querySelector('[data-lab-command-results]');
        if (event.key === 'Escape') {
          if (results) results.hidden = true;
          commandInput.blur();
        } else if (event.key === 'Enter') {
          const first = results?.querySelector('[data-lab-command-module]');
          if (first) { event.preventDefault(); selectCommand(root, first); }
        } else if (event.key === 'ArrowDown') {
          const first = results?.querySelector('[data-lab-command-module]');
          if (first) { event.preventDefault(); first.focus(); }
        }
      });
    }
    const commandResults = root.querySelector('[data-lab-command-results]');
    if (commandResults) commandResults.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        event.preventDefault(); commandResults.hidden = true; commandInput?.focus();
      }
      if (event.key === 'Enter' && event.target.matches('[data-lab-command-module]')) {
        event.preventDefault(); selectCommand(root, event.target);
      }
    });
    const commandShortcut = root.querySelector('[data-lab-command-open]');
    if (commandShortcut) commandShortcut.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault(); commandInput?.focus();
      }
    });

    // Initialize only the canonical browser-local project model. The large optional
    // runtime remains deferred; no server operation or automatic publication occurs.
    try { projectPicker(root); } catch (error) { notify(root, 'Project initialization failed: ' + String(error.message || error)); }

    d.addEventListener('keydown', function (event) {
      if ((event.metaKey || event.ctrlKey) && String(event.key).toLowerCase() === 'k') {
        const input = root.querySelector('[data-lab-command-input]');
        if (input) { event.preventDefault(); input.focus(); }
      }
    });

    let initial = root.dataset.initialModule || 'overview';
    try { initial = new URL(w.location.href).searchParams.get('sc_lab_module') || initial; } catch (_) {}
    openModule(root, initial, false);
  }

  function boot() {
    clearLegacyRecoveryArtifacts();
    syncReleasePresentation(null);
    all(d, '.sc-lab-app').forEach(wire);
  }

  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();

  w.SCLabSafeBootV015206Runtime = Object.freeze({ version: VERSION, boot: boot });
})(window, document);
