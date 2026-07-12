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
          'physics' => 'Physics laboratory',
          'biology' => 'Biology laboratory',
          'astronomy' => 'Astronomy laboratory',
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
            <button type="button" data-quick-tool="electromagnetism-studio"><strong>Electromagnetism</strong><span>Fields, induction, propagation</span></button>
            <button type="button" data-quick-tool="particle-physics"><strong>Particle Physics</strong><span>Particles, decays, detectors</span></button>
            <button type="button" data-quick-tool="circuit-bench"><strong>Circuit &amp; Signal Bench</strong><span>RLC, filters, frequency response</span></button>
            <button type="button" data-quick-tool="sequence-analysis"><strong>Sequence Analysis</strong><span>DNA, RNA, ORFs, alignments</span></button>
            <button type="button" data-quick-tool="enzyme-kinetics"><strong>Enzyme Kinetics</strong><span>Michaelis–Menten and inhibition</span></button>
            <button type="button" data-quick-tool="orbital-mechanics-lab"><strong>Orbital Mechanics Lab</strong><span>Kepler, transfers, Hill and Roche limits</span></button>
            <button type="button" data-quick-tool="stellar-astrophysics"><strong>Stellar Astrophysics</strong><span>Luminosity, blackbody, gravity, lifetime</span></button>
            <button type="button" data-quick-tool="astronomical-photometry"><strong>Astronomical Photometry</strong><span>Magnitudes, aperture counts, SNR</span></button>
            <button type="button" data-quick-tool="cosmology-tools"><strong>Cosmology</strong><span>Hubble distance and critical density</span></button>
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


      <section class="sc-lab-panel" data-lab-module="physics" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/PHYSICS</span><h3>Physics, electromagnetism, and particle physics laboratory</h3></div>
          <div class="sc-lab-panel-actions"><button type="button" class="sc-lab-button" data-physics-run-benchmarks>Run validation suite</button><button type="button" class="sc-lab-button" data-physics-export-validation>Export validation report</button><button type="button" class="sc-lab-button" data-physics-experiment>New physics experiment</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-note>Notebook entry</button></div>
        </div>
        <div class="sc-lab-method-note">Physics analyses preserve inputs, units, equations, constants, assumptions, validation checks, warnings, numerical outputs, plots, timestamps, and the active project. Validation indicates internal consistency with the stated model; it does not certify experimental apparatus, engineering safety, radiation practice, high-voltage systems, RF exposure, or regulatory compliance.</div>
        <div class="sc-lab-tabs sc-lab-tabs-wrap sc-lab-physics-tabs">
          <button type="button" class="is-active" data-physics-tab="mechanics">Mechanics</button>
          <button type="button" data-physics-tab="waves">Waves</button>
          <button type="button" data-physics-tab="thermo-fluids">Thermo &amp; fluids</button>
          <button type="button" data-physics-tab="optics">Optics</button>
          <button type="button" data-physics-tab="electromagnetism">Electromagnetism</button>
          <button type="button" data-physics-tab="circuits">Circuits &amp; signals</button>
          <button type="button" data-physics-tab="quantum">Quantum</button>
          <button type="button" data-physics-tab="nuclear">Nuclear</button>
          <button type="button" data-physics-tab="particle">Particle physics</button>
          <button type="button" data-physics-tab="measurement">Measurement</button>
        </div>

        <div data-physics-pane="mechanics">
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="kinematics"><h4>Uniform-acceleration kinematics</h4><div class="sc-lab-inline-fields"><label>Initial velocity (m s⁻¹)<input data-physics-field="vi" type="number" step="any" value="5"></label><label>Acceleration (m s⁻²)<input data-physics-field="a" type="number" step="any" value="2"></label><label>Time (s)<input data-physics-field="t" type="number" step="any" value="10"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="projectile"><h4>Projectile trajectory</h4><div class="sc-lab-inline-fields"><label>Launch speed (m s⁻¹)<input data-physics-field="v" type="number" step="any" value="25"></label><label>Angle (°)<input data-physics-field="angle" type="number" step="any" value="40"></label><label>Initial height (m)<input data-physics-field="y0" type="number" step="any" value="1.5"></label><label>Gravity (m s⁻²)<input data-physics-field="g" type="number" step="any" value="9.80665"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Model trajectory</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><div class="sc-lab-chart sc-lab-physics-chart" data-physics-chart></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="pendulum"><h4>Pendulum period</h4><div class="sc-lab-inline-fields"><label>Length (m)<input data-physics-field="length" type="number" step="any" value="1"></label><label>Amplitude (°)<input data-physics-field="amplitude" type="number" step="any" value="10"></label><label>Gravity (m s⁻²)<input data-physics-field="g" type="number" step="any" value="9.80665"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate period</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="spring"><h4>Spring and harmonic oscillator</h4><div class="sc-lab-inline-fields"><label>Spring constant (N m⁻¹)<input data-physics-field="k" type="number" step="any" value="30"></label><label>Mass (kg)<input data-physics-field="m" type="number" step="any" value="0.5"></label><label>Displacement (m)<input data-physics-field="x" type="number" step="any" value="0.1"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze oscillator</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
          </div>
        </div>

        <div data-physics-pane="waves" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="wave"><h4>Wave relation and profile</h4><div class="sc-lab-inline-fields"><label>Frequency (Hz)<input data-physics-field="frequency" type="number" step="any" value="440"></label><label>Wave speed (m s⁻¹)<input data-physics-field="speed" type="number" step="any" value="343"></label><label>Amplitude<input data-physics-field="amplitude" type="number" step="any" value="1"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Generate wave</button><button type="button" class="sc-lab-button" data-physics-save>Save waveform</button></div><div class="sc-lab-chart sc-lab-physics-chart" data-physics-chart></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="sound"><h4>Acoustic intensity</h4><div class="sc-lab-inline-fields"><label>Intensity (W m⁻²)<input data-physics-field="intensity" type="number" step="any" value="0.001"></label><label>Reference (W m⁻²)<input data-physics-field="reference" type="number" step="any" value="1e-12"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate sound level</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
          </div>
        </div>

        <div data-physics-pane="thermo-fluids" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="idealGas"><h4>Ideal gas state</h4><div class="sc-lab-inline-fields"><label>Amount (mol)<input data-physics-field="n" type="number" step="any" value="1"></label><label>Temperature (K)<input data-physics-field="temperature" type="number" step="any" value="298.15"></label><label>Pressure (Pa)<input data-physics-field="pressure" type="number" step="any" value="101325"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate state</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="thermodynamics"><h4>First law and ideal limits</h4><div class="sc-lab-inline-fields"><label>Heat into system (J)<input data-physics-field="q" type="number" step="any" value="500"></label><label>Work on system (J)<input data-physics-field="w" type="number" step="any" value="-120"></label><label>Cold temperature (K)<input data-physics-field="tcold" type="number" step="any" value="290"></label><label>Hot temperature (K)<input data-physics-field="thot" type="number" step="any" value="500"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze system</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="fluid"><h4>Fluid regime and pressure</h4><div class="sc-lab-inline-fields"><label>Density (kg m⁻³)<input data-physics-field="density" type="number" step="any" value="998"></label><label>Velocity (m s⁻¹)<input data-physics-field="velocity" type="number" step="any" value="1.5"></label><label>Length scale (m)<input data-physics-field="length" type="number" step="any" value="0.02"></label><label>Dynamic viscosity (Pa s)<input data-physics-field="viscosity" type="number" step="any" value="0.001002"></label><label>Depth (m)<input data-physics-field="depth" type="number" step="any" value="3"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze flow</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="bernoulli"><h4>Bernoulli pressure relation</h4><div class="sc-lab-inline-fields"><label>P₁ (Pa)<input data-physics-field="p1" type="number" step="any" value="150000"></label><label>Density (kg m⁻³)<input data-physics-field="density" type="number" step="any" value="998"></label><label>v₁ (m s⁻¹)<input data-physics-field="v1" type="number" step="any" value="1"></label><label>v₂ (m s⁻¹)<input data-physics-field="v2" type="number" step="any" value="3"></label><label>z₁ (m)<input data-physics-field="z1" type="number" step="any" value="0"></label><label>z₂ (m)<input data-physics-field="z2" type="number" step="any" value="2"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate P₂</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
          </div>
        </div>

        <div data-physics-pane="optics" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="optics"><h4>Refraction and thin lens</h4><div class="sc-lab-inline-fields"><label>n₁<input data-physics-field="n1" type="number" step="any" value="1"></label><label>n₂<input data-physics-field="n2" type="number" step="any" value="1.5"></label><label>Incident angle (°)<input data-physics-field="theta1" type="number" step="any" value="35"></label><label>Focal length (m)<input data-physics-field="focalLength" type="number" step="any" value="0.1"></label><label>Object distance (m)<input data-physics-field="objectDistance" type="number" step="any" value="0.3"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze optics</button><button type="button" class="sc-lab-button" data-physics-save>Save optical record</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="diffraction"><h4>Single-aperture diffraction</h4><div class="sc-lab-inline-fields"><label>Wavelength (nm)<input data-physics-field="wavelengthNm" type="number" step="any" value="532"></label><label>Aperture (mm)<input data-physics-field="apertureMm" type="number" step="any" value="0.1"></label><label>Screen distance (m)<input data-physics-field="screenDistance" type="number" step="any" value="2"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate pattern scale</button><button type="button" class="sc-lab-button" data-physics-save>Save optical record</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="photon"><h4>Photon and spectral quantities</h4><label>Wavelength (nm)<input data-physics-field="wavelengthNm" type="number" step="any" value="500"></label><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate photon</button><button type="button" class="sc-lab-button" data-physics-save>Save optical record</button></div><pre data-physics-output></pre></article>
          </div>
        </div>

        <div data-physics-pane="electromagnetism" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="coulomb"><h4>Coulomb force and potential energy</h4><div class="sc-lab-inline-fields"><label>q₁ (C)<input data-physics-field="q1" type="number" step="any" value="1e-6"></label><label>q₂ (C)<input data-physics-field="q2" type="number" step="any" value="-2e-6"></label><label>Separation (m)<input data-physics-field="r" type="number" step="any" value="0.25"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate interaction</button><button type="button" class="sc-lab-button" data-physics-save>Save field model</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="pointField"><h4>Multiple point-charge field</h4><label>Charges JSON (q, x, y)<textarea rows="7" data-physics-field="charges">[{"q":1e-6,"x":-0.1,"y":0},{"q":-1e-6,"x":0.1,"y":0}]</textarea></label><div class="sc-lab-inline-fields"><label>Evaluation x (m)<input data-physics-field="x" type="number" step="any" value="0"></label><label>Evaluation y (m)<input data-physics-field="y" type="number" step="any" value="0.2"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Resolve field</button><button type="button" class="sc-lab-button" data-physics-save>Save field model</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="capacitor"><h4>Capacitor network</h4><div class="sc-lab-inline-fields"><label>Capacitances (F)<input data-physics-field="capacitances" value="1e-6,2e-6,4e-6"></label><label>Connection<select data-physics-field="mode"><option value="parallel">Parallel</option><option value="series">Series</option></select></label><label>Voltage (V)<input data-physics-field="voltage" type="number" step="any" value="12"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze network</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="magnetic"><h4>Magnetic fields</h4><div class="sc-lab-inline-fields"><label>Current (A)<input data-physics-field="current" type="number" step="any" value="2"></label><label>Radius (m)<input data-physics-field="r" type="number" step="any" value="0.05"></label><label>Turns<input data-physics-field="turns" type="number" step="any" value="100"></label><label>Solenoid length (m)<input data-physics-field="length" type="number" step="any" value="0.3"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate fields</button><button type="button" class="sc-lab-button" data-physics-save>Save field model</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="lorentz"><h4>Lorentz force and particle orbit</h4><div class="sc-lab-inline-fields"><label>Charge (C)<input data-physics-field="q" type="number" step="any" value="1.602176634e-19"></label><label>Speed (m s⁻¹)<input data-physics-field="v" type="number" step="any" value="2e6"></label><label>Magnetic field (T)<input data-physics-field="B" type="number" step="any" value="0.5"></label><label>Angle (°)<input data-physics-field="angle" type="number" step="any" value="90"></label><label>Mass (kg)<input data-physics-field="mass" type="number" step="any" value="1.67262192369e-27"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze motion</button><button type="button" class="sc-lab-button" data-physics-save>Save field model</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="induction"><h4>Faraday induction</h4><div class="sc-lab-inline-fields"><label>Turns<input data-physics-field="turns" type="number" step="any" value="200"></label><label>Flux change (Wb)<input data-physics-field="deltaFlux" type="number" step="any" value="0.002"></label><label>Time interval (s)<input data-physics-field="deltaTime" type="number" step="any" value="0.05"></label><label>Resistance (Ω)<input data-physics-field="resistance" type="number" step="any" value="10"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate induction</button><button type="button" class="sc-lab-button" data-physics-save>Save field model</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="emWave"><h4>Electromagnetic propagation</h4><div class="sc-lab-inline-fields"><label>Frequency (Hz)<input data-physics-field="frequency" type="number" step="any" value="2.4e9"></label><label>Conductivity (S m⁻¹)<input data-physics-field="conductivity" type="number" step="any" value="5.8e7"></label><label>Relative permeability<input data-physics-field="relativePermeability" type="number" step="any" value="1"></label><label>Relative permittivity<input data-physics-field="relativePermittivity" type="number" step="any" value="1"></label><label>Power (W)<input data-physics-field="power" type="number" step="any" value="1"></label><label>Distance (m)<input data-physics-field="distance" type="number" step="any" value="2"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze propagation</button><button type="button" class="sc-lab-button" data-physics-save>Save field model</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="waveguide"><h4>Rectangular waveguide</h4><div class="sc-lab-inline-fields"><label>Broad dimension a (m)<input data-physics-field="width" type="number" step="any" value="0.02286"></label><label>Relative permittivity<input data-physics-field="relativePermittivity" type="number" step="any" value="1"></label><label>Operating frequency (Hz)<input data-physics-field="frequency" type="number" step="any" value="10e9"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Check cutoff</button><button type="button" class="sc-lab-button" data-physics-save>Save field model</button></div><pre data-physics-output></pre></article>
          </div>
        </div>

        <div data-physics-pane="circuits" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="rlc"><h4>Series RLC and AC power</h4><div class="sc-lab-inline-fields"><label>R (Ω)<input data-physics-field="R" type="number" step="any" value="100"></label><label>L (H)<input data-physics-field="L" type="number" step="any" value="0.01"></label><label>C (F)<input data-physics-field="C" type="number" step="any" value="1e-6"></label><label>Frequency (Hz)<input data-physics-field="frequency" type="number" step="any" value="1591.55"></label><label>RMS voltage (V)<input data-physics-field="voltage" type="number" step="any" value="10"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze circuit</button><button type="button" class="sc-lab-button" data-physics-save>Save circuit analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="frequencySweep"><h4>RLC frequency sweep</h4><div class="sc-lab-inline-fields"><label>R (Ω)<input data-physics-field="R" type="number" step="any" value="100"></label><label>L (H)<input data-physics-field="L" type="number" step="any" value="0.01"></label><label>C (F)<input data-physics-field="C" type="number" step="any" value="1e-6"></label><label>Minimum frequency (Hz)<input data-physics-field="fmin" type="number" step="any" value="10"></label><label>Maximum frequency (Hz)<input data-physics-field="fmax" type="number" step="any" value="100000"></label><label>Points<input data-physics-field="points" type="number" step="1" value="160"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Sweep response</button><button type="button" class="sc-lab-button" data-physics-save>Save circuit analysis</button></div><div class="sc-lab-chart sc-lab-physics-chart" data-physics-chart></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="filter"><h4>First-order RC filter</h4><div class="sc-lab-inline-fields"><label>Type<select data-physics-field="type"><option value="lowpass">Low-pass</option><option value="highpass">High-pass</option></select></label><label>R (Ω)<input data-physics-field="R" type="number" step="any" value="1000"></label><label>C (F)<input data-physics-field="C" type="number" step="any" value="1e-6"></label><label>Frequency (Hz)<input data-physics-field="frequency" type="number" step="any" value="100"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate response</button><button type="button" class="sc-lab-button" data-physics-save>Save circuit analysis</button></div><pre data-physics-output></pre></article>
          </div>
          <div class="sc-lab-method-note">The browser Signal Bench foundation records analytical circuit and waveform results. Direct oscilloscope, serial, and instrument acquisition will route through the local Workbench runner in a later device-integration release.</div>
        </div>

        <div data-physics-pane="quantum" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="deBroglie"><h4>Relativistic de Broglie wavelength</h4><div class="sc-lab-inline-fields"><label>Mass (kg)<input data-physics-field="mass" type="number" step="any" value="9.1093837015e-31"></label><label>Velocity (m s⁻¹)<input data-physics-field="velocity" type="number" step="any" value="1e7"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate wave properties</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="particleBox"><h4>Particle in a one-dimensional box</h4><div class="sc-lab-inline-fields"><label>Quantum number n<input data-physics-field="n" type="number" step="1" value="1"></label><label>Particle mass (kg)<input data-physics-field="mass" type="number" step="any" value="9.1093837015e-31"></label><label>Box length (m)<input data-physics-field="length" type="number" step="any" value="1e-9"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate level</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="tunneling"><h4>Rectangular barrier tunneling</h4><div class="sc-lab-inline-fields"><label>Particle mass (kg)<input data-physics-field="mass" type="number" step="any" value="9.1093837015e-31"></label><label>Barrier energy (eV)<input data-physics-field="barrierEv" type="number" step="any" value="5"></label><label>Particle energy (eV)<input data-physics-field="energyEv" type="number" step="any" value="2"></label><label>Barrier width (nm)<input data-physics-field="widthNm" type="number" step="any" value="1"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Estimate transmission</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="hydrogen"><h4>Hydrogen spectral transition</h4><div class="sc-lab-inline-fields"><label>Initial n<input data-physics-field="ni" type="number" step="1" value="3"></label><label>Final n<input data-physics-field="nf" type="number" step="1" value="2"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate transition</button><button type="button" class="sc-lab-button" data-physics-save>Save analysis</button></div><pre data-physics-output></pre></article>
          </div>
        </div>

        <div data-physics-pane="nuclear" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="decay"><h4>Radioactive decay and activity</h4><div class="sc-lab-inline-fields"><label>Half-life<input data-physics-field="halfLife" type="number" step="any" value="5.27"></label><label>Elapsed time<input data-physics-field="time" type="number" step="any" value="10"></label><label>Initial nuclei or amount<input data-physics-field="initial" type="number" step="any" value="1000000"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate decay</button><button type="button" class="sc-lab-button" data-physics-save>Save nuclear record</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="binding"><h4>Nuclear binding energy</h4><div class="sc-lab-inline-fields"><label>Protons Z<input data-physics-field="protons" type="number" step="1" value="26"></label><label>Neutrons N<input data-physics-field="neutrons" type="number" step="1" value="30"></label><label>Neutral atomic mass (u)<input data-physics-field="atomicMassU" type="number" step="any" value="55.93493633"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate binding</button><button type="button" class="sc-lab-button" data-physics-save>Save nuclear record</button></div><pre data-physics-output></pre></article>
          </div>
        </div>

        <div data-physics-pane="particle" hidden>
          <div class="sc-lab-grid sc-lab-grid-2 sc-lab-particle-reference">
            <article class="sc-lab-tool"><h4>Particle reference</h4><div class="sc-lab-inline-fields"><label>Search<input type="search" data-particle-search placeholder="Particle, symbol, or family"></label><label>Family<select data-particle-family><option value="all">All families</option><option>Lepton</option><option>Quark</option><option>Gauge boson</option><option>Scalar boson</option><option>Baryon</option><option>Meson</option></select></label></div><div class="sc-lab-particle-list" data-particle-list></div></article>
            <article class="sc-lab-tool"><h4>Particle record</h4><div class="sc-lab-particle-detail" data-particle-detail>Select a particle.</div></article>
          </div>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="relativistic"><h4>Relativistic kinematics</h4><div class="sc-lab-inline-fields"><label>Rest mass (kg)<input data-physics-field="massKg" type="number" step="any" value="9.1093837015e-31"></label><label>Velocity (m s⁻¹)<input data-physics-field="velocity" type="number" step="any" value="2.5e8"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate four-kinematics</button><button type="button" class="sc-lab-button" data-physics-save>Save particle event</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="invariantMass"><h4>Invariant mass from four-vectors</h4><label>Four-vectors JSON (E, px, py, pz)<textarea rows="7" data-physics-field="fourVectors">[{"E":60,"px":30,"py":0,"pz":40},{"E":50,"px":-20,"py":0,"pz":-30}]</textarea></label><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Reconstruct invariant mass</button><button type="button" class="sc-lab-button" data-physics-save>Save particle event</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="twoBodyDecay"><h4>Two-body decay kinematics</h4><div class="sc-lab-inline-fields"><label>Parent mass<input data-physics-field="parentMass" type="number" step="any" value="125.25"></label><label>Daughter mass 1<input data-physics-field="mass1" type="number" step="any" value="0"></label><label>Daughter mass 2<input data-physics-field="mass2" type="number" step="any" value="0"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Solve decay</button><button type="button" class="sc-lab-button" data-physics-save>Save particle event</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="detector"><h4>Detector and track reconstruction</h4><div class="sc-lab-inline-fields"><label>Magnetic field (T)<input data-physics-field="B" type="number" step="any" value="2"></label><label>Track radius (m)<input data-physics-field="radius" type="number" step="any" value="1.2"></label><label>|Charge| (e)<input data-physics-field="charge" type="number" step="any" value="1"></label><label>Flight distance (m)<input data-physics-field="distance" type="number" step="any" value="3"></label><label>Flight time (s)<input data-physics-field="time" type="number" step="any" value="1.2e-8"></label><label>Observed events<input data-physics-field="events" type="number" step="any" value="1250"></label><label>Background events<input data-physics-field="background" type="number" step="any" value="400"></label><label>Efficiency<input data-physics-field="efficiency" type="number" step="any" value="0.82"></label><label>Integrated luminosity<input data-physics-field="luminosity" type="number" step="any" value="100"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Analyze detector event</button><button type="button" class="sc-lab-button" data-physics-save>Save detector analysis</button></div><pre data-physics-output></pre></article>
          </div>
        </div>

        <div data-physics-pane="measurement" hidden>
          <div class="sc-lab-grid sc-lab-grid-2">
            <article class="sc-lab-tool" data-physics-tool="uncertainty"><h4>Independent uncertainty combination</h4><label>Standard uncertainties JSON<textarea rows="6" data-physics-field="values">[0.12,0.08,0.05]</textarea></label><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Combine uncertainties</button><button type="button" class="sc-lab-button" data-physics-save>Save measurement record</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="powerLawUncertainty"><h4>Power-law uncertainty propagation</h4><div class="sc-lab-inline-fields"><label>Coefficient<input data-physics-field="coefficient" type="number" step="any" value="1"></label></div><label>Variables JSON<textarea rows="8" data-physics-field="variables">[{"name":"length","value":2.0,"uncertainty":0.01,"power":1},{"name":"width","value":1.5,"uncertainty":0.01,"power":1},{"name":"height","value":0.5,"uncertainty":0.005,"power":1}]</textarea></label><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Propagate uncertainty</button><button type="button" class="sc-lab-button" data-physics-save>Save validation record</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool" data-physics-tool="weightedMean"><h4>Uncertainty-weighted mean and consistency</h4><label>Measurements JSON<textarea rows="8" data-physics-field="measurements">[{"value":9.80,"uncertainty":0.08},{"value":9.85,"uncertainty":0.05},{"value":9.78,"uncertainty":0.07}]</textarea></label><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-run>Calculate weighted mean</button><button type="button" class="sc-lab-button" data-physics-save>Save validation record</button></div><pre data-physics-output></pre></article>
            <article class="sc-lab-tool sc-lab-physics-validation-dashboard"><h4>Physics numerical validation suite</h4><p>Run deterministic benchmark cases spanning mechanics, electromagnetism, circuits, optics, nuclear physics, and particle physics. Results can be saved to the project and exported as JSON.</p><div class="sc-lab-validation-summary" data-physics-benchmark-output><strong>Not run</strong><span>Use “Run validation suite” above.</span></div><div class="sc-lab-table-wrap" data-physics-benchmark-table></div></article>
            <article class="sc-lab-tool"><h4>Physics experiment templates</h4><div class="sc-lab-template-list"><span>Pendulum and gravitational acceleration</span><span>Spring constant and oscillation</span><span>Lens focal length</span><span>Diffraction-grating measurement</span><span>RC time constant</span><span>RLC resonance</span><span>Electromagnetic induction</span><span>Particle-track reconstruction</span><span>Radioactive-decay simulation</span><span>Blackbody-spectrum analysis</span></div><button type="button" class="sc-lab-button sc-lab-button-primary" data-physics-experiment>Create experiment record</button></article>
          </div>
        </div>
      </section>


      <section class="sc-lab-panel" data-lab-module="biology" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/BIOLOGY</span><h3>Biology and computational biology laboratory</h3></div>
          <div class="sc-lab-panel-actions"><button type="button" class="sc-lab-button" data-biology-experiment>Create experiment</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-biology-run-benchmarks>Run validation suite</button></div>
        </div>
        <div class="sc-lab-method-note">Biology analyses preserve sequences, sample context, inputs, model assumptions, validation warnings, numerical outputs, project links, and notebook-ready records. These methods support research, education, and prototyping; they do not replace laboratory controls, validated clinical pipelines, biosafety review, taxonomic expertise, or regulated diagnostic interpretation.</div>
        <div class="sc-lab-tabs sc-lab-tabs-wrap sc-lab-biology-tabs">
          <button type="button" class="is-active" data-biology-tab="cellular">Cellular systems</button>
          <button type="button" data-biology-tab="enzymes">Enzymes</button>
          <button type="button" data-biology-tab="genetics">Genetics</button>
          <button type="button" data-biology-tab="sequences">Sequence lab</button>
          <button type="button" data-biology-tab="proteins">Proteins</button>
          <button type="button" data-biology-tab="population">Population genetics</button>
          <button type="button" data-biology-tab="ecology">Ecology</button>
          <button type="button" data-biology-tab="physiology">Physiology</button>
          <button type="button" data-biology-tab="measurement">Validation</button>
        </div>
        <div data-biology-pane="cellular"><div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="cellular"></div></div>
        <div data-biology-pane="enzymes" hidden><div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="enzymes"></div></div>
        <div data-biology-pane="genetics" hidden><div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="genetics"></div></div>
        <div data-biology-pane="sequences" hidden><div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="sequences"></div></div>
        <div data-biology-pane="proteins" hidden><div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="proteins"></div></div>
        <div data-biology-pane="population" hidden><div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="population"></div></div>
        <div data-biology-pane="ecology" hidden><div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="ecology"></div></div>
        <div data-biology-pane="physiology" hidden><div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="physiology"></div></div>
        <div data-biology-pane="measurement" hidden>
          <div class="sc-lab-grid sc-lab-grid-2" data-biology-tool-grid="measurement"></div>
          <article class="sc-lab-tool sc-lab-tool-wide sc-lab-biology-validation-dashboard">
            <h4>Biology numerical validation suite</h4>
            <p>Deterministic benchmark cases cover enzyme kinetics, sequence composition, translation, population genetics, diversity, qPCR, physiology, and osmotic pressure.</p>
            <div data-biology-benchmark-table class="sc-lab-data-note">Run the validation suite to compare the biology engine with reference cases.</div>
            <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-biology-save-benchmarks>Save validation report</button></div>
          </article>
          <article class="sc-lab-tool sc-lab-tool-wide">
            <h4>Biology experiment templates</h4>
            <div class="sc-lab-template-list"><span>Enzyme-rate experiment</span><span>Serial-dilution and colony count</span><span>DNA extraction and sequence QC</span><span>PCR and gel planning</span><span>qPCR relative-expression study</span><span>Microbial growth curve</span><span>Population diversity survey</span><span>Mark–recapture field study</span><span>Protein sequence characterization</span><span>Membrane-potential model</span></div>
          </article>
        </div>
      </section>


      <section class="sc-lab-panel" data-lab-module="astronomy" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/ASTRONOMY</span><h3>Astronomy and astrophysics laboratory</h3></div>
          <div class="sc-lab-panel-actions"><button type="button" class="sc-lab-button" data-astronomy-experiment>Create observation record</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-astronomy-run-benchmarks>Run validation suite</button></div>
        </div>
        <div class="sc-lab-method-note">Astronomy analyses preserve celestial targets, coordinates, time systems, orbital assumptions, instrument parameters, source data, validation warnings, plots, project links, and notebook-ready records. Simplified models require comparison with authoritative ephemerides, calibrated observations, and current cosmological parameters.</div>
        <div class="sc-lab-tabs sc-lab-tabs-wrap sc-lab-astronomy-tabs">
          <button type="button" class="is-active" data-astronomy-tab="coordinates">Coordinates & time</button>
          <button type="button" data-astronomy-tab="orbits">Orbital mechanics</button>
          <button type="button" data-astronomy-tab="planetary">Planetary systems</button>
          <button type="button" data-astronomy-tab="stellar">Stellar astrophysics</button>
          <button type="button" data-astronomy-tab="photometry">Photometry</button>
          <button type="button" data-astronomy-tab="spectroscopy">Spectroscopy</button>
          <button type="button" data-astronomy-tab="galaxies">Galaxies</button>
          <button type="button" data-astronomy-tab="cosmology">Cosmology</button>
          <button type="button" data-astronomy-tab="telescopes">Telescopes & imaging</button>
          <button type="button" data-astronomy-tab="validation">Validation</button>
        </div>
        <div data-astronomy-pane="coordinates"><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="coordinates"></div></div>
        <div data-astronomy-pane="orbits" hidden><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="orbits"></div></div>
        <div data-astronomy-pane="planetary" hidden><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="planetary"></div></div>
        <div data-astronomy-pane="stellar" hidden><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="stellar"></div></div>
        <div data-astronomy-pane="photometry" hidden><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="photometry"></div></div>
        <div data-astronomy-pane="spectroscopy" hidden><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="spectroscopy"></div></div>
        <div data-astronomy-pane="galaxies" hidden><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="galaxies"></div></div>
        <div data-astronomy-pane="cosmology" hidden><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="cosmology"></div></div>
        <div data-astronomy-pane="telescopes" hidden><div class="sc-lab-grid sc-lab-grid-2" data-astronomy-tool-grid="telescopes"></div></div>
        <div data-astronomy-pane="validation" hidden>
          <article class="sc-lab-tool sc-lab-tool-wide sc-lab-astronomy-validation-dashboard">
            <h4>Astronomy numerical validation suite</h4>
            <p>Reference cases cover coordinates, parallax, Keplerian orbits, stellar radiation, photometry, cosmology, telescope diffraction, exoplanet transits, and compact objects.</p>
            <div data-astronomy-benchmark-table class="sc-lab-data-note">Run the validation suite to compare the astronomy engine with deterministic reference cases.</div>
            <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-astronomy-save-benchmarks>Save validation report</button></div>
          </article>
          <article class="sc-lab-tool sc-lab-tool-wide">
            <h4>Astronomy observation and analysis templates</h4>
            <div class="sc-lab-template-list"><span>Variable-star light curve</span><span>Exoplanet transit</span><span>Astrometric proper motion</span><span>Spectral redshift measurement</span><span>Stellar temperature and luminosity</span><span>Galaxy rotation curve</span><span>Telescope plate-scale calibration</span><span>Photometric aperture and SNR</span><span>Orbital transfer study</span><span>Blackbody spectrum analysis</span></div>
          </article>
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
