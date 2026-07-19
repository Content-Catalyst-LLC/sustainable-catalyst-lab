<?php
/** Sustainable Catalyst Lab v0.39.1 Security, Privacy, Secrets, and Audit Hardening. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Security_Privacy_V0391 {
    const VERSION = '0.39.1';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_security_privacy', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_security_console', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('security-privacy','security-console','secret-vault','audit-integrity','privacy-operations') as $alias) { $aliases[$alias] = 'security-privacy-v0391'; }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="security-privacy-v0391"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/security-privacy/v0391/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) { $path=SC_LAB_DIR.$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function health() {
        $required=array('backend/app/security_privacy_hardening.py','backend/tests/test_security_privacy_hardening_v0391.py','assets/js/modules/security-privacy-v0391.js','assets/css/sc-lab-security-privacy-v0391.css','contracts/security-privacy-policy-v0391.json','contracts/secret-record-v0391.schema.json','contracts/service-credential-v0391.schema.json','contracts/security-audit-event-v0391.schema.json','contracts/privacy-request-v0391.schema.json');
        $files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'aes256GcmSecrets'=>true,'credentialHashing'=>true,'requestNonceReplayProtection'=>true,'signedAuditChains'=>true,'privacyScanning'=>true,'privacyRequests'=>true,'singleSignOn'=>false,'externalKeyManagement'=>false,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Security_Privacy_V0391::init();
