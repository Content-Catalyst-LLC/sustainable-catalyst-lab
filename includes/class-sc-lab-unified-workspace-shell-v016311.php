<?php
/** Sustainable Catalyst Lab v0.163.1.1 — Unified Workspace Shell Live-DOM Binding & Page-Length Repair. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Unified_Workspace_Shell_V016311 {
    const VERSION = '0.163.1.1';
    const FEATURE_VERSION = '0.163.1';

    public static function init() {
        // This class is loaded after the legacy v0.154 asset gate. Register at
        // PHP_INT_MAX so our replacement assets survive that gate.
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue_after_legacy_gate'), PHP_INT_MAX);
        add_filter('body_class', array(__CLASS__, 'body_class'), PHP_INT_MAX);
        add_filter('the_content', array(__CLASS__, 'inject_server_shell'), PHP_INT_MAX);
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if ($post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app')) { return true; }
        if (function_exists('is_page') && is_page('lab')) { return true; }
        $path = isset($_SERVER['REQUEST_URI']) ? (string) parse_url((string) $_SERVER['REQUEST_URI'], PHP_URL_PATH) : '';
        return (bool) preg_match('~/(?:lab)/?$~', $path);
    }

    private static function asset_token($rel) {
        $path = SC_LAB_DIR . ltrim((string) $rel, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    public static function body_class($classes) {
        if (self::is_lab_request()) { $classes[] = 'sc-lab-v016311-progressive'; }
        return array_values(array_unique($classes));
    }

    public static function enqueue_after_legacy_gate() {
        if (!self::is_lab_request()) { return; }

        // v0.163.1 used priority 240 and could be pruned later by the v0.154
        // PHP_INT_MAX asset gate. Remove the old handles and enqueue the repair
        // only after that gate has already run.
        wp_dequeue_style('sc-lab-unified-workspace-shell-v01631');
        wp_dequeue_script('sc-lab-unified-workspace-shell-v01631');

        $css = 'assets/css/sc-lab-unified-workspace-shell-v016311.css';
        $js  = 'assets/js/sc-lab-unified-workspace-shell-v016311.js';

        // Deliberately dependency-free: the shell is a presentation coordinator
        // and must not be blocked by a pruned historical asset handle.
        wp_enqueue_style(
            'sc-lab-unified-workspace-shell-v016311',
            SC_LAB_URL . $css,
            array(),
            self::asset_token($css)
        );
        wp_enqueue_script(
            'sc-lab-unified-workspace-shell-v016311',
            SC_LAB_URL . $js,
            array(),
            self::asset_token($js),
            true
        );
        wp_localize_script('sc-lab-unified-workspace-shell-v016311', 'SCLabUnifiedWorkspaceShellV016311', array(
            'version' => self::VERSION,
            'featureVersion' => self::FEATURE_VERSION,
            'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
            'defaultWorkspace' => 'overview',
            'specialistWorkspaceCount' => 11,
            'singleVisibleWorkspace' => true,
            'serverRenderedShell' => true,
            'liveDomBindingRepair' => true,
            'legacyAssetGateSurvival' => true,
            'pageLengthFailSafe' => true,
        ));
    }

    private static function nav_button($id, $code, $label, $description, $selected = false) {
        return '<button type="button" class="sc-lab-v016311-nav-button" data-sc-lab-shell-open="' . esc_attr($id) . '" data-search="' . esc_attr(strtolower($label . ' ' . $description)) . '" aria-selected="' . ($selected ? 'true' : 'false') . '">' .
            '<span class="sc-lab-v016311-code">' . esc_html($code) . '</span>' .
            '<span class="sc-lab-v016311-nav-copy"><strong>' . esc_html($label) . '</strong><small>' . esc_html($description) . '</small></span>' .
            '</button>';
    }

    private static function server_shell_markup() {
        $groups = array(
            'Research' => array(
                array('four-d','4D','4D Workspace','Multidimensional modeling, linked views, scenes and project assets.'),
                array('notebook','NB','Notebook & Protocol','Reproducible protocols, notebooks, compute references and manifests.'),
                array('batch','BX','Batch Experiments','Sweeps, ensembles, deterministic trials and execution handoffs.'),
            ),
            'Compute' => array(
                array('compute','HP','Compute & HPC','Distributed, accelerated and scheduler-neutral execution planning.'),
            ),
            'Evidence' => array(
                array('cross-study','XS','Cross-Study','Cross-study replication and descriptive meta-experiment synthesis.'),
                array('replication','RN','Replication Network','Independent replication nodes, plans, receipts and human review.'),
                array('review','RV','Scientific Review','Validation dossiers, findings, sign-off, dissent and publication handoff.'),
            ),
            'Operations' => array(
                array('research-os','OS','Research OS','Human-controlled research lifecycle, packages and project command center.'),
                array('programs','PG','Programs','Research programs, portfolios, objectives and milestones.'),
                array('resources','RS','Resources','Cross-project dependencies, shared resources and planning scenarios.'),
                array('governance','GV','Governance','Institutional review bodies, federation, decisions and sign-off evidence.'),
            ),
        );
        $nav = '';
        foreach ($groups as $group => $items) {
            $nav .= '<div class="sc-lab-v016311-nav-group" data-group="' . esc_attr(strtolower($group)) . '"><h4>' . esc_html($group) . '</h4>';
            foreach ($items as $item) { $nav .= self::nav_button($item[0], $item[1], $item[2], $item[3]); }
            $nav .= '</div>';
        }

        $cards = array(
            array('four-d','4D Workspace','Model, inspect and preserve multidimensional scientific scenes.'),
            array('notebook','Notebook & Protocol','Define reproducible methods and computational records.'),
            array('compute','Compute & HPC','Plan distributed and accelerated scientific execution.'),
            array('replication','Replication','Coordinate cross-study and independent reproduction work.'),
            array('review','Review','Inspect evidence, findings, sign-off and publication readiness.'),
            array('research-os','Research OS','Coordinate the human-controlled project lifecycle.'),
            array('programs','Programs','Coordinate multiple projects and research portfolios.'),
            array('governance','Governance','Manage institutional review and federated oversight.'),
        );
        $card_html = '';
        foreach ($cards as $card) {
            $card_html .= '<button type="button" class="sc-lab-v016311-overview-card" data-sc-lab-shell-open="' . esc_attr($card[0]) . '"><span>' . esc_html($card[1]) . '</span><small>' . esc_html($card[2]) . '</small><b>Open workspace →</b></button>';
        }

        return '<section class="sc-lab-v016311-shell" data-sc-lab-unified-shell data-sc-lab-unified-shell-v016311 data-server-rendered="1" data-active-workspace="overview">' .
            '<header class="sc-lab-v016311-topbar"><div><p class="sc-lab-v016311-eyebrow">LAB / ' . esc_html(self::VERSION) . ' · UNIFIED WORKSPACE SHELL</p><h3>Scientific workspaces, one active context at a time.</h3><p>Choose a workspace instead of rendering the entire research operating surface as one long page.</p></div><div class="sc-lab-v016311-topbar-tools"><label>Find workspace<input type="search" data-sc-lab-shell-search placeholder="Search workspaces…" autocomplete="off"></label><span data-sc-lab-shell-status>Overview · discovering workspaces</span></div></header>' .
            '<div class="sc-lab-v016311-layout"><aside class="sc-lab-v016311-rail" aria-label="Lab workspace navigation"><div class="sc-lab-v016311-rail-head">' .
            self::nav_button('overview', 'OV', 'Overview', 'Start here and open only the workspace you need.', true) .
            '<button type="button" class="sc-lab-v016311-collapse" data-sc-lab-shell-collapse aria-label="Collapse workspace rail" title="Collapse workspace rail">⇤</button></div><nav data-sc-lab-shell-nav>' . $nav . '</nav></aside>' .
            '<main class="sc-lab-v016311-main"><section class="sc-lab-v016311-overview" data-sc-lab-shell-overview><div class="sc-lab-v016311-overview-head"><div><p class="sc-lab-v016311-eyebrow">LAB / OVERVIEW</p><h4>Choose the research surface for the task at hand.</h4></div><span>Progressive navigation · specialist state preserved</span></div><div class="sc-lab-v016311-overview-grid">' . $card_html . '</div></section><div class="sc-lab-v016311-stage" data-sc-lab-shell-stage aria-live="polite"></div><details class="sc-lab-v016311-governance" data-sc-lab-shell-governance><summary>Methods &amp; governance</summary><div data-sc-lab-shell-governance-copy>Module-specific scientific boundaries appear here when a workspace is open. Existing Lab governance and human-authorization rules remain unchanged.</div></details></main></div>' .
            '<noscript><p class="sc-lab-v016311-noscript">JavaScript is required to open specialist workspaces. The progressive shell is keeping the full module stack collapsed to prevent an unusably long page.</p></noscript>' .
            '</section>';
    }

    public static function inject_server_shell($content) {
        if (!self::is_lab_request()) { return $content; }
        if (strpos((string) $content, 'data-sc-lab-unified-shell-v016311') !== false) { return $content; }
        $shell = self::server_shell_markup();

        // Prefer placing the shell directly inside the canonical Lab application
        // so it shares the app width/theme. If the canonical wrapper changes,
        // prepend rather than failing silently.
        $pattern = '~(<[^>]+class=["\'][^"\']*\bsc-lab-app\b[^"\']*["\'][^>]*>)~i';
        $count = 0;
        $out = preg_replace($pattern, '$1' . $shell, (string) $content, 1, $count);
        if ($count === 1 && is_string($out)) { return $out; }
        return $shell . (string) $content;
    }
}
