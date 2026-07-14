<?php
$root = dirname( __DIR__ );
$main = file_get_contents( $root . '/sustainable-catalyst-lab.php' );
$runtime = file_get_contents( $root . '/includes/class-sc-lab-runtime-stability-v0254.php' );
$js = file_get_contents( $root . '/assets/js/sc-lab-runtime-stability-v0254.js' );

$checks = array(
	'plugin header version' => preg_match( '/^\s*\*\s*Version:\s*0\.25\.4\s*$/m', $main ),
	'constant version' => false !== strpos( $main, "define('SC_LAB_VERSION', '0.25.4')" ),
	'runtime include' => false !== strpos( $main, 'class-sc-lab-runtime-stability-v0254.php' ),
	'runtime init' => false !== strpos( $main, 'SC_Lab_Runtime_Stability_V0254::init()' ),
	'shortcode output filter' => false !== strpos( $runtime, 'do_shortcode_tag' ),
	'single panel selector' => false !== strpos( $runtime, 'data-module-panel' ),
	'module REST route' => false !== strpos( $runtime, '/runtime/v0254/module/' ),
	'health REST route' => false !== strpos( $runtime, '/runtime/v0254/health' ),
	'admin-only legacy mode' => false !== strpos( $runtime, "current_user_can( 'manage_options' )" ),
	'duplicate runtime guard' => false !== strpos( $js, '__SCLabRuntimeStabilityV0254' ),
	'abortable requests' => false !== strpos( $js, 'AbortController' ),
	'unmount lifecycle' => false !== strpos( $js, 'sc:lab:module-unmounting' ),
	'mount lifecycle' => false !== strpos( $js, 'sc:lab:module-mounted' ),
	'one panel cleanup' => false !== strpos( $js, "querySelectorAll('[data-module-panel]')" ),
	'hidden activation repair' => false !== strpos( $runtime, 'activate_panel_html' ),
	'balanced tag parser' => false !== strpos( $runtime, 'find_matching_tag_end' ),
	'visible mounted panel CSS' => false !== strpos( file_get_contents( $root . '/assets/css/sc-lab-runtime-stability-v0254.css' ), '[data-sc-lab-mounted="1"]' ),
);

$failed = array_keys( array_filter( $checks, static function ( $passed ) { return ! $passed; } ) );
if ( $failed ) {
	fwrite( STDERR, 'v0.25.4 failed checks: ' . implode( ', ', $failed ) . PHP_EOL );
	exit( 1 );
}

echo 'Application Startup and Runtime Stability checks passed: ' . count( $checks ) . PHP_EOL;
