<?php
if (!defined('ABSPATH')) { exit; }

class SC_Lab_Admin {
    public static function defaults() {
        return array(
            'workbench_url' => home_url('/lab/workbench/'),
            'decision_studio_url' => home_url('/lab/decision-studio/'),
            'site_intelligence_url' => home_url('/lab/site-intelligence/'),
            'cache_minutes' => 30,
            'enable_feeds' => 1,
            'enable_climate_maps' => 1,
            'ncbi_tool' => 'sustainable_catalyst_lab',
            'ncbi_email' => get_option('admin_email'),
            'enable_remote_compute' => 0,
            'compute_backend_url' => '',
            'compute_api_key' => '',
            'compute_client_id' => 'sustainable-catalyst-wordpress',
            'compute_signing_secret' => '',
            'compute_timeout_seconds' => 20,
            'compute_job_timeout_seconds' => 120,
            'compute_job_max_attempts' => 2,
            'compute_job_poll_ms' => 1200,
            'compute_verify_ssl' => 1,
        );
    }

    public function __construct() {
        add_action('admin_menu', array($this, 'menu'));
        add_action('admin_init', array($this, 'register'));
        add_action('admin_notices', array($this, 'duplicate_notice'));
        add_action('admin_post_sc_lab_deactivate_duplicates', array($this, 'deactivate_duplicates'));
    }

    public static function duplicate_plugins() {
        if (!function_exists('get_plugins')) { require_once ABSPATH . 'wp-admin/includes/plugin.php'; }
        $current = defined('SC_LAB_PLUGIN_BASENAME') ? SC_LAB_PLUGIN_BASENAME : plugin_basename(SC_LAB_FILE);
        $duplicates = array();
        foreach ((array) get_plugins() as $path => $data) {
            if ($path === $current) { continue; }
            $name = isset($data['Name']) ? (string) $data['Name'] : '';
            $domain = isset($data['TextDomain']) ? (string) $data['TextDomain'] : '';
            if ($name === 'Sustainable Catalyst Lab' || $domain === 'sustainable-catalyst-lab') { $duplicates[$path] = $data; }
        }
        return $duplicates;
    }

    public function duplicate_notice() {
        if (!current_user_can('activate_plugins')) { return; }
        $duplicates = self::duplicate_plugins();
        if (!$duplicates) { return; }
        $settings_url = admin_url('options-general.php?page=sc-lab-settings#sc-lab-installation-identity');
        echo '<div class="notice notice-warning"><p><strong>Sustainable Catalyst Lab detected duplicate installations.</strong> WordPress identifies a plugin by its folder and bootstrap filename. Keep <code>sustainable-catalyst-lab/sustainable-catalyst-lab.php</code> and deactivate the versioned copies.</p><p><a class="button button-primary" href="' . esc_url($settings_url) . '">Review duplicate Lab plugins</a></p></div>';
    }

    public function deactivate_duplicates() {
        if (!current_user_can('activate_plugins')) { wp_die(esc_html__('You are not allowed to manage plugins.', 'sustainable-catalyst-lab')); }
        check_admin_referer('sc_lab_deactivate_duplicates');
        $duplicates = array_keys(self::duplicate_plugins());
        if ($duplicates) { deactivate_plugins($duplicates, true); }
        $url = add_query_arg(array('page'=>'sc-lab-settings','sc_lab_duplicates_deactivated'=>count($duplicates)), admin_url('options-general.php'));
        wp_safe_redirect($url . '#sc-lab-installation-identity');
        exit;
    }

    public function menu() { add_options_page('Sustainable Catalyst Lab', 'Sustainable Catalyst Lab', 'manage_options', 'sc-lab-settings', array($this, 'page')); }
    public function register() { register_setting('sc_lab_settings_group', 'sc_lab_settings', array($this, 'sanitize')); }

    public function sanitize($input) {
        $defaults = self::defaults();
        $backend = esc_url_raw(isset($input['compute_backend_url']) ? $input['compute_backend_url'] : $defaults['compute_backend_url']);
        return array(
            'workbench_url' => esc_url_raw(isset($input['workbench_url']) ? $input['workbench_url'] : $defaults['workbench_url']),
            'decision_studio_url' => esc_url_raw(isset($input['decision_studio_url']) ? $input['decision_studio_url'] : $defaults['decision_studio_url']),
            'site_intelligence_url' => esc_url_raw(isset($input['site_intelligence_url']) ? $input['site_intelligence_url'] : $defaults['site_intelligence_url']),
            'cache_minutes' => max(5, min(1440, absint(isset($input['cache_minutes']) ? $input['cache_minutes'] : 30))),
            'enable_feeds' => empty($input['enable_feeds']) ? 0 : 1,
            'enable_climate_maps' => empty($input['enable_climate_maps']) ? 0 : 1,
            'ncbi_tool' => sanitize_key(isset($input['ncbi_tool']) ? $input['ncbi_tool'] : $defaults['ncbi_tool']),
            'ncbi_email' => sanitize_email(isset($input['ncbi_email']) ? $input['ncbi_email'] : $defaults['ncbi_email']),
            'enable_remote_compute' => empty($input['enable_remote_compute']) ? 0 : 1,
            'compute_backend_url' => untrailingslashit($backend),
            'compute_api_key' => substr(preg_replace('/[\x00-\x1F\x7F]/', '', (string) wp_unslash(isset($input['compute_api_key']) ? $input['compute_api_key'] : $defaults['compute_api_key'])), 0, 512),
            'compute_client_id' => sanitize_key(isset($input['compute_client_id']) ? $input['compute_client_id'] : $defaults['compute_client_id']),
            'compute_signing_secret' => substr(preg_replace('/[\x00-\x1F\x7F]/', '', (string) wp_unslash(isset($input['compute_signing_secret']) ? $input['compute_signing_secret'] : $defaults['compute_signing_secret'])), 0, 512),
            'compute_timeout_seconds' => max(5, min(60, absint(isset($input['compute_timeout_seconds']) ? $input['compute_timeout_seconds'] : 20))),
            'compute_job_timeout_seconds' => max(5, min(900, absint(isset($input['compute_job_timeout_seconds']) ? $input['compute_job_timeout_seconds'] : 120))),
            'compute_job_max_attempts' => max(1, min(5, absint(isset($input['compute_job_max_attempts']) ? $input['compute_job_max_attempts'] : 2))),
            'compute_job_poll_ms' => max(500, min(10000, absint(isset($input['compute_job_poll_ms']) ? $input['compute_job_poll_ms'] : 1200))),
            'compute_verify_ssl' => empty($input['compute_verify_ssl']) ? 0 : 1,
        );
    }

    public function page() {
        if (!current_user_can('manage_options')) { return; }
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), self::defaults());
        ?>
        <div class="wrap"><h1>Sustainable Catalyst Lab</h1>
        <p>Configure the modular science workspace, PDF reporting and Decision Studio routes, source caching, application routes, and the governed Python Compute Core.</p>
        <form method="post" action="options.php"><?php settings_fields('sc_lab_settings_group'); ?>
        <h2>Application routes and scientific sources</h2>
        <table class="form-table" role="presentation">
        <?php foreach (array('workbench_url'=>'Workbench route','decision_studio_url'=>'Decision Studio route','site_intelligence_url'=>'Site Intelligence route') as $key=>$label): ?>
        <tr><th scope="row"><label for="<?php echo esc_attr($key); ?>"><?php echo esc_html($label); ?></label></th><td><input class="regular-text" type="url" id="<?php echo esc_attr($key); ?>" name="sc_lab_settings[<?php echo esc_attr($key); ?>]" value="<?php echo esc_attr($settings[$key]); ?>"></td></tr>
        <?php endforeach; ?>
        <tr><th scope="row"><label for="cache_minutes">Feed cache</label></th><td><input type="number" min="5" max="1440" id="cache_minutes" name="sc_lab_settings[cache_minutes]" value="<?php echo esc_attr($settings['cache_minutes']); ?>"> minutes</td></tr>
        <tr><th scope="row">Modules</th><td><label><input type="checkbox" name="sc_lab_settings[enable_feeds]" value="1" <?php checked($settings['enable_feeds'], 1); ?>> Scientific feeds</label><br><label><input type="checkbox" name="sc_lab_settings[enable_climate_maps]" value="1" <?php checked($settings['enable_climate_maps'], 1); ?>> Climate maps</label></td></tr>
        <tr><th scope="row"><label for="ncbi_tool">NCBI tool name</label></th><td><input class="regular-text" id="ncbi_tool" name="sc_lab_settings[ncbi_tool]" value="<?php echo esc_attr($settings['ncbi_tool']); ?>"></td></tr>
        <tr><th scope="row"><label for="ncbi_email">NCBI contact email</label></th><td><input class="regular-text" type="email" id="ncbi_email" name="sc_lab_settings[ncbi_email]" value="<?php echo esc_attr($settings['ncbi_email']); ?>"></td></tr>
        </table>

        <h2 id="sc-lab-compute-settings">Python Compute Core</h2>
        <p>WordPress is the control-plane gateway for the FastAPI compute service. Browser requests remain same-origin; backend credentials and the HMAC signing secret are never localized into JavaScript.</p>
        <table class="form-table" role="presentation">
          <tr><th scope="row">Remote execution</th><td><label><input type="checkbox" name="sc_lab_settings[enable_remote_compute]" value="1" <?php checked($settings['enable_remote_compute'], 1); ?>> Enable the governed Python Compute Core</label></td></tr>
          <tr><th scope="row"><label for="compute_backend_url">Compute API URL</label></th><td><input class="regular-text" type="url" id="compute_backend_url" name="sc_lab_settings[compute_backend_url]" value="<?php echo esc_attr($settings['compute_backend_url']); ?>" placeholder="https://sustainable-catalyst-lab-compute-api.onrender.com"><p class="description">Enter the service origin only, without <code>/v1</code>.</p></td></tr>
          <tr><th scope="row"><label for="compute_api_key">Compute API key</label></th><td><input class="regular-text" type="password" autocomplete="new-password" id="compute_api_key" name="sc_lab_settings[compute_api_key]" value="<?php echo esc_attr($settings['compute_api_key']); ?>"><p class="description">Legacy migration key matching <code>SC_LAB_COMPUTE_API_KEY</code>. HMAC signing below is preferred.</p></td></tr>
          <tr><th scope="row"><label for="compute_client_id">Compute client ID</label></th><td><input class="regular-text" id="compute_client_id" name="sc_lab_settings[compute_client_id]" value="<?php echo esc_attr($settings['compute_client_id']); ?>"><p class="description">Identifies this WordPress control plane in compute provenance.</p></td></tr>
          <tr><th scope="row"><label for="compute_signing_secret">HMAC signing secret</label></th><td><input class="regular-text" type="password" autocomplete="new-password" id="compute_signing_secret" name="sc_lab_settings[compute_signing_secret]" value="<?php echo esc_attr($settings['compute_signing_secret']); ?>"><p class="description">Use the same <code>SC_LAB_COMPUTE_SIGNING_SECRET</code> configured on the Python backend.</p></td></tr>
          <tr><th scope="row"><label for="compute_timeout_seconds">Proxy timeout</label></th><td><input type="number" min="5" max="60" id="compute_timeout_seconds" name="sc_lab_settings[compute_timeout_seconds]" value="<?php echo esc_attr($settings['compute_timeout_seconds']); ?>"> seconds</td></tr>
          <tr><th scope="row"><label for="compute_job_timeout_seconds">Default job timeout</label></th><td><input type="number" min="5" max="900" id="compute_job_timeout_seconds" name="sc_lab_settings[compute_job_timeout_seconds]" value="<?php echo esc_attr($settings['compute_job_timeout_seconds']); ?>"> seconds<p class="description">The isolated Python worker is terminated when this limit is exceeded.</p></td></tr>
          <tr><th scope="row"><label for="compute_job_max_attempts">Default job attempts</label></th><td><input type="number" min="1" max="5" id="compute_job_max_attempts" name="sc_lab_settings[compute_job_max_attempts]" value="<?php echo esc_attr($settings['compute_job_max_attempts']); ?>"><p class="description">Retryable worker failures use exponential backoff up to this attempt count.</p></td></tr>
          <tr><th scope="row"><label for="compute_job_poll_ms">Job polling interval</label></th><td><input type="number" min="500" max="10000" step="100" id="compute_job_poll_ms" name="sc_lab_settings[compute_job_poll_ms]" value="<?php echo esc_attr($settings['compute_job_poll_ms']); ?>"> milliseconds</td></tr>
          <tr><th scope="row">TLS verification</th><td><label><input type="checkbox" name="sc_lab_settings[compute_verify_ssl]" value="1" <?php checked($settings['compute_verify_ssl'], 1); ?>> Verify the Render service certificate</label></td></tr>
        </table>
        <?php submit_button(); ?></form>
        <hr>
        <section id="sc-lab-compute-queue-monitor">
          <h2>Compute queue monitor</h2>
          <p>The queue is stored in SQLite using WAL mode. Running jobs execute in isolated child processes so cancellation and time limits can terminate the worker without taking down the API.</p>
          <?php
          $queue_response = class_exists('SC_Lab_Python_Compute_Core_V0261') ? SC_Lab_Python_Compute_Core_V0261::queue_status() : new WP_Error('queue_monitor_unavailable','The v0.26.1 compute queue gateway is unavailable.');
          $worker_response = class_exists('SC_Lab_Python_Compute_Core_V0261') ? SC_Lab_Python_Compute_Core_V0261::workers() : new WP_Error('worker_monitor_unavailable','The v0.26.1 worker gateway is unavailable.');
          $queue_data = $queue_response instanceof WP_REST_Response ? $queue_response->get_data() : null;
          $worker_data = $worker_response instanceof WP_REST_Response ? $worker_response->get_data() : null;
          ?>
          <?php if (is_array($queue_data) && isset($queue_data['counts'])): ?>
            <table class="widefat striped" style="max-width:960px"><tbody>
              <tr><th>Storage</th><td><?php echo esc_html(isset($queue_data['storage']) ? $queue_data['storage'] : 'unknown'); ?></td></tr>
              <tr><th>Worker capacity</th><td><?php echo esc_html(isset($queue_data['workerCapacity']) ? $queue_data['workerCapacity'] : 0); ?></td></tr>
              <tr><th>Active workers</th><td><?php echo esc_html(isset($queue_data['activeWorkers']) ? $queue_data['activeWorkers'] : 0); ?></td></tr>
              <tr><th>Queued / retrying</th><td><?php echo esc_html((int)($queue_data['counts']['queued'] ?? 0) + (int)($queue_data['counts']['retrying'] ?? 0)); ?></td></tr>
              <tr><th>Completed</th><td><?php echo esc_html((int)($queue_data['counts']['completed'] ?? 0)); ?></td></tr>
              <tr><th>Failed / timed out</th><td><?php echo esc_html((int)($queue_data['counts']['failed'] ?? 0) + (int)($queue_data['counts']['timed_out'] ?? 0)); ?></td></tr>
              <tr><th>Worker health</th><td><?php echo esc_html(is_array($worker_data) && !empty($worker_data['healthy']) ? 'Healthy' : 'Unavailable or degraded'); ?></td></tr>
            </tbody></table>
          <?php else: ?>
            <div class="notice notice-info inline"><p><?php echo esc_html(is_wp_error($queue_response) ? $queue_response->get_error_message() : 'The Python Compute Core queue is not currently reachable. Save the backend settings and reload this page.'); ?></p></div>
          <?php endif; ?>
        </section>
        <hr>
        <section id="sc-lab-installation-identity">
          <h2>Plugin installation identity</h2>
          <p>Updates must use the stable archive <code>sustainable-catalyst-lab.zip</code>, containing the folder <code>sustainable-catalyst-lab/</code> and bootstrap file <code>sustainable-catalyst-lab.php</code>. Uploading the repository ZIP or a versioned folder creates a separate WordPress plugin instance.</p>
          <table class="widefat striped" style="max-width:960px"><tbody>
            <tr><th>Current plugin basename</th><td><code><?php echo esc_html(SC_LAB_PLUGIN_BASENAME); ?></code></td></tr>
            <tr><th>Stable plugin slug</th><td><code><?php echo esc_html(SC_LAB_PLUGIN_SLUG); ?></code></td></tr>
            <tr><th>Current version</th><td><code><?php echo esc_html(SC_LAB_VERSION); ?></code></td></tr>
          </tbody></table>
          <?php $duplicates = self::duplicate_plugins(); ?>
          <?php if ($duplicates): ?>
            <h3>Duplicate installations detected</h3>
            <table class="widefat striped" style="max-width:960px"><thead><tr><th>Plugin path</th><th>Version</th><th>Status</th></tr></thead><tbody>
            <?php foreach ($duplicates as $path => $data): ?><tr><td><code><?php echo esc_html($path); ?></code></td><td><?php echo esc_html(isset($data['Version']) ? $data['Version'] : 'unknown'); ?></td><td><?php echo is_plugin_active($path) ? 'Active' : 'Inactive'; ?></td></tr><?php endforeach; ?>
            </tbody></table>
            <p>This action deactivates duplicate instances but does not delete their folders or project data.</p>
            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
              <input type="hidden" name="action" value="sc_lab_deactivate_duplicates">
              <?php wp_nonce_field('sc_lab_deactivate_duplicates'); ?>
              <?php submit_button('Deactivate duplicate Lab instances', 'secondary', 'submit', false); ?>
            </form>
          <?php else: ?><p><strong>No duplicate Lab installations were detected.</strong></p><?php endif; ?>
        </section></div>
        <?php
    }
}
