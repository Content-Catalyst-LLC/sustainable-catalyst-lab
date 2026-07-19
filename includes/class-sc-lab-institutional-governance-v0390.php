<?php
/** Sustainable Catalyst Lab v0.39.0 Institutional Administration, Identity, and Governance. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Institutional_Governance_V0390 {
    const VERSION = '0.39.0';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_institutional_governance', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_governance_console', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('institutional-governance','institutional-administration','identity-governance','governance-console','institution-admin') as $alias) {
            $aliases[$alias] = 'institutional-governance-v0390';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="institutional-governance-v0390"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/institutional-governance/v0390/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/institutional-governance/v0390/catalog', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'catalog'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function catalog() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'institutionRoles'=>array('institution-viewer','researcher','steward','approver','auditor','institution-admin','institution-owner'),
            'classifications'=>array('public','internal','confidential','restricted'),
            'principalTypes'=>array('human','service'),
            'secretStorage'=>false,'singleSignOn'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'backend/app/institutional_governance.py',
            'backend/tests/test_institutional_governance_v0390.py',
            'assets/js/modules/institutional-governance-v0390.js',
            'assets/css/sc-lab-institutional-governance-v0390.css',
            'contracts/institutional-governance-policy-v0390.json',
            'contracts/institution-v0390.schema.json',
            'contracts/institutional-principal-v0390.schema.json',
            'contracts/institutional-role-binding-v0390.schema.json',
            'contracts/workspace-governance-v0390.schema.json',
            'contracts/governance-decision-v0390.schema.json',
            'contracts/governance-approval-request-v0390.schema.json',
        );
        $files=array(); $ok=true;
        foreach($required as $relative){$files[$relative]=self::state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'institutions'=>true,'organizationalUnits'=>true,'humanAndServicePrincipals'=>true,
            'roleBindings'=>true,'classificationPolicy'=>true,'retentionPolicy'=>true,
            'approvalWorkflow'=>true,'policyEvaluation'=>true,'secretStorage'=>false,'singleSignOn'=>false,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
SC_Lab_Institutional_Governance_V0390::init();
