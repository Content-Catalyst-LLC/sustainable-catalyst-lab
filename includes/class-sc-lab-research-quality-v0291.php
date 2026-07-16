<?php
/**
 * Sustainable Catalyst Lab v0.29.1 Research Quality and Method Review.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Research_Quality_V0291 {
    const VERSION = '0.29.1';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
    }

    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('method-review','research-quality','quality-review','method-governance','method-quality') as $alias) {
            $aliases[$alias] = 'method-review';
        }
        return $aliases;
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/research-quality/v0291/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/research-quality/v0291/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/research-quality/v0291/policies', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'policies'),'permission_callback'=>'__return_true'));
    }

    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,'reviewSchema'=>'sc-lab-method-review/0.29.1','decisionSchema'=>'sc-lab-method-review-decision/0.29.1',
            'bundleSchema'=>'sc-lab-method-review-bundle/0.29.1','collections'=>array('methodReviewRecords','reviewDecisionRecords','methodDeprecationRecords','methodReviewComparisons'),
            'links'=>array('benchmarks','validationEvidence','sources','evidence','reproducibleRuns','researchProvenance'),'storageMode'=>'browser-local-project-records','serverBackedRegistry'=>false
        ));
    }

    public static function policies() {
        $path = SC_LAB_DIR . 'contracts/method-review-policy-v0291.json';
        $decoded = is_file($path) ? json_decode((string) file_get_contents($path), true) : null;
        return rest_ensure_response(is_array($decoded) ? array_merge(array('ok'=>true), $decoded) : array('ok'=>false,'version'=>self::VERSION));
    }

    public static function health() {
        $required = array(
            'assets/js/modules/research-quality-v0291.js','assets/css/sc-lab-research-quality-v0291.css',
            'contracts/method-review-v0291.schema.json','contracts/method-review-policy-v0291.json',
            'contracts/method-review-result-v0291.schema.json','contracts/method-review-bundle-v0291.schema.json'
        );
        $files=array(); $ok=true;
        foreach ($required as $relative) {
            $exists=is_file(SC_LAB_DIR.$relative); $ok=$ok&&$exists;
            $files[$relative]=array('exists'=>$exists,'sha256'=>$exists?hash_file('sha256',SC_LAB_DIR.$relative):null);
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,'release'=>SC_LAB_VERSION,
            'architecture'=>'project-method-review-registry-with-governed-python-evaluation','approvalWorkflow'=>true,
            'benchmarkCoverage'=>true,'calibrationTracking'=>true,'deprecationHistory'=>true,'files'=>$files,'time'=>gmdate('c')
        ));
    }
}
