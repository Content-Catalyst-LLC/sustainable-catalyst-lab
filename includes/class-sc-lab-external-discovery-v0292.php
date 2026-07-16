<?php
/** Sustainable Catalyst Lab v0.29.2 External Scholarly and Data Discovery. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_External_Discovery_V0292 {
    const VERSION = '0.29.2';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
    }

    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('scholarly-discovery','external-discovery','source-discovery','literature-discovery','data-discovery','catalog-discovery') as $alias) {
            $aliases[$alias] = 'scholarly-discovery';
        }
        return $aliases;
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/discovery/v0292/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/discovery/v0292/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/discovery/v0292/providers', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'providers'),'permission_callback'=>'__return_true'));
    }

    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,'searchSchema'=>'sc-lab-external-discovery-search/0.29.2','candidateSchema'=>'sc-lab-scholarly-discovery-candidate/0.29.2',
            'importSchema'=>'sc-lab-discovery-source-import/0.29.2','collections'=>array('discoverySearches','discoveryCandidates','sourceImportBatches','openAccessLookups','libraryProfiles'),
            'importsInto'=>array('researchSources','datasets'),'links'=>array('evidenceRecords','researchProvenance','methodReviewRecords'),'storageMode'=>'browser-local-project-records','serverBackedRegistry'=>false
        ));
    }

    public static function providers() {
        $path = SC_LAB_DIR . 'contracts/external-discovery-policy-v0292.json';
        $decoded = is_file($path) ? json_decode((string) file_get_contents($path), true) : null;
        return rest_ensure_response(is_array($decoded) ? array_merge(array('ok'=>true), $decoded) : array('ok'=>false,'version'=>self::VERSION));
    }

    public static function health() {
        $required = array(
            'assets/js/modules/external-discovery-v0292.js','assets/css/sc-lab-external-discovery-v0292.css',
            'contracts/external-discovery-policy-v0292.json','contracts/external-discovery-search-v0292.schema.json',
            'contracts/scholarly-discovery-candidate-v0292.schema.json','contracts/discovery-source-import-v0292.schema.json'
        );
        $files=array(); $ok=true;
        foreach ($required as $relative) {
            $exists=is_file(SC_LAB_DIR.$relative); $ok=$ok&&$exists;
            $files[$relative]=array('exists'=>$exists,'sha256'=>$exists?hash_file('sha256',SC_LAB_DIR.$relative):null);
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,'release'=>SC_LAB_VERSION,
            'architecture'=>'allowlisted-external-discovery-with-project-source-imports','liveProviders'=>array('crossref','openalex','datacite'),
            'handoffs'=>array('worldcat','google-scholar','openurl'),'deduplication'=>true,'sourceImport'=>true,'arbitraryRemoteFetch'=>false,'files'=>$files,'time'=>gmdate('c')
        ));
    }
}
