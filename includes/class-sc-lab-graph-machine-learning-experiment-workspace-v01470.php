<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Machine_Learning_Experiment_Workspace_V01470 {
    const VERSION='0.147.0';
    const NS='sc-lab/v1';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route(self::NS,'/graph-machine-learning-experiment-workspace/v01470/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NS,'/graph-machine-learning-experiment-workspace/v01470/acceptance',array('methods'=>'GET','callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NS,'/graph-machine-learning-experiment-workspace/v01470/catalog',array('methods'=>'GET','callback'=>array(__CLASS__,'catalog'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'graphMachineLearningExperimentWorkspace'=>true,'api_route_count'=>65,'predecessorVersion'=>'0.146.0','workspaceExecutionAuthority'=>true,'workbenchPrototypeExecutionAuthority'=>true,'platformCoreCanonicalAuthority'=>true,'labExecutesGraphMLTraining'=>false,'labExecutesGraphMLInference'=>false,'candidatePredictionsRemainCandidates'=>true,'automaticRelationshipEstablishment'=>false,'automaticModelRanking'=>false,'automaticWinnerSelection'=>false,'automaticScientificValidity'=>false,'predictionIsEvidence'=>false)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'accepted'=>array('graphMLStudyObjectModel'=>true,'graphSpecificLeakageAudits'=>true,'linkPredictionCandidateObjects'=>true,'GNNExplanationObjects'=>true,'reproducibilityPackage'=>true),'scientificValidityCertified'=>false,'predictionIsEvidence'=>false)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'taskTypes'=>array('node-classification','edge-classification','graph-classification','node-regression','edge-regression','graph-regression','link-prediction','graph-anomaly-detection','node-anomaly-detection','edge-anomaly-detection','graph-embedding','node-embedding','edge-embedding','representation-learning','self-supervised','contrastive','other'),'modelFamilies'=>array('gcn','graphsage','gat','gin','rgcn','heterogeneous-gnn','temporal-gnn','graph-transformer','message-passing','graph-autoencoder','variational-graph-autoencoder','knowledge-graph-embedding','random-walk-embedding','spectral','matrix-factorization','hybrid','custom','other'),'automaticRelationshipEstablishment'=>false,'predictionIsEvidence'=>false)); }
}
SC_Lab_Graph_Machine_Learning_Experiment_Workspace_V01470::init();
