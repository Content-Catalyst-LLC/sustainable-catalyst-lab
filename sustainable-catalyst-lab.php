<?php
/**
 * Plugin Name: Sustainable Catalyst Lab
 * Plugin URI: https://sustainablecatalyst.com/lab/
 * Description: Modular scientific workspace for natural science and engineering feeds, climate maps, chemistry, physics, biology, astronomy, materials, Earth systems, climate, ocean, marine science, energy, universal visualization and export, selectable-text PDF reports, Decision Studio handoff packets, portable method contracts, governed Python Compute Core, curated multi-language execution, workspace data management, experiments, evidence, notebooks, and data-connected documentation.
 * Version: 0.26.5
 * Update URI: https://sustainablecatalyst.com/lab/
 * Author: Content Catalyst LLC
 * License: GPL-2.0-or-later
 * Text Domain: sustainable-catalyst-lab
 */

if (!defined('ABSPATH')) { exit; }

define('SC_LAB_VERSION', '0.26.5');
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

require_once plugin_dir_path(__FILE__) . 'includes/class-sc-lab-python-compute-core-v0261.php';
SC_Lab_Python_Compute_Core_V0261::init();

register_activation_hook(__FILE__, array('SC_Lab_Plugin', 'activate'));
add_action('plugins_loaded', array('SC_Lab_Plugin', 'instance'));
