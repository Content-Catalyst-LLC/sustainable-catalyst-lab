<?php
/** Functional parser test for the v0.25.4 single-panel runtime. */

define( 'ABSPATH', __DIR__ );

if ( ! function_exists( 'sanitize_key' ) ) {
	function sanitize_key( $key ) {
		$key = strtolower( (string) $key );
		return preg_replace( '/[^a-z0-9_-]/', '', $key );
	}
}
if ( ! function_exists( 'esc_attr' ) ) {
	function esc_attr( $value ) {
		return htmlspecialchars( (string) $value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8' );
	}
}
if ( ! function_exists( 'esc_html' ) ) {
	function esc_html( $value ) {
		return htmlspecialchars( (string) $value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8' );
	}
}

require dirname( __DIR__ ) . '/includes/class-sc-lab-runtime-stability-v0254.php';

$source = <<<'HTML'
<div class="lab-shell">
  <nav>
    <button data-lab-module="overview">Overview</button>
    <button data-lab-module="chemistry">Chemistry</button>
  </nav>
  <main>
    <section class="panel overview" data-module-panel="overview" aria-hidden="false">
      <h2>Overview panel</h2>
      <section><p>Nested section</p></section>
    </section>
    <section class="panel chemistry" data-module-panel="chemistry" hidden aria-hidden="true">
      <h2>Chemistry panel</h2>
      <img src="instrument.png" alt="Instrument">
      <section><p>Nested chemistry section</p></section>
    </section>
  </main>
</div>
HTML;

$reflection = new ReflectionClass( 'SC_Lab_Runtime_Stability_V0254' );

$build = $reflection->getMethod( 'build_lazy_shell' );
$build->setAccessible( true );
$initial = $build->invoke( null, $source, 'overview' );

$extract = $reflection->getMethod( 'extract_panel' );
$extract->setAccessible( true );
$chemistry = $extract->invoke( null, $source, 'chemistry' );

$checks = array(
	'initial shell marker' => false !== strpos( $initial, 'data-sc-lab-runtime-shell="0.25.4"' ),
	'initial keeps overview' => false !== strpos( $initial, 'Overview panel' ),
	'initial removes chemistry' => false === strpos( $initial, 'Chemistry panel' ),
	'initial has one module panel' => 1 === substr_count( $initial, 'data-module-panel=' ),
	'initial panel mounted' => false !== strpos( $initial, 'data-sc-lab-mounted="1"' ),
	'chemistry extracted' => is_array( $chemistry ) && false !== strpos( $chemistry['html'], 'Chemistry panel' ),
	'chemistry hidden removed' => is_array( $chemistry ) && ! preg_match( '/<section[^>]*\shidden(?:\s|=|>)/i', $chemistry['html'] ),
	'chemistry aria activated' => is_array( $chemistry ) && false !== strpos( $chemistry['html'], 'aria-hidden="false"' ),
	'chemistry active classes' => is_array( $chemistry ) && false !== strpos( $chemistry['html'], 'sc-lab-runtime-active-panel-v0254' ),
	'chemistry lazy image' => is_array( $chemistry ) && false !== strpos( $chemistry['html'], 'loading="lazy"' ),
	'nested panel balanced' => is_array( $chemistry ) && false !== strpos( $chemistry['html'], 'Nested chemistry section' ),
	'node count recorded' => is_array( $chemistry ) && $chemistry['node_count'] >= 5,
);

$failed = array_keys( array_filter( $checks, static function ( $passed ) { return ! $passed; } ) );
if ( $failed ) {
	fwrite( STDERR, 'v0.25.4 parser failed checks: ' . implode( ', ', $failed ) . PHP_EOL );
	exit( 1 );
}

echo 'Single-panel parser checks passed: ' . count( $checks ) . PHP_EOL;
