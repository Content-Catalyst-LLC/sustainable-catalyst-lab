<?php
/**
 * Plugin Name: Sustainable Catalyst Lab
 * Plugin URI: https://sustainablecatalyst.com/lab/
 * Description: Modular scientific workspace for natural science and engineering feeds, climate maps, chemistry, physics, biology, astronomy, materials, Earth systems, climate, ocean, marine science, energy, universal visualization and export, selectable-text PDF reports, Decision Studio handoff packets, portable method contracts, governed Python Compute Core, scientific computing, numerical methods, numerical validation and benchmark libraries, precision and solver governance, accessible scientific visualization, checkpointed long-running jobs, result caching, curated multi-language execution, workspace data management, production recovery, incident diagnostics, experiments, evidence, notebooks, scientific workflow orchestration, dependency graphs, declarative workflow conditions, checkpoint history, partial recovery, durable schedules, authenticated event triggers, missed-run recovery, concurrency controls, adaptive experiment campaigns, sequential design, Gaussian-process surrogate modeling, Bayesian optimization, active learning, predictive uncertainty, resource-aware trial search, budget-aware orchestration, closed-loop simulation and instrument campaigns, signed measurement ingestion, safety interlocks, operator-approved setpoints, shared research projects, role-governed team workspaces, single-use invitations, collaboration-safe resource linking, append-only review discussions, review assignments, approval gates, immutable scientific sign-off, and data-connected documentation.
 * Version: 0.35.1
 * Update URI: https://sustainablecatalyst.com/lab/
 * Author: Content Catalyst LLC
 * License: GPL-2.0-or-later
 * Text Domain: sustainable-catalyst-lab
 */

if (!defined('ABSPATH')) { exit; }

define('SC_LAB_VERSION', '0.35.1');
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-architecture-building.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-architecture-building-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-urban-planning-spatial.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-urban-planning-spatial-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-sustainable-cities-resilience.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-sustainable-cities-resilience-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-comparative-economics-development-systems.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-comparative-economics-development-systems-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-aerospace-engineering-flight-systems.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-aerospace-engineering-flight-systems-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-rocket-propulsion-spaceflight.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-rocket-propulsion-spaceflight-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-microbiology-laboratory.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-microbiology-laboratory-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-circular-economy-industrial-ecology.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-circular-economy-industrial-ecology-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-civil-infrastructure-interface-repair.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-engineering-interface-repair-v0200.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-civil-runtime-v0200.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-civil-panel-router-v0200.php';
define('SC_LAB_FILE', __FILE__);
define('SC_LAB_PLUGIN_BASENAME', plugin_basename(__FILE__));
define('SC_LAB_PLUGIN_SLUG', 'sustainable-catalyst-lab');
define('SC_LAB_DIR', plugin_dir_path(__FILE__));
define('SC_LAB_URL', plugin_dir_url(__FILE__));

require_once SC_LAB_DIR . 'includes/class-sc-lab-feeds.php';
require_once SC_LAB_DIR . 'includes/class-sc-lab-rest.php';
require_once SC_LAB_DIR . 'includes/class-sc-lab-admin.php';
require_once SC_LAB_DIR . 'includes/class-sc-lab-plugin.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biochemistry-molecular-analysis.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biochemistry-molecular-analysis-rest.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biochemistry-production-v0211.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biochemistry-batch-rest-v0212.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-molecular-validation-rest-v0213.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biotechnology-bioprocess-rest-v0220.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-bioprocess-production-v0221.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-bioprocess-monitoring-control-v0222.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-bioprocess-monitoring-rest-v0222.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-bioprocess-validation-provenance-v0223.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-bioprocess-validation-rest-v0223.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biomedical-engineering-biosignals-v0230.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biomedical-biosignals-rest-v0230.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biosignal-production-v0231.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biosignal-visualization-comparison-v0232.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biosignal-visualization-rest-v0232.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-genetics-genomics-v0240.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-genetics-genomics-rest-v0240.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-genomics-production-v0241.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-genomic-visualization-v0242.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-genomic-visualization-rest-v0242.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-genomic-validation-v0243.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-genomic-validation-rest-v0243.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-laboratory-data-instrumentation-v0250.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-laboratory-instrumentation-rest-v0250.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-instrumentation-production-v0251.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-instrumentation-live-visualization-v0252.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-instrumentation-live-rest-v0252.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-instrumentation-validation-custody-v0253.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-instrumentation-validation-rest-v0253.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biotechnology-bioprocess-engineering-v0220.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-molecular-validation-provenance-v0213.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-biochemistry-visualization-batch-v0212.php';

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-runtime-repair-v02631.php';
SC_Lab_Runtime_Repair_V02631::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-integrity-v02632.php';
SC_Lab_Integrity_V02632::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-observe-domain-v02633.php';
// v0.26.3.4 supersedes the v0.26.3.3 feed-panel mount while retaining its climate and compatibility code.
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-observe-feeds-v02634.php';
SC_Lab_Observe_Domain_V02633::init();
SC_Lab_Observe_Feeds_V02634::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-functional-validation-v0264.php';
SC_Lab_Functional_Validation_V0264::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-interface-reliability-v0265.php';
SC_Lab_Interface_Reliability_V0265::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-production-stability-v0266.php';
SC_Lab_Production_Stability_V0266::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-numerical-methods-v0270.php';
SC_Lab_Numerical_Methods_V0270::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-numerical-validation-v0271.php';
SC_Lab_Numerical_Validation_V0271::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-long-jobs-v0272.php';
SC_Lab_Long_Jobs_V0272::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-numerical-governance-v0273.php';
SC_Lab_Numerical_Governance_V0273::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-numerical-visualization-v0274.php';
SC_Lab_Numerical_Visualization_V0274::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-project-workspace-v0280.php';
SC_Lab_Project_Workspace_V0280::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-dataset-registry-v0281.php';
SC_Lab_Dataset_Registry_V0281::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-reproducible-runs-v0282.php';
SC_Lab_Reproducible_Runs_V0282::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-research-provenance-v0290.php';
SC_Lab_Research_Provenance_V0290::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-research-quality-v0291.php';
SC_Lab_Research_Quality_V0291::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-external-discovery-v0292.php';
SC_Lab_External_Discovery_V0292::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-experiment-framework-v0300.php';
SC_Lab_Experiment_Framework_V0300::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-design-studies-v0301.php';
SC_Lab_Design_Studies_V0301::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-model-calibration-v0302.php';
SC_Lab_Model_Calibration_V0302::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-distributed-dispatcher-v0310.php';
SC_Lab_Distributed_Dispatcher_V0310::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-persistent-queue-v0311.php';
SC_Lab_Persistent_Queue_V0311::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-worker-agent-v0312.php';
SC_Lab_Worker_Agent_V0312::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-artifact-transport-v0313.php';
SC_Lab_Artifact_Transport_V0313::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-dispatcher-operations-v0314.php';
SC_Lab_Dispatcher_Operations_V0314::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-workflow-orchestration-v0320.php';
SC_Lab_Workflow_Orchestration_V0320::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-workflow-automation-v0322.php';
SC_Lab_Workflow_Automation_V0322::init();

// v0.33.1 Bayesian Optimization, Active Learning, and Resource-Aware Search.
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-experiment-campaigns-v0331.php';
SC_Lab_Experiment_Campaigns_V0331::init();

// v0.33.2 Closed-Loop Simulation and Instrument Campaigns.
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-closed-loop-campaigns-v0332.php';
SC_Lab_Closed_Loop_Campaigns_V0332::init();

// v0.34.0 Scientific Model Registry and Environment Reproduction.
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-model-registry-v0340.php';
SC_Lab_Model_Registry_V0340::init();

// v0.34.1 Ensemble Simulation, Global Sensitivity, and Uncertainty.
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-ensemble-uncertainty-v0341.php';
SC_Lab_Ensemble_Uncertainty_V0341::init();

// v0.34.2 Surrogate Models and Reduced-Order Analysis.
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-surrogate-reduced-order-v0342.php';
SC_Lab_Surrogate_Reduced_Order_V0342::init();

// v0.35.0 Shared Research Projects and Team Workspaces.
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-team-workspaces-v0350.php';
SC_Lab_Team_Workspaces_V0350::init();

// v0.35.1 Review, Comments, Approvals, and Scientific Sign-Off.
require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-workspace-review-v0351.php';
SC_Lab_Workspace_Review_V0351::init();

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-python-compute-core-v0261.php';
SC_Lab_Python_Compute_Core_V0261::init();

register_activation_hook(__FILE__, array('SC_Lab_Plugin', 'activate'));
add_action('plugins_loaded', array('SC_Lab_Plugin', 'instance'));
