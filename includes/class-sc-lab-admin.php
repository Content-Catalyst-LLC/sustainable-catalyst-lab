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
        );
    }

    public function __construct() {
        add_action('admin_menu', array($this, 'menu'));
        add_action('admin_init', array($this, 'register'));
    }

    public function menu() {
        add_options_page('Sustainable Catalyst Lab', 'Sustainable Catalyst Lab', 'manage_options', 'sc-lab-settings', array($this, 'page'));
    }

    public function register() {
        register_setting('sc_lab_settings_group', 'sc_lab_settings', array($this, 'sanitize'));
    }

    public function sanitize($input) {
        $defaults = self::defaults();
        return array(
            'workbench_url' => esc_url_raw(isset($input['workbench_url']) ? $input['workbench_url'] : $defaults['workbench_url']),
            'decision_studio_url' => esc_url_raw(isset($input['decision_studio_url']) ? $input['decision_studio_url'] : $defaults['decision_studio_url']),
            'site_intelligence_url' => esc_url_raw(isset($input['site_intelligence_url']) ? $input['site_intelligence_url'] : $defaults['site_intelligence_url']),
            'cache_minutes' => max(5, min(1440, absint(isset($input['cache_minutes']) ? $input['cache_minutes'] : 30))),
            'enable_feeds' => empty($input['enable_feeds']) ? 0 : 1,
            'enable_climate_maps' => empty($input['enable_climate_maps']) ? 0 : 1,
            'ncbi_tool' => sanitize_key(isset($input['ncbi_tool']) ? $input['ncbi_tool'] : $defaults['ncbi_tool']),
            'ncbi_email' => sanitize_email(isset($input['ncbi_email']) ? $input['ncbi_email'] : $defaults['ncbi_email']),
        );
    }

    public function page() {
        if (!current_user_can('manage_options')) { return; }
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), self::defaults());
        ?>
        <div class="wrap"><h1>Sustainable Catalyst Lab</h1>
        <p>Configure the modular science workspace, source caching, and routes into the larger Sustainable Catalyst applications.</p>
        <form method="post" action="options.php"><?php settings_fields('sc_lab_settings_group'); ?>
        <table class="form-table" role="presentation">
        <?php foreach (array('workbench_url'=>'Workbench route','decision_studio_url'=>'Decision Studio route','site_intelligence_url'=>'Site Intelligence route') as $key=>$label): ?>
        <tr><th scope="row"><label for="<?php echo esc_attr($key); ?>"><?php echo esc_html($label); ?></label></th><td><input class="regular-text" type="url" id="<?php echo esc_attr($key); ?>" name="sc_lab_settings[<?php echo esc_attr($key); ?>]" value="<?php echo esc_attr($settings[$key]); ?>"></td></tr>
        <?php endforeach; ?>
        <tr><th scope="row"><label for="cache_minutes">Feed cache</label></th><td><input type="number" min="5" max="1440" id="cache_minutes" name="sc_lab_settings[cache_minutes]" value="<?php echo esc_attr($settings['cache_minutes']); ?>"> minutes</td></tr>
        <tr><th scope="row">Modules</th><td><label><input type="checkbox" name="sc_lab_settings[enable_feeds]" value="1" <?php checked($settings['enable_feeds'], 1); ?>> Scientific feeds</label><br><label><input type="checkbox" name="sc_lab_settings[enable_climate_maps]" value="1" <?php checked($settings['enable_climate_maps'], 1); ?>> Climate maps</label></td></tr>
        <tr><th scope="row"><label for="ncbi_tool">NCBI tool name</label></th><td><input class="regular-text" id="ncbi_tool" name="sc_lab_settings[ncbi_tool]" value="<?php echo esc_attr($settings['ncbi_tool']); ?>"></td></tr>
        <tr><th scope="row"><label for="ncbi_email">NCBI contact email</label></th><td><input class="regular-text" type="email" id="ncbi_email" name="sc_lab_settings[ncbi_email]" value="<?php echo esc_attr($settings['ncbi_email']); ?>"></td></tr>
        </table><?php submit_button(); ?></form></div>
        <?php
    }
}
