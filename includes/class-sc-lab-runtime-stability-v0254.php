<?php
/**
 * Sustainable Catalyst Lab v0.25.4 runtime stability layer.
 *
 * Keeps the main Lab application shell small by retaining one module panel at
 * a time and loading additional panels through the WordPress REST API.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

final class SC_Lab_Runtime_Stability_V0254 {
	const VERSION = '0.25.4';
	const REST_NAMESPACE = 'sc-lab/v1';
	const ROOT_ID = 'sc-lab-v0254-document-root';

	/** @var bool */
	private static $initialized = false;

	/** @var bool */
	private static $rendering_full_app = false;

	/** @var bool */
	private static $assets_enqueued = false;

	/**
	 * Register the patch once.
	 */
	public static function init() {
		if ( self::$initialized ) {
			return;
		}

		self::$initialized = true;

		add_action( 'wp_enqueue_scripts', array( __CLASS__, 'maybe_enqueue_assets' ), 1 );
		add_action( 'rest_api_init', array( __CLASS__, 'register_routes' ) );
		add_filter( 'do_shortcode_tag', array( __CLASS__, 'filter_shortcode_output' ), PHP_INT_MAX, 4 );
	}

	/**
	 * Detect the main Lab page before the normal module assets are printed.
	 */
	public static function maybe_enqueue_assets() {
		if ( is_admin() ) {
			return;
		}

		global $post;
		$has_main_shortcode = $post instanceof WP_Post
			&& has_shortcode( (string) $post->post_content, 'sc_lab_app' );

		if ( $has_main_shortcode || isset( $_GET['sc_lab_module'] ) || isset( $_GET['sc_lab_safe'] ) ) {
			self::enqueue_assets();
		}
	}

	/**
	 * Enqueue the small head runtime before the large module scripts.
	 */
	private static function enqueue_assets() {
		if ( self::$assets_enqueued ) {
			return;
		}

		self::$assets_enqueued = true;

		$base_url = defined( 'SC_LAB_URL' ) ? SC_LAB_URL : plugin_dir_url( dirname( __DIR__ ) . '/sustainable-catalyst-lab.php' );

		wp_enqueue_style(
			'sc-lab-runtime-stability-v0254',
			$base_url . 'assets/css/sc-lab-runtime-stability-v0254.css',
			array(),
			self::VERSION
		);

		wp_enqueue_script(
			'sc-lab-runtime-stability-v0254',
			$base_url . 'assets/js/sc-lab-runtime-stability-v0254.js',
			array(),
			self::VERSION,
			true
		);

		$config = array(
			'version'       => self::VERSION,
			'restBase'      => esc_url_raw( rest_url( self::REST_NAMESPACE . '/runtime/v0254' ) ),
			'nonce'         => is_user_logged_in() ? wp_create_nonce( 'wp_rest' ) : '',
			'defaultModule' => self::requested_module(),
			'safeStart'     => isset( $_GET['sc_lab_safe'] ),
			'nodeBudget'    => 12000,
			'panelBudget'   => 900000,
		);

		wp_localize_script( 'sc-lab-runtime-stability-v0254', 'SCLabRuntimeV0254', $config );
		wp_add_inline_script(
			'sc-lab-runtime-stability-v0254',
			'window.SCLabRuntimeMode="lazy";window.SCLabRuntimeVersion="0.25.4";',
			'before'
		);
	}

	/**
	 * Replace the all-at-once app output with one retained module panel.
	 */
	public static function filter_shortcode_output( $output, $tag, $attr, $match ) {
		unset( $attr, $match );

		if ( 'sc_lab_app' !== $tag || self::$rendering_full_app ) {
			return $output;
		}

		if ( is_admin() && ! wp_doing_ajax() ) {
			return $output;
		}

		if ( self::legacy_mode_allowed() ) {
			return $output;
		}

		self::enqueue_assets();

		return self::build_lazy_shell( (string) $output, self::requested_module() );
	}

	/**
	 * Register public read-only module and health routes.
	 */
	public static function register_routes() {
		register_rest_route(
			self::REST_NAMESPACE,
			'/runtime/v0254/module/(?P<module>[a-z0-9-]+)',
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => array( __CLASS__, 'rest_module' ),
				'permission_callback' => '__return_true',
				'args'                => array(
					'module' => array(
						'sanitize_callback' => 'sanitize_key',
						'validate_callback' => array( __CLASS__, 'validate_module_slug' ),
					),
				),
			)
		);

		register_rest_route(
			self::REST_NAMESPACE,
			'/runtime/v0254/health',
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => array( __CLASS__, 'rest_health' ),
				'permission_callback' => '__return_true',
			)
		);
	}

	/**
	 * Validate a requested module slug without permitting path-like values.
	 */
	public static function validate_module_slug( $value ) {
		return is_string( $value ) && (bool) preg_match( '/^[a-z0-9][a-z0-9-]{0,79}$/', $value );
	}

	/**
	 * Return a single module panel.
	 */
	public static function rest_module( WP_REST_Request $request ) {
		$module = sanitize_key( (string) $request['module'] );
		$full   = self::render_full_application();

		if ( '' === trim( $full ) ) {
			return new WP_Error(
				'sc_lab_runtime_empty_application',
				__( 'The Lab application returned no output.', 'sustainable-catalyst-lab' ),
				array( 'status' => 500 )
			);
		}

		$panel = self::extract_panel( $full, $module );
		if ( ! is_array( $panel ) ) {
			return new WP_Error(
				'sc_lab_runtime_module_not_found',
				__( 'The requested Lab module is unavailable.', 'sustainable-catalyst-lab' ),
				array( 'status' => 404, 'module' => $module )
			);
		}

		return rest_ensure_response(
			array(
				'ok'        => true,
				'version'   => self::VERSION,
				'module'    => $module,
				'html'      => $panel['html'],
				'bytes'     => strlen( $panel['html'] ),
				'nodeCount' => $panel['node_count'],
			)
		);
	}

	/**
	 * Lightweight production-health response.
	 */
	public static function rest_health() {
		return rest_ensure_response(
			array(
				'ok'              => true,
				'version'         => self::VERSION,
				'mode'            => 'single-panel-lazy-runtime',
				'panelParser'     => 'balanced-tag-parser',
				'duplicateGuard'  => true,
				'abortableLoads'  => true,
				'legacyAdminOnly' => true,
			)
		);
	}

	/**
	 * Render the original shortcode while bypassing this output filter.
	 */
	private static function render_full_application() {
		self::$rendering_full_app = true;
		try {
			return (string) do_shortcode( '[sc_lab_app]' );
		} finally {
			self::$rendering_full_app = false;
		}
	}

	/**
	 * Create a reduced shell containing one module panel.
	 */
	private static function build_lazy_shell( $html, $requested_module ) {
		$panels = self::scan_module_panels( $html );
		if ( ! $panels ) {
			return self::fallback_shell( $requested_module );
		}

		$selected = isset( $panels[ $requested_module ] ) ? $requested_module : '';
		if ( ! $selected && isset( $panels['overview'] ) ) {
			$selected = 'overview';
		}
		if ( ! $selected ) {
			$keys     = array_keys( $panels );
			$selected = (string) reset( $keys );
		}

		$ordered = array_values( $panels );
		usort(
			$ordered,
			static function ( $left, $right ) {
				return $left['start'] <=> $right['start'];
			}
		);

		$cursor = 0;
		$body   = '';
		foreach ( $ordered as $panel ) {
			$body .= substr( $html, $cursor, $panel['start'] - $cursor );
			if ( $panel['slug'] === $selected ) {
				$panel_html = self::activate_panel_html( $panel['html'] );
				$body .= '<div data-sc-lab-lazy-host="1">' . $panel_html . '</div>';
			}
			$cursor = $panel['end'];
		}
		$body .= substr( $html, $cursor );

		return '<div id="' . esc_attr( self::ROOT_ID ) . '" data-sc-lab-runtime-shell="' . esc_attr( self::VERSION ) . '" data-sc-lab-active-module="' . esc_attr( $selected ) . '" data-sc-lab-original-panel-count="' . esc_attr( (string) count( $panels ) ) . '">' .
			self::runtime_bar_html( $selected ) .
			$body .
			'<noscript><p class="sc-lab-runtime-error-v0254">JavaScript is required to switch among Lab modules. The Overview remains available.</p></noscript>' .
			'</div>';
	}

	/**
	 * Extract exactly one panel from the original application output.
	 */
	private static function extract_panel( $html, $module ) {
		$panels = self::scan_module_panels( $html );
		if ( ! isset( $panels[ $module ] ) ) {
			return null;
		}

		$panel_html = $panels[ $module ]['html'];
		$panel_html = preg_replace( '~<script\b[^>]*>.*?</script\s*>~is', '', $panel_html );
		$panel_html = self::add_lazy_media_attributes( $panel_html );
		$panel_html = self::activate_panel_html( $panel_html );

		if ( ! is_string( $panel_html ) || strlen( $panel_html ) > 1500000 ) {
			return null;
		}

		return array(
			'html'       => $panel_html,
			'node_count' => self::approximate_node_count( $panel_html ),
		);
	}

	/**
	 * Locate top-level module panel ranges without requiring the PHP DOM extension.
	 */
	private static function scan_module_panels( $html ) {
		$pattern = '~<([a-z][a-z0-9:-]*)\b[^>]*\bdata-module-panel\s*=\s*(["\'])([^"\']+)\2[^>]*>~i';
		if ( ! preg_match_all( $pattern, $html, $matches, PREG_OFFSET_CAPTURE ) ) {
			return array();
		}

		$panels = array();
		$count  = count( $matches[0] );
		for ( $index = 0; $index < $count; $index++ ) {
			$opening = $matches[0][ $index ][0];
			$start   = (int) $matches[0][ $index ][1];
			$tag     = strtolower( $matches[1][ $index ][0] );
			$slug    = sanitize_key( $matches[3][ $index ][0] );
			if ( ! $slug || isset( $panels[ $slug ] ) ) {
				continue;
			}

			$end = self::find_matching_tag_end( $html, $tag, $start, strlen( $opening ) );
			if ( null === $end || $end <= $start ) {
				continue;
			}

			$panels[ $slug ] = array(
				'slug'  => $slug,
				'tag'   => $tag,
				'start' => $start,
				'end'   => $end,
				'html'  => substr( $html, $start, $end - $start ),
			);
		}

		return $panels;
	}

	/**
	 * Balance opening and closing tags of the panel's own element type.
	 */
	private static function find_matching_tag_end( $html, $tag, $start, $opening_length ) {
		$token_pattern = '~</?' . preg_quote( $tag, '~' ) . '\b[^>]*>~i';
		$offset        = $start + $opening_length;
		$depth         = 1;

		while ( preg_match( $token_pattern, $html, $match, PREG_OFFSET_CAPTURE, $offset ) ) {
			$token       = $match[0][0];
			$token_start = (int) $match[0][1];
			$offset      = $token_start + strlen( $token );

			if ( 0 === strpos( ltrim( $token ), '</' ) ) {
				$depth--;
				if ( 0 === $depth ) {
					return $offset;
				}
			} elseif ( ! preg_match( '~/\s*>$~', $token ) ) {
				$depth++;
			}
		}

		return null;
	}

	/**
	 * Make the retained or fetched panel visible and mark it as mounted.
	 */
	private static function activate_panel_html( $html ) {
		$html = preg_replace_callback(
			'~^(\s*<[a-z][a-z0-9:-]*\b[^>]*>)~i',
			static function ( $match ) {
				$opening = $match[1];

				$opening = preg_replace( '~\s+hidden\b(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+))?~i', '', $opening );
				$opening = preg_replace( '~\s+aria-hidden\s*=\s*(["\'])true\1~i', ' aria-hidden="false"', $opening );

				if ( preg_match( '~\sclass\s*=\s*(["\'])(.*?)\1~is', $opening, $class_match ) ) {
					$classes = preg_split( '/\s+/', trim( $class_match[2] ) );
					$classes = array_values( array_filter( $classes ) );
					foreach ( array( 'is-active', 'sc-lab-runtime-active-panel-v0254' ) as $class_name ) {
						if ( ! in_array( $class_name, $classes, true ) ) {
							$classes[] = $class_name;
						}
					}
					$replacement = ' class=' . $class_match[1] . esc_attr( implode( ' ', $classes ) ) . $class_match[1];
					$opening = str_replace( $class_match[0], $replacement, $opening );
				} else {
					$opening = preg_replace(
						'~^((?:\s*)<[a-z][a-z0-9:-]*\b)~i',
						'$1 class="is-active sc-lab-runtime-active-panel-v0254"',
						$opening,
						1
					);
				}

				return $opening;
			},
			$html,
			1
		);

		return self::add_attribute_to_opening_tag( $html, 'data-sc-lab-mounted', '1' );
	}

	/**
	 * Add an attribute to the first opening tag in an HTML fragment.
	 */
	private static function add_attribute_to_opening_tag( $html, $name, $value ) {
		if ( preg_match( '~^\s*<[^>]+\b' . preg_quote( $name, '~' ) . '\s*=~i', $html ) ) {
			return $html;
		}

		return preg_replace(
			'~^(\s*<[a-z][a-z0-9:-]*\b)~i',
			'$1 ' . $name . '="' . esc_attr( $value ) . '"',
			$html,
			1
		);
	}

	/**
	 * Add browser-native lazy loading to media in a fetched panel.
	 */
	private static function add_lazy_media_attributes( $html ) {
		$html = preg_replace_callback(
			'~<img\b[^>]*>~i',
			static function ( $match ) {
				$tag = $match[0];
				if ( false === stripos( $tag, ' loading=' ) ) {
					$tag = preg_replace( '~\s*/?>$~', ' loading="lazy"$0', $tag, 1 );
				}
				if ( false === stripos( $tag, ' decoding=' ) ) {
					$tag = preg_replace( '~\s*/?>$~', ' decoding="async"$0', $tag, 1 );
				}
				return $tag;
			},
			$html
		);

		return preg_replace_callback(
			'~<iframe\b[^>]*>~i',
			static function ( $match ) {
				$tag = $match[0];
				if ( false === stripos( $tag, ' loading=' ) ) {
					$tag = preg_replace( '~\s*>$~', ' loading="lazy"$0', $tag, 1 );
				}
				return $tag;
			},
			$html
		);
	}

	/**
	 * Estimate the element count for diagnostics and safe budgets.
	 */
	private static function approximate_node_count( $html ) {
		preg_match_all( '~<[a-z][a-z0-9:-]*\b[^>]*>~i', $html, $matches );
		return count( $matches[0] );
	}

	/**
	 * Runtime controls added above the existing application chrome.
	 */
	private static function runtime_bar_html( $module ) {
		return '<div class="sc-lab-runtime-bar-v0254" data-sc-lab-runtime-bar="1">' .
			'<p class="sc-lab-runtime-status-v0254">Stable runtime active · one laboratory loaded at a time</p>' .
			'<div class="sc-lab-runtime-actions-v0254">' .
			'<button type="button" data-sc-lab-runtime-action="overview">Overview</button>' .
			'<button type="button" data-sc-lab-runtime-action="reload">Reload module</button>' .
			'<button type="button" data-sc-lab-runtime-action="safe">Safe start</button>' .
			'</div>' .
			'<span class="sc-lab-runtime-meta-v0254" data-sc-lab-runtime-meta="1">v' . esc_html( self::VERSION ) . ' · ' . esc_html( $module ) . '</span>' .
			'</div>';
	}

	/**
	 * Emergency shell used when the canonical app has no recognizable panels.
	 */
	private static function fallback_shell( $module ) {
		$module = esc_html( $module );
		return '<section id="' . esc_attr( self::ROOT_ID ) . '" class="sc-lab-runtime-fallback-v0254" data-sc-lab-runtime-shell="' . esc_attr( self::VERSION ) . '">' .
			'<p class="sc-lab-runtime-status-v0254">Sustainable Catalyst Lab stable runtime</p>' .
			'<h2>Application safe start</h2>' .
			'<p>The full all-at-once application was withheld to prevent another browser crash. The canonical application did not expose recognizable module panels for the stability layer.</p>' .
			'<p><strong>Requested module:</strong> ' . $module . '</p>' .
			'<p>Focused Lab shortcodes and REST calculation routes remain available.</p>' .
			'</section>';
	}

	/**
	 * Requested initial module, with explicit safe-start override.
	 */
	private static function requested_module() {
		if ( isset( $_GET['sc_lab_safe'] ) ) {
			return 'overview';
		}
		$module = isset( $_GET['sc_lab_module'] ) ? sanitize_key( wp_unslash( $_GET['sc_lab_module'] ) ) : 'overview';
		return self::validate_module_slug( $module ) ? $module : 'overview';
	}

	/**
	 * The old all-at-once page is available only to administrators for diagnosis.
	 */
	private static function legacy_mode_allowed() {
		return isset( $_GET['sc_lab_legacy'] )
			&& current_user_can( 'manage_options' );
	}

}
