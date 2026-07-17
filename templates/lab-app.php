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
          'project-workspace' => 'Project architecture',
          'dataset-registry' => 'Dataset registry',
          'reproducible-runs' => 'Reproducible runs',
          'research-provenance' => 'Evidence & provenance',
          'method-review' => 'Method review',
          'scholarly-discovery' => 'Scholarly discovery',
          'experiment-framework' => 'Experiment framework',
          'design-studies' => 'Design studies',
          'model-calibration' => 'Model calibration',
          'workflow-orchestration' => 'Scientific workflows',
          'workflow-automation' => 'Scheduled & event-driven runs',
          'experiment-campaigns' => 'Adaptive experiment campaigns',
          'closed-loop-campaigns' => 'Closed-loop campaigns',
          'distributed-dispatcher' => 'Compute dispatcher',
          'persistent-queue' => 'Persistent queue',
          'dispatcher-operations' => 'Dispatcher operations',
          'worker-agent' => 'Secure worker agents',
          'artifact-transport' => 'Artifact transport',
          'activity' => 'Activity',
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
          'numerical-visualization' => 'Scientific Visualization',
          'long-running-jobs' => 'Long Jobs & Checkpoints',
          'chemistry' => 'Chemistry',
          'physics' => 'Physics laboratory',
          'biology' => 'Biology laboratory',
          'astronomy' => 'Astronomy calculations',
          'materials' => 'Materials laboratory',
          'earth-systems' => 'Earth systems laboratory',
          'energy-engineering' => 'Energy & engineering',
  'electrical-embedded' => 'Electrical & embedded',
  'mechanical-thermal' => 'Mechanical & thermal', 'civil-infrastructure' => 'Civil & infrastructure', 'architecture-building' => 'Architecture & building performance', 'urban-planning-spatial' => 'Urban planning & spatial systems', 'sustainable-cities-resilience' => 'Sustainable cities & urban resilience', 'comparative-economics-development-systems' => 'Comparative economics & development systems', 'aerospace-engineering-flight-systems' => 'Aerospace engineering & flight systems', 'rocket-propulsion-spaceflight' => 'Rocket propulsion & spaceflight', 'microbiology-laboratory' => 'Microbiology laboratory', 'biochemistry-molecular-analysis' => 'Biochemistry & molecular analysis', 'biotechnology-bioprocess-engineering' => 'Biotechnology & bioprocess engineering',
    'biomedical-engineering-biosignals' => 'Biomedical engineering & biosignals',
    'genetics-genomics-sequence-analysis' => 'Genetics, genomics & sequence analysis',
    'laboratory-data-instrumentation' => 'Laboratory data & instrumentation', 'circular-economy-industrial-ecology' => 'Circular economy & industrial ecology',
          'visualization-studio' => 'Visualization & export',
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
        'System' => array(
          'workspace-data' => 'Workspace data',
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
