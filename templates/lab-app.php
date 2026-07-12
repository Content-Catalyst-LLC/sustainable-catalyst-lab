<?php if (!defined('ABSPATH')) { exit; } ?>
<div class="sc-lab-app" data-initial-module="<?php echo esc_attr($sc_lab_initial_module); ?>" data-initial-project="<?php echo esc_attr($sc_lab_initial_project); ?>">
  <header class="sc-lab-topbar">
    <div class="sc-lab-topbar-primary">
      <button type="button" class="sc-lab-nav-toggle" data-lab-nav-toggle aria-expanded="false" aria-controls="sc-lab-module-nav">
        <span aria-hidden="true">☰</span><span>Modules</span>
      </button>

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
    </div>

    <div class="sc-lab-commandbar">
      <div class="sc-lab-command-search">
        <label class="screen-reader-text" for="sc-lab-command-input">Search Lab tools and modules</label>
        <input id="sc-lab-command-input" type="search" placeholder="Search tools, feeds, equations, or modules…" autocomplete="off" data-lab-command-input>
        <kbd>⌘K</kbd>
        <div class="sc-lab-command-results" data-lab-command-results hidden></div>
      </div>
      <div class="sc-lab-command-actions" aria-label="Quick project actions">
        <button type="button" class="sc-lab-button" data-command-action="observation">Add observation</button>
        <button type="button" class="sc-lab-button" data-command-action="experiment">New experiment</button>
        <button type="button" class="sc-lab-button sc-lab-button-primary" data-command-action="note">Notebook entry</button>
      </div>
    </div>
  </header>

  <div class="sc-lab-layout">
    <nav id="sc-lab-module-nav" class="sc-lab-nav" aria-label="Lab modules" data-lab-nav>
      <?php
      $groups = array(
        'Project' => array(
          'overview' => 'Overview',
          'activity' => 'Activity',
        ),
        'Observe' => array(
          'scientific-feeds' => 'Observation board',
          'climate-maps' => 'Climate maps',
          'space-telescopes' => 'Space observations',
          'marine-biology' => 'Marine biology',
        ),
        'Analyze' => array(
          'dataset-inspector' => 'Dataset inspector',
          'chemistry' => 'Chemistry',
          'science-engineering' => 'Science & engineering',
        ),
        'Record' => array(
          'experiments' => 'Experiments',
          'evidence-decisions' => 'Evidence & decisions',
          'notebook' => 'Notebook',
          'documentation' => 'Documentation',
        ),
        'System' => array(
          'source-registry' => 'Source registry',
          'system-status' => 'Connector status',
        ),
      );
      foreach ($groups as $group => $items): ?>
        <div class="sc-lab-nav-group">
          <span class="sc-lab-nav-heading"><?php echo esc_html($group); ?></span>
          <?php foreach ($items as $key => $label): ?>
            <button type="button" class="sc-lab-nav-button" data-lab-module-button="<?php echo esc_attr($key); ?>"><?php echo esc_html($label); ?></button>
          <?php endforeach; ?>
        </div>
      <?php endforeach; ?>
      <div class="sc-lab-nav-links">
        <span class="sc-lab-nav-heading">Open full application</span>
        <a data-route="workbench" href="#">Prototyping Workbench</a>
        <a data-route="decisionStudio" href="#">Decision Studio</a>
        <a data-route="siteIntelligence" href="#">Site Intelligence</a>
      </div>
    </nav>

    <main class="sc-lab-main">
      <section class="sc-lab-panel" data-lab-module="overview">
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/OVERVIEW</span><h3>Scientific project workspace</h3></div>
          <span class="sc-lab-status-dot is-ready">Ready</span>
        </div>

        <div class="sc-lab-metrics" data-overview-metrics></div>

        <section class="sc-lab-dashboard-section">
          <div class="sc-lab-dashboard-head">
            <div><span class="sc-lab-section-code">LIVE/SIGNALS</span><h4>Scientific signals</h4></div>
            <button type="button" class="sc-lab-button" data-overview-refresh>Refresh signals</button>
          </div>
          <div class="sc-lab-overview-signals" data-overview-signals>
            <div class="sc-lab-data-note">Loading a concise view of Earth, space, marine, and literature signals…</div>
          </div>
        </section>

        <section class="sc-lab-dashboard-section">
          <div class="sc-lab-dashboard-head"><div><span class="sc-lab-section-code">QUICK/TOOLS</span><h4>Scientific tools</h4></div></div>
          <div class="sc-lab-quick-tools" data-quick-tools>
            <button type="button" data-quick-tool="periodic-table"><strong>Periodic Table</strong><span>Elements and properties</span></button>
            <button type="button" data-quick-tool="stoichiometry"><strong>Stoichiometry</strong><span>Formulas, balance, yield</span></button>
            <button type="button" data-quick-tool="spectrometry"><strong>Spectrometry</strong><span>Import, process, detect peaks</span></button>
            <button type="button" data-quick-tool="photon"><strong>Photon Energy</strong><span>Wavelength, frequency, energy</span></button>
            <button type="button" data-quick-tool="rlc"><strong>RLC Impedance</strong><span>Reactance, phase, resonance</span></button>
            <button type="button" data-quick-tool="orbit"><strong>Orbital Mechanics</strong><span>Velocity and period</span></button>
            <button type="button" data-quick-tool="uncertainty"><strong>Uncertainty</strong><span>Independent propagation</span></button>
            <button type="button" data-quick-tool="pv"><strong>Energy Systems</strong><span>Photovoltaic output</span></button>
          </div>
        </section>

        <div class="sc-lab-dashboard-columns">
          <section class="sc-lab-dashboard-section">
            <div class="sc-lab-dashboard-head"><div><span class="sc-lab-section-code">PROJECT/WORK</span><h4>Active scientific work</h4></div></div>
            <div class="sc-lab-project-work" data-project-work></div>
          </section>
          <section class="sc-lab-dashboard-section">
            <div class="sc-lab-dashboard-head"><div><span class="sc-lab-section-code">PROJECT/ACTIVITY</span><h4>Recent activity</h4></div><button type="button" class="sc-lab-text-button" data-open-module="activity">View all</button></div>
            <div class="sc-lab-list" data-recent-activity></div>
          </section>
        </div>

        <section class="sc-lab-dashboard-section">
          <div class="sc-lab-dashboard-head"><div><span class="sc-lab-section-code">PROJECT/TRACE</span><h4>Traceability map</h4></div></div>
          <div class="sc-lab-trace-map" data-traceability></div>
        </section>

        <div class="sc-lab-empty-state" data-overview-empty hidden>
          <h4>Start a scientific record</h4>
          <p>Create a first evidence record, experiment, calculation, or notebook entry. Every result remains connected to the active project.</p>
          <div class="sc-lab-empty-actions">
            <button type="button" class="sc-lab-button" data-open-module="scientific-feeds">Query signals</button>
            <button type="button" class="sc-lab-button" data-command-action="experiment">Create experiment</button>
            <button type="button" class="sc-lab-button" data-quick-tool="stoichiometry">Run calculation</button>
            <button type="button" class="sc-lab-button sc-lab-button-primary" data-command-action="note">Add notebook entry</button>
          </div>
        </div>
      </section>

      <section class="sc-lab-panel" data-lab-module="activity" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/ACTIVITY</span><h3>Project activity record</h3></div><button type="button" class="sc-lab-button" data-export-activity>Export CSV</button></div>
        <div class="sc-lab-toolbar"><label>Filter<input type="search" data-activity-filter placeholder="Search project activity"></label><label>Limit<select data-activity-limit><option>25</option><option selected>50</option><option>100</option><option>200</option></select></label></div>
        <div class="sc-lab-list sc-lab-activity-list" data-activity-list></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="scientific-feeds" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/FEEDS</span><h3>Scientific signal board</h3></div><button class="sc-lab-button" data-feed-refresh>Refresh</button></div>
        <div class="sc-lab-toolbar">
          <label>Source<select data-feed-source><option value="all-science">All scientific sources</option><option value="usgs-earthquakes">USGS earthquakes</option><option value="nasa-eonet">NASA EONET</option><option value="pubmed-science">PubMed</option><option value="arxiv-physics">arXiv</option><option value="nasa-space-telescopes">NASA space releases</option><option value="obis-marine">OBIS marine biology</option></select></label>
          <label>Query<input type="search" data-feed-query placeholder="Topic, place, or taxon"></label>
          <label>Limit<input type="number" min="1" max="30" value="12" data-feed-limit></label>
          <button class="sc-lab-button sc-lab-button-primary" data-feed-run>Run query</button>
        </div>
        <div class="sc-lab-feed-status" data-feed-status>Select a source and run a query.</div>
        <div class="sc-lab-observation-actions"><button class="sc-lab-button" data-feed-to-dataset disabled>Open results in Dataset Inspector</button><button class="sc-lab-button" data-save-query disabled>Save query</button></div><div class="sc-lab-feed-grid" data-feed-results></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="climate-maps" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/CLIMATE</span><h3>Climate and Earth observation map</h3></div><button class="sc-lab-button" data-climate-save>Save map state</button></div>
        <div class="sc-lab-toolbar">
          <label>Layer<select data-climate-layer><option value="MODIS_Terra_CorrectedReflectance_TrueColor">True color</option><option value="MODIS_Terra_Land_Surface_Temp_Day">Land surface temperature</option><option value="IMERG_Precipitation_Rate">Precipitation rate</option><option value="AIRS_L3_Carbon_Dioxide_500hPa_Volume_Mixing_Ratio_Daily_Day">Atmospheric CO₂</option><option value="MODIS_Terra_Aerosol">Aerosol optical depth</option><option value="MODIS_Terra_NDSI_Snow_Cover">Snow cover</option><option value="VIIRS_SNPP_Chlorophyll_A">Ocean chlorophyll-a</option></select></label>
          <label>Date<input type="date" data-climate-date></label>
          <label>Region<select data-climate-region><option value="-180,-90,180,90">Global</option><option value="-130,20,-60,55">North America</option><option value="-20,30,45,72">Europe</option><option value="90,-50,180,10">Australasia</option><option value="-85,-60,-30,20">South America</option></select></label>
          <label>Opacity<input type="range" min="20" max="100" value="100" data-climate-opacity></label><button class="sc-lab-button sc-lab-button-primary" data-climate-render>Render</button><button class="sc-lab-button" data-climate-export>Export metadata</button>
        </div>
        <div class="sc-lab-map-frame"><img data-climate-image tabindex="0" alt="NASA GIBS climate and Earth observation layer"><div class="sc-lab-map-overlay" data-climate-loading hidden>Loading NASA GIBS layer…</div></div><div class="sc-lab-map-readout" data-climate-readout>Click the map to record a coordinate.</div><div class="sc-lab-map-metadata" data-climate-metadata></div>
        <div class="sc-lab-data-note">Source: NASA Global Imagery Browse Services. Save a map state to preserve the layer, date, region, and source URL in the active project.</div>
      </section>

      <section class="sc-lab-panel" data-lab-module="space-telescopes" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/ASTRONOMY</span><h3>Space telescope observations and releases</h3></div><button class="sc-lab-button sc-lab-button-primary" data-space-load>Load releases</button></div>
        <div class="sc-lab-toolbar"><label>Telescope<select data-space-telescope><option value="all">All</option><option value="JWST">JWST</option><option value="Hubble">Hubble</option><option value="Chandra">Chandra</option><option value="Spitzer">Spitzer</option></select></label><label>Target or topic<input type="search" value="nebula galaxy exoplanet" data-space-query></label><label>Limit<input type="number" min="1" max="30" value="18" data-space-limit></label><button class="sc-lab-button" data-space-dataset disabled>Dataset inspector</button></div><div class="sc-lab-observation-summary" data-space-summary></div>
        <div class="sc-lab-feed-grid" data-space-results></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="marine-biology" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/MARINE</span><h3>Marine biodiversity observations</h3></div><button class="sc-lab-button sc-lab-button-primary" data-marine-load>Query OBIS</button></div>
        <div class="sc-lab-toolbar"><label>Scientific name or taxon<input type="search" value="Cetacea" data-marine-query></label><label>Limit<input type="number" min="1" max="30" value="25" data-marine-limit></label><button class="sc-lab-button" data-marine-dataset disabled>Dataset inspector</button></div><div class="sc-lab-observation-summary" data-marine-summary></div><div class="sc-lab-mini-chart" data-marine-chart></div>
        <div class="sc-lab-feed-grid" data-marine-results></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="dataset-inspector" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/DATA</span><h3>Scientific dataset inspector</h3></div><div class="sc-lab-inline-actions"><button class="sc-lab-button" data-dataset-save>Save dataset</button><button class="sc-lab-button" data-dataset-export>Export CSV</button></div></div>
        <div class="sc-lab-dataset-header" data-dataset-header>No dataset loaded. Open feed results, import CSV, or select a saved project dataset.</div>
        <div class="sc-lab-toolbar"><label>Saved dataset<select data-dataset-select><option value="">Current working dataset</option></select></label><label>Filter rows<input type="search" data-dataset-filter placeholder="Search any field"></label><label>X variable<select data-dataset-x></select></label><label>Y variable<select data-dataset-y></select></label><label>Rows<select data-dataset-limit><option>25</option><option selected>100</option><option>250</option></select></label></div>
        <details class="sc-lab-data-import"><summary>Import CSV or JSON</summary><textarea rows="8" data-dataset-import placeholder="Paste CSV or a JSON array of records"></textarea><button class="sc-lab-button sc-lab-button-primary" data-dataset-import-run>Import data</button></details>
        <div class="sc-lab-dataset-stats" data-dataset-stats></div>
        <div class="sc-lab-grid sc-lab-grid-2"><section><h4>Data table</h4><div data-dataset-table></div></section><section><h4>Variable plot</h4><div class="sc-lab-chart" data-dataset-chart></div></section></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="chemistry" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/CHEMISTRY</span><h3>Chemistry laboratory</h3></div>
          <div class="sc-lab-panel-actions"><button class="sc-lab-button" data-chem-new-experiment>New chemistry experiment</button><button class="sc-lab-button sc-lab-button-primary" data-chem-notebook>Notebook entry</button></div>
        </div>
        <div class="sc-lab-method-note">Calculations are recorded with inputs, outputs, timestamps, and the active project. Review units, assumptions, significant figures, hazards, and experimental conditions before laboratory use.</div>
        <div class="sc-lab-tabs sc-lab-tabs-wrap">
          <button class="is-active" data-chem-tab="periodic">Periodic table</button>
          <button data-chem-tab="composition">Composition</button>
          <button data-chem-tab="reactions">Reactions</button>
          <button data-chem-tab="solutions">Solutions</button>
          <button data-chem-tab="acid-base">Acid–base</button>
          <button data-chem-tab="thermochemistry">Thermochemistry</button>
          <button data-chem-tab="electrochemistry">Electrochemistry</button>
          <button data-chem-tab="kinetics">Kinetics</button>
          <button data-chem-tab="calibration">Calibration</button>
        </div>

        <div data-chem-pane="periodic">
          <div class="sc-lab-toolbar"><label>Find element<input type="search" data-element-search placeholder="Name, symbol, or atomic number"></label><label>Property<select data-element-property><option value="category">Category</option><option value="atomicMass">Atomic mass</option><option value="period">Period</option><option value="group">Group</option></select></label></div>
          <div class="sc-lab-periodic-wrap"><div class="sc-lab-periodic" data-periodic-table></div></div>
          <div class="sc-lab-element-detail" data-element-detail>Select an element.</div>
        </div>

        <div data-chem-pane="composition" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Molar mass and percent composition</h4><label>Chemical formula<input value="Al2(SO4)3" data-formula-input></label><div class="sc-lab-inline-actions"><button class="sc-lab-button sc-lab-button-primary" data-formula-run>Analyze formula</button><button class="sc-lab-button" data-percent-run>Percent composition</button></div><pre data-formula-output></pre></article>
            <article class="sc-lab-tool"><h4>Empirical formula</h4><label>Element amounts JSON<textarea rows="6" data-empirical-input>[{"symbol":"C","amount":40.0},{"symbol":"H","amount":6.7},{"symbol":"O","amount":53.3}]</textarea></label><button class="sc-lab-button sc-lab-button-primary" data-empirical-run>Derive empirical formula</button><pre data-empirical-output></pre></article>
            <article class="sc-lab-tool"><h4>Molecular formula</h4><label>Empirical formula<input value="CH2O" data-molecular-empirical></label><label>Measured molar mass (g mol⁻¹)<input type="number" step="any" value="180.16" data-molecular-mass></label><button class="sc-lab-button sc-lab-button-primary" data-molecular-run>Derive molecular formula</button><pre data-molecular-output></pre></article>
          </div>
        </div>

        <div data-chem-pane="reactions" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Balance reaction</h4><label>Equation<input value="Fe + O2 -> Fe2O3" data-balance-input></label><button class="sc-lab-button sc-lab-button-primary" data-balance-run>Balance exactly</button><pre data-balance-output></pre></article>
            <article class="sc-lab-tool"><h4>Limiting reagent and products</h4><label>Balanced or unbalanced equation<input value="2 H2 + O2 -> 2 H2O" data-limit-equation></label><label>Reactant moles JSON<input value='{"H2":3,"O2":2}' data-limit-moles></label><button class="sc-lab-button sc-lab-button-primary" data-limit-run>Calculate reaction extent</button><pre data-limit-output></pre></article>
            <article class="sc-lab-tool"><h4>Theoretical yield</h4><label>Product formula<input value="H2O" data-yield-product></label><label>Product amount (mol)<input type="number" step="any" value="1.5" data-yield-moles></label><button class="sc-lab-button sc-lab-button-primary" data-yield-run>Calculate mass yield</button><pre data-yield-output></pre></article>
            <article class="sc-lab-tool"><h4>Reaction record</h4><label>Reaction title<input value="Iron oxidation trial" data-reaction-title></label><label>Conditions and observations<textarea rows="5" data-reaction-conditions placeholder="Temperature, pressure, solvent, catalyst, atmosphere, observations"></textarea></label><button class="sc-lab-button sc-lab-button-primary" data-reaction-save>Save reaction record</button><pre data-reaction-save-output></pre></article>
          </div>
        </div>

        <div data-chem-pane="solutions" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Solution concentration</h4><div class="sc-lab-inline-fields"><label>Solute (mol)<input type="number" step="any" value="0.25" data-conc-moles></label><label>Solution (L)<input type="number" step="any" value="0.5" data-conc-volume></label><label>Solute (g)<input type="number" step="any" value="14.61" data-conc-solute-g></label><label>Solvent (kg)<input type="number" step="any" value="0.48" data-conc-solvent-kg></label><label>Solution (g)<input type="number" step="any" value="494.61" data-conc-solution-g></label></div><button class="sc-lab-button sc-lab-button-primary" data-conc-run>Calculate concentration measures</button><pre data-conc-output></pre></article>
            <article class="sc-lab-tool"><h4>Dilution</h4><div class="sc-lab-inline-fields"><label>C₁<input type="number" step="any" value="1" data-dilution-c1></label><label>V₁<input type="number" step="any" value="10" data-dilution-v1></label><label>C₂<input type="number" step="any" value="0.1" data-dilution-c2></label><label>V₂<input type="number" step="any" placeholder="leave one blank" data-dilution-v2></label></div><button class="sc-lab-button sc-lab-button-primary" data-dilution-run>Solve C₁V₁ = C₂V₂</button><pre data-dilution-output></pre></article>
            <article class="sc-lab-tool"><h4>Solubility from Ksp</h4><div class="sc-lab-inline-fields"><label>Ksp<input type="number" step="any" value="1.8e-10" data-ksp></label><label>Cation coefficient<input type="number" step="1" value="1" data-ksp-cation></label><label>Anion coefficient<input type="number" step="1" value="2" data-ksp-anion></label></div><button class="sc-lab-button sc-lab-button-primary" data-ksp-run>Calculate molar solubility</button><pre data-ksp-output></pre></article>
          </div>
        </div>

        <div data-chem-pane="acid-base" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Strong acid or base</h4><div class="sc-lab-inline-fields"><label>Type<select data-strong-type><option value="acid">Acid</option><option value="base">Base</option></select></label><label>Concentration (mol L⁻¹)<input type="number" step="any" value="0.01" data-strong-conc></label><label>H⁺/OH⁻ equivalents<input type="number" step="any" value="1" data-strong-eq></label></div><button class="sc-lab-button sc-lab-button-primary" data-strong-run>Calculate pH</button><pre data-strong-output></pre></article>
            <article class="sc-lab-tool"><h4>Weak acid or base</h4><div class="sc-lab-inline-fields"><label>Model<select data-weak-type><option value="acid">Weak acid</option><option value="base">Weak base</option></select></label><label>Initial concentration<input type="number" step="any" value="0.1" data-weak-conc></label><label>Ka or Kb<input type="number" step="any" value="1.8e-5" data-weak-k></label></div><button class="sc-lab-button sc-lab-button-primary" data-weak-run>Solve equilibrium</button><pre data-weak-output></pre></article>
            <article class="sc-lab-tool"><h4>Buffer</h4><div class="sc-lab-inline-fields"><label>pKa<input type="number" step="any" value="4.76" data-buffer-pka></label><label>HA amount<input type="number" step="any" value="0.1" data-buffer-acid></label><label>A⁻ amount<input type="number" step="any" value="0.1" data-buffer-base></label></div><button class="sc-lab-button sc-lab-button-primary" data-buffer-run>Calculate Henderson–Hasselbalch pH</button><pre data-buffer-output></pre></article>
            <article class="sc-lab-tool"><h4>Strong acid/base titration</h4><div class="sc-lab-inline-fields"><label>Analyte<select data-titration-type><option value="acid">Acid</option><option value="base">Base</option></select></label><label>Analyte concentration<input type="number" step="any" value="0.1" data-titration-analyte-c></label><label>Analyte volume (mL)<input type="number" step="any" value="25" data-titration-analyte-v></label><label>Titrant concentration<input type="number" step="any" value="0.1" data-titration-titrant-c></label><label>Titrant added (mL)<input type="number" step="any" value="12.5" data-titration-titrant-v></label></div><button class="sc-lab-button sc-lab-button-primary" data-titration-run>Calculate titration state</button><pre data-titration-output></pre></article>
          </div>
        </div>

        <div data-chem-pane="thermochemistry" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Calorimetry</h4><div class="sc-lab-inline-fields"><label>Mass (g)<input type="number" step="any" value="100" data-cal-mass></label><label>Specific heat (J g⁻¹ K⁻¹)<input type="number" step="any" value="4.184" data-cal-cp></label><label>Initial °C<input type="number" step="any" value="20" data-cal-ti></label><label>Final °C<input type="number" step="any" value="28" data-cal-tf></label></div><button class="sc-lab-button sc-lab-button-primary" data-cal-run>Calculate heat</button><pre data-cal-output></pre></article>
            <article class="sc-lab-tool"><h4>Gibbs free energy</h4><div class="sc-lab-inline-fields"><label>ΔH (kJ mol⁻¹)<input type="number" step="any" value="-92.4" data-gibbs-h></label><label>ΔS (J mol⁻¹ K⁻¹)<input type="number" step="any" value="-198" data-gibbs-s></label><label>Temperature (K)<input type="number" step="any" value="298.15" data-gibbs-t></label></div><button class="sc-lab-button sc-lab-button-primary" data-gibbs-run>Calculate ΔG and K</button><pre data-gibbs-output></pre></article>
            <article class="sc-lab-tool"><h4>Hess’s law</h4><label>Steps JSON<textarea rows="7" data-hess-input>[{"label":"Step 1","multiplier":1,"deltaHkJ":-393.5},{"label":"Step 2","multiplier":-1,"deltaHkJ":-283.0}]</textarea></label><button class="sc-lab-button sc-lab-button-primary" data-hess-run>Sum reaction enthalpy</button><pre data-hess-output></pre></article>
          </div>
        </div>

        <div data-chem-pane="electrochemistry" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Nernst equation</h4><div class="sc-lab-inline-fields"><label>E° cell (V)<input type="number" step="any" value="1.10" data-nernst-e></label><label>Temperature (K)<input type="number" step="any" value="298.15" data-nernst-t></label><label>Electrons n<input type="number" step="1" value="2" data-nernst-n></label><label>Reaction quotient Q<input type="number" step="any" value="10" data-nernst-q></label></div><button class="sc-lab-button sc-lab-button-primary" data-nernst-run>Calculate cell potential</button><pre data-nernst-output></pre></article>
            <article class="sc-lab-tool"><h4>Electrolysis and Faraday’s law</h4><div class="sc-lab-inline-fields"><label>Current (A)<input type="number" step="any" value="2" data-electrolysis-current></label><label>Time (s)<input type="number" step="any" value="1800" data-electrolysis-time></label><label>Electrons n<input type="number" step="1" value="2" data-electrolysis-n></label><label>Molar mass (g mol⁻¹)<input type="number" step="any" value="63.546" data-electrolysis-mm></label></div><button class="sc-lab-button sc-lab-button-primary" data-electrolysis-run>Calculate deposited mass</button><pre data-electrolysis-output></pre></article>
          </div>
        </div>

        <div data-chem-pane="kinetics" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Arrhenius equation</h4><div class="sc-lab-inline-fields"><label>Pre-exponential factor A<input type="number" step="any" value="1e12" data-arr-a></label><label>Activation energy (kJ mol⁻¹)<input type="number" step="any" value="75" data-arr-ea></label><label>Temperature (K)<input type="number" step="any" value="298.15" data-arr-t></label></div><button class="sc-lab-button sc-lab-button-primary" data-arr-run>Calculate rate constant</button><pre data-arr-output></pre></article>
            <article class="sc-lab-tool"><h4>Integrated rate law</h4><div class="sc-lab-inline-fields"><label>Order<select data-rate-order><option value="0">Zero</option><option value="1" selected>First</option><option value="2">Second</option></select></label><label>k<input type="number" step="any" value="0.02" data-rate-k></label><label>Initial concentration<input type="number" step="any" value="1" data-rate-a0></label><label>Time<input type="number" step="any" value="30" data-rate-time></label></div><button class="sc-lab-button sc-lab-button-primary" data-rate-run>Calculate concentration</button><pre data-rate-output></pre></article>
          </div>
        </div>

        <div data-chem-pane="calibration" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool"><h4>Analytical calibration curve</h4><label>Concentration, signal pairs<textarea rows="9" data-chem-cal-points>0,0.003
1,0.105
2,0.203
3,0.307
4,0.405</textarea></label><label>Unknown signal<input type="number" step="any" value="0.256" data-chem-cal-unknown></label><button class="sc-lab-button sc-lab-button-primary" data-chem-cal-run>Fit calibration and estimate unknown</button><pre data-chem-cal-output></pre></article>
            <article class="sc-lab-tool"><h4>Calibration record</h4><div class="sc-lab-chart" data-chem-cal-chart></div><button class="sc-lab-button" data-chem-cal-save>Save calibration record</button></article>
          </div>
        </div>
      </section>


      <section class="sc-lab-panel" data-lab-module="science-engineering" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/ANALYSIS</span><h3>Science and engineering tools</h3></div></div>
        <div class="sc-lab-tabs"><button class="is-active" data-analysis-tab="calculators">Calculators</button><button data-analysis-tab="spectrometry">Spectrometry Studio</button></div>
        <div data-analysis-pane="calculators"><div class="sc-lab-toolbar"><label>Domain<select data-calculator-domain></select></label><label>Tool<select data-calculator-select></select></label></div><div class="sc-lab-calculator" data-calculator-form></div></div>
        <div data-analysis-pane="spectrometry" hidden>
          <div class="sc-lab-spectrometry-header">
            <div class="sc-lab-toolbar"><label>Method<select data-spectrum-method><option value="uvvis">UV–visible</option><option value="ir">Infrared</option><option value="raman">Raman</option><option value="fluorescence">Fluorescence</option><option value="mass">Mass spectrometry</option><option value="generic">Generic x–y signal</option></select></label><label>Sample ID<input value="SAMPLE-001" data-spectrum-sample></label><label>Title<input value="Analytical spectrum" data-spectrum-title></label></div>
            <div class="sc-lab-method-note">Raw data are retained in memory until the spectrum is saved. Each processing action is recorded in the spectrum history for reproducibility.</div>
          </div>
          <div class="sc-lab-grid sc-lab-grid-2 sc-lab-spectrometry-grid">
            <article class="sc-lab-tool">
              <h4>Raw data and processing</h4>
              <label>CSV or whitespace x,y data<textarea rows="13" data-spectrum-input>400,0.12
425,0.15
450,0.18
475,0.43
500,0.91
525,0.62
550,0.31
575,0.20
600,0.14</textarea></label>
              <div class="sc-lab-inline-actions"><button class="sc-lab-button sc-lab-button-primary" data-spectrum-load>Load raw spectrum</button><button class="sc-lab-button" data-spectrum-reset>Reset to raw</button></div>
              <div class="sc-lab-process-grid">
                <label>Baseline<select data-spectrum-baseline-method><option value="linear">Endpoint linear</option><option value="rolling-minimum">Rolling minimum</option></select></label>
                <label>Window<input type="number" min="3" step="2" value="15" data-spectrum-window></label>
                <button class="sc-lab-button" data-spectrum-baseline>Apply baseline</button>
                <label>Smoothing<select data-spectrum-smooth-method><option value="mean">Moving mean</option><option value="median">Moving median</option></select></label>
                <label>Radius<input type="number" min="1" value="2" data-spectrum-radius></label>
                <button class="sc-lab-button" data-spectrum-smooth>Smooth</button>
                <label>Normalize<select data-spectrum-normalize-mode><option value="max">Maximum</option><option value="area">Area</option><option value="minmax">Min–max</option></select></label>
                <button class="sc-lab-button" data-spectrum-normalize>Normalize</button>
                <button class="sc-lab-button" data-spectrum-derivative>First derivative</button>
                <label>Conversion<select data-spectrum-conversion><option value="none">Select conversion</option><option value="t-to-a">Transmittance fraction → absorbance</option><option value="percent-to-a">Transmittance % → absorbance</option><option value="a-to-t">Absorbance → transmittance fraction</option><option value="a-to-percent">Absorbance → transmittance %</option></select></label>
                <button class="sc-lab-button" data-spectrum-convert>Convert</button>
              </div>
              <h4>Peak detection</h4>
              <div class="sc-lab-inline-fields"><label>Threshold<input type="number" step="any" placeholder="automatic" data-spectrum-threshold></label><label>Minimum distance<input type="number" step="any" value="0" data-spectrum-distance></label><label>Minimum prominence<input type="number" step="any" value="0" data-spectrum-prominence></label></div>
              <div class="sc-lab-inline-actions"><button class="sc-lab-button sc-lab-button-primary" data-spectrum-peaks>Detect and characterize peaks</button><button class="sc-lab-button" data-spectrum-export>Export processed CSV</button></div>
            </article>
            <article class="sc-lab-tool">
              <h4>Spectrum and analytical results</h4>
              <div data-spectrum-chart class="sc-lab-chart sc-lab-spectrum-chart"></div>
              <div class="sc-lab-spectrum-metrics" data-spectrum-metrics></div>
              <div class="sc-lab-spectrum-peaks" data-spectrum-peak-table></div>
              <details><summary>Processing history and numerical output</summary><pre data-spectrum-output></pre></details>
              <div class="sc-lab-inline-actions"><button class="sc-lab-button sc-lab-button-primary" data-spectrum-save>Save spectrum to project</button><button class="sc-lab-button" data-spectrum-note>Add analysis to notebook</button></div>
            </article>
          </div>
          <section class="sc-lab-tool sc-lab-tool-wide sc-lab-calibration-section">
            <h4>Spectrometric calibration</h4>
            <div class="sc-lab-grid sc-lab-grid-2"><div><label>Concentration, signal pairs<textarea rows="7" data-spectrum-cal-points>0,0.002
1,0.101
2,0.201
3,0.302
4,0.402</textarea></label><label>Unknown signal<input type="number" step="any" value="0.251" data-spectrum-cal-unknown></label><button class="sc-lab-button sc-lab-button-primary" data-spectrum-cal-run>Fit calibration</button></div><div><div class="sc-lab-chart" data-spectrum-cal-chart></div><pre data-spectrum-cal-output></pre><button class="sc-lab-button" data-spectrum-cal-save>Save calibration</button></div></div>
          </section>
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

      <section class="sc-lab-panel" data-lab-module="source-registry" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/SOURCES</span><h3>Scientific source registry</h3></div><button class="sc-lab-button sc-lab-button-primary" data-source-refresh>Refresh registry</button></div>
        <div class="sc-lab-toolbar"><label>Filter<input type="search" data-source-filter placeholder="Source, domain, coverage, or format"></label></div>
        <div class="sc-lab-source-registry" data-source-registry></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="system-status" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/STATUS</span><h3>System and connector status</h3></div><button class="sc-lab-button sc-lab-button-primary" data-status-refresh>Run checks</button></div>
        <div class="sc-lab-status-table" data-system-status></div>
      </section>
    </main>
  </div>

  <dialog class="sc-lab-record-dialog" data-record-dialog>
    <form method="dialog" class="sc-lab-record-dialog-shell">
      <header><div><span class="sc-lab-section-code" data-dialog-source>SCIENTIFIC/RECORD</span><h3 data-dialog-title>Scientific record</h3></div><button value="cancel" class="sc-lab-dialog-close" aria-label="Close">×</button></header>
      <div class="sc-lab-dialog-body"><p data-dialog-summary></p><dl data-dialog-meta></dl></div>
      <footer><a class="sc-lab-button" target="_blank" rel="noopener" data-dialog-open-source>Open source</a><a class="sc-lab-button" data-dialog-site-intelligence hidden>Open in Site Intelligence</a><button value="cancel" class="sc-lab-button sc-lab-button-primary">Close</button></footer>
    </form>
  </dialog>

  <div class="sc-lab-toast" role="status" aria-live="polite" data-lab-toast hidden></div>
</div>
