<?php
/**
 * Plugin Name: Sustainable Catalyst Lab
 * Plugin URI: https://sustainablecatalyst.com/lab/
 * Description: Modular scientific workspace for natural science and engineering feeds, climate maps, chemistry, physics, biology, astronomy, materials, energy, experiments, evidence, notebooks, and data-connected documentation.
 * Version: 0.2.0
 * Author: Content Catalyst LLC
 * License: GPL-2.0-or-later
 * Text Domain: sustainable-catalyst-lab
 */

if (!defined('ABSPATH')) { exit; }

define('SC_LAB_VERSION', '0.2.0');
define('SC_LAB_FILE', __FILE__);
define('SC_LAB_DIR', plugin_dir_path(__FILE__));
define('SC_LAB_URL', plugin_dir_url(__FILE__));

require_once SC_LAB_DIR . 'includes/class-sc-lab-feeds.php';
require_once SC_LAB_DIR . 'includes/class-sc-lab-rest.php';
require_once SC_LAB_DIR . 'includes/class-sc-lab-admin.php';
require_once SC_LAB_DIR . 'includes/class-sc-lab-plugin.php';

register_activation_hook(__FILE__, array('SC_Lab_Plugin', 'activate'));
add_action('plugins_loaded', array('SC_Lab_Plugin', 'instance'));
