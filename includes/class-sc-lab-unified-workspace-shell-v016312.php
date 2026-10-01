<?php
/** Sustainable Catalyst Lab v0.163.1.2 — Front-Door Visualization & Scientific Signals Retention Repair. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Unified_Workspace_Shell_V016312 {
    const VERSION = '0.163.1.2';
    const FEATURE_VERSION = '0.163.1';

    public static function init() {
        // v0.163.1.1 successfully repaired page length but treated the 4D
        // front-door visualizer as a specialist module. Retire its hooks before
        // WordPress renders the Lab request, then install the corrected shell.
        self::retire_v016311();
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue_after_legacy_gate'), PHP_INT_MAX);
        add_filter('body_class', array(__CLASS__, 'body_class'), PHP_INT_MAX);
        add_filter('the_content', array(__CLASS__, 'inject_server_shell_after_front_door'), PHP_INT_MAX);
    }

    private static function retire_v016311() {
        if (!class_exists('SC_Lab_Unified_Workspace_Shell_V016311')) { return; }
        remove_action('wp_enqueue_scripts', array('SC_Lab_Unified_Workspace_Shell_V016311', 'enqueue_after_legacy_gate'), PHP_INT_MAX);
        remove_filter('body_class', array('SC_Lab_Unified_Workspace_Shell_V016311', 'body_class'), PHP_INT_MAX);
        remove_filter('the_content', array('SC_Lab_Unified_Workspace_Shell_V016311', 'inject_server_shell'), PHP_INT_MAX);
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
        if (self::is_lab_request()) {
            $classes[] = 'sc-lab-v016312-frontdoor';
            $classes[] = 'sc-lab-v016312-progressive';
        }
        return array_values(array_unique($classes));
    }

    public static function enqueue_after_legacy_gate() {
        if (!self::is_lab_request()) { return; }

        // Remove both superseded shell lines. This still runs after the legacy
        // v0.154 PHP_INT_MAX asset gate so the replacement assets survive it.
        foreach (array('sc-lab-unified-workspace-shell-v01631','sc-lab-unified-workspace-shell-v016311') as $handle) {
            wp_dequeue_style($handle);
            wp_deregister_style($handle);
            wp_dequeue_script($handle);
            wp_deregister_script($handle);
        }

        $css = 'assets/css/sc-lab-unified-workspace-shell-v016312.css';
        $js  = 'assets/js/sc-lab-unified-workspace-shell-v016312.js';
        wp_enqueue_style('sc-lab-unified-workspace-shell-v016312', SC_LAB_URL . $css, array(), self::asset_token($css));
        wp_enqueue_script('sc-lab-unified-workspace-shell-v016312', SC_LAB_URL . $js, array(), self::asset_token($js), true);
        wp_localize_script('sc-lab-unified-workspace-shell-v016312', 'SCLabUnifiedWorkspaceShellV016312', array(
            'version' => self::VERSION,
            'featureVersion' => self::FEATURE_VERSION,
            'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
            'defaultWorkspace' => 'overview',
            'specialistWorkspaceCount' => 10,
            'persistentFrontDoorFourD' => true,
            'scientificSignalsVisibleOnOverview' => true,
            'scientificSignalsAutoRefresh' => true,
            'singleVisibleSpecialistWorkspace' => true,
            'shellAfterFrontDoor' => true,
            'pageLengthFailSafe' => true,
        ));
    }

    private static function nav_button($id, $code, $label, $description, $selected = false) {
        return '<button type="button" class="sc-lab-v016312-nav-button" data-sc-lab-shell-open="' . esc_attr($id) . '" data-search="' . esc_attr(strtolower($label . ' ' . $description)) . '" aria-selected="' . ($selected ? 'true' : 'false') . '">' .
            '<span class="sc-lab-v016312-code">' . esc_html($code) . '</span>' .
            '<span class="sc-lab-v016312-nav-copy"><strong>' . esc_html($label) . '</strong><small>' . esc_html($description) . '</small></span>' .
            '</button>';
    }

    private static function server_shell_markup() {
        // 4D is intentionally absent: the front-door visualization stays visible
        // above the specialist shell and is not adopted/moved by navigation.
        $groups = array(
            'Research' => array(
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
            $nav .= '<div class="sc-lab-v016312-nav-group" data-group="' . esc_attr(strtolower($group)) . '"><h4>' . esc_html($group) . '</h4>';
            foreach ($items as $item) { $nav .= self::nav_button($item[0], $item[1], $item[2], $item[3]); }
            $nav .= '</div>';
        }

        $cards = array(
            array('notebook','Notebook & Protocol','Define reproducible methods and computational records.'),
            array('batch','Batch Experiments','Run reproducible sweeps and ensemble planning.'),
            array('compute','Compute & HPC','Plan distributed and accelerated scientific execution.'),
            array('cross-study','Cross-Study','Compare replication evidence across studies.'),
            array('replication','Replication','Coordinate independent reproduction work.'),
            array('review','Review','Inspect evidence, findings, sign-off and publication readiness.'),
            array('research-os','Research OS','Coordinate the human-controlled project lifecycle.'),
            array('programs','Programs','Coordinate multiple projects and research portfolios.'),
            array('resources','Resources','Inspect dependencies, capacity and research-resource plans.'),
            array('governance','Governance','Manage institutional review and federated oversight.'),
        );
        $card_html = '';
        foreach ($cards as $card) {
            $card_html .= '<button type="button" class="sc-lab-v016312-overview-card" data-sc-lab-shell-open="' . esc_attr($card[0]) . '"><span>' . esc_html($card[1]) . '</span><small>' . esc_html($card[2]) . '</small><b>Open workspace →</b></button>';
        }

        return '<section class="sc-lab-v016312-shell" data-sc-lab-unified-shell data-sc-lab-unified-shell-v016312 data-server-rendered="1" data-active-workspace="overview">' .
            '<header class="sc-lab-v016312-topbar"><div><p class="sc-lab-v016312-eyebrow">LAB / ' . esc_html(self::VERSION) . ' · SPECIALIST WORKSPACES</p><h3>Continue from the 4D front door into the specialist research environment.</h3><p>The 4D visualization and Scientific signals remain visible above. Open one specialist workspace at a time here.</p></div><div class="sc-lab-v016312-topbar-tools"><button type="button" data-sc-lab-frontdoor-scroll>↑ Back to 4D visualization</button><label>Find workspace<input type="search" data-sc-lab-shell-search placeholder="Search workspaces…" autocomplete="off"></label><span data-sc-lab-shell-status>Overview · discovering workspaces</span></div></header>' .
            '<div class="sc-lab-v016312-layout"><aside class="sc-lab-v016312-rail" aria-label="Lab specialist workspace navigation"><div class="sc-lab-v016312-rail-head">' .
            self::nav_button('overview', 'OV', 'Overview', 'Choose a specialist workspace.', true) .
            '<button type="button" class="sc-lab-v016312-collapse" data-sc-lab-shell-collapse aria-label="Collapse workspace rail" title="Collapse workspace rail">⇤</button></div><nav data-sc-lab-shell-nav>' . $nav . '</nav></aside>' .
            '<main class="sc-lab-v016312-main"><section class="sc-lab-v016312-overview" data-sc-lab-shell-overview><div class="sc-lab-v016312-overview-head"><div><p class="sc-lab-v016312-eyebrow">LAB / SPECIALIST WORKSPACES</p><h4>Choose the research surface for the next step.</h4></div><span>Front door retained · specialist state preserved</span></div><div class="sc-lab-v016312-overview-grid">' . $card_html . '</div></section><div class="sc-lab-v016312-stage" data-sc-lab-shell-stage aria-live="polite"></div><details class="sc-lab-v016312-governance" data-sc-lab-shell-governance><summary>Methods &amp; governance</summary><div data-sc-lab-shell-governance-copy>Module-specific scientific boundaries appear here when a workspace is open. Existing Lab governance and human-authorization rules remain unchanged.</div></details></main></div>' .
            '<noscript><p class="sc-lab-v016312-noscript">JavaScript is required to open specialist workspaces. The 4D front door and scientific overview remain available while the specialist stack stays collapsed.</p></noscript>' .
            '</section>';
    }

    public static function inject_server_shell_after_front_door($content) {
        if (!self::is_lab_request()) { return $content; }
        $content = (string) $content;
        if (strpos($content, 'data-sc-lab-unified-shell-v016312') !== false) { return $content; }
        // Append rather than inject at the .sc-lab-app opening tag. This keeps
        // the canonical 4D visualization, research-start cards, figures, work,
        // scientific signals and traceability overview ahead of the shell.
        return $content . self::server_shell_markup();
    }
}
