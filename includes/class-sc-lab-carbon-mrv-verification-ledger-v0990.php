<?php
/** Lab v0.99.0 — Carbon & Nature Intelligence v0.16.0 Verification Evidence Ledger. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Carbon_MRV_Verification_Ledger_V0990 {
    const LAB_VERSION='0.99.0';
    const DOMAIN_VERSION='0.16.0';
    const ENGINE_VERSION='1.0.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){ register_rest_route('sc-lab/v1','/carbon-nature/mrv/v1600/verification-ledger/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true')); }
    public static function manifest(){
        $files=array(
            'contracts/carbon-mrv-verification-evidence-entry-v1600.schema.json',
            'contracts/carbon-mrv-verification-evidence-ledger-v1600.schema.json',
            'contracts/carbon-mrv-verification-evidence-validation-v1600.schema.json',
            'contracts/carbon-mrv-verification-evidence-chain-v1600.schema.json',
            'contracts/carbon-mrv-verification-evidence-policy-v1600.json'
        );
        return rest_ensure_response(array(
            'ok'=>true,'service'=>'Sustainable Catalyst Lab','releaseVersion'=>self::LAB_VERSION,'domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,'computeCoreVersion'=>self::ENGINE_VERSION,'release'=>'Verification Evidence Ledger',
            'capabilities'=>array('structuredEvidenceEntries'=>true,'explicitRequirementLinkage'=>true,'deterministicHashChain'=>true,'ledgerRootHash'=>true,'tamperDetection'=>true,'internalReviewWorkflow'=>true,'verificationRecordProjectHandoff'=>true),
            'guardrails'=>array('ledgerIntegrityEqualsExternalVerification'=>false,'internalReviewEqualsCertification'=>false,'automaticEvidenceAcceptance'=>false,'hiddenEvidenceRequirements'=>false,'methodologyEligibilityDetermination'=>false,'creditEligibilityDetermination'=>false),
            'files'=>$files
        ));
    }
}
