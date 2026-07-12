<?php if (!defined('ABSPATH')) { exit; } ?>
<div class="sc-lab-app" data-initial-module="<?php echo esc_attr($sc_lab_initial_module); ?>" data-initial-project="<?php echo esc_attr($sc_lab_initial_project); ?>">
  <header class="sc-lab-topbar">
    <div class="sc-lab-titleblock">
      <span class="sc-lab-kicker">Sustainable Catalyst</span>
      <h2>Lab</h2>
      <span class="sc-lab-version">v<?php echo esc_html(SC_LAB_VERSION); ?></span>
    </div>
    <div class="sc-lab-project-controls">
      <label for="sc-lab-project-select">Project</label>
      <select id="sc-lab-project-select" data-lab-project-select></select>
      <button type="button" class="sc-lab-button" data-lab-action="new-project">New</button>
      <button type="button" class="sc-lab-button" data-lab-action="import-project">Import</button>
      <button type="button" class="sc-lab-button" data-lab-action="export-project">Export</button>
      <input type="file" accept="application/json" hidden data-lab-import-file>
    </div>
  </header>

  <div class="sc-lab-layout">
    <nav class="sc-lab-nav" aria-label="Lab modules">
      <?php
      $items = array(
        'overview'=>'Overview','scientific-feeds'=>'Scientific feeds','climate-maps'=>'Climate maps','space-telescopes'=>'Space telescopes','marine-biology'=>'Marine biology','chemistry'=>'Chemistry','science-engineering'=>'Science & engineering','experiments'=>'Experiments','evidence-decisions'=>'Evidence & decisions','notebook'=>'Notebook','documentation'=>'Documentation','system-status'=>'System status'
      );
      foreach ($items as $key=>$label): ?>
        <button type="button" class="sc-lab-nav-button" data-lab-module-button="<?php echo esc_attr($key); ?>"><?php echo esc_html($label); ?></button>
      <?php endforeach; ?>
      <div class="sc-lab-nav-links">
        <a data-route="workbench" href="#">Workbench</a>
        <a data-route="decisionStudio" href="#">Decision Studio</a>
        <a data-route="siteIntelligence" href="#">Site Intelligence</a>
      </div>
    </nav>

    <main class="sc-lab-main">
      <section class="sc-lab-panel" data-lab-module="overview">
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/OVERVIEW</span><h3>Scientific project workspace</h3></div><span class="sc-lab-status-dot is-ready">Ready</span></div>
        <div class="sc-lab-metrics" data-overview-metrics></div>
        <div class="sc-lab-grid sc-lab-grid-3">
          <article class="sc-lab-tool"><h4>Start from evidence</h4><p>Review Earth, space, marine, literature, and climate records and save them into the active project.</p><button class="sc-lab-button sc-lab-button-primary" data-open-module="scientific-feeds">Open feeds</button></article>
          <article class="sc-lab-tool"><h4>Run scientific work</h4><p>Use chemistry, spectrometry, physics, astronomy, materials, Earth science, biology, and energy tools.</p><button class="sc-lab-button sc-lab-button-primary" data-open-module="chemistry">Open chemistry</button></article>
          <article class="sc-lab-tool"><h4>Record and document</h4><p>Connect calculations, experiments, evidence, notes, decisions, and generated technical documents.</p><button class="sc-lab-button sc-lab-button-primary" data-open-module="documentation">Generate documentation</button></article>
        </div>
        <div class="sc-lab-split">
          <section><h4>Recent activity</h4><div class="sc-lab-list" data-recent-activity></div></section>
          <section><h4>Project traceability</h4><div class="sc-lab-trace">Sources → Evidence → Hypotheses → Calculations → Experiments → Decisions → Documentation</div></section>
        </div>
      </section>

      <section class="sc-lab-panel" data-lab-module="scientific-feeds" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/FEEDS</span><h3>Scientific signal board</h3></div><button class="sc-lab-button" data-feed-refresh>Refresh</button></div>
        <div class="sc-lab-toolbar">
          <label>Source<select data-feed-source><option value="usgs-earthquakes">USGS earthquakes</option><option value="nasa-eonet">NASA EONET</option><option value="pubmed-science">PubMed</option><option value="arxiv-physics">arXiv</option><option value="nasa-space-telescopes">NASA space releases</option><option value="obis-marine">OBIS marine biology</option></select></label>
          <label>Query<input type="search" data-feed-query placeholder="Topic or taxon"></label>
          <label>Limit<input type="number" min="1" max="30" value="12" data-feed-limit></label>
          <button class="sc-lab-button sc-lab-button-primary" data-feed-run>Run query</button>
        </div>
        <div class="sc-lab-feed-status" data-feed-status>Select a source and run a query.</div>
        <div class="sc-lab-feed-grid" data-feed-results></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="climate-maps" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/CLIMATE</span><h3>Climate and Earth observation map</h3></div><button class="sc-lab-button" data-climate-save>Save map state</button></div>
        <div class="sc-lab-toolbar">
          <label>Layer<select data-climate-layer><option value="MODIS_Terra_CorrectedReflectance_TrueColor">True color</option><option value="MODIS_Terra_Land_Surface_Temp_Day">Land surface temperature</option><option value="IMERG_Precipitation_Rate">Precipitation rate</option><option value="AIRS_L3_Carbon_Dioxide_500hPa_Volume_Mixing_Ratio_Daily_Day">Atmospheric CO₂</option><option value="MODIS_Terra_Aerosol">Aerosol optical depth</option></select></label>
          <label>Date<input type="date" data-climate-date></label>
          <label>Region<select data-climate-region><option value="-180,-90,180,90">Global</option><option value="-130,20,-60,55">North America</option><option value="-20,30,45,72">Europe</option><option value="90,-50,180,10">Australasia</option><option value="-85,-60,-30,20">South America</option></select></label>
          <button class="sc-lab-button sc-lab-button-primary" data-climate-render>Render</button>
        </div>
        <div class="sc-lab-map-frame"><img data-climate-image alt="NASA GIBS climate and Earth observation layer"><div class="sc-lab-map-overlay" data-climate-loading hidden>Loading NASA GIBS layer…</div></div>
        <div class="sc-lab-data-note">Source: NASA Global Imagery Browse Services (GIBS). Layer availability varies by date.</div>
      </section>

      <section class="sc-lab-panel" data-lab-module="space-telescopes" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/ASTRONOMY</span><h3>Space telescope observations and releases</h3></div><button class="sc-lab-button sc-lab-button-primary" data-space-load>Load releases</button></div>
        <div class="sc-lab-toolbar"><label>Search<input type="search" value="James Webb Hubble telescope nebula galaxy" data-space-query></label></div>
        <div class="sc-lab-feed-grid" data-space-results></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="marine-biology" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/MARINE</span><h3>Marine biodiversity observations</h3></div><button class="sc-lab-button sc-lab-button-primary" data-marine-load>Query OBIS</button></div>
        <div class="sc-lab-toolbar"><label>Scientific name or taxon<input type="search" value="Cetacea" data-marine-query></label><label>Limit<input type="number" min="1" max="30" value="15" data-marine-limit></label></div>
        <div class="sc-lab-feed-grid" data-marine-results></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="chemistry" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/CHEM</span><h3>Chemistry workspace</h3></div></div>
        <div class="sc-lab-tabs"><button class="is-active" data-chem-tab="periodic">Periodic table</button><button data-chem-tab="stoichiometry">Stoichiometry</button><button data-chem-tab="solutions">Solutions</button></div>
        <div data-chem-pane="periodic">
          <div class="sc-lab-toolbar"><label>Find element<input type="search" data-element-search placeholder="Name, symbol, or atomic number"></label><label>Property<select data-element-property><option value="category">Category</option><option value="atomicMass">Atomic mass</option><option value="period">Period</option><option value="group">Group</option></select></label></div>
          <div class="sc-lab-periodic-wrap"><div class="sc-lab-periodic" data-periodic-table></div></div>
          <div class="sc-lab-element-detail" data-element-detail>Select an element.</div>
        </div>
        <div data-chem-pane="stoichiometry" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Formula and molar mass</h4><label>Chemical formula<input value="Al2(SO4)3" data-formula-input></label><button class="sc-lab-button sc-lab-button-primary" data-formula-run>Analyze</button><pre data-formula-output></pre></article>
            <article class="sc-lab-tool"><h4>Balance equation</h4><label>Equation<input value="Fe + O2 -> Fe2O3" data-balance-input></label><button class="sc-lab-button sc-lab-button-primary" data-balance-run>Balance</button><pre data-balance-output></pre></article>
            <article class="sc-lab-tool"><h4>Limiting reagent</h4><label>Balanced equation<input value="2 H2 + O2 -> 2 H2O" data-limit-equation></label><label>Reactant moles JSON<input value='{"H2":3,"O2":2}' data-limit-moles></label><button class="sc-lab-button sc-lab-button-primary" data-limit-run>Calculate</button><pre data-limit-output></pre></article>
            <article class="sc-lab-tool"><h4>Theoretical yield</h4><label>Product formula<input value="H2O" data-yield-product></label><label>Product moles<input type="number" step="any" value="1.5" data-yield-moles></label><button class="sc-lab-button sc-lab-button-primary" data-yield-run>Calculate</button><pre data-yield-output></pre></article>
          </div>
        </div>
        <div data-chem-pane="solutions" hidden>
          <article class="sc-lab-tool sc-lab-tool-wide"><h4>Dilution calculator</h4><div class="sc-lab-inline-fields"><label>C₁<input type="number" step="any" value="1" data-dilution-c1></label><label>V₁<input type="number" step="any" value="10" data-dilution-v1></label><label>C₂<input type="number" step="any" value="0.1" data-dilution-c2></label><label>V₂<input type="number" step="any" placeholder="solve" data-dilution-v2></label></div><button class="sc-lab-button sc-lab-button-primary" data-dilution-run>Solve C₁V₁=C₂V₂</button><pre data-dilution-output></pre></article>
        </div>
      </section>

      <section class="sc-lab-panel" data-lab-module="science-engineering" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/ANALYSIS</span><h3>Science and engineering tools</h3></div></div>
        <div class="sc-lab-tabs"><button class="is-active" data-analysis-tab="calculators">Calculators</button><button data-analysis-tab="spectrometry">Spectrometry</button></div>
        <div data-analysis-pane="calculators"><div class="sc-lab-toolbar"><label>Domain<select data-calculator-domain></select></label><label>Tool<select data-calculator-select></select></label></div><div class="sc-lab-calculator" data-calculator-form></div></div>
        <div data-analysis-pane="spectrometry" hidden>
          <div class="sc-lab-grid sc-lab-grid-2"><article class="sc-lab-tool"><h4>Import spectrum</h4><label>CSV or whitespace x,y data<textarea rows="12" data-spectrum-input>400,0.12
450,0.18
500,0.91
550,0.31
600,0.14</textarea></label><div class="sc-lab-inline-actions"><button class="sc-lab-button" data-spectrum-load>Load</button><button class="sc-lab-button" data-spectrum-baseline>Baseline</button><button class="sc-lab-button" data-spectrum-smooth>Smooth</button><button class="sc-lab-button sc-lab-button-primary" data-spectrum-peaks>Detect peaks</button></div><pre data-spectrum-output></pre></article><article class="sc-lab-tool"><h4>Spectrum plot</h4><div data-spectrum-chart class="sc-lab-chart"></div><button class="sc-lab-button" data-spectrum-export>Export processed CSV</button></article></div>
        </div>
      </section>

      <section class="sc-lab-panel" data-lab-module="experiments" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/EXPERIMENTS</span><h3>Experiment registry</h3></div><button class="sc-lab-button sc-lab-button-primary" data-new-experiment>New experiment</button></div>
        <div class="sc-lab-list" data-experiment-list></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="evidence-decisions" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/EVIDENCE</span><h3>Evidence, hypotheses, and decisions</h3></div></div>
        <div class="sc-lab-grid sc-lab-grid-3"><section><h4>Evidence inbox</h4><div class="sc-lab-list" data-evidence-list></div></section><section><h4>Hypotheses</h4><button class="sc-lab-button" data-new-hypothesis>Add hypothesis</button><div class="sc-lab-list" data-hypothesis-list></div></section><section><h4>Decisions</h4><button class="sc-lab-button" data-new-decision>Add decision</button><div class="sc-lab-list" data-decision-list></div></section></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="notebook" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/NOTEBOOK</span><h3>Research and laboratory notebook</h3></div><button class="sc-lab-button sc-lab-button-primary" data-new-note>New entry</button></div>
        <div class="sc-lab-toolbar"><label>Filter<input type="search" data-note-filter placeholder="Search entries"></label><button class="sc-lab-button" data-export-notebook>Export Markdown</button></div><div class="sc-lab-list" data-note-list></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="documentation" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/DOCS</span><h3>Data-connected documentation</h3></div></div>
        <div class="sc-lab-toolbar"><label>Document type<select data-doc-type><option value="research-report">Research report</option><option value="experiment-report">Experiment report</option><option value="scientific-brief">Scientific evidence brief</option><option value="technical-record">Technical project record</option></select></label><label>Title<input data-doc-title value="Lab project report"></label><button class="sc-lab-button sc-lab-button-primary" data-generate-doc>Generate</button></div>
        <div class="sc-lab-doc-status" data-doc-status>No document generated.</div><textarea class="sc-lab-doc-editor" rows="24" data-doc-editor></textarea><div class="sc-lab-inline-actions"><button class="sc-lab-button" data-save-doc>Save snapshot</button><button class="sc-lab-button" data-export-doc-md>Export Markdown</button><button class="sc-lab-button" data-export-doc-html>Export HTML</button></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="system-status" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/STATUS</span><h3>System and connector status</h3></div><button class="sc-lab-button sc-lab-button-primary" data-status-refresh>Run checks</button></div>
        <div class="sc-lab-status-table" data-system-status></div>
      </section>
    </main>
  </div>
  <div class="sc-lab-toast" role="status" aria-live="polite" data-lab-toast hidden></div>
</div>
