<?php
/** Sustainable Catalyst Lab v0.89.0 — Carbon & Nature Intelligence v0.6.0 Soil Organic Carbon Lab Foundation. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Soil_Organic_Carbon_V0890 {
    const LAB_VERSION = '0.89.0';
    const DOMAIN_VERSION = '0.6.0';
    const ENGINE_VERSION = '1.0.0';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/carbon-nature/soc/v0600/module', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'manifest'),
            'permission_callback' => '__return_true',
        ));
    }

    private static function file_state($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return array('exists'=>is_file($path), 'sha256'=>is_file($path) ? hash_file('sha256', $path) : null);
    }

    public static function manifest() {
        $required = array(
            'backend/app/soil_organic_carbon_v0890.py',
            'backend/tests/test_soil_organic_carbon_v0890.py',
            'assets/js/modules/soil-organic-carbon-v0890.js',
            'assets/css/sc-lab-soil-organic-carbon-v0890.css',
            'contracts/soc-layer-input-v0600.schema.json',
            'contracts/soc-profile-input-v0600.schema.json',
            'contracts/soc-profile-result-v0600.schema.json',
            'contracts/soc-project-packet-v0600.schema.json',
            'contracts/soc-foundation-policy-v0600.json',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok ? 'soil-organic-carbon-lab-foundation-ready' : 'incomplete',
            'domain'=>'Carbon & Nature Intelligence',
            'domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::LAB_VERSION,
            'computeCoreVersion'=>self::ENGINE_VERSION,
            'release'=>'Soil Organic Carbon Lab Foundation',
            'capabilities'=>array(
                'fixedDepthSOCStock'=>true,'socConcentrationNormalization'=>true,'bulkDensityNormalization'=>true,
                'depthNormalization'=>true,'coarseFragmentCorrection'=>true,'profileAggregation'=>true,
                'parcelAreaScaling'=>true,'projectPacketHandoff'=>true,'deterministicFingerprints'=>true,
            ),
            'guardrails'=>array(
                'equivalentSoilMassNotImplemented'=>true,'stockChangeNotInferred'=>true,'sequestrationRateNotInferred'=>true,
                'co2eNotInferred'=>true,'uncertaintyNotInferred'=>true,'methodologyNotSelectedAutomatically'=>true,
                'additionalityNotDetermined'=>true,'permanenceNotDetermined'=>true,'creditEligibilityNotDetermined'=>true,
                'verificationNotPerformed'=>true,
            ),
            'files'=>$files,
        ));
    }
}
