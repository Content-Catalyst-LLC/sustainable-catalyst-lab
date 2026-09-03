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
        <span class="sc-lab-version">v<?php echo esc_html(defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : SC_LAB_VERSION); ?></span>
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

    <nav class="sc-lab-workspace-switcher" aria-label="Primary Lab workspaces" data-v0481-workspace-switcher>
      <button type="button" data-open-module="model-studio" data-v0481-workspace="model-studio"><span>MODEL</span><strong>Model Studio</strong></button>
      <button type="button" data-open-module="graph-studio" data-v0481-workspace="graph-studio"><span>GRAPH</span><strong>Graph Studio</strong></button>
      <button type="button" data-open-module="experiments" data-v0481-workspace="experiments"><span>EXPERIMENT</span><strong>Experiments</strong></button>
      <button type="button" data-open-module="scientific-feeds" data-v0481-workspace="scientific-feeds"><span>OBSERVE</span><strong>Observations</strong></button>
    </nav>

    <nav class="sc-lab-context-nav-v0483" aria-label="Contextual Lab tools" data-v0483-context-nav hidden>
      <span class="sc-lab-context-label-v0483" data-v0483-context-label>Workspace</span>
      <div class="sc-lab-context-items-v0483" data-v0483-context-items></div>
    </nav>

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
    <nav id="sc-lab-module-nav" class="sc-lab-nav sc-lab-nav-v0483" aria-label="Lab workspaces" data-lab-nav data-v0483-rail>
      <div class="sc-lab-primary-rail-v0483" data-v0483-primary-rail>
        <button type="button" class="sc-lab-rail-item-v0483" data-open-module="overview" data-v0483-primary="overview" data-rail-symbol="O"><span class="sc-lab-rail-symbol-v0483" aria-hidden="true">O</span><span class="sc-lab-rail-label-v0483">Overview</span></button>
        <button type="button" class="sc-lab-rail-item-v0483" data-open-module="model-studio" data-v0483-primary="model-studio" data-rail-symbol="M"><span class="sc-lab-rail-symbol-v0483" aria-hidden="true">M</span><span class="sc-lab-rail-label-v0483">Model Studio</span></button>
        <button type="button" class="sc-lab-rail-item-v0483" data-open-module="graph-studio" data-v0483-primary="graph-studio" data-rail-symbol="G"><span class="sc-lab-rail-symbol-v0483" aria-hidden="true">G</span><span class="sc-lab-rail-label-v0483">Graph Studio</span></button>
        <button type="button" class="sc-lab-rail-item-v0483" data-open-module="experiments" data-v0483-primary="experiments" data-rail-symbol="E"><span class="sc-lab-rail-symbol-v0483" aria-hidden="true">E</span><span class="sc-lab-rail-label-v0483">Experiments</span></button>
        <button type="button" class="sc-lab-rail-item-v0483" data-open-module="scientific-feeds" data-v0483-primary="scientific-feeds" data-rail-symbol="O"><span class="sc-lab-rail-symbol-v0483" aria-hidden="true">O</span><span class="sc-lab-rail-label-v0483">Observations</span></button>
        <button type="button" class="sc-lab-rail-item-v0483" data-open-module="notebook" data-v0483-primary="notebook" data-rail-symbol="N"><span class="sc-lab-rail-symbol-v0483" aria-hidden="true">N</span><span class="sc-lab-rail-label-v0483">Notebook</span></button>
        <div class="sc-lab-rail-separator-v0483" aria-hidden="true"></div>
        <button type="button" class="sc-lab-rail-item-v0483 sc-lab-rail-item-v0483--utility" data-v0483-tools-toggle aria-expanded="false" aria-controls="sc-lab-tools-v0483"><span class="sc-lab-rail-symbol-v0483" aria-hidden="true">⋯</span><span class="sc-lab-rail-label-v0483">More tools</span></button>
        <button type="button" class="sc-lab-rail-item-v0483 sc-lab-rail-item-v0483--utility" data-v0483-search><span class="sc-lab-rail-symbol-v0483" aria-hidden="true">⌕</span><span class="sc-lab-rail-label-v0483">Search</span></button>
        <button type="button" class="sc-lab-rail-collapse-v0483" data-v0483-rail-collapse aria-pressed="false"><span aria-hidden="true">⇤</span><span class="sc-lab-rail-label-v0483">Collapse rail</span></button>
      </div>

      <?php
      $groups = array(
        'Project' => array(
          'overview' => 'Overview',
          'project-workspace' => 'Project architecture',
          'dataset-registry' => 'Dataset registry',
          'research-provenance' => 'Evidence & provenance',
          'activity' => 'Activity',
        ),
        'Model' => array(
          'model-studio' => 'Model Studio',
          'model-calibration' => 'Model calibration',
          'design-studies' => 'Design studies',
          'model-registry' => 'Scientific model registry',
          'probabilistic-analysis' => 'Uncertainty & sensitivity',
          'ensemble-uncertainty' => 'Registered-model ensembles',
          'surrogate-reduced-order' => 'Surrogate models & reduced-order analysis',
        ),
        'Visualize' => array(
          'graph-studio' => 'Graph Studio',
          'numerical-visualization' => 'Scientific Visualization',
          'visualization-studio' => 'Visualization & export',
        ),
        'Observe' => array(
          'scientific-feeds' => 'Observation board',
          'climate-maps' => 'Climate maps',
          'astronomy-observations' => 'Space & astronomy observations',
          'marine-biology' => 'Marine biology',
        ),
        'Analyze' => array(
          'dataset-inspector' => 'Dataset inspector',
          'numerical-methods' => 'Numerical Methods Studio',
          'numerical-validation' => 'Numerical Validation Library',
          'numerical-governance' => 'Precision & Solver Governance',
          'long-running-jobs' => 'Long Jobs & Checkpoints',
          'chemistry' => 'Chemistry',
          'physics' => 'Physics laboratory',
          'biology' => 'Biology laboratory',
          'astronomy' => 'Astronomy calculations',
          'materials' => 'Materials laboratory',
          'earth-systems' => 'Earth systems laboratory',
          'energy-engineering' => 'Energy & engineering',
          'electrical-embedded' => 'Electrical & embedded',
          'mechanical-thermal' => 'Mechanical & thermal',
          'civil-infrastructure' => 'Civil & infrastructure',
          'architecture-building' => 'Architecture & building performance',
          'urban-planning-spatial' => 'Urban planning & spatial systems',
          'sustainable-cities-resilience' => 'Sustainable cities & urban resilience',
          'comparative-economics-development-systems' => 'Comparative economics & development systems',
          'aerospace-engineering-flight-systems' => 'Aerospace engineering & flight systems',
          'rocket-propulsion-spaceflight' => 'Rocket propulsion & spaceflight',
          'microbiology-laboratory' => 'Microbiology laboratory',
          'biochemistry-molecular-analysis' => 'Biochemistry & molecular analysis',
          'biotechnology-bioprocess-engineering' => 'Biotechnology & bioprocess engineering',
          'biomedical-engineering-biosignals' => 'Biomedical engineering & biosignals',
          'genetics-genomics-sequence-analysis' => 'Genetics, genomics & sequence analysis',
          'laboratory-data-instrumentation' => 'Laboratory data & instrumentation',
          'circular-economy-industrial-ecology' => 'Circular economy & industrial ecology',
          'code-studio' => 'Code switcher',
          'science-engineering' => 'Science & engineering',
        ),
        'Record' => array(
          'experiments' => 'Experiments',
          'evidence-decisions' => 'Evidence & decisions',
          'notebook' => 'Notebook',
          'report-studio' => 'PDF reports',
          'documentation' => 'Documentation',
        ),
        'Research operations' => array(
          'reproducible-runs' => 'Reproducible runs',
          'method-review' => 'Method review',
          'scholarly-discovery' => 'Scholarly discovery',
          'experiment-framework' => 'Experiment framework',
          'manuscript-assembly' => 'Manuscript, report & notebook assembly',
          'public-reproduction' => 'Public reproduction & verification',
          'research-interoperability' => 'Research interoperability',
          'typed-cross-product-handoffs' => 'Typed product handoffs',
          'public-research-integrations' => 'Public API & integrations',
          'team-workspaces' => 'Shared projects & team workspaces',
          'workspace-review' => 'Review, approvals & sign-off',
          'workflow-orchestration' => 'Scientific workflows',
          'workflow-automation' => 'Scheduled & event-driven runs',
          'experiment-campaigns' => 'Adaptive experiment campaigns',
          'closed-loop-campaigns' => 'Closed-loop campaigns',
        ),
        'System' => array(
          'institutional-governance-v0390' => 'Institutional governance',
          'multi-instance-operations-v0392' => 'Backup, migration & recovery',
          'performance-chaos-v0393' => 'Performance, load & chaos validation',
          'connected-platform-beta-v0400' => 'Connected research platform beta',
          'interface-finalization-v0401' => 'Accessible mobile and offline workspace',
          'public-release-hardening-v0402' => 'Migration, compatibility & release hardening',
          'connected-platform-v1000' => 'Connected scientific platform',
          'distributed-dispatcher' => 'Compute dispatcher',
          'persistent-queue' => 'Persistent queue',
          'dispatcher-operations' => 'Dispatcher operations',
          'worker-agent' => 'Secure worker agents',
          'artifact-transport' => 'Artifact transport',
          'workspace-data' => 'Workspace data',
          'source-registry' => 'Source registry',
          'system-status' => 'Connector status',
        ),
      );
      ?>
      <section id="sc-lab-tools-v0483" class="sc-lab-tools-launcher-v0483" data-v0483-tools hidden aria-label="Scientific tools launcher">
        <div class="sc-lab-tools-head-v0483">
          <div><span class="sc-lab-section-code">LAB / TOOLS</span><strong>Scientific tools</strong></div>
          <button type="button" class="sc-lab-button" data-v0483-tools-close aria-label="Close scientific tools">Close</button>
        </div>
        <label class="sc-lab-tools-search-v0483"><span>Find a module</span><input type="search" data-v0483-tools-search placeholder="Search scientific tools…" autocomplete="off"></label>
        <div class="sc-lab-tools-groups-v0483" data-v0483-tools-groups>
      <?php foreach ($groups as $group => $items): ?>
        <div class="sc-lab-nav-group" data-lab-nav-group="<?php echo esc_attr($group); ?>">
          <button type="button" class="sc-lab-nav-heading sc-lab-nav-group-toggle" data-lab-nav-group-toggle aria-expanded="true"><?php echo esc_html($group); ?></button>
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
        </div>
      </section>
    </nav>

    <main class="sc-lab-main">
      <section class="sc-lab-panel sc-lab-overview-v0481" data-lab-module="overview">
        <div class="sc-lab-overview-heading-v0481">
          <div>
            <span class="sc-lab-section-code">LAB / SCIENTIFIC WORKSPACE</span>
            <h3>Model. Visualize. Test. Record.</h3>
            <p>Use the active project as a connected scientific workspace. Start with a model or observation, inspect the evidence visually, then preserve the result as a reproducible project record.</p>
          </div>
          <span class="sc-lab-status-dot is-ready">Ready</span>
        </div>

        <section class="sc-lab-overview-stage-v0481" aria-label="Graph Studio front door">
          <div class="sc-lab-overview-figure-v0481 sc-lab-overview-figure-v0710">
            <div class="sc-lab-overview-figure-head-v0481">
              <div>
                <span class="sc-lab-section-code">ADVANCED VISUALIZATION / 4D PROJECTION</span>
                <h4>Multidimensional response field <span class="sc-lab-v0710-title-tag">Illustrative</span></h4>
                <p>Explore a browser-rendered 4D response surface, vector field, uncertainty envelope, contours, and projected tesseract before opening Graph Studio.</p>
              </div>
              <div class="sc-lab-overview-figure-actions-v0481">
                <button type="button" class="sc-lab-button" data-v0481-open-latest>Latest saved figure</button>
                <button type="button" class="sc-lab-button sc-lab-button-primary" data-open-module="graph-studio">Open Graph Studio</button>
              </div>
            </div>

            <div class="sc-lab-v0710-visualizer" data-v0710-visualizer>
              <div class="sc-lab-v0710-toolbar">
                <div class="sc-lab-v0710-toolbar-group" aria-label="Visualization layers">
                  <button type="button" aria-pressed="true" disabled>4D surface</button>
                  <button type="button" data-v0710-layer="vector" aria-pressed="true">Vector field</button>
                  <button type="button" data-v0710-layer="uncertainty" aria-pressed="true">Uncertainty</button>
                  <button type="button" data-v0710-layer="contours" aria-pressed="true">Contours</button>
                </div>
                <span class="sc-lab-v0710-compute" data-v0710-compute-state data-state="unknown">Checking compute</span>
              </div>

              <div class="sc-lab-v0710-body">
                <div class="sc-lab-v0710-canvas-wrap">
                  <canvas class="sc-lab-v0710-canvas" data-v0710-canvas aria-label="Interactive illustrative four-dimensional scientific response field projected into three dimensions"></canvas>
                  <div class="sc-lab-v0710-overlay" aria-hidden="true">
                    <span class="sc-lab-v0710-chip"><strong>4D</strong> x · y · z · w</span>
                    <span class="sc-lab-v0710-chip">Browser rendered</span>
                    <span class="sc-lab-v0710-chip">No compute required</span>
                  </div>
                  <div class="sc-lab-v0710-readout" data-v0710-readout>Projected 4D response field</div>
                  <div class="sc-lab-v0710-pointer" data-v0710-pointer>Move over the field to inspect coordinates</div>
                </div>

                <aside class="sc-lab-v0710-controls" aria-label="Higher-dimensional visualization controls">
                  <h5>Dimensional context</h5>
                  <p>The fourth dimension is represented by hyperslicing and 4D-to-3D projection, not as a literal fourth spatial axis.</p>
                  <label class="sc-lab-v0710-control"><span>W hyperslice <output>−1 ↔ +1</output></span><input data-v0710-w type="range" min="-1" max="1" step="0.01" value="0.37"></label>
                  <label class="sc-lab-v0710-control"><span>XW rotation <output>4D plane</output></span><input data-v0710-xw type="range" min="-1.4" max="1.4" step="0.01" value="0.34"></label>
                  <label class="sc-lab-v0710-control"><span>YW rotation <output>4D plane</output></span><input data-v0710-yw type="range" min="-1.4" max="1.4" step="0.01" value="-0.22"></label>
                  <button type="button" class="sc-lab-v0710-animate" data-v0710-animate aria-pressed="false">Animate 4D sweep</button>
                </aside>
              </div>

              <div class="sc-lab-v0710-metrics" aria-label="Illustrative visualization diagnostics">
                <div class="sc-lab-v0710-metric"><small>Peak response</small><strong data-v0710-metric="peak">2.48</strong><em>relative illustrative units</em></div>
                <div class="sc-lab-v0710-metric"><small>W hyperslice</small><strong data-v0710-metric="slice">0.37</strong><em>active 4D slice</em></div>
                <div class="sc-lab-v0710-metric"><small>Field density</small><strong>31×31</strong><em>browser sampling grid</em></div>
                <div class="sc-lab-v0710-metric"><small>Layers</small><strong>5</strong><em>surface · vector · uncertainty · contour · polytope</em></div>
              </div>
            </div>
            <p class="sc-lab-v0710-note">This front-door visualization is an illustrative scientific interface demonstration. Saved project figures and computed results remain explicitly identified and are opened in Graph Studio.</p>
          </div>

          <aside class="sc-lab-overview-launcher-v0481" aria-label="Primary research workspaces">
            <span class="sc-lab-section-code">RESEARCH / START</span>
            <h4>Choose a workspace</h4>
            <p>Primary research tools stay one action away. Specialist modules remain available in the navigation and command search.</p>
            <div class="sc-lab-overview-launcher-actions-v0481">
              <button type="button" data-open-module="model-studio"><span>01</span><strong>Model Studio</strong><small>Build, fit, diagnose and compare.</small></button>
              <button type="button" data-open-module="graph-studio"><span>02</span><strong>Graph Studio</strong><small>Inspect and publish scientific figures.</small></button>
              <button type="button" data-open-module="experiments"><span>03</span><strong>Experiments</strong><small>Plan and preserve experimental work.</small></button>
              <button type="button" data-open-module="scientific-feeds"><span>04</span><strong>Observations</strong><small>Bring scientific signals into the project.</small></button>
            </div>
          </aside>
        </section>

        <div class="sc-lab-metrics sc-lab-metrics-v0481" data-overview-metrics></div>

        <div class="sc-lab-overview-work-v0481">
          <section class="sc-lab-dashboard-section sc-lab-dashboard-section-v0481">
            <div class="sc-lab-dashboard-head"><div><span class="sc-lab-section-code">PROJECT / FIGURES</span><h4>Recent scientific figures</h4></div><button type="button" class="sc-lab-text-button" data-open-module="graph-studio">Open library</button></div>
            <div class="sc-lab-overview-figures-v0481" data-v0481-project-figures></div>
          </section>
          <section class="sc-lab-dashboard-section sc-lab-dashboard-section-v0481">
            <div class="sc-lab-dashboard-head"><div><span class="sc-lab-section-code">PROJECT / WORK</span><h4>Active scientific work</h4></div><button type="button" class="sc-lab-text-button" data-open-module="activity">Activity</button></div>
            <div class="sc-lab-project-work" data-project-work></div>
          </section>
        </div>

        <details class="sc-lab-secondary-drawer-v0481">
          <summary><span><span class="sc-lab-section-code">LIVE / SIGNALS</span><strong>Scientific signals</strong></span><small>Earth, space, marine and scholarly observations</small></summary>
          <div class="sc-lab-secondary-drawer-body-v0481">
            <div class="sc-lab-dashboard-head"><div></div><button type="button" class="sc-lab-button" data-overview-refresh>Refresh signals</button></div>
            <div class="sc-lab-overview-signals" data-overview-signals><div class="sc-lab-data-note">Scientific signals load when this drawer is opened or refreshed.</div></div>
          </div>
        </details>

        <details class="sc-lab-secondary-drawer-v0481">
          <summary><span><span class="sc-lab-section-code">TOOLS / SPECIALIST</span><strong>Scientific tool library</strong></span><small>Chemistry, physics, biology, Earth systems, energy and engineering tools</small></summary>
          <div class="sc-lab-secondary-drawer-body-v0481">
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
              <button type="button" data-quick-tool="materials-characterization"><strong>Materials Characterization</strong><span>XRD, lattice parameters, crystallite size</span></button>
              <button type="button" data-quick-tool="mechanical-properties"><strong>Mechanical Properties</strong><span>Stress, fracture, fatigue, and creep</span></button>
              <button type="button" data-quick-tool="materials-microscopy"><strong>Materials Microscopy</strong><span>Particle, grain, and image analysis</span></button>
              <button type="button" data-quick-tool="earth-climate-analysis"><strong>Earth &amp; Climate Analysis</strong><span>Atmosphere, trends, hydrology, carbon</span></button>
              <button type="button" data-quick-tool="ocean-marine-analysis"><strong>Ocean &amp; Marine Systems</strong><span>Waves, circulation, ecology, fisheries</span></button>
              <button type="button" data-quick-tool="remote-hazards"><strong>Remote Sensing &amp; Hazards</strong><span>Indices, classification, recurrence, runup</span></button>
              <button type="button" data-quick-tool="energy-systems"><strong>Energy Systems</strong><span>Balances, efficiency, capacity, intensity</span></button>
              <button type="button" data-quick-tool="renewable-energy"><strong>Renewable Energy</strong><span>Solar, wind, hydro, and resource analysis</span></button>
              <button type="button" data-quick-tool="storage-grid"><strong>Storage &amp; Grid</strong><span>Batteries, hydrogen, power systems, reliability</span></button>
              <button type="button" data-quick-tool="energy-economics"><strong>Energy Economics</strong><span>LCOE, LCOS, NPV, emissions, reliability</span></button>
              <button type="button" data-quick-tool="orbit"><strong>Orbital Mechanics</strong><span>Velocity and period</span></button>
              <button type="button" data-quick-tool="uncertainty"><strong>Uncertainty</strong><span>Independent propagation</span></button>
              <button type="button" data-quick-tool="pv"><strong>Energy Systems</strong><span>Photovoltaic output</span></button>
            </div>
          </div>
        </details>

        <details class="sc-lab-secondary-drawer-v0481">
          <summary><span><span class="sc-lab-section-code">PROJECT / TRACE</span><strong>Traceability and recent activity</strong></span><small>Sources → observations → evidence → models → experiments → decisions</small></summary>
          <div class="sc-lab-secondary-drawer-body-v0481">
            <div class="sc-lab-dashboard-columns">
              <section><div class="sc-lab-dashboard-head"><div><h4>Traceability map</h4></div></div><div class="sc-lab-trace-map" data-traceability></div></section>
              <section><div class="sc-lab-dashboard-head"><div><h4>Recent activity</h4></div><button type="button" class="sc-lab-text-button" data-open-module="activity">View all</button></div><div class="sc-lab-list" data-recent-activity></div></section>
            </div>
          </div>
        </details>

        <div class="sc-lab-empty-state sc-lab-empty-state-v0481" data-overview-empty hidden>
          <h4>Start a scientific record</h4>
          <p>Create a model, figure, experiment, observation, or notebook entry. Every result remains connected to the active project.</p>
          <div class="sc-lab-empty-actions">
            <button type="button" class="sc-lab-button" data-open-module="model-studio">Build model</button>
            <button type="button" class="sc-lab-button" data-open-module="graph-studio">Create figure</button>
            <button type="button" class="sc-lab-button" data-command-action="experiment">Create experiment</button>
            <button type="button" class="sc-lab-button sc-lab-button-primary" data-command-action="note">Add notebook entry</button>
          </div>
        </div>
      </section>

      <section class="sc-lab-panel sc-lab-project-workspace-v0280" data-lab-module="project-workspace" data-module-panel="project-workspace" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/PROJECT-ARCHITECTURE</span><h3>Project and Workspace Data Architecture</h3></div><span class="sc-lab-status-dot is-ready">Schema 0.28.0</span></div>
        <div class="sc-lab-method-note">One compatibility-preserving project model now links experiments, datasets, models, calculations, notes, sources, reports, and compute jobs across every laboratory. Existing v0.20.0 browser projects migrate in place; unknown fields are retained.</div>
        <div class="sc-ws0280-status" data-workspace-v0280-status role="status" aria-live="polite">Loading project architecture…</div>
        <div class="sc-ws0280-metrics" data-workspace-v0280-metrics></div>
        <div class="sc-ws0280-grid">
          <section class="sc-ws0280-card is-wide"><div class="sc-lab-panel-head"><div><h4>Project record index</h4><span data-workspace-v0280-project-name></span></div><span data-workspace-v0280-record-count>0 records</span></div><div class="sc-ws0280-toolbar"><label>Search<input type="search" data-workspace-v0280-search placeholder="Title, type, collection, or method"></label><label>Record type<select data-workspace-v0280-type><option value="">All record types</option></select></label></div><div class="sc-ws0280-table-wrap" role="region" aria-label="Project record index" tabindex="0"><table class="sc-ws0280-table"><thead><tr><th>Record</th><th>Type</th><th>Collection</th><th>Status</th><th>Updated</th></tr></thead><tbody data-workspace-v0280-records></tbody></table></div></section>
          <section class="sc-ws0280-card"><h4>Schema and migration</h4><div class="sc-ws0280-migration" data-workspace-v0280-migration></div><p class="sc-ws0280-note" data-workspace-v0280-storage></p><div class="sc-ws0280-actions"><button type="button" class="sc-lab-button" data-workspace-v0280-migrate>Normalize all projects</button><button type="button" class="sc-lab-button" data-workspace-v0280-export>Export project bundle</button><button type="button" class="sc-lab-button" data-workspace-v0280-import>Import project bundle</button><input type="file" accept="application/json,.json" hidden data-workspace-v0280-file></div></section>
          <section class="sc-ws0280-card"><h4>Project checkpoints</h4><div class="sc-ws0280-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-workspace-v0280-checkpoint>Create checkpoint</button></div><div class="sc-ws0280-list" data-workspace-v0280-checkpoints></div></section>
          <section class="sc-ws0280-card is-wide"><h4>Record relationships</h4><div class="sc-ws0280-relationship-fields"><label>From<select data-workspace-v0280-from><option value="">Choose a record</option></select></label><label>To<select data-workspace-v0280-to><option value="">Choose a record</option></select></label><label>Relationship<select data-workspace-v0280-relationship-type><option value="related-to">Related to</option><option value="derived-from">Derived from</option><option value="supports">Supports</option><option value="tests">Tests</option><option value="documents">Documents</option><option value="uses">Uses</option></select></label><div class="sc-ws0280-actions"><button type="button" class="sc-lab-button" data-workspace-v0280-relationship-add>Add relationship</button></div></div><div class="sc-ws0280-list" data-workspace-v0280-relationships></div></section>
        </div>
      </section>




      <section class="sc-lab-panel sc-exp0300" data-lab-module="experiment-framework" data-module-panel="experiment-framework" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/EXPERIMENTS</span><h3>Reproducible Experiment Framework</h3></div><span class="sc-lab-status-dot is-ready">Schema 0.30.0</span></div>
        <p>Design protocols before execution, freeze hypotheses and analysis plans, record governed runs and deviations, compare replications, and export a portable experiment bundle.</p>
        <div class="sc-exp0300-status" data-exp-v0300-status role="status" aria-live="polite">Loading experiment framework…</div><div class="sc-exp0300-metrics" data-exp-v0300-metrics></div>
        <div class="sc-exp0300-grid">
          <section class="sc-exp0300-card is-wide"><h4>Experiment protocol</h4><div class="sc-exp0300-form">
            <input type="hidden" data-exp-v0300-protocol-id><label>Title<input data-exp-v0300-title value="Controlled growth response experiment"></label><label>Domain<input data-exp-v0300-domain value="Scientific experiment"></label><label>Design<select data-exp-v0300-design><option value="observational">Observational</option><option value="controlled" selected>Controlled</option><option value="randomized-controlled">Randomized controlled</option><option value="factorial">Factorial</option><option value="crossover">Crossover</option><option value="simulation">Simulation</option><option value="field-study">Field study</option><option value="replication">Replication</option></select></label><label>Protocol status<select data-exp-v0300-protocol-status><option value="draft">Draft</option><option value="preregistered">Preregistered</option><option value="active">Active</option><option value="completed">Completed</option><option value="suspended">Suspended</option><option value="archived">Archived</option></select></label>
            <label class="is-wide">Objective<textarea rows="2" data-exp-v0300-objective>Measure the effect of the independent variable on the dependent outcome.</textarea></label><label class="is-wide">Hypothesis<textarea rows="2" data-exp-v0300-hypothesis>The independent variable produces a measurable change in the dependent outcome.</textarea></label><label class="is-wide">Null hypothesis<textarea rows="2" data-exp-v0300-null>No measurable difference exists between conditions.</textarea></label>
            <label class="is-wide">Variables — one per line: name | role | unit<textarea rows="5" data-exp-v0300-variables>treatment|independent|condition\noutcome|dependent|unit</textarea></label><label>Controls — one per line<textarea rows="4" data-exp-v0300-controls>control condition</textarea></label><label>Procedure — one step per line<textarea rows="4" data-exp-v0300-procedure>Assign conditions\nApply procedure\nMeasure outcome\nRecord deviations</textarea></label>
            <label>Target sample size<input type="number" min="0" data-exp-v0300-sample-size value="30"></label><label>Preregistration identifier<input data-exp-v0300-preregistration></label><label class="is-wide">Analysis plan<textarea rows="3" data-exp-v0300-analysis>Compare prespecified outcome measures across conditions and report effect sizes, uncertainty, exclusions, and deviations.</textarea></label><label>Randomization<textarea rows="2" data-exp-v0300-randomization></textarea></label><label>Blinding<textarea rows="2" data-exp-v0300-blinding></textarea></label><label class="is-wide">Linked source IDs — one per line<textarea rows="2" data-exp-v0300-sources></textarea></label>
          </div><div class="sc-exp0300-actions"><button class="sc-lab-button" data-exp-v0300-validate>Validate protocol</button><button class="sc-lab-button sc-lab-button-primary" data-exp-v0300-save>Save protocol</button><button class="sc-lab-button" data-exp-v0300-export>Export experiment bundle</button></div></section>
          <section class="sc-exp0300-card"><h4>Record experiment run</h4><div class="sc-exp0300-form"><label class="is-wide">Run title<input data-exp-v0300-run-title></label><label>Replicate<input type="number" min="1" value="1" data-exp-v0300-replicate></label><label>Status<select data-exp-v0300-run-status><option value="planned">Planned</option><option value="running">Running</option><option value="completed" selected>Completed</option><option value="failed">Failed</option><option value="excluded">Excluded</option></select></label><label>Operator<input data-exp-v0300-operator></label><label>Location<input data-exp-v0300-location></label><label class="is-wide">Results JSON<textarea rows="5" data-exp-v0300-result-json>{"outcome": 1.0}</textarea></label><label class="is-wide">Deviations — one per line<textarea rows="3" data-exp-v0300-deviations></textarea></label></div><div class="sc-exp0300-actions"><button class="sc-lab-button sc-lab-button-primary" data-exp-v0300-run>Record run</button></div></section>
          <section class="sc-exp0300-card"><h4>Replication and reporting</h4><label>Select two or more runs<select multiple size="8" data-exp-v0300-run-select></select></label><label>Relative tolerance<input type="number" min="0" step="0.001" value="0.05" data-exp-v0300-tolerance></label><div class="sc-exp0300-actions"><button class="sc-lab-button" data-exp-v0300-compare>Compare runs</button><button class="sc-lab-button" data-exp-v0300-report>Build report</button></div></section>
          <section class="sc-exp0300-card"><h4>Saved protocols</h4><div class="sc-exp0300-list" data-exp-v0300-protocols></div></section>
          <section class="sc-exp0300-card is-wide"><h4>Run history</h4><div class="sc-exp0300-table-wrap"><table class="sc-exp0300-table"><thead><tr><th>Run</th><th>Protocol</th><th>Replicate</th><th>Status</th><th>Completed</th></tr></thead><tbody data-exp-v0300-runs></tbody></table></div></section>
          <section class="sc-exp0300-card is-wide"><h4>Validation, comparison, and report output</h4><pre class="sc-exp0300-output" data-exp-v0300-output>No output yet.</pre></section>
        </div>
      </section>


      <section class="sc-lab-panel sc-doe0301" data-lab-module="design-studies" data-module-panel="design-studies" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/DESIGN-STUDIES</span><h3>Parameter Studies and Design of Experiments</h3></div><span class="sc-lab-status-dot is-ready">Schema 0.30.1</span></div>
        <p>Generate governed experimental designs, attach them to project protocols, record observed responses, fit bounded response models, rank sensitivities, and prepare registered-method batch plans.</p>
        <div class="sc-doe0301-status" data-doe-v0301-status role="status" aria-live="polite">Loading design-study architecture…</div><div class="sc-doe0301-metrics" data-doe-v0301-metrics></div>
        <div class="sc-doe0301-grid">
          <section class="sc-doe0301-card is-wide"><h4>Study definition</h4><div class="sc-doe0301-form">
            <label>Title<input data-doe-v0301-title value="Controlled parameter study"></label><label>Linked experiment protocol<select data-doe-v0301-protocol><option value="">No linked protocol</option></select></label><label>Purpose<select data-doe-v0301-purpose><option value="screening">Screening</option><option value="space-filling">Space filling</option><option value="optimization">Optimization</option><option value="response-surface">Response surface</option></select></label>
            <label>Design<select data-doe-v0301-design><option value="full-factorial">Full factorial</option><option value="fractional-factorial">Fractional factorial</option><option value="latin-hypercube">Latin hypercube</option><option value="central-composite">Central composite</option><option value="box-behnken">Box-Behnken</option><option value="one-factor-at-a-time">One factor at a time</option></select></label><label>Objective<select data-doe-v0301-objective><option value="explore">Explore</option><option value="maximize">Maximize</option><option value="minimize">Minimize</option><option value="target">Target</option></select></label><label>Target value<input type="number" step="any" data-doe-v0301-target></label>
            <label>Response name<input data-doe-v0301-response value="outcome"></label><label>Response unit<input data-doe-v0301-response-unit></label><label>Run budget<input type="number" min="2" max="2000" value="20" data-doe-v0301-budget></label><label>Random seed<input type="number" value="42" data-doe-v0301-seed></label><label>Center points<input type="number" min="1" max="20" value="3" data-doe-v0301-centers></label><label>Registered method ID<input data-doe-v0301-method placeholder="simulation.parameter_sweep"></label>
            <label class="is-wide">Factors — name | type | low | high | levels comma-separated | unit<textarea rows="6" data-doe-v0301-factors>temperature|continuous|10|30||°C
pressure|continuous|1|3||bar</textarea></label><label class="is-wide">Notes<textarea rows="2" data-doe-v0301-notes></textarea></label>
          </div><div class="sc-doe0301-actions"><button class="sc-lab-button" data-doe-v0301-recommend>Recommend design</button><button class="sc-lab-button sc-lab-button-primary" data-doe-v0301-generate>Generate design</button><button class="sc-lab-button" data-doe-v0301-batch>Build batch plan</button><button class="sc-lab-button" data-doe-v0301-export>Export bundle</button></div></section>
          <section class="sc-doe0301-card is-wide"><div class="sc-lab-panel-head"><h4>Design matrix and observed response</h4><span data-doe-v0301-run-count>0 runs</span></div><div class="sc-doe0301-table-wrap"><table class="sc-doe0301-table"><thead><tr data-doe-v0301-matrix-head><th>Design</th></tr></thead><tbody data-doe-v0301-matrix></tbody></table></div><div class="sc-doe0301-actions"><button class="sc-lab-button sc-lab-button-primary" data-doe-v0301-analyze>Analyze responses</button></div></section>
          <section class="sc-doe0301-card"><h4>Saved studies</h4><div class="sc-doe0301-list" data-doe-v0301-studies></div></section>
          <section class="sc-doe0301-card"><h4>Governed output</h4><pre class="sc-doe0301-output" data-doe-v0301-output>No design generated.</pre></section>
        </div>

        <details class="sc-doe0560" data-advanced-design-v0560>
          <summary>Advanced experimental design &amp; sequential experimentation</summary>
          <div class="sc-doe0560__body">
            <p class="sc-doe0560__intro">Generate bounded D-optimal or maximin designs, inspect information-matrix diagnostics, assign balanced blocks and center replicates, and propose sequential augmentation without automatically executing or stopping an experiment.</p>
            <p class="sc-doe0560__status" data-doe-v0560-status role="status" aria-live="polite">Advanced experimental design ready. The factor definition above remains the source of truth.</p>
            <div class="sc-doe0560__metrics" data-doe-v0560-metrics></div>
            <div class="sc-doe0560__grid">
              <section class="sc-doe0560__card is-wide"><h4>Optimal initial design</h4><div class="sc-doe0560__fields">
                <label>Criterion<select data-doe-v0560-criterion><option value="d-optimal" selected>D-optimal information</option><option value="maximin">Maximin space filling</option></select></label>
                <label>Model order<select data-doe-v0560-model-order><option value="linear">Linear main effects</option><option value="interaction">Main effects + interactions</option><option value="quadratic" selected>Quadratic response surface</option></select></label>
                <label>Initial run budget<input type="number" min="2" max="500" value="12" data-doe-v0560-runs></label>
                <label>Candidate pool<input type="number" min="12" max="1500" value="240" data-doe-v0560-candidates></label>
                <label>Blocks<input type="number" min="1" max="20" value="1" data-doe-v0560-blocks></label>
                <label>Center replicates<input type="number" min="0" max="20" value="2" data-doe-v0560-centers></label>
                <label>Seed<input type="number" value="42" data-doe-v0560-seed></label>
                <label>Objective<select data-doe-v0560-objective><option value="explore" selected>Explore</option><option value="maximize">Maximize</option><option value="minimize">Minimize</option><option value="target">Target</option></select></label>
                <label>Target value<input type="number" step="any" data-doe-v0560-target></label>
                <label class="is-wide"><span><input type="checkbox" checked data-doe-v0560-randomize> Randomize proposed run order</span></label>
                <label class="is-wide">Design evidence / protocol note<textarea rows="3" data-doe-v0560-evidence placeholder="Why these factor bounds, model order, blocks, replication, and stopping criteria are scientifically justified."></textarea></label>
              </div><div class="sc-doe0560__actions"><button type="button" class="sc-lab-button" data-doe-v0560-example>Load example</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-doe-v0560-generate>Generate advanced design</button><button type="button" class="sc-lab-button" data-doe-v0560-save-design>Save design evidence</button><button type="button" class="sc-lab-button" data-doe-v0560-graph>Graph design space</button><button type="button" class="sc-lab-button" data-doe-v0560-graph-studio>Open in Graph Studio</button></div></section>
              <section class="sc-doe0560__card is-wide"><div class="sc-lab-panel-head"><h4>Initial design and observed response</h4><span>Responses remain editable evidence</span></div><div class="sc-doe0560__table"><table><thead><tr data-doe-v0560-matrix-head><th>Run</th><th>Design</th></tr></thead><tbody data-doe-v0560-matrix><tr><td>No advanced design generated.</td></tr></tbody></table></div></section>
              <section class="sc-doe0560__card"><h4>Optimality diagnostics</h4><pre class="sc-doe0560__output" data-doe-v0560-diagnostics>No diagnostics yet.</pre><div class="sc-doe0560__canvas" data-doe-v0560-canvas><div class="sc-lab-data-note">Generate a design, then graph its coded design space.</div></div></section>
              <section class="sc-doe0560__card"><h4>Sequential augmentation</h4><div class="sc-doe0560__fields">
                <label>Strategy<select data-doe-v0560-strategy><option value="information-gain" selected>Information gain</option><option value="response-guided">Response-guided heuristic</option></select></label>
                <label>Next batch<input type="number" min="1" max="50" value="3" data-doe-v0560-batch></label>
                <label>Maximum total runs<input type="number" min="2" max="500" value="18" data-doe-v0560-max-total></label>
                <label>Minimum relative information gain<input type="number" min="0" step="0.001" value="0" data-doe-v0560-min-gain></label>
                <label>Exploration weight<input type="number" min="0" step="0.1" value="1" data-doe-v0560-exploration></label>
              </div><div class="sc-doe0560__actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-doe-v0560-sequential>Propose next batch</button><button type="button" class="sc-lab-button" data-doe-v0560-save-plan>Save sequential proposal</button></div><div class="sc-doe0560__review" data-doe-v0560-stopping><strong>REVIEW</strong><span>Stopping evidence appears here. Lab never stops or executes the experiment automatically.</span></div></section>
              <section class="sc-doe0560__card is-wide"><h4>Sequential proposal</h4><div class="sc-doe0560__table"><table><thead><tr data-doe-v0560-proposal-head><th>Run</th><th>Proposal</th></tr></thead><tbody data-doe-v0560-proposal><tr><td>No sequential proposal yet.</td></tr></tbody></table></div><details><summary>Governed record</summary><pre class="sc-doe0560__output" data-doe-v0560-record>No advanced design record yet.</pre></details></section>
            </div>
          </div>
        </details>
      </section>

      <section class="sc-lab-panel sc-lab-provenance-v0290" data-lab-module="research-provenance" data-module-panel="research-provenance" hidden>
        <header><p class="sc-lab-eyebrow">Project governance</p><h2>Evidence, Sources, and Research Provenance</h2><p>Capture sources, quotations, assumptions, limitations, citations, and evidence links as durable project records.</p><div data-prov-v0290-status role="status">Loading provenance workspace…</div></header>
        <div class="sc-lab-prov-metrics" data-prov-v0290-metrics></div>
        <div class="sc-lab-prov-grid"><article class="sc-lab-prov-card"><h3>Add source</h3><label>Title<input data-prov-v0290-title></label><label>Authors, separated by semicolons<input data-prov-v0290-authors></label><label>Year<input data-prov-v0290-year></label><label>Type<select data-prov-v0290-type><option>journal-article</option><option>book</option><option>report</option><option>dataset</option><option>website</option><option>other</option></select></label><label>Publisher<input data-prov-v0290-publisher></label><label>DOI<input data-prov-v0290-doi></label><label>URL<input data-prov-v0290-url></label><label>License<input data-prov-v0290-license></label><button type="button" class="sc-lab-button" data-prov-v0290-add-source>Save source</button></article>
        <article class="sc-lab-prov-card"><h3>Capture evidence</h3><label>Source<select data-prov-v0290-source></select></label><label>Evidence excerpt<textarea rows="5" data-prov-v0290-excerpt></textarea></label><label>Locator<input data-prov-v0290-locator placeholder="p. 42, table 3, section 2"></label><label>Claim supported or challenged<textarea rows="3" data-prov-v0290-claim></textarea></label><label>Strength<select data-prov-v0290-strength><option>supporting</option><option>contradicting</option><option>contextual</option><option>uncertain</option></select></label><button type="button" class="sc-lab-button" data-prov-v0290-add-evidence>Capture evidence</button></article>
        <article class="sc-lab-prov-card"><h3>Assumptions and limitations</h3><label>Assumption<textarea rows="3" data-prov-v0290-assumption></textarea></label><button type="button" class="sc-lab-button" data-prov-v0290-add-assumption>Add assumption</button><label>Limitation<textarea rows="3" data-prov-v0290-limitation></textarea></label><button type="button" class="sc-lab-button" data-prov-v0290-add-limitation>Add limitation</button></article>
        <article class="sc-lab-prov-card"><h3>Link evidence to a project record</h3><label>Subject record ID<input data-prov-v0290-subject></label><label>Sources<select multiple size="5" data-prov-v0290-link-sources></select></label><label>Evidence<select multiple size="5" data-prov-v0290-link-evidence></select></label><button type="button" class="sc-lab-button" data-prov-v0290-link>Create provenance link</button><button type="button" class="sc-lab-button" data-prov-v0290-export>Export provenance bundle</button></article></div>
        <div class="sc-lab-prov-table"><h3>Sources</h3><table><thead><tr><th>Title</th><th>Authors</th><th>Year</th><th>In-text citation</th></tr></thead><tbody data-prov-v0290-sources></tbody></table></div>
        <div class="sc-lab-prov-table"><h3>Evidence</h3><table><thead><tr><th>Source</th><th>Claim</th><th>Locator</th><th>Strength</th></tr></thead><tbody data-prov-v0290-evidence></tbody></table></div>
      </section>
      <section class="sc-lab-panel sc-lab-quality-v0291" data-lab-module="method-review" data-module-panel="method-review" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/RESEARCH-QUALITY</span><h3>Research Quality and Method Review</h3></div><span class="sc-lab-status-dot is-ready">Schema 0.29.1</span></div>
        <p>Review scientific and computational methods against benchmark coverage, validation evidence, reproducibility, provenance, calibration, limitations, and documented reviewer decisions.</p>
        <div class="sc-quality0291-statusline" data-quality-v0291-status role="status" aria-live="polite">Loading method-review registry…</div>
        <div class="sc-quality0291-metrics" data-quality-v0291-metrics></div>
        <div class="sc-quality0291-grid">
          <section class="sc-quality0291-card"><h4>Method and review scope</h4><div class="sc-quality0291-form">
            <label class="is-wide">Existing project method<select data-quality-v0291-candidate><option value="">Choose existing method record</option></select></label>
            <label>Method ID<input data-quality-v0291-method-id placeholder="numerical.root.bracketed_polynomial"></label><label>Method title<input data-quality-v0291-title></label>
            <label>Method version<input data-quality-v0291-method-version></label><label>Domain<input data-quality-v0291-domain></label>
            <label>Method owner<input data-quality-v0291-owner></label><label>Risk tier<select data-quality-v0291-risk><option value="exploratory">Exploratory</option><option value="standard" selected>Standard</option><option value="high-consequence">High consequence</option></select></label>
            <label>Review status<select data-quality-v0291-review-status><option value="draft">Draft</option><option value="under-review">Under review</option><option value="changes-requested">Changes requested</option><option value="conditionally-approved">Conditionally approved</option><option value="approved">Approved</option><option value="rejected">Rejected</option><option value="deprecated">Deprecated</option></select></label>
          </div></section>
          <section class="sc-quality0291-card"><h4>Coverage and evidence</h4><div class="sc-quality0291-form">
            <label>Benchmarks passed<input type="number" min="0" value="0" data-quality-v0291-bench-passed></label><label>Benchmarks total<input type="number" min="0" value="0" data-quality-v0291-bench-total></label>
            <label class="is-wide">Benchmark IDs<textarea rows="3" data-quality-v0291-bench-ids placeholder="One benchmark ID per line"></textarea></label>
            <label>Validation evidence<select multiple data-quality-v0291-validation-evidence></select></label><label>Research sources<select multiple data-quality-v0291-sources></select></label>
            <label>Evidence records<select multiple data-quality-v0291-evidence></select></label><label>Reproducible runs<select multiple data-quality-v0291-runs></select></label>
            <label class="is-wide">Provenance records<select multiple data-quality-v0291-provenance></select></label>
          </div></section>
          <section class="sc-quality0291-card"><h4>Limitations, calibration, and reviewer</h4><div class="sc-quality0291-form">
            <label>Assumptions<textarea rows="4" data-quality-v0291-assumptions placeholder="One per line"></textarea></label><label>Known limitations<textarea rows="4" data-quality-v0291-limitations placeholder="One per line"></textarea></label>
            <label class="is-wide">Known issues<textarea rows="3" data-quality-v0291-issues placeholder="One per line"></textarea></label>
            <label>Calibration status<select data-quality-v0291-calibration><option value="not-required">Not required</option><option value="uncalibrated">Uncalibrated</option><option value="calibrated">Calibrated</option><option value="due">Due</option><option value="expired">Expired</option></select></label><label>Calibration reference<input data-quality-v0291-calibration-reference></label>
            <label>Last calibrated<input type="date" data-quality-v0291-calibrated-at></label><label>Calibration due<input type="date" data-quality-v0291-calibration-due></label>
            <label>Reviewer name<input data-quality-v0291-reviewer></label><label>Reviewer role<input data-quality-v0291-reviewer-role></label><label class="sc-quality0291-check is-wide"><input type="checkbox" data-quality-v0291-independent> Independent reviewer</label>
            <label class="is-wide">Reviewer notes<textarea rows="5" data-quality-v0291-notes></textarea></label>
          </div><div class="sc-quality0291-actions"><button type="button" class="sc-lab-button" data-quality-v0291-new>New review</button><button type="button" class="sc-lab-button" data-quality-v0291-evaluate>Evaluate</button><button type="button" class="sc-lab-button" data-quality-v0291-save>Save draft</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-quality-v0291-submit>Submit for review</button></div></section>
          <section class="sc-quality0291-card"><h4>Policy evaluation</h4><div class="sc-quality0291-evaluation" data-quality-v0291-evaluation>Run an evaluation to see policy readiness.</div><h4>Reviewer decision</h4><div class="sc-quality0291-form"><label>Decision<select data-quality-v0291-decision><option value="no-decision">No decision</option><option value="approve">Approve</option><option value="conditional-approval">Conditional approval</option><option value="request-changes">Request changes</option><option value="reject">Reject</option><option value="deprecate">Deprecate</option></select></label><label class="is-wide">Rationale<textarea rows="4" data-quality-v0291-rationale></textarea></label></div><div class="sc-quality0291-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-quality-v0291-record-decision>Record decision</button><button type="button" class="sc-lab-button" data-quality-v0291-compare>Compare latest revisions</button><button type="button" class="sc-lab-button" data-quality-v0291-export>Export review bundle</button></div></section>
          <section class="sc-quality0291-card is-wide"><h4>Method-review registry</h4><div class="sc-quality0291-table-wrap"><table class="sc-quality0291-table"><thead><tr><th>Method</th><th>Risk</th><th>Benchmarks</th><th>Status</th><th>Score</th><th>Updated</th></tr></thead><tbody data-quality-v0291-rows></tbody></table></div></section>
          <section class="sc-quality0291-card is-wide"><h4>Selected review or comparison</h4><pre class="sc-quality0291-detail" data-quality-v0291-detail>No review selected.</pre></section>
        </div>
      </section>

      <section class="sc-lab-panel sc-lab-repro-v0282" data-lab-module="reproducible-runs" data-module-panel="reproducible-runs" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/REPRODUCIBILITY</span><h3>Reproducible Computational Runs</h3></div><span class="sc-lab-status-dot is-ready">Schema 0.28.2</span></div>
        <p>Freeze governed requests, outputs, environments, package versions, checksums, warnings, and failure histories into portable project records.</p>
        <div class="sc-repro0282-status" data-repro-v0282-status role="status" aria-live="polite">Preparing reproducible-run registry…</div>
        <div class="sc-repro0282-metrics" data-repro-v0282-metrics></div>
        <div class="sc-repro0282-grid">
          <section class="sc-repro0282-card"><h4>Freeze a project result</h4><div class="sc-repro0282-toolbar"><label>Completed record<select data-repro-v0282-source></select></label><label>Notes<textarea class="sc-repro0282-note" data-repro-v0282-notes placeholder="Method notes, assumptions, or limitations"></textarea></label></div><div class="sc-repro0282-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-repro-v0282-freeze>Freeze selected record</button><button type="button" class="sc-lab-button" data-repro-v0282-example>Run verified example</button></div></section>
          <section class="sc-repro0282-card"><h4>Compare runs</h4><div class="sc-repro0282-toolbar"><label>Absolute tolerance<input type="number" step="any" value="1e-9" data-repro-v0282-abs></label><label>Relative tolerance<input type="number" step="any" value="1e-7" data-repro-v0282-rel></label></div><div class="sc-repro0282-actions"><button type="button" class="sc-lab-button" data-repro-v0282-compare>Compare two selected runs</button><button type="button" class="sc-lab-button" data-repro-v0282-export>Export bundle</button><button type="button" class="sc-lab-button" data-repro-v0282-import>Import bundle</button><input type="file" accept="application/json" hidden data-repro-v0282-file></div></section>
          <section class="sc-repro0282-card"><h4>Run manifests</h4><div class="sc-repro0282-runs" data-repro-v0282-runs></div></section>
          <section class="sc-repro0282-card"><h4>Selected manifest or comparison</h4><pre class="sc-repro0282-detail" data-repro-v0282-detail>No run selected.</pre></section>
          <section class="sc-repro0282-card is-wide"><h4>Comparison history</h4><div class="sc-lab-table-wrap"><table class="sc-repro0282-table"><thead><tr><th>Left</th><th>Right</th><th>Status</th><th>Differences</th><th>Created</th></tr></thead><tbody data-repro-v0282-comparisons></tbody></table></div></section>
        </div>
      </section>

      <section class="sc-lab-panel sc-lab-dataset-registry-v0281" data-lab-module="dataset-registry" data-module-panel="dataset-registry" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/DATASET-REGISTRY</span><h3>Dataset Registry and Scientific Data Management</h3></div><span class="sc-lab-status-dot is-ready">Schema 0.28.1</span></div>
        <div class="sc-lab-method-note">Register scientific datasets with a data dictionary, units, variable roles, source and license metadata, validation state, profile statistics, and derived-dataset lineage. CSV, JSON, and GeoJSON are parsed in the browser; NetCDF is registered as metadata-only until governed binary parsing is enabled.</div>
        <div class="sc-ds0281-status" data-dataset-v0281-status role="status" aria-live="polite">Loading the dataset registry…</div>
        <div class="sc-ds0281-metrics" data-dataset-v0281-metrics></div>
        <div class="sc-ds0281-layout">
          <section class="sc-ds0281-card"><h4>Registered datasets</h4><div class="sc-ds0281-toolbar"><label>Search<input type="search" data-dataset-v0281-search placeholder="Dataset, source, or description"></label><label>Format<select data-dataset-v0281-filter-format><option value="">All formats</option><option value="csv">CSV</option><option value="json">JSON</option><option value="geojson">GeoJSON</option><option value="netcdf">NetCDF</option><option value="tabular">Tabular</option></select></label></div><div class="sc-ds0281-list" data-dataset-v0281-list></div></section>
          <section class="sc-ds0281-card"><h4>Register or import a dataset</h4><div class="sc-ds0281-form"><label>Title<input type="text" data-dataset-v0281-title placeholder="Dataset title"></label><label>Format<select data-dataset-v0281-format><option value="csv">CSV</option><option value="json">JSON records</option><option value="geojson">GeoJSON</option><option value="netcdf">NetCDF metadata</option></select></label><label class="is-wide">Description<textarea rows="3" data-dataset-v0281-description></textarea></label><label>Source name<input type="text" data-dataset-v0281-source></label><label>Source URL<input type="url" data-dataset-v0281-source-url></label><label class="is-wide">Citation<input type="text" data-dataset-v0281-citation></label><label>License<select data-dataset-v0281-license><option>Unknown</option><option>CC0-1.0</option><option>CC-BY-4.0</option><option>CC-BY-SA-4.0</option><option>ODC-PDDL-1.0</option><option>ODC-BY-1.0</option><option>US-Public-Domain</option><option>Proprietary</option><option>Other</option></select></label><label>License URL<input type="url" data-dataset-v0281-license-url></label><label class="is-wide">License terms<input type="text" data-dataset-v0281-license-terms></label><label>Derived from<select data-dataset-v0281-parent><option value="">No parent dataset</option></select></label><label>Upload<input type="file" data-dataset-v0281-file accept=".csv,.json,.geojson,.nc,.netcdf,application/json,text/csv"></label><label class="is-wide">Paste data<textarea data-dataset-v0281-input placeholder="Paste CSV, JSON records, or GeoJSON"></textarea></label></div><div class="sc-ds0281-actions"><button type="button" class="sc-lab-button" data-dataset-v0281-prepare>Parse and validate</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-dataset-v0281-register disabled>Register dataset</button></div></section>
          <section class="sc-ds0281-card is-wide"><h4>Prepared dataset and data dictionary</h4><div data-dataset-v0281-draft></div></section>
          <section class="sc-ds0281-card is-wide"><h4>Dataset metadata, profile, and lineage</h4><div data-dataset-v0281-details></div></section>
        </div>
      </section>

      <section class="sc-lab-panel sc-lab-discovery-v0292" data-lab-module="scholarly-discovery" data-module-panel="scholarly-discovery" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/DISCOVERY</span><h3>External Scholarly and Data Discovery</h3></div><span class="sc-lab-status-dot is-ready">Schema 0.29.2</span></div>
        <p>Search governed scholarly metadata providers, deduplicate records, inspect access signals, and import selected works into the project’s evidence and provenance source library.</p>
        <div class="sc-discovery0292-status" data-discovery-v0292-status role="status" aria-live="polite">Preparing discovery providers…</div>
        <div class="sc-discovery0292-provider-grid" data-discovery-v0292-providers></div>
        <div class="sc-discovery0292-metrics" data-discovery-v0292-metrics></div>
        <div class="sc-discovery0292-layout">
          <section class="sc-discovery0292-card"><h4>Scholarly search</h4><div class="sc-discovery0292-form"><label class="is-wide">Query<input type="search" data-discovery-v0292-query placeholder="Title, DOI, author, topic, dataset, or full citation"></label><div class="is-wide sc-discovery0292-providers"><label><input type="checkbox" value="crossref" data-discovery-provider checked> Crossref</label><label><input type="checkbox" value="datacite" data-discovery-provider checked> DataCite</label><label><input type="checkbox" value="openalex" data-discovery-provider> OpenAlex</label></div><label>From year<input type="number" min="1000" max="3000" data-discovery-v0292-yearFrom></label><label>Through year<input type="number" min="1000" max="3000" data-discovery-v0292-yearTo></label><label>Work type<input type="text" data-discovery-v0292-type placeholder="article, dataset, book…"></label><label>Results per provider<input type="number" min="1" max="25" value="10" data-discovery-v0292-limit></label><label class="is-wide"><span><input type="checkbox" data-discovery-v0292-dedupe checked> Deduplicate across providers</span></label></div><div class="sc-discovery0292-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-discovery-v0292-search>Search providers</button><button type="button" class="sc-lab-button" data-discovery-v0292-dedupeAction>Deduplicate again</button><button type="button" class="sc-lab-button" data-discovery-v0292-import>Import selected sources</button><button type="button" class="sc-lab-button" data-discovery-v0292-export>Export results</button></div></section>
          <section class="sc-discovery0292-card"><h4>Library profile and handoffs</h4><div class="sc-discovery0292-form"><label class="is-wide">Institution or library<input type="text" data-discovery-v0292-institution placeholder="Optional local library name"></label><label class="is-wide">OpenURL resolver base<input type="url" data-discovery-v0292-resolver placeholder="Stored locally; link generation only"></label><label class="is-wide">Notes<textarea rows="3" data-discovery-v0292-profileNotes placeholder="Access, ILL, or catalog notes"></textarea></label></div><div class="sc-discovery0292-actions"><button type="button" class="sc-lab-button" data-discovery-v0292-saveProfile>Save local profile</button><button type="button" class="sc-lab-button" data-discovery-v0292-worldcat>Search WorldCat</button><button type="button" class="sc-lab-button" data-discovery-v0292-scholar>Search Google Scholar</button></div><h4>Provider report</h4><ul class="sc-discovery0292-reports" data-discovery-v0292-reports></ul></section>
          <section class="sc-discovery0292-card is-wide"><h4>Deduplicated results</h4><div class="sc-discovery0292-results" data-discovery-v0292-results></div></section>
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
        <div class="sc-lab-toolbar"><label>Telescope<select data-space-telescope><option value="all">All</option><option value="JWST">JWST</option><option value="Hubble">Hubble</option><option value="Chandra">Chandra</option><option value="Spitzer">Spitzer</option></select></label><label>Target or topic<input type="search" value="nebula galaxy exoplanet" data-space-query></label><label>Limit<input type="number" min="1" max="30" value="18" data-space-limit></label><button class="sc-lab-button" data-space-dataset disabled>Dataset inspector</button></div><div class="sc-lab-observation-summary" data-space-summary>Preparing NASA observation query…</div>
        <div class="sc-lab-feed-grid" data-space-results><div class="sc-lab-data-note">The initial NASA query will run automatically.</div></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="marine-biology" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/MARINE</span><h3>Marine biodiversity observations</h3></div><button class="sc-lab-button sc-lab-button-primary" data-marine-load>Query OBIS</button></div>
        <div class="sc-lab-toolbar"><label>Scientific name or taxon<input type="search" value="Cetacea" data-marine-query></label><label>Limit<input type="number" min="1" max="30" value="25" data-marine-limit></label><button class="sc-lab-button" data-marine-dataset disabled>Dataset inspector</button></div><div class="sc-lab-observation-summary" data-marine-summary>Preparing OBIS biodiversity query…</div><div class="sc-lab-mini-chart" data-marine-chart></div>
        <div class="sc-lab-feed-grid" data-marine-results><div class="sc-lab-data-note">The initial OBIS query will run automatically.</div></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="dataset-inspector" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/DATA</span><h3>Scientific dataset inspector</h3></div><div class="sc-lab-inline-actions"><button class="sc-lab-button" data-dataset-save>Save dataset</button><button class="sc-lab-button" data-dataset-export>Export CSV</button></div></div>
        <div class="sc-lab-dataset-header" data-dataset-header>No dataset loaded. Open feed results, import CSV, or select a saved project dataset.</div>
        <div class="sc-lab-toolbar"><label>Saved dataset<select data-dataset-select><option value="">Current working dataset</option></select></label><label>Filter rows<input type="search" data-dataset-filter placeholder="Search any field"></label><label>X variable<select data-dataset-x></select></label><label>Y variable<select data-dataset-y></select></label><label>Rows<select data-dataset-limit><option>25</option><option selected>100</option><option>250</option></select></label></div>
        <details class="sc-lab-data-import"><summary>Import CSV or JSON</summary><textarea rows="8" data-dataset-import placeholder="Paste CSV or a JSON array of records"></textarea><button class="sc-lab-button sc-lab-button-primary" data-dataset-import-run>Import data</button></details>
        <details class="sc-dt0550" data-data-transform-v0550>
          <summary>Scientific data transformation &amp; derived variables</summary>
          <div class="sc-dt0550__body">
            <div class="sc-dt0550__head"><div><span class="sc-lab-section-code">DATA / PREPARATION / v0.55.0</span><h4>Reproducible scientific transformation pipeline</h4><p>Transform the current working dataset through a bounded, reviewable plan. Derived variables use Lab's safe equation grammar; unit conversions use a governed compatibility catalog; every operation produces reproducible lineage hashes.</p></div><span class="sc-dt0550__contract">TRANSFORM 0.55.0</span></div>
            <p class="sc-dt0550__status" data-dt-v0550-status role="status" aria-live="polite">Scientific data transformation ready. Load a dataset above, then define or load a transformation plan.</p>
            <div class="sc-dt0550__grid">
              <section class="sc-dt0550__card"><h4>Transformation plan</h4><label>Plan title<input data-dt-v0550-title value="Scientific data transformation"></label><label>Operations as JSON<textarea data-dt-v0550-plan spellcheck="false">[
  {"type":"derive","name":"derived_value","expression":"x * 2","unit":""}
]</textarea></label><label>Scientific notes / assumptions<textarea data-dt-v0550-notes></textarea></label><div class="sc-dt0550__actions"><button type="button" class="sc-lab-button" data-dt-v0550-example>Load illustrative dataset &amp; plan</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-dt-v0550-run>Run transformation</button></div><p class="sc-dt0550__note">Supported operations: derive, filter, rename, select, drop, scale, unit-convert, cast, and explicit imputation. No arbitrary code or automatic feature engineering.</p></section>
              <section class="sc-dt0550__card"><h4>Governed dataset join</h4><div class="sc-dt0550__grid"><label>Left key<input data-dt-v0550-join-left-key placeholder="id"></label><label>Right key<input data-dt-v0550-join-right-key placeholder="id"></label><label>Join mode<select data-dt-v0550-join-how><option value="left">Left</option><option value="inner">Inner</option></select></label><label>Collision suffix<input data-dt-v0550-join-suffix value="_right"></label></div><label>Right-side rows as JSON<textarea data-dt-v0550-join-right spellcheck="false">[]</textarea></label><div class="sc-dt0550__actions"><button type="button" class="sc-lab-button" data-dt-v0550-join>Join into working dataset</button></div><details><summary>Join record</summary><pre data-dt-v0550-join-record>No v0.55 join yet.</pre></details></section>
              <section class="sc-dt0550__card is-wide"><h4>Transformation evidence</h4><div class="sc-dt0550__summary" data-dt-v0550-summary></div><div data-dt-v0550-lineage><div class="sc-lab-data-note">Run a transformation to generate lineage.</div></div><div class="sc-dt0550__actions"><button type="button" class="sc-lab-button" data-dt-v0550-use>Use transformed dataset</button><button type="button" class="sc-lab-button" data-dt-v0550-save>Save derived dataset + lineage</button></div></section>
              <section class="sc-dt0550__card"><h4>Transformed data preview</h4><div data-dt-v0550-preview><div class="sc-lab-data-note">No transformation result yet.</div></div></section>
              <section class="sc-dt0550__card"><h4>Derived-variable figure</h4><label>Numeric transformed variable<select data-dt-v0550-graph-column></select></label><div class="sc-dt0550__actions"><button type="button" class="sc-lab-button" data-dt-v0550-graph>Render figure</button><button type="button" class="sc-lab-button" data-dt-v0550-graph-studio>Open in Graph Studio</button></div><div class="sc-dt0550__canvas" data-dt-v0550-canvas><div class="sc-lab-data-note">Render a transformed variable to create a scientific figure.</div></div></section>
              <section class="sc-dt0550__card is-wide"><details><summary>Transformation record</summary><pre data-dt-v0550-record>No v0.55 transformation yet.</pre></details></section>
            </div>
          </div>
        </details>
        <div class="sc-lab-dataset-stats" data-dataset-stats></div>
        <div class="sc-lab-grid sc-lab-grid-2"><section><h4>Data table</h4><div data-dataset-table></div></section><section><h4>Variable plot</h4><div class="sc-lab-chart" data-dataset-chart></div></section></div>
      </section>


      <section class="sc-lab-panel sc-lab-numerical-v0270" data-lab-module="numerical-methods" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/NUMERICS</span><h3>Scientific Computing and Numerical Methods</h3></div>
          <span class="sc-lab-status-dot is-ready">Python Compute Core</span>
        </div>
        <div class="sc-lab-method-note">Run governed numerical methods through the Sustainable Catalyst Python Compute Core. Methods are registered, schema-constrained, resource-bounded, and returned with reproducibility provenance. Public arbitrary-code execution is not enabled.</div>
        <div class="sc-num-status" data-numerical-status role="status" aria-live="polite" data-tone="loading">Loading the numerical-method registry…</div>
        <div class="sc-num-grid">
          <section class="sc-num-card" aria-labelledby="sc-num-method-heading">
            <h4 id="sc-num-method-heading" data-numerical-method-title>Numerical method</h4>
            <div class="sc-num-meta"><code data-numerical-method-id>Registry loading</code><span>Packages: <strong data-numerical-packages>—</strong></span><span>Cost: <strong data-numerical-cost>—</strong></span></div>
            <p data-numerical-description>Choose a governed scientific method.</p>
            <ul data-numerical-assumptions><li>Method assumptions will appear here.</li></ul>
            <div class="sc-num-fields">
              <label class="is-wide">Method<select data-numerical-method aria-describedby="sc-num-method-heading"></select></label>
              <label>Execution<select data-numerical-execution><option value="automatic">Automatic</option><option value="synchronous">Immediate</option><option value="queued">Persistent queue</option></select></label>
              <label>Random seed<input data-numerical-seed type="number" step="1" value="42"></label>
              <label class="is-wide">Inputs JSON<textarea data-numerical-inputs spellcheck="false">{}</textarea></label>
              <label class="is-wide">Parameters JSON<textarea data-numerical-parameters spellcheck="false">{}</textarea></label>
            </div>
            <div class="sc-num-actions">
              <button type="button" class="sc-lab-button" data-numerical-example>Load governed example</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-numerical-run>Run method</button>
              <button type="button" class="sc-lab-button" data-numerical-cancel disabled>Cancel queued job</button>
            </div>
          </section>
          <section class="sc-num-card sc-num-result" aria-labelledby="sc-num-result-heading">
            <h4 id="sc-num-result-heading">Result and provenance</h4>
            <div class="sc-num-summary" data-numerical-summary><strong>No method has run.</strong><span>Choose a method and run the governed example.</span></div>
            <div data-numerical-plot><div class="sc-lab-data-note">A supported line-series output will render here.</div></div>
            <h5>Numerical output</h5><pre data-numerical-output>No output.</pre>
            <div class="sc-num-actions"><button type="button" class="sc-lab-button" data-numerical-save disabled>Save to project</button><button type="button" class="sc-lab-button" data-numerical-export disabled>Export result JSON</button></div>
            <details><summary>Execution provenance</summary><pre data-numerical-provenance>No provenance.</pre></details>
            <details><summary>Raw compute response</summary><pre data-numerical-raw>No response.</pre></details>
          </section>
        </div>
      </section>

      <section class="sc-lab-panel sc-lab-benchmark-v0271" data-lab-module="numerical-validation" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/VALIDATION</span><h3>Numerical Validation and Benchmark Library</h3></div>
          <span class="sc-lab-status-dot is-ready">Known-answer fixtures</span>
        </div>
        <div class="sc-lab-method-note">Validate governed Python numerical methods against analytic solutions, reference fixtures, tolerance rules, unit assertions, residual checks, deterministic seeds, and convergence series. Browser references are independent lightweight checks and do not replace the Python benchmark result.</div>
        <div data-benchmark-status role="status" aria-live="polite" data-tone="loading">Loading the benchmark library…</div>
        <div class="sc-benchmark-layout">
          <section class="sc-benchmark-card" aria-labelledby="sc-benchmark-current-title">
            <h4 id="sc-benchmark-current-title" data-benchmark-title>Numerical benchmark</h4>
            <p><code data-benchmark-id>Catalog loading</code></p>
            <p data-benchmark-description>Choose a known-answer fixture.</p>
            <p><strong>Tags:</strong> <span data-benchmark-tags>—</span></p>
            <label>Benchmark<select data-benchmark-select></select></label>
            <h5>Acceptance assertions</h5>
            <ul data-benchmark-assertions><li>Assertions will appear here.</li></ul>
            <div class="sc-benchmark-actions">
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-benchmark-run>Run selected benchmark</button>
              <button type="button" class="sc-lab-button" data-benchmark-convergence disabled>Run convergence series</button>
              <button type="button" class="sc-lab-button" data-benchmark-run-all>Run all benchmarks</button>
              <button type="button" class="sc-lab-button" data-benchmark-export disabled>Export report JSON</button>
            </div>
            <details><summary>Independent browser reference</summary><pre data-benchmark-browser-reference>No reference loaded.</pre></details>
          </section>
          <section class="sc-benchmark-card" aria-labelledby="sc-benchmark-result-title">
            <h4 id="sc-benchmark-result-title">Validation result</h4>
            <div data-benchmark-summary><strong>No benchmark has run.</strong></div>
            <div class="sc-benchmark-table-wrap"><table><thead><tr><th>Status</th><th>Output</th><th>Rule</th><th>Expected</th><th>Actual</th><th>Unit</th></tr></thead><tbody data-benchmark-assertion-results><tr><td colspan="6">No assertion results.</td></tr></tbody></table></div>
            <details open><summary>Python output</summary><pre data-benchmark-python-output>No output.</pre></details>
            <details><summary>Execution provenance</summary><pre data-benchmark-provenance>No provenance.</pre></details>
          </section>
        </div>
        <section class="sc-benchmark-card">
          <h4>Full benchmark suite</h4>
          <p data-benchmark-suite-summary>No suite has run.</p>
          <div class="sc-benchmark-table-wrap"><table><thead><tr><th>Status</th><th>Benchmark</th><th>Method</th><th>Runtime</th><th>Error</th></tr></thead><tbody data-benchmark-suite-results><tr><td colspan="5">No suite results.</td></tr></tbody></table></div>
        </section>
        <section class="sc-benchmark-card">
          <h4>Convergence diagnostics</h4>
          <p data-benchmark-convergence-summary>Select a benchmark with a convergence series.</p>
          <div class="sc-benchmark-table-wrap"><table><thead><tr><th>Level</th><th>Parameters</th><th>Actual</th><th>Absolute error</th><th>Runtime</th></tr></thead><tbody data-benchmark-convergence-results><tr><td colspan="5">No convergence series.</td></tr></tbody></table></div>
        </section>
      </section>


      <section class="sc-lab-panel sc-lab-governance-v0273" data-lab-module="numerical-governance" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/GOVERNANCE</span><h3>Numerical Precision and Solver Governance</h3></div><span class="sc-lab-status-dot is-ready">Governed solvers</span></div>
        <div class="sc-lab-method-note">Choose a precision profile, request or accept a registered solver, validate units, inspect condition and convergence diagnostics, and compare selected results with an independent reference method. The backend continues to reject arbitrary code and unregistered solvers.</div>
        <div data-governance-status role="status" aria-live="polite" data-tone="loading">Loading solver-governance policies…</div>
        <div class="sc-governance-layout">
          <section class="sc-governance-card"><h4 data-governance-title>Governed method</h4><p><code data-governance-id>Loading registry</code></p><p data-governance-description></p><p><strong>Profiles:</strong> <span data-governance-supported>—</span></p>
            <div class="sc-governance-fields">
              <label class="wide">Method<select data-governance-method></select></label><label>Precision profile<select data-governance-profile><option value="fast">Fast exploratory</option><option value="balanced" selected>Balanced scientific</option><option value="strict">Strict validation</option><option value="diagnostic">Diagnostic comparison</option></select></label><label>Solver policy<select data-governance-policy><option value="automatic">Automatic</option><option value="recommended">Recommended</option><option value="manual">Manual registered solver</option></select></label>
              <label>Requested solver<input data-governance-solver placeholder="Leave blank for automatic"></label><label>Unit policy<select data-governance-unit-policy><option value="off">Off</option><option value="warn" selected>Warn</option><option value="strict">Strict</option></select></label><label>Ill-conditioned systems<select data-governance-ill-policy><option value="least-squares" selected>Use least-squares fallback</option><option value="warn">Warn and continue</option><option value="reject">Reject</option></select></label><label>Condition threshold<input data-governance-condition type="number" value="1e12" step="any"></label>
              <label>Absolute tolerance<input data-governance-absolute type="number" value="1e-9" step="any"></label><label>Relative tolerance<input data-governance-relative type="number" value="1e-8" step="any"></label><label>Uncertainty standard<select data-governance-uncertainty><option>method-default</option><option>GUM-inspired</option><option>Monte-Carlo</option><option>bootstrap</option></select></label><label>Random seed<input data-governance-seed type="number" value="42"></label>
              <label class="wide"><input data-governance-reference type="checkbox"> Run independent reference-method comparison</label><label class="wide">Inputs JSON<textarea data-governance-inputs>{}</textarea></label><label class="wide">Parameters JSON<textarea data-governance-parameters>{}</textarea></label><label class="wide">Units JSON<textarea data-governance-units>{}</textarea></label>
            </div><div class="sc-governance-actions"><button class="sc-lab-button" data-governance-example>Load example</button><button class="sc-lab-button" data-governance-recommend>Recommend solver</button><button class="sc-lab-button sc-lab-button-primary" data-governance-run>Run governed method</button><button class="sc-lab-button" data-governance-compare>Run comparison</button></div>
          </section>
          <section class="sc-governance-card"><h4>Governance result</h4><div class="sc-governance-recommendation" data-governance-recommendation><strong>No recommendation yet.</strong></div><div class="sc-governance-summary" data-governance-summary><strong>No governed run yet.</strong></div><h5>Floating-point precision</h5><pre data-governance-precision-output>No precision report.</pre><h5>Unit validation</h5><pre data-governance-unit-output>No unit report.</pre><h5>Convergence and conditioning</h5><pre data-governance-diagnostics-output>No diagnostics.</pre><h5>Reference comparison</h5><pre data-governance-comparison-output>No comparison.</pre><details><summary>Numerical output</summary><pre data-governance-result-output>No output.</pre></details><details><summary>Provenance</summary><pre data-governance-provenance>No provenance.</pre></details><button class="sc-lab-button" data-governance-export disabled>Export governance report</button></section>
        </div>
      </section>


      <section class="sc-lab-panel sc-lab-visual-v0274" data-lab-module="numerical-visualization" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/COMPUTE/VISUALIZE</span><h3>Scientific Visualization for Numerical Results</h3></div><span class="sc-lab-status-dot is-ready">Accessible exports</span></div>
        <div class="sc-lab-method-note">Run a governed numerical method or paste a compatible result, then generate a server-normalized visualization specification with an accessible SVG, tabular fallback, and SVG, PNG, CSV, and JSON exports. Arbitrary plotting code is not executed.</div>
        <div data-visual-status role="status" aria-live="polite" data-tone="loading">Loading visualization profiles…</div>
        <div class="sc-visual-layout">
          <section class="sc-visual-card"><div class="sc-visual-method-summary" data-visual-method-summary><strong>Loading methods…</strong></div><div class="sc-visual-fields">
            <label class="wide">Numerical method<select data-visual-method></select></label><label>Visualization type<select data-visual-type><option value="auto">Automatic</option></select></label><label>Measure<select data-visual-measure><option value="amplitude">Amplitude / derivative</option><option value="power">Power spectrum</option><option value="elasticity">Elasticity</option></select></label>
            <label>Precision profile<select data-visual-profile><option value="fast">Fast</option><option value="balanced" selected>Balanced</option><option value="strict">Strict</option><option value="diagnostic">Diagnostic</option></select></label><label>Random seed<input data-visual-seed type="number" value="42"></label><label>Maximum plotted points<input data-visual-max-points type="number" min="50" max="2000" value="1200"></label>
            <label class="wide">Title<input data-visual-title value="Scientific visualization"></label><label class="wide">Accessible description<textarea data-visual-description>Governed scientific visualization of the selected numerical result.</textarea></label><label>X-axis label<input data-visual-x-label></label><label>Y-axis label<input data-visual-y-label></label><label>Z-value label<input data-visual-z-label></label>
            <label class="wide">Inputs JSON<textarea data-visual-inputs>{}</textarea></label><label class="wide">Parameters JSON<textarea data-visual-parameters>{}</textarea></label><label class="wide">Units JSON<textarea data-visual-units>{}</textarea></label><label class="wide">Result outputs JSON<textarea data-visual-outputs>{}</textarea></label>
          </div><div class="sc-visual-actions"><button class="sc-lab-button" data-visual-example>Load method example</button><button class="sc-lab-button" data-visual-heatmap-example>Load heatmap example</button><button class="sc-lab-button sc-lab-button-primary" data-visual-run>Run & visualize</button><button class="sc-lab-button" data-visual-generate>Visualize pasted result</button></div></section>
          <section class="sc-visual-card"><div class="sc-visual-canvas" data-visual-canvas><div class="sc-lab-data-note">Run a method or paste result outputs to render a visualization.</div></div><div class="sc-visual-actions"><button class="sc-lab-button" data-visual-svg disabled>Export SVG</button><button class="sc-lab-button" data-visual-png disabled>Export PNG</button><button class="sc-lab-button" data-visual-csv disabled>Export CSV</button><button class="sc-lab-button" data-visual-json disabled>Export JSON</button><button class="sc-lab-button" data-visual-save disabled>Save to project</button></div><div class="sc-visual-table" data-visual-table></div><details><summary>Visualization specification</summary><pre data-visual-spec>No specification.</pre></details><textarea data-visual-svg-output hidden></textarea></section>
        </div>
      </section>

      <section class="sc-lab-panel sc-lab-long-jobs-v0272" data-lab-module="long-running-jobs" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/COMPUTE/JOBS</span><h3>Long-Running Numerical Jobs and Checkpoint Recovery</h3></div>
          <span class="sc-lab-status-dot is-ready">Persistent queue</span>
        </div>
        <div class="sc-lab-method-note">Run larger numerical studies through the governed Python Compute Core. Checkpoint-capable methods can be paused, resumed after interruption, inspected before completion, prioritized, and reused from the result cache.</div>
        <div data-longjobs-status role="status" aria-live="polite" data-state="loading">Loading compute queue…</div>
        <div class="sc-lab-toolbar">
          <label>Example job<select data-longjobs-example><option value="sweep">1,000-point logistic parameter sweep</option><option value="bootstrap">20,000-resample bootstrap interval</option></select></label>
          <label>Priority<input type="number" min="0" max="100" step="10" value="50" data-longjobs-priority></label>
          <label>Cache policy<select data-longjobs-cache><option value="use">Use cached result</option><option value="refresh">Refresh cache</option><option value="bypass">Bypass cache</option></select></label>
          <button type="button" class="sc-lab-button sc-lab-button-primary" data-longjobs-submit>Submit checkpointed job</button>
          <button type="button" class="sc-lab-button" data-longjobs-refresh>Refresh</button>
          <button type="button" class="sc-lab-button" data-longjobs-purge>Purge result cache</button>
        </div>
        <div class="sc-longjobs-metrics" data-longjobs-metrics></div>
        <div class="sc-longjobs-grid">
          <section class="sc-longjobs-card" aria-labelledby="sc-longjobs-list-title"><h4 id="sc-longjobs-list-title">Project compute jobs</h4><div class="sc-longjobs-list" data-longjobs-list><div class="sc-lab-data-note">Loading jobs…</div></div></section>
          <section class="sc-longjobs-card" aria-labelledby="sc-longjobs-detail-title"><h4 id="sc-longjobs-detail-title">Job recovery and partial results</h4><div data-longjobs-detail><div class="sc-lab-data-note">Select a job to inspect checkpoints.</div></div></section>
        </div>
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


      <section class="sc-lab-panel" data-lab-module="materials" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/MATERIALS</span><h3>Materials science and characterization laboratory</h3></div>
          <div class="sc-lab-panel-actions"><button type="button" class="sc-lab-button" data-materials-experiment>Create characterization study</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-materials-run-benchmarks>Run validation suite</button></div>
        </div>
        <div class="sc-lab-method-note">Materials analyses preserve specimen identity, processing history, geometry, units, instrument assumptions, derived properties, validation warnings, project links, and notebook-ready records. Screening equations do not replace calibrated mechanical testing, instrument corrections, microscopy quality control, or assessed thermodynamic data.</div>
        <div class="sc-lab-tabs sc-lab-tabs-wrap sc-lab-materials-tabs">
          <button type="button" class="is-active" data-materials-tab="mechanical">Mechanical</button>
          <button type="button" data-materials-tab="thermal">Thermal</button>
          <button type="button" data-materials-tab="electrical">Electrical</button>
          <button type="button" data-materials-tab="magnetic">Magnetic</button>
          <button type="button" data-materials-tab="optical">Optical</button>
          <button type="button" data-materials-tab="crystallography">Crystallography &amp; XRD</button>
          <button type="button" data-materials-tab="phase">Phase &amp; diffusion</button>
          <button type="button" data-materials-tab="corrosion">Corrosion</button>
          <button type="button" data-materials-tab="polymers">Polymers</button>
          <button type="button" data-materials-tab="composites">Composites</button>
          <button type="button" data-materials-tab="microscopy">Microscopy</button>
          <button type="button" data-materials-tab="validation">Validation</button>
        </div>
        <div data-materials-pane="mechanical"><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="mechanical"></div></div>
        <div data-materials-pane="thermal" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="thermal"></div></div>
        <div data-materials-pane="electrical" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="electrical"></div></div>
        <div data-materials-pane="magnetic" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="magnetic"></div></div>
        <div data-materials-pane="optical" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="optical"></div></div>
        <div data-materials-pane="crystallography" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="crystallography"></div></div>
        <div data-materials-pane="phase" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="phase"></div></div>
        <div data-materials-pane="corrosion" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="corrosion"></div></div>
        <div data-materials-pane="polymers" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="polymers"></div></div>
        <div data-materials-pane="composites" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="composites"></div></div>
        <div data-materials-pane="microscopy" hidden><div class="sc-lab-grid sc-lab-grid-2" data-materials-tool-grid="microscopy"></div></div>
        <div data-materials-pane="validation" hidden>
          <article class="sc-lab-tool sc-lab-tool-wide sc-lab-materials-validation-dashboard">
            <h4>Materials numerical validation suite</h4>
            <p>Reference cases cover mechanics, thermal transport, electrical resistivity, optical reflectance, diffraction, phase fractions, corrosion, composites, and microscopy resolution.</p>
            <div data-materials-benchmark-table class="sc-lab-data-note">Run the validation suite to compare the materials engine with deterministic reference cases.</div>
            <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-materials-save-benchmarks>Save validation report</button></div>
          </article>
          <article class="sc-lab-tool sc-lab-tool-wide">
            <h4>Materials characterization templates</h4>
            <div class="sc-lab-template-list"><span>Tensile stress–strain study</span><span>Fracture and fatigue screening</span><span>Thermal conductivity and diffusivity</span><span>Four-point electrical resistivity</span><span>Hall-effect carrier analysis</span><span>XRD phase and crystallite analysis</span><span>DSC transition and crystallinity study</span><span>Corrosion weight-loss exposure</span><span>Composite modulus comparison</span><span>Microscopy particle and grain statistics</span></div>
          </article>
        </div>
      </section>


      <section class="sc-lab-panel" data-lab-module="earth-systems" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/EARTH-SYSTEMS</span><h3>Earth, climate, ocean, and marine systems laboratory</h3></div>
          <div class="sc-lab-panel-actions"><button type="button" class="sc-lab-button" data-earth-experiment>Create Earth systems study</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-earth-run-benchmarks>Run validation suite</button></div>
        </div>
        <div class="sc-lab-method-note">Earth systems analyses preserve spatial and temporal scope, units, model assumptions, source context, validation warnings, project links, and notebook-ready records. Screening equations do not replace calibrated field observations, authoritative climate products, TEOS-10 ocean calculations, geotechnical assessment, hydrodynamic models, or reviewed hazard analysis.</div>
        <div class="sc-lab-tabs sc-lab-tabs-wrap sc-lab-earth-tabs">
          <button type="button" class="is-active" data-earth-tab="solid-earth">Solid Earth</button>
          <button type="button" data-earth-tab="atmosphere">Atmosphere</button>
          <button type="button" data-earth-tab="climate">Climate</button>
          <button type="button" data-earth-tab="hydrology">Hydrology</button>
          <button type="button" data-earth-tab="ocean">Ocean</button>
          <button type="button" data-earth-tab="marine">Marine systems</button>
          <button type="button" data-earth-tab="remote">Remote sensing</button>
          <button type="button" data-earth-tab="hazards">Hazards</button>
          <button type="button" data-earth-tab="carbon">Carbon cycle</button>
          <button type="button" data-earth-tab="validation">Validation</button>
        </div>
        <div data-earth-pane="solid-earth"><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="solid-earth"></div></div>
        <div data-earth-pane="atmosphere" hidden><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="atmosphere"></div></div>
        <div data-earth-pane="climate" hidden><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="climate"></div></div>
        <div data-earth-pane="hydrology" hidden><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="hydrology"></div></div>
        <div data-earth-pane="ocean" hidden><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="ocean"></div></div>
        <div data-earth-pane="marine" hidden><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="marine"></div></div>
        <div data-earth-pane="remote" hidden><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="remote"></div></div>
        <div data-earth-pane="hazards" hidden><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="hazards"></div></div>
        <div data-earth-pane="carbon" hidden><div class="sc-lab-grid sc-lab-grid-2" data-earth-tool-grid="carbon"></div></div>
        <div data-earth-pane="validation" hidden>
          <article class="sc-lab-tool sc-lab-tool-wide sc-lab-earth-validation-dashboard">
            <h4>Earth systems numerical validation suite</h4>
            <p>Reference cases cover plate motion, seismic moment, atmospheric humidity, CO₂ forcing, catchment runoff, ocean waves, tsunami travel, marine diversity, remote-sensing indices, hazard recurrence, atmospheric carbon, and soil carbon.</p>
            <div data-earth-benchmark-table class="sc-lab-data-note">Run the validation suite to compare the Earth systems engine with deterministic reference cases.</div>
            <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-earth-save-benchmarks>Save validation report</button></div>
          </article>
          <article class="sc-lab-tool sc-lab-tool-wide">
            <h4>Earth systems investigation templates</h4>
            <div class="sc-lab-template-list"><span>Plate motion and seismic source study</span><span>Atmospheric profile and moisture analysis</span><span>Climate anomaly and trend assessment</span><span>Catchment water-balance study</span><span>Groundwater flow and storage</span><span>Wave, current, and mixed-layer analysis</span><span>Marine biodiversity and trophic transfer</span><span>Remote-sensing index validation</span><span>Flood, landslide, ash, and coastal-hazard screening</span><span>Carbon stock and sequestration accounting</span></div>
          </article>
        </div>
      </section>


      <section class="sc-lab-panel" data-lab-module="energy-engineering" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/ENERGY-ENGINEERING</span><h3>Energy and engineering laboratory</h3></div>
          <div class="sc-lab-panel-actions"><button type="button" class="sc-lab-button" data-energy-experiment>Create energy systems study</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-energy-run-benchmarks>Run validation suite</button></div>
        </div>
        <div class="sc-lab-method-note">Energy and engineering analyses preserve system boundaries, units, conversion chains, efficiencies, operating conditions, emissions factors, economic assumptions, reliability assumptions, validation warnings, project links, and notebook-ready records. Screening equations do not replace detailed electrical studies, equipment certification, dispatch simulation, process design, safety engineering, utility interconnection studies, or licensed professional review.</div>
        <div class="sc-lab-tabs sc-lab-tabs-wrap sc-lab-energy-tabs">
          <button type="button" class="is-active" data-energy-tab="balances">Balances</button>
          <button type="button" data-energy-tab="solar">Solar</button>
          <button type="button" data-energy-tab="wind">Wind</button>
          <button type="button" data-energy-tab="hydro">Hydro</button>
          <button type="button" data-energy-tab="storage">Storage</button>
          <button type="button" data-energy-tab="grid">Power &amp; grid</button>
          <button type="button" data-energy-tab="thermal">Thermal systems</button>
          <button type="button" data-energy-tab="fuels">Fuels &amp; hydrogen</button>
          <button type="button" data-energy-tab="emissions">Emissions</button>
          <button type="button" data-energy-tab="economics">Techno-economics</button>
          <button type="button" data-energy-tab="reliability">Reliability</button>
          <button type="button" data-energy-tab="validation">Validation</button>
        </div>
        <div data-energy-pane="balances"><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="balances"></div></div>
        <div data-energy-pane="solar" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="solar"></div></div>
        <div data-energy-pane="wind" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="wind"></div></div>
        <div data-energy-pane="hydro" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="hydro"></div></div>
        <div data-energy-pane="storage" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="storage"></div></div>
        <div data-energy-pane="grid" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="grid"></div></div>
        <div data-energy-pane="thermal" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="thermal"></div></div>
        <div data-energy-pane="fuels" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="fuels"></div></div>
        <div data-energy-pane="emissions" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="emissions"></div></div>
        <div data-energy-pane="economics" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="economics"></div></div>
        <div data-energy-pane="reliability" hidden><div class="sc-lab-grid sc-lab-grid-2" data-energy-tool-grid="reliability"></div></div>
        <div data-energy-pane="validation" hidden>
          <article class="sc-lab-tool sc-lab-tool-wide sc-lab-energy-validation-dashboard">
            <h4>Energy and engineering numerical validation suite</h4>
            <p>Reference cases cover energy closure, solar, wind, hydro, storage, three-phase power, thermal conduction, hydrogen production, discounted cash flow, levelized cost, component reliability, and expected energy not served.</p>
            <div data-energy-benchmark-table class="sc-lab-data-note">Run the validation suite to compare the energy engine with deterministic reference cases.</div>
            <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-energy-save-benchmarks>Save validation report</button></div>
          </article>
          <article class="sc-lab-tool sc-lab-tool-wide">
            <h4>Energy and engineering study templates</h4>
            <div class="sc-lab-template-list"><span>Facility energy balance and intensity</span><span>Solar resource and PV sizing</span><span>Wind resource and turbine performance</span><span>Hydropower and pumped storage</span><span>Battery autonomy and degradation</span><span>Grid losses and power-factor correction</span><span>Thermal system and heat-exchanger analysis</span><span>Hydrogen production and conversion</span><span>Lifecycle emissions and carbon payback</span><span>LCOE, LCOS, NPV, and IRR comparison</span><span>N−1 and loss-of-load reliability study</span></div>
          </article>
        </div>
      </section>


        <section class="sc-lab-panel" data-lab-module="electrical-embedded" hidden data-module-panel="electrical-embedded">
    <div class="sc-lab-panel-head">
      <div><span class="sc-lab-section-code">LAB/ELECTRICAL-EMBEDDED</span><h3>Electrical, electronics, and embedded systems</h3></div>
      <div class="sc-lab-panel-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-electrical-run-benchmarks>Run validation suite</button></div>
    </div>
    <div class="sc-lab-electrical-boundary"><strong>Engineering boundary.</strong> These are auditable screening and education tools. Verify datasheets, tolerances, parasitics, layout, grounding, thermal limits, electrical codes, certification requirements, and physical measurements. Never connect an unverified design to mains voltage, high-energy batteries, medical equipment, vehicles, industrial machinery, or safety-critical systems.</div>
    <div class="sc-lab-electrical-tabs" role="tablist" aria-label="Electrical laboratory work areas">
      <button type="button" class="sc-lab-button is-active" data-electrical-tab="dc">DC circuits</button>
      <button type="button" class="sc-lab-button" data-electrical-tab="ac">AC systems</button>
      <button type="button" class="sc-lab-button" data-electrical-tab="analog">Analog electronics</button>
      <button type="button" class="sc-lab-button" data-electrical-tab="digital">Digital logic</button>
      <button type="button" class="sc-lab-button" data-electrical-tab="embedded">Embedded systems</button>
      <button type="button" class="sc-lab-button" data-electrical-tab="power">Power & thermal</button>
      <button type="button" class="sc-lab-button" data-electrical-tab="signals">Signals</button>
      <button type="button" class="sc-lab-button" data-electrical-tab="devices">Devices & firmware</button>
    </div>
    <div data-electrical-pane="dc"><div class="sc-lab-electrical-tool-grid" data-electrical-grid="dc"></div></div>
    <div data-electrical-pane="ac" hidden><div class="sc-lab-electrical-tool-grid" data-electrical-grid="ac"></div></div>
    <div data-electrical-pane="analog" hidden><div class="sc-lab-electrical-tool-grid" data-electrical-grid="analog"></div></div>
    <div data-electrical-pane="digital" hidden><div class="sc-lab-electrical-tool-grid" data-electrical-grid="digital"></div></div>
    <div data-electrical-pane="embedded" hidden><div class="sc-lab-electrical-tool-grid" data-electrical-grid="embedded"></div></div>
    <div data-electrical-pane="power" hidden><div class="sc-lab-electrical-tool-grid" data-electrical-grid="power"></div></div>
    <div data-electrical-pane="signals" hidden><div class="sc-lab-electrical-tool-grid" data-electrical-grid="signals"></div></div>
    <div data-electrical-pane="devices" hidden>
      <div class="sc-lab-electrical-device-grid">
        <article class="sc-lab-tool"><h4>Embedded device profile</h4><div class="sc-lab-inline-fields"><label><span>Profile name</span><input data-electrical-device-name value="Environmental sensor node"></label><label><span>Board</span><select data-electrical-board></select></label><label><span>Supply voltage</span><input type="number" step="any" data-electrical-device-voltage value="3.3"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-electrical-create-device>Create profile</button><button type="button" class="sc-lab-button" data-electrical-save-device>Save profile</button></div><pre class="sc-lab-electrical-console" data-electrical-device-output></pre></article>
        <article class="sc-lab-tool"><h4>Logic-level interface validation</h4><div class="sc-lab-inline-fields"><label><span>Source voltage</span><input type="number" step="any" data-interface-source-voltage value="3.3"></label><label><span>Target voltage</span><input type="number" step="any" data-interface-target-voltage value="3.3"></label></div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-electrical-validate-interface>Validate interface</button><button type="button" class="sc-lab-button" data-electrical-save-interface>Save validation</button></div><pre class="sc-lab-electrical-console" data-electrical-interface-output></pre></article>
        <article class="sc-lab-tool"><h4>Firmware starter artifacts</h4><label><span>Template</span><select data-electrical-firmware-template><option value="arduino-cpp">Arduino C++</option><option value="micropython">MicroPython</option><option value="rust-embedded">Rust embedded</option><option value="linux-python">Linux / Python</option></select></label><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-electrical-save-firmware>Save firmware artifact</button></div><pre class="sc-lab-electrical-console" data-electrical-firmware-output>#include &lt;Arduino.h&gt;
// Select a template to inspect starter source.</pre></article>
      </div>
    </div>
    <article class="sc-lab-tool"><h4>Validation suite output</h4><pre class="sc-lab-electrical-console" data-electrical-benchmark-output>Run the deterministic benchmark suite to create a hardware-validation record.</pre></article>

  <div data-electrical-embedded-root></div>
</section>

    <section class="sc-lab-panel" data-lab-module="mechanical-thermal" hidden data-module-panel="mechanical-thermal">
    <div class="sc-lab-panel-head">
      <div><span class="sc-lab-section-code">LAB/MECHANICAL-THERMAL</span><h3>Mechanical and thermal engineering</h3></div>
      <div class="sc-lab-panel-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-mt-bench>Run validation suite</button></div>
    </div>
    <div class="sc-lab-electrical-boundary"><strong>Engineering boundary.</strong> These methods support transparent calculations and preliminary screening. Verify geometry, material data, load cases, fatigue, fracture, tolerances, manufacturing conditions, thermal properties, fluid properties, boundary conditions, applicable codes, and physical measurements. Safety-critical, regulated, structural, pressure, rotating-equipment, combustion, HVAC, and life-safety work requires qualified professional review.</div>
    <div data-mechanical-thermal-root></div>
  </section>

<section class="sc-lab-panel sc-lab-module" data-module-panel="civil-infrastructure" hidden data-lab-module="civil-infrastructure">
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/CIVIL-INFRASTRUCTURE</p>
      <h3>Civil engineering and infrastructure systems</h3>
      <p>Auditable screening calculations for structures, soils, drainage, transportation, water systems, lifecycle cost, risk, reliability, resilience, and embodied carbon.</p>
    </div>
  </header>
  <div data-civil-infrastructure-root></div>
</section>

<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="architecture-building"
    data-module-panel="architecture-building"
>
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/ARCHITECTURE-BUILDING</p>
      <h3>Architecture and building performance</h3>
      <p>Auditable calculations for building geometry, envelope performance, solar and daylight systems, ventilation and indoor environmental quality, HVAC energy, water, carbon, acoustics, and passive resilience.</p>
    </div>
  </header>
  <div data-architecture-building-root></div>
</section>

<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="urban-planning-spatial"
    data-module-panel="urban-planning-spatial"
>
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/URBAN-PLANNING-SPATIAL</p>
      <h3>Urban planning and spatial systems</h3>
      <p>Auditable calculations for land use, density, accessibility, mobility, spatial networks, GIS indicators, public services, equity, resilience, and urban scenarios.</p>
    </div>
  </header>
  <div data-urban-planning-spatial-root></div>
</section>

<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="sustainable-cities-resilience"
    data-module-panel="sustainable-cities-resilience"
>
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/SUSTAINABLE-CITIES-RESILIENCE</p>
      <h3>Sustainable cities and urban resilience</h3>
      <p>Auditable calculations for urban resource flows, climate mitigation, adaptation, critical infrastructure continuity, equity, social resilience, governance, and integrated city scenarios.</p>
    </div>
  </header>
  <div data-sustainable-cities-resilience-root></div>
</section>

<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="comparative-economics-development-systems"
    data-module-panel="comparative-economics-development-systems"
>
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/COMPARATIVE-ECONOMICS-DEVELOPMENT-SYSTEMS</p>
      <h3>Comparative economics and development systems</h3>
      <p>Auditable calculations for national accounts, economic growth, productivity, convergence, trade, structural transformation, labor markets, poverty, inequality, human development, public finance, development finance, and resilience scenarios.</p>
    </div>
  </header>
  <div data-comparative-economics-development-systems-root></div>
</section>

<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="aerospace-engineering-flight-systems"
    data-module-panel="aerospace-engineering-flight-systems"
>
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/AEROSPACE-ENGINEERING-FLIGHT-SYSTEMS</p>
      <h3>Aerospace engineering and flight systems</h3>
      <p>Auditable calculations for atmosphere and aerodynamics, flight mechanics, aircraft performance, stability and control, propulsion integration, structures, loads, aeroelastic screening, navigation, mission analysis, and flight-system reliability.</p>
    </div>
  </header>
  <div data-aerospace-engineering-flight-systems-root></div>
</section>

<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="rocket-propulsion-spaceflight"
    data-module-panel="rocket-propulsion-spaceflight"
>
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/ROCKET-PROPULSION-SPACEFLIGHT</p>
      <h3>Rocket propulsion and spaceflight</h3>
      <p>Auditable educational and preliminary-design calculations for rocket performance, nozzle flow, launch-vehicle staging, ascent dynamics, orbital mechanics, spacecraft power and thermal systems, communications, mission budgets, and reliability.</p>
    </div>
  </header>
  <div data-rocket-propulsion-spaceflight-root></div>
</section>

<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="microbiology-laboratory"
    data-module-panel="microbiology-laboratory"
>
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/MICROBIOLOGY</p>
      <h3>Microbiology laboratory</h3>
      <p>Auditable calculations for microbial growth, continuous culture, enumeration, microscopy, environmental microbiology, antimicrobial and disinfection screening, microbial ecology, and laboratory quality control.</p>
    </div>
  </header>
  <div data-microbiology-laboratory-root></div>
</section>





<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="circular-economy-industrial-ecology"
    data-module-panel="circular-economy-industrial-ecology"
>
  <header class="sc-lab-panel-header">
    <div>
      <p class="sc-lab-kicker">LAB/CIRCULAR-ECONOMY-INDUSTRIAL-ECOLOGY</p>
      <h3>Circular economy and industrial ecology</h3>
      <p>Auditable calculations for material-flow accounting, circular products, waste prevention and recovery, industrial symbiosis, lifecycle footprints, resource productivity, and circular transition scenarios.</p>
    </div>
  </header>
  <div data-circular-economy-industrial-ecology-root></div>
</section>






  <section class="sc-lab-panel" data-lab-module="visualization-studio" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/VISUALIZATION</span><h3>Universal visualization and export studio</h3></div>
          <span class="sc-lab-status-dot is-ready">Shared engine</span>
        </div>
        <div class="sc-lab-method-note">Run any Lab calculation and its structured result will be captured here. The same result contract drives the chart, SVG, PNG, PDF, CSV, JSON, project record, notebook entry, and Decision Studio analysis packet.</div>
        <div class="sc-lab-viz-layout">
          <aside class="sc-lab-viz-controls">
            <label>Figure title<input type="text" data-viz-title value="Scientific analysis"></label>
            <label>Subtitle<textarea rows="3" data-viz-subtitle placeholder="Method, scenario, or interpretation boundary"></textarea></label>
            <label>Chart type<select data-viz-type><option value="auto">Automatic</option><option value="line">Line</option><option value="scatter">Scatter</option><option value="bar">Bar</option><option value="summary">Summary</option></select></label>
            <label>Theme<select data-viz-theme></select></label>
            <label>Aspect ratio<select data-viz-aspect><option value="16:9">16:9 presentation</option><option value="3:2">3:2 report</option><option value="4:3">4:3 document</option><option value="1:1">1:1 square</option></select></label>
            <label class="sc-lab-check"><input type="checkbox" checked data-viz-grid> Show grid</label>
            <label class="sc-lab-check"><input type="checkbox" checked data-viz-legend> Show legend</label>
            <button type="button" class="sc-lab-button sc-lab-button-primary" data-viz-render>Render figure</button>
          </aside>
          <div class="sc-lab-viz-workspace">
            <div class="sc-lab-doc-status" data-viz-status>Run any calculation to create a visualization-ready result.</div>
            <div class="sc-lab-viz-chart" data-viz-chart><div class="sc-lab-data-note">No analysis has been captured yet.</div></div>
            <div class="sc-lab-viz-export-grid" aria-label="Visualization export actions">
              <button type="button" class="sc-lab-button" data-viz-export-svg>Download SVG</button>
              <button type="button" class="sc-lab-button" data-viz-export-png>Download PNG</button>
              <button type="button" class="sc-lab-button" data-viz-export-pdf>Download PDF</button>
              <button type="button" class="sc-lab-button" data-viz-export-csv>Download CSV</button>
              <button type="button" class="sc-lab-button" data-viz-export-json>Download analysis JSON</button>
              <button type="button" class="sc-lab-button" data-viz-save>Save to project</button>
              <button type="button" class="sc-lab-button" data-viz-notebook>Add to notebook</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-viz-handoff-studio>Send to Decision Studio</button>
            </div>
            <details class="sc-lab-viz-audit"><summary>Analysis and audit metadata</summary><pre data-viz-meta>{}</pre></details>

            <section class="sc-lab-dimensional-studio" aria-labelledby="sc-lab-dimensional-title">
              <div class="sc-lab-dimensional-head">
                <div><span class="sc-lab-section-code">LAB/3D-4D</span><h4 id="sc-lab-dimensional-title">Dimensional scene and polytope viewer</h4></div>
                <span class="sc-lab-status-dot is-ready">Interactive projection</span>
              </div>
              <p class="sc-lab-method-note">Render true three-coordinate scenes or four-coordinate models projected 4D → 3D → 2D. Current results use direct numeric fields when available; otherwise the viewer labels the output as a normalized result-space glyph rather than physical geometry.</p>
              <div class="sc-lab-dimensional-layout">
                <aside class="sc-lab-dimensional-controls">
                  <label>Scene source<select data-dim-preset><option value="tesseract4d">4D tesseract</option><option value="simplex4d">4D simplex / 5-cell</option><option value="crossPolytope4d">4D 16-cell</option><option value="cube3d">3D cube</option><option value="current4d">Current analysis as 4D result space</option><option value="current3d">Current analysis as 3D result space</option><option value="custom">Custom scene JSON</option></select></label>
                  <label>Theme<select data-dim-theme></select></label>
                  <div class="sc-lab-dimensional-actions"><button type="button" class="sc-lab-button" data-dim-load-analysis>Load current analysis</button><button type="button" class="sc-lab-button" data-dim-reset>Reset view</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-dim-render>Render</button><button type="button" class="sc-lab-button" data-dim-animate>Animate</button></div>
                  <div class="sc-lab-dimensional-toggles"><label class="sc-lab-check"><input type="checkbox" checked data-dim-show-vertices> Vertices</label><label class="sc-lab-check"><input type="checkbox" checked data-dim-show-edges> Edges</label><label class="sc-lab-check"><input type="checkbox" data-dim-show-labels> Labels</label></div>
                  <details open><summary>3D camera rotation</summary><div class="sc-lab-slider-grid"><label>X rotation<input type="range" min="-180" max="180" step="1" value="18" data-dim-rotation="x"></label><label>Y rotation<input type="range" min="-180" max="180" step="1" value="-24" data-dim-rotation="y"></label><label>Z rotation<input type="range" min="-180" max="180" step="1" value="8" data-dim-rotation="z"></label><label>3D perspective<input type="range" min="2.2" max="14" step="0.1" value="6" data-dim-distance3></label><label>Scene scale<input type="range" min="0.45" max="1.8" step="0.05" value="1" data-dim-scale></label></div></details>
                  <details><summary>4D plane rotation</summary><div class="sc-lab-slider-grid"><label>XY<input type="range" min="-180" max="180" step="1" value="0" data-dim-rotation="xy"></label><label>XZ<input type="range" min="-180" max="180" step="1" value="0" data-dim-rotation="xz"></label><label>XW<input type="range" min="-180" max="180" step="1" value="22" data-dim-rotation="xw"></label><label>YZ<input type="range" min="-180" max="180" step="1" value="0" data-dim-rotation="yz"></label><label>YW<input type="range" min="-180" max="180" step="1" value="-18" data-dim-rotation="yw"></label><label>ZW<input type="range" min="-180" max="180" step="1" value="14" data-dim-rotation="zw"></label><label>4D perspective<input type="range" min="1.5" max="10" step="0.1" value="4" data-dim-distance4></label></div></details>
                  <details><summary>Custom scene specification</summary><label>Scene JSON<textarea rows="10" data-dim-custom>{"dimensions":4,"title":"Custom four-dimensional scene","vertices":[[-1,-1,-1,-1],[1,-1,-1,-1],[1,1,-1,-1],[-1,1,-1,-1]],"edges":[[0,1],[1,2],[2,3],[3,0]]}</textarea></label></details>
                </aside>
                <div class="sc-lab-dimensional-workspace">
                  <div class="sc-lab-doc-status" data-dim-status>Preparing dimensional scene…</div>
                  <div class="sc-lab-dimensional-chart" data-dim-chart></div>
                  <div class="sc-lab-viz-export-grid" aria-label="Dimensional visualization export actions"><button type="button" class="sc-lab-button" data-dim-export-svg>Download SVG</button><button type="button" class="sc-lab-button" data-dim-export-png>Download PNG</button><button type="button" class="sc-lab-button" data-dim-export-pdf>Download PDF</button><button type="button" class="sc-lab-button" data-dim-export-json>Download scene JSON</button><button type="button" class="sc-lab-button" data-dim-export-package>Download scene package</button><button type="button" class="sc-lab-button" data-dim-save>Save scene to project</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-dim-handoff>Send scene to Decision Studio</button></div>
                  <details class="sc-lab-viz-audit"><summary>Scene and projection metadata</summary><pre data-dim-meta>{}</pre></details>
                </div>
              </div>
            </section>
          </div>
        </div>
      </section>



      <section class="sc-lab-panel" data-lab-module="report-studio" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/REPORTING</span><h3>PDF reports and Decision Studio handoff</h3></div>
          <span class="sc-lab-status-dot is-ready">Auditable</span>
        </div>
        <div class="sc-lab-method-note">Compose a text-selectable technical report, decision brief, evidence packet, or executive summary from up to twelve Lab analyses. The report retains equations, inputs, outputs, figures, dimensional scenes, assumptions, warnings, validation, sources, code/runtime metadata, and audit fingerprints.</div>
        <div class="sc-lab-report-layout">
          <aside class="sc-lab-report-controls">
            <label>Report title<input type="text" value="Sustainable Catalyst Lab analysis report" data-report-title></label>
            <label>Subtitle<input type="text" value="Auditable calculations, figures, assumptions, validation, and provenance" data-report-subtitle></label>
            <div class="sc-lab-grid sc-lab-grid-2">
              <label>Report type<select data-report-type><option value="technical-report">Technical report</option><option value="decision-brief">Decision brief</option><option value="evidence-packet">Evidence packet</option><option value="executive-summary">Executive summary</option></select></label>
              <label>Page size<select data-report-page-size><option value="LETTER">US Letter</option><option value="A4">A4</option></select></label>
            </div>
            <label>Executive summary<textarea rows="7" data-report-summary placeholder="Summarize the question, methods, findings, limitations, and decision relevance."></textarea></label>
            <label class="sc-lab-check"><input type="checkbox" checked data-report-audit> Include full audit metadata</label>
            <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-report-load-current>Load current analysis</button><button type="button" class="sc-lab-button" data-report-select-all>Select up to 12</button><button type="button" class="sc-lab-button" data-report-clear-selection>Clear</button></div>
            <div class="sc-lab-report-analysis-list" data-report-analysis-list></div>
            <button type="button" class="sc-lab-button sc-lab-button-primary" data-report-compose>Compose report preview</button>
          </aside>
          <div class="sc-lab-report-workspace">
            <div class="sc-lab-doc-status" data-report-status>Run a calculation or select a saved visualization to begin.</div>
            <article class="sc-lab-report-preview" data-report-preview><div class="sc-lab-data-note">No report has been composed yet.</div></article>
            <div class="sc-lab-report-actions" aria-label="Report export and handoff actions">
              <button type="button" class="sc-lab-button" data-report-download-pdf>Download local PDF</button>
              <button type="button" class="sc-lab-button" data-report-download-render>Download Render PDF</button>
              <button type="button" class="sc-lab-button" data-report-download-json>Download report JSON</button>
              <button type="button" class="sc-lab-button" data-report-download-packet>Download handoff packet</button>
              <button type="button" class="sc-lab-button" data-report-validate>Validate handoff</button>
              <button type="button" class="sc-lab-button" data-report-save>Save report to project</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-report-handoff>Send to Decision Studio</button>
            </div>
            <details class="sc-lab-viz-audit"><summary>Report contract and audit metadata</summary><pre data-report-meta>{}</pre></details>
          </div>
        </div>
      </section>

      <section class="sc-lab-panel" data-lab-module="code-studio" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/COMPUTE-DISPATCHER</span><h3>Universal code switcher and multi-language execution</h3></div>
          <span class="sc-lab-status-dot" data-code-backend-indicator>Local mode</span>
        </div>
        <div class="sc-lab-method-note">Inspect equivalent source in twelve languages, run the portable contract locally, or execute curated implementations through the governed WordPress-to-Python Compute Core gateway. The public interface never submits arbitrary source code and never receives the Render API key.</div>
        <div class="sc-lab-compute-statusbar">
          <div><strong data-code-backend-title>Python Compute Core</strong><span data-code-backend-status>Checking configuration…</span></div>
          <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-code-backend-refresh>Refresh backend</button><button type="button" class="sc-lab-button" data-code-cancel-job disabled>Cancel active job</button></div>
        </div>
        <div class="sc-lab-code-layout">
          <aside class="sc-lab-code-controls">
            <label>Method<select data-code-method></select></label>
            <label>Language<select data-code-language></select></label>
            <label>Execution mode<select data-code-execution-mode><option value="local">Local portable contract</option><option value="render">Render native worker</option></select></label>
            <label>Request mode<select data-code-request-mode><option value="direct">Direct execution</option><option value="queued">Queued worker job</option></select></label>
            <div class="sc-lab-code-fields" data-code-fields></div>
            <button type="button" class="sc-lab-button sc-lab-button-primary" data-code-run>Run selected engine</button>
            <button type="button" class="sc-lab-button" data-code-validate>Compare with current JavaScript</button>
            <button type="button" class="sc-lab-button" data-code-render>Regenerate source</button>
            <div class="sc-lab-data-note" data-code-status></div>
          </aside>
          <div class="sc-lab-code-workspace">
            <div class="sc-lab-code-toolbar">
              <button type="button" class="sc-lab-button" data-code-copy>Copy code</button>
              <button type="button" class="sc-lab-button" data-code-download>Download source</button>
              <button type="button" class="sc-lab-button" data-code-contract>Download method JSON</button>
              <button type="button" class="sc-lab-button" data-code-notebook>Download notebook</button>
              <button type="button" class="sc-lab-button" data-code-catalog>Download catalog</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-code-save>Save to project</button>
            </div>
            <textarea class="sc-lab-code-editor" rows="31" spellcheck="false" data-code-source></textarea>
            <div class="sc-lab-grid sc-lab-grid-2">
              <article class="sc-lab-tool"><h4>Execution result</h4><pre data-code-result></pre></article>
              <article class="sc-lab-tool"><h4>Method contract</h4><pre data-code-meta></pre></article>
            </div>
            <div data-code-validation></div>
            <section class="sc-lab-tool sc-lab-tool-wide sc-lab-worker-panel">
              <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">WORKERS/COMPARE</span><h4>Cross-language execution</h4></div><button type="button" class="sc-lab-button sc-lab-button-primary" data-code-compare-workers>Compare selected workers</button></div>
              <p class="sc-lab-data-note">Only runtimes reported as available by the Render service are executable. Source-only languages remain viewable and downloadable.</p>
              <div class="sc-lab-worker-languages" data-code-worker-languages></div>
              <div data-code-worker-comparison></div>
            </section>
            <section class="sc-lab-tool sc-lab-tool-wide sc-lab-job-panel">
              <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">QUEUE/JOB</span><h4>Execution job record</h4></div></div>
              <pre data-code-job>No queued job is active.</pre>
            </section>
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


      <section class="sc-lab-panel" data-lab-module="workspace-data" hidden>
        <div class="sc-lab-panel-head">
          <div><span class="sc-lab-section-code">LAB/DATA-MANAGEMENT</span><h3>Workspace backup, restore, and reset</h3></div>
          <span class="sc-lab-status-dot is-ready">Local workspace</span>
        </div>
        <div class="sc-lab-method-note">These controls manage Sustainable Catalyst Lab data stored in this browser. Export a backup before destructive changes. Resetting local Lab data does not deactivate the WordPress plugin or remove the public Lab page.</div>
        <div data-workspace-counts></div>
        <div class="sc-lab-grid sc-lab-grid-2 sc-lab-workspace-management">
          <article class="sc-lab-tool">
            <h4>Back up the workspace</h4>
            <p>Download every project, record, chart, analysis packet, note, observation, and compatible preference.</p>
            <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-workspace-export-json>Export workspace JSON</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-workspace-export-zip>Export complete ZIP</button></div>
            <p class="sc-lab-data-note">The ZIP contains workspace.json, project JSON files, notebook Markdown, observations CSV, visualization records, analysis packets, a manifest, and restore instructions.</p>
          </article>
          <article class="sc-lab-tool">
            <h4>Restore a backup</h4>
            <label>Restore mode<select data-restore-mode><option value="copy">Import projects as copies</option><option value="merge">Merge by project identifier</option><option value="replace">Replace the current workspace</option></select></label>
            <input type="file" accept="application/json,.json,application/zip,.zip" hidden data-workspace-restore-file>
            <button type="button" class="sc-lab-button sc-lab-button-primary" data-workspace-restore>Select backup</button>
            <div class="sc-lab-data-note" data-restore-status>No restore file selected.</div>
          </article>
          <article class="sc-lab-tool sc-lab-tool-wide sc-lab-danger-zone">
            <h4>Selective reset and factory reset</h4>
            <label>Reset scope<select data-reset-scope><option value="preferences">Reset interface and visualization settings</option><option value="notes-observations">Clear notes and observations across all projects</option><option value="analysis-history">Clear calculation and analysis history across all projects</option><option value="active-project">Reset the active project but keep its project shell</option><option value="delete-active">Delete the active project</option><option value="factory-reset">Factory-reset the complete local Lab workspace</option></select></label>
            <div class="sc-lab-reset-description" data-reset-description></div><div class="sc-lab-reset-scope-count" data-reset-scope-count></div>
            <div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button" data-reset-backup>Download backup first</button><span data-reset-backup-state></span></div>
            <label>Type <strong>RESET</strong> to confirm<input type="text" autocomplete="off" data-reset-confirm></label>
            <button type="button" class="sc-lab-button sc-lab-button-danger" data-reset-apply disabled>Apply selected reset</button>
            <details><summary>Last deletion receipt</summary><pre data-reset-receipt>No reset has been completed in this session.</pre></details>
          </article>
        </div>
      </section>

      <section class="sc-lab-panel" data-lab-module="source-registry" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/SOURCES</span><h3>Scientific source registry</h3></div><button class="sc-lab-button sc-lab-button-primary" data-source-refresh>Refresh registry</button></div>
        <div class="sc-lab-toolbar"><label>Filter<input type="search" data-source-filter placeholder="Source, domain, coverage, or format"></label></div>
        <div class="sc-lab-source-registry" data-source-registry></div>
      </section>

      <section class="sc-lab-panel" data-lab-module="system-status" hidden>
        <div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">LAB/STATUS</span><h3>System and connector status</h3></div><button class="sc-lab-button sc-lab-button-primary" data-status-refresh>Run checks</button></div>
        <section class="sc-lab-release-console-v0821" data-sc-lab-release-console data-sc-lab-canonical-release-source="build/sc-lab-release-manifest.json">
          <div class="sc-lab-release-console-v0821__hero">
            <div><span class="sc-lab-release-console-v0821__eyebrow">Sustainable Catalyst Lab · Public Release</span><strong class="sc-lab-release-console-v0821__release" data-sc-lab-console-release>v<?php echo esc_html(defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : 'unknown'); ?></strong></div>
            <span class="sc-lab-release-console-v0821__state" data-sc-lab-console-state>Checking release integrity…</span>
          </div>
          <div class="sc-lab-release-console-v0821__section"><h4>Components</h4><div class="sc-lab-release-console-v0821__components" data-sc-lab-console-components><div class="sc-lab-release-console__component"><span>Lab Platform</span><strong><?php echo esc_html(defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : 'unknown'); ?></strong></div><div class="sc-lab-release-console__component"><span>Platform Compatibility</span><strong><?php echo esc_html(defined('SC_LAB_PLATFORM_COMPAT_VERSION') ? SC_LAB_PLATFORM_COMPAT_VERSION : 'unknown'); ?></strong></div></div></div>
          <div class="sc-lab-release-console-v0821__section"><h4>Release Integrity</h4><div class="sc-lab-release-console-v0821__integrity" data-sc-lab-console-integrity><div class="sc-lab-release-console__check"><span>…</span><strong>Checking canonical release identity</strong></div></div></div>
        </section>
        <div class="sc-lab-status-table" data-system-status></div>
      </section>

<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="biochemistry-molecular-analysis"
    data-module-panel="biochemistry-molecular-analysis"
    hidden
>
    <header class="sc-lab-module-header">
        <p class="sc-lab-kicker">LAB/BIOCHEMISTRY</p>
        <h3>Biochemistry and molecular analysis</h3>
        <p>
            Auditable calculations for biomolecule quantification,
            proteins, enzyme kinetics, nucleic acids, molecular
            binding, buffers, spectroscopy, separations, and
            laboratory quality control.
        </p>
    </header>

    <div
        data-biochemistry-molecular-analysis-root
    ></div>

    <div
        data-biochemistry-visualization-batch-root
    ></div>

    <div
        data-molecular-validation-provenance-root
    ></div>
</section>


<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="biotechnology-bioprocess-engineering"
    data-module-panel="biotechnology-bioprocess-engineering"
    hidden
>
    <header class="sc-lab-module-header">
        <p class="sc-lab-kicker">LAB/BIOTECHNOLOGY/BIOPROCESS</p>
        <h3>Biotechnology and bioprocess engineering</h3>
        <p>
            Auditable calculations and process simulations for cell
            growth, reactor balances, feed strategy, continuous
            culture, oxygen transfer, mixing, scale-up, production,
            and downstream recovery.
        </p>
    </header>

    <div data-biotechnology-bioprocess-root></div>

    <div data-bioprocess-monitoring-control-root></div>

    <div data-bioprocess-validation-provenance-root></div>
</section>


<section
    class="sc-lab-panel sc-lab-module"
    data-lab-module="biomedical-engineering-biosignals"
    data-module-panel="biomedical-engineering-biosignals"
    hidden
>
    <header class="sc-lab-module-header">
        <p class="sc-lab-kicker">
            LAB/BIOMEDICAL/BIOSIGNALS
        </p>
        <h3>
            Biomedical engineering and biosignals
        </h3>
        <p>
            Non-clinical calculations and waveform analysis for
            acquisition design, ECG, PPG, respiration, EMG, EEG,
            filtering, and signal-quality review.
        </p>
    </header>

    <div data-biomedical-biosignals-root></div>

    <div data-biosignal-visualization-root></div>
</section>


<section class="sc-lab-panel sc-lab-module" data-lab-module="genetics-genomics-sequence-analysis" data-module-panel="genetics-genomics-sequence-analysis" hidden>
  <header class="sc-lab-module-header">
    <p class="sc-lab-kicker">LAB/GENETICS/GENOMICS</p>
    <h3>Genetics, genomics, and sequence analysis</h3>
    <p>Deterministic sequence analysis, visualization, validation, dataset manifests, and tamper-aware provenance for research workflows.</p>
  </header>
  <div data-genetics-genomics-root></div>
  <div data-genomic-visualization-root></div>
  <div data-genomic-validation-root></div>
</section>


<section class="sc-lab-panel sc-lab-module" data-lab-module="laboratory-data-instrumentation" data-module-panel="laboratory-data-instrumentation" hidden>
  <header class="sc-lab-module-header">
    <p class="sc-lab-kicker">LAB/DATA/INSTRUMENTATION</p>
    <h3>Laboratory data and instrumentation</h3>
    <p>Instrument, sensor, sample, run, calibration, maintenance, measurement, and custody records with normalized ingestion and auditable manifests.</p>
  </header>
  <div data-laboratory-instrumentation-root></div>

    <div data-instrumentation-live-visualization-root></div>

    <div data-instrumentation-validation-custody-root></div>
</section>

      <section class="sc-lab-panel sc-lab-module sc-gs0470" data-lab-module="graph-studio" data-module-panel="graph-studio" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">VISUALIZE / GRAPH STUDIO / v0.82.0</p><h3>Scientific Visualization Workspace</h3><p>Build governed 2D, 3D, 4D, spatial, geospatial, raster, and scientifically marked-up figures from explicit datasets and geometry. v0.82 makes uncertainty, empirical distributions, posterior draws, and explicit ensembles first-class visualization objects while preserving markup, spatial, linked-view, 4D, 3D, large-data, and data-binding compatibility.</p></header>
        <p class="sc-gs0470-status" data-gs-v0470-status role="status" aria-live="polite">Graph Studio loading…</p>
        <div class="sc-gs0470-shell">
          <aside class="sc-gs0470-controls" aria-label="Figure controls">
            <section class="sc-gs0470-card"><h4>Figure definition</h4>
              <label>Visualization type<select data-gs-v0470-kind>
                <optgroup label="Core 2D"><option value="line-scatter">Scatter + fitted line</option><option value="line">Line</option><option value="scatter">Scatter</option><option value="step">Step</option><option value="area">Area</option><option value="stacked-area">Stacked area</option></optgroup>
                <optgroup label="Bars & distributions"><option value="bar">Bar</option><option value="grouped-bar">Grouped bar</option><option value="stacked-bar">Stacked bar</option><option value="histogram">Histogram</option><option value="horizontal-bars">Horizontal bars</option><option value="density">Density / KDE</option><option value="box">Box</option><option value="violin">Violin</option></optgroup>
                <optgroup label="Inference & diagnostics"><option value="error-bar">Error bar</option><option value="confidence-band">Confidence band</option><option value="ecdf">ECDF</option><option value="qq">Q-Q</option><option value="residual">Residual</option></optgroup>
                <optgroup label="Fields & binned views"><option value="heatmap">Heatmap</option><option value="contour">Contour</option><option value="hexbin">Hexbin</option></optgroup>
                <optgroup label="Analytical"><option value="waterfall">Waterfall</option><option value="pareto">Pareto</option></optgroup>
                <optgroup label="3D scientific scenes"><option value="point-cloud-3d">3D point cloud</option><option value="polyline-3d">3D trajectory / polyline</option><option value="vectors-3d">3D vector field</option><option value="mesh-3d">3D mesh · explicit triangles</option></optgroup><optgroup label="Higher-dimensional"><option value="surface-4d">4D response surface · Canvas</option></optgroup>
              </select></label>
              <label>Figure title<input data-gs-v0470-title value="Scientific figure"></label>
              <label>Subtitle<input data-gs-v0470-subtitle placeholder="Optional scientific context"></label>
              <div class="sc-gs0470-inline"><label>X field<input data-gs-v0470-x value="x"></label><label>Primary Y field<input data-gs-v0470-y value="y"></label></div>
              <div data-gs-v0730-tabular-only><label>Series <small>key:label:mode, comma separated</small><input data-gs-v0470-series value="observed:Observed:points,fit:Fitted model:line"></label>
              <div class="sc-gs0470-inline"><label>Z field <small>heatmap</small><input data-gs-v0470-z value="z"></label><label>Histogram bins<input type="number" min="4" max="40" value="12" data-gs-v0470-bins></label></div></div>
              <div class="sc-gs0470-inline"><label>X-axis label<input data-gs-v0470-x-label value="Time"></label><label>Y-axis label<input data-gs-v0470-y-label value="Response"></label></div>
              <div class="sc-gs0740-axis-grid" data-gs-v0730-tabular-only>
                <div class="sc-gs0740-axis-card"><strong>X AXIS</strong><div class="sc-gs0740-mini"><label>Scale<select data-gs-v0740-x-scale><option>linear</option><option>log</option><option>symlog</option><option>probability</option><option>datetime</option><option>categorical</option></select></label><label>Unit<input data-gs-v0740-x-unit placeholder="s, m, USD…"></label></div><div class="sc-gs0740-mini"><label>Ticks<select data-gs-v0740-x-format><option>auto</option><option>scientific</option><option>si</option><option>plain</option><option>percent</option></select></label><label><input type="checkbox" data-gs-v0740-x-invert> Invert axis</label></div></div>
                <div class="sc-gs0740-axis-card"><strong>Y AXIS</strong><div class="sc-gs0740-mini"><label>Scale<select data-gs-v0740-y-scale><option>linear</option><option>log</option><option>symlog</option><option>probability</option><option>datetime</option><option>categorical</option></select></label><label>Unit<input data-gs-v0740-y-unit placeholder="mg/L, %, Pa…"></label></div><div class="sc-gs0740-mini"><label>Ticks<select data-gs-v0740-y-format><option>auto</option><option>scientific</option><option>si</option><option>plain</option><option>percent</option></select></label><label><input type="checkbox" data-gs-v0740-y-invert> Invert axis</label></div></div>
              </div>
              <label data-gs-v0730-tabular-only>Hexbin size <small>used only for hexbin</small><input type="number" step="any" min="0.000001" value="1" data-gs-v0740-bin-size></label>
              <section class="sc-gs0750-binding" aria-label="Scientific data binding">
                <div class="sc-gs0750-binding-head"><strong>DATASET → TRANSFORM → BIND</strong><span>v0.75 · reproducible lineage</span></div>
                <div class="sc-gs0750-grid"><label>Dataset ID<input data-gs-v0750-dataset-id value="graph-studio-dataset"></label><label>Dataset title<input data-gs-v0750-dataset-title value="Graph Studio dataset"></label><label>Source type<select data-gs-v0750-source-type><option value="inline">Inline / pasted</option><option value="experiment">Experiment</option><option value="dataset-registry">Dataset Registry</option><option value="instrument">Instrument</option><option value="archive">Archive</option><option value="example">Example</option></select></label><label>Source record ID<input data-gs-v0750-source-id placeholder="dataset / run / source record"></label><label>Source URI<input data-gs-v0750-source-uri placeholder="Optional canonical URI"></label><label>License<input data-gs-v0750-license placeholder="Optional data license"></label></div>
                <div class="sc-gs0750-grid"><label>Group field<input data-gs-v0750-group placeholder="species, cohort, scenario…"></label><label>Point label field<input data-gs-v0750-label placeholder="sample_id"></label><label>Lower interval field<input data-gs-v0750-y-low placeholder="response_low"></label><label>Upper interval field<input data-gs-v0750-y-high placeholder="response_high"></label><label>Contour level field<input data-gs-v0750-level placeholder="level (optional)"></label><label>Binding ID<input data-gs-v0750-binding-id value="graph-studio-binding"></label></div>
                <label>Transformation pipeline JSON <small>governed operations; [] is an identity pipeline</small><textarea rows="7" spellcheck="false" data-gs-v0750-pipeline>{"operations":[]}</textarea></label>
                <label class="sc-gs0750-check"><input type="checkbox" checked data-gs-v0750-drop-missing> Drop rows missing mapped values before figure binding</label>
                <p class="sc-gs0750-boundary">Supported governed stages include derive, filter, select/drop/rename, cast, impute, scale, unit conversion, sort, aggregate, bin, and drop-missing. Arbitrary code, SQL, network access, automatic imputation, and automatic unit inference remain disabled.</p>
              </section>
              <section class="sc-gs0760-adaptive" aria-label="Large-data adaptive rendering">
                <div class="sc-gs0760-head"><strong>LARGE-DATA ADAPTIVE RENDERING</strong><span>v0.76 · deterministic render plans</span></div>
                <div class="sc-gs0760-grid"><label>Strategy<select data-gs-v0760-strategy><option value="auto" selected>Auto by plot kind</option><option value="lttb">LTTB · line fidelity</option><option value="grid">Grid · spatial/scatter</option><option value="quantile">Quantile · distributions</option><option value="stride">Stride · deterministic</option><option value="full">Full · within budget</option></select></label><label>Render point budget<input type="number" min="100" max="5000" step="100" value="2000" data-gs-v0760-budget></label><label class="sc-gs0760-check"><input type="checkbox" checked data-gs-v0760-progressive> Progressive preview → interactive → detail</label></div>
                <p class="sc-gs0760-boundary">Adaptive rendering changes only the displayed representation. Source rows and source fingerprint remain authoritative. Browser inline sources are bounded to 50,000 rows; the Python v0.76 backend accepts up to 250,000 rows. Scientific transformations are never applied after sampling.</p>
              </section>
              <section class="sc-gs0770-scene" data-gs-v0770-scene-options hidden aria-label="3D scientific scene controls">
                <div class="sc-gs0770-head"><strong>3D SCIENTIFIC SCENE</strong><span>v0.77 · canvas3d</span></div>
                <div class="sc-gs0770-grid"><label>Camera projection<select data-gs-v0770-projection><option value="perspective" selected>Perspective</option><option value="orthographic">Orthographic</option></select></label><label>Camera position<input data-gs-v0770-camera-position value="3.2,2.4,4.4" placeholder="x,y,z"></label><label>Camera target<input data-gs-v0770-camera-target value="0,0,0" placeholder="x,y,z"></label><label>Point size<input type="number" min="1" max="18" step="0.5" value="4" data-gs-v0770-point-size></label><label>Line / vector width<input type="number" min="0.5" max="8" step="0.25" value="1.5" data-gs-v0770-line-width></label><label>Vector scale<input type="number" step="0.1" value="1" data-gs-v0770-vector-scale></label></div>
                <div class="sc-gs0770-grid" data-gs-v0770-vector-fields hidden><label>dX field<input data-gs-v0770-dx value="dx"></label><label>dY field<input data-gs-v0770-dy value="dy"></label><label>dZ field<input data-gs-v0770-dz value="dz"></label></div>
                <label data-gs-v0770-mesh-fields hidden>Explicit triangle indexes <small>JSON array; e.g. [[0,1,2],[0,2,3]]</small><textarea rows="5" spellcheck="false" data-gs-v0770-faces>[]</textarea></label>
                <label>Clipping intent <small>optional JSON; no implicit clipping</small><textarea rows="3" spellcheck="false" data-gs-v0770-clipping>{"enabled":false,"bounds":{}}</textarea></label>
                <p class="sc-gs0770-boundary">3D scenes preserve explicit scientific coordinates and supplied topology. Point clouds are not converted into surfaces; mesh triangles are never inferred; the canvas3d renderer uses painter depth sorting rather than claiming a hardware depth buffer or hidden-surface guarantee. Large 3D datasets use the v0.76 deterministic stride representation before scene construction.</p>
              </section>
              <div data-gs-v0750-surface-options hidden><label>4D data mode<select data-gs-v0750-surface-mode><option value="project-data" selected>Project dataset · point projection</option><option value="biodiversity">Synthetic biodiversity demonstration</option><option value="generic">Synthetic generic response field</option></select></label></div>
              <div data-gs-v0730-surface-only hidden><label>Synthetic 4D profile<select data-gs-v0730-profile><option value="generic">Generic response field</option><option value="biodiversity">Biodiversity demonstration</option></select></label><div class="sc-gs0470-inline"><label>Z-axis label<input data-gs-v0730-z-label value="Response"></label><label>Fourth dimension label<input data-gs-v0730-w-label value="Fourth dimension"></label></div><div class="sc-gs0750-grid"><label>W field<input data-gs-v0750-w value="w"></label><label>Z unit<input data-gs-v0750-z-unit placeholder="unit"></label><label>W unit<input data-gs-v0750-w-unit placeholder="unit"></label></div><p class="sc-lab-data-note">Project-data 4D mode binds x/y/z/w rows and projects observed records only. Values are normalized for projection while original domains and units remain in provenance. v0.75 does not interpolate a surface, infer uncertainty, or forecast between records.</p></div>
              <section class="sc-gs0780-state" data-gs-v0780-state-options hidden aria-label="4D time and parameter-space controls">
                <div class="sc-gs0780-state-head"><strong>4D / TIME / PARAMETER SPACE</strong><span>v0.78 · observed states only</span></div>
                <div class="sc-gs0780-grid">
                  <label>State-space mode<select data-gs-v0780-mode><option value="4d-points" selected>Observed 4D points</option><option value="time-sequence">Discrete time-state sequence</option><option value="parameter-sweep">Observed parameter sweep</option><option value="legacy">Legacy v0.75 4D projection path</option></select></label>
                  <label>State axis field<input data-gs-v0780-axis-field value="w" placeholder="time, parameter, sweep_value…"></label>
                  <label>Axis scale<select data-gs-v0780-axis-scale><option value="numeric">Numeric</option><option value="index">Index / discrete time</option><option value="elapsed">Elapsed time</option><option value="timestamp">ISO timestamp</option><option value="categorical">Categorical parameter</option></select></label>
                  <label>Axis label<input data-gs-v0780-axis-label value="Fourth dimension"></label>
                  <label>Axis unit<input data-gs-v0780-axis-unit placeholder="s, year, °C, scenario…"></label>
                  <label>Playback FPS<input type="number" min="0.25" max="30" step="0.25" value="4" data-gs-v0780-fps></label>
                </div>
                <div class="sc-gs0780-rotations"><label>XW rotation °<input type="number" min="-3600" max="3600" step="1" value="28" data-gs-v0780-xw></label><label>YW rotation °<input type="number" min="-3600" max="3600" step="1" value="-18" data-gs-v0780-yw></label><label>ZW rotation °<input type="number" min="-3600" max="3600" step="1" value="12" data-gs-v0780-zw></label></div>
                <div class="sc-gs0780-grid"><label><input type="checkbox" data-gs-v0780-slice-enabled> Enable W hyperslice</label><label>Slice center<input type="number" step="any" value="0" data-gs-v0780-slice-center></label><label>Slice tolerance<input type="number" min="0" step="any" value="0.05" data-gs-v0780-slice-tolerance></label><label><input type="checkbox" checked data-gs-v0780-loop> Loop time playback</label></div>
                <p class="sc-gs0780-boundary">v0.78 navigates supplied x/y/z/w records and exact observed time or parameter states. Playback never creates intermediate frames. Parameter scrubbing never interpolates unobserved parameter values. Hyperslicing filters supplied W coordinates; it does not infer a surface, trajectory, forecast, or uncertainty field.</p>
              </section>
              <section class="sc-gs0790-compose" aria-label="Linked views, faceting and figure composition">
                <div class="sc-gs0790-head"><strong>LINKED VIEWS / FACETS / COMPOSITION</strong><span>v0.79 · declared coordination</span></div>
                <div class="sc-gs0790-grid"><label>Facet field<input data-gs-v0790-facet-field placeholder="species, cohort, scenario…"></label><label>Facet columns<input type="number" min="1" max="8" value="3" data-gs-v0790-facet-columns></label><label>Link channel<select data-gs-v0790-link-channel><option value="selection">Selection</option><option value="filter">Filter</option><option value="state-axis">State axis</option></select></label><label>Explicit link key<input data-gs-v0790-link-key placeholder="sample_id"></label><label>Layout<select data-gs-v0790-layout><option value="grid">Grid</option><option value="rows">Rows</option><option value="columns">Columns</option><option value="freeform">Freeform</option></select></label><label><input type="checkbox" checked data-gs-v0790-bidirectional> Bidirectional selection</label></div>
                <div class="sc-gs0470-actions"><button type="button" class="sc-lab-button" data-gs-v0790-example>Load linked-view composition</button><button type="button" class="sc-lab-button" data-gs-v0790-facet>Build facets from current rows</button></div>
                <div class="sc-gs0790-preview" data-gs-v0790-preview><div>2D view</div><div>Diagnostics</div><div>3D scene</div><div>4D state space</div></div>
                <p class="sc-gs0790-boundary">Views coordinate only through declared keys and channels. Lab does not infer joins, statistical coupling, causal relationships, or synthetic panels. Facets retain source-row indexes rather than silently copying or transforming authoritative data. Mixed 2D/3D/4D panels preserve their own renderer and provenance.</p>
              </section>
              <section class="sc-gs0800-spatial" aria-label="Spatial, geospatial and raster controls">
                <div class="sc-gs0800-head"><strong>SPATIAL / GEOSPATIAL / RASTER</strong><span>v0.80 · canvas-spatial · declared CRS</span></div>
                <div class="sc-gs0800-grid">
                  <label>CRS identifier<input data-gs-v0800-crs value="EPSG:4326" placeholder="EPSG:4326, LOCAL:..." /></label>
                  <label>CRS name<input data-gs-v0800-crs-name value="WGS 84 · declared" /></label>
                  <label>Axis order<select data-gs-v0800-axis-order><option value="xy" selected>X / Y</option><option value="yx">Y / X</option></select></label>
                  <label>Coordinate units<input data-gs-v0800-units value="degrees" placeholder="degrees, m, km…" /></label>
                  <label><input type="checkbox" checked data-gs-v0800-geographic /> Geographic coordinates</label>
                  <label>Viewport bounds<input data-gs-v0800-bounds value="-90,-45,90,45" placeholder="minX,minY,maxX,maxY" /></label>
                </div>
                <label>Vector geometry JSON <small>explicit GeoJSON FeatureCollection or layer object</small><textarea rows="8" spellcheck="false" data-gs-v0800-vector></textarea></label>
                <label>Raster grid JSON <small>explicit bounds + values; no interpolation or resampling</small><textarea rows="8" spellcheck="false" data-gs-v0800-raster></textarea></label>
                <div class="sc-gs0470-actions"><button type="button" class="sc-lab-button" data-gs-v0800-example>Load spatial + raster example</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-gs-v0800-build>Build spatial figure</button></div>
                <canvas class="sc-gs0800-canvas" width="960" height="540" data-gs-v0800-canvas aria-label="Spatial scientific canvas"></canvas>
                <details><summary>Spatial figure contract</summary><pre class="sc-gs0800-summary" data-gs-v0800-summary>No spatial figure rendered.</pre></details>
                <p class="sc-gs0800-boundary">v0.80 visualizes supplied geometry and raster cells in their already-declared coordinate reference system. Lab does not silently geocode, infer a CRS, reproject layers, spatially join unrelated records, repair topology, interpolate or resample raster cells, impute nodata, or fetch network basemaps. Bounding-box selection is an explicit display/query operation over supplied feature bounds.</p>
              </section>
              <section class="sc-gs0810-markup" aria-label="Annotation, measurement and scientific markup controls">
                <div class="sc-gs0810-head"><strong>ANNOTATION / MEASUREMENT / SCIENTIFIC MARKUP</strong><span>v0.81 · governed overlay</span></div>
                <div class="sc-gs0810-grid">
                  <label>Coordinate space<select data-gs-v0810-space><option value="screen-normalized" selected>Screen normalized</option><option value="data-2d">Data 2D</option><option value="data-3d">Data 3D</option><option value="state-4d">State 4D</option><option value="projected">Projected spatial</option><option value="geographic">Geographic</option></select></label>
                  <label>Declared units<input data-gs-v0810-units value="unitless" placeholder="m, s, Pa, unitless…" /></label>
                  <label>Markup coordinate bounds<input data-gs-v0810-bounds value="0,0,1,1" placeholder="minX,minY,maxX,maxY" /></label>
                </div>
                <label>Annotations JSON <small>point, label, arrow, line, polyline, region, threshold</small><textarea rows="7" spellcheck="false" data-gs-v0810-annotations></textarea></label>
                <label>Measurements JSON <small>coordinate, distance, polyline-length, angle, planar area</small><textarea rows="7" spellcheck="false" data-gs-v0810-measurements></textarea></label>
                <div class="sc-gs0470-actions"><button type="button" class="sc-lab-button" data-gs-v0810-example>Load scientific markup example</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-gs-v0810-build>Build markup overlay</button></div>
                <canvas class="sc-gs0810-canvas" width="960" height="540" data-gs-v0810-canvas aria-label="Scientific annotation and measurement overlay"></canvas>
                <details><summary>Markup figure contract</summary><pre class="sc-gs0810-summary" data-gs-v0810-summary>No scientific markup rendered.</pre></details>
                <p class="sc-gs0810-boundary">Annotations are review/presentation objects, not observations. Measurements are derived only from explicit markup coordinates and declared units. Lab does not silently convert units, snap geometry, infer uncertainty, create observations, or interpret a mark scientifically. Geographic distance and area are refused until the governed geodesy layer is available.</p>
              </section>

              <section class="sc-gs0820-uncertainty" aria-label="Uncertainty, ensemble and distribution visualization controls">
                <div class="sc-gs0820-head"><strong>UNCERTAINTY / ENSEMBLE / DISTRIBUTION</strong><span>v0.82 · governed semantics</span></div>
                <div class="sc-gs0820-grid">
                  <label>Uncertainty series JSON <small>intervals or quantile ribbons</small><textarea rows="9" spellcheck="false" data-gs-v0820-uncertainty>[]</textarea></label>
                  <label>Distribution JSON <small>explicit empirical samples</small><textarea rows="9" spellcheck="false" data-gs-v0820-distribution></textarea></label>
                  <label>Ensemble JSON <small>explicit members; exact shared states for envelopes</small><textarea rows="9" spellcheck="false" data-gs-v0820-ensemble></textarea></label>
                </div>
                <div class="sc-gs0470-actions"><button type="button" class="sc-lab-button" data-gs-v0820-example>Load uncertainty example</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-gs-v0820-build>Build uncertainty view</button></div>
                <canvas class="sc-gs0820-canvas" width="960" height="540" data-gs-v0820-canvas aria-label="Uncertainty ensemble and distribution visualization"></canvas>
                <details><summary>Uncertainty figure contract</summary><pre class="sc-gs0820-summary" data-gs-v0820-summary>No uncertainty visualization rendered.</pre></details>
                <p class="sc-gs0820-boundary">Intervals retain their declared confidence, credible, prediction, bootstrap, or custom semantics. Distributions are empirical unless the source explicitly says otherwise. Ensemble envelopes require exact shared state coordinates. Lab does not infer uncertainty, fit a parametric distribution, run KDE, silently convert interval meanings, interpolate ensemble members, synthesize samples, or forecast missing states.</p>
              </section>
              <section class="sc-gs0830-provenance" aria-label="Provenance-aware scientific figure controls">
                <div class="sc-gs0830-head"><strong>PROVENANCE-AWARE SCIENTIFIC FIGURES</strong><span>v0.83 · engine 2.10 · tamper-evident lineage</span></div>
                <label>Figure provenance JSON <small>explicit dataset, transformation, model, renderer, state, markup and uncertainty fingerprints</small><textarea rows="13" spellcheck="false" data-gs-v0830-provenance></textarea></label>
                <div class="sc-gs0470-actions"><button type="button" class="sc-lab-button" data-gs-v0830-example>Load provenance example</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-gs-v0830-build>Attach + verify lineage</button></div>
                <p class="sc-gs0830-status" data-gs-v0830-status>Awaiting explicit figure lineage.</p>
                <details><summary>Figure provenance contract</summary><pre class="sc-gs0830-summary" data-gs-v0830-summary>No provenance-aware figure built.</pre></details>
                <p class="sc-gs0830-boundary">v0.83 fingerprints explicit scientific lineage. Lab does not infer missing sources, hide transformations, silently replace fingerprints, repair broken provenance, or describe unverifiable lineage as verified. Export manifests preserve the figure, base-figure and lineage identities.</p>
              </section>
              <label>Dataset rows JSON<textarea data-gs-v0470-rows spellcheck="false"></textarea></label>
              <div class="sc-gs0470-actions"><button type="button" class="sc-lab-button" data-gs-v0470-example>Load bound 2D example</button><button type="button" class="sc-lab-button" data-gs-v0770-example-3d>Load 3D mesh example</button><button type="button" class="sc-lab-button" data-gs-v0730-example-4d>Load bound 4D example</button><button type="button" class="sc-lab-button" data-gs-v0780-example-state>Load time-state example</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-gs-v0470-render>Transform + bind + render</button></div>
            </section>
            <section class="sc-gs0470-card"><h4>Publication metadata</h4>
              <label>Aspect ratio<select data-gs-v0470-aspect><option value="16:9">16:9 landscape</option><option value="3:2">3:2 landscape</option><option value="4:3">4:3 figure</option><option value="1:1">1:1 square</option></select></label>
              <label>Caption<textarea data-gs-v0470-caption placeholder="Concise figure caption"></textarea></label>
              <label>Source<input data-gs-v0470-source placeholder="Dataset, archive, experiment, or source"></label>
              <label>Method<input data-gs-v0470-method placeholder="Method / model / validation note"></label>
              <label>Notes<input data-gs-v0470-notes placeholder="Uncertainty, exclusions, interpretation"></label>
              <label>Tags<input data-gs-v0470-tags placeholder="diagnostics, publication, response-surface"></label>
              <div class="sc-gs0470-checks"><label><input type="checkbox" checked data-gs-v0470-grid> Grid</label><label><input type="checkbox" checked data-gs-v0470-legend> Legend</label></div>
            </section>
            <section class="sc-gs0470-card"><h4>Figure actions</h4><p class="sc-lab-data-note">Every saved v0.83 figure preserves its renderer-aware specification and provenance. Uncertainty layers preserve explicit interval semantics, empirical sample provenance, ensemble-member identity, exact alignment rules, and the authoritative base-figure fingerprint. Scientific markup remains separate from observations. Spatial figures additionally preserve declared CRS, viewport, explicit vector/raster layer fingerprints, nodata policy, and no-reprojection/no-interpolation boundaries. Dataset-bound figures retain transformation/adaptive lineage; 3D scenes retain camera and explicit geometry; 4D state spaces retain source fingerprints, state-axis definitions, projection rotations, observed-state indexes, and no-interpolation boundaries. SVG/PNG/CSV/JSON remain available for 2D; canvas3d and canvas4d use PNG/JSON.</p>
              <div class="sc-gs0470-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-gs-v0470-save>Save figure</button><button type="button" class="sc-lab-button" data-gs-v0470-duplicate>Duplicate draft</button><button type="button" class="sc-lab-button" data-gs-v0470-latest>Open latest graph</button><button type="button" class="sc-lab-button" data-gs-v0470-notebook>Add to notebook</button><button type="button" class="sc-lab-button" data-gs-v0470-report>Send to report</button></div>
            </section>
          </aside>
          <div class="sc-gs0470-workspace">
            <section class="sc-gs0470-canvas-card"><div class="sc-gs0470-canvas-head"><div><span class="sc-lab-section-code">FIGURE / CANVAS</span><h4>Interactive scientific canvas</h4><p>Presentation changes remain separate from the underlying scientific record.</p></div><span class="sc-gs0470-badge" data-gs-v0730-renderer-badge>Engine 2.9 · svg2d / canvas3d / canvas4d / canvas-spatial + scientific-markup + uncertainty-distribution overlays</span></div><div class="sc-gs0470-canvas" data-gs-v0470-canvas></div></section>
            <section class="sc-gs0470-library"><div class="sc-gs0470-library-head"><h4>Project figure library</h4><span><strong data-gs-v0470-figure-count>0</strong> FIGURES</span></div><div class="sc-gs0470-library-list" data-gs-v0470-library></div></section>
            <details><summary>Scientific graph specification</summary><pre class="sc-gs0470-spec" data-gs-v0470-spec>No figure rendered.</pre></details>
          </div>
        </div>
      </section>

      <section class="sc-lab-panel sc-lab-module sc-ms0460" data-lab-module="model-studio" data-module-panel="model-studio" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / MODEL STUDIO / v0.46.0</p><h3>Response Surfaces, Optimization &amp; Design-Space Exploration</h3><p>Fit auditable quadratic response surfaces from bounded experimental factors, inspect coefficient and lack-of-fit evidence, explore constrained design spaces, identify governed optima, and carry the results into the shared interactive scientific graph, dynamic-system, uncertainty, and publication workflows.</p></header>
        <p class="sc-ms0460-status" data-ms-v0460-status role="status" aria-live="polite">Model Studio loading…</p>
        <div class="sc-ms0460-workflow" aria-label="Model Studio workflow"><span>Define</span><span>Fit surface</span><span>Explore</span><span>Optimize</span><span>Diagnose</span><span>Simulate</span><span>Review evidence</span><span>Publish</span><span>Register</span></div>
        <div class="sc-ms0460-safety"><span>NO EVAL</span><span>NO PYTHON</span><span>WHITELISTED FUNCTIONS</span><span>DECLARED SYMBOLS ONLY</span></div>
        <div class="sc-ms0460-grid">
          <section class="sc-ms0460-card"><h4>Model definition</h4>
            <label>Equation template<select data-ms-v0460-template><option value="exponential">Exponential decay</option><option value="linear">Linear screening</option><option value="logistic">Logistic growth</option><option value="michaelis">Michaelis-Menten saturation</option><option value="power">Power law</option></select></label>
            <label>Model title<input data-ms-v0460-title value="Scientific model"></label>
            <label>Model family<select data-ms-v0460-family><option value="declarative-expression">Declarative scientific expression</option><option value="linear-multivariate">Linear multivariate calibration</option><option value="polynomial-univariate">Polynomial univariate calibration</option><option value="exponential-univariate">Exponential univariate calibration</option><option value="logistic-univariate">Logistic univariate calibration</option><option value="registered-model">Registered scientific model</option></select></label>
            <div data-ms-v0460-equation-wrap><label>Scientific equation<input class="sc-ms0460-equation" data-ms-v0460-equation value="y = a * exp(-k*x)" spellcheck="false"></label></div>
            <div class="sc-ms0460-equation-tools" data-ms-v0460-equation-tools><p><strong>Safe grammar:</strong> + − × ÷ ^ and registered functions including exp, log, sqrt, sin, cos, tan, min, max and abs.</p><button type="button" class="sc-lab-button" data-ms-v0460-validate>Validate equation</button><div class="sc-ms0460-validation" data-ms-v0460-equation-validation data-state="idle">Validate the equation to inspect its safe execution contract.</div></div>
            <label data-ms-v0460-registered-wrap hidden>Registered model ID<input data-ms-v0460-registered-model placeholder="model-registry ID or alias"></label>
            <div class="sc-ms0460-inline"><label>Input symbols<input data-ms-v0460-features value="x" placeholder="x,z"></label><label>Output symbol<input data-ms-v0460-response value="y"></label></div>
            <label>Parameter symbols<input data-ms-v0460-parameters value="a,k" placeholder="a,k"></label>
            <label>Parameter preview values<input data-ms-v0460-parameter-values value="a=10,k=0.35" placeholder="a=10,k=0.35"></label>
            <label>Parameter bounds<input data-ms-v0460-parameter-bounds placeholder="a=0:20,k=0:2"></label>
            <label>Scientific constants<input data-ms-v0460-constants placeholder="g=9.80665"></label>
            <label>Initial conditions <small>(metadata for dynamic-system handoff)</small><input data-ms-v0460-initial-conditions placeholder="N=10"></label>
            <div class="sc-ms0460-inline"><label>Primary X unit<input data-ms-v0460-x-unit placeholder="s"></label><label>Y unit<input data-ms-v0460-y-unit placeholder="mg/L"></label></div>
            <label>Dataset registry ID<input data-ms-v0460-dataset-id placeholder="Optional dataset ID"></label>
            <label>Assumptions<textarea data-ms-v0460-assumptions></textarea></label><label>Limitations<textarea data-ms-v0460-limitations></textarea></label>
            <div class="sc-ms0460-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ms-v0460-preview>Evaluate model preview</button><button type="button" class="sc-lab-button" data-ms-v0460-save>Save model definition</button></div>
            <p class="sc-ms0460-note">Algebraic equation previews remain governed by the v0.42 safe grammar. Dynamic-system derivative expressions retain the same v0.45 whitelist. Registered calibration diagnostics remain separate; arbitrary code and arbitrary algebraic-form fitting remain disabled.</p>
          </section>
          <section class="sc-ms0460-card"><h4>Data binding &amp; scientific graph</h4>
            <label>Preview input rows as JSON<textarea data-ms-v0460-rows aria-label="Preview dataset rows"></textarea></label>
            <div class="sc-ms0460-summary" data-ms-v0460-summary></div>
            <div class="sc-ms0460-graph" data-ms-v0460-graph><div class="sc-lab-data-note">Evaluate a model preview to render the scientific equation.</div></div>
            <div class="sc-ms0460-publication"><h4>Publication figure</h4><p>These settings are embedded into exported figures. The graph toolbar provides reset, zoom, pan, SVG, 2× PNG, CSV, JSON, and accessible-table controls.</p><div class="sc-ms0460-inline"><label>Aspect ratio<select data-ms-v0460-publication-aspect><option value="16:9">16:9 landscape</option><option value="3:2">3:2 landscape</option><option value="4:3">4:3 figure</option><option value="1:1">1:1 square</option></select></label><label>Subtitle<input data-ms-v0460-publication-subtitle placeholder="Optional figure subtitle"></label></div><label>Caption<textarea data-ms-v0460-publication-caption placeholder="Concise publication caption"></textarea></label><div class="sc-ms0460-inline"><label>Source<input data-ms-v0460-publication-source placeholder="Dataset, archive, or source"></label><label>Method<input data-ms-v0460-publication-method placeholder="Model / method / validation note"></label></div><label>Notes<input data-ms-v0460-publication-notes placeholder="Uncertainty, exclusions, or interpretation note"></label><div class="sc-ms0460-checks"><label><input type="checkbox" checked data-ms-v0460-publication-grid> Show grid</label><label><input type="checkbox" checked data-ms-v0460-publication-legend> Show legend</label></div><button type="button" class="sc-lab-button" data-ms-v0460-publication-apply>Apply publication settings</button><button type="button" class="sc-lab-button" data-ms-v0460-open-graph-studio>Open in Graph Studio</button></div>
            <details><summary>Evaluated rows</summary><pre class="sc-ms0460-contract sc-ms0460-evaluated" data-ms-v0460-evaluated-rows>No evaluation yet.</pre></details>
            <details><summary>Scientific graph specification</summary><pre class="sc-ms0460-contract" data-ms-v0460-graph-spec>No graph specification yet.</pre></details>
            <h4>Governed handoffs</h4><div class="sc-ms0460-handoffs"><button type="button" class="sc-lab-button" data-ms-v0460-handoff="response-surfaces">Response surfaces</button><button type="button" class="sc-lab-button" data-ms-v0460-handoff="dynamic-systems">Dynamic systems</button><button type="button" class="sc-lab-button" data-ms-v0460-handoff="model-diagnostics">Diagnostics evidence</button><button type="button" class="sc-lab-button" data-ms-v0460-handoff="model-calibration">Calibration</button><button type="button" class="sc-lab-button" data-ms-v0460-handoff="design-studies">Design studies</button><button type="button" class="sc-lab-button" data-ms-v0460-open-probabilistic>Uncertainty &amp; sensitivity</button><button type="button" class="sc-lab-button" data-ms-v0460-handoff="ensemble-uncertainty">Registered-model ensemble</button><button type="button" class="sc-lab-button" data-ms-v0460-handoff="model-registry">Model registry</button></div>
            <section class="sc-mh0490" data-model-handoff-v0490 aria-label="Lab and Workbench model exchange">
              <div class="sc-mh0490__head"><div><span class="sc-lab-section-code">MODEL / EXCHANGE</span><h4>Lab ↔ Workbench model exchange</h4><p>Move the same governed computational model between scientific validation in Lab and interactive exploration in Workbench. The handoff preserves scientific definition and provenance without enabling arbitrary code.</p></div><span class="sc-mh0490__contract">CONTRACT 0.49.0</span></div>
              <div class="sc-mh0490__preserves" aria-label="Preserved model fields"><span>Equation</span><span>Variables + units</span><span>Parameters + bounds</span><span>Initial conditions</span><span>Dataset bindings</span><span>Assumptions</span><span>Provenance</span></div>
              <div class="sc-mh0490__pending" data-mh-v0490-pending data-state="idle"><strong>NO PENDING WORKBENCH MODEL</strong><span>Send a model back from Workbench to make it available here.</span></div>
              <div class="sc-mh0490__actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-mh-v0490-send>Open model in Workbench</button><button type="button" class="sc-lab-button" data-mh-v0490-prepare>Prepare handoff only</button><button type="button" class="sc-lab-button" data-mh-v0490-import>Import pending Workbench model</button><button type="button" class="sc-lab-button" data-mh-v0490-download>Download shared model</button><button type="button" class="sc-lab-button" data-mh-v0490-clear>Clear pending</button></div>
              <p class="sc-mh0490__status" data-mh-v0490-status role="status" aria-live="polite">Shared Lab ↔ Workbench model contract loading…</p>
              <details><summary>Shared computational model handoff</summary><pre data-mh-v0490-contract>No Workbench handoff prepared.</pre></details>
            </section>
            <section class="sc-rmp0500" data-reproducible-model-package-v0500 aria-label="Reproducible model package and research bundle">
              <div class="sc-rmp0500__head"><div><span class="sc-lab-section-code">MODEL / REPRODUCIBILITY</span><h4>Reproducible model package</h4><p>Freeze the shared computational model together with its dataset reference or snapshot, methods, results, figures, environment, assumptions, limitations, and provenance. Packages are content-hashed, independently verifiable, portable as JSON or a research ZIP, and can be registered as immutable model versions.</p></div><span class="sc-rmp0500__contract">PACKAGE 0.50.0</span></div>
              <div class="sc-rmp0500__controls"><label>Model version<input data-rmp-v0500-version value="1.0.0" aria-label="Semantic model version"></label><p class="sc-lab-data-note">Registry versions are immutable. If scientific content changes after registration, choose a new semantic version.</p></div>
              <div class="sc-rmp0500__summary" aria-label="Package summary"><article><span>Models</span><strong data-rmp-v0500-models>0</strong></article><article><span>Dataset</span><strong data-rmp-v0500-dataset>none</strong></article><article><span>Results</span><strong data-rmp-v0500-results>0</strong></article><article><span>Figures</span><strong data-rmp-v0500-figures>0</strong></article><article><span>Package hash</span><strong data-rmp-v0500-hash>—</strong></article></div>
              <div class="sc-rmp0500__actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-rmp-v0500-build>Build package</button><button type="button" class="sc-lab-button" data-rmp-v0500-verify>Verify package</button><button type="button" class="sc-lab-button" data-rmp-v0500-download>Download JSON</button><button type="button" class="sc-lab-button" data-rmp-v0500-bundle>Download research ZIP</button><button type="button" class="sc-lab-button" data-rmp-v0500-register>Register model version</button><button type="button" class="sc-lab-button" data-rmp-v0500-registry>Open model registry</button></div>
              <p class="sc-rmp0500__status" data-rmp-v0500-status role="status" aria-live="polite">Reproducible model package workspace loading…</p>
              <details><summary>Package record and verification</summary><pre data-rmp-v0500-record>No reproducible model package built.</pre></details>
            </section>
            <details><summary>Model contract</summary><pre class="sc-ms0460-contract" data-ms-v0460-contract>No model contract yet.</pre></details>
          </section>

          <section class="sc-ms0510" data-advanced-statistical-modeling-v0510 aria-label="Advanced statistical modeling and generalized regression">
            <div class="sc-ms0510__head"><div><span class="sc-lab-section-code">MODEL / STATISTICS</span><h4>Advanced statistical modeling &amp; generalized regression</h4><p>Fit multivariable Gaussian regressions, robust and regularized models, binomial and Poisson generalized linear models, and cubic splines. Validation, coefficient evidence, scientific figures, and candidate comparison stay connected to the active Lab project and reproducible-model workflow.</p></div><span class="sc-ms0510__contract">STATISTICS 0.51.0</span></div>
            <div class="sc-ms0510__layout">
              <div class="sc-ms0510__controls">
                <label>Study title<input data-stats-v0510-title value="Advanced statistical model"></label>
                <div class="sc-ms0510__inline"><label>Response family<select data-stats-v0510-family><option value="gaussian">Gaussian</option><option value="binomial-logit">Binomial · logit</option><option value="poisson-log">Poisson · log</option></select></label><label>Estimator<select data-stats-v0510-estimator><option value="ols">OLS</option></select></label></div>
                <div class="sc-ms0510__inline"><label>Model type<select data-stats-v0510-model-type><option value="linear">Linear</option><option value="cubic-spline">Cubic spline</option></select></label><label>Weight column<input data-stats-v0510-weight placeholder="WLS only"></label></div>
                <label>Feature columns <small>comma separated</small><input data-stats-v0510-features value="x,z"></label>
                <div class="sc-ms0510__inline"><label>Response column<input data-stats-v0510-response value="y"></label><label>Spline feature<input data-stats-v0510-spline-feature value="x"></label></div>
                <div class="sc-ms0510__inline"><label>Regularization α<input type="number" step="any" min="0" value="0.2" data-stats-v0510-alpha></label><label>Elastic-net L1 ratio<input type="number" step="0.05" min="0" max="1" value="0.5" data-stats-v0510-l1-ratio></label></div>
                <div class="sc-ms0510__inline"><label>Interior spline knots<input type="number" min="0" max="12" value="4" data-stats-v0510-knots></label><label class="sc-ms0510__check"><input type="checkbox" data-stats-v0510-standardize> Standardize design columns</label></div>
                <label>Dataset rows as JSON<textarea data-stats-v0510-rows spellcheck="false">[]</textarea></label>
                <div class="sc-ms0510__actions"><button type="button" class="sc-lab-button" data-stats-v0510-example>Load statistical example</button><button type="button" class="sc-lab-button" data-stats-v0510-current>Use current Model Studio rows</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-stats-v0510-fit>Fit model</button></div>
                <div class="sc-ms0510__inline"><label>CV folds<input type="number" min="2" max="20" value="5" data-stats-v0510-folds></label><label>Repeats<input type="number" min="1" max="10" value="1" data-stats-v0510-repeats></label></div>
                <label>Validation seed<input type="number" value="42" data-stats-v0510-seed></label>
                <div class="sc-ms0510__actions"><button type="button" class="sc-lab-button" data-stats-v0510-validate>Cross-validate</button><button type="button" class="sc-lab-button" data-stats-v0510-compare>Compare baseline / robust / regularized</button><button type="button" class="sc-lab-button" data-stats-v0510-save>Save evidence</button></div>
                <p class="sc-ms0510__status" data-stats-v0510-status role="status" aria-live="polite">Advanced statistical modeling loading…</p>
                <p class="sc-ms0510__boundary"><strong>Scientific boundary.</strong> Model coefficients describe associations under the declared model and data. Lab does not infer causality, automatically select features, execute arbitrary formulas, or attach classical p-values to regularized or Huber estimates.</p>
              </div>
              <div class="sc-ms0510__evidence">
                <div class="sc-ms0510__summary" data-stats-v0510-summary></div>
                <div class="sc-ms0510__graph-tabs" aria-label="Statistical figure selector"><button type="button" data-stats-v0510-graph="observedPredicted" aria-pressed="true">Observed / predicted</button><button type="button" data-stats-v0510-graph="residualVsFitted" aria-pressed="false">Residuals</button><button type="button" data-stats-v0510-graph="coefficients" aria-pressed="false">Coefficients</button><button type="button" data-stats-v0510-graph="splineCurve" aria-pressed="false">Spline</button><button type="button" class="sc-lab-button" data-stats-v0510-graph-studio>Open figure in Graph Studio</button></div>
                <div class="sc-ms0510__canvas" data-stats-v0510-canvas><div class="sc-lab-data-note">Fit a statistical model to generate scientific figures.</div></div>
                <div class="sc-ms0510__table" data-stats-v0510-coefficients></div>
                <div class="sc-ms0510__table" data-stats-v0510-comparison></div>
                <details><summary>Statistical model / validation record</summary><pre data-stats-v0510-record>No advanced statistical result yet.</pre></details>
              </div>
            </div>
          </section>

          <section class="sc-bayes0520" data-bayesian-inference-v0520 aria-label="Bayesian inference, posterior diagnostics, and posterior predictive modeling">
            <div class="sc-bayes0520__head"><div><span class="sc-lab-section-code">MODEL / BAYESIAN</span><h4>Bayesian inference, posterior diagnostics &amp; posterior predictive modeling</h4><p>Estimate posterior distributions for Gaussian, binomial-logit, and Poisson-log regression models with explicit priors, multi-chain sampling, diagnostic review, credible intervals, and posterior-predictive checks. Bayesian evidence remains connected to the active project, Graph Studio, and reproducible-model packages.</p></div><span class="sc-bayes0520__contract">BAYESIAN 0.52.0</span></div>
            <div class="sc-bayes0520__layout">
              <div class="sc-bayes0520__controls">
                <label>Study title<input data-bayes-v0520-title value="Bayesian model"></label>
                <div class="sc-bayes0520__inline"><label>Response family<select data-bayes-v0520-family><option value="gaussian">Gaussian</option><option value="binomial-logit">Binomial · logit</option><option value="poisson-log">Poisson · log</option></select></label><label>Model type<select data-bayes-v0520-model-type><option value="linear">Linear</option><option value="cubic-spline">Cubic spline</option></select></label></div>
                <label>Feature columns <small>comma separated</small><input data-bayes-v0520-features value="x,z"></label>
                <div class="sc-bayes0520__inline"><label>Response column<input data-bayes-v0520-response value="y"></label><label>Credible level<input type="number" min="0.5" max="0.999" step="0.001" value="0.95" data-bayes-v0520-credible></label></div>
                <div class="sc-bayes0520__inline"><label>Spline feature<input data-bayes-v0520-spline-feature value="x"></label><label>Interior knots<input type="number" min="0" max="12" value="3" data-bayes-v0520-knots></label></div>
                <label class="sc-bayes0520__check"><input type="checkbox" checked data-bayes-v0520-standardize> Standardize design columns</label>
                <h5>Priors</h5>
                <div class="sc-bayes0520__inline"><label>Intercept mean<input type="number" step="any" value="0" data-bayes-v0520-intercept-mean></label><label>Intercept SD<input type="number" step="any" min="0.000001" value="10" data-bayes-v0520-intercept-sd></label></div>
                <div class="sc-bayes0520__inline"><label>Coefficient mean<input type="number" step="any" value="0" data-bayes-v0520-coef-mean></label><label>Coefficient SD<input type="number" step="any" min="0.000001" value="2.5" data-bayes-v0520-coef-sd></label></div>
                <div class="sc-bayes0520__inline"><label>Residual variance prior shape<input type="number" step="any" min="0.000001" value="2" data-bayes-v0520-sigma-shape></label><label>Residual variance prior scale<input type="number" step="any" min="0.000001" value="2" data-bayes-v0520-sigma-scale></label></div>
                <h5>Sampler</h5>
                <div class="sc-bayes0520__inline"><label>Chains<input type="number" min="2" max="8" value="4" data-bayes-v0520-chains></label><label>Posterior draws / chain<input type="number" min="50" max="4000" value="800" data-bayes-v0520-draws></label></div>
                <div class="sc-bayes0520__inline"><label>Warmup / chain<input type="number" min="0" max="3000" value="500" data-bayes-v0520-warmup></label><label>Seed<input type="number" value="42" data-bayes-v0520-seed></label></div>
                <div class="sc-bayes0520__inline"><label>Metropolis proposal scale<input type="number" min="0.02" max="20" step="0.05" value="1" data-bayes-v0520-proposal-scale></label><label>Target acceptance<input type="number" min="0.1" max="0.7" step="0.01" value="0.28" data-bayes-v0520-target-accept></label></div>
                <label>Posterior-predictive draws<input type="number" min="20" max="1200" value="300" data-bayes-v0520-ppc-draws></label>
                <label>Dataset rows as JSON<textarea data-bayes-v0520-rows spellcheck="false">[]</textarea></label>
                <div class="sc-bayes0520__actions"><button type="button" class="sc-lab-button" data-bayes-v0520-example>Load Bayesian example</button><button type="button" class="sc-lab-button" data-bayes-v0520-use-stats>Use v0.51 statistical setup</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-bayes-v0520-fit>Sample posterior</button></div>
                <div class="sc-bayes0520__actions"><button type="button" class="sc-lab-button" data-bayes-v0520-predict>Posterior predictive</button><button type="button" class="sc-lab-button" data-bayes-v0520-save>Save Bayesian evidence</button></div>
                <p class="sc-bayes0520__status" data-bayes-v0520-status role="status" aria-live="polite">Bayesian modeling loading…</p>
                <p class="sc-bayes0520__boundary"><strong>Scientific boundary.</strong> Posterior claims are conditional on the declared model, data, priors, and sampler. Split-R̂, ESS, MCSE, acceptance rates, trace plots, and posterior-predictive checks are review evidence—not an automatic convergence certificate. Lab does not select priors automatically, infer causality, execute arbitrary code, or claim that a posterior distribution proves a real-world mechanism.</p>
              </div>
              <div class="sc-bayes0520__evidence">
                <div class="sc-bayes0520__summary" data-bayes-v0520-summary></div>
                <div class="sc-bayes0520__graph-tabs" aria-label="Bayesian figure selector"><button type="button" data-bayes-v0520-graph="posteriorPredictive" aria-pressed="true">Posterior predictive</button><button type="button" data-bayes-v0520-graph="coefficientIntervals" aria-pressed="false">Credible intervals</button><button type="button" data-bayes-v0520-graph="trace" aria-pressed="false">Trace</button><button type="button" data-bayes-v0520-graph="predictiveSummary" aria-pressed="false">Predictive summary</button><button type="button" class="sc-lab-button" data-bayes-v0520-graph-studio>Open figure in Graph Studio</button></div>
                <div class="sc-bayes0520__canvas" data-bayes-v0520-canvas><div class="sc-lab-data-note">Fit a Bayesian model to generate posterior and predictive figures.</div></div>
                <h5>Posterior summary</h5><div class="sc-bayes0520__table" data-bayes-v0520-posterior></div>
                <h5>Chain diagnostics</h5><div class="sc-bayes0520__table" data-bayes-v0520-diagnostics></div>
                <details><summary>Bayesian model / posterior record</summary><pre data-bayes-v0520-record>No Bayesian result yet.</pre></details>
              </div>
            </div>
          </section>

          <section class="sc-ms0460-card sc-ms0460-diagnostics-card"><h4>Diagnostics &amp; model evidence</h4>
            <p>Fit registered model forms against observed response values, inspect residual behavior, estimate out-of-sample performance, and compare alternatives using the same deterministic validation policy.</p>
            <div class="sc-ms0460-diagnostic-controls">
              <label>Validation model form<select data-ms-v0460-validation-model><option value="linear-multivariate">Linear multivariate</option><option value="polynomial-univariate">Polynomial univariate</option><option value="exponential-univariate">Exponential univariate</option><option value="logistic-univariate">Logistic univariate</option></select></label>
              <label>Objective<select data-ms-v0460-objective><option value="least-squares">Least squares</option><option value="weighted-least-squares">Weighted least squares</option><option value="robust-huber">Robust Huber</option><option value="robust-soft-l1">Robust soft-L1</option></select></label>
              <label>Polynomial degree<input type="number" min="1" max="5" value="2" data-ms-v0460-degree></label>
              <label>Folds<input type="number" min="2" max="20" value="5" data-ms-v0460-folds></label>
              <label>Repeats<input type="number" min="1" max="10" value="1" data-ms-v0460-repeats></label>
              <label>Seed<input type="number" value="42" data-ms-v0460-seed></label>
            </div>
            <div class="sc-ms0460-actions"><button type="button" class="sc-lab-button" data-ms-v0460-diagnostics-example>Load diagnostics example</button><button type="button" class="sc-lab-button" data-ms-v0460-run-diagnostics>Run diagnostics</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-ms-v0460-run-cv>Run cross-validation</button></div>
            <div class="sc-ms0460-summary sc-ms0460-diagnostic-summary" data-ms-v0460-diagnostic-summary><article><span>RMSE</span><strong>—</strong></article><article><span>MAE</span><strong>—</strong></article><article><span>R²</span><strong>—</strong></article><article><span>AICc</span><strong>—</strong></article><article><span>CV RMSE</span><strong>—</strong></article><article><span>CV ± SD</span><strong>—</strong></article></div>
            <div class="sc-ms0460-diagnostic-graphs">
              <div class="sc-ms0460-graph" data-ms-v0460-observed-graph><div class="sc-lab-data-note">Observed vs predicted appears after diagnostics.</div></div>
              <div class="sc-ms0460-graph" data-ms-v0460-residual-graph><div class="sc-lab-data-note">Residuals vs fitted appears after diagnostics.</div></div>
              <div class="sc-ms0460-graph" data-ms-v0460-qq-graph><div class="sc-lab-data-note">Normal Q–Q diagnostic appears after diagnostics.</div></div>
              <div class="sc-ms0460-graph" data-ms-v0460-cv-graph><div class="sc-lab-data-note">Fold RMSE appears after cross-validation.</div></div>
            </div>
            <details><summary>Diagnostics / validation record</summary><pre class="sc-ms0460-contract" data-ms-v0460-diagnostic-record>No diagnostics record yet.</pre></details>
            <hr>
            <h4>Scientific model comparison</h4>
            <p>Select two or more registered forms. Lab evaluates each candidate with the same folds, repeats, seed, response, features, and dataset, then ranks primarily by mean validation RMSE with AICc and BIC as tie-breakers.</p>
            <label>Candidate model forms<select multiple size="4" data-ms-v0460-comparison-models><option value="linear-multivariate" selected>Linear multivariate</option><option value="polynomial-univariate" selected>Polynomial univariate</option><option value="exponential-univariate">Exponential univariate</option><option value="logistic-univariate">Logistic univariate</option></select></label>
            <div class="sc-ms0460-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ms-v0460-compare>Compare selected models</button></div>
            <div class="sc-ms0460-graph" data-ms-v0460-comparison-graph><div class="sc-lab-data-note">Cross-validation comparison appears here.</div></div>
            <div class="sc-ms0460-comparison-table" data-ms-v0460-comparison-table></div>
            <details><summary>Model comparison record</summary><pre class="sc-ms0460-contract" data-ms-v0460-comparison-record>No model comparison yet.</pre></details>
          </section>

          <section class="sc-ms0460-card sc-ms0460-surface-card"><h4>Response surfaces, optimization &amp; design-space exploration</h4>
            <p>Fit a full second-order response surface in coded factor space, including linear terms, quadratic curvature, and all two-factor interactions. Lab reports coefficient uncertainty, design-matrix conditioning, information criteria, and a replicated-point lack-of-fit test when the experimental design provides pure-error degrees of freedom.</p>
            <div class="sc-ms0460-surface-grid">
              <div>
                <label>Study title<input data-ms-v0460-surface-title value="Catalyst yield response surface"></label>
                <label>Factor bounds <small>one per line: symbol=low:high[:unit]</small><textarea data-ms-v0460-surface-factors spellcheck="false">T=20:80:C
P=1:9:bar</textarea></label>
                <div class="sc-ms0460-inline"><label>Response symbol<input data-ms-v0460-surface-response value="Yield"></label><label>Response unit<input data-ms-v0460-surface-response-unit value="%"></label></div>
                <label>Experimental rows as JSON<textarea data-ms-v0460-surface-rows aria-label="Response surface experimental rows">[]</textarea></label>
                <div class="sc-ms0460-actions"><button type="button" class="sc-lab-button" data-ms-v0460-surface-example>Load response-surface example</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-ms-v0460-surface-fit>Fit quadratic surface</button></div>
                <hr><h4>Explore bounded design space</h4>
                <div class="sc-ms0460-inline"><label>X factor<input data-ms-v0460-surface-x value="T"></label><label>Y factor<input data-ms-v0460-surface-y value="P"></label></div>
                <label>Other fixed factors <small>symbol=value, comma-separated</small><input data-ms-v0460-surface-fixed placeholder="C=0.5"></label>
                <div class="sc-ms0460-inline"><label>Response minimum<input type="number" step="any" data-ms-v0460-surface-min value="90"></label><label>Response maximum<input type="number" step="any" data-ms-v0460-surface-max placeholder="Optional"></label></div>
                <label>Grid points per axis<input type="number" min="9" max="81" value="31" data-ms-v0460-surface-grid></label>
                <button type="button" class="sc-lab-button" data-ms-v0460-surface-explore>Explore response surface</button>
                <hr><h4>Bounded optimization</h4>
                <div class="sc-ms0460-inline"><label>Goal<select data-ms-v0460-surface-goal><option value="maximize">Maximize response</option><option value="minimize">Minimize response</option><option value="target">Reach target response</option></select></label><label>Target<input type="number" step="any" data-ms-v0460-surface-target placeholder="Required for target"></label></div>
                <div class="sc-ms0460-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ms-v0460-surface-optimize>Optimize within bounds</button><button type="button" class="sc-lab-button" data-ms-v0460-surface-save>Save design-space evidence</button></div>
                <div class="sc-ms0460-dynamic-note"><strong>v0.46 boundary</strong>Optimization is restricted to the declared continuous factor bounds and the fitted quadratic surface. Lab does not extrapolate beyond the design region and does not yet perform mixed-integer or multi-response desirability optimization.</div>
              </div>
              <div>
                <div class="sc-ms0460-summary" data-ms-v0460-surface-summary><article><span>R²</span><strong>—</strong></article><article><span>RMSE</span><strong>—</strong></article><article><span>LOF p</span><strong>—</strong></article><article><span>Feasible</span><strong>—</strong></article><article><span>Optimum</span><strong>—</strong></article><article><span>Boundary</span><strong>—</strong></article></div>
                <div class="sc-ms0460-surface-graphs"><div class="sc-ms0460-graph" data-ms-v0460-surface-heatmap><div class="sc-lab-data-note">The bounded response-surface heatmap appears after design-space exploration.</div></div><div class="sc-ms0460-graph" data-ms-v0460-surface-fit-graph><div class="sc-lab-data-note">Observed-versus-predicted evidence appears after surface fitting.</div></div><div class="sc-ms0460-graph" data-ms-v0460-surface-residual-graph><div class="sc-lab-data-note">Response-surface residuals appear after fitting.</div></div><div class="sc-ms0460-graph" data-ms-v0460-surface-coefficient-graph><div class="sc-lab-data-note">Coded coefficient influence appears after fitting.</div></div></div>
                <details><summary>Response-surface / design-space record</summary><pre class="sc-ms0460-contract" data-ms-v0460-surface-record>No response-surface record yet.</pre></details>
              </div>
            </div>
          </section>

          <section class="sc-ms0460-card sc-ms0460-dynamic-card"><h4>Dynamic systems &amp; ODE parameter estimation</h4>
            <p>Build deterministic coupled ordinary differential equation systems with declared states, bounded parameters, explicit initial conditions, and a governed solver. Derivative expressions reuse the safe v0.42 scientific grammar; no Python or arbitrary code is executed.</p>
            <div class="sc-ms0460-dynamic-grid">
              <div class="sc-ms0460-dynamic-controls">
                <label>Dynamic-system template<select data-ms-v0460-dynamic-template><option value="exponential">Exponential decay</option><option value="logistic">Logistic growth</option><option value="sir">SIR compartment model</option><option value="predator">Predator-prey</option></select></label>
                <label>System title<input data-ms-v0460-dynamic-title value="Exponential decay ODE"></label>
                <div class="sc-ms0460-inline"><label>Independent variable<input data-ms-v0460-dynamic-time-symbol value="t"></label><label>Time unit<input data-ms-v0460-dynamic-time-unit value="s"></label></div>
                <label>State initial conditions <small>symbol=value</small><input data-ms-v0460-dynamic-states value="X=10" placeholder="S=990,I=10,R=0"></label>
                <label>State units <small>optional symbol=unit</small><input data-ms-v0460-dynamic-state-units placeholder="S=people,I=people,R=people"></label>
                <label>Parameter starting values <small>symbol=value</small><input data-ms-v0460-dynamic-parameters value="k=0.2"></label>
                <label>Parameter bounds <small>symbol=lower:upper</small><input data-ms-v0460-dynamic-bounds value="k=0:2"></label>
                <label>Fixed parameter symbols <small>comma-separated; otherwise estimated</small><input data-ms-v0460-dynamic-fixed placeholder=""></label>
                <label>Scientific constants <small>symbol=value</small><input data-ms-v0460-dynamic-constants placeholder="Pop=1000"></label>
                <label>Derivative equations <small>one per line as State: expression</small><textarea class="sc-ms0460-ode-equations" data-ms-v0460-dynamic-equations spellcheck="false">X: -k*X</textarea></label>
                <div class="sc-ms0460-parameter-controls"><label>Start<input type="number" step="any" value="0" data-ms-v0460-dynamic-start></label><label>End<input type="number" step="any" value="5" data-ms-v0460-dynamic-end></label><label>Points<input type="number" min="2" max="5000" value="201" data-ms-v0460-dynamic-points></label><label>Solver<select data-ms-v0460-dynamic-solver><option>RK45</option><option>RK23</option><option>DOP853</option><option>Radau</option><option>BDF</option><option>LSODA</option></select></label></div>
                <div class="sc-ms0460-inline"><label>Relative tolerance<input type="number" step="any" value="0.000001" data-ms-v0460-dynamic-rtol></label><label>Absolute tolerance<input type="number" step="any" value="0.000000001" data-ms-v0460-dynamic-atol></label></div>
                <div class="sc-ms0460-actions"><button type="button" class="sc-lab-button" data-ms-v0460-dynamic-normalize>Validate ODE system</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-ms-v0460-dynamic-simulate>Simulate trajectories</button><button type="button" class="sc-lab-button" data-ms-v0460-dynamic-save>Save dynamic evidence</button></div>
                <div class="sc-ms0460-dynamic-note"><strong>v0.45 boundary</strong>ODE events, delay differential equations, stochastic differential equations, and PDEs are not executed in this release. This foundation is deterministic ODE modeling with bounded parameter estimation.</div>
              </div>
              <div>
                <div class="sc-ms0460-summary" data-ms-v0460-dynamic-summary><article><span>States</span><strong>—</strong></article><article><span>Parameters</span><strong>—</strong></article><article><span>Solver</span><strong>—</strong></article><article><span>Trajectory points</span><strong>—</strong></article><article><span>Fit RMSE</span><strong>—</strong></article><article><span>Identifiability</span><strong>—</strong></article></div>
                <div class="sc-ms0460-dynamic-graphs"><div class="sc-ms0460-graph" data-ms-v0460-dynamic-trajectory><div class="sc-lab-data-note">State trajectories appear after ODE simulation.</div></div><div class="sc-ms0460-graph" data-ms-v0460-dynamic-phase><div class="sc-lab-data-note">Phase portrait appears for systems with two or more states.</div></div></div>
                <hr><h4>Estimate parameters from observations</h4>
                <p>Bind observations by the independent-variable symbol and one or more state symbols. Lab estimates only parameters not marked fixed, respects configured bounds, and reports local Jacobian identifiability evidence.</p>
                <div class="sc-ms0460-inline"><label>Observed states<input data-ms-v0460-dynamic-observed-states value="X" placeholder="S,I,R"></label><label>Robust loss<select data-ms-v0460-dynamic-loss><option value="linear">Linear least squares</option><option value="soft_l1">Soft-L1</option><option value="huber">Huber</option><option value="cauchy">Cauchy</option><option value="arctan">Arctan</option></select></label></div>
                <div class="sc-ms0460-inline"><label>Robust f-scale<input type="number" step="any" min="0.000001" value="1" data-ms-v0460-dynamic-fscale></label><label>Max evaluations<input type="number" min="10" max="4000" value="1000" data-ms-v0460-dynamic-max-evals></label></div>
                <label>Observed rows as JSON<textarea class="sc-ms0460-observations" data-ms-v0460-dynamic-observations aria-label="Dynamic system observation rows">[]</textarea></label>
                <div class="sc-ms0460-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ms-v0460-dynamic-estimate>Estimate bounded parameters</button></div>
                <div class="sc-ms0460-dynamic-graphs"><div class="sc-ms0460-graph" data-ms-v0460-dynamic-fit><div class="sc-lab-data-note">Observed vs fitted trajectories appear after parameter estimation.</div></div><div class="sc-ms0460-graph" data-ms-v0460-dynamic-residual><div class="sc-lab-data-note">Parameter-estimation residuals appear here.</div></div></div>
                <details><summary>Dynamic-system / estimation record</summary><pre class="sc-ms0460-contract" data-ms-v0460-dynamic-record>No dynamic-system record yet.</pre></details>
              </div>
            </div>

            <details class="sc-ds0540" data-ds-v0540-root>
              <summary>Dynamic Systems II — events, regimes, bifurcation &amp; phase analysis <small>v0.54.0</small></summary>
              <p class="sc-ds0540__intro">Extend the governed ODE definition above with safe event functions, evidence-backed scheduled regime changes, bounded numerical parameter sweeps, and two-state autonomous phase-plane diagnostics. These tools remain deterministic and declarative; no arbitrary Python or executable callbacks are accepted.</p>
              <p data-ds-v0540-status role="status" aria-live="polite">Dynamic Systems II ready. Configure the base ODE above, then add advanced analysis only where scientifically appropriate.</p>
              <div class="sc-ds0540__grid">
                <div class="sc-ds0540__controls">
                  <label>Events as JSON <small>expression is zero at the event; direction -1, 0, or 1</small><textarea data-ds-v0540-events spellcheck="false">[]</textarea></label>
                  <label>Scheduled regime changes as JSON <small>time + parameterValues and/or stateValues + evidence</small><textarea data-ds-v0540-regimes spellcheck="false">[]</textarea></label>
                  <div class="sc-ds0540__actions"><button type="button" class="sc-lab-button" data-ds-v0540-example>Load advanced example controls</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-ds-v0540-simulate>Simulate events &amp; regimes</button></div>
                  <hr><h5>Numerical bifurcation scan</h5>
                  <div class="sc-ds0540__inline"><label>Parameter<input data-ds-v0540-sweep-parameter placeholder="r"></label><label>State<input data-ds-v0540-sweep-state placeholder="N"></label></div>
                  <div class="sc-ds0540__inline"><label>Lower<input type="number" step="any" data-ds-v0540-sweep-lower value="0.1"></label><label>Upper<input type="number" step="any" data-ds-v0540-sweep-upper value="1"></label></div>
                  <div class="sc-ds0540__inline"><label>Parameter points<input type="number" min="3" max="121" value="41" data-ds-v0540-sweep-points></label><label>Transient fraction<input type="number" min="0.25" max="0.97" step="0.05" value="0.7" data-ds-v0540-transient></label></div>
                  <button type="button" class="sc-lab-button" data-ds-v0540-bifurcation>Run numerical bifurcation scan</button>
                  <hr><h5>Advanced two-state phase analysis</h5>
                  <label>Phase domain JSON<textarea data-ds-v0540-phase-domain spellcheck="false">{
  "x": {"min": 0, "max": 10, "points": 25},
  "y": {"min": 0, "max": 10, "points": 25}
}</textarea></label>
                  <button type="button" class="sc-lab-button" data-ds-v0540-phase>Analyze phase plane</button>
                  <div class="sc-ds0540__note"><strong>Scientific boundary</strong>Numerical sweeps can reveal candidate regime transitions but are not formal bifurcation proofs. Equilibrium stability is local numerical evidence. Delay equations, SDEs, PDEs, automatic regime inference, and automatic control actions remain outside this release.</div>
                </div>
                <div class="sc-ds0540__evidence">
                  <div class="sc-ds0540__summary" data-ds-v0540-summary><article><span>Evidence</span><strong>—</strong></article><article><span>Events</span><strong>—</strong></article><article><span>Regimes</span><strong>—</strong></article><article><span>Equilibria</span><strong>—</strong></article><article><span>Solver</span><strong>—</strong></article><article><span>Review</span><strong>required</strong></article></div>
                  <div class="sc-ds0540__canvas" data-ds-v0540-canvas><div class="sc-lab-data-note">Run an event/regime simulation, numerical bifurcation scan, or phase analysis to generate scientific evidence.</div></div>
                  <div class="sc-ds0540__actions"><button type="button" class="sc-lab-button" data-ds-v0540-graph-studio>Open current figure in Graph Studio</button><button type="button" class="sc-lab-button" data-ds-v0540-save>Save Dynamic Systems II evidence</button></div>
                  <details><summary>Dynamic Systems II record</summary><pre data-ds-v0540-record>No v0.54 analysis yet.</pre></details>
                </div>
              </div>
            </details>
          </section>
        </div>
      </section>

      <section class="sc-lab-panel sc-cal0302" data-lab-module="model-calibration" data-module-panel="model-calibration" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / MODEL CALIBRATION / v0.30.2</p><h3>Scientific model calibration and validation</h3><p>Fit registered scientific model forms to project datasets, reserve holdout observations, inspect residuals and parameter uncertainty, compare models, and preserve calibration provenance.</p></header>
        <p data-cal-v0302-status role="status" aria-live="polite">Model calibration loading…</p>
        <div class="sc-cal0302-metrics" data-cal-v0302-metrics></div>
        <div class="sc-cal0302-grid"><div class="sc-cal0302-card">
          <input type="hidden" data-cal-v0302-study-id>
          <label>Study title<input data-cal-v0302-title value="Scientific model calibration"></label>
          <label>Model form<select data-cal-v0302-model><option value="linear-multivariate">Linear multivariate</option><option value="polynomial-univariate">Polynomial univariate</option><option value="exponential-univariate">Exponential univariate</option><option value="logistic-univariate">Logistic univariate</option></select></label>
          <label>Feature columns<input data-cal-v0302-features value="x"></label><label>Response column<input data-cal-v0302-response value="y"></label>
          <label>Objective<select data-cal-v0302-objective><option value="least-squares">Least squares</option><option value="weighted-least-squares">Weighted least squares</option><option value="robust-huber">Robust Huber</option><option value="robust-soft-l1">Robust soft L1</option></select></label>
          <label>Weight column<input data-cal-v0302-weight></label><label>Polynomial degree<input type="number" min="1" max="5" value="2" data-cal-v0302-degree></label>
          <label>Holdout fraction<input type="number" min="0" max="0.5" step="0.05" value="0.2" data-cal-v0302-holdout></label><label>Random seed<input type="number" value="42" data-cal-v0302-seed></label>
          <label>Dataset registry ID<input data-cal-v0302-dataset-id></label><label>Experiment protocol ID<input data-cal-v0302-protocol-id></label><label>Design study ID<input data-cal-v0302-design-id></label><label>Limitations and notes<textarea data-cal-v0302-notes></textarea></label>
        </div><div class="sc-cal0302-card"><label>Dataset rows as JSON<textarea data-cal-v0302-rows placeholder='[{"x":1,"y":3}]'></textarea></label><div class="sc-cal0302-actions"><button class="sc-lab-button" data-cal-v0302-sample>Load example</button><button class="sc-lab-button sc-lab-button-primary" data-cal-v0302-run>Calibrate and validate</button></div><label>Saved results<select multiple size="6" data-cal-v0302-results></select></label><div class="sc-cal0302-actions"><button class="sc-lab-button" data-cal-v0302-compare>Compare selected</button><button class="sc-lab-button" data-cal-v0302-report>Build report</button><button class="sc-lab-button" data-cal-v0302-export>Export bundle</button></div></div></div>
        <div class="sc-cal0302-card"><h4>Calibration output</h4><pre data-cal-v0302-output>Run a governed calibration to inspect parameters, confidence intervals, residuals, holdout metrics, and provenance.</pre></div>
      </section>




      <section class="sc-lab-panel sc-wf0321" data-lab-module="workflow-orchestration" data-module-panel="workflow-orchestration" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / WORKFLOW ORCHESTRATION / v0.32.1</p><h3>Workflow Checkpoints, Conditional Execution, and Partial Recovery</h3><p>Build dependency-aware scientific workflows with safe declarative conditions, durable checkpoint history, resumable node context, and lineage-preserving recovery runs that reuse successful work while restarting only affected branches.</p></header>
        <details class="sc-beta0600" data-integrated-research-beta-v0600 open>
          <summary>Integrated Scientific Research Beta <span class="sc-beta0600__badge">v0.60.0</span></summary>
          <div class="sc-beta0600__body">
            <div class="sc-beta0600__intro"><div><h4>One coherent research journey across the Lab</h4><p>Assess whether the active project has the metadata evidence needed to move coherently from data and models through validation, uncertainty, experiments, figures, workflows, reproducibility, compute hardening, and scientific audit. v0.60 evaluates evidence only; it does not certify science or authorize publication.</p></div><span class="sc-beta0600__badge">PROJECT / BETA</span></div>
            <p class="sc-beta0600__status" data-beta-v0600-status role="status" aria-live="polite">Integrated beta loading…</p>
            <div class="sc-beta0600__actions">
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-beta-v0600-assess>Assess integrated research journey</button>
              <button type="button" class="sc-lab-button" data-beta-v0600-packet>Build beta evidence packet</button>
              <button type="button" class="sc-lab-button" data-beta-v0600-verify>Verify packet hash</button>
              <button type="button" class="sc-lab-button" data-beta-v0600-save>Save beta evidence</button>
            </div>
            <div class="sc-beta0600__metrics" data-beta-v0600-metrics></div>
            <div class="sc-beta0600__grid">
              <section class="sc-beta0600__card"><h5>Integrated research journey</h5><div class="sc-beta0600__journey" data-beta-v0600-journey><p>No beta journey assessment yet.</p></div></section>
              <section class="sc-beta0600__card"><h5>Readiness / packet evidence</h5><pre class="sc-beta0600__output" data-beta-v0600-output>No integrated beta evidence has been generated yet.</pre></section>
            </div>
            <p class="sc-beta0600__note">The beta packet contains metadata, counts, contract hashes, and evidence hashes only. Raw datasets, credentials, and scientific inputs are excluded. Human review remains mandatory.</p>
          </div>
        </details>
        <details class="sc-slc0610" data-scientific-study-lifecycle-v0610 open>
          <summary>End-to-End Scientific Study &amp; Research Project Lifecycle <span class="sc-slc0610__badge">v0.61.0</span></summary>
          <div class="sc-slc0610__body">
            <div class="sc-slc0610__intro"><div><h4>Turn the integrated Lab project into one governed scientific study</h4><p>Define the research question and protocol, connect existing project evidence, review each required lifecycle stage, preserve conclusions and limitations, and build a tamper-evident study packet. v0.61 records scientific project state; it does not certify science, infer causality, authorize physical experiments, or publish automatically.</p></div><span class="sc-slc0610__badge">PROJECT / STUDY</span></div>
            <p class="sc-slc0610__status" data-slc-v0610-status role="status" aria-live="polite">Scientific study lifecycle loading…</p>
            <div class="sc-slc0610__actions">
              <label>Study template <select data-slc-v0610-template></select></label>
              <button type="button" class="sc-lab-button" data-slc-v0610-load-template>Load template</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-slc-v0610-evaluate>Evaluate study lifecycle</button>
              <button type="button" class="sc-lab-button" data-slc-v0610-save-study>Save study</button>
              <button type="button" class="sc-lab-button" data-slc-v0610-packet>Build study packet</button>
              <button type="button" class="sc-lab-button" data-slc-v0610-verify>Verify packet</button>
              <button type="button" class="sc-lab-button" data-slc-v0610-save-evidence>Save lifecycle evidence</button>
            </div>
            <div class="sc-slc0610__metrics" data-slc-v0610-metrics></div>
            <div class="sc-slc0610__grid">
              <section class="sc-slc0610__card"><h5>Scientific study definition</h5>
                <div class="sc-slc0610__fields">
                  <label>Study ID<input data-slc-v0610-id></label><label>Study type<select data-slc-v0610-type><option value="observational">Observational</option><option value="experimental">Experimental</option><option value="computational">Computational</option><option value="mixed">Mixed</option></select></label>
                  <label class="is-wide">Study title<input data-slc-v0610-title></label><label>Study status<select data-slc-v0610-study-status><option value="draft">Draft</option><option value="active">Active</option><option value="review">Review</option><option value="complete">Complete</option><option value="archived">Archived</option></select></label>
                  <label class="is-wide">Research question<textarea data-slc-v0610-question></textarea></label>
                  <label class="is-wide">Rationale<textarea data-slc-v0610-rationale></textarea></label>
                  <label class="is-wide">Hypotheses / expectations — one per line<textarea data-slc-v0610-hypotheses></textarea></label>
                  <label class="is-wide">Methods / protocol summary<textarea data-slc-v0610-methods></textarea></label>
                  <label class="is-wide">Analysis and validation plan<textarea data-slc-v0610-analysis-plan></textarea></label>
                  <label class="is-wide">Uncertainty plan<textarea data-slc-v0610-uncertainty></textarea></label>
                  <label class="is-wide">Conclusion summary — entered by the researcher<textarea data-slc-v0610-conclusion></textarea></label>
                  <label class="is-wide">Limitations<textarea data-slc-v0610-limitations></textarea></label>
                  <label class="is-wide">Open questions / follow-up<textarea data-slc-v0610-open-questions></textarea></label>
                </div>
              </section>
              <section class="sc-slc0610__card"><h5>Study lifecycle and human review</h5><div class="sc-slc0610__stages" data-slc-v0610-stages><p>No lifecycle assessment yet.</p></div>
                <div class="sc-slc0610__review"><label>Stage<select data-slc-v0610-review-stage><option value="">Choose stage</option><option value="question">Research question &amp; hypotheses</option><option value="protocol">Protocol &amp; analysis plan</option><option value="data">Data &amp; provenance</option><option value="analysis">Analysis / modeling</option><option value="validation">Validation &amp; diagnostics</option><option value="uncertainty">Uncertainty &amp; limitations</option><option value="experiment">Experimental evidence</option><option value="figure">Scientific figures</option><option value="conclusion">Conclusions &amp; limitations</option><option value="reproducibility">Reproducibility package</option><option value="audit">Scientific audit</option></select></label><label>Decision<select data-slc-v0610-review-decision><option value="accept">Accept stage evidence</option><option value="block">Block stage</option><option value="reopen">Reopen stage</option></select></label><label class="is-wide">Review rationale<textarea data-slc-v0610-review-rationale placeholder="Explain the evidence reviewed and the basis for this stage decision."></textarea></label><div class="is-wide"><button type="button" class="sc-lab-button sc-lab-button-primary" data-slc-v0610-review>Record stage review</button></div></div>
              </section>
              <section class="sc-slc0610__card"><h5>Saved project studies</h5><div class="sc-slc0610__saved" data-slc-v0610-saved></div></section>
              <section class="sc-slc0610__card"><h5>Lifecycle / packet evidence</h5><pre class="sc-slc0610__output" data-slc-v0610-output>No scientific study lifecycle evidence generated yet.</pre></section>
            </div>
            <p class="sc-slc0610__note">Study packets contain study metadata, stage states, evidence references/hashes, and review hashes. Raw datasets, credentials, arbitrary code, and automatic scientific claims are excluded.</p>
          </div>
        </details>

        <details class="sc-sct0620" data-scientific-claims-v0620 open>
          <summary>Scientific Claims, Evidence Matrix &amp; Conclusion Traceability <span class="sc-sct0620__badge">v0.62.0</span></summary>
          <div class="sc-sct0620__body">
            <div class="sc-sct0620__intro"><div><h4>Trace every scientific conclusion back through explicit evidence</h4><p>Record claims as researcher-authored statements, link supporting and contradicting evidence, preserve uncertainty and limitations, and connect final conclusions to reviewed claims. v0.62 evaluates traceability and evidence completeness; it does not infer claims, certify scientific validity, or authorize causal conclusions.</p></div><span class="sc-sct0620__badge">PROJECT / CLAIMS</span></div>
            <p class="sc-sct0620__status" data-sct-v0620-status role="status" aria-live="polite">Scientific claims traceability loading…</p>
            <div class="sc-sct0620__boundary"><strong>Governance boundary:</strong> a <em>traceable</em> claim means its evidence, uncertainty, contradictions, limitations, and review lineage are explicit. It is not an automatic truth, causal-validity, or publication claim.</div>
            <div class="sc-sct0620__actions">
              <button type="button" class="sc-lab-button" data-sct-v0620-evaluate>Evaluate evidence matrix</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-sct-v0620-packet>Build conclusion traceability packet</button>
              <button type="button" class="sc-lab-button" data-sct-v0620-verify>Verify packet hash</button>
              <button type="button" class="sc-lab-button" data-sct-v0620-save-evidence>Save traceability evidence</button>
            </div>
            <div class="sc-sct0620__metrics" data-sct-v0620-metrics></div>
            <div class="sc-sct0620__grid">
              <section class="sc-sct0620__card"><h5>Scientific claim</h5>
                <div class="sc-sct0620__actions"><button type="button" class="sc-lab-button" data-sct-v0620-new-claim>New claim</button><button type="button" class="sc-lab-button" data-sct-v0620-save-claim>Save claim</button></div>
                <div class="sc-sct0620__fields">
                  <label>Claim ID<input data-sct-v0620-claim-id value="claim-1"></label><label>Claim type<select data-sct-v0620-claim-type><option value="descriptive">Descriptive</option><option value="associational">Associational</option><option value="comparative">Comparative</option><option value="predictive">Predictive</option><option value="mechanistic">Mechanistic</option><option value="causal">Causal</option><option value="methodological">Methodological</option><option value="null">Null / no-effect</option></select></label>
                  <label>Status<select data-sct-v0620-claim-status><option value="active">Active</option><option value="draft">Draft</option><option value="withdrawn">Withdrawn</option><option value="superseded">Superseded</option></select></label><label class="is-wide">Claim statement<textarea data-sct-v0620-claim-statement placeholder="State the bounded scientific claim. Do not overstate causality or scope."></textarea></label>
                  <label class="is-wide">Scope / population / domain note<textarea data-sct-v0620-claim-scope></textarea></label>
                  <label class="is-wide">Supporting evidence refs — one per line<textarea data-sct-v0620-support placeholder="analysis-1"></textarea></label>
                  <label class="is-wide">Contradicting evidence refs<textarea data-sct-v0620-contradict></textarea></label>
                  <label>Validation evidence refs<textarea data-sct-v0620-validate></textarea></label><label>Uncertainty evidence refs<textarea data-sct-v0620-uncertainty></textarea></label>
                  <label>Limitation evidence refs<textarea data-sct-v0620-limit></textarea></label><label>Figure / context refs<textarea data-sct-v0620-figure></textarea></label>
                  <label>Claim review<select data-sct-v0620-claim-review-decision><option value="accept">Accept traceability</option><option value="accept-with-qualification">Accept with qualification</option><option value="block">Block claim</option><option value="reject">Reject claim</option><option value="reopen">Reopen claim</option></select></label>
                  <label class="is-wide">Claim review rationale<textarea data-sct-v0620-claim-review-rationale placeholder="Explain the supporting, contradicting, uncertainty, and limitation evidence reviewed."></textarea></label>
                </div>
                <button type="button" class="sc-lab-button sc-lab-button-primary" data-sct-v0620-review-claim>Record claim review</button>
              </section>
              <section class="sc-sct0620__card"><h5>Conclusion trace</h5>
                <div class="sc-sct0620__actions"><button type="button" class="sc-lab-button" data-sct-v0620-new-conclusion>New conclusion</button><button type="button" class="sc-lab-button" data-sct-v0620-save-conclusion>Save conclusion</button></div>
                <div class="sc-sct0620__fields">
                  <label>Conclusion ID<input data-sct-v0620-conclusion-id value="conclusion-1"></label><label class="is-wide">Conclusion statement<textarea data-sct-v0620-conclusion-statement placeholder="Write the conclusion in language bounded by the linked claims and limitations."></textarea></label>
                  <label class="is-wide">Linked claim IDs — one per line<textarea data-sct-v0620-conclusion-claims placeholder="claim-1"></textarea></label>
                  <label class="is-wide">Limitation evidence refs<textarea data-sct-v0620-conclusion-limits></textarea></label>
                  <label class="is-wide">Caveats / scope / unresolved uncertainty<textarea data-sct-v0620-conclusion-caveats></textarea></label>
                  <label>Conclusion review<select data-sct-v0620-conclusion-review-decision><option value="accept">Accept conclusion trace</option><option value="block">Block conclusion</option><option value="reopen">Reopen conclusion</option></select></label>
                  <label class="is-wide">Conclusion review rationale<textarea data-sct-v0620-conclusion-review-rationale placeholder="Explain why the conclusion wording is justified by the reviewed claim set."></textarea></label>
                </div>
                <button type="button" class="sc-lab-button sc-lab-button-primary" data-sct-v0620-review-conclusion>Record conclusion review</button>
              </section>
              <section class="sc-sct0620__card"><h5>Project evidence catalog</h5><p class="sc-sct0620__note">Click an evidence record to copy its reference. Only metadata, IDs, titles, and existing hashes are cataloged here; raw scientific values are not sent to the traceability evaluator.</p><div class="sc-sct0620__catalog" data-sct-v0620-catalog></div></section>
              <section class="sc-sct0620__card"><h5>Saved claims</h5><div class="sc-sct0620__saved" data-sct-v0620-saved-claims></div><h5>Saved conclusions</h5><div class="sc-sct0620__saved" data-sct-v0620-saved-conclusions></div></section>
            </div>
            <div class="sc-sct0620__tables">
              <section class="sc-sct0620__card"><h5>Claim × evidence matrix</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Claim</th><th>Type</th><th>Gate</th><th>Primary support</th><th>Contradictions</th><th>Uncertainty / limits</th><th>Conclusions</th></tr></thead><tbody data-sct-v0620-claim-matrix><tr><td colspan="7">No claims evaluated.</td></tr></tbody></table></div></section>
              <section class="sc-sct0620__card"><h5>Conclusion traceability</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Conclusion</th><th>Gate</th><th>Claims</th><th>Review</th></tr></thead><tbody data-sct-v0620-conclusion-matrix><tr><td colspan="4">No conclusions evaluated.</td></tr></tbody></table></div></section>
            </div>
            <section class="sc-sct0620__card"><h5>Matrix / packet evidence</h5><pre class="sc-sct0620__output" data-sct-v0620-output>No scientific claim traceability evidence generated yet.</pre></section>
            <p class="sc-sct0620__note">Contradicting evidence is retained rather than suppressed. Figure links provide context/presentation lineage but do not substitute for primary support. Causal claims are blocked when the active v0.61 study design is not experimental or mixed.</p>
          </div>
        </details>

        <details class="sc-lit0630" data-scientific-literature-v0630>
          <summary>Scientific Literature, Citation Graph &amp; Source-to-Claim Provenance <span class="sc-lit0630__badge">v0.63.0</span></summary>
          <div class="sc-lit0630__body">
            <div class="sc-lit0630__intro"><div><h4>Extend claim traceability outward to published and archival sources</h4><p>Register bibliographic metadata, review source applicability, connect literature to v0.62 scientific claims, preserve contradictory findings, and record source-to-source citation relations. v0.63 traces provenance; it does not rank authority, determine truth, verify retractions automatically, or fetch literature during evaluation.</p></div><span class="sc-lit0630__badge">PROJECT / LITERATURE</span></div>
            <p class="sc-lit0630__status" data-lit-v0630-status role="status" aria-live="polite">Scientific literature provenance loading…</p>
            <div class="sc-lit0630__boundary"><strong>Governance boundary:</strong> source status, peer-review state, applicability, and inclusion are declared/reviewed metadata. Lab does not infer bibliometric authority or treat citation counts as scientific validity.</div>
            <div class="sc-lit0630__actions">
              <button type="button" class="sc-lab-button" data-lit-v0630-evaluate>Evaluate literature provenance</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-lit-v0630-packet>Build provenance packet</button>
              <button type="button" class="sc-lab-button" data-lit-v0630-verify>Verify packet hash</button>
              <button type="button" class="sc-lab-button" data-lit-v0630-save-evidence>Save provenance evidence</button>
            </div>
            <div class="sc-lit0630__metrics" data-lit-v0630-metrics></div>
            <div class="sc-lit0630__grid">
              <section class="sc-lit0630__card"><h5>Literature source record</h5>
                <div class="sc-lit0630__actions"><button type="button" class="sc-lab-button" data-lit-v0630-new-source>New source</button><button type="button" class="sc-lab-button" data-lit-v0630-save-source>Save source</button></div>
                <div class="sc-lit0630__fields">
                  <label>Source ID<input data-lit-v0630-source-id value="source-1"></label><label>Source type<select data-lit-v0630-source-type><option value="journal-article">Journal article</option><option value="preprint">Preprint</option><option value="report">Report</option><option value="dataset">Dataset</option><option value="book">Book</option><option value="book-chapter">Book chapter</option><option value="thesis">Thesis</option><option value="conference-paper">Conference paper</option><option value="standard">Standard</option><option value="government-publication">Government publication</option><option value="repository-record">Repository record</option><option value="archive-record">Archive record</option><option value="other">Other</option></select></label>
                  <label class="is-wide">Title<input data-lit-v0630-title></label><label class="is-wide">Authors — one per line<textarea data-lit-v0630-authors></textarea></label>
                  <label>Publication year<input type="number" min="0" max="2200" data-lit-v0630-year></label><label>Journal / collection / container<input data-lit-v0630-container></label><label>Publisher<input data-lit-v0630-publisher></label><label>Origin<select data-lit-v0630-origin><option value="manual">Manual</option><option value="research-library">Research Library</option><option value="doi">DOI</option><option value="crossref">Crossref</option><option value="pubmed">PubMed</option><option value="openalex">OpenAlex</option><option value="repository">Repository</option><option value="archive">Archive</option><option value="other">Other</option></select></label>
                  <label>DOI<input data-lit-v0630-doi></label><label>PMID<input data-lit-v0630-pmid></label><label>arXiv<input data-lit-v0630-arxiv></label><label>ISBN<input data-lit-v0630-isbn></label>
                  <label class="is-wide">Source URL<input type="url" data-lit-v0630-url></label><label>Research Library record ref<input data-lit-v0630-library-ref></label>
                  <label>Source status<select data-lit-v0630-source-status><option value="unknown">Unknown</option><option value="active">Active</option><option value="corrected">Corrected</option><option value="retracted">Retracted</option><option value="withdrawn">Withdrawn</option></select></label><label>Peer review status<select data-lit-v0630-peer-review><option value="unknown">Unknown</option><option value="peer-reviewed">Peer reviewed</option><option value="not-peer-reviewed">Not peer reviewed</option><option value="preprint">Preprint</option><option value="not-applicable">Not applicable</option></select></label>
                  <label class="is-wide">Scope / applicability note<textarea data-lit-v0630-scope placeholder="Population, methods, jurisdiction, time period, or applicability notes."></textarea></label>
                  <label>Source review<select data-lit-v0630-review-decision><option value="include">Include</option><option value="include-with-caution">Include with caution</option><option value="exclude">Exclude</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Source review rationale<textarea data-lit-v0630-review-rationale></textarea></label>
                </div>
                <button type="button" class="sc-lab-button sc-lab-button-primary" data-lit-v0630-review-source>Record source review</button>
              </section>
              <section class="sc-lit0630__card"><h5>Saved literature sources</h5><div class="sc-lit0630__saved" data-lit-v0630-sources></div>
                <h5>Source → claim provenance</h5><div class="sc-lit0630__fields">
                  <label>Claim<select data-lit-v0630-link-claim></select></label><label>Literature source<select data-lit-v0630-link-source></select></label><label>Role<select data-lit-v0630-link-role><option value="supports">Supports</option><option value="contradicts">Contradicts</option><option value="contextualizes">Contextualizes</option><option value="methodological-background">Methodological background</option><option value="uncertainty">Uncertainty</option><option value="limitation">Limitation</option><option value="replication">Replication</option><option value="non-replication">Non-replication</option></select></label><label>Locator<input data-lit-v0630-link-locator placeholder="p. 14; Results §3.2"></label><label class="is-wide">Provenance note<textarea data-lit-v0630-link-note></textarea></label>
                </div><button type="button" class="sc-lab-button" data-lit-v0630-add-link>Add source-to-claim link</button>
                <h5>Citation graph edge</h5><div class="sc-lit0630__fields"><label>From source<select data-lit-v0630-edge-from></select></label><label>Relation<select data-lit-v0630-edge-relation><option value="cites">Cites</option><option value="supports">Supports</option><option value="contradicts">Contradicts</option><option value="extends">Extends</option><option value="replicates">Replicates</option><option value="fails-to-replicate">Fails to replicate</option><option value="corrects">Corrects</option><option value="retracts">Retracts</option><option value="uses-data-from">Uses data from</option><option value="uses-method-from">Uses method from</option><option value="related">Related</option></select></label><label>To source<select data-lit-v0630-edge-to></select></label><label>Locator<input data-lit-v0630-edge-locator></label><label class="is-wide">Relation note<textarea data-lit-v0630-edge-note></textarea></label></div><button type="button" class="sc-lab-button" data-lit-v0630-add-edge>Add citation edge</button>
              </section>
            </div>
            <div class="sc-lit0630__tables">
              <section class="sc-lit0630__card"><h5>Claim × literature provenance</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Claim</th><th>Gate</th><th>Sources</th><th>Reviewed</th><th>Contradictions</th><th>Unresolved</th></tr></thead><tbody data-lit-v0630-claim-matrix><tr><td colspan="6">No literature provenance evaluated.</td></tr></tbody></table></div></section>
              <section class="sc-lit0630__card"><h5>Source-to-claim links</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Claim</th><th>Role</th><th>Source</th><th>Locator</th></tr></thead><tbody data-lit-v0630-links><tr><td colspan="4">No links saved.</td></tr></tbody></table></div><h5>Citation graph</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>From</th><th>Relation</th><th>To</th></tr></thead><tbody data-lit-v0630-edges><tr><td colspan="3">No citation edges saved.</td></tr></tbody></table></div></section>
            </div>
            <section class="sc-lit0630__card"><h5>Literature / citation provenance evidence</h5><pre class="sc-lit0630__output" data-lit-v0630-output>No literature provenance evidence generated yet.</pre></section>
            <p class="sc-lit0630__note">Full-text documents are not copied into this packet. Citation counts are not authority scores. Retraction/correction status is declared metadata unless a separate governed connector verifies it. Contradicting and non-replication sources remain visible.</p>
          </div>
        </details>


        <details class="sc-es0640" data-evidence-synthesis-v0640>
          <summary>Replication, Systematic Evidence Synthesis &amp; Meta-Analysis <span class="sc-es0640__badge">v0.64.0</span></summary>
          <div class="sc-es0640__body">
            <div class="sc-es0640__intro"><div><h4>Synthesize reviewed literature without collapsing disagreement</h4><p>Register aggregate study effect estimates from v0.63 literature sources, evaluate replications, calculate fixed- or random-effects summaries, preserve heterogeneity, and attach the result back to the scientific claim set. v0.64 summarizes evidence; it does not determine scientific truth.</p></div><span class="sc-es0640__badge">PROJECT / SYNTHESIS</span></div>
            <p class="sc-es0640__status" data-es-v0640-status role="status" aria-live="polite">Evidence synthesis loading…</p>
            <div class="sc-es0640__boundary"><strong>Governance boundary:</strong> aggregate effect estimates only. Source inclusion must already be human reviewed in v0.63. High heterogeneity remains visible and requires qualified human review; no automatic publication-bias correction or causal certification is performed.</div>
            <div class="sc-es0640__actions"><button type="button" class="sc-lab-button" data-es-v0640-save-protocol>Save synthesis protocol</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-es-v0640-analyze>Run evidence synthesis</button><button type="button" class="sc-lab-button" data-es-v0640-packet>Build synthesis packet</button><button type="button" class="sc-lab-button" data-es-v0640-verify>Verify packet</button><button type="button" class="sc-lab-button" data-es-v0640-save-evidence>Save synthesis evidence</button></div>
            <div class="sc-es0640__metrics" data-es-v0640-metrics></div>
            <div class="sc-es0640__grid">
              <section class="sc-es0640__card"><h5>Synthesis protocol</h5><div class="sc-es0640__fields"><label>Protocol ID<input data-es-v0640-protocol-id value="synthesis-1"></label><label>Title<input data-es-v0640-title value="Scientific evidence synthesis"></label><label class="is-wide">Research question<textarea data-es-v0640-question></textarea></label><label class="is-wide">Linked v0.62 claim IDs<textarea data-es-v0640-claims placeholder="claim-1"></textarea></label><label>Effect metric<select data-es-v0640-metric><option value="generic">Generic</option><option value="mean-difference">Mean difference</option><option value="standardized-mean-difference">Standardized mean difference</option><option value="log-odds-ratio">Log odds ratio</option><option value="log-risk-ratio">Log risk ratio</option><option value="fisher-z-correlation">Fisher-z correlation</option></select></label><label>Model<select data-es-v0640-model><option value="random-effects">Random effects</option><option value="fixed-effect">Fixed effect</option></select></label><label>Minimum studies<input type="number" min="2" max="100" value="2" data-es-v0640-min-studies></label><label class="is-wide">Inclusion criteria<textarea data-es-v0640-include></textarea></label><label class="is-wide">Exclusion criteria<textarea data-es-v0640-exclude></textarea></label><label class="is-wide">Scope / harmonization note<textarea data-es-v0640-scope></textarea></label></div><h5>Human synthesis review</h5><div class="sc-es0640__fields"><label>Decision<select data-es-v0640-review-decision><option value="accept">Accept synthesis</option><option value="accept-with-qualification">Accept with qualification</option><option value="block">Block synthesis</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Rationale<textarea data-es-v0640-review-rationale placeholder="Address heterogeneity, replication disagreement, exclusions, and scope limitations."></textarea></label></div><button type="button" class="sc-lab-button" data-es-v0640-review>Record synthesis review</button></section>
              <section class="sc-es0640__card"><h5>Aggregate study effect estimate</h5><div class="sc-es0640__fields"><label>Effect ID<input data-es-v0640-effect-id value="effect-1"></label><label>Literature source<select data-es-v0640-effect-source></select></label><label class="is-wide">Linked claim IDs<textarea data-es-v0640-effect-claims placeholder="claim-1"></textarea></label><label>Effect estimate<input type="number" step="any" data-es-v0640-effect></label><label>Standard error<input type="number" step="any" min="0" data-es-v0640-se></label><label>Sample size<input type="number" min="1" data-es-v0640-n></label><label>Subgroup<input data-es-v0640-subgroup></label><label>Replication of source<select data-es-v0640-replication-of></select></label><label>Estimate label<input data-es-v0640-label placeholder="Primary adjusted estimate"></label><label class="is-wide">Effect note<textarea data-es-v0640-effect-note placeholder="Extraction/harmonization note; do not paste participant-level data."></textarea></label></div><button type="button" class="sc-lab-button" data-es-v0640-add-effect>Add aggregate effect</button><h5>Saved protocols</h5><div class="sc-es0640__saved" data-es-v0640-saved></div></section>
            </div>
            <div class="sc-es0640__grid"><section class="sc-es0640__card"><h5>Study effects</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Effect</th><th>Source</th><th>Metric</th><th>Estimate</th><th>SE</th><th>Replication of</th></tr></thead><tbody data-es-v0640-effects><tr><td colspan="6">No aggregate effect estimates saved.</td></tr></tbody></table></div></section><section class="sc-es0640__card"><h5>Replication assessment</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Replication</th><th>Original</th><th>Gate</th><th>Δ z</th></tr></thead><tbody data-es-v0640-replications><tr><td colspan="4">No replication links recorded.</td></tr></tbody></table></div></section></div>
            <section class="sc-es0640__card"><h5>Synthesis / meta-analysis evidence</h5><pre class="sc-es0640__output" data-es-v0640-output>No evidence synthesis generated yet.</pre></section>
            <p class="sc-es0640__note">A pooled estimate is a model-based summary, not a truth score. I² and τ² remain explicit; leave-one-out sensitivity and replication disagreement remain visible. Study quality is declared/reviewed upstream rather than inferred from citation counts or journal prestige.</p>
          </div>
        </details>

        <details class="sc-eg0650" data-evidence-grading-v0650>
          <summary>Scientific Evidence Grading, Contradiction Analysis &amp; Consensus Boundaries <span class="sc-eg0650__badge">v0.65.0</span></summary>
          <div class="sc-eg0650__body">
            <div class="sc-eg0650__intro"><div><h4>State what the evidence supports — and where agreement stops</h4><p>Grade the evidence state for reviewed v0.62 claims using v0.63 literature provenance and v0.64 synthesis/replication evidence. Contradictions, replication disagreement, heterogeneity, source caution, and scope limitations remain explicit. v0.65 defines a reviewable evidence boundary; it does not calculate a truth score or certify scientific consensus.</p></div><span class="sc-eg0650__badge">PROJECT / EVIDENCE</span></div>
            <p class="sc-eg0650__status" data-eg-v0650-status role="status" aria-live="polite">Evidence grading loading…</p>
            <div class="sc-eg0650__boundary"><strong>Governance boundary:</strong> evidence grades are transparent rule states, not numerical authority scores. Citation counts and journal prestige are not used. A final consensus boundary requires explicit human claim review plus a human boundary decision and written scope statement.</div>
            <div class="sc-eg0650__actions"><button type="button" class="sc-lab-button" data-eg-v0650-use-project>Use active project evidence</button><button type="button" class="sc-lab-button" data-eg-v0650-save>Save boundary assessment</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-eg-v0650-evaluate>Grade evidence &amp; analyze contradictions</button><button type="button" class="sc-lab-button" data-eg-v0650-packet>Build evidence/consensus packet</button><button type="button" class="sc-lab-button" data-eg-v0650-verify>Verify packet</button><button type="button" class="sc-lab-button" data-eg-v0650-save-evidence>Save evidence</button></div>
            <div class="sc-eg0650__metrics" data-eg-v0650-metrics></div>
            <div class="sc-eg0650__grid">
              <section class="sc-eg0650__card"><h5>Evidence boundary definition</h5><div class="sc-eg0650__fields"><label>Assessment ID<input data-eg-v0650-assessment-id value="evidence-boundary-1"></label><label>Title<input data-eg-v0650-title value="Scientific evidence and consensus boundary"></label><label class="is-wide">v0.62 claim IDs<textarea data-eg-v0650-claims placeholder="claim-1"></textarea></label><label class="is-wide">v0.64 synthesis protocol IDs<textarea data-eg-v0650-syntheses placeholder="synthesis-1"></textarea></label><label>Population / system scope<textarea data-eg-v0650-population></textarea></label><label>Context / setting scope<textarea data-eg-v0650-context></textarea></label><label class="is-wide">Outcome / phenomenon scope<textarea data-eg-v0650-outcome></textarea></label><label class="is-wide">Human-written consensus boundary statement<textarea data-eg-v0650-boundary placeholder="State only what can reasonably be concluded within the reviewed evidence and scope."></textarea></label><label class="is-wide">Qualification / unresolved disagreement note<textarea data-eg-v0650-qualification placeholder="Preserve heterogeneity, contradictions, source cautions, and exceptions here."></textarea></label></div><h5>Human boundary review</h5><div class="sc-eg0650__fields"><label>Decision<select data-eg-v0650-review-decision><option value="accept-boundary">Accept bounded consensus</option><option value="accept-with-qualification">Accept with qualification</option><option value="block">Block boundary</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Rationale<textarea data-eg-v0650-review-rationale placeholder="Explain why the evidence boundary is defensible, qualified, blocked, or reopened."></textarea></label></div><button type="button" class="sc-lab-button" data-eg-v0650-review>Record boundary review</button></section>
              <section class="sc-eg0650__card"><h5>Evidence grading rules</h5><div class="sc-eg0650__legend"><span>insufficient</span><span>limited</span><span>moderate</span><span>substantial</span><span>contested</span></div><p>Substantial evidence requires a reviewed synthesis, multiple reviewed supports, at least one directionally consistent replication, no material contradiction, and no high heterogeneity. Moderate and limited states remain useful evidence but cannot become an unqualified bounded consensus automatically.</p><h5>Saved assessments</h5><div class="sc-eg0650__saved" data-eg-v0650-saved></div><h5>Current gate</h5><p class="sc-eg0650__gate" data-eg-v0650-gate data-gate="needs-review">needs-review</p></section>
            </div>
            <div class="sc-eg0650__grid"><section class="sc-eg0650__card"><h5>Claim × evidence grading matrix</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Claim</th><th>Grade</th><th>Support</th><th>Contradictions</th><th>Replication C/D</th><th>Boundary candidate</th></tr></thead><tbody data-eg-v0650-grades><tr><td colspan="6">No evidence grading assessment yet.</td></tr></tbody></table></div></section><section class="sc-eg0650__card"><h5>Contradiction analysis</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Claim</th><th>State</th><th>Factors</th><th>Qualified interpretation?</th></tr></thead><tbody data-eg-v0650-contradictions><tr><td colspan="4">No contradiction analysis yet.</td></tr></tbody></table></div></section></div>
            <section class="sc-eg0650__card"><h5>Evidence grade / consensus boundary evidence</h5><pre class="sc-eg0650__output" data-eg-v0650-output>No v0.65 evidence grading evidence generated yet.</pre></section>
            <p class="sc-eg0650__note">A consensus boundary is a scoped human-reviewed statement about the current evidence record, not a declaration of truth. Contradicting sources, non-replications, heterogeneity, limitations, source cautions, unresolved references, and qualified reviews remain in the packet.</p>
          </div>
        </details>

        <details class="sc-sa0660" data-scientific-argumentation-v0660>
          <summary>Competing Hypotheses &amp; Scientific Argumentation <span class="sc-sa0660__badge">v0.66.0</span></summary>
          <div class="sc-sa0660__body">
            <div class="sc-sa0660__intro"><div><h4>Compare rival explanations without turning evidence into an automatic winner</h4><p>Define competing hypotheses, state predictions before interpretation, map governed evidence to each alternative, design discriminating tests, preserve falsifying challenges, and record explicit human judgments. v0.66 structures scientific argumentation; it does not prove, automatically falsify, or rank hypotheses by a hidden truth score.</p></div><span class="sc-sa0660__badge">PROJECT / ARGUMENT</span></div>
            <p class="sc-sa0660__status" data-sa-v0660-status role="status" aria-live="polite">Scientific argumentation loading…</p>
            <div class="sc-sa0660__boundary"><strong>Governance boundary:</strong> unresolved alternatives remain visible. A falsifying candidate is an evidence challenge requiring human review, not an automatic rejection. A provisional preference is explicitly labeled provisional and never converted into proof or causal certification.</div>
            <div class="sc-sa0660__actions"><button type="button" class="sc-lab-button" data-sa-v0660-use-project>Use active project evidence</button><button type="button" class="sc-lab-button" data-sa-v0660-save-case>Save argument case</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-sa-v0660-evaluate>Evaluate competing hypotheses</button><button type="button" class="sc-lab-button" data-sa-v0660-packet>Build argumentation packet</button><button type="button" class="sc-lab-button" data-sa-v0660-verify>Verify packet</button><button type="button" class="sc-lab-button" data-sa-v0660-save-evidence>Save argument evidence</button></div>
            <div class="sc-sa0660__metrics" data-sa-v0660-metrics></div>
            <div class="sc-sa0660__grid">
              <section class="sc-sa0660__card"><h5>Argument case</h5><div class="sc-sa0660__fields"><label>Case ID<input data-sa-v0660-case-id value="argument-case-1"></label><label>Title<input data-sa-v0660-title value="Competing hypotheses"></label><label class="is-wide">Research question<textarea data-sa-v0660-question placeholder="What competing explanations could account for the observed evidence?"></textarea></label><label class="is-wide">Linked v0.62 claim IDs<textarea data-sa-v0660-claims placeholder="claim-1"></textarea></label><label class="is-wide">Linked v0.65 evidence-boundary assessment IDs<textarea data-sa-v0660-boundaries placeholder="evidence-boundary-1"></textarea></label><label class="is-wide">Scope note<textarea data-sa-v0660-scope placeholder="Population, system, context, timeframe, assumptions, and known limits."></textarea></label><label class="is-wide">Decision boundary / unresolved alternatives note<textarea data-sa-v0660-decision-boundary placeholder="State what remains unresolved and why any preference remains provisional."></textarea></label></div><h5>Human argument review</h5><div class="sc-sa0660__fields"><label>Decision<select data-sa-v0660-case-review-decision><option value="accept-argument-map">Accept argument map</option><option value="accept-with-unresolved-alternatives">Accept with unresolved alternatives</option><option value="block">Block argument</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Rationale<textarea data-sa-v0660-case-review-rationale></textarea></label></div><button type="button" class="sc-lab-button" data-sa-v0660-review-case-button>Record argument review</button></section>
              <section class="sc-sa0660__card"><h5>Competing hypothesis</h5><div class="sc-sa0660__fields"><label>Hypothesis ID<input data-sa-v0660-hypothesis-id value="hypothesis-1"></label><label>Title<input data-sa-v0660-hypothesis-title></label><label class="is-wide">Hypothesis statement<textarea data-sa-v0660-hypothesis-statement></textarea></label><label class="is-wide">Mechanism / explanation<textarea data-sa-v0660-hypothesis-mechanism></textarea></label><label class="is-wide">Linked claim IDs<textarea data-sa-v0660-hypothesis-claims></textarea></label><label class="is-wide">Scope / assumptions<textarea data-sa-v0660-hypothesis-scope></textarea></label><label>Prediction ID<input data-sa-v0660-prediction-id value="prediction-1"></label><label>Expected outcome<select data-sa-v0660-prediction-outcome><option value="present">Present</option><option value="absent">Absent</option><option value="increase">Increase</option><option value="decrease">Decrease</option><option value="association">Association</option><option value="no-effect">No effect</option><option value="custom">Custom</option></select></label><label class="is-wide">Prediction statement<textarea data-sa-v0660-prediction-statement></textarea></label><label>Discriminating test ID<input data-sa-v0660-prediction-test placeholder="test-1"></label><label>Prediction boundary<input data-sa-v0660-prediction-boundary></label></div><button type="button" class="sc-lab-button" data-sa-v0660-save-hypothesis>Save hypothesis</button><h5>Saved hypotheses</h5><div class="sc-sa0660__saved" data-sa-v0660-saved-hypotheses></div></section>
            </div>
            <div class="sc-sa0660__grid">
              <section class="sc-sa0660__card"><h5>Hypothesis evidence mapping</h5><div class="sc-sa0660__fields"><label>Link ID<input data-sa-v0660-link-id value="argument-link-1"></label><label>Hypothesis<select data-sa-v0660-link-hypothesis></select></label><label class="is-wide">Evidence reference<select data-sa-v0660-link-evidence></select></label><label>Relation<select data-sa-v0660-link-relation><option value="supports">Supports</option><option value="contradicts">Contradicts</option><option value="falsifying-candidate">Falsifying candidate</option><option value="discriminates-for">Discriminates for</option><option value="discriminates-against">Discriminates against</option><option value="uncertainty">Uncertainty</option><option value="neutral">Neutral</option><option value="contextualizes">Contextualizes</option></select></label><label>Prediction ID<input data-sa-v0660-link-prediction></label><label>Test ID<input data-sa-v0660-link-test></label><label class="is-wide">Interpretive note<textarea data-sa-v0660-link-note></textarea></label></div><button type="button" class="sc-lab-button" data-sa-v0660-add-link>Add evidence link</button><div class="sc-lab-table-wrap"><table><thead><tr><th>Hypothesis</th><th>Evidence</th><th>Relation</th><th>Test</th></tr></thead><tbody data-sa-v0660-links><tr><td colspan="4">No hypothesis evidence links.</td></tr></tbody></table></div></section>
              <section class="sc-sa0660__card"><h5>Discriminating test</h5><div class="sc-sa0660__fields"><label>Test ID<input data-sa-v0660-test-id value="discriminating-test-1"></label><label>Title<input data-sa-v0660-test-title value="Discriminating test"></label><label>Method reference<input data-sa-v0660-test-method></label><label>Observed evidence<select data-sa-v0660-test-evidence></select></label><label>Hypothesis A<select data-sa-v0660-test-h1></select></label><label>Expected A<select data-sa-v0660-test-h1-outcome><option value="present">Present</option><option value="absent">Absent</option><option value="increase">Increase</option><option value="decrease">Decrease</option><option value="association">Association</option><option value="no-effect">No effect</option><option value="custom">Custom</option></select></label><label>Hypothesis B<select data-sa-v0660-test-h2></select></label><label>Expected B<select data-sa-v0660-test-h2-outcome><option value="present">Present</option><option value="absent">Absent</option><option value="increase">Increase</option><option value="decrease">Decrease</option><option value="association">Association</option><option value="no-effect">No effect</option><option value="custom">Custom</option></select></label><label>Status<select data-sa-v0660-test-status><option value="planned">Planned</option><option value="observed">Observed</option><option value="inconclusive">Inconclusive</option></select></label><label class="is-wide">Limitations<textarea data-sa-v0660-test-limitations></textarea></label></div><button type="button" class="sc-lab-button" data-sa-v0660-add-test>Save discriminating test</button><div class="sc-lab-table-wrap"><table><thead><tr><th>Test</th><th>Alternatives</th><th>Expected outcomes</th><th>Status</th></tr></thead><tbody data-sa-v0660-tests><tr><td colspan="4">No discriminating tests.</td></tr></tbody></table></div></section>
            </div>
            <div class="sc-sa0660__grid">
              <section class="sc-sa0660__card"><h5>Human hypothesis review</h5><div class="sc-sa0660__fields"><label>Hypothesis<select data-sa-v0660-review-hypothesis></select></label><label>Decision<select data-sa-v0660-hypothesis-review-decision><option value="retain">Retain</option><option value="provisionally-prefer">Provisionally prefer</option><option value="reject">Reject</option><option value="block">Block</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Rationale<textarea data-sa-v0660-hypothesis-review-rationale placeholder="Address support, contradiction, falsifying challenges, discriminating tests, and unresolved alternatives."></textarea></label></div><button type="button" class="sc-lab-button" data-sa-v0660-review-hypothesis-button>Record hypothesis review</button><h5>Current gate</h5><p class="sc-sa0660__gate" data-sa-v0660-gate data-gate="needs-review">needs-review</p></section>
              <section class="sc-sa0660__card"><h5>Argumentation evidence</h5><pre class="sc-sa0660__output" data-sa-v0660-output>No v0.66 scientific argumentation evidence generated yet.</pre></section>
            </div>
            <div class="sc-sa0660__grid"><section class="sc-sa0660__card"><h5>Hypothesis × evidence assessment</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Hypothesis</th><th>State</th><th>Predictions</th><th>Support</th><th>Contradictions</th><th>Falsifying challenges</th><th>Human review</th></tr></thead><tbody data-sa-v0660-matrix><tr><td colspan="7">No hypothesis assessment yet.</td></tr></tbody></table></div></section><section class="sc-sa0660__card"><h5>Discrimination analysis</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Test</th><th>Hypotheses</th><th>Distinct predictions</th><th>Discriminates?</th></tr></thead><tbody data-sa-v0660-discrimination><tr><td colspan="4">No discriminating tests evaluated.</td></tr></tbody></table></div></section></div>
            <p class="sc-sa0660__note">Scientific argumentation is an explicit map of alternatives and evidence. A retained or provisionally preferred hypothesis remains open to revision; rejected alternatives, contradictory evidence, falsifying candidates, failed discriminating tests, and unresolved uncertainty remain in the provenance packet.</p>
          </div>
        </details>

        <details class="sc-ci0670" data-causal-inference-v0670>
          <summary>Causal Inference &amp; Quasi-Experimental Methods <span class="sc-ci0670__badge">v0.67.0</span></summary>
          <div class="sc-ci0670__body">
            <div class="sc-ci0670__intro"><div><h4>Estimate causal contrasts without hiding identification assumptions</h4><p>Define a governed quasi-experimental design, state the estimand and assignment mechanism, record identification assumptions, add aggregate effect estimates, inspect method-specific diagnostics and sensitivity evidence, and preserve explicit human review. Supported methods include matching, weighting, difference-in-differences, interrupted time series, and regression discontinuity.</p></div><span class="sc-ci0670__badge">PROJECT / CAUSAL</span></div>
            <p class="sc-ci0670__status" data-ci-v0670-status role="status" aria-live="polite">Causal inference loading…</p>
            <div class="sc-ci0670__boundary"><strong>Governance boundary:</strong> a bounded causal estimate is conditional on the stated design, identification assumptions, diagnostics, sensitivity analysis, scope, and human review. v0.67 never converts observational or quasi-experimental evidence into automatic proof of causation.</div>
            <div class="sc-ci0670__actions"><button type="button" class="sc-lab-button" data-ci-v0670-use-project>Use active project context</button><button type="button" class="sc-lab-button" data-ci-v0670-defaults>Load method assumptions</button><button type="button" class="sc-lab-button" data-ci-v0670-save-design>Save causal design</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-ci-v0670-evaluate>Evaluate causal design</button><button type="button" class="sc-lab-button" data-ci-v0670-packet>Build causal packet</button><button type="button" class="sc-lab-button" data-ci-v0670-verify>Verify packet</button><button type="button" class="sc-lab-button" data-ci-v0670-save-evidence>Save causal evidence</button></div>
            <div class="sc-ci0670__metrics" data-ci-v0670-metrics></div>
            <div class="sc-ci0670__grid">
              <section class="sc-ci0670__card"><h5>Causal design</h5><div class="sc-ci0670__fields"><label>Design ID<input data-ci-v0670-design-id value="causal-design-1"></label><label>Method<select data-ci-v0670-method><option value="matching">Matching</option><option value="weighting">Weighting</option><option value="difference-in-differences" selected>Difference-in-differences</option><option value="interrupted-time-series">Interrupted time series</option><option value="regression-discontinuity">Regression discontinuity</option></select></label><label>Title<input data-ci-v0670-title value="Causal design"></label><label>Study ID<input data-ci-v0670-study-id placeholder="study-1"></label><label class="is-wide">Linked v0.62 claim IDs<textarea data-ci-v0670-claims placeholder="claim-1"></textarea></label><label class="is-wide">Estimand<textarea data-ci-v0670-estimand placeholder="Define the causal contrast being estimated."></textarea></label><label>Treatment / exposure<textarea data-ci-v0670-treatment></textarea></label><label>Comparison<textarea data-ci-v0670-comparison></textarea></label><label>Outcome<textarea data-ci-v0670-outcome></textarea></label><label>Time boundary<textarea data-ci-v0670-time></textarea></label><label class="is-wide">Assignment mechanism<textarea data-ci-v0670-assignment placeholder="Describe how treatment/exposure assignment occurs and why the design may identify the estimand."></textarea></label><label class="is-wide">Identification assumptions — one per line: kind | status | statement<textarea data-ci-v0670-assumptions></textarea></label><label class="is-wide">Method notes<textarea data-ci-v0670-method-notes></textarea></label><label class="is-wide">Limitations / residual confounding boundary<textarea data-ci-v0670-limitations></textarea></label></div><h5>Human causal review</h5><div class="sc-ci0670__fields"><label>Decision<select data-ci-v0670-review-decision><option value="accept-assumptions">Accept assumptions within scope</option><option value="accept-with-qualification">Accept with qualification</option><option value="block">Block causal interpretation</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Rationale<textarea data-ci-v0670-review-rationale placeholder="Address identification assumptions, diagnostics, sensitivity, alternative explanations, and limitations."></textarea></label></div><button type="button" class="sc-lab-button" data-ci-v0670-review>Record causal review</button></section>
              <section class="sc-ci0670__card"><h5>Aggregate causal estimate</h5><div class="sc-ci0670__fields"><label>Estimate ID<input data-ci-v0670-estimate-id value="causal-estimate-1"></label><label>Effect metric<select data-ci-v0670-effect-metric><option value="difference">Difference</option><option value="standardized-difference">Standardized difference</option><option value="log-odds-ratio">Log odds ratio</option><option value="log-risk-ratio">Log risk ratio</option><option value="ratio">Ratio</option><option value="slope-change">Slope change</option><option value="level-change">Level change</option><option value="custom">Custom</option></select></label><label>Estimate<input type="number" step="any" data-ci-v0670-estimate></label><label>Standard error<input type="number" step="any" data-ci-v0670-se></label><label>CI lower<input type="number" step="any" data-ci-v0670-ci-low></label><label>CI upper<input type="number" step="any" data-ci-v0670-ci-high></label><label>Treated N<input type="number" min="0" data-ci-v0670-n-treated></label><label>Comparison N<input type="number" min="0" data-ci-v0670-n-comparison></label><label class="is-wide">Estimate note<textarea data-ci-v0670-estimate-note></textarea></label></div><button type="button" class="sc-lab-button" data-ci-v0670-add-estimate>Save aggregate estimate</button><h5>Project causal records</h5><div data-ci-v0670-saved><p>No v0.67 causal records saved.</p></div></section>
            </div>
            <div class="sc-ci0670__grid">
              <section class="sc-ci0670__card"><h5>Method diagnostic / sensitivity check</h5><div class="sc-ci0670__fields"><label>Diagnostic ID<input data-ci-v0670-diagnostic-id value="causal-diagnostic-1"></label><label>Kind<input data-ci-v0670-diagnostic-kind placeholder="parallel-trends"></label><label>State<select data-ci-v0670-diagnostic-state><option value="pass">Pass</option><option value="caution">Caution</option><option value="fail">Fail</option><option value="inconclusive">Inconclusive</option></select></label><label>Evidence reference<input data-ci-v0670-diagnostic-evidence></label><label>Aggregate value<input type="number" step="any" data-ci-v0670-diagnostic-value></label><label>Threshold<input type="number" step="any" data-ci-v0670-diagnostic-threshold></label><label class="is-wide">Diagnostic note<textarea data-ci-v0670-diagnostic-note></textarea></label></div><button type="button" class="sc-lab-button" data-ci-v0670-add-diagnostic>Save diagnostic</button><h5>Current gate</h5><p class="sc-ci0670__gate" data-ci-v0670-gate data-gate="needs-review">needs-review</p></section>
              <section class="sc-ci0670__card"><h5>Causal inference evidence</h5><pre class="sc-ci0670__output" data-ci-v0670-output>No v0.67 causal inference evidence generated yet.</pre></section>
            </div>
            <div class="sc-ci0670__grid"><section class="sc-ci0670__card"><h5>Identification assumption coverage</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Required assumption</th><th>State</th></tr></thead><tbody data-ci-v0670-assumption-table><tr><td colspan="2">No assumption assessment yet.</td></tr></tbody></table></div></section><section class="sc-ci0670__card"><h5>Method diagnostic coverage</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Required diagnostic</th><th>State</th></tr></thead><tbody data-ci-v0670-diagnostic-table><tr><td colspan="2">No diagnostic assessment yet.</td></tr></tbody></table></div></section></div>
            <p class="sc-ci0670__note">v0.67 accepts aggregate estimates and governed diagnostic metadata only. Raw participant-level data, treatment/outcome vectors, hidden assumption satisfaction, automatic causal certification, arbitrary code, and network fetching during evaluation are excluded.</p>
          </div>
        </details>

        <details class="sc-hm0680" data-hierarchical-modeling-v0680>
          <summary>Hierarchical, Multilevel &amp; Cross-Study Modeling <span class="sc-hm0680__badge">v0.68.0</span></summary>
          <div class="sc-hm0680__body">
            <div class="sc-hm0680__intro"><div><h4>Model variation across groups and studies without erasing structure</h4><p>Fit governed aggregate hierarchical models with explicit partial pooling, random-intercept cluster pooling, random-slope/meta-regression structure, between-unit heterogeneity, shrinkage diagnostics, and human-reviewed generalization boundaries. v0.68 works from aggregate unit/study estimates and reported uncertainty; participant-level records are outside this release boundary.</p></div><span class="sc-hm0680__badge">PROJECT / MULTILEVEL</span></div>
            <p class="sc-hm0680__status" data-hm-v0680-status role="status" aria-live="polite">Hierarchical modeling loading…</p>
            <div class="sc-hm0680__boundary"><strong>Governance boundary:</strong> partial pooling describes modeled variation among the recorded groups, sites, cohorts, institutions, or studies. A bounded multilevel estimate does not establish universal transportability, ecological inference, causal proof, or validity outside the stated population and moderator range.</div>
            <div class="sc-hm0680__actions"><button type="button" class="sc-lab-button" data-hm-v0680-use-project>Use active project context</button><button type="button" class="sc-lab-button" data-hm-v0680-defaults>Load model boundaries</button><button type="button" class="sc-lab-button" data-hm-v0680-save-model>Save model definition</button><button type="button" class="sc-lab-button" data-hm-v0680-fit>Fit partial-pooling model</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-hm-v0680-evaluate>Evaluate multilevel model</button><button type="button" class="sc-lab-button" data-hm-v0680-packet>Build model packet</button><button type="button" class="sc-lab-button" data-hm-v0680-verify>Verify packet</button><button type="button" class="sc-lab-button" data-hm-v0680-save-evidence>Save model evidence</button></div>
            <div class="sc-hm0680__metrics" data-hm-v0680-metrics></div>
            <div class="sc-hm0680__grid">
              <section class="sc-hm0680__card"><h5>Hierarchical model definition</h5><div class="sc-hm0680__fields"><label>Model ID<input data-hm-v0680-model-id value="hierarchical-model-1"></label><label>Model type<select data-hm-v0680-model-type><option value="hierarchical-normal">Hierarchical normal / partial pooling</option><option value="random-intercept">Random intercept / clustered pooling</option><option value="random-slope">Random slope / moderator model</option><option value="cross-study-pooling">Cross-study random-effects pooling</option><option value="cross-study-meta-regression">Cross-study meta-regression</option></select></label><label>Level type<select data-hm-v0680-level-type><option value="group">Group</option><option value="site">Site</option><option value="study" selected>Study</option><option value="region">Region</option><option value="cohort">Cohort</option><option value="institution">Institution</option><option value="custom">Custom</option></select></label><label>Effect metric<select data-hm-v0680-effect-metric><option value="difference">Difference</option><option value="standardized-difference">Standardized difference</option><option value="log-odds-ratio">Log odds ratio</option><option value="log-risk-ratio">Log risk ratio</option><option value="fisher-z">Fisher-z correlation</option><option value="slope">Slope</option><option value="level">Level</option><option value="custom">Custom</option></select></label><label>Title<input data-hm-v0680-title value="Hierarchical model"></label><label>Study ID<input data-hm-v0680-study-id placeholder="study-1"></label><label class="is-wide">Linked v0.62 claim IDs<textarea data-hm-v0680-claims placeholder="claim-1"></textarea></label><label class="is-wide">Linked v0.64 synthesis IDs<textarea data-hm-v0680-syntheses placeholder="synthesis-1"></textarea></label><label class="is-wide">Outcome definition<textarea data-hm-v0680-outcome></textarea></label><label>Moderator name<input data-hm-v0680-moderator-name placeholder="mean-age"></label><label class="is-wide">Population boundary<textarea data-hm-v0680-population-boundary placeholder="Define the populations/groups/studies represented by this model."></textarea></label><label class="is-wide">Generalization boundary<textarea data-hm-v0680-generalization-boundary placeholder="State where the pooled/shrunken estimates should not be extrapolated."></textarea></label><label class="is-wide">Modeling assumptions<textarea data-hm-v0680-assumptions></textarea></label><label class="is-wide">Limitations<textarea data-hm-v0680-limitations></textarea></label></div><h5>Human multilevel-model review</h5><div class="sc-hm0680__fields"><label>Decision<select data-hm-v0680-review-decision><option value="accept-within-scope">Accept within stated scope</option><option value="accept-with-qualification">Accept with qualification</option><option value="block">Block interpretation</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Rationale<textarea data-hm-v0680-review-rationale placeholder="Address heterogeneity, shrinkage, cluster/study comparability, moderator range, transportability, and limitations."></textarea></label></div><button type="button" class="sc-lab-button" data-hm-v0680-review>Record model review</button></section>
              <section class="sc-hm0680__card"><h5>Aggregate unit / study estimate</h5><div class="sc-hm0680__fields"><label>Record ID<input data-hm-v0680-unit-record-id value="hierarchical-unit-1"></label><label>Unit / study ID<input data-hm-v0680-unit-id value="study-1"></label><label>Cluster ID<input data-hm-v0680-cluster-id placeholder="site-a"></label><label>Literature/source ref<input data-hm-v0680-source-ref placeholder="source-1"></label><label>Estimate<input type="number" step="any" data-hm-v0680-estimate></label><label>Standard error<input type="number" step="any" data-hm-v0680-se></label><label>CI lower<input type="number" step="any" data-hm-v0680-ci-low></label><label>CI upper<input type="number" step="any" data-hm-v0680-ci-high></label><label>Moderator value<input type="number" step="any" data-hm-v0680-moderator-value></label><label>Aggregate N<input type="number" min="0" data-hm-v0680-sample-size></label><label class="is-wide">Unit note<textarea data-hm-v0680-unit-note></textarea></label></div><button type="button" class="sc-lab-button" data-hm-v0680-add-unit>Save aggregate unit estimate</button><h5>Project multilevel records</h5><div data-hm-v0680-saved><p>No v0.68 multilevel records saved.</p></div></section>
            </div>
            <div class="sc-hm0680__grid">
              <section class="sc-hm0680__card"><h5>Aggregate unit estimates</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Unit</th><th>Cluster</th><th>Source</th><th>Estimate</th><th>SE</th><th>Moderator</th></tr></thead><tbody data-hm-v0680-units><tr><td colspan="6">No v0.68 aggregate unit estimates.</td></tr></tbody></table></div><h5>Current gate</h5><p class="sc-hm0680__gate" data-hm-v0680-gate data-gate="needs-review">needs-review</p></section>
              <section class="sc-hm0680__card"><h5>Hierarchical modeling evidence</h5><pre class="sc-hm0680__output" data-hm-v0680-output>No v0.68 hierarchical modeling evidence generated yet.</pre></section>
            </div>
            <div class="sc-hm0680__grid"><section class="sc-hm0680__card"><h5>Shrinkage / model-fit diagnostics</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Unit</th><th>Observed</th><th>Shrunken / predicted</th><th>Pooling weight / residual</th></tr></thead><tbody data-hm-v0680-shrinkage><tr><td colspan="4">No shrinkage/residual diagnostics yet.</td></tr></tbody></table></div></section><section class="sc-hm0680__card"><h5>Interpretation boundary</h5><p>Report τ² and I² alongside pooled estimates. Treat large shrinkage as a model consequence, not proof that unit differences are noise. Random-slope/meta-regression estimates apply over the observed moderator range unless a researcher explicitly justifies otherwise.</p></section></div>
            <p class="sc-hm0680__note">v0.68 accepts aggregate unit/study estimates and their uncertainty only. Raw participant records, automatic generalization, ecological inference, hidden model selection, automatic causal proof, arbitrary code, and network fetching during evaluation are excluded.</p>
          </div>
        </details>

        <details class="sc-th0690" data-scientific-theory-v0690>
          <summary>Scientific Theory &amp; Conceptual Model Workspace <span class="sc-th0690__badge">v0.69.0</span></summary>
          <div class="sc-th0690__body">
            <div class="sc-th0690__intro"><div><h4>Connect constructs, mechanisms, hypotheses, equations, claims, and evidence into an explicit theory</h4><p>Build governed conceptual and mechanistic models with defined constructs, typed relations, testable predictions, falsification conditions, scope boundaries, and explicit human review. v0.69 represents a scientific theory as a challengeable model of explanation; conceptual coherence is not scientific proof.</p></div><span class="sc-th0690__badge">PROJECT / THEORY</span></div>
            <p class="sc-th0690__status" data-theory-v0690-status role="status" aria-live="polite">Scientific Theory workspace loading…</p>
            <div class="sc-th0690__boundary"><strong>Governance boundary:</strong> a theory-bounded result means the conceptual structure, predictions, evidence links, falsification boundaries, and human scope review are explicit. It does not establish causal truth, universal generalization, or empirical validity outside the linked evidence.</div>
            <div class="sc-th0690__actions"><button type="button" class="sc-lab-button" data-theory-v0690-use-project>Use active project context</button><button type="button" class="sc-lab-button" data-theory-v0690-defaults>Load theory boundaries</button><button type="button" class="sc-lab-button" data-theory-v0690-save-theory>Save theory definition</button><button type="button" class="sc-lab-button" data-theory-v0690-graph>Build conceptual graph</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-theory-v0690-evaluate>Evaluate theory</button><button type="button" class="sc-lab-button" data-theory-v0690-packet>Build theory packet</button><button type="button" class="sc-lab-button" data-theory-v0690-verify>Verify packet</button><button type="button" class="sc-lab-button" data-theory-v0690-save-evidence>Save theory evidence</button></div>
            <div class="sc-th0690__metrics" data-theory-v0690-metrics></div>
            <div class="sc-th0690__grid">
              <section class="sc-th0690__card"><h5>Theory definition</h5><div class="sc-th0690__fields"><label>Theory ID<input data-theory-v0690-theory-id value="scientific-theory-1"></label><label>Theory type<select data-theory-v0690-type><option value="conceptual-model">Conceptual model</option><option value="mechanistic-theory">Mechanistic theory</option><option value="systems-theory">Systems theory</option><option value="causal-theory">Causal theory</option><option value="integrative-framework">Integrative framework</option><option value="custom">Custom</option></select></label><label>Title<input data-theory-v0690-title value="Scientific theory"></label><label>Study ID<input data-theory-v0690-study-id placeholder="study-1"></label><label class="is-wide">Linked v0.62 claim IDs<textarea data-theory-v0690-claims placeholder="claim-1"></textarea></label><label class="is-wide">Linked v0.66 hypothesis IDs<textarea data-theory-v0690-hypotheses placeholder="hypothesis-1"></textarea></label><label class="is-wide">Linked model IDs<textarea data-theory-v0690-models placeholder="hierarchical-model-1"></textarea></label><label class="is-wide">Purpose<textarea data-theory-v0690-purpose></textarea></label><label class="is-wide">Core mechanism<textarea data-theory-v0690-mechanism placeholder="State the proposed mechanism without treating it as proven."></textarea></label><label class="is-wide">Scope boundary<textarea data-theory-v0690-scope></textarea></label><label class="is-wide">Assumptions<textarea data-theory-v0690-assumptions></textarea></label><label class="is-wide">Limitations<textarea data-theory-v0690-limitations></textarea></label></div><h5>Human theory review</h5><div class="sc-th0690__fields"><label>Decision<select data-theory-v0690-review-decision><option value="accept-within-scope">Accept within stated scope</option><option value="accept-with-qualification">Accept with qualification</option><option value="block">Block interpretation</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Rationale<textarea data-theory-v0690-review-rationale placeholder="Address construct validity, mechanisms, alternatives, prediction quality, falsifiability, evidence linkage, scope, and limitations."></textarea></label></div><button type="button" class="sc-lab-button" data-theory-v0690-review>Record theory review</button></section>
              <section class="sc-th0690__card"><h5>Construct</h5><div class="sc-th0690__fields"><label>Construct ID<input data-theory-v0690-construct-id value="construct-1"></label><label>Role<select data-theory-v0690-construct-role><option value="exposure">Exposure</option><option value="outcome">Outcome</option><option value="mediator">Mediator</option><option value="moderator">Moderator</option><option value="confounder">Confounder</option><option value="latent">Latent</option><option value="mechanism">Mechanism</option><option value="context">Context</option><option value="state">State</option><option value="parameter">Parameter</option><option value="custom">Custom</option></select></label><label>Name<input data-theory-v0690-construct-name value="Construct"></label><label>Unit / scale<input data-theory-v0690-construct-unit></label><label class="is-wide">Definition<textarea data-theory-v0690-construct-definition></textarea></label><label class="is-wide">Operationalization<textarea data-theory-v0690-construct-operationalization></textarea></label><label class="is-wide">Evidence refs<textarea data-theory-v0690-construct-evidence placeholder="claim-1"></textarea></label><label class="is-wide">Note<textarea data-theory-v0690-construct-note></textarea></label></div><button type="button" class="sc-lab-button" data-theory-v0690-add-construct>Save construct</button><h5>Project theory records</h5><div data-theory-v0690-saved><p>No v0.69 theory records saved.</p></div></section>
            </div>
            <div class="sc-th0690__grid">
              <section class="sc-th0690__card"><h5>Relation / mechanism</h5><div class="sc-th0690__fields"><label>Relation ID<input data-theory-v0690-relation-id value="relation-1"></label><label>Type<select data-theory-v0690-relation-type><option value="causes">Causes</option><option value="associates">Associates</option><option value="mediates">Mediates</option><option value="moderates">Moderates</option><option value="inhibits">Inhibits</option><option value="enables">Enables</option><option value="depends-on">Depends on</option><option value="feedback">Feedback</option><option value="transforms">Transforms</option><option value="constrains">Constrains</option><option value="custom">Custom</option></select></label><label>Source construct<input data-theory-v0690-source placeholder="construct-a"></label><label>Target construct<input data-theory-v0690-target placeholder="construct-b"></label><label class="is-wide">Mechanism<textarea data-theory-v0690-relation-mechanism></textarea></label><label>Equation / model ref<input data-theory-v0690-equation-ref></label><label>Causal assumption ref<input data-theory-v0690-causal-assumption-ref></label><label class="is-wide">Uncertainty note<textarea data-theory-v0690-relation-uncertainty></textarea></label><label class="is-wide">Evidence refs<textarea data-theory-v0690-relation-evidence></textarea></label></div><button type="button" class="sc-lab-button" data-theory-v0690-add-relation>Save relation</button></section>
              <section class="sc-th0690__card"><h5>Testable prediction</h5><div class="sc-th0690__fields"><label>Prediction ID<input data-theory-v0690-prediction-id value="prediction-1"></label><label>Hypothesis ID<input data-theory-v0690-prediction-hypothesis placeholder="hypothesis-1"></label><label class="is-wide">Prediction statement<textarea data-theory-v0690-prediction-statement></textarea></label><label>Expected direction<input data-theory-v0690-prediction-direction placeholder="positive / negative / nonlinear"></label><label class="is-wide">Discriminating against hypothesis IDs<textarea data-theory-v0690-prediction-rivals></textarea></label><label class="is-wide">Falsification condition<textarea data-theory-v0690-prediction-falsification placeholder="State the observation that would challenge this prediction."></textarea></label><label class="is-wide">Evidence refs<textarea data-theory-v0690-prediction-evidence></textarea></label><label class="is-wide">Note<textarea data-theory-v0690-prediction-note></textarea></label></div><button type="button" class="sc-lab-button" data-theory-v0690-add-prediction>Save prediction</button></section>
            </div>
            <div class="sc-th0690__grid"><section class="sc-th0690__card"><h5>Conceptual graph</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Source</th><th>Relation</th><th>Target</th><th>Mechanism hash</th></tr></thead><tbody data-theory-v0690-graph-rows><tr><td colspan="4">Build the conceptual graph to inspect theory relations.</td></tr></tbody></table></div><h5>Current gate</h5><p class="sc-th0690__gate" data-theory-v0690-gate data-gate="needs-review">needs-review</p></section><section class="sc-th0690__card"><h5>Theory evaluation / packet evidence</h5><pre class="sc-th0690__output" data-theory-v0690-output>No v0.69 scientific theory evidence generated yet.</pre></section></div>
            <p class="sc-th0690__note">v0.69 stores conceptual metadata, hashes, definitions, relations, predictions, evidence references, falsification conditions, scope, limitations, and human review. Raw datasets, automatic theory proof, automatic causal certification, universal generalization, arbitrary code, and network fetching during evaluation are excluded.</p>
          </div>
        </details>


        <details class="sc-pr0700" data-preregistration-v0700>
          <summary>Research Questions, Hypothesis Registry &amp; Preregistration <span class="sc-pr0700__badge">v0.70.0</span></summary>
          <div class="sc-pr0700__body">
            <div class="sc-pr0700__intro"><div><h4>Freeze the scientific plan before results are interpreted</h4><p>Register explicit research questions, hypotheses, outcomes, analysis rules, exclusions, stopping rules, information-size rationale, and sensitivity plans. Freeze the registered metadata before outcome results are inspected, then disclose post-freeze deviations without rewriting the original plan.</p></div><span class="sc-pr0700__badge">PROJECT / PREREGISTRATION</span></div>
            <p class="sc-pr0700__status" data-prereg-v0700-status role="status" aria-live="polite">Preregistration workspace loading…</p>
            <div class="sc-pr0700__boundary"><strong>Governance boundary:</strong> preregistration-bounded does not mean the hypothesis is true or the study is bias-free. It means the pre-result plan, frozen snapshot, declared deviations, scope, limitations, and human review are explicit and tamper-evident.</div>
            <div class="sc-pr0700__actions"><button type="button" class="sc-lab-button" data-prereg-v0700-use-project>Use active project context</button><button type="button" class="sc-lab-button" data-prereg-v0700-defaults>Load preregistration boundaries</button><button type="button" class="sc-lab-button" data-prereg-v0700-save>Save plan</button><button type="button" class="sc-lab-button" data-prereg-v0700-freeze>Freeze preregistration</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-prereg-v0700-evaluate>Evaluate registration</button><button type="button" class="sc-lab-button" data-prereg-v0700-packet>Build packet</button><button type="button" class="sc-lab-button" data-prereg-v0700-verify>Verify packet</button><button type="button" class="sc-lab-button" data-prereg-v0700-save-evidence>Save registration evidence</button></div>
            <div class="sc-pr0700__metrics" data-prereg-v0700-metrics></div>
            <div class="sc-pr0700__grid">
              <section class="sc-pr0700__card"><h5>Preregistration plan</h5><div class="sc-pr0700__fields"><label>Registration ID<input data-prereg-v0700-id value="preregistration-1"></label><label>Study ID<input data-prereg-v0700-study-id placeholder="study-1"></label><label class="is-wide">Title<input data-prereg-v0700-title value="Scientific preregistration"></label><label class="is-wide">Registered research-question IDs<textarea data-prereg-v0700-question-ids placeholder="rq-1"></textarea></label><label class="is-wide">Registered hypothesis IDs<textarea data-prereg-v0700-hypothesis-ids placeholder="registered-hypothesis-1"></textarea></label><label class="is-wide">Primary outcome<textarea data-prereg-v0700-primary-outcome></textarea></label><label class="is-wide">Secondary outcomes<textarea data-prereg-v0700-secondary-outcomes></textarea></label><label class="is-wide">Analysis plan<textarea data-prereg-v0700-analysis-plan></textarea></label><label class="is-wide">Inclusion criteria<textarea data-prereg-v0700-inclusion></textarea></label><label class="is-wide">Exclusion criteria<textarea data-prereg-v0700-exclusion></textarea></label><label class="is-wide">Stopping rule<textarea data-prereg-v0700-stopping-rule></textarea></label><label class="is-wide">Sample / information-size rationale<textarea data-prereg-v0700-sample-size></textarea></label><label class="is-wide">Missing-data plan<textarea data-prereg-v0700-missing-data></textarea></label><label class="is-wide">Multiplicity plan<textarea data-prereg-v0700-multiplicity></textarea></label><label class="is-wide">Sensitivity plan<textarea data-prereg-v0700-sensitivity></textarea></label><label>Results access state<select data-prereg-v0700-results-state><option value="unknown">Unknown</option><option value="not-inspected">Not inspected</option><option value="inspected">Inspected</option></select></label><label class="is-wide">Pre-result attestation<textarea data-prereg-v0700-attestation></textarea></label><label class="is-wide">Scope boundary<textarea data-prereg-v0700-scope></textarea></label><label class="is-wide">Limitations<textarea data-prereg-v0700-limitations></textarea></label></div><h5>Human preregistration review</h5><div class="sc-pr0700__fields"><label>Decision<select data-prereg-v0700-review-decision><option value="accept-within-scope">Accept within stated scope</option><option value="accept-with-qualification">Accept with qualification</option><option value="block">Block interpretation</option><option value="reopen">Reopen</option></select></label><label class="is-wide">Rationale<textarea data-prereg-v0700-review-rationale placeholder="Review the frozen plan, hypotheses, outcome hierarchy, analysis rules, deviations, scope, and limitations."></textarea></label></div><button type="button" class="sc-lab-button" data-prereg-v0700-review>Record preregistration review</button></section>
              <section class="sc-pr0700__card"><h5>Research question</h5><div class="sc-pr0700__fields"><label>Question ID<input data-prereg-v0700-question-id value="rq-1"></label><label>Question type<select data-prereg-v0700-question-type><option value="causal">Causal</option><option value="descriptive">Descriptive</option><option value="associational">Associational</option><option value="predictive">Predictive</option><option value="mechanistic">Mechanistic</option><option value="comparative">Comparative</option><option value="custom">Custom</option></select></label><label class="is-wide">Research question<textarea data-prereg-v0700-question></textarea></label><label class="is-wide">Rationale<textarea data-prereg-v0700-question-rationale></textarea></label><label class="is-wide">Population boundary<textarea data-prereg-v0700-population></textarea></label><label class="is-wide">Exposure / intervention<textarea data-prereg-v0700-exposure></textarea></label><label class="is-wide">Comparator<textarea data-prereg-v0700-comparator></textarea></label><label class="is-wide">Outcome boundary<textarea data-prereg-v0700-outcome-boundary></textarea></label><label>Time horizon<input data-prereg-v0700-time-horizon></label><label class="is-wide">Linked v0.69 theory IDs<textarea data-prereg-v0700-theory-ids></textarea></label><label class="is-wide">Linked v0.62 claim IDs<textarea data-prereg-v0700-claim-ids></textarea></label><label class="is-wide">Note<textarea data-prereg-v0700-question-note></textarea></label></div><button type="button" class="sc-lab-button" data-prereg-v0700-add-question>Save research question</button><h5>Project registration records</h5><div data-prereg-v0700-saved><p>No v0.70 registration records saved.</p></div></section>
            </div>
            <div class="sc-pr0700__grid">
              <section class="sc-pr0700__card"><h5>Hypothesis registry</h5><div class="sc-pr0700__fields"><label>Hypothesis ID<input data-prereg-v0700-hypothesis-id value="registered-hypothesis-1"></label><label>Role<select data-prereg-v0700-hypothesis-role><option value="primary">Primary</option><option value="secondary">Secondary</option><option value="exploratory">Exploratory</option><option value="null">Null</option><option value="alternative">Alternative</option><option value="mechanistic">Mechanistic</option><option value="custom">Custom</option></select></label><label>Research question ID<input data-prereg-v0700-hypothesis-question value="rq-1"></label><label>Direction<select data-prereg-v0700-hypothesis-direction><option value="positive">Positive</option><option value="negative">Negative</option><option value="non-directional">Non-directional</option><option value="nonlinear">Nonlinear</option><option value="equivalence">Equivalence</option><option value="non-inferiority">Non-inferiority</option><option value="custom">Custom</option></select></label><label>Linked v0.66 hypothesis<input data-prereg-v0700-argument-hypothesis></label><label>Linked v0.69 prediction<input data-prereg-v0700-theory-prediction></label><label class="is-wide">Hypothesis statement<textarea data-prereg-v0700-hypothesis-statement></textarea></label><label>Outcome ref<input data-prereg-v0700-hypothesis-outcome></label><label>Exposure ref<input data-prereg-v0700-hypothesis-exposure></label><label class="is-wide">Effect / contrast<textarea data-prereg-v0700-effect-contrast></textarea></label><label class="is-wide">Falsification boundary<textarea data-prereg-v0700-hypothesis-falsification></textarea></label><label class="is-wide">Note<textarea data-prereg-v0700-hypothesis-note></textarea></label></div><button type="button" class="sc-lab-button" data-prereg-v0700-add-hypothesis>Register hypothesis</button></section>
              <section class="sc-pr0700__card"><h5>Post-freeze deviation log</h5><p>Do not edit the frozen snapshot to make later choices look preregistered. Record the change here instead.</p><div class="sc-pr0700__fields"><label>Deviation ID<input data-prereg-v0700-deviation-id value="deviation-1"></label><label>Type<select data-prereg-v0700-deviation-type><option value="analysis">Analysis</option><option value="outcome">Outcome</option><option value="research-question">Research question</option><option value="hypothesis">Hypothesis</option><option value="exclusion">Exclusion</option><option value="stopping-rule">Stopping rule</option><option value="sample-size">Sample size</option><option value="missing-data">Missing data</option><option value="multiplicity">Multiplicity</option><option value="sensitivity">Sensitivity</option><option value="other">Other</option></select></label><label>Section ref<input data-prereg-v0700-deviation-section></label><label>Discovered at<input data-prereg-v0700-deviation-discovered placeholder="ISO 8601 timestamp"></label><label class="is-wide">Description<textarea data-prereg-v0700-deviation-description></textarea></label><label class="is-wide">Rationale<textarea data-prereg-v0700-deviation-rationale></textarea></label><label class="is-wide">Impact on interpretation<textarea data-prereg-v0700-deviation-impact></textarea></label><label class="is-wide">Evidence refs<textarea data-prereg-v0700-deviation-evidence></textarea></label></div><button type="button" class="sc-lab-button" data-prereg-v0700-add-deviation>Log deviation</button></section>
            </div>
            <div class="sc-pr0700__grid"><section class="sc-pr0700__card"><h5>Current gate</h5><p class="sc-pr0700__gate" data-prereg-v0700-gate data-gate="needs-freeze">needs-freeze</p><p>A freeze records hashes of the registered questions, hypotheses, outcomes, analysis plan, exclusions, stopping rule, and other prespecified boundaries. Changes after freeze must be disclosed as deviations.</p></section><section class="sc-pr0700__card"><h5>Preregistration evaluation / packet evidence</h5><pre class="sc-pr0700__output" data-prereg-v0700-output>No v0.70 preregistration evidence generated yet.</pre></section></div>
            <p class="sc-pr0700__note">v0.70 stores governed research metadata, hashes, freeze snapshots, deviation records, scope, limitations, and human review. Raw datasets, participant-level records, automatic hypothesis validation, automatic post-hoc preregistration, automatic outcome reclassification, arbitrary code, and network fetching during evaluation are excluded.</p>
          </div>
        </details>

        <details class="sc-bfd0601" data-beta-field-diagnostics-v0601>
          <summary>Beta Field Diagnostics, Integration Soak &amp; Runtime Repair <span class="sc-bfd0601__badge">v0.60.1</span></summary>
          <div class="sc-bfd0601__body">
            <div class="sc-bfd0601__intro"><div><h4>Exercise the integrated beta before adding more science</h4><p>Capture a metadata-only runtime snapshot, localize cross-studio failures, and run a bounded four-cycle WordPress ↔ compute integration soak. The diagnostic layer reports repair evidence and failure domains; it does not mutate scientific state or send external telemetry.</p></div><span class="sc-bfd0601__badge">BETA / FIELD</span></div>
            <p class="sc-bfd0601__status" data-bfd-v0601-status role="status" aria-live="polite">Beta field diagnostics loading…</p>
            <div class="sc-bfd0601__actions">
              <button type="button" class="sc-lab-button" data-bfd-v0601-capture>Capture runtime snapshot</button>
              <button type="button" class="sc-lab-button" data-bfd-v0601-probe>Run integration probe</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-bfd-v0601-soak-button>Run bounded integration soak</button>
              <button type="button" class="sc-lab-button" data-bfd-v0601-packet>Build diagnostic packet</button>
              <button type="button" class="sc-lab-button" data-bfd-v0601-verify>Verify packet</button>
              <button type="button" class="sc-lab-button" data-bfd-v0601-save>Save diagnostic evidence</button>
            </div>
            <div class="sc-bfd0601__metrics" data-bfd-v0601-metrics></div>
            <div class="sc-bfd0601__grid">
              <section class="sc-bfd0601__card"><h5>Endpoint soak</h5><div class="sc-bfd0601__soak" data-bfd-v0601-soak><p>No soak result yet.</p></div><h5>Failure domains</h5><div class="sc-bfd0601__domains" data-bfd-v0601-domains><span>none</span></div><h5>Repair evidence</h5><ul class="sc-bfd0601__hints" data-bfd-v0601-hints><li>Run the integration probe to localize a failure.</li></ul></section>
              <section class="sc-bfd0601__card"><h5>Diagnostic evidence</h5><pre class="sc-bfd0601__output" data-bfd-v0601-output>No beta field diagnostic evidence generated yet.</pre></section>
            </div>
            <p class="sc-bfd0601__note">The soak is bounded and user initiated. Runtime metadata, endpoint status/latency, hashes, and failure categories may be retained; raw datasets, credentials, model inputs, automatic repairs, and external telemetry are excluded.</p>
          </div>
        </details>
        <details class="sc-wfc0570" data-scientific-workflow-v0570 open>
          <summary>Scientific Workflow Composer <span class="sc-wfc0570__badge">v0.57.0</span></summary>
          <div class="sc-wfc0570__body">
            <div class="sc-wfc0570__intro"><div><h4>Compose reproducible scientific pipelines</h4><p>Connect governed Lab stages into a saved, rerunnable research workflow. v0.57 executes registered scientific adapters only; arbitrary code, external callbacks, automatic experiment execution, registry promotion, and publication remain disabled.</p></div><span class="sc-wfc0570__badge">PROJECT / WORKFLOW</span></div>
            <p class="sc-wfc0570__status" data-wfc-v0570-status role="status" aria-live="polite">Workflow Composer loading…</p>
            <div class="sc-wfc0570__toolbar">
              <label>Template<select data-wfc-v0570-template></select></label>
              <label>Workflow title<input data-wfc-v0570-title value="Scientific workflow"></label>
              <div class="sc-wfc0570__actions"><button type="button" class="sc-lab-button" data-wfc-v0570-load-template>Load template</button><button type="button" class="sc-lab-button" data-wfc-v0570-use-dataset>Use project dataset</button></div>
            </div>
            <div class="sc-wfc0570__catalog" data-wfc-v0570-catalog aria-label="Registered scientific workflow stages"></div>
            <div class="sc-wfc0570__pipeline" data-wfc-v0570-pipeline><p>No workflow loaded.</p></div>
            <div class="sc-wfc0570__actions">
              <button type="button" class="sc-lab-button" data-wfc-v0570-validate>Validate workflow</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-wfc-v0570-run>Run workflow</button>
              <button type="button" class="sc-lab-button" data-wfc-v0570-rerun>Rerun / compare</button>
              <button type="button" class="sc-lab-button" data-wfc-v0570-save-workflow>Save workflow</button>
              <button type="button" class="sc-lab-button" data-wfc-v0570-save-run>Save run evidence</button>
            </div>
            <div class="sc-wfc0570__metrics" data-wfc-v0570-metrics></div>
            <div class="sc-wfc0570__grid">
              <section class="sc-wfc0570__card"><h5>Stage timeline</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Stage</th><th>Kind</th><th>Status</th><th>ms</th><th>Output hash</th></tr></thead><tbody data-wfc-v0570-timeline><tr><td colspan="5">No workflow run yet.</td></tr></tbody></table></div></section>
              <section class="sc-wfc0570__card"><h5>Saved project workflows</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Workflow</th><th>Stages</th><th>Hash</th><th>Action</th></tr></thead><tbody data-wfc-v0570-saved><tr><td colspan="4">No saved v0.57 workflows in this project.</td></tr></tbody></table></div></section>
            </div>
            <details class="sc-wfc0570__advanced"><summary>Workflow definition and run inputs</summary><div class="sc-wfc0570__advanced-grid"><label>Workflow JSON<textarea data-wfc-v0570-definition aria-label="Scientific workflow definition">{}</textarea></label><label>Run inputs JSON<textarea data-wfc-v0570-inputs aria-label="Scientific workflow inputs">{}</textarea></label></div><h5>Latest run record</h5><pre data-wfc-v0570-output>No workflow run yet.</pre></details>
          </div>
        </details>
        <details class="sc-ch0580" data-compute-hardening-v0580>
          <summary>Large workload &amp; compute hardening <span class="sc-ch0580__badge">v0.58.0</span></summary>
          <div class="sc-ch0580__body">
            <div class="sc-ch0580__intro"><div><h4>Keep scientific workflows responsive at scale</h4><p>Assess workload size before execution, queue large runs without blocking the interface, reuse deterministic cached results, inspect bounded dataset windows, and request cooperative cancellation. Running scientific code is never force-terminated and arbitrary executable jobs remain disabled.</p></div><span class="sc-ch0580__badge">PROJECT / COMPUTE</span></div>
            <p class="sc-ch0580__status" data-ch-v0580-status role="status" aria-live="polite">Compute hardening loading…</p>
            <div class="sc-ch0580__actions">
              <button type="button" class="sc-lab-button" data-ch-v0580-assess>Assess current workflow</button>
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-ch-v0580-queue>Queue workflow asynchronously</button>
              <button type="button" class="sc-lab-button" data-ch-v0580-refresh>Refresh compute jobs</button>
            </div>
            <div class="sc-ch0580__metrics" data-ch-v0580-metrics></div>
            <div class="sc-ch0580__grid">
              <section class="sc-ch0580__card"><h5>Recent hardened compute jobs</h5><div class="sc-lab-table-wrap"><table><thead><tr><th>Job</th><th>Operation</th><th>Status</th><th>Cache</th><th>Action</th></tr></thead><tbody data-ch-v0580-jobs><tr><td colspan="5">No hardened compute jobs yet.</td></tr></tbody></table></div></section>
              <section class="sc-ch0580__card"><h5>Assessment / result evidence</h5><pre class="sc-ch0580__output" data-ch-v0580-output>Assess the current workflow or queue it for bounded asynchronous execution.</pre></section>
            </div>
          </div>
        </details>
        <details class="sc-audit0590" data-scientific-audit-v0590>
          <summary>Security, privacy, reproducibility &amp; scientific audit <span class="sc-audit0590__badge">v0.59.0</span></summary>
          <div class="sc-audit0590__body">
            <div class="sc-audit0590__intro"><div><h4>Audit research evidence before preservation or external sharing</h4><p>Scan the active scientific workflow for prohibited executable fields, secret/credential leakage, direct identifiers, data-minimization concerns, and missing reproducibility evidence. Findings record paths and categories only; sensitive values are not echoed into the audit report.</p></div><span class="sc-audit0590__badge">PROJECT / AUDIT</span></div>
            <p class="sc-audit0590__status" data-audit-v0590-status role="status" aria-live="polite">Scientific audit loading…</p>
            <div class="sc-audit0590__controls">
              <label>Research purpose / minimization note<textarea rows="2" data-audit-v0590-purpose placeholder="State why the dataset fields are necessary for this scientific workflow."></textarea></label>
              <label>Required dataset columns<input data-audit-v0590-required placeholder="temperature, canopy, site_id"></label>
            </div>
            <div class="sc-audit0590__actions">
              <button type="button" class="sc-lab-button sc-lab-button-primary" data-audit-v0590-audit>Audit current workflow</button>
              <button type="button" class="sc-lab-button" data-audit-v0590-minimize>Review dataset minimization</button>
              <button type="button" class="sc-lab-button" data-audit-v0590-redact>Build redacted export</button>
              <button type="button" class="sc-lab-button" data-audit-v0590-verify>Verify audit hash</button>
              <button type="button" class="sc-lab-button" data-audit-v0590-save>Save audit evidence</button>
              <button type="button" class="sc-lab-button" data-audit-v0590-download>Download redacted export</button>
            </div>
            <div class="sc-audit0590__metrics" data-audit-v0590-metrics></div>
            <pre class="sc-audit0590__output" data-audit-v0590-output>No v0.59 scientific audit has been run yet.</pre>
            <p class="sc-audit0590__note">Audit results are decision support, not certification. Automatic publication, deletion, high-stakes decisions, and scientific certification remain disabled.</p>
          </div>
        </details>
        <p class="sc-wf0321-status" data-wf-v0321-status role="status" aria-live="polite">Workflow recovery loading…</p>
        <div class="sc-wf0321-metrics" data-wf-v0321-metrics></div>
        <div class="sc-wf0321-grid">
          <div class="sc-wf0321-card">
            <h4>Workflow definition</h4>
            <p>Conditions are declarative data only. Arbitrary Python, shell code, JavaScript, and callback URLs are rejected.</p>
            <textarea data-wf-v0321-definition aria-label="Scientific workflow JSON">{
  "id": "calibration-pipeline",
  "title": "Calibration pipeline",
  "projectId": "default",
  "nodes": [
    {
      "id": "profile-dataset",
      "method": "dataset.profile",
      "request": {"inputs": {"records": []}},
      "priority": 70
    },
    {
      "id": "calibrate-model",
      "method": "model.calibrate",
      "dependsOn": ["profile-dataset"],
      "condition": {"source": "run.inputs.runCalibration", "operator": "equals", "value": true},
      "bindings": [
        {"fromNode": "profile-dataset", "sourcePath": "result.profile", "targetPath": "inputs.datasetProfile"}
      ],
      "request": {"inputs": {"model": "linear"}},
      "checkpointingRequired": true,
      "artifactOutputs": [{"kind": "result", "name": "calibration-result"}]
    }
  ]
}</textarea>
            <div class="sc-wf0321-actions"><button type="button" class="sc-lab-button" data-wf-v0321-validate>Validate graph</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-wf-v0321-save>Save definition</button></div>
          </div>
          <div class="sc-wf0321-card">
            <h4>Run controls</h4>
            <label>Workflow ID <input data-wf-v0321-workflowid value="calibration-pipeline"></label>
            <label>Run inputs <textarea data-wf-v0321-inputs aria-label="Workflow run inputs">{"runCalibration":true}</textarea></label>
            <label>Workflow run ID <input data-wf-v0321-runid placeholder="workflow-run-…"></label>
            <label>Operator reason <input data-wf-v0321-reason value="operator action from Lab workflow panel"></label>
            <div class="sc-wf0321-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wf-v0321-start>Start run</button><button type="button" class="sc-lab-button" data-wf-v0321-inspect>Reconcile and inspect</button><button type="button" class="sc-lab-button" data-wf-v0321-cancel>Cancel run</button><button type="button" class="sc-lab-button" data-wf-v0321-refresh>Refresh</button></div>
          </div>
          <div class="sc-wf0321-card">
            <h4>Partial recovery</h4>
            <label>Restart node IDs <input data-wf-v0321-restartnodes placeholder="calibrate-model, publish-report"></label>
            <label class="sc-wf0321-check"><input type="checkbox" checked data-wf-v0321-downstream> Include downstream dependents</label>
            <label class="sc-wf0321-check"><input type="checkbox" checked data-wf-v0321-resume> Reuse latest checkpoints</label>
            <div class="sc-wf0321-actions"><button type="button" class="sc-lab-button" data-wf-v0321-plan>Preview recovery</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-wf-v0321-recover>Start recovery run</button></div>
          </div>
          <div class="sc-wf0321-card">
            <h4>Checkpoint controls</h4>
            <label>Node ID <input data-wf-v0321-nodeid placeholder="calibrate-model"></label>
            <label>Checkpoint payload <textarea data-wf-v0321-checkpoint aria-label="Checkpoint payload">{"state":{"iteration":1},"progress":0.1,"message":"operator checkpoint"}</textarea></label>
            <div class="sc-wf0321-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wf-v0321-recordcheckpoint>Record checkpoint</button><button type="button" class="sc-lab-button" data-wf-v0321-listcheckpoints>List checkpoints</button></div>
          </div>
          <div class="sc-wf0321-card is-wide"><h4>Workflow runs</h4><div class="sc-lab-table-wrap"><table><thead><tr><th>Run</th><th>Workflow</th><th>Project</th><th>Status</th><th>Recovery generation</th><th>Updated</th><th>Action</th></tr></thead><tbody data-wf-v0321-runs></tbody></table></div></div>
          <div class="sc-wf0321-card is-wide"><h4>Definition, run state, checkpoints, and timeline</h4><pre class="sc-wf0321-output" data-wf-v0321-output>No response yet.</pre></div>
        </div>
      </section>



      <section class="sc-lab-panel sc-wa0322" data-lab-module="workflow-automation" data-module-panel="workflow-automation" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / WORKFLOW AUTOMATION / v0.32.2</p><h3>Scheduled and Event-Driven Research Runs</h3><p>Run saved scientific workflows from durable UTC schedules or authenticated external events, with missed-run recovery, duplicate-event protection, concurrency policies, firing history, and direct workflow-run provenance.</p></header>
        <p class="sc-wa0322-status" data-wa-v0322-status role="status" aria-live="polite">Workflow automation loading…</p>
        <div class="sc-wa0322-metrics" data-wa-v0322-metrics></div>
        <div class="sc-wa0322-grid">
          <div class="sc-wa0322-card"><h4>Schedule definition</h4><textarea data-wa-v0322-schedule aria-label="Workflow schedule JSON">{
  "id": "daily-calibration",
  "workflowId": "calibration-pipeline",
  "title": "Daily calibration",
  "trigger": {"type": "cron", "expression": "0 13 * * 1-5", "timezone": "UTC"},
  "run": {
    "inputs": {"runCalibration": true},
    "misfirePolicy": "catch-up-one",
    "misfireGraceSeconds": 900,
    "concurrencyPolicy": "forbid",
    "maxConcurrentRuns": 1
  }
}</textarea><div class="sc-wa0322-actions"><button type="button" class="sc-lab-button" data-wa-v0322-validate>Validate</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-wa-v0322-save>Save schedule</button></div></div>
          <div class="sc-wa0322-card"><h4>Manual and scheduler controls</h4><label>Schedule ID<input data-wa-v0322-scheduleid value="daily-calibration"></label><label>Run override JSON<textarea data-wa-v0322-override>{}</textarea></label><div class="sc-wa0322-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wa-v0322-trigger>Trigger now</button><button type="button" class="sc-lab-button" data-wa-v0322-tick>Run scheduler tick</button><button type="button" class="sc-lab-button" data-wa-v0322-refresh>Refresh</button></div></div>
          <div class="sc-wa0322-card"><h4>Event ingestion</h4><p>Backend event routes require normal compute authentication. Deployments may additionally require an HMAC event signature.</p><textarea data-wa-v0322-event aria-label="Workflow event JSON">{"id":"dataset-created-001","type":"dataset.created","payload":{"projectId":"default","datasetId":"dataset-001"}}</textarea><div class="sc-wa0322-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wa-v0322-ingest>Ingest event</button></div></div>
          <div class="sc-wa0322-card is-wide"><h4>Saved schedules</h4><div class="sc-lab-table-wrap"><table class="sc-wa0322-table"><thead><tr><th>Schedule</th><th>Workflow</th><th>Trigger</th><th>Status</th><th>Next fire</th><th>Actions</th></tr></thead><tbody data-wa-v0322-schedules></tbody></table></div></div>
          <div class="sc-wa0322-card is-wide"><h4>Automation state, firings, and event receipts</h4><pre class="sc-wa0322-output" data-wa-v0322-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-ec0331" data-lab-module="experiment-campaigns" data-module-panel="experiment-campaigns" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / ADAPTIVE EXPERIMENTS / v0.33.1</p><h3>Bayesian Optimization, Active Learning, and Resource-Aware Search</h3><p>Fit an inspectable Gaussian-process surrogate to completed workflow trials, quantify predictive uncertainty, select the next experiment with governed acquisition policies, and trade expected scientific value against explicit resource costs.</p></header>
        <p class="sc-ec0331-status" data-ec-v0331-status role="status" aria-live="polite">Bayesian campaign engine loading…</p>
        <div class="sc-ec0331-metrics" data-ec-v0331-metrics></div>
        <div class="sc-ec0331-grid">
          <div class="sc-ec0331-card is-wide"><h4>Campaign definition</h4><textarea data-ec-v0331-definition aria-label="Bayesian experiment campaign JSON">{
  "id": "bayesian-calibration-campaign",
  "title": "Resource-aware Bayesian calibration",
  "workflowId": "calibration-pipeline",
  "projectId": "default",
  "parameterSpace": {
    "learningRate": {"type": "continuous", "min": 0.001, "max": 0.1, "precision": 6},
    "iterations": {"type": "integer", "min": 50, "max": 500, "step": 50},
    "solver": {"type": "categorical", "values": ["least-squares", "robust"]}
  },
  "objective": {"path": "nodes.calibrate-model.result.metrics.rmse", "goal": "minimize", "target": 0.05},
  "strategy": {
    "type": "resource-aware-bayesian",
    "initialRandomTrials": 6,
    "kernel": "matern52",
    "acquisition": "expected-improvement",
    "candidatePoolSize": 512,
    "lengthScale": 0.35,
    "observationNoise": 0.000001,
    "improvementThreshold": 0.001,
    "costExponent": 1.0,
    "randomSeed": 3310
  },
  "resourceModel": {
    "enabled": true,
    "baseCost": 1,
    "parameterWeights": {"iterations": 4},
    "categoricalCosts": {"solver": {"robust": 2}},
    "resultCostPath": "nodes.calibrate-model.result.metrics.computeCost",
    "maxEstimatedCostPerTrial": 10,
    "maxTotalCost": 100
  },
  "budget": {"maxTrials": 40, "maxFailures": 6, "maxConcurrentTrials": 1},
  "stopping": {"patience": 10, "minImprovement": 0.001, "target": 0.05},
  "run": {"parameterInputPath": "campaign.parameters", "baseInputs": {"runCalibration": true}, "autoAdvance": true}
}</textarea><div class="sc-ec0331-actions"><button type="button" class="sc-lab-button" data-ec-v0331-validate>Validate definition</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-ec-v0331-save>Save campaign</button></div></div>
          <div class="sc-ec0331-card"><h4>Campaign and model controls</h4><label>Campaign ID<input data-ec-v0331-campaignid value="bayesian-calibration-campaign"></label><label>Trials to propose<input type="number" min="1" max="100" value="1" data-ec-v0331-count></label><label>Operator reason<input data-ec-v0331-reason value="operator action from Lab Bayesian campaign panel"></label><div class="sc-ec0331-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ec-v0331-start>Start</button><button type="button" class="sc-lab-button" data-ec-v0331-preview>Preview proposal</button><button type="button" class="sc-lab-button" data-ec-v0331-surrogate>Inspect surrogate</button><button type="button" class="sc-lab-button" data-ec-v0331-pause>Pause</button><button type="button" class="sc-lab-button" data-ec-v0331-resume>Resume</button><button type="button" class="sc-lab-button" data-ec-v0331-advance>Propose next</button><button type="button" class="sc-lab-button" data-ec-v0331-reconcile>Reconcile</button><button type="button" class="sc-lab-button" data-ec-v0331-inspect>Inspect</button><button type="button" class="sc-lab-button" data-ec-v0331-tick>Run campaign tick</button><button type="button" class="sc-lab-button" data-ec-v0331-refresh>Refresh</button><button type="button" class="sc-lab-button" data-ec-v0331-cancel>Cancel</button></div></div>
          <div class="sc-ec0331-card"><h4>Manual observation</h4><p>Import an external, simulation, or instrument observation with both objective and resource cost so it can train the same surrogate.</p><textarea data-ec-v0331-observation aria-label="Manual Bayesian observation JSON">{
  "parameters": {"learningRate": 0.01, "iterations": 200, "solver": "least-squares"},
  "objectiveValue": 0.082,
  "costValue": 2.4,
  "source": "instrument bench run",
  "result": {"notes": "Imported observation"}
}</textarea><div class="sc-ec0331-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ec-v0331-observe>Record observation</button></div><p class="sc-ec0331-note"><strong>Safety:</strong> the surrogate proposes only typed parameter values. It cannot execute arbitrary code, shell commands, callback URLs, or unregistered methods.</p></div>
          <div class="sc-ec0331-card is-wide"><h4>Saved campaigns</h4><div class="sc-lab-table-wrap"><table class="sc-ec0331-table"><thead><tr><th>Campaign</th><th>Workflow</th><th>Strategy</th><th>Status</th><th>Completed / budget</th><th>Best objective</th><th>Cost</th><th>Surrogate</th><th>Actions</th></tr></thead><tbody data-ec-v0331-campaigns></tbody></table></div></div>
          <div class="sc-ec0331-card is-wide"><h4>Campaign, surrogate, prediction, acquisition, trial, and timeline records</h4><pre class="sc-ec0331-output" data-ec-v0331-output>No response yet.</pre></div>
        </div>
      </section>


      <section class="sc-lab-panel sc-mr0340" data-lab-module="model-registry" data-module-panel="model-registry" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / MODEL GOVERNANCE / v0.34.0</p><h3>Scientific Model Registry and Environment Reproduction</h3><p>Register immutable scientific model versions, lock runtime and dependency environments, promote reviewed versions, preserve deprecation history, and export portable reproduction manifests with cryptographic verification.</p></header>
        <p data-mr-v0340-status role="status" aria-live="polite">Scientific model registry loading…</p>
        <div class="sc-mr0340-metrics" data-mr-v0340-metrics></div>
        <div class="sc-mr0340-grid">
          <div class="sc-mr0340-card is-wide"><h4>Register model version</h4><textarea data-mr-v0340-definition aria-label="Scientific model definition JSON">{
  "id": "heat-transfer-surrogate",
  "modelVersion": "1.0.0",
  "title": "Heat-transfer surrogate",
  "projectId": "default",
  "type": "registered-method",
  "methodId": "simulation.parameter_sweep",
  "sourceRevision": "replace-with-git-commit",
  "artifactIds": ["replace-with-model-artifact-id"],
  "defaultInputs": {"temperature": 350},
  "parameters": {"tolerance": 1e-8},
  "environment": {
    "id": "heat-transfer-python-312",
    "title": "Python 3.12 scientific environment",
    "runtime": {"pythonVersion": "3.12.12"},
    "container": {"image": "sc-lab-compute", "digest": "sha256:replace-with-digest"},
    "dependencies": [
      {"name": "numpy", "version": "2.2.0", "hashes": ["sha256:replace-with-wheel-hash"]},
      {"name": "scipy", "version": "1.15.0", "hashes": ["sha256:replace-with-wheel-hash"]}
    ]
  },
  "provenance": {"author": "Sustainable Catalyst Lab"}
}</textarea><div class="sc-mr0340-actions"><button type="button" class="sc-lab-button" data-mr-v0340-action="validate">Validate</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-mr-v0340-action="register">Register immutable version</button><button type="button" class="sc-lab-button" data-mr-v0340-action="refresh">Refresh</button></div></div>
          <div class="sc-mr0340-card"><h4>Version governance</h4><label>Model ID<input data-mr-v0340-modelid value="heat-transfer-surrogate"></label><label>Version or alias<input data-mr-v0340-version value="1.0.0"></label><label>Operator reason<input data-mr-v0340-reason value="Reviewed and validated for production use."></label><div class="sc-mr0340-actions"><button type="button" class="sc-lab-button" data-mr-v0340-action="inspect">Inspect</button><button type="button" class="sc-lab-button" data-mr-v0340-action="candidate">Promote candidate</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-mr-v0340-action="production">Promote production</button><button type="button" class="sc-lab-button" data-mr-v0340-action="archived">Archive</button><button type="button" class="sc-lab-button" data-mr-v0340-action="deprecate">Deprecate</button><button type="button" class="sc-lab-button" data-mr-v0340-action="timeline">Timeline</button></div><p class="sc-mr0340-note"><strong>Integrity rule:</strong> registered versions are immutable. Any change to model content, dependencies, artifacts, or execution parameters requires a new semantic version.</p></div>
          <div class="sc-mr0340-card"><h4>Capture environment</h4><textarea data-mr-v0340-environment aria-label="Environment capture JSON">{
  "id": "local-python-312",
  "title": "Local Python environment",
  "dependencies": [
    {"name": "numpy", "version": "2.2.0"},
    {"name": "scipy", "version": "1.15.0"}
  ],
  "sourceRevision": "replace-with-git-commit"
}</textarea><div class="sc-mr0340-actions"><button type="button" class="sc-lab-button" data-mr-v0340-action="capture">Capture environment lock</button></div></div>
          <div class="sc-mr0340-card is-wide"><h4>Registered model versions</h4><div class="sc-mr0340-table-wrap"><table class="sc-mr0340-table"><thead><tr><th>Model</th><th>Version</th><th>Type</th><th>Channel</th><th>Action</th></tr></thead><tbody data-mr-v0340-models></tbody></table></div></div>
          <div class="sc-mr0340-card"><h4>Reproduction manifest</h4><div class="sc-mr0340-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-mr-v0340-action="reproduction">Build manifest</button><button type="button" class="sc-lab-button" data-mr-v0340-action="verify">Verify manifest</button></div><textarea data-mr-v0340-manifest aria-label="Model reproduction manifest JSON">{}</textarea></div>
          <div class="sc-mr0340-card"><h4>Registry, environment, promotion, and verification records</h4><pre class="sc-mr0340-output" data-mr-v0340-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-lab-module sc-pa0480" data-lab-module="probabilistic-analysis" data-module-panel="probabilistic-analysis" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">MODEL / UNCERTAINTY &amp; SENSITIVITY / v0.53.0</p><h3>Integrated Uncertainty, Sensitivity &amp; Probabilistic Visualization</h3><p>Propagate explicit input and parameter uncertainty through safe declarative Model Studio models, represent independent or evidence-backed dependent inputs, quantify output distributions and threshold probabilities, inspect dependence-aware sensitivity, and carry probabilistic figures directly into Graph Studio.</p></header>
        <p class="sc-pa0480-status" data-pa-v0480-status role="status" aria-live="polite">Probabilistic analysis loading…</p>
        <div class="sc-pa0480-shell">
          <aside class="sc-pa0480-controls" aria-label="Probabilistic analysis controls">
            <section class="sc-pa0480-card"><h4>Model</h4><div class="sc-pa0480-model" data-pa-v0480-model>No model loaded.</div><div class="sc-pa0480-actions"><button type="button" class="sc-lab-button" data-pa-v0480-load-model>Use current Model Studio model</button><button type="button" class="sc-lab-button" data-pa-v0480-example>Load example</button></div></section>
            <section class="sc-pa0480-card"><h4>Study definition</h4><label>Study title<input data-pa-v0480-title></label><label>Fixed operating values <small>symbol=value, comma separated</small><input data-pa-v0480-fixed placeholder="x=5"></label><div class="sc-pa0480-inline"><label>Sampling design<select data-pa-v0480-method><option value="latin-hypercube">Latin hypercube</option><option value="monte-carlo">Monte Carlo</option><option value="sobol">Sobol sequence</option><option value="saltelli-sobol">Saltelli–Sobol sensitivity</option></select></label><label>Base samples<input type="number" min="16" max="65536" value="2048" data-pa-v0480-samples></label></div><div class="sc-pa0480-inline"><label>Seed<input type="number" value="42" data-pa-v0480-seed></label><label>Central interval<select data-pa-v0480-confidence><option value="0.90">90%</option><option value="0.95" selected>95%</option><option value="0.99">99%</option></select></label></div><label>Output thresholds <small>comma separated</small><input data-pa-v0480-thresholds placeholder="10, 20"></label></section>
            <section class="sc-pa0480-card"><h4>Uncertain inputs</h4><p class="sc-pa0480-note">Distributions are never inferred silently. Define them explicitly. When Model Studio provides parameter bounds, Lab may populate those bounds as a visible uniform starting point.</p><div class="sc-pa0480-inputs" data-pa-v0480-inputs></div><div class="sc-pa0480-actions"><button type="button" class="sc-lab-button" data-pa-v0480-add-input>Add uncertain input</button></div></section><section class="sc-pa0480-card sc-cu0530-card"><h4>Input dependence</h4><p class="sc-pa0480-note">Keep inputs independent unless you have evidence for dependence. Gaussian-copula dependence preserves each declared marginal distribution while applying an explicit latent correlation structure.</p><label>Dependency model<select data-pa-v0530-dependency-method><option value="independent" selected>Independent inputs</option><option value="gaussian-copula">Gaussian copula</option></select></label><label>Matrix interpretation<select data-pa-v0530-matrix-type><option value="correlation" selected>Correlation matrix</option><option value="covariance">Covariance matrix</option></select></label><label>Matrix <small>JSON; row/column order must match uncertain inputs</small><textarea data-pa-v0530-matrix rows="5" spellcheck="false">[[1,0],[0,1]]</textarea></label><label>Evidence/source note<input data-pa-v0530-source placeholder="e.g. observed dataset / published covariance"></label><p class="sc-pa0480-note">Dependent-input Saltelli–Sobol decomposition is intentionally blocked. Use Monte Carlo, Latin hypercube, or Sobol sequence sampling when dependence is active.</p></section>
            <section class="sc-pa0480-card"><h4>Uncertainty ribbon</h4><label><input type="checkbox" data-pa-v0480-curve-enabled> Propagate uncertainty across a deterministic X range</label><div class="sc-pa0480-inline"><label>X symbol<input data-pa-v0480-curve-symbol placeholder="x"></label><label>Points<input type="number" min="3" max="160" value="41" data-pa-v0480-curve-points></label></div><div class="sc-pa0480-inline"><label>Start<input type="number" step="any" value="0" data-pa-v0480-curve-start></label><label>Stop<input type="number" step="any" value="10" data-pa-v0480-curve-stop></label></div></section>
            <section class="sc-pa0480-card"><h4>Run &amp; preserve</h4><div class="sc-pa0480-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pa-v0480-run>Run uncertainty analysis</button><button type="button" class="sc-lab-button" data-pa-v0480-save>Save evidence</button><button type="button" class="sc-lab-button" data-pa-v0480-open-graph>Open figure in Graph Studio</button></div><p class="sc-pa0480-note">v0.53 studies support independent inputs or an explicit correlation/covariance dependency model. Dependence is never inferred silently and does not imply causality. Registered-model distributed ensembles remain available in the advanced ensemble module.</p></section>
          </aside>
          <div class="sc-pa0480-workspace">
            <div class="sc-pa0480-summary" data-pa-v0480-summary></div>
            <section class="sc-pa0480-canvas-card"><div class="sc-lab-panel-head"><div><span class="sc-lab-section-code">PROBABILITY / FIGURE</span><h4>Probabilistic visualization</h4></div><div class="sc-pa0480-tabs" role="toolbar" aria-label="Probabilistic figures"><button type="button" class="sc-lab-button" data-pa-v0480-graph="distribution" aria-pressed="false">Distribution</button><button type="button" class="sc-lab-button" data-pa-v0480-graph="cdf" aria-pressed="false">CDF</button><button type="button" class="sc-lab-button" data-pa-v0480-graph="sensitivity" aria-pressed="false">Sensitivity</button><button type="button" class="sc-lab-button" data-pa-v0480-graph="dependency" aria-pressed="false">Dependency</button><button type="button" class="sc-lab-button" data-pa-v0480-graph="uncertaintyBand" aria-pressed="false">Uncertainty ribbon</button></div></div><div class="sc-pa0480-canvas" data-pa-v0480-canvas></div></section>
            <div class="sc-pa0480-evidence-grid"><section class="sc-pa0480-evidence"><h4>Sensitivity evidence</h4><div data-pa-v0480-sensitivity-table></div></section><section class="sc-pa0480-evidence"><h4>Threshold probabilities</h4><div data-pa-v0480-threshold-table></div></section><section class="sc-pa0480-evidence"><h4>Dependency diagnostics</h4><div data-pa-v0530-dependency-summary><p class="sc-pa0480-note">Run a study to compare the declared dependency model with sampled dependence.</p></div></section></div>
            <details><summary>Probabilistic analysis record</summary><pre data-pa-v0480-record>No probabilistic analysis yet.</pre></details>
          </div>
        </div>
      </section>

      <section class="sc-lab-panel sc-eu0341" data-lab-module="ensemble-uncertainty" data-module-panel="ensemble-uncertainty" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / MODEL ANALYSIS / v0.34.1</p><h3>Ensemble Simulation, Global Sensitivity, and Uncertainty</h3><p>Run immutable registered-model ensembles through governed workers, propagate uncertain inputs, compare weighted model members, and quantify output distributions and global parameter influence.</p></header>
        <p data-eu-v0341-status role="status" aria-live="polite">Ensemble and uncertainty engine loading…</p>
        <div class="sc-eu0341-metrics" data-eu-v0341-metrics></div>
        <div class="sc-eu0341-grid">
          <div class="sc-eu0341-card is-wide"><h4>Ensemble study definition</h4><textarea data-eu-v0341-definition aria-label="Ensemble study JSON">{
  "id": "thermal-model-ensemble",
  "title": "Thermal model uncertainty study",
  "projectId": "default",
  "members": [
    {"modelId": "heat-transfer-surrogate", "modelVersion": "production", "weight": 0.7},
    {"modelId": "heat-transfer-physics", "modelVersion": "1.0.0", "weight": 0.3}
  ],
  "variables": [
    {"name": "temperature", "path": "temperature", "distribution": "normal", "mean": 350, "stdDev": 8},
    {"name": "conductivity", "path": "conductivity", "distribution": "uniform", "low": 0.4, "high": 0.8}
  ],
  "design": {"method": "latin-hypercube", "samples": 128, "seed": 2026},
  "output": {"path": "result.value", "label": "Heat flux", "unit": "W/m2"},
  "analysis": {"confidence": 0.95, "thresholds": [100, 150]},
  "execution": {"priority": 60, "maxAttempts": 3, "timeoutSeconds": 900}
}</textarea><div class="sc-eu0341-actions"><button type="button" class="sc-lab-button" data-eu-v0341-action="validate">Validate design</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-eu-v0341-action="save">Save immutable study</button></div><p class="sc-eu0341-note"><strong>Governance:</strong> members must be immutable registered-method model versions. Lab never executes arbitrary Python, shell commands, or callbacks from a study definition.</p></div>
          <div class="sc-eu0341-card"><h4>Study controls</h4><label>Study ID<input data-eu-v0341-studyid value="thermal-model-ensemble"></label><label>Operator reason<input data-eu-v0341-reason value="operator action from ensemble analysis panel"></label><div class="sc-eu0341-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-eu-v0341-action="start">Start evaluations</button><button type="button" class="sc-lab-button" data-eu-v0341-action="reconcile">Reconcile</button><button type="button" class="sc-lab-button" data-eu-v0341-action="inspect">Inspect</button><button type="button" class="sc-lab-button" data-eu-v0341-action="timeline">Timeline</button><button type="button" class="sc-lab-button" data-eu-v0341-action="refresh">Refresh</button><button type="button" class="sc-lab-button" data-eu-v0341-action="cancel">Cancel</button></div></div>
          <div class="sc-eu0341-card"><h4>Operator-recorded result</h4><p class="sc-eu0341-note">Use only for validated external results or test fixtures. Normal studies reconcile results automatically from the dispatcher.</p><label>Evaluation ID<input data-eu-v0341-evaluation placeholder="ensemble-eval-..."></label><label>Numeric output value<input data-eu-v0341-value type="number" step="any"></label><div class="sc-eu0341-actions"><button type="button" class="sc-lab-button" data-eu-v0341-action="result">Record result</button></div></div>
          <div class="sc-eu0341-card is-wide"><h4>Saved studies</h4><div class="sc-eu0341-table-wrap"><table class="sc-eu0341-table"><thead><tr><th>Study</th><th>Status</th><th>Project</th><th>Definition</th><th>Action</th></tr></thead><tbody data-eu-v0341-studies></tbody></table></div></div>
          <div class="sc-eu0341-card is-wide"><h4>Study, evaluation, uncertainty, sensitivity, and provenance records</h4><pre class="sc-eu0341-output" data-eu-v0341-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-sr0342" data-lab-module="surrogate-reduced-order" data-module-panel="surrogate-reduced-order" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / MODEL ACCELERATION / v0.34.2</p><h3>Surrogate Models and Reduced-Order Analysis</h3><p>Train reproducible surrogate models, compress high-dimensional simulation states with proper orthogonal decomposition, validate approximation error, reconstruct reduced states, and publish immutable surrogate versions into the Scientific Model Registry.</p></header>
        <p data-sr-v0342-status role="status" aria-live="polite">Surrogate and reduced-order engine loading…</p>
        <div class="sc-sr0342-metrics" data-sr-v0342-metrics></div>
        <div class="sc-sr0342-grid">
          <div class="sc-sr0342-card is-wide"><h4>Training definition</h4><textarea data-sr-v0342-definition aria-label="Surrogate or reduced-order study JSON">{
  "id": "thermal-response-surrogate",
  "title": "Thermal response surrogate",
  "projectId": "default",
  "mode": "surrogate",
  "data": {
    "features": ["temperature", "flow"],
    "inputs": [[300, 1], [320, 1.5], [340, 2], [360, 2.5], [380, 3], [400, 3.5]],
    "outputs": [42.0, 46.5, 51.0, 55.5, 60.0, 64.5]
  },
  "training": {"algorithm": "polynomial-ridge", "degree": 2, "ridge": 1e-8},
  "validation": {"holdoutFraction": 0.2, "randomSeed": 3420, "maximumNormalizedRmse": 0.25, "minimumR2": 0.0},
  "reducedOrder": {"method": "pod-svd", "energyThreshold": 0.99, "maxRank": 20, "center": true},
  "provenance": {"datasetId": "replace-with-training-dataset-id"}
}</textarea><div class="sc-sr0342-actions"><button type="button" class="sc-lab-button" data-sr-v0342-action="validate">Validate definition</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-sr-v0342-action="train">Train immutable study</button><button type="button" class="sc-lab-button" data-sr-v0342-action="refresh">Refresh</button></div><p class="sc-sr0342-note"><strong>Modes:</strong> use <code>surrogate</code> for scalar response approximation, <code>reduced-order</code> for POD/SVD state compression, or <code>hybrid-rom</code> to learn parameter-to-reduced-state mappings. Definitions cannot execute arbitrary Python, shell commands, or callbacks.</p></div>
          <div class="sc-sr0342-card"><h4>Study controls</h4><label>Study ID<input data-sr-v0342-studyid value="thermal-response-surrogate"></label><div class="sc-sr0342-actions"><button type="button" class="sc-lab-button" data-sr-v0342-action="inspect">Inspect</button><button type="button" class="sc-lab-button" data-sr-v0342-action="timeline">Timeline</button></div></div>
          <div class="sc-sr0342-card"><h4>Prediction or reconstruction</h4><textarea data-sr-v0342-prediction aria-label="Prediction request JSON">{
  "inputs": {"temperature": 350, "flow": 2.2}
}</textarea><div class="sc-sr0342-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-sr-v0342-action="predict">Predict</button></div></div>
          <div class="sc-sr0342-card"><h4>Publish to model registry</h4><textarea data-sr-v0342-registration aria-label="Model registry publication JSON">{
  "id": "thermal-response-surrogate",
  "modelVersion": "1.0.0",
  "channel": "candidate",
  "sourceRevision": "replace-with-git-commit",
  "environment": {
    "id": "surrogate-rom-python-312",
    "dependencies": [{"name": "numpy", "version": "2.x"}, {"name": "scipy", "version": "1.x"}]
  }
}</textarea><div class="sc-sr0342-actions"><button type="button" class="sc-lab-button" data-sr-v0342-action="register">Register immutable version</button></div></div>
          <div class="sc-sr0342-card is-wide"><h4>Saved surrogate and ROM studies</h4><div class="sc-sr0342-table-wrap"><table class="sc-sr0342-table"><thead><tr><th>Study</th><th>Mode</th><th>Status</th><th>Model hash</th><th>Action</th></tr></thead><tbody data-sr-v0342-studies></tbody></table></div></div>
          <div class="sc-sr0342-card is-wide"><h4>Training, validation, prediction, reduced basis, registry, and provenance records</h4><pre class="sc-sr0342-output" data-sr-v0342-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-tw0350" data-lab-module="team-workspaces" data-module-panel="team-workspaces" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / COLLABORATION / v0.35.0</p><h3>Shared Research Projects and Team Workspaces</h3><p>Create private research workspaces with explicit membership roles, single-use invitations, governed links to Lab resources, ownership continuity, durable access decisions, and a complete collaboration timeline.</p></header>
        <p data-tw-v0350-status role="status" aria-live="polite">Shared workspace service loading…</p>
        <div class="sc-tw0350-metrics" data-tw-v0350-metrics></div>
        <div class="sc-tw0350-grid">
          <div class="sc-tw0350-card is-wide"><h4>Workspace definition</h4><textarea data-tw-v0350-definition aria-label="Shared research workspace JSON">{
  "id": "climate-resilience-team",
  "title": "Climate Resilience Research Team",
  "description": "Shared workspace for datasets, workflows, models, evidence, and reports.",
  "primaryProjectId": "climate-resilience-2026",
  "settings": {"resourceDefaultRole": "viewer", "invitationExpiryHours": 168}
}</textarea><div class="sc-tw0350-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-tw-v0350-action="create">Create workspace</button><button type="button" class="sc-lab-button" data-tw-v0350-action="update">Update</button><button type="button" class="sc-lab-button" data-tw-v0350-action="refresh">Refresh</button></div><p class="sc-tw0350-note"><strong>Integration:</strong> v0.35.0 governs membership and shared resource access; v0.35.1 adds review, approvals, and sign-off in the adjacent workspace.</p></div>
          <div class="sc-tw0350-card"><h4>Workspace controls</h4><label>Workspace ID<input data-tw-v0350-workspaceid value="climate-resilience-team"></label><label>Operator reason<input data-tw-v0350-reason value="Recorded collaboration governance action."></label><div class="sc-tw0350-actions"><button type="button" class="sc-lab-button" data-tw-v0350-action="inspect">Inspect</button><button type="button" class="sc-lab-button" data-tw-v0350-action="timeline">Timeline</button><button type="button" class="sc-lab-button" data-tw-v0350-action="archive">Archive</button></div></div>
          <div class="sc-tw0350-card"><h4>Invite member</h4><textarea data-tw-v0350-invite aria-label="Workspace invitation JSON">{
  "inviteeActorId": "wp-user-2",
  "inviteeLabel": "Research collaborator",
  "role": "contributor",
  "expiresHours": 168
}</textarea><div class="sc-tw0350-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-tw-v0350-action="invite">Create single-use invitation</button></div></div>
          <div class="sc-tw0350-card"><h4>Accept invitation</h4><p class="sc-tw0350-note sc-tw0350-secret">Invitation tokens are returned only once. Send the token through an appropriate private channel.</p><label>Invitation token<input data-tw-v0350-token autocomplete="off"></label><div class="sc-tw0350-actions"><button type="button" class="sc-lab-button" data-tw-v0350-action="accept">Accept for current user</button></div></div>
          <div class="sc-tw0350-card"><h4>Member governance</h4><textarea data-tw-v0350-member aria-label="Workspace member role JSON">{
  "actorId": "wp-user-2",
  "role": "editor"
}</textarea><div class="sc-tw0350-actions"><button type="button" class="sc-lab-button" data-tw-v0350-action="member-role">Change role</button><button type="button" class="sc-lab-button" data-tw-v0350-action="remove-member">Remove member</button></div></div>
          <div class="sc-tw0350-card"><h4>Transfer ownership</h4><textarea data-tw-v0350-transfer aria-label="Workspace ownership transfer JSON">{
  "newOwnerId": "wp-user-2",
  "reason": "Principal investigator responsibility transferred."
}</textarea><div class="sc-tw0350-actions"><button type="button" class="sc-lab-button" data-tw-v0350-action="transfer">Transfer ownership</button></div></div>
          <div class="sc-tw0350-card"><h4>Link governed Lab resource</h4><textarea data-tw-v0350-resource aria-label="Workspace resource link JSON">{
  "resourceType": "dataset",
  "resourceId": "climate-observations-2026",
  "title": "Climate observations dataset",
  "minimumRole": "contributor",
  "metadata": {"purpose": "shared analysis input"}
}</textarea><div class="sc-tw0350-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-tw-v0350-action="link">Link resource</button><button type="button" class="sc-lab-button" data-tw-v0350-action="unlink">Unlink by linkId</button></div></div>
          <div class="sc-tw0350-card"><h4>Access decision</h4><textarea data-tw-v0350-access aria-label="Workspace access decision JSON">{
  "action": "resources.read",
  "resourceLinkId": "replace-with-link-id"
}</textarea><div class="sc-tw0350-actions"><button type="button" class="sc-lab-button" data-tw-v0350-action="authorize">Evaluate current user</button></div></div>
          <div class="sc-tw0350-card is-wide"><h4>Accessible team workspaces</h4><div class="sc-tw0350-table-wrap"><table class="sc-tw0350-table"><thead><tr><th>Workspace</th><th>Your role</th><th>Status</th><th>Primary project</th><th>Action</th></tr></thead><tbody data-tw-v0350-workspaces></tbody></table></div></div>
          <div class="sc-tw0350-card is-wide"><h4>Workspace, membership, invitation, resource, access, and activity records</h4><pre class="sc-tw0350-output" data-tw-v0350-output>No response yet.</pre></div>
        </div>
      </section>


      <section class="sc-lab-panel sc-wr0351" data-lab-module="workspace-review" data-module-panel="workspace-review" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / COLLABORATION GOVERNANCE / v0.35.1</p><h3>Review, Comments, Approvals, and Scientific Sign-Off</h3><p>Run append-only scientific discussions, assign reviewers, enforce explicit approval gates, prevent stale concurrent updates, and create immutable sign-off records for governed workspace resources.</p></header>
        <p data-wr-v0351-status role="status" aria-live="polite">Review and sign-off service loading…</p>
        <div class="sc-wr0351-metrics" data-wr-v0351-metrics></div>
        <div class="sc-wr0351-grid">
          <div class="sc-wr0351-card"><h4>Workspace context</h4><label>Workspace ID<input data-wr-v0351-workspace value="climate-team"></label><label>Thread ID<input data-wr-v0351-thread value="methods-review"></label><label>Comment ID<input data-wr-v0351-comment value="comment-1"></label><label>Assignment ID<input data-wr-v0351-assignment value="assignment-1"></label><label>Approval ID<input data-wr-v0351-approval value="approval-1"></label><div class="sc-wr0351-actions"><button type="button" class="sc-lab-button" data-wr-v0351-action="refresh">Refresh health</button><button type="button" class="sc-lab-button" data-wr-v0351-action="threads">List threads</button><button type="button" class="sc-lab-button" data-wr-v0351-action="timeline">Review timeline</button></div></div>
          <div class="sc-wr0351-card"><h4>Create review thread</h4><textarea data-wr-v0351-thread-json>{
  "id": "methods-review",
  "title": "Methods and evidence review",
  "resourceLinkId": "replace-with-link-id"
}</textarea><div class="sc-wr0351-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wr-v0351-action="create-thread">Create thread</button></div></div>
          <div class="sc-wr0351-card"><h4>Append-only comment</h4><textarea data-wr-v0351-comment-json>{
  "body": "Please document the uncertainty assumptions and validation evidence.",
  "parentCommentId": null
}</textarea><textarea data-wr-v0351-withdraw-json>{"reason":"Superseded by a corrected comment."}</textarea><div class="sc-wr0351-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wr-v0351-action="comment">Add comment</button><button type="button" class="sc-lab-button" data-wr-v0351-action="withdraw-comment">Withdraw comment</button></div></div>
          <div class="sc-wr0351-card"><h4>Resolve or reopen thread</h4><textarea data-wr-v0351-thread-state-json>{
  "expectedRevision": 1,
  "resolution": "The requested evidence was added and verified."
}</textarea><div class="sc-wr0351-actions"><button type="button" class="sc-lab-button" data-wr-v0351-action="resolve">Resolve</button><button type="button" class="sc-lab-button" data-wr-v0351-action="reopen">Reopen</button></div></div>
          <div class="sc-wr0351-card"><h4>Review assignment</h4><textarea data-wr-v0351-assignment-json>{
  "id": "assignment-1",
  "resourceLinkId": "replace-with-link-id",
  "reviewerId": "wp-user-2",
  "instructions": "Review methods, evidence, and uncertainty claims."
}</textarea><textarea data-wr-v0351-assignment-state-json>{"expectedRevision":1,"status":"in-review"}</textarea><div class="sc-wr0351-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wr-v0351-action="assign">Assign reviewer</button><button type="button" class="sc-lab-button" data-wr-v0351-action="update-assignment">Update assignment</button></div></div>
          <div class="sc-wr0351-card"><h4>Approval request</h4><textarea data-wr-v0351-approval-json>{
  "id": "approval-1",
  "resourceLinkId": "replace-with-link-id",
  "title": "Scientific publication approval",
  "requiredApprovals": 1,
  "requireNoOpenThreads": true,
  "requireAssignmentsComplete": true,
  "signoffMinimumRole": "administrator"
}</textarea><div class="sc-wr0351-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wr-v0351-action="create-approval">Create approval</button><button type="button" class="sc-lab-button" data-wr-v0351-action="inspect-approval">Inspect</button><button type="button" class="sc-lab-button" data-wr-v0351-action="evaluate">Evaluate gates</button></div></div>
          <div class="sc-wr0351-card"><h4>Immutable decision</h4><textarea data-wr-v0351-decision-json>{
  "expectedRevision": 1,
  "decision": "approve",
  "rationale": "The methods and evidence satisfy the declared review standard.",
  "evidence": [{"type":"dataset","id":"observations-2026"}]
}</textarea><div class="sc-wr0351-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wr-v0351-action="decide">Record decision</button></div></div>
          <div class="sc-wr0351-card"><h4>Scientific sign-off</h4><textarea data-wr-v0351-signoff-json>{
  "expectedRevision": 2,
  "statement": "I approve this governed resource for scientific publication."
}</textarea><textarea data-wr-v0351-cancel-json>{"expectedRevision":1,"reason":"Approval request superseded."}</textarea><div class="sc-wr0351-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wr-v0351-action="signoff">Create immutable sign-off</button><button type="button" class="sc-lab-button" data-wr-v0351-action="cancel">Cancel request</button></div></div>
          <div class="sc-wr0351-card is-wide"><h4>Review, approval, decision, sign-off, and event records</h4><p class="sc-wr0351-note">Revision-bearing updates reject stale clients with HTTP 409. Decisions and sign-offs are append-only and cannot be edited or deleted.</p><pre class="sc-wr0351-output" data-wr-v0351-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-wv0352" data-lab-module="workspace-versioning" data-module-panel="workspace-versioning" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / COLLABORATION GOVERNANCE / v0.35.2</p><h3>Version History, Branching, Merge, and Conflict Resolution</h3><p>Preserve immutable research states, develop changes on named branches, compare snapshots, resolve path-level conflicts, and merge approved work without rewriting scientific history.</p></header>
        <p data-wv-v0352-status role="status" aria-live="polite">Workspace version-control service loading…</p>
        <div class="sc-wv0352-metrics" data-wv-v0352-metrics></div>
        <div class="sc-wv0352-grid">
          <div class="sc-wv0352-card"><h4>Workspace context</h4><label>Workspace ID<input data-wv-v0352-workspace value="climate-team"></label><label>Branch ID<input data-wv-v0352-branch value="replace-with-branch-id"></label><label>Snapshot ID<input data-wv-v0352-snapshot value="replace-with-snapshot-id"></label><label>Merge request ID<input data-wv-v0352-merge value="replace-with-merge-id"></label><label>Conflict ID<input data-wv-v0352-conflict value="replace-with-conflict-id"></label><div class="sc-wv0352-actions"><button type="button" class="sc-lab-button" data-wv-v0352-action="refresh">Refresh health</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-wv-v0352-action="bootstrap">Initialize main branch</button><button type="button" class="sc-lab-button" data-wv-v0352-action="branches">List branches</button><button type="button" class="sc-lab-button" data-wv-v0352-action="timeline">Version timeline</button></div></div>
          <div class="sc-wv0352-card"><h4>Create branch</h4><textarea data-wv-v0352-branch-json>{
  "name": "methods/uncertainty-review",
  "sourceBranch": "main",
  "protected": false
}</textarea><textarea data-wv-v0352-branch-state-json>{"expectedRevision":1,"protected":false,"status":"active"}</textarea><div class="sc-wv0352-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wv-v0352-action="create-branch">Create branch</button><button type="button" class="sc-lab-button" data-wv-v0352-action="update-branch">Update branch</button></div></div>
          <div class="sc-wv0352-card is-wide"><h4>Create immutable snapshot</h4><textarea data-wv-v0352-snapshot-json>{
  "expectedHeadSnapshotId": null,
  "message": "Capture the governed research baseline",
  "tree": {
    "reports/climate.json": {"version": 1, "status": "draft"},
    "datasets/observations.json": {"datasetId": "observations-2026"}
  },
  "metadata": {"purpose": "research-state checkpoint"}
}</textarea><div class="sc-wv0352-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wv-v0352-action="snapshot">Create snapshot</button><button type="button" class="sc-lab-button" data-wv-v0352-action="snapshots">List branch history</button><button type="button" class="sc-lab-button" data-wv-v0352-action="get-snapshot">Inspect snapshot</button></div></div>
          <div class="sc-wv0352-card"><h4>Compare or restore</h4><textarea data-wv-v0352-compare-json>{
  "fromSnapshotId": "replace-with-base-snapshot",
  "toSnapshotId": "replace-with-new-snapshot"
}</textarea><textarea data-wv-v0352-restore-json>{
  "expectedHeadSnapshotId": "replace-with-current-head",
  "message": "Restore the approved baseline without rewriting history"
}</textarea><div class="sc-wv0352-actions"><button type="button" class="sc-lab-button" data-wv-v0352-action="compare">Compare snapshots</button><button type="button" class="sc-lab-button" data-wv-v0352-action="restore">Restore as new snapshot</button></div></div>
          <div class="sc-wv0352-card"><h4>Open merge request</h4><textarea data-wv-v0352-merge-json>{
  "sourceBranch": "replace-with-source-branch-id",
  "targetBranch": "main",
  "title": "Merge reviewed uncertainty methods",
  "description": "Three-way merge against the shared research baseline."
}</textarea><div class="sc-wv0352-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wv-v0352-action="create-merge">Create merge request</button><button type="button" class="sc-lab-button" data-wv-v0352-action="merges">List merges</button><button type="button" class="sc-lab-button" data-wv-v0352-action="get-merge">Inspect merge</button></div></div>
          <div class="sc-wv0352-card"><h4>Resolve conflict</h4><textarea data-wv-v0352-resolution-json>{
  "expectedRevision": 1,
  "resolution": "custom",
  "value": {"decision": "reviewed combined value"}
}</textarea><div class="sc-wv0352-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wv-v0352-action="resolve">Record resolution</button></div><p class="sc-wv0352-note">Reviewers may resolve path-level conflicts. Every resolution retains the base, source, target, actor, timestamp, and conflict hash.</p></div>
          <div class="sc-wv0352-card"><h4>Protected-branch approval</h4><textarea data-wv-v0352-approval-json>{
  "expectedRevision": 1,
  "approvalRequestId": "replace-with-signed-approval-id"
}</textarea><div class="sc-wv0352-actions"><button type="button" class="sc-lab-button" data-wv-v0352-action="approval">Attach scientific approval</button></div><p class="sc-wv0352-note">Protected targets require a signed v0.35.1 scientific approval before finalization.</p></div>
          <div class="sc-wv0352-card"><h4>Finalize or cancel merge</h4><textarea data-wv-v0352-finalize-json>{
  "expectedRevision": 2,
  "message": "Merge signed scientific release candidate"
}</textarea><textarea data-wv-v0352-cancel-json>{"expectedRevision":1,"reason":"Superseded by a revised branch."}</textarea><div class="sc-wv0352-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wv-v0352-action="finalize">Finalize merge</button><button type="button" class="sc-lab-button" data-wv-v0352-action="cancel">Cancel merge</button></div></div>
          <div class="sc-wv0352-card is-wide"><h4>Branches, snapshots, comparisons, conflicts, approvals, and history</h4><p class="sc-wv0352-note">Snapshots and merge records are immutable. Rollback creates a new snapshot. Branch heads and merge revisions reject stale clients with HTTP 409.</p><pre class="sc-wv0352-output" data-wv-v0352-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-ar0360" data-lab-module="artifact-repository" data-module-panel="artifact-repository" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / ARTIFACT GOVERNANCE / v0.36.0</p><h3>Scientific Artifact Repository and Data Federation</h3><p>Organize immutable scientific artifacts into governed collections, verify content identities, exchange hashed manifests with trusted institutional nodes, preserve tombstones, and resolve federation conflicts without enabling unrestricted remote execution.</p></header>
        <div data-ar-v0360-status>Connecting to the artifact repository…</div>
        <div class="sc-ar0360-metrics" data-ar-v0360-metrics></div>
        <div class="sc-ar0360-grid">
          <div class="sc-ar0360-card"><h4>Workspace and collection</h4><label>Workspace ID<input data-ar-v0360-workspace value="climate-team"></label><label>Collection ID<input data-ar-v0360-collection value="climate-artifacts"></label><label>Node ID<input data-ar-v0360-node value="sustainable-catalyst-primary"></label><textarea data-ar-v0360-collection-json>{
  "id": "climate-artifacts",
  "title": "Climate Research Artifacts",
  "description": "Governed datasets, model outputs, reports, and provenance records.",
  "visibility": "workspace",
  "metadata": {"discipline": "climate-science"}
}</textarea><div class="sc-ar0360-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ar-v0360-action="create-collection">Create collection</button><button type="button" class="sc-lab-button" data-ar-v0360-action="collections">List collections</button><button type="button" class="sc-lab-button" data-ar-v0360-action="inspect">Inspect</button><button type="button" class="sc-lab-button" data-ar-v0360-action="manifest">Export manifest</button></div><textarea data-ar-v0360-archive-json>{"reason":"collection superseded by an approved research release"}</textarea><button type="button" class="sc-lab-button" data-ar-v0360-action="archive">Archive collection</button></div>
          <div class="sc-ar0360-card"><h4>Register and verify artifact</h4><label>Repository artifact ID<input data-ar-v0360-artifact value="climate-observations-v1"></label><textarea data-ar-v0360-artifact-json>{
  "id": "climate-observations-v1",
  "title": "Regional Climate Observations",
  "artifactType": "dataset",
  "artifactVersion": "1.0.0",
  "mediaType": "application/json",
  "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sizeBytes": 1024,
  "canonicalUri": "urn:sc-lab:climate-observations:1.0.0",
  "provenance": {"method": "validated-observation-import"},
  "metadata": {"license": "CC-BY-4.0"}
}</textarea><div class="sc-ar0360-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ar-v0360-action="register">Register artifact</button><button type="button" class="sc-lab-button" data-ar-v0360-action="verify">Verify integrity</button></div><p class="sc-ar0360-note">Use <code>transportArtifactId</code> to bind a repository record to bytes already verified by Lab’s content-addressed artifact transport.</p></div>
          <div class="sc-ar0360-card"><h4>Federated source</h4><label>Source ID<input data-ar-v0360-source value="institution-west"></label><textarea data-ar-v0360-source-json>{
  "id": "institution-west",
  "title": "Western Research Node",
  "nodeId": "node-west",
  "sourceType": "institutional-repository",
  "endpointUrl": "https://example.org/sc-lab/federation",
  "trustMode": "strict",
  "conflictPolicy": "reject",
  "metadata": {"institution": "Example University"}
}</textarea><div class="sc-ar0360-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ar-v0360-action="create-source">Register source</button><button type="button" class="sc-lab-button" data-ar-v0360-action="sources">List sources</button><button type="button" class="sc-lab-button" data-ar-v0360-action="sync-history">Sync history</button></div></div>
          <div class="sc-ar0360-card"><h4>Manifest synchronization</h4><textarea data-ar-v0360-manifest-json>{
  "schema": "sc-lab-federation-manifest/0.36.0",
  "version": "0.36.0",
  "nodeId": "node-west",
  "generatedAt": "2026-07-17T20:00:00Z",
  "cursor": "1",
  "collection": {"id": "remote-climate", "title": "Remote Climate"},
  "artifacts": [],
  "manifestHash": "replace-with-canonical-manifest-hash"
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-ar-v0360-action="sync">Synchronize manifest</button><p class="sc-ar0360-note"><strong>Federation boundary:</strong> synchronization accepts explicit manifests through authenticated Lab routes. The coordinator does not make arbitrary callbacks to submitted URLs.</p></div>
          <div class="sc-ar0360-card"><h4>Conflict resolution</h4><label>Conflict ID<input data-ar-v0360-conflict value="conflict-id"></label><textarea data-ar-v0360-resolution-json>{"resolution":"retain-both"}</textarea><div class="sc-ar0360-actions"><button type="button" class="sc-lab-button" data-ar-v0360-action="conflicts">Open conflicts</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-ar-v0360-action="resolve">Resolve conflict</button><button type="button" class="sc-lab-button" data-ar-v0360-action="timeline">Timeline</button><button type="button" class="sc-lab-button" data-ar-v0360-action="refresh">Refresh</button></div></div>
          <div class="sc-ar0360-card is-wide"><h4>Collections, artifacts, sources, sync runs, conflicts, and integrity records</h4><pre class="sc-ar0360-output" data-ar-v0360-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-inf0361" data-lab-module="institutional-nodes" data-module-panel="institutional-nodes" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / INSTITUTIONAL FEDERATION / v0.36.1</p><h3>Institutional Node Federation and Local-Data Execution</h3><p>Register governed institutional compute nodes, describe data that must remain local, issue signed registered-method envelopes, and retain attested aggregate results without centralizing confidential or restricted datasets.</p></header>
        <div data-inf-v0361-status role="status" aria-live="polite">Connecting to institutional federation…</div>
        <div class="sc-inf0361-metrics" data-inf-v0361-metrics></div>
        <div class="sc-inf0361-grid">
          <div class="sc-inf0361-card"><h4>Institutional node</h4><label>Workspace ID<input data-inf-v0361-workspace value="health-team"></label><label>Node ID<input data-inf-v0361-node value="hospital-node"></label><textarea data-inf-v0361-node-json>{
  "id": "hospital-node",
  "title": "Hospital Secure Compute Node",
  "institution": "Example Hospital",
  "endpointUrl": "https://hospital.example/sc-lab-node",
  "allowedMethods": ["statistics.descriptive"],
  "classifications": ["public", "internal", "confidential", "restricted"],
  "maxConcurrent": 2,
  "capabilities": {"localExecution": true, "resultAttestation": true}
}</textarea><div class="sc-inf0361-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-inf-v0361-action="register-node">Register node</button><button type="button" class="sc-lab-button" data-inf-v0361-action="nodes">List nodes</button><button type="button" class="sc-lab-button" data-inf-v0361-action="refresh">Refresh</button></div><textarea data-inf-v0361-status-json>{"status":"suspended","reason":"operator maintenance window"}</textarea><button type="button" class="sc-lab-button" data-inf-v0361-action="node-status">Change node status</button><p class="sc-inf0361-note">The node secret is returned once during registration. Store it only in the institutional node runtime, never in WordPress or a browser.</p></div>
          <div class="sc-inf0361-card"><h4>Local data asset</h4><textarea data-inf-v0361-data-json>{
  "id": "local-cohort",
  "title": "Restricted Outcomes Cohort",
  "classification": "restricted",
  "exportPolicy": "aggregate-only",
  "schemaHash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "contentHash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "rowCount": 2500,
  "metadata": {"custodian": "clinical-research-office", "fields": ["age", "outcome"]}
}</textarea><div class="sc-inf0361-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-inf-v0361-action="register-data">Register local data</button><button type="button" class="sc-lab-button" data-inf-v0361-action="data-assets">List local assets</button></div><p class="sc-inf0361-note">Only metadata, schema hashes, classifications, and policy records are centralized. Restricted data bytes stay on the institutional node.</p></div>
          <div class="sc-inf0361-card"><h4>Governed local execution</h4><textarea data-inf-v0361-execution-json>{
  "id": "local-analysis-1",
  "nodeId": "hospital-node",
  "methodId": "statistics.descriptive",
  "dataAssetIds": ["local-cohort"],
  "parameters": {"column": "outcome"},
  "outputPolicy": "aggregate-only",
  "priority": 70
}</textarea><div class="sc-inf0361-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-inf-v0361-action="execute">Create signed request</button><button type="button" class="sc-lab-button" data-inf-v0361-action="executions">List executions</button><button type="button" class="sc-lab-button" data-inf-v0361-action="timeline">Timeline</button></div><p class="sc-inf0361-note"><strong>Execution boundary:</strong> requests reference registered Lab methods and local data IDs. Arbitrary Python, shell commands, executable expressions, and unrestricted callbacks are rejected.</p></div>
          <div class="sc-inf0361-card"><h4>Cancel local execution</h4><label>Execution request ID<input data-inf-v0361-request value="local-analysis-1"></label><textarea data-inf-v0361-cancel-json>{"reason":"research protocol changed before execution"}</textarea><button type="button" class="sc-lab-button" data-inf-v0361-action="cancel">Cancel request</button><p class="sc-inf0361-note">Completed results require a node-authenticated attestation containing the result hash, data-access digest, environment hash, and policy-approved summary.</p></div>
          <div class="sc-inf0361-card is-wide"><h4>Nodes, local data assets, execution envelopes, attestations, and federation history</h4><pre class="sc-inf0361-output" data-inf-v0361-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-edge0362" data-lab-module="offline-edge-sync" data-module-panel="offline-edge-sync" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / FIELD RESEARCH / v0.36.2</p><h3>Offline Field Research and Edge Synchronization</h3><p>Create sealed field-work packages, enroll governed edge devices, synchronize observations after disconnected work, and resolve concurrent edits without moving restricted institutional data into the browser or field package.</p></header>
        <div data-edge-v0362-status role="status" aria-live="polite">Connecting to offline field synchronization…</div>
        <div class="sc-edge0362-metrics" data-edge-v0362-metrics></div>
        <div class="sc-edge0362-grid">
          <div class="sc-edge0362-card"><h4>Edge device</h4><label>Workspace ID<input data-edge-v0362-workspace value="field-team"></label><label>Device ID<input data-edge-v0362-device value="tablet-1"></label><textarea data-edge-v0362-device-json>{
  "id": "tablet-1",
  "title": "Wetland Field Tablet",
  "nodeId": "field-hub",
  "platform": "ios",
  "appVersion": "1.0",
  "capabilities": {"offlineForms": true, "camera": true, "localEncryption": true}
}</textarea><div class="sc-edge0362-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-edge-v0362-action="enroll">Enroll device</button><button type="button" class="sc-lab-button" data-edge-v0362-action="devices">List devices</button><button type="button" class="sc-lab-button" data-edge-v0362-action="refresh">Refresh</button></div><textarea data-edge-v0362-status-json>{"status":"suspended","reason":"device under review"}</textarea><button type="button" class="sc-lab-button" data-edge-v0362-action="device-status">Change device status</button><p class="sc-edge0362-note">The device secret is shown once and belongs only in the encrypted edge runtime. It is never stored in WordPress or exposed to browser-side synchronization.</p></div>
          <div class="sc-edge0362-card"><h4>Offline work package</h4><label>Package ID<input data-edge-v0362-package value="wetland-survey"></label><textarea data-edge-v0362-package-json>{
  "id": "wetland-survey",
  "title": "Wetland Biodiversity Survey",
  "nodeId": "field-hub",
  "definition": {
    "methods": ["statistics.descriptive"],
    "forms": [{"id":"observation","fields":["plot","species","count","notes"]}],
    "protocols": [{"id":"wetland-count-v1","revision":"1.0"}],
    "dataAssetRefs": ["local-wetland-index"],
    "artifactRefs": [],
    "constraints": {"rawRestrictedDataExport": false, "locationPrecision":"coarse-or-none"},
    "metadata": {"study":"wetland-monitoring"}
  }
}</textarea><div class="sc-edge0362-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-edge-v0362-action="create-package">Create package</button><button type="button" class="sc-lab-button" data-edge-v0362-action="seal">Seal package</button><button type="button" class="sc-lab-button" data-edge-v0362-action="assign">Assign device</button><button type="button" class="sc-lab-button" data-edge-v0362-action="packages">List packages</button></div><p class="sc-edge0362-note">Packages contain protocols, forms, method IDs, hashes, and references—not restricted data bytes, arbitrary code, shell commands, or callback URLs.</p></div>
          <div class="sc-edge0362-card"><h4>Synchronization oversight</h4><div class="sc-edge0362-actions"><button type="button" class="sc-lab-button" data-edge-v0362-action="sessions">Sync sessions</button><button type="button" class="sc-lab-button" data-edge-v0362-action="conflicts">Open conflicts</button><button type="button" class="sc-lab-button" data-edge-v0362-action="timeline">Timeline</button></div><p class="sc-edge0362-note">Edge runtimes use signed batches, cursor-based deltas, one-time resume tokens, duplicate change IDs, and immutable device provenance. Browser controls provide oversight only.</p></div>
          <div class="sc-edge0362-card"><h4>Conflict resolution</h4><label>Conflict ID<input data-edge-v0362-conflict value="conflict-id"></label><textarea data-edge-v0362-resolution-json>{"resolution":"retain-both"}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-edge-v0362-action="resolve">Resolve conflict</button><p class="sc-edge0362-note">Available resolutions preserve local, accept edge, retain both, or dismiss the conflict. Reconciliation creates a new event rather than silently rewriting field history.</p></div>
          <div class="sc-edge0362-card is-wide"><h4>Devices, packages, synchronization sessions, conflicts, and field provenance</h4><pre class="sc-edge0362-output" data-edge-v0362-output>No response yet.</pre></div>
        </div>
      </section>


      <section class="sc-lab-panel sc-pub0370" data-lab-module="publication-studio" data-module-panel="publication-studio" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / REPRODUCIBILITY &amp; PUBLICATION / v0.37.0</p><h3>Reproducibility Packages &amp; Research Publication Studio</h3><p>Assemble workspace-governed research bundles, verify immutable manifests, render publication-ready outputs, and publish only after scientific sign-off.</p></header>
        <p class="sc-pub0370-status" data-pub-v0370-status role="status" aria-live="polite">Connecting to the publication studio…</p>
        <div class="sc-pub0370-grid">
          <div class="sc-pub0370-card"><h4>Reproducibility package</h4><label>Workspace ID<input data-pub-v0370-workspace value="publication-team"></label><label>Package ID<input data-pub-v0370-package value="wetland-study-v1"></label><textarea data-pub-v0370-package-json>{
  "id": "wetland-study-v1",
  "title": "Wetland Biodiversity Study",
  "description": "Reproducible research package for the field campaign.",
  "packageVersion": "1.0.0",
  "license": "CC-BY-4.0",
  "resources": [
    {"id":"dataset-summary","type":"dataset","sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","title":"Verified aggregate dataset"},
    {"id":"analysis-workflow","type":"workflow","sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","title":"Registered analysis workflow"}
  ],
  "methods": {"registeredMethods":["statistics.descriptive"]},
  "environment": {"python":"3.12","dependencies":{"numpy":"locked"}},
  "authors": [{"name":"Research Team","role":"author"}],
  "citations": [{"id":"source-1","title":"Field protocol","type":"report"}],
  "provenance": {"workspace":"publication-team","study":"wetland-monitoring"}
}</textarea><div class="sc-pub0370-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pub-v0370-action="package-create">Create package</button><button type="button" class="sc-lab-button" data-pub-v0370-action="package-update">Update draft</button><button type="button" class="sc-lab-button" data-pub-v0370-action="seal">Seal</button><button type="button" class="sc-lab-button" data-pub-v0370-action="verify">Verify</button><button type="button" class="sc-lab-button" data-pub-v0370-action="packages">List packages</button></div><p class="sc-edge0362-note">Sealed packages are immutable. Raw restricted data, executable code, shell commands, secrets, and unrestricted callbacks are rejected.</p></div>
          <div class="sc-pub0370-card"><h4>Research publication</h4><label>Publication ID<input data-pub-v0370-publication value="wetland-study-article"></label><textarea data-pub-v0370-publication-json>{
  "id": "wetland-study-article",
  "packageId": "wetland-study-v1",
  "title": "Wetland Biodiversity Monitoring Results",
  "subtitle": "A reproducible field-research report",
  "abstract": "This report summarizes the governed field campaign and its verified results.",
  "authors": [{"name":"Research Team","affiliation":"Sustainable Catalyst"}],
  "sections": [
    {"id":"methods","title":"Methods","body":"Registered methods and verified field protocols were used."},
    {"id":"results","title":"Results","body":"Aggregate findings are reported with package provenance."}
  ],
  "citations": [{"id":"source-1","title":"Field protocol","author":"Research Team","year":2026}],
  "license": "CC-BY-4.0",
  "visibility": "workspace"
}</textarea><div class="sc-pub0370-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pub-v0370-action="publication-create">Create publication</button><button type="button" class="sc-lab-button" data-pub-v0370-action="publications">List publications</button><button type="button" class="sc-lab-button" data-pub-v0370-action="render">Render outputs</button><button type="button" class="sc-lab-button" data-pub-v0370-action="ready">Mark ready</button></div></div>
          <div class="sc-pub0370-card"><h4>Scientific publication gate</h4><textarea data-pub-v0370-publish-json>{
  "approvalId": "publication-approval-id",
  "scientificSignoff": {
    "id": "scientific-signoff-id",
    "approvalId": "publication-approval-id",
    "signoffHash": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  },
  "canonicalUri": "https://sustainablecatalyst.com/research/wetland-study"
}</textarea><div class="sc-pub0370-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pub-v0370-action="publish">Publish signed release</button><button type="button" class="sc-lab-button" data-pub-v0370-action="timeline">Timeline</button><button type="button" class="sc-lab-button" data-pub-v0370-action="health">Refresh health</button></div><p class="sc-edge0362-note">Publication requires a verified sealed package, a completed approval, and an immutable scientific sign-off bound to the same workspace resource.</p></div>
          <div class="sc-pub0370-card is-wide"><h4>Packages, verification receipts, publication outputs, and provenance</h4><pre class="sc-pub0370-output" data-pub-v0370-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-ma0371" data-lab-module="manuscript-assembly" data-module-panel="manuscript-assembly" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / RESEARCH ASSEMBLY / v0.37.1</p><h3>Manuscript, Report, Notebook &amp; Methods Assembly</h3><p>Build structured research documents from reusable sections and sealed reproducibility packages, generate methods narratives, render safe output-only notebooks, and preserve immutable revision lineage.</p></header>
        <p data-ma-v0371-status role="status" aria-live="polite">Connecting to the assembly studio…</p>
        <div class="sc-ma0371-grid">
          <div class="sc-ma0371-card"><h4>Workspace and section library</h4><label>Workspace ID<input data-ma-v0371-workspace value="publication-team"></label><label>Section ID<input data-ma-v0371-section value="wetland-introduction"></label><textarea data-ma-v0371-section-json>{
  "id": "wetland-introduction",
  "title": "Introduction",
  "kind": "introduction",
  "content": {"body": "Wetland monitoring provides evidence for ecological change."}
}</textarea><div class="sc-ma0371-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ma-v0371-action="section-create">Create section</button><button type="button" class="sc-lab-button" data-ma-v0371-action="section-update">Revise section</button><button type="button" class="sc-lab-button" data-ma-v0371-action="sections">List sections</button></div></div>
          <div class="sc-ma0371-card"><h4>Research assembly</h4><label>Assembly ID<input data-ma-v0371-assembly value="wetland-manuscript-v1"></label><textarea data-ma-v0371-assembly-json>{
  "id": "wetland-manuscript-v1",
  "title": "Wetland Monitoring Study",
  "documentType": "manuscript",
  "template": "imrad",
  "packageId": "wetland-study-v1",
  "citationStyle": "Harvard",
  "metadata": {"authors":[{"name":"Tariq Ahmad"}],"citations":[]},
  "sections": [
    {"id":"abstract","kind":"abstract","title":"Abstract","body":"A reproducible wetland monitoring study."},
    {"librarySectionId":"wetland-introduction"}
  ]
}</textarea><div class="sc-ma0371-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ma-v0371-action="assembly-create">Create assembly</button><button type="button" class="sc-lab-button" data-ma-v0371-action="assembly-update">Update draft</button><button type="button" class="sc-lab-button" data-ma-v0371-action="assemblies">List assemblies</button></div></div>
          <div class="sc-ma0371-card"><h4>Methods and outputs</h4><div class="sc-ma0371-actions"><button type="button" class="sc-lab-button" data-ma-v0371-action="methods">Generate methods</button><button type="button" class="sc-lab-button" data-ma-v0371-action="validate">Validate</button><button type="button" class="sc-lab-button" data-ma-v0371-action="render">Render formats</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-ma-v0371-action="seal">Seal assembly</button></div><p class="sc-ma0371-note">Notebook exports contain narrative and stored result cells only. They never contain executable code.</p></div>
          <div class="sc-ma0371-card"><h4>Revision lineage</h4><textarea data-ma-v0371-revise-json>{"id":"wetland-manuscript-v2","title":"Wetland Monitoring Study — Revision 2"}</textarea><div class="sc-ma0371-actions"><button type="button" class="sc-lab-button" data-ma-v0371-action="revise">Create revision</button><button type="button" class="sc-lab-button" data-ma-v0371-action="timeline">Timeline</button><button type="button" class="sc-lab-button" data-ma-v0371-action="health">Refresh health</button></div></div>
          <div class="sc-ma0371-card is-wide"><h4>Assembly records, validation, renders, and lineage</h4><pre class="sc-ma0371-output" data-ma-v0371-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-pr0372" data-lab-module="public-reproduction" data-module-panel="public-reproduction" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / PUBLIC VERIFICATION / v0.37.2</p><h3>Public Reproduction &amp; Verification Portal</h3><p>Publish safe immutable reproduction records, expose public manifests, issue nonce challenges, and verify independent hash evidence without executing submitted code or centralizing restricted data.</p></header>
        <p class="sc-pr0372-status" data-pr-v0372-status role="status" aria-live="polite">Connecting to the public verification portal…</p>
        <div class="sc-pr0372-grid">
          <div class="sc-pr0372-card"><h4>Workspace record</h4><label>Workspace ID<input data-pr-v0372-workspace value="publication-team"></label><label>Record ID<input data-pr-v0372-record value="wetland-public-verification"></label><label>Public slug<input data-pr-v0372-slug value="wetland-public-verification"></label><textarea data-pr-v0372-record-json>{
  "id": "wetland-public-verification",
  "slug": "wetland-public-verification",
  "publicationId": "wetland-publication-v1",
  "assemblyId": "wetland-manuscript-v1",
  "title": "Wetland Monitoring Reproduction Record",
  "summary": "Independent verification record for the sealed publication package.",
  "visibility": "public",
  "publicMetadata": {"field":"ecology","release":"1.0.0"}
}</textarea><div class="sc-pr0372-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pr-v0372-action="create">Create record</button><button type="button" class="sc-lab-button" data-pr-v0372-action="publish">Publish</button><button type="button" class="sc-lab-button" data-pr-v0372-action="records">List records</button></div></div>
          <div class="sc-pr0372-card"><h4>Public manifest and challenge</h4><textarea data-pr-v0372-challenge-json>{"submitterLabel":"Independent verifier"}</textarea><div class="sc-pr0372-actions"><button type="button" class="sc-lab-button" data-pr-v0372-action="public-record">Public record</button><button type="button" class="sc-lab-button" data-pr-v0372-action="manifest">Manifest</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-pr-v0372-action="issue">Issue challenge</button></div><p class="sc-pr0372-note">The public view excludes workspace member identities, secrets, executable content, and restricted dataset bytes.</p></div>
          <div class="sc-pr0372-card is-wide"><h4>Independent verification evidence</h4><label>Challenge ID<input data-pr-v0372-challenge value="challenge-id"></label><textarea data-pr-v0372-evidence-json>{
  "nonce": "replace-with-issued-nonce",
  "recordHash": "replace-with-record-hash",
  "snapshotHash": "replace-with-snapshot-hash",
  "manifestHash": "replace-with-manifest-hash",
  "publicationHash": "replace-with-publication-hash",
  "packageHash": "replace-with-package-hash",
  "assemblyHash": "replace-with-assembly-hash",
  "resourceHashes": {},
  "environment": {"platform":"independent-verifier"}
}</textarea><div class="sc-pr0372-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pr-v0372-action="submit">Submit evidence</button><button type="button" class="sc-lab-button" data-pr-v0372-action="challenges">Workspace challenges</button><button type="button" class="sc-lab-button" data-pr-v0372-action="timeline">Timeline</button></div></div>
          <div class="sc-pr0372-card"><h4>Receipt lookup</h4><label>Receipt SHA-256<input data-pr-v0372-receipt value="receipt-hash"></label><button type="button" class="sc-lab-button" data-pr-v0372-action="receipt">Verify receipt</button></div>
          <div class="sc-pr0372-card"><h4>Withdrawal</h4><textarea data-pr-v0372-withdraw-json>{"reason":"Superseded by a corrected public record."}</textarea><button type="button" class="sc-lab-button" data-pr-v0372-action="withdraw">Withdraw record</button><p class="sc-pr0372-note">Withdrawal preserves a public tombstone and complete verification history; it does not hard-delete the record.</p></div>
          <div class="sc-pr0372-card is-wide"><h4>Records, manifests, challenges, receipts, and provenance</h4><pre class="sc-pr0372-output" data-pr-v0372-output>No response yet.</pre></div>
        </div>
      </section>



      <section class="sc-lab-panel sc-ig0390" data-lab-module="institutional-governance-v0390" data-module-panel="institutional-governance-v0390" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">INSTITUTION / CONTROL PLANE / v0.39.0</p><h3>Institutional Administration, Identity, and Governance</h3><p>Administer institutions, organizational units, credential-free human and service principals, role bindings, workspace classifications, retention policies, approval gates, and hash-chained governance decisions.</p></header>
        <p class="sc-ig0390-status" data-ig-v0390-status role="status" aria-live="polite">Connecting to the institutional governance service…</p>
        <div class="sc-ig0390-metrics" data-ig-v0390-metrics></div>
        <div class="sc-ig0390-grid">
          <div class="sc-ig0390-card"><h4>Institution and governance context</h4><label>Institution ID<input data-ig-v0390-institution value="catalyst-institute"></label><label>Workspace ID<input data-ig-v0390-workspace value="research-team"></label><div class="sc-ig0390-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="dashboard">Dashboard</button><button type="button" class="sc-lab-button" data-ig-v0390-action="institutions">Institutions</button><button type="button" class="sc-lab-button" data-ig-v0390-action="policies">Policies</button><button type="button" class="sc-lab-button" data-ig-v0390-action="refresh">Health</button><button type="button" class="sc-lab-button" data-ig-v0390-action="timeline">Audit timeline</button></div><p class="sc-ig0390-note">This release stores identity and authority records, not passwords, API secrets, or SSO tokens. Credential hardening is reserved for v0.39.1.</p></div>
          <div class="sc-ig0390-card"><h4>Create an institution</h4><textarea data-ig-v0390-institution-json>{
  "id": "catalyst-institute",
  "name": "Catalyst Institute",
  "description": "Institutional research governance workspace",
  "domains": ["example.org"]
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="create-institution">Create institution</button></div>
          <div class="sc-ig0390-card"><h4>Organizational units</h4><textarea data-ig-v0390-unit-json>{
  "id": "climate-lab",
  "title": "Climate Lab",
  "code": "CLIM"
}</textarea><div class="sc-ig0390-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="create-unit">Create unit</button><button type="button" class="sc-lab-button" data-ig-v0390-action="units">List units</button></div></div>
          <div class="sc-ig0390-card"><h4>Human and service principals</h4><textarea data-ig-v0390-principal-json>{
  "id": "compute-agent",
  "principalType": "service",
  "displayName": "Compute Agent",
  "externalSubject": "service:compute-agent"
}</textarea><div class="sc-ig0390-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="create-principal">Register principal</button><button type="button" class="sc-lab-button" data-ig-v0390-action="principals">List principals</button></div><p class="sc-ig0390-note">Service principals are credential-free identity records in v0.39.0.</p></div>
          <div class="sc-ig0390-card"><h4>Institutional role bindings</h4><textarea data-ig-v0390-binding-json>{
  "principalId": "compute-agent",
  "role": "researcher",
  "workspaceId": "research-team",
  "unitId": "climate-lab",
  "rationale": "Approved compute automation"
}</textarea><label>Binding ID to revoke<input data-ig-v0390-binding value="binding-id"></label><div class="sc-ig0390-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="grant">Grant role</button><button type="button" class="sc-lab-button" data-ig-v0390-action="bindings">List bindings</button><button type="button" class="sc-lab-button" data-ig-v0390-action="revoke">Revoke binding</button></div></div>
          <div class="sc-ig0390-card"><h4>Retention policy</h4><textarea data-ig-v0390-retention-json>{
  "id": "research-ten-years",
  "title": "Research Ten Years",
  "retentionDays": 3650,
  "reviewIntervalDays": 365,
  "disposition": "review",
  "legalHold": false
}</textarea><div class="sc-ig0390-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="create-retention">Create policy</button><button type="button" class="sc-lab-button" data-ig-v0390-action="retention">List policies</button></div></div>
          <div class="sc-ig0390-card"><h4>Workspace governance profile</h4><textarea data-ig-v0390-governance-json>{
  "institutionId": "catalyst-institute",
  "unitId": "climate-lab",
  "classification": "confidential",
  "retentionPolicyId": "research-ten-years",
  "approvalActions": ["research.publish", "research.share"],
  "approvalQuorum": 1,
  "externalSharing": true
}</textarea><div class="sc-ig0390-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="govern">Configure workspace</button><button type="button" class="sc-lab-button" data-ig-v0390-action="workspace">Inspect profile</button></div></div>
          <div class="sc-ig0390-card"><h4>Policy evaluation</h4><textarea data-ig-v0390-evaluate-json>{
  "action": "research.share",
  "resourceType": "dataset",
  "resourceId": "wetland-observations-v1",
  "classification": "confidential"
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="evaluate">Evaluate action</button></div>
          <div class="sc-ig0390-card"><h4>Approval request and decision</h4><textarea data-ig-v0390-approval-json>{
  "id": "wetland-share-approval",
  "requestType": "research-action",
  "action": "research.share",
  "resourceType": "dataset",
  "resourceId": "wetland-observations-v1",
  "request": {"summary":"Share aggregate indicators"}
}</textarea><label>Approval request ID<input data-ig-v0390-approval value="wetland-share-approval"></label><textarea data-ig-v0390-decision-json>{"decision":"approve","rationale":"Aggregate public-interest data only"}</textarea><div class="sc-ig0390-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ig-v0390-action="request-approval">Request approval</button><button type="button" class="sc-lab-button" data-ig-v0390-action="approvals">List approvals</button><button type="button" class="sc-lab-button" data-ig-v0390-action="decide">Record decision</button></div></div>
          <div class="sc-ig0390-card is-wide"><h4>Institutional governance response</h4><pre class="sc-ig0390-output" data-ig-v0390-output>No response yet.</pre></div>
        </div>
      </section>



      <section class="sc-lab-panel sc-beta0400" data-lab-module="connected-platform-beta-v0400" data-module-panel="connected-platform-beta-v0400" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PLATFORM / CONTROLLED BETA / v0.40.0</p><h3>Connected Scientific Research Platform Beta</h3><p>Operate controlled institutional cohorts, guide complete research journeys, collect privacy-minimized opt-in telemetry, triage feedback and limitations, connect support pathways, and evaluate beta release readiness across the Lab’s governance, security, interoperability, recovery, and validation layers.</p></header>
        <div class="sc-beta0400-banner"><strong>Controlled beta boundary</strong><span>This release does not claim general availability. Beta operations never bypass institutional controls, and telemetry never stores raw identifiers or research payloads.</span></div>
        <p class="sc-beta0400-status" data-beta-v0400-status role="status" aria-live="polite">Connecting to connected platform beta operations…</p>
        <div class="sc-beta0400-metrics" data-beta-v0400-metrics></div>
        <div class="sc-beta0400-grid">
          <div class="sc-beta0400-card"><h4>Institutional beta cohort</h4><textarea data-beta-v0400-cohort-json>{
  "id": "institutional-beta-one",
  "name": "Institutional Research Beta One",
  "institutionId": "institution-one",
  "status": "active",
  "goals": ["Validate complete research workflow", "Document operating limitations"]
}</textarea><div class="sc-beta0400-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-beta-v0400-action="create-cohort">Create cohort</button><button type="button" class="sc-lab-button" data-beta-v0400-action="cohorts">List cohorts</button><button type="button" class="sc-lab-button" data-beta-v0400-action="catalog">Beta catalog</button><button type="button" class="sc-lab-button" data-beta-v0400-action="policies">Policies</button></div></div>
          <div class="sc-beta0400-card"><h4>Institution onboarding journey</h4><textarea data-beta-v0400-onboarding-json>{
  "id": "institution-one-onboarding",
  "cohortId": "institutional-beta-one",
  "institutionId": "institution-one",
  "principalId": "beta-research-lead",
  "workspaceId": "wetland-research"
}</textarea><label>Onboarding ID<input data-beta-v0400-onboarding-id value="institution-one-onboarding"></label><textarea data-beta-v0400-onboarding-advance-json>{"stage":"identity","completedItems":["Institution record verified"]}</textarea><div class="sc-beta0400-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-beta-v0400-action="start-onboarding">Start onboarding</button><button type="button" class="sc-lab-button" data-beta-v0400-action="advance-onboarding">Advance one stage</button><button type="button" class="sc-lab-button" data-beta-v0400-action="onboarding">List onboarding</button></div></div>
          <div class="sc-beta0400-card"><h4>Guided end-to-end research project</h4><textarea data-beta-v0400-project-json>{
  "id": "wetland-beta-project",
  "templateId": "evidence-to-experiment",
  "title": "Wetland resilience evidence study",
  "cohortId": "institutional-beta-one",
  "workspaceId": "wetland-research",
  "researchQuestion": "How does drought frequency affect wetland resilience?"
}</textarea><label>Project ID<input data-beta-v0400-project-id value="wetland-beta-project"></label><textarea data-beta-v0400-project-advance-json>{"stage":"source","outputs":{"evidenceRecord":"evidence:wetland-v1"}}</textarea><div class="sc-beta0400-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-beta-v0400-action="create-project">Create guided project</button><button type="button" class="sc-lab-button" data-beta-v0400-action="advance-project">Advance one stage</button><button type="button" class="sc-lab-button" data-beta-v0400-action="projects">List projects</button><button type="button" class="sc-lab-button" data-beta-v0400-action="templates">Templates</button></div></div>
          <div class="sc-beta0400-card"><h4>Privacy-minimized beta telemetry</h4><textarea data-beta-v0400-telemetry-json>{
  "id": "wetland-module-opened",
  "eventType": "module.opened",
  "workspaceId": "wetland-research",
  "optIn": true,
  "properties": {"module":"experiment-framework-v0300","surface":"wordpress"}
}</textarea><div class="sc-beta0400-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-beta-v0400-action="telemetry">Record opted-in event</button><button type="button" class="sc-lab-button" data-beta-v0400-action="telemetry-summary">Telemetry summary</button></div><p class="sc-beta0400-note">Actor and workspace identifiers are hashed. Raw identifiers, secrets, restricted data, and research payloads are rejected.</p></div>
          <div class="sc-beta0400-card"><h4>Feedback and known limitations</h4><textarea data-beta-v0400-feedback-json>{
  "id": "feedback-navigation-one",
  "category": "usability",
  "severity": "medium",
  "title": "Research stage navigation",
  "description": "The transition from analysis to review needs clearer guidance.",
  "projectId": "wetland-beta-project"
}</textarea><textarea data-beta-v0400-limitation-json>{
  "id": "limitation-offline-size",
  "severity": "medium",
  "title": "Large offline package validation",
  "description": "Very large field packages require additional beta testing.",
  "workaround": "Split the package into governed collections.",
  "targetRelease": "0.40.2"
}</textarea><div class="sc-beta0400-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-beta-v0400-action="feedback">Submit feedback</button><button type="button" class="sc-lab-button" data-beta-v0400-action="feedback-list">List feedback</button><button type="button" class="sc-lab-button" data-beta-v0400-action="create-limitation">Register limitation</button><button type="button" class="sc-lab-button" data-beta-v0400-action="limitations">List limitations</button></div></div>
          <div class="sc-beta0400-card"><h4>Support and incident pathway</h4><textarea data-beta-v0400-support-json>{
  "id": "support-institution-setup",
  "severity": "high",
  "title": "Institutional beta setup assistance",
  "summary": "Research administrators need assistance completing the governance and workspace setup.",
  "workspaceId": "wetland-research"
}</textarea><div class="sc-beta0400-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-beta-v0400-action="create-support">Create support case</button><button type="button" class="sc-lab-button" data-beta-v0400-action="support">List support cases</button></div></div>
          <div class="sc-beta0400-card"><h4>Beta release-readiness gate</h4><textarea data-beta-v0400-readiness-json>{"id":"v0.40.0-institutional-beta-readiness"}</textarea><div class="sc-beta0400-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-beta-v0400-action="readiness">Evaluate readiness</button><button type="button" class="sc-lab-button" data-beta-v0400-action="readiness-list">Prior reports</button><button type="button" class="sc-lab-button" data-beta-v0400-action="timeline">Beta timeline</button><button type="button" class="sc-lab-button" data-beta-v0400-action="verify-timeline">Verify timeline</button><button type="button" class="sc-lab-button" data-beta-v0400-action="refresh">Refresh dashboard</button></div><p class="sc-beta0400-note">Expansion is blocked when a required platform component is degraded or a critical feedback, limitation, or support record remains unresolved.</p></div>
          <div class="sc-beta0400-card is-wide"><h4>Beta operations response</h4><pre class="sc-beta0400-output" data-beta-v0400-output>No response yet.</pre></div>
        </div>
      </section>


      <section class="sc-lab-panel sc-if0401" data-lab-module="interface-finalization-v0401" data-module-panel="interface-finalization-v0401" data-service-worker-url="<?php echo esc_url(home_url('/?sc_lab_sw_v0401=1')); ?>" data-offline-public="<?php echo is_user_logged_in() ? '0' : '1'; ?>" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">INTERFACE / ACCESSIBILITY / MOBILE / OFFLINE / v0.40.1</p><h3>Accessible Mobile and Offline Research Workspace</h3><p>Audit the active Lab interface at phone, tablet, and desktop widths, apply accessibility preferences, retain browser-local project snapshots, queue disconnected work, reconcile conflicts explicitly, and opt into a restricted-data-safe offline shell.</p></header>
        <div class="sc-if0401-banner"><strong>Finalization boundary</strong><span>Automated checks support WCAG 2.2 AA-oriented review but do not claim certification. The backend stores only offline metadata and hashes; raw project snapshots remain in this browser. Restricted records are never eligible for offline caching.</span></div>
        <p class="sc-if0401-status" data-if-v0401-status role="status" aria-live="polite">Checking connection and interface state…</p>
        <div class="sc-if0401-metrics" data-if-v0401-metrics></div>
        <div class="sc-if0401-grid">
          <div class="sc-if0401-card"><h4>Responsive accessibility audit</h4><p class="sc-if0401-note">Runs a browser audit for overflow, 44 px targets, keyboard behavior, accessible names, live regions, dialogs, tables, visualizations, reduced motion, forced colors, and text zoom.</p><div class="sc-if0401-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-if-v0401-action="audit">Audit current viewport</button><button type="button" class="sc-lab-button" data-if-v0401-action="audits">Prior audits</button><button type="button" class="sc-lab-button" data-if-v0401-action="catalog">Audit catalog</button><button type="button" class="sc-lab-button" data-if-v0401-action="policies">Policies</button></div></div>
          <div class="sc-if0401-card"><h4>Accessibility and data-use preferences</h4><label>Profile ID<input data-if-v0401-profile-id value="default-researcher"></label><textarea data-if-v0401-preferences-json>{
  "reducedMotion": false,
  "increasedContrast": false,
  "largeText": false,
  "dataSaver": false,
  "touchTargetMinimumPx": 44
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-if-v0401-action="save-preferences">Save and apply preferences</button></div>
          <div class="sc-if0401-card"><h4>Opt-in offline shell</h4><p class="sc-if0401-note">Caches static Lab assets. A public Lab page is cached only after this explicit action; authenticated pages are not cached. Offline research payloads stay in IndexedDB on this device.</p><button type="button" class="sc-lab-button sc-lab-button-primary" data-if-v0401-action="enable-shell">Enable offline shell</button></div>
          <div class="sc-if0401-card"><h4>Browser-local project snapshot</h4><textarea data-if-v0401-local-json>{
  "id": "wetland-local-snapshot",
  "projectId": "wetland-beta-project",
  "workspaceId": "wetland-research",
  "classification": "internal",
  "draft": {"stage":"analyze","notes":"Browser-local draft only"}
}</textarea><div class="sc-if0401-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-if-v0401-action="save-local">Save locally</button><button type="button" class="sc-lab-button" data-if-v0401-action="list-local">List local snapshots</button></div></div>
          <div class="sc-if0401-card"><h4>Governed offline snapshot metadata</h4><textarea data-if-v0401-snapshot-json>{
  "id": "wetland-offline-manifest",
  "projectId": "wetland-beta-project",
  "workspaceId": "wetland-research",
  "classification": "internal",
  "assets": [{"id":"evidence-index","url":"/research/evidence-index.json","sha256":"2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881","sizeBytes":1,"mediaType":"application/json","classification":"internal"}]
}</textarea><div class="sc-if0401-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-if-v0401-action="register-snapshot">Register metadata</button><button type="button" class="sc-lab-button" data-if-v0401-action="snapshots">List metadata</button></div></div>
          <div class="sc-if0401-card"><h4>Disconnected operation queue</h4><textarea data-if-v0401-operation-json>{
  "id": "wetland-draft-op-1",
  "idempotencyKey": "wetland-draft-op-1",
  "workspaceId": "wetland-research",
  "projectId": "wetland-beta-project",
  "operation": "save-draft",
  "baseVersion": "project-v3",
  "payload": {"stage":"analyze","summary":"Offline draft reference"}
}</textarea><div class="sc-if0401-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-if-v0401-action="queue">Queue operation</button><button type="button" class="sc-lab-button" data-if-v0401-action="operations">List queue</button></div></div>
          <div class="sc-if0401-card"><h4>Explicit synchronization reconciliation</h4><textarea data-if-v0401-reconcile-json>{
  "id": "wetland-reconciliation-1",
  "decisions": [{"operationId":"wetland-draft-op-1","status":"applied","remoteVersion":"project-v4","resolution":"Applied after reconnect"}]
}</textarea><div class="sc-if0401-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-if-v0401-action="reconcile">Reconcile queue</button><button type="button" class="sc-lab-button" data-if-v0401-action="verify">Verify event chain</button><button type="button" class="sc-lab-button" data-if-v0401-action="refresh">Refresh dashboard</button></div></div>
          <div class="sc-if0401-card is-wide"><h4>Interface and offline operations response</h4><pre class="sc-if0401-output" data-if-v0401-output>No response yet.</pre></div>
        </div>
      </section>


      <section class="sc-lab-panel sc-cp1000" data-lab-module="connected-platform-v1000" data-module-panel="connected-platform-v1000" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">STABLE / CONNECTED / RESEARCH / COMPUTE / v1.0.0</p><h3>Connected Scientific Research and Compute Platform</h3><p>Register stable public contracts, certify upgrades, declare support lifecycles, attest production and incident readiness, and issue evidence-bound general-availability certifications for the complete connected research platform.</p></header>
        <div class="sc-cp1000-banner"><strong>Stable release boundary.</strong> Breaking public-contract changes require a major version. The API cannot overwrite production files, store credentials, or certify general availability while evidence is missing or critical defects remain.</div>
        <p class="sc-cp1000-status" data-cp-v1000-status role="status" aria-live="polite">Connecting to the stable platform…</p>
        <div class="sc-cp1000-metrics" data-cp-v1000-metrics></div>
        <div class="sc-cp1000-grid">
          <div class="sc-cp1000-card"><h4>Stable contract registry</h4><textarea data-cp-v1000-contract>{"id":"research-api-v1","name":"Sustainable Catalyst Research API","versions":["v1"],"status":"stable","compatibilityPolicy":"Semantic versioning; additive changes within v1 and breaking changes only in a new major version."}</textarea><div class="sc-cp1000-actions"><button class="sc-lab-button sc-lab-button-primary" data-cp-v1000-action="contract">Register contract</button><button class="sc-lab-button" data-cp-v1000-action="list-contracts">List</button></div></div>
          <div class="sc-cp1000-card"><h4>Support lifecycle</h4><textarea data-cp-v1000-support>{"id":"v1-support","releaseVersion":"1.0.0","status":"supported","supportStart":"2026-07-20","maintenanceEnd":"2027-07-20","securityEnd":"2028-07-20","migrationGuidance":"Use signed cumulative installers, verify backups, and retain rollback evidence."}</textarea><div class="sc-cp1000-actions"><button class="sc-lab-button sc-lab-button-primary" data-cp-v1000-action="support">Declare lifecycle</button><button class="sc-lab-button" data-cp-v1000-action="list-support-lifecycles">List</button></div></div>
          <div class="sc-cp1000-card"><h4>Upgrade certification</h4><textarea data-cp-v1000-upgrade>{"id":"v0402-to-v1000","baselineVersion":"0.40.2","backupVerified":true,"rollbackVerified":true,"migrationPassed":true,"packageParityVerified":true}</textarea><div class="sc-cp1000-actions"><button class="sc-lab-button sc-lab-button-primary" data-cp-v1000-action="upgrade">Certify upgrade</button><button class="sc-lab-button" data-cp-v1000-action="list-upgrade-certifications">List</button></div></div>
          <div class="sc-cp1000-card"><h4>Production readiness</h4><textarea data-cp-v1000-production>{"id":"v1-production","components":{"api":{"status":"pass"},"compute":{"status":"pass"},"wordpress":{"status":"pass"},"governance":{"status":"pass"},"security":{"status":"pass"},"recovery":{"status":"pass"},"monitoring":{"status":"pass"}},"monitoringEnabled":true,"persistentStorageVerified":true}</textarea><div class="sc-cp1000-actions"><button class="sc-lab-button sc-lab-button-primary" data-cp-v1000-action="production">Attest production</button><button class="sc-lab-button" data-cp-v1000-action="list-production-attestations">List</button></div></div>
          <div class="sc-cp1000-card"><h4>Incident readiness</h4><textarea data-cp-v1000-incident>{"id":"v1-incident","checks":[{"id":"incident-owner","status":"pass"},{"id":"severity-model","status":"pass"},{"id":"communications-path","status":"pass"},{"id":"rollback-path","status":"pass"},{"id":"backup-restore-path","status":"pass"},{"id":"audit-preservation","status":"pass"},{"id":"support-intake","status":"pass"},{"id":"post-incident-review","status":"pass"}]}</textarea><div class="sc-cp1000-actions"><button class="sc-lab-button sc-lab-button-primary" data-cp-v1000-action="incident">Attest incident readiness</button><button class="sc-lab-button" data-cp-v1000-action="list-incident-readiness">List</button></div></div>
          <div class="sc-cp1000-card"><h4>General availability</h4><textarea data-cp-v1000-ga>{"id":"sustainable-catalyst-lab-v1","evidence":{"stableContracts":{"status":"pass"},"upgradePath":{"status":"pass"},"cleanInstall":{"status":"pass"},"backupRestore":{"status":"pass"},"identityGovernance":{"status":"pass"},"securityPrivacy":{"status":"pass"},"loadResilience":{"status":"pass"},"accessibility":{"status":"pass"},"monitoring":{"status":"pass"},"apiSdkDocumentation":{"status":"pass"},"crossProductHandoffs":{"status":"pass"},"supportLifecycle":{"status":"pass"},"incidentReadiness":{"status":"pass"},"licensing":{"status":"pass"},"reproducibleArchives":{"status":"pass"}},"criticalDefects":[],"highDefects":[]}</textarea><div class="sc-cp1000-actions"><button class="sc-lab-button sc-lab-button-primary" data-cp-v1000-action="ga">Certify GA</button><button class="sc-lab-button" data-cp-v1000-action="list-ga-certifications">Prior certifications</button><button class="sc-lab-button" data-cp-v1000-action="verify">Verify timeline</button><button class="sc-lab-button" data-cp-v1000-action="catalog">Catalog</button><button class="sc-lab-button" data-cp-v1000-action="refresh">Refresh</button></div></div>
          <div class="sc-cp1000-card is-wide"><h4>Stable platform response</h4><pre class="sc-cp1000-output" data-cp-v1000-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-prh0402" data-lab-module="public-release-hardening-v0402" data-module-panel="public-release-hardening-v0402" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">RELEASE / MIGRATION / COMPATIBILITY / v0.40.2</p><h3>Migration, Compatibility, and Public Release Hardening</h3><p>Assess supported upgrades, publish compatibility matrices, retain deprecation guidance, prove clean installs and rollback procedures, and evaluate release-candidate evidence without force-pushing or overwriting production files through the API.</p></header>
        <div class="sc-prh0402-banner"><strong>Release boundary</strong><span>Migration is dry-run by default. A release-candidate-ready result is evidence, not a general-availability claim. Production activation remains operator controlled.</span></div>
        <p class="sc-prh0402-status" data-prh-v0402-status role="status" aria-live="polite">Connecting to public release hardening…</p><div class="sc-prh0402-metrics" data-prh-v0402-metrics></div>
        <div class="sc-prh0402-grid">
          <div class="sc-prh0402-card"><h4>Compatibility matrix</h4><textarea data-prh-v0402-compatibility>{"id":"v0402-compatibility","dimensions":{"wordpress":{"status":"supported","minimum":"6.4"},"php":{"status":"supported","minimum":"8.1"},"python":{"status":"supported","minimum":"3.12"},"browser":{"status":"supported","minimum":"current major versions"},"sdk":{"status":"supported","minimum":"0.40.2"}}}</textarea><div class="sc-prh0402-actions"><button class="sc-lab-button sc-lab-button-primary" data-prh-v0402-action="compatibility">Record matrix</button><button class="sc-lab-button" data-prh-v0402-action="list-compatibility">List</button></div></div>
          <div class="sc-prh0402-card"><h4>Migration dry run</h4><textarea data-prh-v0402-migration>{"id":"v0401-to-v0402","baselineVersion":"0.40.1","targetVersion":"0.40.2","backupVerified":true,"rollbackTested":true}</textarea><div class="sc-prh0402-actions"><button class="sc-lab-button sc-lab-button-primary" data-prh-v0402-action="migration">Assess migration</button><button class="sc-lab-button" data-prh-v0402-action="list-migrations">List</button></div></div>
          <div class="sc-prh0402-card"><h4>Deprecation registry</h4><textarea data-prh-v0402-deprecation>{"id":"legacy-v0-route","subject":"Legacy v0 integration route","status":"announced","replacement":"Stable /v1 research API","removalVersion":"1.1.0","migrationGuidance":"Move integrations to the documented v1 route before removal."}</textarea><div class="sc-prh0402-actions"><button class="sc-lab-button sc-lab-button-primary" data-prh-v0402-action="deprecation">Register</button><button class="sc-lab-button" data-prh-v0402-action="list-deprecations">List</button></div></div>
          <div class="sc-prh0402-card"><h4>Clean-install report</h4><textarea data-prh-v0402-clean>{"id":"v0402-clean-install","checks":[{"id":"source-integrity","status":"pass"},{"id":"database-bootstrap","status":"pass"},{"id":"api-health","status":"pass"},{"id":"wordpress-activation","status":"pass"},{"id":"sdk-discovery","status":"pass"},{"id":"offline-shell-opt-in","status":"pass"},{"id":"security-headers","status":"pass"},{"id":"documentation","status":"pass"}]}</textarea><div class="sc-prh0402-actions"><button class="sc-lab-button sc-lab-button-primary" data-prh-v0402-action="clean">Record clean install</button><button class="sc-lab-button" data-prh-v0402-action="list-clean-installs">List</button></div></div>
          <div class="sc-prh0402-card"><h4>Rollback proof</h4><textarea data-prh-v0402-rollback>{"id":"v0402-rollback","backupId":"pre-v0402-backup","tested":true,"restoreVerified":true,"activationProcedure":"Stage, verify, stop writes, activate restored database, smoke-test, then reopen traffic."}</textarea><div class="sc-prh0402-actions"><button class="sc-lab-button sc-lab-button-primary" data-prh-v0402-action="rollback">Record rollback</button><button class="sc-lab-button" data-prh-v0402-action="list-rollbacks">List</button></div></div>
          <div class="sc-prh0402-card"><h4>Release-candidate gate</h4><textarea data-prh-v0402-candidate>{"id":"v0.40.2-rc","evidence":{"migration":{"status":"pass"},"compatibility":{"status":"pass"},"cleanInstall":{"status":"pass"},"rollback":{"status":"pass"},"security":{"status":"pass"},"licensing":{"status":"pass"},"documentation":{"status":"pass"},"archives":{"status":"pass"},"tests":{"status":"pass"}},"criticalDefects":[],"highDefects":[]}</textarea><div class="sc-prh0402-actions"><button class="sc-lab-button sc-lab-button-primary" data-prh-v0402-action="candidate">Evaluate candidate</button><button class="sc-lab-button" data-prh-v0402-action="list-release-candidates">Prior reports</button><button class="sc-lab-button" data-prh-v0402-action="verify">Verify timeline</button><button class="sc-lab-button" data-prh-v0402-action="catalog">Catalog</button><button class="sc-lab-button" data-prh-v0402-action="refresh">Refresh</button></div></div>
          <div class="sc-prh0402-card is-wide"><h4>Release-hardening response</h4><pre class="sc-prh0402-output" data-prh-v0402-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-pc0393" data-lab-module="performance-chaos-v0393" data-module-panel="performance-chaos-v0393" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">SYSTEM / RELEASE VALIDATION / v0.39.3</p><h3>Performance, Load, and Chaos Validation</h3><p>Measure latency percentiles and throughput, enforce explicit performance budgets, inject bounded failures into isolated resources, and produce evidence-bounded capacity reports without destructive production chaos or external traffic.</p></header>
        <p class="sc-pc0393-status" data-pc-v0393-status role="status" aria-live="polite">Connecting to performance validation…</p>
        <div class="sc-pc0393-metrics" data-pc-v0393-metrics></div>
        <div class="sc-pc0393-grid">
          <div class="sc-pc0393-card"><h4>Load validation</h4><textarea data-pc-v0393-load-json>{
  "id": "api-read-beta-baseline",
  "profile": "api-read",
  "iterations": 200,
  "concurrency": 8,
  "payloadBytes": 4096,
  "budget": {"p95Ms": 250, "maxErrorRate": 0.01, "minThroughputPerSecond": 10}
}</textarea><div class="sc-pc0393-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pc-v0393-action="load">Run load profile</button><button type="button" class="sc-lab-button" data-pc-v0393-action="catalog">Catalog</button><button type="button" class="sc-lab-button" data-pc-v0393-action="policies">Policies</button></div><p class="sc-pc0393-note">Validation workloads use temporary or dedicated validation resources. They do not mutate active research records.</p></div>
          <div class="sc-pc0393-card"><h4>Safe chaos scenario</h4><textarea data-pc-v0393-chaos-json>{
  "id": "database-lock-recovery",
  "scenario": "database-lock"
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-pc-v0393-action="chaos">Run isolated scenario</button><p class="sc-pc0393-note">Available scenarios: database lock, storage latency, worker termination, network timeout simulation, and partial-write rejection. Production chaos remains disabled.</p></div>
          <div class="sc-pc0393-card"><h4>Capacity evidence</h4><textarea data-pc-v0393-capacity-json>{"id":"beta-capacity-report","limit":100}</textarea><div class="sc-pc0393-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pc-v0393-action="capacity">Create capacity report</button><button type="button" class="sc-lab-button" data-pc-v0393-action="runs">List runs</button><button type="button" class="sc-lab-button" data-pc-v0393-action="refresh">Refresh dashboard</button></div><p class="sc-pc0393-note">Reports summarize validated evidence only and never claim production sizing without production-equivalent tests.</p></div>
          <div class="sc-pc0393-card is-wide"><h4>Validation response</h4><pre class="sc-pc0393-output" data-pc-v0393-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-mi0392" data-lab-module="multi-instance-operations-v0392" data-module-panel="multi-instance-operations-v0392" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">SYSTEM / RECOVERY OPERATIONS / v0.39.2</p><h3>Multi-Instance Operations, Backup, Migration, and Disaster Recovery</h3><p>Identify this Lab instance, create consistent signed backups, verify archives, stage non-destructive restores, execute idempotent migration plans, transfer governed recovery bundles between instances, and validate recovery objectives.</p></header>
        <p class="sc-mi0392-status" data-mi-v0392-status role="status" aria-live="polite">Connecting to recovery operations…</p>
        <div class="sc-mi0392-metrics" data-mi-v0392-metrics></div>
        <div class="sc-mi0392-grid">
          <div class="sc-mi0392-card"><h4>Instance registry</h4><textarea data-mi-v0392-instance-json>{
  "id": "sc-lab-secondary",
  "name": "Secondary Research Node",
  "environment": "production",
  "region": "us-central",
  "publicUrl": "https://lab-secondary.example.org",
  "role": "recovery"
}</textarea><div class="sc-mi0392-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-mi-v0392-action="register-instance">Register peer</button><button type="button" class="sc-lab-button" data-mi-v0392-action="instance">Local instance</button><button type="button" class="sc-lab-button" data-mi-v0392-action="instances">All instances</button><button type="button" class="sc-lab-button" data-mi-v0392-action="policies">Policies</button></div></div>
          <div class="sc-mi0392-card"><h4>Consistent backup and verification</h4><textarea data-mi-v0392-backup-json>{
  "label": "pre-release-v0.39.2",
  "artifactMode": "manifest",
  "includeSources": []
}</textarea><label>Backup ID<input data-mi-v0392-backup placeholder="backup identifier"></label><textarea data-mi-v0392-restore-json>{"targetName":"verification-restore"}</textarea><div class="sc-mi0392-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-mi-v0392-action="create-backup">Create backup</button><button type="button" class="sc-lab-button" data-mi-v0392-action="backups">List</button><button type="button" class="sc-lab-button" data-mi-v0392-action="verify-backup">Verify</button><button type="button" class="sc-lab-button" data-mi-v0392-action="stage-restore">Stage restore</button></div><p class="sc-mi0392-note">API restores are staged and verified. They never overwrite active production files.</p></div>
          <div class="sc-mi0392-card"><h4>Migration journal</h4><textarea data-mi-v0392-migration-json>{
  "sourceVersion": "0.39.1",
  "targetVersion": "0.39.2",
  "backupId": "replace-with-verified-backup-id",
  "steps": [
    {"id":"validate-backup","kind":"validation"},
    {"id":"deploy-release","kind":"deployment"}
  ]
}</textarea><label>Migration ID<input data-mi-v0392-migration placeholder="migration identifier"></label><textarea data-mi-v0392-execute-json>{"confirmed":true}</textarea><div class="sc-mi0392-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-mi-v0392-action="create-migration">Create plan</button><button type="button" class="sc-lab-button" data-mi-v0392-action="execute-migration">Execute once</button></div></div>
          <div class="sc-mi0392-card"><h4>Cross-instance recovery transfer</h4><textarea data-mi-v0392-transfer-json>{
  "backupId": "replace-with-verified-backup-id",
  "targetInstanceId": "sc-lab-secondary"
}</textarea><label>Transfer ID<input data-mi-v0392-transfer placeholder="transfer identifier"></label><textarea data-mi-v0392-import-json>{"fileName":"replace-with-transfer-file.zip"}</textarea><div class="sc-mi0392-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-mi-v0392-action="create-transfer">Create transfer</button><button type="button" class="sc-lab-button" data-mi-v0392-action="verify-transfer">Verify</button><button type="button" class="sc-lab-button" data-mi-v0392-action="import-transfer">Import</button></div></div>
          <div class="sc-mi0392-card"><h4>Recovery drill</h4><textarea data-mi-v0392-drill-json>{
  "backupId": "replace-with-verified-backup-id",
  "targetName": "quarterly-recovery-drill"
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-mi-v0392-action="run-drill">Run RPO/RTO drill</button></div>
          <div class="sc-mi0392-card is-wide"><h4>Operations response</h4><div class="sc-mi0392-actions"><button type="button" class="sc-lab-button" data-mi-v0392-action="refresh">Refresh dashboard</button></div><pre class="sc-mi0392-output" data-mi-v0392-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-pri0382" data-lab-module="public-research-integrations" data-module-panel="public-research-integrations" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / EXTERNAL INTEGRATIONS / v0.38.2</p><h3>Public API, Webhooks, Embeds, and Research SDK</h3><p>Operate the stable research API surface, create scoped HTTPS webhook subscriptions, issue signed public-reference embeds, and inspect the dependency-light Python, TypeScript, and browser SDK packages.</p></header>
        <p class="sc-pri0382-status" data-pri-v0382-status role="status" aria-live="polite">Connecting to the public research integration service…</p>
        <div class="sc-pri0382-metrics" data-pri-v0382-metrics></div>
        <div class="sc-pri0382-grid">
          <div class="sc-pri0382-card"><h4>API and SDK discovery</h4><label>Workspace ID<input data-pri-v0382-workspace value="research-team"></label><div class="sc-pri0382-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pri-v0382-action="catalog">API catalog</button><button type="button" class="sc-lab-button" data-pri-v0382-action="policies">Policies</button><button type="button" class="sc-lab-button" data-pri-v0382-action="sdk">SDK manifest</button><button type="button" class="sc-lab-button" data-pri-v0382-action="refresh">Health</button></div><p class="sc-pri0382-note">The public catalog and SDK manifest describe stable <code>/v1</code> routes. Protected operations remain workspace- and scope-governed.</p></div>
          <div class="sc-pri0382-card"><h4>Register an HTTPS webhook</h4><textarea data-pri-v0382-webhook-json>{
  "id": "decision-studio-hook",
  "url": "https://example.org/hooks/sustainable-catalyst",
  "events": ["research.handoff.sealed", "research.dataset.updated"],
  "description": "Decision Studio research intake"
}</textarea><div class="sc-pri0382-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-pri-v0382-action="register-webhook">Register webhook</button><button type="button" class="sc-lab-button" data-pri-v0382-action="webhooks">List webhooks</button></div><p class="sc-pri0382-note">The signing secret is shown only once. Store it outside WordPress and browser code.</p></div>
          <div class="sc-pri0382-card"><h4>Webhook lifecycle and delivery</h4><label>Subscription ID<input data-pri-v0382-subscription value="decision-studio-hook"></label><textarea data-pri-v0382-webhook-update-json>{"status":"paused","description":"Paused for maintenance"}</textarea><label>Delivery ID<input data-pri-v0382-delivery value="delivery-id"></label><div class="sc-pri0382-actions"><button type="button" class="sc-lab-button" data-pri-v0382-action="update-webhook">Update webhook</button><button type="button" class="sc-lab-button" data-pri-v0382-action="deliveries">List deliveries</button><button type="button" class="sc-lab-button" data-pri-v0382-action="dispatch">Dispatch delivery</button></div><p class="sc-pri0382-note">Outbound network delivery is disabled by default and must be explicitly enabled in the backend environment.</p></div>
          <div class="sc-pri0382-card"><h4>Emit a governed research event</h4><textarea data-pri-v0382-event-json>{
  "id": "wetland-dataset-updated",
  "eventType": "research.dataset.updated",
  "subject": "dataset:wetland-observations-v1",
  "data": {"datasetId":"wetland-observations-v1","sha256":"1111111111111111111111111111111111111111111111111111111111111111"}
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-pri-v0382-action="emit">Sign and queue event</button><p class="sc-pri0382-note">Events contain references, hashes, and policy-approved metadata—not secrets, executable payloads, or restricted dataset bytes.</p></div>
          <div class="sc-pri0382-card"><h4>Create a signed research embed</h4><textarea data-pri-v0382-embed-json>{
  "view": "publication",
  "resource": {"id":"wetland-report-v1","title":"Wetland Research Report","sha256":"2222222222222222222222222222222222222222222222222222222222222222"},
  "metadata": {"summary":"Public research reference"},
  "ttlSeconds": 3600
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-pri-v0382-action="embed">Create signed embed</button><p class="sc-pri0382-note">Embed manifests expire and expose public references only. The browser SDK verifies and renders the returned manifest path.</p></div>
          <div class="sc-pri0382-card is-wide"><h4>Integration response</h4><pre class="sc-pri0382-output" data-pri-v0382-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-th0381" data-lab-module="typed-cross-product-handoffs" data-module-panel="typed-cross-product-handoffs" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / PRODUCT ROUTING / v0.38.1</p><h3>Typed Cross-Product Research Handoffs</h3><p>Plan, validate, normalize, and create governed research handoffs through executable product adapters. Every route is contract-bound, target-aware, hash-identified, and delivered through the existing workspace-governed interoperability layer.</p></header>
        <p class="sc-th0381-status" data-th0381-status role="status" aria-live="polite">Loading typed product adapters…</p>
        <div class="sc-th0381-metrics" data-th0381-metrics></div>
        <div class="sc-th0381-grid">
          <div class="sc-th0381-card"><h4>Typed handoff request</h4><label>Workspace ID<input data-th0381-workspace value="research-team"></label><textarea data-th0381-json aria-label="Typed research handoff JSON">{
  "id": "wetland-decision-handoff",
  "sourceProduct": "sustainable-catalyst-lab",
  "targetProduct": "decision-studio",
  "entityType": "dataset",
  "resource": {
    "id": "wetland-observations-v1",
    "title": "Wetland observations",
    "sha256": "1111111111111111111111111111111111111111111111111111111111111111",
    "mediaType": "text/csv",
    "metadata": {"rows": 42}
  },
  "provenance": {"runIds": ["run-1"]}
}</textarea><div class="sc-th0381-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-th0381-action="plan">Validate and plan</button><button type="button" class="sc-lab-button" data-th0381-action="create">Create governed handoff</button><button type="button" class="sc-lab-button" data-th0381-action="routes">Resolve route</button><button type="button" class="sc-lab-button" data-th0381-action="catalog">Adapter catalog</button><button type="button" class="sc-lab-button" data-th0381-action="refresh">Health</button></div><p class="sc-th0381-note">Add both <code>sourceProfileId</code> and <code>targetProfileId</code> to create and seal the handoff in one editor-authorized operation.</p></div>
          <div class="sc-th0381-card"><h4>Adapter, route, plan, and handoff output</h4><pre class="sc-th0381-output" data-th0381-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-ri0380" data-lab-module="research-interoperability" data-module-panel="research-interoperability" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / PLATFORM EXCHANGE / v0.38.0</p><h3>Sustainable Catalyst Research Interoperability Layer</h3><p>Negotiate typed contracts, create canonical cross-product research handoffs, import compatible envelopes idempotently, and preserve signed delivery receipts without arbitrary callbacks or embedded restricted data.</p></header>
        <p class="sc-ri0380-status" data-ri-v0380-status role="status" aria-live="polite">Connecting to the research interoperability layer…</p>
        <div class="sc-ri0380-metrics" data-ri-v0380-metrics></div>
        <div class="sc-ri0380-grid">
          <div class="sc-ri0380-card"><h4>Workspace and product profile</h4><label>Workspace ID<input data-ri-v0380-workspace value="research-team"></label><textarea data-ri-v0380-profile-json>{
  "id": "lab-profile",
  "productId": "sustainable-catalyst-lab",
  "displayName": "Sustainable Catalyst Lab",
  "supportedContracts": ["sc-research-dataset/1.0", "sc-research-workflow/1.0"],
  "capabilities": ["sha256-resources", "provenance", "workspace-governance"]
}</textarea><div class="sc-ri0380-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ri-v0380-action="register-profile">Register profile</button><button type="button" class="sc-lab-button" data-ri-v0380-action="profiles">List profiles</button></div></div>
          <div class="sc-ri0380-card"><h4>Compatibility negotiation</h4><textarea data-ri-v0380-negotiate-json>{
  "sourceProfileId": "lab-profile",
  "targetProfileId": "decision-profile",
  "requestedContracts": ["sc-research-dataset/1.0"],
  "requiredCapabilities": ["sha256-resources", "provenance"]
}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-ri-v0380-action="negotiate">Negotiate compatibility</button><p class="sc-ri0380-note">Profiles declare supported contract versions and capabilities. The coordinator selects only shared, active contracts.</p></div>
          <div class="sc-ri0380-card is-wide"><h4>Canonical research handoff</h4><label>Handoff ID<input data-ri-v0380-handoff value="wetland-dataset-handoff"></label><textarea data-ri-v0380-handoff-json>{
  "id": "wetland-dataset-handoff",
  "sourceProduct": "sustainable-catalyst-lab",
  "targetProduct": "decision-studio",
  "entityType": "dataset",
  "contractVersion": "sc-research-dataset/1.0",
  "resource": {"id":"wetland-dataset-v1","title":"Wetland observations","sha256":"1111111111111111111111111111111111111111111111111111111111111111","mediaType":"text/csv","metadata":{"rows":42}},
  "provenance": {"runIds":["run-1"],"workspaceSnapshot":"2222222222222222222222222222222222222222222222222222222222222222"},
  "requiredCapabilities": ["sha256-resources", "provenance"]
}</textarea><textarea data-ri-v0380-seal-json>{"sourceProfileId":"lab-profile","targetProfileId":"decision-profile"}</textarea><div class="sc-ri0380-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ri-v0380-action="create">Create handoff</button><button type="button" class="sc-lab-button" data-ri-v0380-action="seal">Seal</button><button type="button" class="sc-lab-button" data-ri-v0380-action="bundle">Export bundle</button><button type="button" class="sc-lab-button" data-ri-v0380-action="inspect">Inspect</button><button type="button" class="sc-lab-button" data-ri-v0380-action="handoffs">List handoffs</button></div></div>
          <div class="sc-ri0380-card"><h4>Import compatible envelope</h4><textarea data-ri-v0380-import-json>{"importId":"incoming-handoff","envelope":{},"envelopeHash":"replace-with-exported-envelope-hash"}</textarea><button type="button" class="sc-lab-button sc-lab-button-primary" data-ri-v0380-action="import">Import envelope</button><p class="sc-ri0380-note">Imports are canonical-hash verified and idempotent. Duplicate envelopes return the original receipt rather than creating another record.</p></div>
          <div class="sc-ri0380-card"><h4>Receipt and withdrawal</h4><textarea data-ri-v0380-receipt-json>{"id":"receipt-example","decision":"accepted","details":{"importedResourceId":"decision-resource-1"}}</textarea><label>Receipt SHA-256<input data-ri-v0380-receipt value="receipt-hash"></label><textarea data-ri-v0380-withdraw-json>{"reason":"Superseded by a corrected handoff."}</textarea><div class="sc-ri0380-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-ri-v0380-action="receipt">Record receipt</button><button type="button" class="sc-lab-button" data-ri-v0380-action="verify-receipt">Verify receipt</button><button type="button" class="sc-lab-button" data-ri-v0380-action="withdraw">Withdraw</button><button type="button" class="sc-lab-button" data-ri-v0380-action="timeline">Timeline</button></div></div>
          <div class="sc-ri0380-card is-wide"><h4>Profiles, negotiations, handoffs, receipts, and provenance</h4><pre class="sc-ri0380-output" data-ri-v0380-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-cl0332" data-lab-module="closed-loop-campaigns" data-module-panel="closed-loop-campaigns" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / EXPERIMENT CONTROL / v0.33.2</p><h3>Closed-Loop Simulation and Instrument Campaigns</h3><p>Connect adaptive campaigns to repeated simulation cycles or signed instrument measurements while preserving operator review, safety interlocks, measurement integrity, and complete campaign/workflow/command provenance.</p></header>
        <p data-cl-v0332-status role="status" aria-live="polite">Closed-loop campaign engine loading…</p>
        <div class="sc-cl0332-metrics" data-cl-v0332-metrics></div>
        <div class="sc-cl0332-grid">
          <div class="sc-cl0332-card is-wide"><h4>Loop definition</h4><textarea data-cl-v0332-definition aria-label="Closed-loop campaign JSON">{
  "id": "reactor-optimization-loop",
  "title": "Bench reactor optimization loop",
  "projectId": "default",
  "campaignId": "bayesian-calibration-campaign",
  "mode": "instrument",
  "adapter": {"gatewayId": "bench-gateway-1", "protocol": "signed-envelope-v1", "capabilities": ["temperature", "flow", "yield"]},
  "safety": {
    "signalLimits": {"temperature": {"min": 10, "max": 90}},
    "parameterLimits": {"temperature": {"min": 20, "max": 80, "maxStepDelta": 10}, "flow": {"min": 0.5, "max": 5}},
    "emergencyStopSignals": ["emergencyStop"],
    "requireCommandApproval": true,
    "maxConsecutiveFailures": 3
  },
  "observation": {"objectivePath": "objectiveValue", "parameterPath": "parameters", "signalsPath": "signals", "requireSignature": false},
  "control": {"autoAdvance": true, "maxCycles": 25, "stopOnCampaignCompletion": true}
}</textarea><div class="sc-cl0332-actions"><button type="button" class="sc-lab-button" data-cl-v0332-action="validate">Validate</button><button type="button" class="sc-lab-button sc-lab-button-primary" data-cl-v0332-action="save">Save loop</button></div></div>
          <div class="sc-cl0332-card"><h4>Loop controls</h4><label>Loop ID<input data-cl-v0332-loopid value="reactor-optimization-loop"></label><label>Operator reason<input data-cl-v0332-reason value="operator action from Lab closed-loop panel"></label><div class="sc-cl0332-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-cl-v0332-action="start">Start</button><button type="button" class="sc-lab-button" data-cl-v0332-action="issue">Issue next command</button><button type="button" class="sc-lab-button" data-cl-v0332-action="reconcile">Reconcile</button><button type="button" class="sc-lab-button" data-cl-v0332-action="pause">Pause</button><button type="button" class="sc-lab-button" data-cl-v0332-action="resume">Resume</button><button type="button" class="sc-lab-button" data-cl-v0332-action="inspect">Inspect</button><button type="button" class="sc-lab-button" data-cl-v0332-action="timeline">Timeline</button><button type="button" class="sc-lab-button" data-cl-v0332-action="refresh">Refresh</button><button type="button" class="sc-lab-button" data-cl-v0332-action="emergency-stop">Emergency stop</button><button type="button" class="sc-lab-button" data-cl-v0332-action="cancel">Cancel</button></div><p class="sc-cl0332-note"><strong>Safety boundary:</strong> Lab emits reviewable command envelopes only. It does not open arbitrary callbacks or directly control physical devices.</p></div>
          <div class="sc-cl0332-card"><h4>Measurement ingestion</h4><textarea data-cl-v0332-measurement aria-label="Closed-loop measurement JSON">{
  "id": "measurement-example-1",
  "gatewayId": "bench-gateway-1",
  "commandId": "replace-with-issued-command-id",
  "parameters": {"temperature": 40, "flow": 2},
  "signals": {"temperature": 41.2, "yield": 0.82, "emergencyStop": false},
  "objectiveValue": 0.18
}</textarea><div class="sc-cl0332-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-cl-v0332-action="measurement">Ingest measurement</button></div></div>
          <div class="sc-cl0332-card is-wide"><h4>Loop, command, measurement, safety, cycle, and provenance records</h4><pre class="sc-cl0332-output" data-cl-v0332-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-pq0311" data-lab-module="persistent-queue" data-module-panel="persistent-queue" hidden>
        <h2>Persistent Queue Infrastructure</h2>
        <p>Inspect the durable distributed workload queue, leases, recovery state, and central event history.</p>
        <p data-pq-v0311-status role="status" aria-live="polite">Persistent queue loading…</p>
        <div class="sc-pq-grid" data-pq-v0311-metrics></div>
        <div class="sc-pq-card"><h3>Enqueue and lease</h3><label>Registered method <input data-pq-v0311-method value="simulation.parameter_sweep"></label><label>Priority <input data-pq-v0311-priority type="number" min="0" max="100" value="70"></label><label>Required packages <input data-pq-v0311-packages value="numpy"></label><label>Worker ID <input data-pq-v0311-worker value="browser-worker-default"></label><label>Lease seconds <input data-pq-v0311-lease-seconds type="number" min="30" max="3600" value="300"></label><div class="sc-pq-actions"><button type="button" data-pq-v0311-enqueue>Enqueue workload</button><button type="button" data-pq-v0311-claim>Claim next lease</button><button type="button" data-pq-v0311-renew>Renew lease</button><button type="button" data-pq-v0311-release>Release and requeue</button><button type="button" data-pq-v0311-recover>Run recovery</button><button type="button" data-pq-v0311-refresh>Refresh</button></div></div>
        <h3>Active leases</h3><div class="sc-lab-table-wrap"><table><thead><tr><th>Lease</th><th>Worker</th><th>Status</th><th>Expires</th></tr></thead><tbody data-pq-v0311-leases></tbody></table></div>
        <h3>Recent queue history</h3><div class="sc-lab-table-wrap"><table><thead><tr><th>Time</th><th>Entity</th><th>Event</th><th>ID</th></tr></thead><tbody data-pq-v0311-history></tbody></table></div>
        <pre data-pq-v0311-output aria-label="Persistent queue response">No response yet.</pre>
      </section>

      <section class="sc-lab-panel sc-do0314" data-lab-module="dispatcher-operations" data-module-panel="dispatcher-operations" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / DISTRIBUTED COMPUTE / v0.31.4</p><h3>Dispatcher Operations, Dead-Letter Recovery, and Observability</h3><p>Classify failed workloads, apply bounded retry policies, inspect dead-letter records, replay corrected work, cancel unsafe or obsolete jobs, trace dispatch events, and verify SQLite queue health from one governed operations workspace.</p></header>
        <p class="sc-do0314-status" data-do-v0314-status role="status" aria-live="polite">Dispatcher operations loading…</p>
        <div class="sc-do0314-metrics" data-do-v0314-metrics></div>
        <div class="sc-do0314-grid">
          <div class="sc-do0314-card">
            <h4>Dead-letter queue</h4>
            <label>Maximum records<input type="number" min="1" max="1000" value="100" data-do-v0314-limit></label>
            <div class="sc-do0314-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-do-v0314-refresh>Refresh operations</button><button type="button" class="sc-lab-button" data-do-v0314-recover>Run recovery</button><button type="button" class="sc-lab-button" data-do-v0314-diagnostics>Verify database</button></div>
            <div class="sc-do0314-table-wrap"><table class="sc-do0314-table"><thead><tr><th>Queue ID</th><th>Method</th><th>Project</th><th>Failure</th><th>Attempts</th><th>Dead-lettered</th><th>Actions</th></tr></thead><tbody data-do-v0314-deadletters></tbody></table></div>
          </div>
          <div class="sc-do0314-card">
            <h4>Operator action</h4>
            <label>Queue ID<input data-do-v0314-queueid placeholder="dispatch-job-…"></label>
            <label>Reason<textarea rows="4" data-do-v0314-reason>Reviewed and corrected by the Lab operator.</textarea></label>
            <label><input type="checkbox" checked data-do-v0314-reset> Reset attempt counter on replay</label>
            <div class="sc-do0314-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-do-v0314-replay>Replay queue item</button><button type="button" class="sc-lab-button" data-do-v0314-cancel>Cancel queue item</button></div>
            <p><strong>Safety:</strong> replay and cancellation preserve operator actions and event history. Hard deletion is not exposed.</p>
          </div>
          <div class="sc-do0314-card is-wide"><h4>Operations health, diagnostics, and event timeline</h4><pre class="sc-do0314-output" data-do-v0314-output>No response yet.</pre></div>
        </div>
      </section>

      <section class="sc-lab-panel sc-at0313" data-lab-module="artifact-transport" data-module-panel="artifact-transport" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / DISTRIBUTED COMPUTE / v0.31.3</p><h3>Distributed Artifact, Result, and Checkpoint Transport</h3><p>Move governed inputs, large results, checkpoints, logs, datasets, and provenance records between the coordinator and secure workers with resumable chunks, SHA-256 verification, content-addressed storage, lease-bound access, and retention controls.</p></header>
        <p data-at-v0313-status role="status" aria-live="polite">Artifact transport loading…</p>
        <div class="sc-at0313-metrics" data-at-v0313-metrics></div>
        <div class="sc-at0313-grid">
          <div class="sc-at0313-card"><h4>Retained artifacts</h4><div class="sc-lab-table-wrap"><table><thead><tr><th>Artifact</th><th>Kind</th><th>Size</th><th>SHA-256</th><th>Owner</th><th>Created</th></tr></thead><tbody data-at-v0313-artifacts></tbody></table></div><div class="sc-lab-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-at-v0313-refresh>Refresh transport</button><button type="button" class="sc-lab-button" data-at-v0313-cleanup>Run retention cleanup</button></div></div>
          <div class="sc-at0313-card"><h4>Transport guarantees</h4><ul><li>Content is addressed and deduplicated by SHA-256.</li><li>Chunks are sequential, resumable, and independently verifiable.</li><li>Workers can download only artifacts granted by an active lease.</li><li>Large worker results are externalized from completion receipts.</li><li>Checkpoint and result artifacts retain queue, contract, project, and worker provenance.</li><li>Expired uploads and retained artifacts can be cleaned by policy.</li></ul></div>
        </div>
        <div class="sc-at0313-card"><h4>Coordinator transport health and sessions</h4><pre data-at-v0313-output>No response yet.</pre></div>
      </section>

      <section class="sc-lab-panel sc-wa0312" data-lab-module="worker-agent" data-module-panel="worker-agent" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / DISTRIBUTED COMPUTE / v0.31.3</p><h3>Secure Worker Agent Runtime</h3><p>Operate pull-based Python workers with one-time enrollment, worker-scoped credentials, local signed-contract verification, governed registered-method execution, automatic lease renewal, provenance-bearing completion receipts, and verified artifact transport.</p></header>
        <p data-wa-v0312-status role="status" aria-live="polite">Secure worker runtime loading…</p>
        <div class="sc-wa0312-metrics" data-wa-v0312-metrics></div>
        <div class="sc-wa0312-grid">
          <div class="sc-wa0312-card"><h4>Registered worker agents</h4><div class="sc-lab-table-wrap"><table><thead><tr><th>Worker</th><th>Type</th><th>State</th><th>Mode</th><th>Load</th><th>Agent</th></tr></thead><tbody data-wa-v0312-workers></tbody></table></div></div>
          <div class="sc-wa0312-card"><h4>Security model</h4><ul class="sc-wa0312-security"><li>Enrollment tokens remain on the coordinator and worker host.</li><li>Worker credentials are returned once and stored as coordinator-side SHA-256 digests.</li><li>Dispatch contracts are bound to a worker, signed, and locally verified before execution.</li><li>Only methods registered in the Python Compute Core can run.</li><li>Arbitrary source code, shell commands, callbacks, and executable payloads are rejected.</li></ul><div class="sc-wa0312-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-wa-v0312-refresh>Refresh security status</button></div></div>
        </div>
        <div class="sc-wa0312-card"><h4>Local or institutional worker startup</h4><p>Copy the worker environment example, add the coordinator URL and the two worker secrets on the worker host, validate the configuration, and start the agent.</p><pre data-wa-v0312-command aria-label="Worker startup command"></pre><div class="sc-wa0312-actions"><button type="button" class="sc-lab-button" data-wa-v0312-copy>Copy command</button><button type="button" class="sc-lab-button" data-wa-v0312-download>Download command</button></div></div>
        <div class="sc-wa0312-card"><h4>Coordinator worker-agent health</h4><pre data-wa-v0312-output>No response yet.</pre></div>
      </section>

      <section class="sc-lab-panel sc-dsp0310" data-lab-module="distributed-dispatcher" data-module-panel="distributed-dispatcher" hidden>
        <header class="sc-lab-module-header"><p class="sc-lab-kicker">PROJECT / DISTRIBUTED COMPUTE / v0.31.0</p><h3>Distributed Compute Dispatcher</h3><p>Register governed worker capabilities, route registered numerical workloads, issue signed leases, and preserve dispatch records without enabling arbitrary callbacks or arbitrary code.</p></header>
        <p data-dsp-v0310-status role="status" aria-live="polite">Compute dispatcher loading…</p>
        <div class="sc-dsp0310-metrics" data-dsp-v0310-metrics></div>
        <div class="sc-dsp0310-grid"><div class="sc-dsp0310-card"><h4>Worker profile</h4>
          <label>Worker ID<input data-dsp-v0310-worker-id value="browser-worker-1"></label><label>Name<input data-dsp-v0310-worker-name value="Browser analysis worker"></label>
          <label>Worker type<select data-dsp-v0310-worker-type><option value="browser-web-worker">Browser Web Worker</option><option value="render-cpu">Render CPU</option><option value="local-python">Local Python</option><option value="raspberry-pi">Raspberry Pi</option><option value="institutional-node">Institutional node</option></select></label>
          <label>Registered methods<input data-dsp-v0310-methods value="simulation.parameter_sweep,numerical.root.bracketed_polynomial"></label><label>Packages<input data-dsp-v0310-packages value="numpy,scipy"></label>
          <label>Memory MB<input type="number" min="128" value="1024" data-dsp-v0310-memory></label><label>Concurrent jobs<input type="number" min="1" value="1" data-dsp-v0310-concurrency></label>
          <label><input type="checkbox" data-dsp-v0310-checkpointing checked> Checkpoint capable</label><label>Tags<input data-dsp-v0310-tags value="trusted,cpu"></label>
          <div class="sc-dsp0310-actions"><button class="sc-lab-button sc-lab-button-primary" data-dsp-v0310-register>Register worker</button><button class="sc-lab-button" data-dsp-v0310-heartbeat>Send heartbeat</button><button class="sc-lab-button" data-dsp-v0310-refresh>Refresh registry</button></div>
        </div><div class="sc-dsp0310-card"><h4>Workload routing</h4>
          <label>Registered method<input data-dsp-v0310-workload-method value="simulation.parameter_sweep"></label><label>Target preference<input data-dsp-v0310-targets value="local-python,raspberry-pi,browser-web-worker"></label>
          <label>Required packages<input data-dsp-v0310-required-packages value="numpy"></label><label>Required tags<input data-dsp-v0310-required-tags value="trusted"></label>
          <label>Minimum memory MB<input type="number" min="128" value="512" data-dsp-v0310-min-memory></label><label>Priority<input type="number" min="0" max="100" value="70" data-dsp-v0310-priority></label>
          <label><input type="checkbox" data-dsp-v0310-require-checkpoint checked> Require checkpointing</label><label>Request JSON<textarea data-dsp-v0310-request>{"inputs":{"values":[1,2,3]}}</textarea></label>
          <div class="sc-dsp0310-actions"><button class="sc-lab-button" data-dsp-v0310-route>Route workload</button><button class="sc-lab-button sc-lab-button-primary" data-dsp-v0310-contract>Build signed contract</button><button class="sc-lab-button" data-dsp-v0310-verify>Verify contract</button><button class="sc-lab-button" data-dsp-v0310-export>Export record</button></div>
        </div></div>
        <div class="sc-dsp0310-card"><h4>Worker registry</h4><div class="sc-dsp0310-table-wrap"><table><thead><tr><th>Worker</th><th>Type</th><th>State</th><th>Load</th><th>Memory</th><th>Methods</th></tr></thead><tbody data-dsp-v0310-workers></tbody></table></div></div>
        <div class="sc-dsp0310-card"><h4>Routing and contract output</h4><pre data-dsp-v0310-output>Register a worker, route a workload, and issue a governed dispatch contract.</pre></div>
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
