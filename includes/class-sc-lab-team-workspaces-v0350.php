<?php
/** Sustainable Catalyst Lab v0.35.0 Shared Research Projects and Team Workspaces. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Team_Workspaces_V0350 {
    const VERSION = '0.35.0';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_team_workspaces', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_shared_research_projects', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_collaboration_workspace', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('team-workspaces','shared-research-projects','shared-projects','collaboration-workspace','research-team') as $alias) {
            $aliases[$alias] = 'team-workspaces';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="team-workspaces"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/team-workspaces/v0350/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/team-workspaces/v0350/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'workspaceSchema'=>'sc-lab-team-workspace/0.35.0',
            'membershipSchema'=>'sc-lab-workspace-membership/0.35.0',
            'invitationSchema'=>'sc-lab-workspace-invitation/0.35.0',
            'resourceSchema'=>'sc-lab-workspace-resource-link/0.35.0',
            'eventSchema'=>'sc-lab-workspace-event/0.35.0',
            'roles'=>array('viewer','reviewer','contributor','editor','administrator','owner'),
            'singleUseInvitations'=>true,'ownershipTransfer'=>true,'hardDelete'=>false,
            'reviewComments'=>false,'scientificApprovals'=>false,'arbitraryCode'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/team-workspaces-v0350.js',
            'assets/css/sc-lab-team-workspaces-v0350.css',
            'contracts/team-workspace-v0350.schema.json',
            'contracts/team-workspace-membership-v0350.schema.json',
            'contracts/team-workspace-invitation-v0350.schema.json',
            'contracts/team-workspace-resource-v0350.schema.json',
            'contracts/team-workspace-event-v0350.schema.json',
            'contracts/team-workspace-access-decision-v0350.schema.json',
            'contracts/team-workspace-policy-v0350.json',
            'includes/class-sc-lab-team-workspaces-v0350.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'shared-research-projects-team-workspaces',
            'databaseSchemaVersion'=>1,'roleBasedMembership'=>true,
            'singleUseInvitationTokens'=>true,'governedResourceLinks'=>true,
            'ownershipTransfer'=>true,'archiveWithoutDeletion'=>true,
            'reviewComments'=>false,'scientificApprovals'=>false,'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
