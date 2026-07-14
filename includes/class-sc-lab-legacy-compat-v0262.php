<?php
/**
 * Sustainable Catalyst Lab v0.26.2 legacy laboratory compatibility layer.
 *
 * Restores the multi-panel rendering path used before the v0.25.5 isolated
 * module lifecycle, while retaining the v0.26.x compute and queue layers.
 *
 * @package Sustainable_Catalyst_Lab
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( ! class_exists( 'SC_Lab_Legacy_Compatibility_V0262' ) ) {
	final class SC_Lab_Legacy_Compatibility_V0262 {
		const VERSION = '0.26.2';

		/** @var array<string,string> */
		private static $aliases = array(
			'home'                                      => 'overview',
			'project-overview'                          => 'overview',
			'observation-board'                         => 'feeds',
			'scientific-feeds'                          => 'feeds',
			'signals'                                   => 'feeds',
			'climate-maps'                              => 'climate',
			'earth-observation'                         => 'climate',
			'space-observations'                        => 'astronomy',
			'space-telescopes'                          => 'astronomy',
			'telescopes'                                => 'astronomy',
			'marine-biology'                            => 'marine',
			'marine-biodiversity'                       => 'marine',
			'ocean-biology'                             => 'marine',
			'dataset-inspector'                         => 'data',
			'physics-laboratory'                        => 'physics',
			'biology-laboratory'                        => 'biology',
			'astronomy-laboratory'                      => 'astronomy-lab',
			'astrophysics'                              => 'astronomy-lab',
			'materials-laboratory'                      => 'materials',
			'earth-systems-laboratory'                  => 'earth-systems',
			'energy-engineering'                        => 'energy-engineering',
			'energy-and-engineering'                    => 'energy-engineering',
			'electrical-embedded'                       => 'electrical-embedded',
			'electrical-and-embedded'                   => 'electrical-embedded',
			'electrical-electronics-and-embedded-systems'=> 'electrical-embedded',
			'mechanical-thermal'                        => 'mechanical-thermal',
			'mechanical-and-thermal'                    => 'mechanical-thermal',
			'civil-infrastructure'                      => 'civil-infrastructure',
			'civil-and-infrastructure'                  => 'civil-infrastructure',
			'architecture-building-performance'         => 'architecture-building',
			'architecture-and-building-performance'     => 'architecture-building',
			'urban-planning-spatial-systems'            => 'urban-planning-spatial',
			'urban-planning-and-spatial-systems'        => 'urban-planning-spatial',
			'sustainable-cities-urban-resilience'       => 'sustainable-cities-resilience',
			'sustainable-cities-and-urban-resilience'   => 'sustainable-cities-resilience',
			'comparative-economics-development-systems' => 'comparative-economics-development-systems',
			'comparative-economics-and-development-systems'=> 'comparative-economics-development-systems',
			'aerospace-engineering-flight-systems'      => 'aerospace-engineering-flight-systems',
			'aerospace-engineering-and-flight-systems'  => 'aerospace-engineering-flight-systems',
			'rocket-propulsion-spaceflight'              => 'rocket-propulsion-spaceflight',
			'rocket-propulsion-and-spaceflight'         => 'rocket-propulsion-spaceflight',
			'microbiology-laboratory'                   => 'microbiology',
			'biochemistry-molecular-analysis'           => 'biochemistry-molecular-analysis',
			'biochemistry-and-molecular-analysis'       => 'biochemistry-molecular-analysis',
			'biotechnology-bioprocess-engineering'      => 'biotechnology-bioprocess-engineering',
			'biotechnology-and-bioprocess-engineering'  => 'biotechnology-bioprocess-engineering',
			'biomedical-engineering-biosignals'         => 'biomedical-engineering-biosignals',
			'biomedical-engineering-and-biosignals'     => 'biomedical-engineering-biosignals',
			'genetics-genomics-sequence-analysis'       => 'genetics-genomics-sequence-analysis',
			'genetics-genomics-and-sequence-analysis'   => 'genetics-genomics-sequence-analysis',
			'laboratory-data-instrumentation'           => 'laboratory-data-instrumentation',
			'laboratory-data-and-instrumentation'       => 'laboratory-data-instrumentation',
			'circular-economy-industrial-ecology'       => 'circular-economy-industrial-ecology',
			'circular-economy-and-industrial-ecology'   => 'circular-economy-industrial-ecology',
			'visualization-export'                      => 'visualization',
			'visualization-and-export'                  => 'visualization',
			'code-switcher'                             => 'code-switcher',
			'science-and-engineering'                   => 'science-engineering',
			'experiments'                               => 'experiments',
			'evidence-and-decisions'                    => 'evidence',
			'notebook'                                  => 'notebook',
			'documentation'                             => 'documentation',
			'pdf-reports'                               => 'reports',
			'evidence-decisions'                        => 'evidence',
			'workspace-data'                            => 'workspace-data',
			'source-registry'                           => 'source-registry',
			'connector-status'                          => 'connector-status',
		);

		public static function bootstrap() {
			self::bootstrap_request_mode();
			add_action( 'wp_enqueue_scripts', array( __CLASS__, 'enqueue_assets' ), PHP_INT_MAX );
			add_filter( 'body_class', array( __CLASS__, 'body_classes' ) );
			add_action( 'rest_api_init', array( __CLASS__, 'register_rest_route' ) );
		}

		/**
		 * Force the pre-v0.25.5 complete markup path before the Lab renderer runs.
		 */
		private static function bootstrap_request_mode() {
			if ( self::is_admin_request() || self::is_rest_request() ) {
				return;
			}

			if ( ! self::looks_like_lab_request() ) {
				return;
			}

			// Explicit escape hatch for controlled lifecycle testing.
			if ( isset( $_GET['sc_lab_isolated'] ) && '1' === sanitize_text_field( wp_unslash( $_GET['sc_lab_isolated'] ) ) ) {
				return;
			}

			$_GET['sc_lab_legacy']     = '1';
			$_REQUEST['sc_lab_legacy'] = '1';

			foreach ( array( 'sc_lab_module', 'module', 'lab_module' ) as $key ) {
				if ( empty( $_GET[ $key ] ) ) {
					continue;
				}
				$raw       = sanitize_key( wp_unslash( $_GET[ $key ] ) );
				$canonical = self::canonical_module( $raw );
				$_GET['sc_lab_module']     = $canonical;
				$_REQUEST['sc_lab_module'] = $canonical;
				break;
			}
		}

		private static function is_admin_request() {
			return is_admin() && ! wp_doing_ajax();
		}

		private static function is_rest_request() {
			return defined( 'REST_REQUEST' ) && REST_REQUEST;
		}

		private static function looks_like_lab_request() {
			$uri = isset( $_SERVER['REQUEST_URI'] ) ? (string) wp_unslash( $_SERVER['REQUEST_URI'] ) : '';
			if ( false !== stripos( $uri, '/lab' ) || false !== stripos( $uri, 'sc_lab_' ) ) {
				return true;
			}
			return isset( $_GET['sc_lab_module'] ) || isset( $_GET['lab_module'] );
		}

		public static function canonical_module( $module ) {
			$module = sanitize_key( (string) $module );
			return isset( self::$aliases[ $module ] ) ? self::$aliases[ $module ] : $module;
		}

		public static function enqueue_assets() {
			if ( ! self::is_lab_page() ) {
				return;
			}

			$main_file = dirname( __DIR__ ) . '/sustainable-catalyst-lab.php';
			$js_url    = plugins_url( 'assets/js/lab-legacy-compat-v0262.js', $main_file );
			$css_url   = plugins_url( 'assets/css/lab-legacy-compat-v0262.css', $main_file );

			wp_enqueue_style( 'sc-lab-legacy-compat-v0262', $css_url, array(), self::VERSION );
			wp_enqueue_script( 'sc-lab-legacy-compat-v0262', $js_url, array(), self::VERSION, true );
			wp_add_inline_script(
				'sc-lab-legacy-compat-v0262',
				'window.SCLabCompatibilityV0262Config=' . wp_json_encode(
					array(
						'version' => self::VERSION,
						'aliases' => self::$aliases,
						'legacy'  => true,
					)
				) . ';',
				'before'
			);
		}

		private static function is_lab_page() {
			if ( function_exists( 'is_page' ) && is_page( 'lab' ) ) {
				return true;
			}
			global $post;
			return $post && isset( $post->post_content ) && has_shortcode( (string) $post->post_content, 'sc_lab_app' );
		}

		public static function body_classes( $classes ) {
			if ( self::is_lab_page() ) {
				$classes[] = 'sc-lab-legacy-compat-v0262';
				$classes[] = 'sc-lab-complete-module-markup';
			}
			return $classes;
		}

		public static function register_rest_route() {
			register_rest_route(
				'sc-lab/v1',
				'/runtime-compatibility',
				array(
					'methods'             => 'GET',
					'permission_callback' => '__return_true',
					'callback'            => static function () {
						return rest_ensure_response(
							array(
								'ok'            => true,
								'version'       => self::VERSION,
								'mode'          => 'legacy-compatible',
								'isolated_optin'=> 'sc_lab_isolated=1',
								'aliases'       => self::$aliases,
							)
						);
					},
				)
			);
		}
	}

	SC_Lab_Legacy_Compatibility_V0262::bootstrap();
}
