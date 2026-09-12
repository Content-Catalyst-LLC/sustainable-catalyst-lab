<?php
/** Lab v0.100.0 — Carbon & Nature Intelligence v0.17.0 MRV Reporting & Audit Packets. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Carbon_MRV_Reporting_V01000 {
    const LAB_VERSION='0.100.0';
    const DOMAIN_VERSION='0.17.0';
    const ENGINE_VERSION='1.0.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){ register_rest_route('sc-lab/v1','/carbon-nature/mrv/v1700/reporting/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true')); }
    public static function manifest(){
        $files=array(
            'contracts/carbon-mrv-report-v1700.schema.json',
            'contracts/carbon-mrv-report-validation-v1700.schema.json',
            'contracts/carbon-mrv-audit-packet-v1700.schema.json',
            'contracts/carbon-mrv-reporting-policy-v1700.json'
        );
        return rest_ensure_response(array(
            'ok'=>true,
            'service'=>'Sustainable Catalyst Lab',
            'releaseVersion'=>self::LAB_VERSION,
            'domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,
            'computeCoreVersion'=>self::ENGINE_VERSION,
            'release'=>'MRV Reporting & Audit Packets',
            'capabilities'=>array(
                'structuredMrvReports'=>true,
                'internalSectionCompleteness'=>true,
                'declaredMetricLineage'=>true,
                'verificationLedgerChainCheck'=>true,
                'auditPacketManifest'=>true,
                'artifactDigestIndex'=>true,
                'internalAuditPreparationReadiness'=>true,
                'verificationRecordProjectHandoff'=>true
            ),
            'guardrails'=>array(
                'internalReportReadinessEqualsExternalVerification'=>false,
                'auditPacketEqualsAuditorApproval'=>false,
                'methodologyComplianceDetermination'=>false,
                'creditEligibilityDetermination'=>false,
                'automaticMetricRecalculation'=>false,
                'hiddenExternalReportingRequirements'=>false
            ),
            'files'=>$files
        ));
    }
}
