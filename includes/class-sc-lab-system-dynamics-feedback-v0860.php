<?php
/** Sustainable Catalyst Lab v0.86.0 — System Dynamics, Feedback Loops & Stock-Flow Modeling. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_System_Dynamics_Feedback_V0860 {
    const VERSION='0.86.0';
    const ENGINE_VERSION='1.0.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){
        register_rest_route('sc-lab/v1','/modeling/v0860/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/modeling/v0860/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($r){$p=SC_LAB_DIR.ltrim((string)$r,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'engine'=>'system-dynamics',
        'modelSchema'=>'sc-lab-system-dynamics-model/0.86.0','causalLoopSchema'=>'sc-lab-causal-loop-model/0.86.0','simulationSchema'=>'sc-lab-stock-flow-simulation/0.86.0','leverageSchema'=>'sc-lab-system-leverage-analysis/0.86.0',
        'capabilities'=>array('causalLoopDiagrams'=>true,'reinforcingBalancingLoops'=>true,'explicitDelays'=>true,'stockFlowModels'=>true,'auxiliaryVariables'=>true,'safeEquationEvaluation'=>true,'eulerIntegration'=>true,'rk4Integration'=>true,'scenarioSimulation'=>true,'structuralLeverageAnalysis'=>true,'graphStudioHandoff'=>true,'provenanceFingerprinting'=>true),
        'boundaries'=>array('causalLinkInference'=>false,'automaticEquationGeneration'=>false,'automaticLeveragePointRanking'=>false,'paradigmInference'=>false,'hiddenDelays'=>false,'silentStockClamping'=>false,'automaticUnitConversion'=>false,'arbitraryCode'=>false)
    ));}
    public static function health(){
        $required=array('backend/app/system_dynamics_feedback_v0860.py','backend/tests/test_system_dynamics_feedback_v0860.py','assets/js/modules/system-dynamics-v0860.js','assets/css/sc-lab-system-dynamics-v0860.css','contracts/system-dynamics-model-v0860.schema.json','contracts/causal-loop-model-v0860.schema.json','contracts/stock-flow-simulation-v0860.schema.json','contracts/system-leverage-analysis-v0860.schema.json','contracts/system-dynamics-policy-v0860.json');
        $files=array();$ok=true;foreach($required as $r){$files[$r]=self::file_state($r);if(empty($files[$r]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'system-dynamics-feedback-stock-flow-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_COMPAT_VERSION')?SC_LAB_PLATFORM_COMPAT_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'engine'=>'system-dynamics',
            'causalLoopDiagrams'=>true,'stockFlowModels'=>true,'reinforcingBalancingLoops'=>true,'explicitDelays'=>true,'scenarioSimulation'=>true,'structuralLeverageAnalysis'=>true,'graphStudioHandoff'=>true,'v0850WebGL2Compatibility'=>true,'v0830ProvenanceCompatibility'=>true,
            'causalLinkInference'=>false,'automaticEquationGeneration'=>false,'automaticLeveragePointRanking'=>false,'paradigmInference'=>false,'hiddenDelays'=>false,'silentStockClamping'=>false,'automaticUnitConversion'=>false,'arbitraryCode'=>false,'files'=>$files
        ));
    }
}
