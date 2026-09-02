<?php
/** Sustainable Catalyst Lab v0.72.0 Public Homepage 4D Biodiversity Preview. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Homepage_Biodiversity_V0720 {
    const VERSION = '0.72.0';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_shortcode('sc_lab_home_preview', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_home_biodiversity', array(__CLASS__, 'shortcode'));
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    private static function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        $hash = is_file($path) ? substr(hash_file('sha256', $path), 0, 12) : '0';
        return self::VERSION . '.' . $hash;
    }

    private static function enqueue_assets() {
        $v0710_css = 'assets/css/sc-lab-advanced-visualization-front-door-v0710.css';
        $v0710_js = 'assets/js/modules/advanced-visualization-front-door-v0710.js';
        $v0720_css = 'assets/css/sc-lab-homepage-biodiversity-v0720.css';

        wp_enqueue_style(
            'sc-lab-advanced-visualization-front-door-v0710',
            SC_LAB_URL . $v0710_css,
            array(),
            self::asset_version($v0710_css)
        );
        wp_enqueue_style(
            'sc-lab-homepage-biodiversity-v0720',
            SC_LAB_URL . $v0720_css,
            array('sc-lab-advanced-visualization-front-door-v0710'),
            self::asset_version($v0720_css)
        );
        wp_enqueue_script(
            'sc-lab-advanced-visualization-front-door-v0710',
            SC_LAB_URL . $v0710_js,
            array(),
            self::asset_version($v0710_js),
            true
        );
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/homepage/v0720/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function health() {
        $files = array(
            'includes/class-sc-lab-homepage-biodiversity-v0720.php',
            'assets/css/sc-lab-homepage-biodiversity-v0720.css',
            'assets/js/modules/advanced-visualization-front-door-v0710.js',
        );
        $state = array();
        $ok = true;
        foreach ($files as $relative) {
            $path = SC_LAB_DIR . $relative;
            $exists = is_file($path);
            $state[$relative] = array(
                'exists' => $exists,
                'sha256' => $exists ? hash_file('sha256', $path) : null,
            );
            if (!$exists) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok' => $ok,
            'status' => $ok ? 'homepage-biodiversity-ready' : 'incomplete',
            'version' => self::VERSION,
            'release' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : null,
            'shortcode' => '[sc_lab_home_preview]',
            'profile' => 'biodiversity',
            'dimensionsRepresented' => 4,
            'dimensions' => array('habitat-quality', 'climate-stress', 'biodiversity-response', 'time-disturbance-progression'),
            'renderer' => 'advanced-visualization-front-door-v0710',
            'browserRendered' => true,
            'computeRequired' => false,
            'dataBoundary' => 'Deterministic synthetic illustration only; not observations, forecasts, or ecological measurements.',
            'files' => $state,
            'time' => gmdate('c'),
        ));
    }

    public static function shortcode($atts = array()) {
        $atts = shortcode_atts(array(
            'title' => '4D Biodiversity Modeling',
            'lab_url' => '/lab/',
            'graph_url' => '/lab/',
        ), $atts, 'sc_lab_home_preview');

        self::enqueue_assets();
        $id = function_exists('wp_unique_id') ? wp_unique_id('sc-lab-home-v0720-') : 'sc-lab-home-v0720';
        $title_id = $id . '-title';

        ob_start();
        ?>
        <section id="lab" class="sc-lab-home-v0720" aria-labelledby="<?php echo esc_attr($title_id); ?>" data-sc-lab-home-v0720>
          <header class="sc-lab-home-v0720__head">
            <div>
              <p class="sc-lab-home-v0720__kicker">Research Lab · 4D scientific modeling</p>
              <h2 id="<?php echo esc_attr($title_id); ?>"><?php echo esc_html($atts['title']); ?></h2>
              <p class="sc-lab-home-v0720__lede">Explore how habitat quality, climate stress, biodiversity response, and change over time can be represented together in a higher-dimensional scientific model.</p>
            </div>
            <span class="sc-lab-home-v0720__badge">Illustrative · browser rendered</span>
          </header>

          <div class="sc-lab-home-v0720__visualizer sc-lab-v0710-visualizer" data-v0710-visualizer data-v0710-profile="biodiversity" data-v0710-initial-w="0.60">
            <div class="sc-lab-home-v0720__toolbar">
              <div class="sc-lab-home-v0720__legend" aria-label="Illustrative visualization legend">
                <span><i class="is-surface"></i>Model surface</span>
                <span><i class="is-sample"></i>Synthetic samples</span>
                <span><i class="is-project"></i>Projected state</span>
              </div>
              <span class="sc-lab-home-v0720__dimension"><strong>4D</strong> habitat · climate · response · time</span>
            </div>

            <div class="sc-lab-home-v0720__stage">
              <div class="sc-lab-home-v0720__canvas-wrap">
                <canvas class="sc-lab-v0710-canvas sc-lab-home-v0720__canvas" data-v0710-canvas aria-label="Illustrative four-dimensional biodiversity response field projected into three dimensions"></canvas>
                <div class="sc-lab-v0710-overlay sc-lab-home-v0720__overlay" aria-hidden="true">
                  <span class="sc-lab-v0710-chip"><strong>4D</strong> biodiversity response surface</span>
                  <span class="sc-lab-v0710-chip">Synthetic example</span>
                </div>
                <div class="sc-lab-v0710-readout sc-lab-home-v0720__readout" data-v0710-readout>Illustrative biodiversity field · t 0.60</div>
                <div class="sc-lab-v0710-pointer sc-lab-home-v0720__pointer" data-v0710-pointer>Move over the field to inspect the illustrative model</div>
              </div>

              <aside class="sc-lab-home-v0720__controls" aria-label="Fourth-dimension controls">
                <p class="sc-lab-home-v0720__control-label">4th dimension</p>
                <h3>Time slice</h3>
                <p>Move through a synthetic habitat-and-climate response over time. This demonstrates 4D hyperslicing; it is not a biodiversity forecast.</p>

                <label class="sc-lab-v0710-control sc-lab-home-v0720__time">
                  <span>Time / disturbance <output data-v0710-metric="slice">0.60</output></span>
                  <input data-v0710-w type="range" min="0" max="1" step="0.01" value="0.60" aria-label="Illustrative biodiversity time slice">
                </label>

                <details class="sc-lab-home-v0720__4d-controls">
                  <summary>4D projection controls</summary>
                  <label class="sc-lab-v0710-control"><span>XW rotation <output>4D plane</output></span><input data-v0710-xw type="range" min="-1.4" max="1.4" step="0.01" value="0.34"></label>
                  <label class="sc-lab-v0710-control"><span>YW rotation <output>4D plane</output></span><input data-v0710-yw type="range" min="-1.4" max="1.4" step="0.01" value="-0.22"></label>
                </details>

                <button type="button" class="sc-lab-v0710-animate sc-lab-home-v0720__animate" data-v0710-animate aria-pressed="false">Animate time sweep</button>
                <div class="sc-lab-home-v0720__metric"><small>Peak illustrative response</small><strong data-v0710-metric="peak">—</strong><span>relative synthetic units</span></div>
              </aside>
            </div>
          </div>

          <div class="sc-lab-home-v0720__capabilities" aria-label="Lab capability pathways">
            <div><span>01</span><strong>Model</strong><p>Build mechanistic and statistical representations of ecological systems.</p></div>
            <div><span>02</span><strong>Graph</strong><p>Visualize response surfaces, uncertainty, networks, and higher-dimensional dynamics.</p></div>
            <div><span>03</span><strong>Experiment</strong><p>Design scenarios, compare interventions, and preserve parameter sweeps.</p></div>
            <div><span>04</span><strong>Observe</strong><p>Connect evidence, observations, datasets, and emerging system change.</p></div>
          </div>

          <footer class="sc-lab-home-v0720__foot">
            <p><strong>Illustrative biodiversity model.</strong> Values are deterministic synthetic interface data used to demonstrate Lab visualization. They are not measurements, species estimates, forecasts, or conservation conclusions.</p>
            <div class="sc-lab-home-v0720__actions">
              <a class="sc-lab-home-v0720__button is-primary" href="<?php echo esc_url($atts['lab_url']); ?>">Enter the Lab <span aria-hidden="true">→</span></a>
              <a class="sc-lab-home-v0720__button" href="<?php echo esc_url($atts['graph_url']); ?>">Open Graph Studio <span aria-hidden="true">↗</span></a>
            </div>
          </footer>
        </section>
        <?php
        return ob_get_clean();
    }
}
