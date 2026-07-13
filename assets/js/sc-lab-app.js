(function (w, d) {
  'use strict';

  const Lab = w.SCLab;
  const U = Lab.util;

  function qs(root, selector) { return root.querySelector(selector); }
  function qsa(root, selector) { return [...root.querySelectorAll(selector)]; }
  function empty(text) { return `<div class="sc-lab-data-note">${U.esc(text)}</div>`; }

  function promptRecord(fields) {
    const record = {};
    for (const [key, title, defaultValue = ''] of fields) {
      const value = w.prompt(title, defaultValue);
      if (value === null) return null;
      record[key] = value;
    }
    return record;
  }

  function listHTML(title, body, time, meta = '') {
    return `<article class="sc-lab-list-item">
      <header><h5>${U.esc(title)}</h5><time>${U.esc(U.fmt(time))}</time></header>
      ${body ? `<p>${U.esc(body)}</p>` : ''}
      ${meta ? `<span class="sc-lab-list-meta">${U.esc(meta)}</span>` : ''}
    </article>`;
  }

  function csvCell(value) {
    const text = String(value ?? '');
    return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  }

  function init(root) {
    const projects = new Lab.Projects();
    const config = w.SCLabConfig || {};
    const initial = root.dataset.initialModule || 'overview';
    const select = qs(root, '[data-lab-project-select]');
    const file = qs(root, '[data-lab-import-file]');
    const nav = qs(root, '[data-lab-nav]');
    const navToggle = qs(root, '[data-lab-nav-toggle]');
    const commandInput = qs(root, '[data-lab-command-input]');
    const commandResults = qs(root, '[data-lab-command-results]');
    let currentDocument = null;
    let overviewLoaded = false;
    let currentDataset = null;
    let currentFeedRecords = [];
    let currentSpaceRecords = [];
    let currentMarineRecords = [];
    let spectrum = [];

    function renderSelect() {
      select.innerHTML = '';
      projects.items.forEach(project => {
        const option = d.createElement('option');
        option.value = project.id;
        option.textContent = project.name;
        option.selected = project.id === projects.activeId;
        select.appendChild(option);
      });
    }

    function closeMobileNav() {
      nav.classList.remove('is-open');
      navToggle?.setAttribute('aria-expanded', 'false');
    }

    function openModule(id, options = {}) {
      const exists = qsa(root, '[data-lab-module]').find(panel => panel.dataset.labModule === id);
      if (!exists) return;
      qsa(root, '[data-lab-module]').forEach(panel => { panel.hidden = panel.dataset.labModule !== id; });
      qsa(root, '[data-lab-module-button]').forEach(button => button.classList.toggle('is-active', button.dataset.labModuleButton === id));
      root.dataset.activeModule = id;
      closeMobileNav();

      if (id === 'overview') renderOverview();
      if (id === 'activity') renderActivity();
      if (id === 'experiments') renderExperiments();
      if (id === 'evidence-decisions') renderEvidence();
      if (id === 'notebook') renderNotes();
      if (id === 'system-status') runStatus(false);
      if (id === 'source-registry') loadSourceRegistry();
      if (id === 'dataset-inspector') renderDataset();
      if (options.focus) requestAnimationFrame(() => options.focus.focus());
    }

    function setTab(buttonSelector, buttonData, paneSelector, paneData, value) {
      qsa(root, buttonSelector).forEach(button => button.classList.toggle('is-active', button.dataset[buttonData] === value));
      qsa(root, paneSelector).forEach(pane => { pane.hidden = pane.dataset[paneData] !== value; });
    }

    function openTool(id) {
      const item = Lab.Workspace.quickTools.find(tool => tool.id === id)
        || { kind: 'calculator', module: 'science-engineering', calculatorId: id };
      openModule(item.module);
      if (item.kind === 'chem-tab') setTab('[data-chem-tab]', 'chemTab', '[data-chem-pane]', 'chemPane', item.tab);
      if (item.kind === 'analysis-tab') setTab('[data-analysis-tab]', 'analysisTab', '[data-analysis-pane]', 'analysisPane', item.tab);
      if (item.kind === 'physics-tab') setTab('[data-physics-tab]', 'physicsTab', '[data-physics-pane]', 'physicsPane', item.tab);
      if (item.kind === 'biology-tab') setTab('[data-biology-tab]', 'biologyTab', '[data-biology-pane]', 'biologyPane', item.tab);
      if (item.kind === 'astronomy-tab') setTab('[data-astronomy-tab]', 'astronomyTab', '[data-astronomy-pane]', 'astronomyPane', item.tab);
      if (item.kind === 'materials-tab') setTab('[data-materials-tab]', 'materialsTab', '[data-materials-pane]', 'materialsPane', item.tab);
      if (item.kind === 'earth-tab') setTab('[data-earth-tab]', 'earthTab', '[data-earth-pane]', 'earthPane', item.tab);
      if (item.kind === 'energy-tab') setTab('[data-energy-tab]', 'energyTab', '[data-energy-pane]', 'energyPane', item.tab);
      if (item.kind === 'calculator') {
        setTab('[data-analysis-tab]', 'analysisTab', '[data-analysis-pane]', 'analysisPane', 'calculators');
        selectCalculator(item.calculatorId);
      }
    }

    function executeCommand(item) {
      commandInput.value = '';
      commandResults.hidden = true;
      if (item.kind === 'module') openModule(item.id);
      else if (item.kind === 'calculator') openTool(item.calculatorId || item.id);
      else openTool(item.id);
    }

    function renderCommandResults(query) {
      const matches = Lab.Workspace.search(query, Lab.Calculators.definitions);
      if (!query.trim() || !matches.length) {
        commandResults.hidden = true;
        commandResults.innerHTML = '';
        return;
      }
      commandResults.innerHTML = matches.map((item, index) => `
        <button type="button" data-command-index="${index}">
          <span>${U.esc(item.label)}</span>
          <small>${U.esc(item.group || item.kind || 'Lab')}</small>
        </button>`).join('');
      commandResults.hidden = false;
      qsa(commandResults, '[data-command-index]').forEach(button => {
        button.addEventListener('click', () => executeCommand(matches[Number(button.dataset.commandIndex)]));
      });
    }

    function createExperiment(seed = {}) {
      const record = promptRecord([
        ['title', 'Experiment title', seed.title || 'New experiment'],
        ['question', 'Research question', seed.question || ''],
        ['hypothesis', 'Hypothesis', seed.hypothesis || ''],
        ['method', 'Method or procedure', seed.method || '']
      ]);
      if (!record) return;
      projects.add('experiments', { ...record, status: 'planned' }, `Experiment created: ${record.title}`);
      U.toast(root, 'Experiment added to the project.');
    }

    function createNote(seed = {}) {
      const record = promptRecord([
        ['title', 'Notebook entry title', seed.title || 'Lab note'],
        ['body', 'Observation or note', seed.body || ''],
        ['tagsText', 'Tags, comma separated', seed.tagsText || 'observation']
      ]);
      if (!record) return;
      projects.add('notes', {
        type: seed.type || 'observation',
        title: record.title,
        body: record.body,
        tags: record.tagsText.split(',').map(tag => tag.trim()).filter(Boolean)
      }, `Notebook entry added: ${record.title}`);
      U.toast(root, 'Notebook entry saved.');
    }

    function createObservation() {
      const record = promptRecord([
        ['title', 'Observation title', 'Scientific observation'],
        ['body', 'What was observed?', ''],
        ['conditions', 'Conditions, instrument, or context', '']
      ]);
      if (!record) return;
      projects.add('notes', {
        type: 'observation',
        title: record.title,
        body: `${record.body}${record.conditions ? `\n\nConditions: ${record.conditions}` : ''}`,
        tags: ['observation']
      }, `Observation recorded: ${record.title}`);
      U.toast(root, 'Observation added to the notebook.');
    }

    function handleQuickAction(action) {
      if (action === 'experiment') createExperiment();
      if (action === 'note') createNote();
      if (action === 'observation') createObservation();
    }

    function metricHTML(label, value, module) {
      return `<button type="button" class="sc-lab-metric" data-open-module="${U.esc(module)}"><strong>${value}</strong><span>${U.esc(label)}</span></button>`;
    }

    function renderTrace() {
      const target = qs(root, '[data-traceability]');
      target.innerHTML = Lab.Workspace.traceCounts(projects.get()).map((stage, index, rows) => `
        <button type="button" class="sc-lab-trace-stage" data-open-module="${U.esc(stage.module)}" data-trace-key="${U.esc(stage.key)}">
          <strong>${stage.value}</strong><span>${U.esc(stage.label)}</span>
        </button>${index < rows.length - 1 ? '<span class="sc-lab-trace-arrow" aria-hidden="true">→</span>' : ''}`
      ).join('');
    }

    function renderProjectWork() {
      const project = projects.get();
      const experiments = project.experiments.slice(0, 3).map(item => ({
        title: item.title || 'Untitled experiment',
        body: item.question || item.method || '',
        time: item.createdAt,
        meta: `Experiment · ${item.status || 'planned'}`
      }));
      const calculations = project.calculations.slice(0, 3).map(item => ({
        title: item.type || 'Calculation',
        body: item.calculatorId ? `Calculator: ${item.calculatorId}` : '',
        time: item.createdAt,
        meta: 'Calculation'
      }));
      const biology = project.biologyRecords.slice(0, 3).map(item => ({
        title: item.type || 'Biology analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Biology'
      }));
      const astronomy = project.astronomyRecords.slice(0, 3).map(item => ({
        title: item.type || 'Astronomy analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Astronomy'
      }));
      const materials = project.materialsRecords.slice(0, 3).map(item => ({
        title: item.type || 'Materials analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Materials'
      }));
      const earth = project.earthRecords.slice(0, 3).map(item => ({
        title: item.type || 'Earth systems analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Earth systems'
      }));
      const energy = project.energyRecords.slice(0, 3).map(item => ({
        title: item.type || 'Energy and engineering analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Energy & engineering'
      }));
  const electrical = project.electricalRecords.slice(0, 3).map(item => ({
  title: item.type || 'Electrical and embedded analysis',
  body: item.methodId ? `Method: ${item.methodId}` : '',
  time: item.createdAt || item.recordedAt,
  meta: 'Electrical & embedded'
  }));
  const mechanical = project.mechanicalThermalAnalyses.slice(0, 3).map(item => ({
  title: item.title || item.type || 'Mechanical and thermal analysis',
  body: item.methodId ? `Method: ${item.methodId}` : '',
  time: item.createdAt || item.recordedAt || item.audit?.createdAt,
  meta: 'Mechanical & thermal'
  }));
      const rows = [...experiments, ...calculations, ...biology, ...astronomy, ...materials, ...earth, ...energy, ...electrical, ...mechanical]
        .sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
        .slice(0, 5);
      qs(root, '[data-project-work]').innerHTML = rows.length
        ? rows.map(row => listHTML(row.title, row.body, row.time, row.meta)).join('')
        : empty('No experiments or calculations have been recorded.');
    }

    function renderOverview() {
      const project = projects.get();
      const counts = [
        ['Evidence', project.evidence.length, 'evidence-decisions'],
        ['Experiments', project.experiments.length, 'experiments'],
        ['Calculations', project.calculations.length, 'science-engineering'],
        ['Notes', project.notes.length, 'notebook'],
        ['Decisions', project.decisions.length, 'evidence-decisions'],
        ['Documents', project.documents.length, 'documentation'],
        ['Biology', project.biologyRecords.length, 'biology'],
        ['Astronomy', project.astronomyRecords.length, 'astronomy'],
        ['Materials', project.materialsRecords.length, 'materials'],
        ['Earth systems', project.earthRecords.length, 'earth-systems'],
        ['Energy & engineering', project.energyRecords.length, 'energy-engineering'],
  ['Electrical & embedded', project.electricalRecords.length, 'electrical-embedded'],
  ['Mechanical & thermal', project.mechanicalThermalAnalyses.length, 'mechanical-thermal']
      ];
      qs(root, '[data-overview-metrics]').innerHTML = counts.map(([label, value, module]) => metricHTML(label, value, module)).join('');
      qs(root, '[data-recent-activity]').innerHTML = project.activity.slice(0, 8).map(item => listHTML(item.text, '', item.at)).join('') || empty('No project activity yet.');
      renderProjectWork();
      renderTrace();
      qs(root, '[data-overview-empty]').hidden = Lab.Workspace.projectTotal(project) > 0;
      if (!overviewLoaded && config.features?.feeds !== false) loadOverviewSignals();
    }

    async function loadOverviewSignals() {
      const target = qs(root, '[data-overview-signals]');
      overviewLoaded = true;
      target.innerHTML = '<div class="sc-lab-data-note">Retrieving concise scientific signals…</div>';
      const requests = [
        ['usgs-earthquakes', '', 2],
        ['nasa-eonet', '', 2],
        ['nasa-space-telescopes', 'James Webb Hubble', 2],
        ['obis-marine', 'Cetacea', 2],
        ['pubmed-science', 'environmental monitoring OR materials science', 2],
        ['arxiv-physics', 'all:physics OR all:materials', 2]
      ];
      const results = await Promise.allSettled(requests.map(args => Lab.Feeds.load(...args)));
      const records = results.flatMap(result => result.status === 'fulfilled' ? (result.value.records || []) : []);
      if (!records.length) {
        target.innerHTML = empty('Live signals are temporarily unavailable. Open Scientific signals to query an individual source.');
        return;
      }
      records.sort((a, b) => String(b.observedAt || '').localeCompare(String(a.observedAt || '')));
      Lab.Feeds.render(target, records.slice(0, 8), projects, root, { compact: true });
    }

    function renderActivity() {
      const filter = (qs(root, '[data-activity-filter]')?.value || '').toLowerCase();
      const limit = Number(qs(root, '[data-activity-limit]')?.value || 50);
      const rows = projects.get().activity
        .filter(item => !filter || String(item.text || '').toLowerCase().includes(filter))
        .slice(0, limit);
      qs(root, '[data-activity-list]').innerHTML = rows.map(item => listHTML(item.text, '', item.at)).join('') || empty('No matching activity.');
    }

    function renderExperiments() {
      const rows = projects.get().experiments;
      qs(root, '[data-experiment-list]').innerHTML = rows.map(item => listHTML(item.title, item.question || item.method, item.createdAt, item.status || 'planned')).join('') || empty('No experiments recorded.');
    }

    function renderEvidence() {
      const project = projects.get();
      qs(root, '[data-evidence-list]').innerHTML = project.evidence.map(item => listHTML(item.title, item.summary, item.createdAt, `${item.source || 'Source'} · ${item.status || 'unreviewed'}`)).join('') || empty('No evidence saved.');
      qs(root, '[data-hypothesis-list]').innerHTML = project.hypotheses.map(item => listHTML(item.title, item.statement, item.createdAt, item.status || 'proposed')).join('') || empty('No hypotheses recorded.');
      qs(root, '[data-decision-list]').innerHTML = project.decisions.map(item => listHTML(item.title, item.rationale, item.createdAt, item.status || 'draft')).join('') || empty('No decisions recorded.');
    }

    function renderNotes() {
      const query = (qs(root, '[data-note-filter]').value || '').toLowerCase();
      const rows = projects.get().notes.filter(item => {
        const text = `${item.title || ''} ${item.body || ''} ${(item.tags || []).join(' ')}`.toLowerCase();
        return !query || text.includes(query);
      });
      qs(root, '[data-note-list]').innerHTML = rows.map(item => listHTML(item.title, item.body, item.createdAt, `${item.type || 'note'} · ${(item.tags || []).join(', ')}`)).join('') || empty('No notebook entries match this filter.');
    }

    function renderSelectAndViews() {
      renderSelect();
      renderOverview();
      if (root.dataset.activeModule === 'activity') renderActivity();
      if (root.dataset.activeModule === 'experiments') renderExperiments();
      if (root.dataset.activeModule === 'evidence-decisions') renderEvidence();
      if (root.dataset.activeModule === 'notebook') renderNotes();
      updateDocStale();
      populateDatasetSelect();
    }

    qsa(root, '[data-lab-module-button]').forEach(button => button.addEventListener('click', () => openModule(button.dataset.labModuleButton)));
    root.addEventListener('click', event => {
      const moduleButton = event.target.closest('[data-open-module]');
      if (moduleButton && root.contains(moduleButton)) openModule(moduleButton.dataset.openModule);
      const quickTool = event.target.closest('[data-quick-tool]');
      if (quickTool && root.contains(quickTool)) openTool(quickTool.dataset.quickTool);
      const commandAction = event.target.closest('[data-command-action]');
      if (commandAction && root.contains(commandAction)) handleQuickAction(commandAction.dataset.commandAction);
    });

    navToggle?.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(open));
    });

    qsa(root, '[data-route]').forEach(link => { link.href = config.routes?.[link.dataset.route] || '#'; });
    select.addEventListener('change', () => projects.select(select.value));
    qs(root, '[data-lab-action="new-project"]').addEventListener('click', () => {
      const name = w.prompt('Project name', 'New Lab Project');
      if (name) { projects.create(name); U.toast(root, 'Project created.'); }
    });
    qs(root, '[data-lab-action="export-project"]').addEventListener('click', () => projects.export());
    qs(root, '[data-lab-action="import-project"]').addEventListener('click', () => file.click());
    file.addEventListener('change', () => {
      const selectedFile = file.files[0];
      if (!selectedFile) return;
      selectedFile.text().then(text => {
        projects.import(text);
        U.toast(root, 'Project imported.');
      }).catch(error => U.toast(root, error.message));
      file.value = '';
    });
    projects.onChange(renderSelectAndViews);

    commandInput.addEventListener('input', () => renderCommandResults(commandInput.value));
    commandInput.addEventListener('keydown', event => {
      if (event.key === 'Escape') { commandResults.hidden = true; commandInput.blur(); }
      if (event.key === 'Enter') {
        const first = qs(commandResults, '[data-command-index="0"]');
        if (first) { event.preventDefault(); first.click(); }
      }
    });
    d.addEventListener('keydown', event => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        commandInput.focus();
        commandInput.select();
      }
      if (event.key === '/' && !/input|textarea|select/i.test(d.activeElement?.tagName || '')) {
        event.preventDefault();
        commandInput.focus();
      }
    });
    d.addEventListener('click', event => {
      if (!root.contains(event.target) || !event.target.closest('.sc-lab-command-search')) commandResults.hidden = true;
    });

    qs(root, '[data-overview-refresh]').addEventListener('click', () => { overviewLoaded = false; loadOverviewSignals(); });

    // Scientific feeds.
    async function feedTo(source, query, limit, target, status) {
      if (status) status.textContent = 'Loading scientific source…';
      try {
        let records = [], retrievedAt = U.now(), cached = false;
        if (source === 'all-science') {
          records = await Lab.Observations.loadBoard();
        } else {
          const data = await Lab.Feeds.load(source, query, limit);
          records = data.records || []; retrievedAt = data.retrievedAt; cached = !!data.cached;
        }
        currentFeedRecords = records;
        Lab.Feeds.render(target, records, projects, root);
        qs(root,'[data-feed-to-dataset]').disabled = !records.length;
        qs(root,'[data-save-query]').disabled = !records.length;
        if (status) status.textContent = `${records.length} records · ${source==='all-science'?'multi-source board':cached?'cached':'live retrieval'} · ${U.fmt(retrievedAt)}`;
        return records;
      } catch (error) { target.innerHTML=empty(error.message); if(status)status.textContent=error.message; return []; }
    }

    const feedSource = qs(root, '[data-feed-source]');
    const feedQuery = qs(root, '[data-feed-query]');
    const feedLimit = qs(root, '[data-feed-limit]');
    const feedTarget = qs(root, '[data-feed-results]');
    const feedStatus = qs(root, '[data-feed-status]');
    const runFeed = () => feedTo(feedSource.value, feedQuery.value, Number(feedLimit.value), feedTarget, feedStatus);
    qs(root, '[data-feed-run]').addEventListener('click', runFeed);
    qs(root, '[data-feed-refresh]').addEventListener('click', runFeed);
    qs(root, '[data-space-load]').addEventListener('click', async () => { const telescope=qs(root,'[data-space-telescope]').value; const query=`${telescope==='all'?'':telescope+' '} ${qs(root,'[data-space-query]').value}`.trim(); currentSpaceRecords=await feedTo('nasa-space-telescopes',query,Number(qs(root,'[data-space-limit]').value),qs(root,'[data-space-results]')); qs(root,'[data-space-dataset]').disabled=!currentSpaceRecords.length; const groups={};currentSpaceRecords.forEach(r=>{const t=Lab.Observations.telescope(r);groups[t]=(groups[t]||0)+1});qs(root,'[data-space-summary]').textContent=Object.entries(groups).map(([k,v])=>`${k}: ${v}`).join(' · ')||'No observations returned.'; });
    qs(root, '[data-marine-load]').addEventListener('click', async () => { currentMarineRecords=await feedTo('obis-marine',qs(root,'[data-marine-query]').value,Number(qs(root,'[data-marine-limit]').value),qs(root,'[data-marine-results]')); qs(root,'[data-marine-dataset]').disabled=!currentMarineRecords.length; const taxa=Lab.Observations.taxonSummary(currentMarineRecords).slice(0,6);qs(root,'[data-marine-summary]').textContent=`${currentMarineRecords.length} occurrences · `+taxa.map(([n,c])=>`${n}: ${c}`).join(' · '); renderMarineChart(); });


    function loadDataset(dataset){ currentDataset=dataset; openModule('dataset-inspector'); renderDataset(); }
    root.addEventListener('sc-lab:dataset',event=>loadDataset(Lab.Datasets.fromRecords(event.detail.records,{title:event.detail.title,source:event.detail.source})));
    qs(root,'[data-feed-to-dataset]').addEventListener('click',()=>loadDataset(Lab.Datasets.fromRecords(currentFeedRecords,{title:'Scientific observation board',source:feedSource.value,query:{q:feedQuery.value,limit:Number(feedLimit.value)}})));
    qs(root,'[data-space-dataset]').addEventListener('click',()=>loadDataset(Lab.Datasets.fromRecords(currentSpaceRecords,{title:'Space telescope observations',source:'NASA Image and Video Library'})));
    qs(root,'[data-marine-dataset]').addEventListener('click',()=>loadDataset(Lab.Datasets.fromRecords(currentMarineRecords,{title:'Marine biodiversity occurrences',source:'OBIS'})));
    qs(root,'[data-save-query]').addEventListener('click',()=>{projects.add('savedQueries',{source:feedSource.value,q:feedQuery.value,limit:Number(feedLimit.value),recordCount:currentFeedRecords.length},`Scientific query saved: ${feedSource.value}`);U.toast(root,'Query saved to project.');});
    function datasetRows(){return currentDataset?Lab.Datasets.filter(currentDataset,qs(root,'[data-dataset-filter]').value):[];}
    function populateDatasetSelect(){const sel=qs(root,'[data-dataset-select]');const value=sel.value;sel.innerHTML='<option value="">Current working dataset</option>'+projects.get().datasets.map(x=>`<option value="${U.esc(x.id)}">${U.esc(x.title||'Dataset')}</option>`).join('');sel.value=value;}
    function renderDataset(){populateDatasetSelect();const header=qs(root,'[data-dataset-header]'),table=qs(root,'[data-dataset-table]'),chart=qs(root,'[data-dataset-chart]');if(!currentDataset){header.textContent='No dataset loaded. Open feed results, import CSV, or select a saved project dataset.';table.innerHTML=empty('No dataset loaded.');chart.innerHTML=empty('No dataset loaded.');return;}const rows=datasetRows(),stats=Lab.Datasets.summary(currentDataset,rows);header.textContent=`${currentDataset.title} · ${currentDataset.source} · ${rows.length} filtered rows / ${currentDataset.rows.length} total`;const selects=[qs(root,'[data-dataset-x]'),qs(root,'[data-dataset-y]')];selects.forEach((sel,i)=>{const prev=sel.value;sel.innerHTML=(i===0?'<option value="">Row index</option>':'<option value="">Select numeric variable</option>')+currentDataset.columns.map(c=>`<option>${U.esc(c)}</option>`).join('');if(currentDataset.columns.includes(prev))sel.value=prev;});if(!qs(root,'[data-dataset-y]').value){const num=Object.keys(stats.numeric)[0];if(num)qs(root,'[data-dataset-y]').value=num;}qs(root,'[data-dataset-stats]').innerHTML=`<div><strong>${stats.rows}</strong><span>Rows</span></div><div><strong>${stats.columns}</strong><span>Variables</span></div><div><strong>${stats.missing}</strong><span>Missing cells</span></div><div><strong>${Object.keys(stats.numeric).length}</strong><span>Numeric variables</span></div>`;Lab.Datasets.renderTable(table,currentDataset,rows,Number(qs(root,'[data-dataset-limit]').value));Lab.Datasets.renderChart(chart,currentDataset,rows,qs(root,'[data-dataset-x]').value,qs(root,'[data-dataset-y]').value);}
    ['[data-dataset-filter]','[data-dataset-x]','[data-dataset-y]','[data-dataset-limit]'].forEach(sel=>qs(root,sel).addEventListener(sel.includes('filter')?'input':'change',renderDataset));
    qs(root,'[data-dataset-select]').addEventListener('change',e=>{const found=projects.get().datasets.find(x=>x.id===e.target.value);if(found){currentDataset=found;renderDataset();}});
    qs(root,'[data-dataset-import-run]').addEventListener('click',()=>{try{const raw=qs(root,'[data-dataset-import]').value.trim();if(!raw)throw new Error('Paste CSV or JSON first.');currentDataset=raw[0]==='['?Lab.Datasets.fromRecords(JSON.parse(raw),{title:'Imported JSON dataset',source:'User import'}):Lab.Datasets.parseCSV(raw);renderDataset();}catch(error){U.toast(root,error.message);}});
    qs(root,'[data-dataset-save]').addEventListener('click',()=>{if(!currentDataset)return U.toast(root,'Load a dataset first.');const saved=JSON.parse(JSON.stringify(currentDataset));saved.id=U.uid('datasets');projects.add('datasets',saved,`Dataset saved: ${saved.title}`);U.toast(root,'Dataset saved to project.');});
    qs(root,'[data-dataset-export]').addEventListener('click',()=>{if(currentDataset)U.download(`${(currentDataset.title||'dataset').replace(/[^a-z0-9]+/gi,'-').toLowerCase()}.csv`,Lab.Datasets.csv(currentDataset,datasetRows()),'text/csv');});
    function renderMarineChart(){const points=Lab.Observations.depthSeries(currentMarineRecords);const target=qs(root,'[data-marine-chart]');if(!points.length){target.innerHTML='<div class="sc-lab-data-note">No depth values were supplied by these records.</div>';return;}const max=Math.max(...points.map(p=>p.depth),1);target.innerHTML=`<svg viewBox="0 0 700 140"><line x1="35" y1="15" x2="35" y2="120" stroke="#89949d"/><line x1="35" y1="120" x2="680" y2="120" stroke="#89949d"/>${points.map((p,i)=>`<circle cx="${35+i*(640/Math.max(points.length-1,1))}" cy="${15+p.depth/max*100}" r="3" fill="#d00000"/>`).join('')}<text x="5" y="18" font-size="10">0 m</text><text x="2" y="120" font-size="10">${max.toFixed(0)} m</text></svg>`;}

    // Climate map.
    const climateDate = qs(root, '[data-climate-date]');
    climateDate.value = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    function renderMap() {
      const layer=qs(root,'[data-climate-layer]').value,bbox=qs(root,'[data-climate-region]').value;qs(root,'[data-climate-metadata]').innerHTML=`<span>Layer: ${U.esc(Lab.ClimateMap.layers[layer]?.label||layer)}</span><span>Date: ${U.esc(climateDate.value)}</span><span>Region: ${U.esc(bbox)}</span><span>Unit: ${U.esc(Lab.ClimateMap.layers[layer]?.unit||'source-defined')}</span>`;
      return Lab.ClimateMap.render(
        qs(root, '[data-climate-image]'),
        qs(root, '[data-climate-layer]').value,
        climateDate.value,
        qs(root, '[data-climate-region]').value,
        qs(root, '[data-climate-loading]')
      );
    }
    qs(root, '[data-climate-render]').addEventListener('click', renderMap);
    qs(root,'[data-climate-opacity]').addEventListener('input',e=>qs(root,'[data-climate-image]').style.opacity=Number(e.target.value)/100);
    qs(root,'[data-climate-image]').addEventListener('click',event=>{const point=Lab.ClimateMap.coordinate(event,qs(root,'[data-climate-image]'),qs(root,'[data-climate-region]').value);qs(root,'[data-climate-readout]').textContent=`Selected coordinate: ${point.latitude.toFixed(4)}, ${point.longitude.toFixed(4)}`;projects.add('observations',{title:'Climate map coordinate',source:'NASA GIBS',location:point,layer:qs(root,'[data-climate-layer]').value,date:climateDate.value},`Map coordinate observed: ${point.latitude.toFixed(3)}, ${point.longitude.toFixed(3)}`);});
    qs(root,'[data-climate-export]').addEventListener('click',()=>{const record={source:'NASA GIBS',layer:qs(root,'[data-climate-layer]').value,date:climateDate.value,bbox:qs(root,'[data-climate-region]').value,url:renderMap()};U.download('lab-climate-map.json',JSON.stringify(record,null,2),'application/json');});
    qs(root, '[data-climate-save]').addEventListener('click', () => {
      const record = {
        title: 'NASA GIBS climate map',
        layer: qs(root, '[data-climate-layer]').value,
        date: climateDate.value,
        bbox: qs(root, '[data-climate-region]').value,
        url: renderMap()
      };
      projects.add('mapViews', record, `Climate map saved: ${record.layer}`);
      U.toast(root, 'Climate map state saved.');
    });
    renderMap();

    // Chemistry Laboratory and Spectrometry Studio.
    let rawSpectrum = [];
    let spectrumHistory = [];
    let detectedPeaks = [];
    let currentChemCalibration = null;
    let currentSpectrumCalibration = null;

    const periodic = qs(root, '[data-periodic-table]');
    const elementDetail = qs(root, '[data-element-detail]');
    Lab.Periodic.load(config.elementsUrl).then(elements => {
      Lab.Stoichiometry.setElements(elements);
      drawElements();
    }).catch(error => { elementDetail.textContent = error.message; });

    function drawElements() {
      Lab.Periodic.render(periodic, elementDetail, {
        query: qs(root, '[data-element-search]').value,
        property: qs(root, '[data-element-property]').value
      });
    }
    qs(root, '[data-element-search]').addEventListener('input', drawElements);
    qs(root, '[data-element-property]').addEventListener('change', drawElements);
    qsa(root, '[data-chem-tab]').forEach(button => button.addEventListener('click', () => setTab('[data-chem-tab]', 'chemTab', '[data-chem-pane]', 'chemPane', button.dataset.chemTab)));
    qsa(root, '[data-analysis-tab]').forEach(button => button.addEventListener('click', () => setTab('[data-analysis-tab]', 'analysisTab', '[data-analysis-pane]', 'analysisPane', button.dataset.analysisTab)));

    qs(root, '[data-chem-new-experiment]').addEventListener('click', () => createExperiment({ title: 'Chemistry experiment', question: 'What chemical behavior or analytical result is being investigated?' }));
    qs(root, '[data-chem-notebook]').addEventListener('click', () => createNote({ title: 'Chemistry laboratory note', tagsText: 'chemistry, laboratory' }));

    function recordCalculation(type, input, result, collection = 'calculations') {
      projects.add(collection, { type, input, result, methodVersion: '0.9.4' }, `${type} completed`);
      return result;
    }

    function bindResult(buttonSelector, outputSelector, type, inputFn, calculationFn, collection = 'calculations') {
      qs(root, buttonSelector).addEventListener('click', () => {
        const output = qs(root, outputSelector);
        try {
          const input = inputFn();
          const result = calculationFn(input);
          output.textContent = JSON.stringify(result, null, 2);
          recordCalculation(type, input, result, collection);
        } catch (error) { output.textContent = `Error: ${error.message}`; }
      });
    }

    bindResult('[data-formula-run]', '[data-formula-output]', 'Molar mass',
      () => ({ formula: qs(root, '[data-formula-input]').value }),
      input => Lab.Stoichiometry.molarMass(input.formula));
    bindResult('[data-percent-run]', '[data-formula-output]', 'Percent composition',
      () => ({ formula: qs(root, '[data-formula-input]').value }),
      input => Lab.ChemistryLab.percentComposition(input.formula), 'chemicalRecords');
    bindResult('[data-empirical-run]', '[data-empirical-output]', 'Empirical formula',
      () => JSON.parse(qs(root, '[data-empirical-input]').value),
      input => Lab.ChemistryLab.empiricalFormula(input), 'chemicalRecords');
    bindResult('[data-molecular-run]', '[data-molecular-output]', 'Molecular formula',
      () => ({ empiricalFormula: qs(root, '[data-molecular-empirical]').value, molecularMass: qs(root, '[data-molecular-mass]').value }),
      input => Lab.ChemistryLab.molecularFormula(input), 'chemicalRecords');
    bindResult('[data-balance-run]', '[data-balance-output]', 'Equation balance',
      () => ({ equation: qs(root, '[data-balance-input]').value }),
      input => Lab.Stoichiometry.balanceEquation(input.equation));
    bindResult('[data-limit-run]', '[data-limit-output]', 'Limiting reagent',
      () => ({ equation: qs(root, '[data-limit-equation]').value, moles: JSON.parse(qs(root, '[data-limit-moles]').value) }),
      input => Lab.Stoichiometry.limitingReagent(input.equation, input.moles));
    bindResult('[data-yield-run]', '[data-yield-output]', 'Theoretical yield',
      () => ({ formula: qs(root, '[data-yield-product]').value, moles: qs(root, '[data-yield-moles]').value }),
      input => Lab.Stoichiometry.theoreticalYield(input.formula, input.moles));

    qs(root, '[data-reaction-save]').addEventListener('click', () => {
      const output = qs(root, '[data-reaction-save-output]');
      try {
        const equation = qs(root, '[data-limit-equation]').value || qs(root, '[data-balance-input]').value;
        const balanced = Lab.Stoichiometry.balanceEquation(equation);
        const record = {
          title: qs(root, '[data-reaction-title]').value || 'Chemical reaction',
          equation,
          balancedEquation: balanced.balanced,
          coefficients: balanced.coefficients,
          conditions: qs(root, '[data-reaction-conditions]').value,
          status: 'planned'
        };
        projects.add('reactions', record, `Reaction record saved: ${record.title}`);
        output.textContent = JSON.stringify(record, null, 2);
        U.toast(root, 'Reaction record saved to the active project.');
      } catch (error) { output.textContent = `Error: ${error.message}`; }
    });

    bindResult('[data-conc-run]', '[data-conc-output]', 'Solution concentration',
      () => ({ moles: qs(root, '[data-conc-moles]').value, solutionL: qs(root, '[data-conc-volume]').value, soluteG: qs(root, '[data-conc-solute-g]').value, solventKg: qs(root, '[data-conc-solvent-kg]').value, solutionG: qs(root, '[data-conc-solution-g]').value }),
      input => Lab.ChemistryLab.concentration(input));
    bindResult('[data-dilution-run]', '[data-dilution-output]', 'Dilution',
      () => ({ c1: qs(root, '[data-dilution-c1]').value, v1: qs(root, '[data-dilution-v1]').value, c2: qs(root, '[data-dilution-c2]').value, v2: qs(root, '[data-dilution-v2]').value }),
      input => Lab.Stoichiometry.dilution(input));
    bindResult('[data-ksp-run]', '[data-ksp-output]', 'Molar solubility',
      () => ({ ksp: qs(root, '[data-ksp]').value, cationStoich: qs(root, '[data-ksp-cation]').value, anionStoich: qs(root, '[data-ksp-anion]').value }),
      input => Lab.ChemistryLab.solubility(input));

    bindResult('[data-strong-run]', '[data-strong-output]', 'Strong acid/base pH',
      () => ({ type: qs(root, '[data-strong-type]').value, concentration: qs(root, '[data-strong-conc]').value, equivalents: qs(root, '[data-strong-eq]').value }),
      input => Lab.ChemistryLab.strongAcidBase(input));
    bindResult('[data-weak-run]', '[data-weak-output]', 'Weak acid/base equilibrium',
      () => ({ type: qs(root, '[data-weak-type]').value, concentration: qs(root, '[data-weak-conc]').value, k: qs(root, '[data-weak-k]').value }),
      input => input.type === 'acid' ? Lab.ChemistryLab.weakAcid({ concentration: input.concentration, ka: input.k }) : Lab.ChemistryLab.weakBase({ concentration: input.concentration, kb: input.k }));
    bindResult('[data-buffer-run]', '[data-buffer-output]', 'Buffer pH',
      () => ({ pKa: qs(root, '[data-buffer-pka]').value, acid: qs(root, '[data-buffer-acid]').value, base: qs(root, '[data-buffer-base]').value }),
      input => Lab.ChemistryLab.buffer(input));
    bindResult('[data-titration-run]', '[data-titration-output]', 'Strong acid/base titration',
      () => ({ analyteType: qs(root, '[data-titration-type]').value, analyteC: qs(root, '[data-titration-analyte-c]').value, analyteMl: qs(root, '[data-titration-analyte-v]').value, titrantC: qs(root, '[data-titration-titrant-c]').value, titrantMl: qs(root, '[data-titration-titrant-v]').value }),
      input => Lab.ChemistryLab.titration(input));

    bindResult('[data-cal-run]', '[data-cal-output]', 'Calorimetry',
      () => ({ massG: qs(root, '[data-cal-mass]').value, specificHeat: qs(root, '[data-cal-cp]').value, initialC: qs(root, '[data-cal-ti]').value, finalC: qs(root, '[data-cal-tf]').value }),
      input => Lab.ChemistryLab.calorimetry(input));
    bindResult('[data-gibbs-run]', '[data-gibbs-output]', 'Gibbs free energy',
      () => ({ deltaHkJ: qs(root, '[data-gibbs-h]').value, deltaSJmolK: qs(root, '[data-gibbs-s]').value, temperatureK: qs(root, '[data-gibbs-t]').value }),
      input => Lab.ChemistryLab.gibbs(input));
    bindResult('[data-hess-run]', '[data-hess-output]', 'Hess law',
      () => JSON.parse(qs(root, '[data-hess-input]').value),
      input => Lab.ChemistryLab.hess(input));

    bindResult('[data-nernst-run]', '[data-nernst-output]', 'Nernst cell potential',
      () => ({ eStandard: qs(root, '[data-nernst-e]').value, temperatureK: qs(root, '[data-nernst-t]').value, electrons: qs(root, '[data-nernst-n]').value, reactionQuotient: qs(root, '[data-nernst-q]').value }),
      input => Lab.ChemistryLab.nernst(input));
    bindResult('[data-electrolysis-run]', '[data-electrolysis-output]', 'Electrolysis',
      () => ({ currentA: qs(root, '[data-electrolysis-current]').value, timeS: qs(root, '[data-electrolysis-time]').value, electrons: qs(root, '[data-electrolysis-n]').value, molarMassGmol: qs(root, '[data-electrolysis-mm]').value }),
      input => Lab.ChemistryLab.electrolysis(input));

    bindResult('[data-arr-run]', '[data-arr-output]', 'Arrhenius rate constant',
      () => ({ preExponential: qs(root, '[data-arr-a]').value, activationEnergyKJ: qs(root, '[data-arr-ea]').value, temperatureK: qs(root, '[data-arr-t]').value }),
      input => Lab.ChemistryLab.arrhenius(input));
    bindResult('[data-rate-run]', '[data-rate-output]', 'Integrated rate law',
      () => ({ order: qs(root, '[data-rate-order]').value, k: qs(root, '[data-rate-k]').value, initialConcentration: qs(root, '[data-rate-a0]').value, time: qs(root, '[data-rate-time]').value }),
      input => Lab.ChemistryLab.integratedRate(input));

    function parsePairs(text) {
      return Lab.Spectrometry.parse(text).map(point => ({ x: point.x, y: point.y }));
    }
    function calibrationSvg(result, xLabel = 'Concentration', yLabel = 'Signal') {
      const points = result.points || [];
      if (!points.length) return '';
      const fitted = points.map(point => ({ x: point.x, y: result.slope * point.x + result.intercept }));
      const base = Lab.Spectrometry.svg(fitted, [], { xLabel, yLabel });
      const dots = points.map(point => `<span>${U.esc(point.x)} → ${U.esc(point.y)}</span>`).join('');
      return `${base}<div class="sc-lab-calibration-points">${dots}</div>`;
    }
    qs(root, '[data-chem-cal-run]').addEventListener('click', () => {
      const output = qs(root, '[data-chem-cal-output]');
      try {
        const input = { points: parsePairs(qs(root, '[data-chem-cal-points]').value), unknownSignal: qs(root, '[data-chem-cal-unknown]').value };
        currentChemCalibration = Lab.ChemistryLab.calibration(input);
        output.textContent = JSON.stringify(currentChemCalibration, null, 2);
        qs(root, '[data-chem-cal-chart]').innerHTML = calibrationSvg(currentChemCalibration);
        recordCalculation('Analytical calibration', input, currentChemCalibration, 'calibrations');
      } catch (error) { output.textContent = `Error: ${error.message}`; }
    });
    qs(root, '[data-chem-cal-save]').addEventListener('click', () => {
      if (!currentChemCalibration) return U.toast(root, 'Run the calibration first.');
      projects.add('calibrations', { type: 'chemistry-calibration', result: currentChemCalibration, status: 'draft' }, 'Chemistry calibration record saved');
      U.toast(root, 'Calibration record saved.');
    });

    // Calculator registry.
    const domainSelect = qs(root, '[data-calculator-domain]');
    const calculatorSelect = qs(root, '[data-calculator-select]');
    const calculatorForm = qs(root, '[data-calculator-form]');
    Lab.Calculators.domains().forEach(domain => domainSelect.add(new Option(domain, domain)));

    function populateCalculators(preferredId) {
      calculatorSelect.innerHTML = '';
      Lab.Calculators.byDomain(domainSelect.value).forEach(calculator => calculatorSelect.add(new Option(calculator.name, calculator.id)));
      if (preferredId && [...calculatorSelect.options].some(option => option.value === preferredId)) calculatorSelect.value = preferredId;
      renderCalculator();
    }

    function renderCalculator() {
      const definition = Lab.Calculators.get(calculatorSelect.value);
      if (!definition) { calculatorForm.innerHTML = ''; return; }
      calculatorForm.innerHTML = `<div class="sc-lab-calculator-form" data-calculator-id="${U.esc(definition.id)}"><h4>${U.esc(definition.name)}</h4>
        ${definition.fields.map(([key, label, unit, value]) => `<label>${U.esc(label)}${unit ? ` (${U.esc(unit)})` : ''}<input data-calc-field="${U.esc(key)}" value="${U.esc(value)}"></label>`).join('')}
        <button class="sc-lab-button sc-lab-button-primary" data-calc-run>Calculate</button>
        <div class="sc-lab-calculator-result" data-calc-result>Ready.</div>
      </div>`;
      qs(calculatorForm, '[data-calc-run]').addEventListener('click', () => {
        try {
          const values = {};
          qsa(calculatorForm, '[data-calc-field]').forEach(input => { values[input.dataset.calcField] = input.value; });
          const result = definition.run(values);
          qs(calculatorForm, '[data-calc-result]').textContent = JSON.stringify(result, null, 2);
          projects.add('calculations', { type: definition.name, calculatorId: definition.id, inputs: values, result }, `${definition.name} calculation completed`);
        } catch (error) { qs(calculatorForm, '[data-calc-result]').textContent = `Error: ${error.message}`; }
      });
    }

    function selectCalculator(id) {
      const definition = Lab.Calculators.get(id);
      if (!definition) return;
      domainSelect.value = definition.domain;
      populateCalculators(id);
    }
    domainSelect.addEventListener('change', () => populateCalculators());
    calculatorSelect.addEventListener('change', renderCalculator);
    populateCalculators();

    // Spectrometry Studio.
    function spectrumMethod() { return qs(root, '[data-spectrum-method]').value; }
    function spectrumSummary() {
      if (!spectrum.length) return null;
      const ys = spectrum.map(point => point.y);
      return {
        method: spectrumMethod(), sampleId: qs(root, '[data-spectrum-sample]').value,
        points: spectrum.length, xMin: spectrum[0].x, xMax: spectrum[spectrum.length - 1].x,
        yMin: Math.min(...ys), yMax: Math.max(...ys), area: Lab.Spectrometry.integrate(spectrum),
        centroid: Lab.Spectrometry.centroid(spectrum), estimatedNoise: Lab.Spectrometry.estimateNoise(spectrum),
        peaks: detectedPeaks.length, processingSteps: spectrumHistory.length
      };
    }
    function renderSpectrum() {
      const options = { method: spectrumMethod() };
      qs(root, '[data-spectrum-chart]').innerHTML = spectrum.length ? Lab.Spectrometry.svg(spectrum, detectedPeaks, options) : empty('Load a spectrum to begin.');
      const summary = spectrumSummary();
      qs(root, '[data-spectrum-metrics]').innerHTML = summary ? Object.entries(summary).filter(([key]) => !['method','sampleId'].includes(key)).map(([key,value]) => `<div><strong>${typeof value === 'number' ? Number(value).toPrecision(6) : U.esc(value)}</strong><span>${U.esc(key)}</span></div>`).join('') : '';
      qs(root, '[data-spectrum-peak-table]').innerHTML = detectedPeaks.length ? `<table><thead><tr><th>Position</th><th>Intensity</th><th>Prominence</th><th>FWHM</th></tr></thead><tbody>${detectedPeaks.map(peak => `<tr><td>${U.esc(Number(peak.x).toPrecision(7))}</td><td>${U.esc(Number(peak.y).toPrecision(7))}</td><td>${U.esc(Number(peak.prominence).toPrecision(5))}</td><td>${U.esc(Number(peak.fwhm).toPrecision(5))}</td></tr>`).join('')}</tbody></table>` : empty('No characterized peaks.');
      qs(root, '[data-spectrum-output]').textContent = JSON.stringify({ summary, processingHistory: spectrumHistory, peaks: detectedPeaks }, null, 2);
    }
    function applySpectrumStep(label, fn) {
      if (!spectrum.length) return U.toast(root, 'Load a spectrum first.');
      try {
        spectrum = fn(spectrum);
        spectrumHistory.push({ at: U.now(), action: label });
        detectedPeaks = [];
        renderSpectrum();
      } catch (error) { U.toast(root, error.message); }
    }
    qs(root, '[data-spectrum-method]').addEventListener('change', renderSpectrum);
    qs(root, '[data-spectrum-load]').addEventListener('click', () => {
      try {
        rawSpectrum = Lab.Spectrometry.parse(qs(root, '[data-spectrum-input]').value);
        spectrum = Lab.Spectrometry.clone(rawSpectrum);
        spectrumHistory = [{ at: U.now(), action: 'Imported raw spectrum', points: spectrum.length }];
        detectedPeaks = [];
        renderSpectrum();
      } catch (error) { qs(root, '[data-spectrum-output]').textContent = `Error: ${error.message}`; }
    });
    qs(root, '[data-spectrum-reset]').addEventListener('click', () => {
      if (!rawSpectrum.length) return;
      spectrum = Lab.Spectrometry.clone(rawSpectrum); detectedPeaks = [];
      spectrumHistory.push({ at: U.now(), action: 'Reset to raw data' }); renderSpectrum();
    });
    qs(root, '[data-spectrum-baseline]').addEventListener('click', () => applySpectrumStep(`Baseline: ${qs(root, '[data-spectrum-baseline-method]').value}`, points => Lab.Spectrometry.baseline(points, qs(root, '[data-spectrum-baseline-method]').value, { windowSize: qs(root, '[data-spectrum-window]').value })));
    qs(root, '[data-spectrum-smooth]').addEventListener('click', () => applySpectrumStep(`Smoothing: ${qs(root, '[data-spectrum-smooth-method]').value}`, points => qs(root, '[data-spectrum-smooth-method]').value === 'median' ? Lab.Spectrometry.medianSmooth(points, qs(root, '[data-spectrum-radius]').value) : Lab.Spectrometry.smooth(points, qs(root, '[data-spectrum-radius]').value)));
    qs(root, '[data-spectrum-normalize]').addEventListener('click', () => applySpectrumStep(`Normalization: ${qs(root, '[data-spectrum-normalize-mode]').value}`, points => Lab.Spectrometry.normalize(points, qs(root, '[data-spectrum-normalize-mode]').value)));
    qs(root, '[data-spectrum-derivative]').addEventListener('click', () => applySpectrumStep('First derivative', points => Lab.Spectrometry.derivative(points, 1)));
    qs(root, '[data-spectrum-convert]').addEventListener('click', () => {
      const mode = qs(root, '[data-spectrum-conversion]').value;
      if (mode === 'none') return;
      applySpectrumStep(`Conversion: ${mode}`, points => {
        if (mode === 't-to-a') return Lab.Spectrometry.transmittanceToAbsorbance(points, 'fraction');
        if (mode === 'percent-to-a') return Lab.Spectrometry.transmittanceToAbsorbance(points, 'percent');
        if (mode === 'a-to-t') return Lab.Spectrometry.absorbanceToTransmittance(points, 'fraction');
        return Lab.Spectrometry.absorbanceToTransmittance(points, 'percent');
      });
    });
    qs(root, '[data-spectrum-peaks]').addEventListener('click', () => {
      if (!spectrum.length) return;
      const thresholdRaw = qs(root, '[data-spectrum-threshold]').value;
      detectedPeaks = Lab.Spectrometry.peaks(spectrum, {
        threshold: thresholdRaw === '' ? undefined : Number(thresholdRaw),
        minDistance: qs(root, '[data-spectrum-distance]').value,
        minProminence: qs(root, '[data-spectrum-prominence]').value
      });
      spectrumHistory.push({ at: U.now(), action: 'Peak detection', count: detectedPeaks.length });
      const result = spectrumSummary();
      projects.add('calculations', { type: 'Spectrometry peak analysis', method: spectrumMethod(), result, peaks: detectedPeaks }, 'Spectrometry peak analysis completed');
      renderSpectrum();
    });
    qs(root, '[data-spectrum-export]').addEventListener('click', () => {
      if (!spectrum.length) return;
      U.download(`${(qs(root, '[data-spectrum-sample]').value || 'processed-spectrum').replace(/[^a-z0-9_-]+/gi,'-')}.csv`, Lab.Spectrometry.csv(spectrum), 'text/csv');
    });
    qs(root, '[data-spectrum-save]').addEventListener('click', () => {
      if (!spectrum.length) return U.toast(root, 'Load a spectrum first.');
      const record = {
        title: qs(root, '[data-spectrum-title]').value || 'Analytical spectrum', sampleId: qs(root, '[data-spectrum-sample]').value,
        method: spectrumMethod(), raw: rawSpectrum, processed: spectrum, processingHistory: spectrumHistory,
        peaks: detectedPeaks, summary: spectrumSummary(), status: 'processed'
      };
      projects.add('spectra', record, `Spectrum saved: ${record.title}`);
      U.toast(root, 'Spectrum and processing history saved.');
    });
    qs(root, '[data-spectrum-note]').addEventListener('click', () => {
      const summary = spectrumSummary();
      if (!summary) return U.toast(root, 'Load a spectrum first.');
      createNote({ title: `${qs(root, '[data-spectrum-sample]').value} spectrometry analysis`, body: JSON.stringify({ summary, peaks: detectedPeaks, processingHistory: spectrumHistory }, null, 2), tagsText: `spectrometry, ${spectrumMethod()}, analysis` });
    });

    qs(root, '[data-spectrum-cal-run]').addEventListener('click', () => {
      const output = qs(root, '[data-spectrum-cal-output]');
      try {
        const points = parsePairs(qs(root, '[data-spectrum-cal-points]').value);
        currentSpectrumCalibration = Lab.Spectrometry.calibration(points, qs(root, '[data-spectrum-cal-unknown]').value);
        output.textContent = JSON.stringify(currentSpectrumCalibration, null, 2);
        qs(root, '[data-spectrum-cal-chart]').innerHTML = calibrationSvg(currentSpectrumCalibration);
      } catch (error) { output.textContent = `Error: ${error.message}`; }
    });
    qs(root, '[data-spectrum-cal-save]').addEventListener('click', () => {
      if (!currentSpectrumCalibration) return U.toast(root, 'Run the calibration first.');
      projects.add('calibrations', { type: 'spectrometry-calibration', method: spectrumMethod(), sampleId: qs(root, '[data-spectrum-sample]').value, result: currentSpectrumCalibration }, 'Spectrometry calibration saved');
      U.toast(root, 'Spectrometry calibration saved.');
    });


    // Physics Laboratory.
    Lab.PhysicsLab?.init(root, projects);

    // Biology and Computational Biology Laboratory.
    Lab.BiologyLab?.init(root, projects);

    // Astronomy and Astrophysics Laboratory.
    Lab.AstronomyLab?.init(root, projects);

    // Materials Science and Characterization Laboratory.
    Lab.MaterialsLab?.init(root, projects);

    // Earth, Climate, Ocean, and Marine Systems Laboratory.
    Lab.EarthLab?.init(root, projects);

    // Energy and Engineering Laboratory.
    Lab.EnergyLab?.init(root, projects); // Electrical, Electronics, and Embedded Systems. Lab.ElectricalEmbedded?.init(root, projects); // Mechanical and Thermal Engineering. Lab.MechanicalThermalLab?.init(root, projects); Lab.CivilInfrastructureLab?.init(root, projects);

    // Universal code switcher and portable method contracts.
    Lab.CodeSwitcher?.init(root, projects);

    // Universal visualization, export, and Decision Studio handoff.
    Lab.Visualization?.init(root, projects, config);

    // Structured PDF reports and Decision Studio report handoff.
    Lab.Reporting?.init(root, projects);

    // Interactive 3D and projected 4D scene visualization.
    Lab.DimensionalVisualization?.init(root, projects);

    // Workspace backup, restore, and selective reset.
    Lab.DataManagement?.init(root, projects);

    // Project records.
    qs(root, '[data-new-experiment]').addEventListener('click', () => createExperiment());
    qs(root, '[data-new-hypothesis]').addEventListener('click', () => {
      const record = promptRecord([['title', 'Hypothesis title', 'Working hypothesis'], ['statement', 'Hypothesis statement', ''], ['status', 'Status', 'proposed']]);
      if (record) projects.add('hypotheses', record, `Hypothesis added: ${record.title}`);
    });
    qs(root, '[data-new-decision]').addEventListener('click', () => {
      const record = promptRecord([['title', 'Decision title', 'Project decision'], ['rationale', 'Rationale and evidence', ''], ['status', 'Status', 'draft']]);
      if (record) projects.add('decisions', record, `Decision added: ${record.title}`);
    });
    qs(root, '[data-new-note]').addEventListener('click', () => createNote());
    qs(root, '[data-note-filter]').addEventListener('input', renderNotes);
    qs(root, '[data-export-notebook]').addEventListener('click', () => {
      const project = projects.get();
      const markdown = `# ${project.name} — Lab Notebook\n\n${project.notes.map(note => `## ${note.title}\n\n${note.body || ''}\n\n*${U.fmt(note.createdAt)}*`).join('\n\n')}`;
      U.download(`${project.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}-notebook.md`, markdown, 'text/markdown');
    });
    qs(root, '[data-activity-filter]').addEventListener('input', renderActivity);
    qs(root, '[data-activity-limit]').addEventListener('change', renderActivity);
    qs(root, '[data-export-activity]').addEventListener('click', () => {
      const lines = [['timestamp', 'activity'], ...projects.get().activity.map(item => [item.at, item.text])];
      U.download('lab-project-activity.csv', lines.map(row => row.map(csvCell).join(',')).join('\n'), 'text/csv');
    });

    // Documentation.
    function fingerprint(project) {
      const data = {
        updatedAt: project.updatedAt,
        counts: {
          evidence: project.evidence.length,
          experiments: project.experiments.length,
          hypotheses: project.hypotheses.length,
          decisions: project.decisions.length,
          notes: project.notes.length,
          calculations: project.calculations.length,
          maps: project.maps.length,
          physics: ['physicsRecords','waveforms','circuitAnalyses','fieldModels','particleEvents','detectorAnalyses','nuclearRecords','opticalAnalyses','physicsValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          biology: ['biologyRecords','biologicalSamples','sequences','alignments','proteinAnalyses','geneticAnalyses','populationAnalyses','ecologyAnalyses','physiologyRecords','biologyValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          astronomy: ['astronomyRecords','celestialTargets','orbitalAnalyses','stellarAnalyses','photometryRecords','spectralAnalyses','galaxyAnalyses','cosmologyRecords','telescopeAnalyses','astronomyValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          materials: ['materialsRecords','materialSamples','mechanicalRecords','thermalRecords','electricalRecords','magneticRecords','opticalRecords','crystallographyRecords','phaseRecords','corrosionRecords','polymerRecords','compositeRecords','microscopyRecords','materialsValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          earthSystems: ['earthRecords','geoscienceRecords','atmosphericRecords','climateRecords','hydrologyRecords','oceanRecords','marineSystemRecords','remoteSensingRecords','hazardRecords','carbonCycleRecords','earthValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          energyEngineering: ['energyRecords','engineeringRecords','energySystemRecords','solarRecords','windRecords','hydroRecords','storageRecords','gridRecords','thermalSystemRecords','fuelHydrogenRecords','emissionsRecords','technoEconomicRecords','reliabilityRecords','energyValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0)
        }
      };
      return btoa(unescape(encodeURIComponent(JSON.stringify(data))));
    }

    function generateDocument(type, title) {
      const project = projects.get();
      const sections = [`# ${title}`, '', `Project: ${project.name}`, `Generated: ${new Date().toISOString()}`, `Document type: ${type}`, ''];
      sections.push('## Project summary', '', project.description || 'No project description has been recorded.', '');
      sections.push('## Evidence', '', project.evidence.length ? project.evidence.map(item => `- **${item.title}** — ${item.source || 'Source'}${item.url ? ` — ${item.url}` : ''}`).join('\n') : 'No evidence records.', '');
      sections.push('## Hypotheses', '', project.hypotheses.length ? project.hypotheses.map(item => `- **${item.title}** — ${item.statement || ''}`).join('\n') : 'No hypotheses recorded.', '');
      sections.push('## Calculations and analyses', '', project.calculations.length ? project.calculations.map(item => `- **${item.type || 'Calculation'}** — ${JSON.stringify(item.result || {})}`).join('\n') : 'No calculations recorded.', '');
      const physicsCollections = ['physicsRecords','waveforms','circuitAnalyses','fieldModels','particleEvents','detectorAnalyses','nuclearRecords','opticalAnalyses','physicsValidationRecords'];
      const physicsRecords = physicsCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Physics analyses', '', physicsRecords.length ? physicsRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || {})}`).join('\n') : 'No physics analyses recorded.', '');
      const biologyCollections = ['biologyRecords','biologicalSamples','sequences','alignments','proteinAnalyses','geneticAnalyses','populationAnalyses','ecologyAnalyses','physiologyRecords','biologyValidationRecords'];
      const biologyRecords = biologyCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Biology analyses', '', biologyRecords.length ? biologyRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No biology analyses recorded.', '');
      const astronomyCollections = ['astronomyRecords','celestialTargets','orbitalAnalyses','stellarAnalyses','photometryRecords','spectralAnalyses','galaxyAnalyses','cosmologyRecords','telescopeAnalyses','astronomyValidationRecords'];
      const astronomyRecords = astronomyCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Astronomy analyses', '', astronomyRecords.length ? astronomyRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No astronomy analyses recorded.', '');
      const materialsCollections = ['materialsRecords','materialSamples','mechanicalRecords','thermalRecords','electricalRecords','magneticRecords','opticalRecords','crystallographyRecords','phaseRecords','corrosionRecords','polymerRecords','compositeRecords','microscopyRecords','materialsValidationRecords'];
      const materialsRecords = materialsCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Materials analyses', '', materialsRecords.length ? materialsRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No materials analyses recorded.', '');
      const earthCollections = ['earthRecords','geoscienceRecords','atmosphericRecords','climateRecords','hydrologyRecords','oceanRecords','marineSystemRecords','remoteSensingRecords','hazardRecords','carbonCycleRecords','earthValidationRecords'];
      const earthRecords = earthCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Earth systems analyses', '', earthRecords.length ? earthRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No Earth systems analyses recorded.', '');
      const energyCollections = ['energyRecords','engineeringRecords','energySystemRecords','solarRecords','windRecords','hydroRecords','storageRecords','gridRecords','thermalSystemRecords','fuelHydrogenRecords','emissionsRecords','technoEconomicRecords','reliabilityRecords','energyValidationRecords'];
      const energyRecords = energyCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Energy and engineering analyses', '', energyRecords.length ? energyRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No energy and engineering analyses recorded.', '');
      sections.push('## Experiments', '', project.experiments.length ? project.experiments.map(item => `### ${item.title}\n\nQuestion: ${item.question || ''}\n\nHypothesis: ${item.hypothesis || ''}\n\nMethod: ${item.method || ''}\n\nStatus: ${item.status || 'planned'}`).join('\n\n') : 'No experiments recorded.', '');
      sections.push('## Decisions', '', project.decisions.length ? project.decisions.map(item => `- **${item.title}** — ${item.rationale || ''}`).join('\n') : 'No decisions recorded.', '');
      sections.push('## Notebook record', '', project.notes.length ? project.notes.slice(0, 25).map(item => `### ${item.title}\n\n${item.body || ''}`).join('\n\n') : 'No notebook entries.', '');
      sections.push('## Traceability', '', 'Sources → Evidence → Hypotheses → Calculations → Experiments → Decisions → Documentation', '');
      sections.push('## Scientific review boundary', '', 'Imported observations, calculations, models, prototype outputs, and generated documentation require review against authoritative sources, validated methods, and actual operating conditions.');
      return sections.join('\n');
    }

    function updateDocStale() {
      if (!currentDocument) return;
      const stale = currentDocument.fingerprint !== fingerprint(projects.get());
      qs(root, '[data-doc-status]').textContent = stale
        ? 'Project data changed after generation. Regenerate or preserve this text as a released snapshot.'
        : 'Document reflects the current project record.';
      qs(root, '[data-doc-status]').classList.toggle('is-stale', stale);
    }

    qs(root, '[data-generate-doc]').addEventListener('click', () => {
      const type = qs(root, '[data-doc-type]').value;
      const title = qs(root, '[data-doc-title]').value || 'Lab project report';
      const markdown = generateDocument(type, title);
      currentDocument = { type, title, markdown, fingerprint: fingerprint(projects.get()), generatedAt: U.now() };
      qs(root, '[data-doc-editor]').value = markdown;
      updateDocStale();
      populateDatasetSelect();
    });
    qs(root, '[data-save-doc]').addEventListener('click', () => {
      const markdown = qs(root, '[data-doc-editor]').value;
      if (!markdown.trim()) return;
      const type = qs(root, '[data-doc-type]').value;
      const title = qs(root, '[data-doc-title]').value || 'Lab project report';
      projects.add('documents', { type, title, markdown, fingerprint: fingerprint(projects.get()), status: 'snapshot' }, `Document snapshot saved: ${title}`);
      currentDocument = { type, title, markdown, fingerprint: fingerprint(projects.get()), generatedAt: U.now() };
      updateDocStale();
      populateDatasetSelect();
      U.toast(root, 'Document snapshot saved.');
    });
    qs(root, '[data-export-doc-md]').addEventListener('click', () => {
      const text = qs(root, '[data-doc-editor]').value;
      if (text.trim()) U.download('lab-document.md', text, 'text/markdown');
    });
    qs(root, '[data-export-doc-html]').addEventListener('click', () => {
      const text = qs(root, '[data-doc-editor]').value;
      if (!text.trim()) return;
      const html = `<!doctype html><meta charset="utf-8"><title>${U.esc(qs(root, '[data-doc-title]').value)}</title><pre>${U.esc(text)}</pre>`;
      U.download('lab-document.html', html, 'text/html');
    });


    async function loadSourceRegistry(){const target=qs(root,'[data-source-registry]');target.innerHTML='<div class="sc-lab-data-note">Loading source metadata and connector health…</div>';try{const data=await U.fetchJson(`${config.restBase}sources/status`);root._sourceRows=Object.entries(data.sources||{});renderSourceRegistry();}catch(error){target.innerHTML=empty(error.message);}}
    function renderSourceRegistry(){const q=(qs(root,'[data-source-filter]').value||'').toLowerCase();const rows=(root._sourceRows||[]).filter(([id,m])=>!q||`${id} ${m.label} ${m.domain} ${m.coverage} ${m.format}`.toLowerCase().includes(q));qs(root,'[data-source-registry]').innerHTML=rows.map(([id,m])=>`<article class="sc-lab-source-row"><div><strong>${U.esc(m.label)}</strong><span>${U.esc(id)}</span></div><div><strong>${U.esc(m.domain)}</strong><span>${U.esc(m.kind)}</span></div><div><strong>${U.esc(m.coverage||'—')}</strong><span>${U.esc(m.temporal||'—')}</span></div><div><strong>${U.esc(m.endpoint||'—')}</strong><span>${U.esc(m.format||'—')}</span></div><div><strong class="sc-lab-source-state ${U.esc(m.status||'not_checked')}">${U.esc(m.status||'not checked')}</strong><span>${U.esc(m.lastChecked?U.fmt(m.lastChecked):m.message||'Not checked')}</span></div></article>`).join('')||empty('No matching sources.');}
    qs(root,'[data-source-refresh]').addEventListener('click',loadSourceRegistry);qs(root,'[data-source-filter]').addEventListener('input',renderSourceRegistry);

    // System status.
    async function runStatus(showToast = true) {
      const target = qs(root, '[data-system-status]');
      target.innerHTML = '<div class="sc-lab-status-row"><span>Lab REST API</span><span class="sc-lab-status-value warn">Checking</span><span>Testing WordPress route and source registry.</span></div>';
      try {
        const [status, sources] = await Promise.all([
          U.fetchJson(`${config.restBase}status`),
          U.fetchJson(`${config.restBase}sources/status`)
        ]);
        const rows = [
          ['Lab REST API', status.ok ? 'Ready' : 'Unavailable', `Version ${status.version || 'unknown'} · ${U.fmt(status.time)}`],
          ['Scientific source registry', sources.sources ? 'Ready' : 'Unavailable', `${Object.keys(sources.sources || {}).length} configured connectors`],
          ['Browser project storage', 'Ready', `${projects.items.length} local project${projects.items.length === 1 ? '' : 's'}`],
          ['Periodic table', Lab.Periodic?.getElements?.().length === 118 ? 'Ready' : 'Loading', `${Lab.Periodic?.getElements?.().length || 0} element records`],
          ['Calculator registry', 'Ready', `${Lab.Calculators.definitions.length} scientific calculators`],
          ['Physics laboratory', Lab.PhysicsLab?.particles?.length ? 'Ready' : 'Unavailable', `${Lab.PhysicsLab?.particles?.length || 0} particle reference records · ${Object.keys(Lab.PhysicsLab?.tools || {}).length} physics methods`],
          ['Biology laboratory', Lab.BiologyLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.BiologyLab?.definitions?.length || 0} computational biology methods · ${Lab.BiologyLab?.benchmarks?.length || 0} validation cases`],
          ['Astronomy laboratory', Lab.AstronomyLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.AstronomyLab?.definitions?.length || 0} astronomy methods · ${Lab.AstronomyLab?.benchmarks?.length || 0} validation cases`],
          ['Materials laboratory', Lab.MaterialsLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.MaterialsLab?.definitions?.length || 0} materials methods · ${Lab.MaterialsLab?.benchmarks?.length || 0} validation cases`],
          ['Earth systems laboratory', Lab.EarthLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.EarthLab?.definitions?.length || 0} Earth systems methods · ${Lab.EarthLab?.benchmarks?.length || 0} validation cases`],
          ['Energy and engineering laboratory', Lab.EnergyLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.EnergyLab?.definitions?.length || 0} energy and engineering methods · ${Lab.EnergyLab?.benchmarks?.length || 0} validation cases`], ['Mechanical and thermal engineering laboratory', Lab.MechanicalThermalLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.MechanicalThermalLab?.definitions?.length || 0} mechanical and thermal methods · ${Lab.MechanicalThermalLab?.benchmarks?.length || 0} validation cases`],
          ['Visualization and export engine', Lab.Visualization ? 'Ready' : 'Unavailable', 'SVG, PNG, PDF, CSV, JSON, project records, and Decision Studio packets'],
          ['Workspace data management', Lab.DataManagement ? 'Ready' : 'Unavailable', 'Workspace backup, restore, selective clearing, and factory reset']
        ];
        target.innerHTML = rows.map(([name, value, detail]) => `<div class="sc-lab-status-row"><span>${U.esc(name)}</span><span class="sc-lab-status-value ${value === 'Ready' ? 'ok' : 'warn'}">${U.esc(value)}</span><span>${U.esc(detail)}</span></div>`).join('');
        if (showToast) U.toast(root, 'System checks completed.');
      } catch (error) {
        target.innerHTML = `<div class="sc-lab-status-row"><span>Lab REST API</span><span class="sc-lab-status-value warn">Unavailable</span><span>${U.esc(error.message)}</span></div>`;
      }
    }
    qs(root, '[data-status-refresh]').addEventListener('click', () => runStatus(true));

    renderSelect();
    openModule(initial);
  }

  d.addEventListener('DOMContentLoaded', () => {
    d.querySelectorAll('.sc-lab-app').forEach(init);
  });
})(window, document);
