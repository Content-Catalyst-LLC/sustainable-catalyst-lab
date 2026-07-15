<?php
/**
 * Sustainable Catalyst Lab v0.26.3.2 installation, version, and asset integrity layer.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Integrity_V02632 {
    const VERSION = '0.26.3.2';
    const MANIFEST_RELATIVE = 'build/sc-lab-release-manifest.json';
    const EXPECTED_BASENAME = 'sustainable-catalyst-lab/sustainable-catalyst-lab.php';
    private static $initialized = false;
    private static $assets = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('plugins_loaded', array(__CLASS__, 'record_identity'), 50);
        add_action('wp_enqueue_scripts', array(__CLASS__, 'maybe_enqueue'), 2);
        add_filter('script_loader_src', array(__CLASS__, 'version_asset_url'), PHP_INT_MAX, 2);
        add_filter('style_loader_src', array(__CLASS__, 'version_asset_url'), PHP_INT_MAX, 2);
        add_filter('do_shortcode_tag', array(__CLASS__, 'annotate_app'), PHP_INT_MAX, 4);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_action('admin_notices', array(__CLASS__, 'admin_notice'));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if (isset($_GET['sc_lab_module']) || isset($_GET['sc_lab_safe'])) { return true; }
        return $post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app');
    }

    private static function file_hash($relative) {
        $relative = ltrim((string) $relative, '/');
        $path = SC_LAB_DIR . $relative;
        return is_file($path) ? hash_file('sha256', $path) : null;
    }

    private static function asset_token($relative) {
        $hash = self::file_hash($relative);
        return self::VERSION . '.' . ($hash ? substr($hash, 0, 16) : 'missing');
    }

    private static function relative_from_asset_url($src) {
        $src = (string) $src;
        $base = trailingslashit((string) SC_LAB_URL);
        if (strpos($src, $base) !== 0) { return null; }
        $path = (string) parse_url($src, PHP_URL_PATH);
        $base_path = (string) parse_url($base, PHP_URL_PATH);
        if (!$path || strpos($path, $base_path) !== 0) { return null; }
        $relative = ltrim(substr($path, strlen($base_path)), '/');
        return preg_match('~^(assets|build)/[A-Za-z0-9_./-]+$~', $relative) ? $relative : null;
    }

    public static function version_asset_url($src, $handle) {
        unset($handle);
        $relative = self::relative_from_asset_url($src);
        if (!$relative) { return $src; }
        return add_query_arg('ver', rawurlencode(self::asset_token($relative)), remove_query_arg('ver', $src));
    }

    public static function maybe_enqueue() {
        if (!self::is_lab_request() || self::$assets) { return; }
        self::$assets = true;
        $script = 'assets/js/sc-lab-integrity-v02632.js';
        wp_enqueue_script('sc-lab-integrity-v02632', SC_LAB_URL . $script, array('sc-lab-runtime-v02631'), self::asset_token($script), true);
        wp_localize_script('sc-lab-integrity-v02632', 'SCLabIntegrityConfigV02632', array(
            'version' => self::VERSION,
            'pluginVersion' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'panelRuntimeVersion' => class_exists('SC_Lab_Runtime_Repair_V02631') ? SC_Lab_Runtime_Repair_V02631::VERSION : null,
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/runtime/health')),
            'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/runtime/v02632/manifest')),
            'expectedBasename' => self::EXPECTED_BASENAME,
        ));
    }

    public static function annotate_app($output, $tag, $attr, $match) {
        unset($attr, $match);
        if ($tag !== 'sc_lab_app' || is_admin()) { return $output; }
        $manifest = self::manifest();
        $summary = array(
            'releaseVersion' => self::VERSION,
            'pluginVersion' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'panelRuntimeVersion' => class_exists('SC_Lab_Runtime_Repair_V02631') ? SC_Lab_Runtime_Repair_V02631::VERSION : null,
            'buildFingerprint' => isset($manifest['buildFingerprint']) ? $manifest['buildFingerprint'] : null,
            'sourceCommit' => isset($manifest['sourceCommit']) ? $manifest['sourceCommit'] : null,
        );
        $json = wp_json_encode($summary, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        $json = str_replace('</', '<\\/', (string) $json);
        $output = preg_replace('/(<div\s+id=("|\')sc-lab-v02631-root\2\b)/i', '$1 data-sc-lab-release="' . esc_attr(self::VERSION) . '" data-sc-lab-integrity-version="' . esc_attr(self::VERSION) . '"', (string) $output, 1);
        $output = str_replace('Panel routing repair active', 'Lab integrity layer active', $output);
        return '<script type="application/json" data-sc-lab-release-summary>' . $json . '</script>' . $output;
    }

    private static function manifest_path() {
        return SC_LAB_DIR . self::MANIFEST_RELATIVE;
    }

    public static function manifest() {
        $path = self::manifest_path();
        if (!is_file($path)) { return array(); }
        $decoded = json_decode((string) file_get_contents($path), true);
        return is_array($decoded) ? $decoded : array();
    }

    private static function plugin_header_version($file) {
        if (!is_file($file)) { return null; }
        if (function_exists('get_file_data')) {
            $data = get_file_data($file, array('Version' => 'Version'), 'plugin');
            return isset($data['Version']) ? (string) $data['Version'] : null;
        }
        $head = (string) file_get_contents($file, false, null, 0, 8192);
        return preg_match('/^[ \t*#@]*Version:\s*(.+)$/mi', $head, $m) ? trim($m[1]) : null;
    }

    private static function plugin_candidates() {
        if (!defined('WP_PLUGIN_DIR') || !is_dir(WP_PLUGIN_DIR)) { return array(); }
        $active = (array) get_option('active_plugins', array());
        $network = function_exists('is_multisite') && is_multisite() ? array_keys((array) get_site_option('active_sitewide_plugins', array())) : array();
        $records = array();
        foreach ((array) glob(WP_PLUGIN_DIR . '/*/sustainable-catalyst-lab.php') as $file) {
            $basename = str_replace(trailingslashit(WP_PLUGIN_DIR), '', $file);
            $records[] = array(
                'basename' => $basename,
                'folder' => basename(dirname($file)),
                'version' => self::plugin_header_version($file),
                'active' => in_array($basename, $active, true) || in_array($basename, $network, true),
                'current' => defined('SC_LAB_FILE') && realpath($file) === realpath(SC_LAB_FILE),
                'sha256' => hash_file('sha256', $file),
            );
        }
        usort($records, function($a, $b) { return strcmp($a['basename'], $b['basename']); });
        return $records;
    }

    private static function template_modules() {
        $path = SC_LAB_DIR . 'templates/lab-app.php';
        if (!is_file($path)) { return array(); }
        $text = (string) file_get_contents($path);
        preg_match_all('/data-lab-module=("|\')([^"\']+)\1/i', $text, $matches);
        $modules = array_values(array_unique(array_map('sanitize_key', isset($matches[2]) ? $matches[2] : array())));
        sort($modules);
        return $modules;
    }

    private static function route_checks() {
        $modules = self::template_modules();
        $aliases = class_exists('SC_Lab_Runtime_Repair_V02631') ? SC_Lab_Runtime_Repair_V02631::alias_map() : array();
        $checks = array();
        foreach (array('marine' => 'marine-biology', 'climate' => 'climate-maps', 'evidence' => 'evidence-decisions') as $alias => $canonical) {
            $resolved = isset($aliases[$alias]) ? sanitize_key((string) $aliases[$alias]) : $alias;
            $checks[$alias] = array(
                'expected' => $canonical,
                'resolved' => $resolved,
                'canonicalPanelPresent' => in_array($canonical, $modules, true),
                'ok' => $resolved === $canonical && in_array($canonical, $modules, true),
            );
        }
        return $checks;
    }

    private static function verify_manifest() {
        $manifest = self::manifest();
        $results = array();
        foreach ((array) (isset($manifest['criticalFiles']) ? $manifest['criticalFiles'] : array()) as $relative => $expected) {
            $actual = self::file_hash($relative);
            $results[$relative] = array('expected' => $expected, 'actual' => $actual, 'ok' => is_string($expected) && hash_equals($expected, (string) $actual));
        }
        $ok = !empty($results);
        foreach ($results as $record) { if (empty($record['ok'])) { $ok = false; break; } }
        return array('present' => !empty($manifest), 'ok' => $ok, 'files' => $results);
    }

    private static function identity() {
        $actual_basename = defined('SC_LAB_PLUGIN_BASENAME') ? SC_LAB_PLUGIN_BASENAME : (defined('SC_LAB_FILE') ? plugin_basename(SC_LAB_FILE) : null);
        $actual_folder = defined('SC_LAB_DIR') ? basename(rtrim(SC_LAB_DIR, '/\\')) : null;
        $bootstrap = defined('SC_LAB_FILE') ? realpath(SC_LAB_FILE) : null;
        return array(
            'expectedBasename' => self::EXPECTED_BASENAME,
            'actualBasename' => $actual_basename,
            'basenameMatches' => $actual_basename === self::EXPECTED_BASENAME,
            'expectedFolder' => 'sustainable-catalyst-lab',
            'actualFolder' => $actual_folder,
            'folderMatches' => $actual_folder === 'sustainable-catalyst-lab',
            'bootstrap' => $bootstrap,
            'bootstrapExists' => $bootstrap && is_file($bootstrap),
        );
    }

    private static function release_state() {
        $manifest = self::manifest();
        $identity = self::identity();
        $verification = self::verify_manifest();
        $candidates = self::plugin_candidates();
        $versions = array(
            'release' => self::VERSION,
            'pluginConstant' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'pluginHeader' => defined('SC_LAB_FILE') ? self::plugin_header_version(SC_LAB_FILE) : null,
            'panelRuntime' => class_exists('SC_Lab_Runtime_Repair_V02631') ? SC_Lab_Runtime_Repair_V02631::VERSION : null,
            'computeCore' => class_exists('SC_Lab_Python_Compute_Core_V0260') ? SC_Lab_Python_Compute_Core_V0260::VERSION : null,
            'queueCore' => class_exists('SC_Lab_Python_Compute_Core_V0261') ? SC_Lab_Python_Compute_Core_V0261::VERSION : null,
            'manifestRelease' => isset($manifest['releaseVersion']) ? $manifest['releaseVersion'] : null,
        );
        $version_consistent = $versions['release'] === $versions['pluginConstant'] && $versions['release'] === $versions['pluginHeader'] && $versions['release'] === $versions['manifestRelease'];
        $duplicate_risk = count($candidates) > 1;
        $partial = !$version_consistent || empty($verification['ok']) || empty($identity['basenameMatches']) || empty($identity['folderMatches']);
        return array(
            'ok' => !$partial && !$duplicate_risk,
            'state' => $partial ? 'partial-or-mismatched' : ($duplicate_risk ? 'duplicate-plugin-risk' : 'verified'),
            'partialInstallRisk' => $partial,
            'duplicatePluginRisk' => $duplicate_risk,
            'versions' => $versions,
            'identity' => $identity,
            'manifest' => array(
                'sourceCommit' => isset($manifest['sourceCommit']) ? $manifest['sourceCommit'] : null,
                'buildFingerprint' => isset($manifest['buildFingerprint']) ? $manifest['buildFingerprint'] : null,
                'generatedAt' => isset($manifest['generatedAt']) ? $manifest['generatedAt'] : null,
                'verification' => $verification,
            ),
            'pluginCandidates' => $candidates,
            'routeChecks' => self::route_checks(),
            'assetStrategy' => 'content-sha256-query-versioning',
            'rollback' => array(
                'method' => 'Restore the timestamped safety ZIP created by the installer, or upload the previous verified WordPress plugin ZIP.',
                'preserve' => array('wp-content/uploads', 'sc_lab_settings', 'Python Compute Core database and environment variables'),
                'neverDeleteRepositoryBeforeBackup' => true,
            ),
        );
    }

    public static function record_identity() {
        if (!defined('SC_LAB_VERSION')) { return; }
        update_option('sc_lab_plugin_identity', array(
            'slug' => defined('SC_LAB_PLUGIN_SLUG') ? SC_LAB_PLUGIN_SLUG : 'sustainable-catalyst-lab',
            'basename' => defined('SC_LAB_PLUGIN_BASENAME') ? SC_LAB_PLUGIN_BASENAME : null,
            'folder' => defined('SC_LAB_DIR') ? basename(rtrim(SC_LAB_DIR, '/\\')) : null,
            'version' => SC_LAB_VERSION,
            'integrityVersion' => self::VERSION,
            'recordedAt' => gmdate('c'),
        ), false);
    }

    public static function routes() {
        $definition = array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        );
        register_rest_route('sc-lab/v1', '/runtime/health', $definition);
        register_rest_route('sc-lab/v1', '/runtime/v02632/health', $definition);
        register_rest_route('sc-lab/v1', '/runtime/v02632/manifest', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'manifest_response'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function health() {
        return rest_ensure_response(self::release_state());
    }

    public static function manifest_response() {
        $manifest = self::manifest();
        return rest_ensure_response(array(
            'ok' => !empty($manifest),
            'releaseVersion' => self::VERSION,
            'manifest' => $manifest,
            'verification' => self::verify_manifest(),
        ));
    }

    public static function admin_notice() {
        if (!current_user_can('activate_plugins')) { return; }
        $state = self::release_state();
        if (!empty($state['ok'])) { return; }
        $issues = array();
        if (!empty($state['partialInstallRisk'])) { $issues[] = 'release files or version markers do not match'; }
        if (!empty($state['duplicatePluginRisk'])) { $issues[] = 'more than one Sustainable Catalyst Lab plugin folder exists'; }
        echo '<div class="notice notice-error"><p><strong>Sustainable Catalyst Lab integrity warning:</strong> ' . esc_html(implode('; ', $issues)) . '. Check <code>/wp-json/sc-lab/v1/runtime/health</code> before continuing upgrades.</p></div>';
    }
}
