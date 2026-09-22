<?php
/** Sustainable Catalyst Lab v0.108.0 — Findings, Claims, Evidence & Validation Bridge. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Platform_Core_V3_Findings_Validation_V01080 {
    const VERSION = '0.108.0';
    const MINIMUM_CORE_RELEASE = '3.0.0';
    const PRODUCT_REF = 'product:sustainable-catalyst-lab';
    const BRIDGE_SCHEMA = 'sc-lab-platform-core-v3-findings-claims-evidence-validation/0.108.0';
    const FINDING_CLAIM_EVIDENCE_CONTRACT = 'sc.research.finding-claim-evidence.v1';
    const VALIDATION_CHALLENGE_CONTRACT = 'sc.research.validation-challenge.v1';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01080/research-intelligence/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01080/research-intelligence/manifest', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01080/research-intelligence/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }

    private static function file_state($relative) {
        $path=SC_LAB_DIR.$relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }

    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,
            'version'=>self::VERSION,
            'bridgeSchema'=>self::BRIDGE_SCHEMA,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'findingClaimEvidenceContract'=>self::FINDING_CLAIM_EVIDENCE_CONTRACT,
            'validationChallengeContract'=>self::VALIDATION_CHALLENGE_CONTRACT,
            'automaticCoreSubmission'=>false,
            'automaticScientificCertification'=>false,
        ));
    }

    public static function manifest() {
        return rest_ensure_response(array(
            'ok'=>true,
            'status'=>'findings-claims-evidence-validation-bridge-ready',
            'version'=>self::VERSION,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'productRef'=>self::PRODUCT_REF,
            'findingClaimEvidenceContract'=>self::FINDING_CLAIM_EVIDENCE_CONTRACT,
            'validationChallengeContract'=>self::VALIDATION_CHALLENGE_CONTRACT,
            'labRemainsScientificAuthority'=>true,
            'humanReviewBoundariesPreserved'=>true,
            'automaticCoreSubmission'=>false,
            'automaticClaimInference'=>false,
            'automaticEvidenceJudgment'=>false,
            'automaticContradictionResolution'=>false,
            'automaticReplicationCertification'=>false,
            'scientificValidityCertifiedByBridge'=>false,
            'truthDeterminedByBridge'=>false,
            'visualReasoningScientificSceneBridgeDeferredTo'=>'0.109.0',
        ));
    }

    public static function health() {
        $required=array(
            'contracts/platform-core-v3-findings-validation-v01080.schema.json',
            'contracts/platform-core-v3-findings-validation-policy-v01080.json',
            'includes/class-sc-lab-platform-core-v3-findings-validation-v01080.php'
        );
        $files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'platform-core-v3-findings-claims-evidence-validation-ready':'incomplete',
            'version'=>self::VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'productRef'=>self::PRODUCT_REF,
            'findingClaimEvidenceContract'=>self::FINDING_CLAIM_EVIDENCE_CONTRACT,
            'validationChallengeContract'=>self::VALIDATION_CHALLENGE_CONTRACT,
            'automaticCoreSubmission'=>false,
            'automaticScientificCertification'=>false,
            'files'=>$files,
            'time'=>gmdate('c')
        ));
    }
}
SC_Lab_Platform_Core_V3_Findings_Validation_V01080::init();
