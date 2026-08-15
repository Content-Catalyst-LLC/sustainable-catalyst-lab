<?php
/** Sustainable Catalyst Lab v0.59.0 — Security, Privacy, Reproducibility & Scientific Audit. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Audit_V0590 {
    const VERSION='0.59.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/scientific-audit/v0590/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/scientific-audit/v0590/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'auditSchema'=>'sc-lab-scientific-audit-report/0.59.0','redactedExportSchema'=>'sc-lab-redacted-research-export/0.59.0','dataMinimizationSchema'=>'sc-lab-data-minimization-review/0.59.0'));}
    public static function health(){
        $required=array('backend/app/scientific_audit_v0590.py','backend/tests/test_scientific_audit_v0590.py','assets/js/modules/scientific-audit-v0590.js','assets/css/sc-lab-scientific-audit-v0590.css','contracts/scientific-audit-report-v0590.schema.json','contracts/redacted-research-export-v0590.schema.json','contracts/data-minimization-review-v0590.schema.json','contracts/scientific-audit-policy-v0590.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'security-privacy-reproducibility-scientific-audit-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'automaticCertification'=>false,'automaticPublication'=>false,'automaticHighStakesDecision'=>false,'rawSensitiveValuesInFindings'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
