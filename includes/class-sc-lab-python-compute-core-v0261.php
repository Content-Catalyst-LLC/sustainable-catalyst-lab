<?php
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Python_Compute_Core_V0261 {
    const VERSION = '0.27.3';
    const NAMESPACE = 'sc-lab/v1';

    public static function init() {
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route(self::NAMESPACE, '/compute/core/health', array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/capabilities', array('methods'=>'GET','callback'=>array(__CLASS__,'capabilities'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/methods', array('methods'=>'GET','callback'=>array(__CLASS__,'methods'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/methods/(?P<method>[A-Za-z0-9._-]{1,128})', array('methods'=>'GET','callback'=>array(__CLASS__,'method'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/run', array('methods'=>'POST','callback'=>array(__CLASS__,'run'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/governance/health', array('methods'=>'GET','callback'=>array(__CLASS__,'governance_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/governance/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'governance_policies'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/governance/recommend', array('methods'=>'POST','callback'=>array(__CLASS__,'governance_recommend'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/governance/compare', array('methods'=>'POST','callback'=>array(__CLASS__,'governance_compare'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/visualization/health', array('methods'=>'GET','callback'=>array(__CLASS__,'visualization_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/visualization/profiles', array('methods'=>'GET','callback'=>array(__CLASS__,'visualization_profiles'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/visualization/spec', array('methods'=>'POST','callback'=>array(__CLASS__,'visualization_spec'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/visualization/csv', array('methods'=>'POST','callback'=>array(__CLASS__,'visualization_csv'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/datasets/health', array('methods'=>'GET','callback'=>array(__CLASS__,'dataset_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/datasets/profile', array('methods'=>'POST','callback'=>array(__CLASS__,'dataset_profile'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/reproducibility/health', array('methods'=>'GET','callback'=>array(__CLASS__,'reproducibility_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/reproducibility/environment', array('methods'=>'GET','callback'=>array(__CLASS__,'reproducibility_environment'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/reproducibility/manifest', array('methods'=>'POST','callback'=>array(__CLASS__,'reproducibility_manifest'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/reproducibility/verify', array('methods'=>'POST','callback'=>array(__CLASS__,'reproducibility_verify'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/reproducibility/compare', array('methods'=>'POST','callback'=>array(__CLASS__,'reproducibility_compare'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/research-quality/health', array('methods'=>'GET','callback'=>array(__CLASS__,'research_quality_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/research-quality/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'research_quality_policies'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/research-quality/reviews/normalize', array('methods'=>'POST','callback'=>array(__CLASS__,'research_quality_normalize'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/research-quality/reviews/evaluate', array('methods'=>'POST','callback'=>array(__CLASS__,'research_quality_evaluate'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/research-quality/reviews/verify', array('methods'=>'POST','callback'=>array(__CLASS__,'research_quality_verify'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/research-quality/reviews/compare', array('methods'=>'POST','callback'=>array(__CLASS__,'research_quality_compare'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/discovery/health', array('methods'=>'GET','callback'=>array(__CLASS__,'discovery_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/discovery/providers', array('methods'=>'GET','callback'=>array(__CLASS__,'discovery_providers'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/discovery/search', array('methods'=>'POST','callback'=>array(__CLASS__,'discovery_search'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/discovery/normalize', array('methods'=>'POST','callback'=>array(__CLASS__,'discovery_normalize'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/discovery/deduplicate', array('methods'=>'POST','callback'=>array(__CLASS__,'discovery_deduplicate'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/discovery/open-access', array('methods'=>'POST','callback'=>array(__CLASS__,'discovery_open_access'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/discovery/openurl', array('methods'=>'POST','callback'=>array(__CLASS__,'discovery_openurl'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/experiments/health', array('methods'=>'GET','callback'=>array(__CLASS__,'experiments_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/experiments/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'experiments_policies'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/experiments/protocols/normalize', array('methods'=>'POST','callback'=>array(__CLASS__,'experiments_protocol_normalize'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/experiments/protocols/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'experiments_protocol_validate'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/experiments/runs/build', array('methods'=>'POST','callback'=>array(__CLASS__,'experiments_run_build'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/experiments/runs/compare', array('methods'=>'POST','callback'=>array(__CLASS__,'experiments_runs_compare'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/experiments/reports/build', array('methods'=>'POST','callback'=>array(__CLASS__,'experiments_report_build'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/experiments/verify', array('methods'=>'POST','callback'=>array(__CLASS__,'experiments_verify'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/design-studies/health', array('methods'=>'GET','callback'=>array(__CLASS__,'design_studies_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/design-studies/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'design_studies_policies'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/design-studies/normalize', array('methods'=>'POST','callback'=>array(__CLASS__,'design_studies_normalize'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/design-studies/generate', array('methods'=>'POST','callback'=>array(__CLASS__,'design_studies_generate'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/design-studies/analyze', array('methods'=>'POST','callback'=>array(__CLASS__,'design_studies_analyze'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/design-studies/recommend', array('methods'=>'POST','callback'=>array(__CLASS__,'design_studies_recommend'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/design-studies/batches/build', array('methods'=>'POST','callback'=>array(__CLASS__,'design_studies_batch'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/design-studies/verify', array('methods'=>'POST','callback'=>array(__CLASS__,'design_studies_verify'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/model-calibration/health', array('methods'=>'GET','callback'=>array(__CLASS__,'model_calibration_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/model-calibration/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'model_calibration_policies'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/model-calibration/normalize', array('methods'=>'POST','callback'=>array(__CLASS__,'model_calibration_normalize'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/model-calibration/calibrate', array('methods'=>'POST','callback'=>array(__CLASS__,'model_calibration_calibrate'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/model-calibration/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'model_calibration_validate'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/model-calibration/compare', array('methods'=>'POST','callback'=>array(__CLASS__,'model_calibration_compare'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/model-calibration/reports/build', array('methods'=>'POST','callback'=>array(__CLASS__,'model_calibration_report'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/model-calibration/verify', array('methods'=>'POST','callback'=>array(__CLASS__,'model_calibration_verify'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/health', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_policies'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/workers', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_workers'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/workers/register', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_register'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/workers/(?P<worker>[A-Za-z0-9._-]{1,180})/heartbeat', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_heartbeat'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/route', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_route'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/contracts/build', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_contract_build'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/contracts/verify', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_contract_verify'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/queue/status', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_queue_status'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/queue/enqueue', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_queue_enqueue'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/leases', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_leases'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/leases/claim', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_lease_claim'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/leases/(?P<lease>[A-Za-z0-9._-]{1,180})/renew', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_lease_renew'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/leases/(?P<lease>[A-Za-z0-9._-]{1,180})/release', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_lease_release'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/recovery/run', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_recovery'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/history', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_history'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/operations/health', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_operations_health'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/operations/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_operations_policies'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/operations/metrics', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_operations_metrics'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/operations/diagnostics', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_operations_diagnostics'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/dead-letters', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_dead_letters'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/dead-letters/replay', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_dead_letters_replay'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/queue/(?P<queue>[A-Za-z0-9._-]{1,220})', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_queue_item'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/queue/(?P<queue>[A-Za-z0-9._-]{1,220})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'dispatcher_queue_timeline'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/queue/(?P<queue>[A-Za-z0-9._-]{1,220})/replay', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_queue_replay'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/dispatcher/queue/(?P<queue>[A-Za-z0-9._-]{1,220})/cancel', array('methods'=>'POST','callback'=>array(__CLASS__,'dispatcher_queue_cancel'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/worker-agent/health', array('methods'=>'GET','callback'=>array(__CLASS__,'worker_agent_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/worker-agent/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'worker_agent_policies'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/worker-agent/credentials/status', array('methods'=>'GET','callback'=>array(__CLASS__,'worker_agent_credentials_status'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/worker-agent/workers', array('methods'=>'GET','callback'=>array(__CLASS__,'worker_agent_workers'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/artifacts/health', array('methods'=>'GET','callback'=>array(__CLASS__,'artifact_health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/artifacts/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'artifact_policies'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/artifacts/list', array('methods'=>'GET','callback'=>array(__CLASS__,'artifact_list'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/artifacts/uploads', array('methods'=>'GET','callback'=>array(__CLASS__,'artifact_uploads'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/artifacts/cleanup', array('methods'=>'POST','callback'=>array(__CLASS__,'artifact_cleanup'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/health', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_health'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_policies'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_validate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/save', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_save'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/list', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_list'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/definitions/(?P<workflow>[A-Za-z0-9._-]{1,180})/runs', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_start'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_runs'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs/(?P<run>[A-Za-z0-9._-]{1,180})', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_run'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs/(?P<run>[A-Za-z0-9._-]{1,180})/reconcile', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_reconcile'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs/(?P<run>[A-Za-z0-9._-]{1,180})/cancel', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_cancel'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs/(?P<run>[A-Za-z0-9._-]{1,180})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_timeline'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs/(?P<run>[A-Za-z0-9._-]{1,180})/recovery-plan', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_recovery_plan'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs/(?P<run>[A-Za-z0-9._-]{1,180})/recover', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_recover'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs/(?P<run>[A-Za-z0-9._-]{1,180})/nodes/(?P<node>[A-Za-z0-9._-]{1,180})/restart', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_restart_node'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflows/runs/(?P<run>[A-Za-z0-9._-]{1,180})/nodes/(?P<node>[A-Za-z0-9._-]{1,180})/checkpoints', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_checkpoints'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_record_checkpoint'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/health', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_automation_health'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_automation_policies'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/schedules/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_automation_validate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/schedules', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_automation_schedules'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_automation_save'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/schedules/(?P<schedule>[A-Za-z0-9._-]{1,180})/trigger', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_automation_trigger'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/schedules/(?P<schedule>[A-Za-z0-9._-]{1,180})/enable', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_automation_enable'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/schedules/(?P<schedule>[A-Za-z0-9._-]{1,180})/disable', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_automation_disable'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/tick', array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_automation_tick'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/firings', array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_automation_firings'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/workflow-automation/events', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'workflow_automation_events'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'workflow_automation_ingest'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/health', array('methods'=>'GET','callback'=>array(__CLASS__,'experiment_campaign_health'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'experiment_campaign_policies'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_validate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'experiment_campaign_list'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_save'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/tick', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_tick'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})', array('methods'=>'GET','callback'=>array(__CLASS__,'experiment_campaign_get'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/start', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_start'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/pause', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_pause'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/resume', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_resume'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/advance', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_advance'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/reconcile', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_reconcile'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/cancel', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_cancel'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/observations', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_observe'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/surrogate', array('methods'=>'GET','callback'=>array(__CLASS__,'experiment_campaign_surrogate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/proposal-preview', array('methods'=>'POST','callback'=>array(__CLASS__,'experiment_campaign_proposal_preview'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/trials', array('methods'=>'GET','callback'=>array(__CLASS__,'experiment_campaign_trials'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/experiment-campaigns/(?P<campaign>[A-Za-z0-9._-]{1,180})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'experiment_campaign_timeline'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/health', array('methods'=>'GET','callback'=>array(__CLASS__,'closed_loop_health'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'closed_loop_policies'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_validate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'closed_loop_list'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_save'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/tick', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_tick'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})', array('methods'=>'GET','callback'=>array(__CLASS__,'closed_loop_get'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/start', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_start'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/pause', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_pause'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/resume', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_resume'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/reconcile', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_reconcile'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/cancel', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_cancel'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/emergency-stop', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_emergency_stop'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/commands/issue', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_issue'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/commands/(?P<command>[A-Za-z0-9._-]{1,220})/approve', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_approve'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/commands/(?P<command>[A-Za-z0-9._-]{1,220})/dispatch', array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_dispatch'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/measurements', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'closed_loop_measurements'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'closed_loop_measurement'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/closed-loop-campaigns/(?P<loop>[A-Za-z0-9._-]{1,180})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'closed_loop_timeline'),'permission_callback'=>array(__CLASS__,'operations_permission')));

        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/health', array('methods'=>'GET','callback'=>array(__CLASS__,'model_registry_health'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'model_registry_policies'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/environments/capture', array('methods'=>'POST','callback'=>array(__CLASS__,'model_registry_capture_environment'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/environments/compare', array('methods'=>'POST','callback'=>array(__CLASS__,'model_registry_compare_environment'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'model_registry_validate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/models', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'model_registry_list'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'model_registry_register'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/models/(?P<model>[A-Za-z0-9._-]{1,180})', array('methods'=>'GET','callback'=>array(__CLASS__,'model_registry_get'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/models/(?P<model>[A-Za-z0-9._-]{1,180})/(?P<version>[A-Za-z0-9.+-]{1,120})/promote', array('methods'=>'POST','callback'=>array(__CLASS__,'model_registry_promote'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/models/(?P<model>[A-Za-z0-9._-]{1,180})/(?P<version>[A-Za-z0-9.+-]{1,120})/deprecate', array('methods'=>'POST','callback'=>array(__CLASS__,'model_registry_deprecate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/models/(?P<model>[A-Za-z0-9._-]{1,180})/reproduction', array('methods'=>'GET','callback'=>array(__CLASS__,'model_registry_reproduction'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/models/(?P<model>[A-Za-z0-9._-]{1,180})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'model_registry_timeline'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/model-registry/reproduction/verify', array('methods'=>'POST','callback'=>array(__CLASS__,'model_registry_verify'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/health', array('methods'=>'GET','callback'=>array(__CLASS__,'ensemble_health'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'ensemble_policies'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'ensemble_validate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'ensemble_list'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'ensemble_create'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/(?P<study>[A-Za-z0-9._-]{1,180})', array('methods'=>'GET','callback'=>array(__CLASS__,'ensemble_get'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/(?P<study>[A-Za-z0-9._-]{1,180})/start', array('methods'=>'POST','callback'=>array(__CLASS__,'ensemble_start'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/(?P<study>[A-Za-z0-9._-]{1,180})/reconcile', array('methods'=>'POST','callback'=>array(__CLASS__,'ensemble_reconcile'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/(?P<study>[A-Za-z0-9._-]{1,180})/cancel', array('methods'=>'POST','callback'=>array(__CLASS__,'ensemble_cancel'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/(?P<study>[A-Za-z0-9._-]{1,180})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'ensemble_timeline'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/ensemble-studies/(?P<study>[A-Za-z0-9._-]{1,180})/evaluations/(?P<evaluation>[A-Za-z0-9._-]{1,220})/result', array('methods'=>'POST','callback'=>array(__CLASS__,'ensemble_record_result'),'permission_callback'=>array(__CLASS__,'operations_permission')));

        register_rest_route(self::NAMESPACE, '/compute/core/surrogate-rom/health', array('methods'=>'GET','callback'=>array(__CLASS__,'surrogate_rom_health'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/surrogate-rom/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'surrogate_rom_policies'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/surrogate-rom/validate', array('methods'=>'POST','callback'=>array(__CLASS__,'surrogate_rom_validate'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/surrogate-rom/studies', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'surrogate_rom_list'),'permission_callback'=>array(__CLASS__,'operations_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'surrogate_rom_train'),'permission_callback'=>array(__CLASS__,'operations_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/surrogate-rom/studies/(?P<study>[A-Za-z0-9._-]{1,180})', array('methods'=>'GET','callback'=>array(__CLASS__,'surrogate_rom_get'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/surrogate-rom/studies/(?P<study>[A-Za-z0-9._-]{1,180})/predict', array('methods'=>'POST','callback'=>array(__CLASS__,'surrogate_rom_predict'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/surrogate-rom/studies/(?P<study>[A-Za-z0-9._-]{1,180})/register', array('methods'=>'POST','callback'=>array(__CLASS__,'surrogate_rom_register'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/surrogate-rom/studies/(?P<study>[A-Za-z0-9._-]{1,180})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'surrogate_rom_timeline'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/health', array('methods'=>'GET','callback'=>array(__CLASS__,'team_workspace_health'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/policies', array('methods'=>'GET','callback'=>array(__CLASS__,'team_workspace_policies'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'team_workspace_list'),'permission_callback'=>array(__CLASS__,'collaboration_permission')),
            array('methods'=>'POST','callback'=>array(__CLASS__,'team_workspace_create'),'permission_callback'=>array(__CLASS__,'collaboration_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/invitations/accept', array('methods'=>'POST','callback'=>array(__CLASS__,'team_workspace_accept'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'team_workspace_get'),'permission_callback'=>array(__CLASS__,'collaboration_permission')),
            array('methods'=>'PATCH','callback'=>array(__CLASS__,'team_workspace_update'),'permission_callback'=>array(__CLASS__,'collaboration_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})/archive', array('methods'=>'POST','callback'=>array(__CLASS__,'team_workspace_archive'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})/invitations', array('methods'=>'POST','callback'=>array(__CLASS__,'team_workspace_invite'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})/members/(?P<member>[A-Za-z0-9._:-]{1,180})', array(
            array('methods'=>'PATCH','callback'=>array(__CLASS__,'team_workspace_member_role'),'permission_callback'=>array(__CLASS__,'collaboration_permission')),
            array('methods'=>'DELETE','callback'=>array(__CLASS__,'team_workspace_remove_member'),'permission_callback'=>array(__CLASS__,'collaboration_permission')),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})/ownership', array('methods'=>'POST','callback'=>array(__CLASS__,'team_workspace_transfer'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})/resources', array('methods'=>'POST','callback'=>array(__CLASS__,'team_workspace_link_resource'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})/resources/(?P<link>[A-Za-z0-9._:-]{1,180})', array('methods'=>'DELETE','callback'=>array(__CLASS__,'team_workspace_unlink_resource'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})/authorize', array('methods'=>'POST','callback'=>array(__CLASS__,'team_workspace_authorize'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));
        register_rest_route(self::NAMESPACE, '/compute/core/team-workspaces/(?P<workspace>[A-Za-z0-9._:-]{1,180})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'team_workspace_timeline'),'permission_callback'=>array(__CLASS__,'collaboration_permission')));

        register_rest_route(self::NAMESPACE, '/compute/core/jobs', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'jobs_list'),'permission_callback'=>'__return_true'),
            array('methods'=>'POST','callback'=>array(__CLASS__,'job_create'),'permission_callback'=>'__return_true'),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'job_status'),'permission_callback'=>'__return_true'),
            array('methods'=>'DELETE','callback'=>array(__CLASS__,'job_cancel'),'permission_callback'=>'__return_true'),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/cancel', array('methods'=>'POST','callback'=>array(__CLASS__,'job_cancel_post'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/retry', array('methods'=>'POST','callback'=>array(__CLASS__,'job_retry'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/pause', array('methods'=>'POST','callback'=>array(__CLASS__,'job_pause'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/resume', array('methods'=>'POST','callback'=>array(__CLASS__,'job_resume'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/checkpoints', array('methods'=>'GET','callback'=>array(__CLASS__,'job_checkpoints'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/cache/status', array('methods'=>'GET','callback'=>array(__CLASS__,'cache_status'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/cache', array('methods'=>'DELETE','callback'=>array(__CLASS__,'cache_purge'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/workers', array('methods'=>'GET','callback'=>array(__CLASS__,'workers'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/queue/status', array('methods'=>'GET','callback'=>array(__CLASS__,'queue_status'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks', array('methods'=>'GET','callback'=>array(__CLASS__,'benchmarks'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks/(?P<benchmark>[A-Za-z0-9._-]{1,128})', array('methods'=>'GET','callback'=>array(__CLASS__,'benchmark'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks/run', array('methods'=>'POST','callback'=>array(__CLASS__,'benchmark_run'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks/run-suite', array('methods'=>'POST','callback'=>array(__CLASS__,'benchmark_suite'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks/convergence', array('methods'=>'POST','callback'=>array(__CLASS__,'benchmark_convergence'),'permission_callback'=>'__return_true'));
    }

    private static function settings() {
        return wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
    }

    private static function rate_limit() {
        $ip = isset($_SERVER['REMOTE_ADDR']) ? sanitize_text_field(wp_unslash($_SERVER['REMOTE_ADDR'])) : 'unknown';
        $key = 'sc_lab_core_rate_' . md5($ip . gmdate('YmdHi'));
        $count = (int) get_transient($key);
        if ($count >= 120) { return new WP_Error('compute_rate_limited','Too many Python Compute Core requests. Try again in a minute.',array('status'=>429)); }
        set_transient($key, $count + 1, 2 * MINUTE_IN_SECONDS);
        return true;
    }

    public static function signed_headers($path, $method, $body, $settings = null) {
        $settings = is_array($settings) ? $settings : self::settings();
        $headers = array('Accept'=>'application/json','Content-Type'=>'application/json','X-SC-Lab-Client'=>isset($settings['compute_client_id']) ? $settings['compute_client_id'] : 'sustainable-catalyst-wordpress');
        $user = function_exists('wp_get_current_user') ? wp_get_current_user() : null;
        $actor_id = ($user && !empty($user->ID)) ? 'wp-user-' . absint($user->ID) : 'wordpress-system';
        $actor_name = ($user && !empty($user->display_name)) ? sanitize_text_field($user->display_name) : 'WordPress system';
        $headers['X-SC-Lab-Actor'] = $actor_id;
        $headers['X-SC-Lab-Actor-Name'] = $actor_name;
        if (!empty($settings['compute_api_key'])) { $headers['X-SC-Lab-Key'] = $settings['compute_api_key']; }
        if (!empty($settings['compute_signing_secret'])) {
            $timestamp = (string) time();
            $digest = hash('sha256', (string) $body);
            $canonical = $timestamp . "\n" . strtoupper($method) . "\n" . $path . "\n" . $digest;
            $headers['X-SC-Lab-Timestamp'] = $timestamp;
            $headers['X-SC-Lab-Signature'] = hash_hmac('sha256', $canonical, $settings['compute_signing_secret']);
        }
        return $headers;
    }

    private static function proxy($path, $method = 'GET', $payload = null, $limit = 2097152, $signature_path = null) {
        $limited = self::rate_limit(); if (is_wp_error($limited)) { return $limited; }
        $settings = self::settings();
        if (empty($settings['enable_remote_compute']) || empty($settings['compute_backend_url'])) { return new WP_Error('compute_disabled','The Python Compute Core is not enabled or configured.',array('status'=>503)); }
        $body = null === $payload ? '' : wp_json_encode($payload);
        $url = untrailingslashit($settings['compute_backend_url']) . $path;
        $args = array('method'=>$method,'timeout'=>max(5,min(120,absint($settings['compute_timeout_seconds']))),'redirection'=>2,'sslverify'=>!empty($settings['compute_verify_ssl']),'headers'=>self::signed_headers($signature_path ? $signature_path : $path,$method,$body,$settings),'limit_response_size'=>max(262144,min(8388608,absint($limit))));
        if (null !== $payload) { $args['body']=$body; }
        $response = wp_safe_remote_request($url,$args);
        if (is_wp_error($response)) { return new WP_Error('python_compute_unavailable',$response->get_error_message(),array('status'=>502)); }
        $status=wp_remote_retrieve_response_code($response); $decoded=json_decode(wp_remote_retrieve_body($response),true);
        if (!is_array($decoded)) { $decoded=array('detail'=>'The Python Compute Core returned an invalid JSON response.'); $status=502; }
        return new WP_REST_Response($decoded,$status);
    }

    private static function sanitize_tree($value, $depth = 0, &$nodes = 0, $max_nodes = 5000, $max_depth = 10) {
        $nodes++;
        if ($nodes > $max_nodes || $depth > $max_depth) { return new WP_Error('compute_payload_too_complex','The compute payload is too complex.',array('status'=>422)); }
        if (is_null($value) || is_bool($value)) { return $value; }
        if (is_int($value) || is_float($value)) { return is_finite((float)$value) ? $value : null; }
        if (is_string($value)) { return substr(wp_strip_all_tags($value,true),0,2048); }
        if (!is_array($value)) { return null; }
        if (count($value) > 100000) { return new WP_Error('compute_array_too_large','A compute array exceeds the 100,000-item foundation limit.',array('status'=>422)); }
        $clean=array();
        foreach ($value as $key=>$item) {
            $clean_key=is_int($key)?$key:substr(preg_replace('/[^A-Za-z0-9._-]/','',(string)$key),0,128);
            if ($clean_key==='') { continue; }
            $child=self::sanitize_tree($item,$depth+1,$nodes,$max_nodes,$max_depth); if(is_wp_error($child)){return $child;} $clean[$clean_key]=$child;
        }
        return $clean;
    }

    private static function clean_governance($value) {
        $value=is_array($value)?$value:array(); $out=array();
        $allowed_profiles=array('fast','balanced','strict','diagnostic'); $profile=isset($value['precisionProfile'])?sanitize_key($value['precisionProfile']):'balanced'; $out['precisionProfile']=in_array($profile,$allowed_profiles,true)?$profile:'balanced';
        $solver_policy=isset($value['solverPolicy'])?sanitize_key($value['solverPolicy']):'automatic'; $out['solverPolicy']=in_array($solver_policy,array('automatic','recommended','manual'),true)?$solver_policy:'automatic';
        if(!empty($value['requestedSolver'])){$out['requestedSolver']=substr(sanitize_text_field($value['requestedSolver']),0,64);}
        $unit_policy=isset($value['unitPolicy'])?sanitize_key($value['unitPolicy']):'warn'; $out['unitPolicy']=in_array($unit_policy,array('off','warn','strict'),true)?$unit_policy:'warn';
        $ill=isset($value['illConditionedPolicy'])?sanitize_key($value['illConditionedPolicy']):'least-squares'; $out['illConditionedPolicy']=in_array($ill,array('reject','warn','least-squares'),true)?$ill:'least-squares';
        if(isset($value['conditionThreshold'])&&is_numeric($value['conditionThreshold'])){$out['conditionThreshold']=max(1.0,(float)$value['conditionThreshold']);}
        if(isset($value['absoluteTolerance'])&&is_numeric($value['absoluteTolerance'])){$out['absoluteTolerance']=max(1e-15,min(1e-2,(float)$value['absoluteTolerance']));}
        if(isset($value['relativeTolerance'])&&is_numeric($value['relativeTolerance'])){$out['relativeTolerance']=max(1e-15,min(1e-2,(float)$value['relativeTolerance']));}
        $out['referenceComparison']=!empty($value['referenceComparison']);
        $standard=isset($value['uncertaintyStandard'])?sanitize_text_field($value['uncertaintyStandard']):'method-default'; $out['uncertaintyStandard']=in_array($standard,array('method-default','GUM-inspired','Monte-Carlo','bootstrap'),true)?$standard:'method-default';
        return $out;
    }

    public static function operations_permission() {
        return current_user_can('manage_options');
    }

    public static function collaboration_permission() {
        return is_user_logged_in();
    }

    public static function health() { return self::proxy('/health'); }
    public static function capabilities() { return self::proxy('/v1/capabilities'); }
    public static function methods() { return self::proxy('/v1/methods'); }
    public static function method(WP_REST_Request $request) { return self::proxy('/v1/methods/' . rawurlencode(sanitize_text_field($request['method']))); }
    public static function run(WP_REST_Request $request) {
        $body=$request->get_json_params(); if(!is_array($body)){return new WP_Error('invalid_compute_request','A JSON compute request is required.',array('status'=>422));}
        $method=isset($body['method'])?preg_replace('/[^A-Za-z0-9._-]/','',(string)$body['method']):'';
        if($method===''){return new WP_Error('invalid_compute_method','A registered method identifier is required.',array('status'=>422));}
        $nodes=0; $inputs=self::sanitize_tree(isset($body['inputs'])?$body['inputs']:array(),0,$nodes); if(is_wp_error($inputs)){return $inputs;}
        $nodes=0; $parameters=self::sanitize_tree(isset($body['parameters'])?$body['parameters']:array(),0,$nodes); if(is_wp_error($parameters)){return $parameters;}
        $payload=array('method'=>$method,'inputs'=>$inputs,'parameters'=>$parameters,'units'=>isset($body['units'])&&is_array($body['units'])?array_map('sanitize_text_field',$body['units']):array(),'project_id'=>isset($body['project_id'])?sanitize_text_field($body['project_id']):null,'requested_outputs'=>isset($body['requested_outputs'])&&is_array($body['requested_outputs'])?array_slice(array_map('sanitize_key',$body['requested_outputs']),0,16):array('summary','values'),'execution_target'=>'automatic');
        if(isset($body['version'])){$payload['version']=sanitize_text_field($body['version']);}
        if(isset($body['random_seed'])&&is_numeric($body['random_seed'])){$payload['random_seed']=(int)$body['random_seed'];}
        $payload['governance']=self::clean_governance(isset($body['governance'])?$body['governance']:array());
        return self::proxy('/v1/compute/run','POST',$payload,4194304);
    }

    private static function clean_job_request($body) {
        if (!is_array($body)) { return new WP_Error('invalid_compute_job','A JSON compute job request is required.',array('status'=>422)); }
        $source = isset($body['request']) && is_array($body['request']) ? $body['request'] : (isset($body['execute']) && is_array($body['execute']) ? $body['execute'] : $body);
        $method = isset($source['method']) ? preg_replace('/[^A-Za-z0-9._-]/','',(string)$source['method']) : (isset($source['methodId']) ? preg_replace('/[^A-Za-z0-9._-]/','',(string)$source['methodId']) : '');
        if ($method === '') { return new WP_Error('invalid_compute_method','A registered method identifier is required.',array('status'=>422)); }
        $nodes=0; $inputs=self::sanitize_tree(isset($source['inputs'])?$source['inputs']:array(),0,$nodes); if(is_wp_error($inputs)){return $inputs;}
        $nodes=0; $parameters=self::sanitize_tree(isset($source['parameters'])?$source['parameters']:array(),0,$nodes); if(is_wp_error($parameters)){return $parameters;}
        $request=array(
            'method'=>$method,
            'inputs'=>$inputs,
            'parameters'=>$parameters,
            'units'=>isset($source['units'])&&is_array($source['units'])?array_map('sanitize_text_field',$source['units']):array(),
            'project_id'=>isset($source['project_id'])?sanitize_text_field($source['project_id']):(isset($source['projectId'])?sanitize_text_field($source['projectId']):null),
            'requested_outputs'=>isset($source['requested_outputs'])&&is_array($source['requested_outputs'])?array_slice(array_map('sanitize_key',$source['requested_outputs']),0,16):array('summary','values'),
            'execution_target'=>'automatic',
        );
        if(isset($source['version'])){$request['version']=sanitize_text_field($source['version']);}
        if(isset($source['random_seed'])&&is_numeric($source['random_seed'])){$request['random_seed']=(int)$source['random_seed'];}
        if(isset($source['randomSeed'])&&is_numeric($source['randomSeed'])){$request['random_seed']=(int)$source['randomSeed'];}
        $request['governance']=self::clean_governance(isset($source['governance'])?$source['governance']:array());
        $payload=array('operation'=>'core_run','request'=>$request);
        if(isset($body['idempotencyKey'])){$payload['idempotencyKey']=substr(sanitize_text_field($body['idempotencyKey']),0,128);}
        if(isset($body['timeoutSeconds'])){$payload['timeoutSeconds']=max(1,min(900,absint($body['timeoutSeconds'])));}
        if(isset($body['maxAttempts'])){$payload['maxAttempts']=max(1,min(5,absint($body['maxAttempts'])));}
        if(isset($body['priority'])){$payload['priority']=max(0,min(100,absint($body['priority'])));}
        if(isset($body['cacheMode'])){
            $cache_mode=sanitize_key($body['cacheMode']);
            $payload['cacheMode']=in_array($cache_mode,array('use','refresh','bypass'),true)?$cache_mode:'use';
        }
        return $payload;
    }

    public static function jobs_list(WP_REST_Request $request) {
        $query=array();
        if($request->get_param('status')){$query['status']=sanitize_key($request->get_param('status'));}
        if($request->get_param('project_id')){$query['project_id']=sanitize_text_field($request->get_param('project_id'));}
        $query['limit']=max(1,min(200,absint($request->get_param('limit')?:50)));
        $query['offset']=max(0,absint($request->get_param('offset')?:0));
        return self::proxy('/v1/jobs?' . http_build_query($query,'','&'),'GET',null,4194304,'/v1/jobs');
    }
    public static function job_create(WP_REST_Request $request) {
        $payload=self::clean_job_request($request->get_json_params());
        return is_wp_error($payload)?$payload:self::proxy('/v1/jobs','POST',$payload,4194304);
    }
    public static function job_status(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job'])); }
    public static function job_cancel(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job']),'DELETE'); }
    public static function job_cancel_post(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job']) . '/cancel','POST',array()); }
    public static function job_retry(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job']) . '/retry','POST',array()); }
    public static function job_pause(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job']) . '/pause','POST',array()); }
    public static function job_resume(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job']) . '/resume','POST',array()); }
    public static function job_checkpoints(WP_REST_Request $request) {
        $limit=max(1,min(200,absint($request->get_param('limit')?:20)));
        return self::proxy('/v1/jobs/' . rawurlencode($request['job']) . '/checkpoints?limit=' . $limit,'GET',null,8388608,'/v1/jobs/' . rawurlencode($request['job']) . '/checkpoints');
    }
    public static function cache_status() { return self::proxy('/v1/cache/status'); }
    public static function cache_purge() { return self::proxy('/v1/cache','DELETE'); }
    public static function workers() { return self::proxy('/v1/workers'); }
    public static function queue_status() { return self::proxy('/v1/queue/status'); }
    public static function benchmarks() { return self::proxy('/v1/benchmarks'); }
    public static function benchmark(WP_REST_Request $request) {
        $id = preg_replace('/[^A-Za-z0-9._-]/', '', (string)$request['benchmark']);
        return self::proxy('/v1/benchmarks/' . rawurlencode($id));
    }
    private static function benchmark_payload(WP_REST_Request $request, $suite = false) {
        $body = $request->get_json_params();
        $body = is_array($body) ? $body : array();
        if ($suite) {
            $ids = isset($body['benchmarkIds']) && is_array($body['benchmarkIds']) ? array_slice($body['benchmarkIds'], 0, 100) : array();
            return array('benchmarkIds'=>array_values(array_filter(array_map(function($id){ return preg_replace('/[^A-Za-z0-9._-]/','',(string)$id); }, $ids))));
        }
        $id = isset($body['benchmarkId']) ? preg_replace('/[^A-Za-z0-9._-]/','',(string)$body['benchmarkId']) : '';
        if ($id === '') { return new WP_Error('invalid_benchmark','A benchmarkId is required.',array('status'=>422)); }
        return array('benchmarkId'=>$id);
    }
    public static function benchmark_run(WP_REST_Request $request) {
        $payload=self::benchmark_payload($request); if(is_wp_error($payload)){return $payload;}
        return self::proxy('/v1/benchmarks/run','POST',$payload,8388608);
    }
    public static function benchmark_suite(WP_REST_Request $request) {
        $payload=self::benchmark_payload($request,true); if(is_wp_error($payload)){return $payload;}
        return self::proxy('/v1/benchmarks/run-suite','POST',$payload,8388608);
    }
    public static function benchmark_convergence(WP_REST_Request $request) {
        $payload=self::benchmark_payload($request); if(is_wp_error($payload)){return $payload;}
        return self::proxy('/v1/benchmarks/convergence','POST',$payload,8388608);
    }

    public static function governance_health() { return self::proxy('/v1/governance/health'); }
    public static function governance_policies() { return self::proxy('/v1/governance/policies'); }
    private static function governance_payload(WP_REST_Request $request) {
        $body=$request->get_json_params(); if(!is_array($body)){return new WP_Error('invalid_governance_request','A JSON compute request is required.',array('status'=>422));}
        $method=isset($body['method'])?preg_replace('/[^A-Za-z0-9._-]/','',(string)$body['method']):''; if($method===''){return new WP_Error('invalid_compute_method','A registered method identifier is required.',array('status'=>422));}
        $nodes=0;$inputs=self::sanitize_tree(isset($body['inputs'])?$body['inputs']:array(),0,$nodes);if(is_wp_error($inputs)){return $inputs;} $nodes=0;$parameters=self::sanitize_tree(isset($body['parameters'])?$body['parameters']:array(),0,$nodes);if(is_wp_error($parameters)){return $parameters;}
        return array('method'=>$method,'inputs'=>$inputs,'parameters'=>$parameters,'units'=>isset($body['units'])&&is_array($body['units'])?array_map('sanitize_text_field',$body['units']):array(),'governance'=>self::clean_governance(isset($body['governance'])?$body['governance']:array()),'project_id'=>isset($body['project_id'])?sanitize_text_field($body['project_id']):null,'requested_outputs'=>array('summary','values'),'execution_target'=>'automatic','random_seed'=>isset($body['random_seed'])&&is_numeric($body['random_seed'])?(int)$body['random_seed']:42);
    }
    public static function governance_recommend(WP_REST_Request $request){$payload=self::governance_payload($request);return is_wp_error($payload)?$payload:self::proxy('/v1/governance/recommend','POST',$payload,4194304);}
    public static function governance_compare(WP_REST_Request $request){$payload=self::governance_payload($request);return is_wp_error($payload)?$payload:self::proxy('/v1/governance/compare','POST',$payload,8388608);}
    public static function visualization_health(){return self::proxy('/v1/visualization/health');}
    public static function visualization_profiles(){return self::proxy('/v1/visualization/profiles');}
    private static function visualization_payload(WP_REST_Request $request){$body=$request->get_json_params();if(!is_array($body)){return new WP_Error('invalid_visualization_request','A JSON visualization request is required.',array('status'=>422));}$method=isset($body['method'])?sanitize_text_field($body['method']):'';$outputs=isset($body['outputs'])&&is_array($body['outputs'])?$body['outputs']:array();$visualization=isset($body['visualization'])&&is_array($body['visualization'])?$body['visualization']:array();return array('method'=>$method,'outputs'=>$outputs,'visualization'=>$visualization);}
    public static function visualization_spec(WP_REST_Request $request){$payload=self::visualization_payload($request);return is_wp_error($payload)?$payload:self::proxy('/v1/visualization/spec','POST',$payload,8388608);}
    public static function visualization_csv(WP_REST_Request $request){$payload=self::visualization_payload($request);return is_wp_error($payload)?$payload:self::proxy('/v1/visualization/csv','POST',$payload,8388608);}
    public static function dataset_health(){return self::proxy('/v1/datasets/health');}
    public static function dataset_profile(WP_REST_Request $request){$body=$request->get_json_params();if(!is_array($body)){return new WP_Error('invalid_dataset_profile','A JSON dataset profile request is required.',array('status'=>422));}$nodes=0;$clean=self::sanitize_tree($body,0,$nodes);if(is_wp_error($clean)){return $clean;}if(isset($clean['rows'])&&is_array($clean['rows'])){$clean['rows']=array_slice($clean['rows'],0,5000);}return self::proxy('/v1/datasets/profile','POST',$clean,8388608);}
    public static function reproducibility_health(){return self::proxy('/v1/reproducibility/health');}
    public static function reproducibility_environment(){return self::proxy('/v1/reproducibility/environment');}
    private static function reproducibility_payload(WP_REST_Request $request){$body=$request->get_json_params();if(!is_array($body)){return new WP_Error('invalid_reproducibility_payload','A JSON reproducibility payload is required.',array('status'=>422));}$nodes=0;$clean=self::sanitize_tree($body,0,$nodes);return is_wp_error($clean)?$clean:$clean;}
    public static function reproducibility_manifest(WP_REST_Request $request){$p=self::reproducibility_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/reproducibility/manifest','POST',$p,8388608);}
    public static function reproducibility_verify(WP_REST_Request $request){$p=self::reproducibility_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/reproducibility/verify','POST',$p,8388608);}
    public static function reproducibility_compare(WP_REST_Request $request){$p=self::reproducibility_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/reproducibility/compare','POST',$p,8388608);}

    public static function research_quality_health(){return self::proxy('/v1/research-quality/health');}
    public static function research_quality_policies(){return self::proxy('/v1/research-quality/policies');}
    private static function research_quality_payload(WP_REST_Request $request){$body=$request->get_json_params();if(!is_array($body)){return new WP_Error('invalid_research_quality_payload','A JSON method-review payload is required.',array('status'=>422));}$nodes=0;$clean=self::sanitize_tree($body,0,$nodes);return is_wp_error($clean)?$clean:$clean;}
    public static function research_quality_normalize(WP_REST_Request $request){$p=self::research_quality_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/research-quality/reviews/normalize','POST',$p,8388608);}
    public static function research_quality_evaluate(WP_REST_Request $request){$p=self::research_quality_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/research-quality/reviews/evaluate','POST',$p,8388608);}
    public static function research_quality_verify(WP_REST_Request $request){$p=self::research_quality_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/research-quality/reviews/verify','POST',$p,8388608);}
    public static function research_quality_compare(WP_REST_Request $request){$p=self::research_quality_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/research-quality/reviews/compare','POST',$p,8388608);}

    public static function discovery_health(){return self::proxy('/v1/discovery/health');}
    public static function discovery_providers(){return self::proxy('/v1/discovery/providers');}
    private static function discovery_payload(WP_REST_Request $request){
        $body=$request->get_json_params(); if(!is_array($body)){return new WP_Error('invalid_discovery_payload','A JSON discovery payload is required.',array('status'=>422));}
        $nodes=0; $clean=self::sanitize_tree($body,0,$nodes); if(is_wp_error($clean)){return $clean;}
        if(isset($clean['query'])){$clean['query']=substr(sanitize_text_field((string)$clean['query']),0,500);}
        if(isset($clean['providers'])&&is_array($clean['providers'])){$allowed=array('crossref','openalex','datacite');$clean['providers']=array_values(array_intersect($allowed,array_map('sanitize_key',array_slice($clean['providers'],0,3))));}
        if(isset($clean['maxResults'])){$clean['maxResults']=max(1,min(25,absint($clean['maxResults'])));}
        if(isset($clean['candidates'])&&is_array($clean['candidates'])){$clean['candidates']=array_slice($clean['candidates'],0,500);}
        return $clean;
    }
    public static function discovery_search(WP_REST_Request $request){$p=self::discovery_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/discovery/search','POST',$p,8388608);}
    public static function discovery_normalize(WP_REST_Request $request){$p=self::discovery_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/discovery/normalize','POST',$p,8388608);}
    public static function discovery_deduplicate(WP_REST_Request $request){$p=self::discovery_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/discovery/deduplicate','POST',$p,8388608);}
    public static function discovery_open_access(WP_REST_Request $request){$p=self::discovery_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/discovery/open-access','POST',$p,8388608);}
    public static function discovery_openurl(WP_REST_Request $request){$p=self::discovery_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/discovery/openurl','POST',$p,8388608);}

    public static function experiments_health(){return self::proxy('/v1/experiments/health');}
    public static function experiments_policies(){return self::proxy('/v1/experiments/policies');}
    private static function experiments_payload(WP_REST_Request $request){$body=$request->get_json_params();if(!is_array($body)){return new WP_Error('invalid_experiment_payload','A JSON experiment payload is required.',array('status'=>422));}$nodes=0;$clean=self::sanitize_tree($body,0,$nodes);if(is_wp_error($clean)){return $clean;}return $clean;}
    public static function experiments_protocol_normalize(WP_REST_Request $request){$p=self::experiments_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiments/protocols/normalize','POST',$p,8388608);}
    public static function experiments_protocol_validate(WP_REST_Request $request){$p=self::experiments_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiments/protocols/validate','POST',$p,8388608);}
    public static function experiments_run_build(WP_REST_Request $request){$p=self::experiments_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiments/runs/build','POST',$p,8388608);}
    public static function experiments_runs_compare(WP_REST_Request $request){$p=self::experiments_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiments/runs/compare','POST',$p,8388608);}
    public static function experiments_report_build(WP_REST_Request $request){$p=self::experiments_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiments/reports/build','POST',$p,8388608);}
    public static function experiments_verify(WP_REST_Request $request){$p=self::experiments_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiments/verify','POST',$p,8388608);}

    public static function design_studies_health(){return self::proxy('/v1/design-studies/health');}
    public static function design_studies_policies(){return self::proxy('/v1/design-studies/policies');}
    private static function design_studies_payload(WP_REST_Request $request){$body=$request->get_json_params();if(!is_array($body)){return new WP_Error('invalid_design_study_payload','A JSON design-study payload is required.',array('status'=>422));}$nodes=0;$clean=self::sanitize_tree($body,0,$nodes);if(is_wp_error($clean)){return $clean;}return $clean;}
    public static function design_studies_normalize(WP_REST_Request $request){$p=self::design_studies_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/design-studies/normalize','POST',$p,8388608);}
    public static function design_studies_generate(WP_REST_Request $request){$p=self::design_studies_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/design-studies/generate','POST',$p,8388608);}
    public static function design_studies_analyze(WP_REST_Request $request){$p=self::design_studies_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/design-studies/analyze','POST',$p,8388608);}
    public static function design_studies_recommend(WP_REST_Request $request){$p=self::design_studies_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/design-studies/recommend','POST',$p,8388608);}
    public static function design_studies_batch(WP_REST_Request $request){$p=self::design_studies_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/design-studies/batches/build','POST',$p,8388608);}
    public static function design_studies_verify(WP_REST_Request $request){$p=self::design_studies_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/design-studies/verify','POST',$p,8388608);}
    private static function model_calibration_payload(WP_REST_Request $request){$p=$request->get_json_params();return is_array($p)?$p:new WP_Error('sc_lab_invalid_calibration_payload','A JSON object is required.',array('status'=>400));}
    public static function model_calibration_health(){return self::proxy('/v1/model-calibration/health');}
    public static function model_calibration_policies(){return self::proxy('/v1/model-calibration/policies');}
    public static function model_calibration_normalize(WP_REST_Request $request){$p=self::model_calibration_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-calibration/normalize','POST',$p,8388608);}
    public static function model_calibration_calibrate(WP_REST_Request $request){$p=self::model_calibration_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-calibration/calibrate','POST',$p,8388608);}
    public static function model_calibration_validate(WP_REST_Request $request){$p=self::model_calibration_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-calibration/validate','POST',$p,8388608);}
    public static function model_calibration_compare(WP_REST_Request $request){$p=self::model_calibration_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-calibration/compare','POST',$p,8388608);}
    public static function model_calibration_report(WP_REST_Request $request){$p=self::model_calibration_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-calibration/reports/build','POST',$p,8388608);}
    public static function model_calibration_verify(WP_REST_Request $request){$p=self::model_calibration_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-calibration/verify','POST',$p,8388608);}
    private static function dispatcher_payload(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){return new WP_Error('sc_lab_invalid_dispatcher_payload','A JSON dispatcher payload is required.',array('status'=>400));}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:$clean;}
    public static function dispatcher_health(){return self::proxy('/v1/dispatcher/health');}
    public static function dispatcher_policies(){return self::proxy('/v1/dispatcher/policies');}
    public static function dispatcher_workers(WP_REST_Request $request){$active=$request->get_param('activeOnly')?'true':'false';return self::proxy('/v1/dispatcher/workers?activeOnly='.$active);}
    public static function dispatcher_register(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/workers/register','POST',$p,8388608);}
    public static function dispatcher_heartbeat(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/workers/'.rawurlencode($request['worker']).'/heartbeat','POST',$p,8388608);}
    public static function dispatcher_route(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/route','POST',$p,8388608);}
    public static function dispatcher_contract_build(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/contracts/build','POST',$p,8388608);}
    public static function dispatcher_contract_verify(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/contracts/verify','POST',$p,8388608);}
    public static function dispatcher_queue_status(){return self::proxy('/v1/dispatcher/queue/status');}
    public static function dispatcher_queue_enqueue(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/queue/enqueue','POST',$p,8388608);}
    public static function dispatcher_leases(WP_REST_Request $request){$limit=max(1,min(500,intval($request->get_param('limit')?:100)));return self::proxy('/v1/dispatcher/leases?limit='.$limit);}
    public static function dispatcher_lease_claim(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/leases/claim','POST',$p,8388608);}
    public static function dispatcher_lease_renew(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/leases/'.rawurlencode($request['lease']).'/renew','POST',$p,8388608);}
    public static function dispatcher_lease_release(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/leases/'.rawurlencode($request['lease']).'/release','POST',$p,8388608);}
    public static function dispatcher_recovery(){return self::proxy('/v1/dispatcher/recovery/run','POST',array(),8388608);}
    public static function dispatcher_history(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));return self::proxy('/v1/dispatcher/history?limit='.$limit);}
    public static function dispatcher_operations_health(){return self::proxy('/v1/dispatcher/operations/health');}
    public static function dispatcher_operations_policies(){return self::proxy('/v1/dispatcher/operations/policies');}
    public static function dispatcher_operations_metrics(){return self::proxy('/v1/dispatcher/operations/metrics');}
    public static function dispatcher_operations_diagnostics(){return self::proxy('/v1/dispatcher/operations/diagnostics');}
    public static function dispatcher_dead_letters(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));$class=sanitize_key($request->get_param('failureClass')?:'');$query='limit='.$limit.($class?'&failureClass='.rawurlencode($class):'');return self::proxy('/v1/dispatcher/dead-letters?'.$query);}
    public static function dispatcher_dead_letters_replay(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/dead-letters/replay','POST',$p,8388608);}
    public static function dispatcher_queue_item(WP_REST_Request $request){return self::proxy('/v1/dispatcher/queue/'.rawurlencode($request['queue']));}
    public static function dispatcher_queue_timeline(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:250)));return self::proxy('/v1/dispatcher/queue/'.rawurlencode($request['queue']).'/timeline?limit='.$limit);}
    public static function dispatcher_queue_replay(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/queue/'.rawurlencode($request['queue']).'/replay','POST',$p,8388608);}
    public static function dispatcher_queue_cancel(WP_REST_Request $request){$p=self::dispatcher_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/dispatcher/queue/'.rawurlencode($request['queue']).'/cancel','POST',$p,8388608);}
    public static function worker_agent_health(){return self::proxy('/v1/worker-agent/health');}
    public static function worker_agent_policies(){return self::proxy('/v1/worker-agent/policies');}
    public static function worker_agent_credentials_status(){return self::proxy('/v1/worker-agent/credentials/status');}
    public static function worker_agent_workers(){return self::proxy('/v1/dispatcher/workers');}
    public static function artifact_health(){return self::proxy('/v1/artifacts/health');}
    public static function artifact_policies(){return self::proxy('/v1/artifacts/policies');}
    public static function artifact_list(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));return self::proxy('/v1/artifacts?limit='.$limit);}
    public static function artifact_uploads(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));return self::proxy('/v1/artifacts/uploads?limit='.$limit);}
    public static function artifact_cleanup(){return self::proxy('/v1/artifacts/cleanup','POST',array(),8388608);}
    private static function workflow_payload(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){return new WP_Error('sc_lab_invalid_workflow_payload','A JSON workflow payload is required.',array('status'=>400));}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:$clean;}
    public static function workflow_health(){return self::proxy('/v1/workflows/health');}
    public static function workflow_policies(){return self::proxy('/v1/workflows/policies');}
    public static function workflow_validate(WP_REST_Request $request){$p=self::workflow_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/workflows/validate','POST',$p,8388608);}
    public static function workflow_save(WP_REST_Request $request){$p=self::workflow_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/workflows','POST',$p,8388608);}
    public static function workflow_list(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));$project=sanitize_text_field($request->get_param('projectId')?:'');$query='limit='.$limit.($project?'&projectId='.rawurlencode($project):'');return self::proxy('/v1/workflows?'.$query);}
    public static function workflow_start(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:self::proxy('/v1/workflows/'.rawurlencode($request['workflow']).'/runs','POST',$clean,8388608);}
    public static function workflow_runs(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));$workflow=sanitize_text_field($request->get_param('workflowId')?:'');$project=sanitize_text_field($request->get_param('projectId')?:'');$status=sanitize_key($request->get_param('status')?:'');$parts=array('limit='.$limit);if($workflow){$parts[]='workflowId='.rawurlencode($workflow);}if($project){$parts[]='projectId='.rawurlencode($project);}if($status){$parts[]='status='.rawurlencode($status);}return self::proxy('/v1/workflow-runs?'.implode('&',$parts));}
    public static function workflow_run(WP_REST_Request $request){$reconcile=$request->get_param('reconcile');$value=($reconcile===false||$reconcile==='false'||$reconcile==='0')?'false':'true';return self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'?reconcile='.$value);}
    public static function workflow_reconcile(WP_REST_Request $request){return self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'/reconcile','POST',array(),8388608);}
    public static function workflow_cancel(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'/cancel','POST',$clean,8388608);}
    public static function workflow_timeline(WP_REST_Request $request){$limit=max(1,min(2000,intval($request->get_param('limit')?:500)));return self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'/timeline?limit='.$limit);}
    public static function workflow_recovery_plan(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'/recovery-plan','POST',$clean,8388608);}
    public static function workflow_recover(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'/recover','POST',$clean,8388608);}
    public static function workflow_restart_node(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'/nodes/'.rawurlencode($request['node']).'/restart','POST',$clean,8388608);}
    public static function workflow_checkpoints(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));return self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'/nodes/'.rawurlencode($request['node']).'/checkpoints?limit='.$limit);}
    public static function workflow_record_checkpoint(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:self::proxy('/v1/workflow-runs/'.rawurlencode($request['run']).'/nodes/'.rawurlencode($request['node']).'/checkpoints','POST',$clean,8388608);}
    private static function workflow_automation_payload(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:$clean;}
    public static function workflow_automation_health(){return self::proxy('/v1/workflow-automation/health');}
    public static function workflow_automation_policies(){return self::proxy('/v1/workflow-automation/policies');}
    public static function workflow_automation_validate(WP_REST_Request $request){$p=self::workflow_automation_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/workflow-automation/schedules/validate','POST',$p,8388608);}
    public static function workflow_automation_save(WP_REST_Request $request){$p=self::workflow_automation_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/workflow-automation/schedules','POST',$p,8388608);}
    public static function workflow_automation_schedules(WP_REST_Request $request){$parts=array('limit='.max(1,min(1000,intval($request->get_param('limit')?:100))));$workflow=sanitize_text_field($request->get_param('workflowId')?:'');if($workflow){$parts[]='workflowId='.rawurlencode($workflow);}return self::proxy('/v1/workflow-automation/schedules?'.implode('&',$parts));}
    public static function workflow_automation_trigger(WP_REST_Request $request){$p=self::workflow_automation_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/workflow-automation/schedules/'.rawurlencode($request['schedule']).'/trigger','POST',$p,8388608);}
    public static function workflow_automation_enable(WP_REST_Request $request){return self::proxy('/v1/workflow-automation/schedules/'.rawurlencode($request['schedule']).'/enable','POST',array(),8388608);}
    public static function workflow_automation_disable(WP_REST_Request $request){return self::proxy('/v1/workflow-automation/schedules/'.rawurlencode($request['schedule']).'/disable','POST',array(),8388608);}
    public static function workflow_automation_tick(){return self::proxy('/v1/workflow-automation/tick','POST',array(),8388608);}
    public static function workflow_automation_firings(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));return self::proxy('/v1/workflow-automation/firings?limit='.$limit);}
    public static function workflow_automation_events(WP_REST_Request $request){$limit=max(1,min(1000,intval($request->get_param('limit')?:100)));return self::proxy('/v1/workflow-automation/events?limit='.$limit);}
    public static function workflow_automation_ingest(WP_REST_Request $request){$p=self::workflow_automation_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/workflow-automation/events','POST',$p,8388608);}

    private static function experiment_campaign_payload(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes);return is_wp_error($clean)?$clean:$clean;}
    public static function experiment_campaign_health(){return self::proxy('/v1/experiment-campaigns/health');}
    public static function experiment_campaign_policies(){return self::proxy('/v1/experiment-campaigns/policies');}
    public static function experiment_campaign_validate(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiment-campaigns/validate','POST',$p,8388608);}
    public static function experiment_campaign_save(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiment-campaigns','POST',$p,8388608);}
    public static function experiment_campaign_list(WP_REST_Request $request){$parts=array('limit='.max(1,min(1000,intval($request->get_param('limit')?:100))));$project=sanitize_text_field($request->get_param('projectId')?:'');$status=sanitize_key($request->get_param('status')?:'');if($project){$parts[]='projectId='.rawurlencode($project);}if($status){$parts[]='status='.rawurlencode($status);}return self::proxy('/v1/experiment-campaigns?'.implode('&',$parts));}
    public static function experiment_campaign_get(WP_REST_Request $request){$reconcile=$request->get_param('reconcile');$value=($reconcile===true||$reconcile==='true'||$reconcile==='1')?'true':'false';return self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'?reconcile='.$value);}
    public static function experiment_campaign_start(WP_REST_Request $request){return self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/start','POST',array(),8388608);}
    public static function experiment_campaign_pause(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/pause','POST',$p,8388608);}
    public static function experiment_campaign_resume(WP_REST_Request $request){return self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/resume','POST',array(),8388608);}
    public static function experiment_campaign_advance(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/advance','POST',$p,8388608);}
    public static function experiment_campaign_reconcile(WP_REST_Request $request){return self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/reconcile','POST',array(),8388608);}
    public static function experiment_campaign_cancel(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/cancel','POST',$p,8388608);}
    public static function experiment_campaign_observe(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/observations','POST',$p,8388608);}
    public static function experiment_campaign_surrogate(WP_REST_Request $request){return self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/surrogate');}
    public static function experiment_campaign_proposal_preview(WP_REST_Request $request){return self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/proposal-preview','POST',array(),8388608);}
    public static function experiment_campaign_trials(WP_REST_Request $request){$parts=array('limit='.max(1,min(5000,intval($request->get_param('limit')?:500))));$status=sanitize_key($request->get_param('status')?:'');if($status){$parts[]='status='.rawurlencode($status);}return self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/trials?'.implode('&',$parts));}
    public static function experiment_campaign_timeline(WP_REST_Request $request){$limit=max(1,min(5000,intval($request->get_param('limit')?:500)));return self::proxy('/v1/experiment-campaigns/'.rawurlencode($request['campaign']).'/timeline?limit='.$limit);}
    public static function experiment_campaign_tick(){return self::proxy('/v1/experiment-campaigns/tick','POST',array(),8388608);}
    public static function closed_loop_health(){return self::proxy('/v1/closed-loop-campaigns/health');}
    public static function closed_loop_policies(){return self::proxy('/v1/closed-loop-campaigns/policies');}
    public static function closed_loop_validate(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/closed-loop-campaigns/validate','POST',$p,8388608);}
    public static function closed_loop_save(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/closed-loop-campaigns','POST',$p,8388608);}
    public static function closed_loop_list(WP_REST_Request $request){$parts=array('limit='.max(1,min(1000,intval($request->get_param('limit')?:100))));$project=sanitize_text_field($request->get_param('projectId')?:'');$status=sanitize_key($request->get_param('status')?:'');if($project){$parts[]='projectId='.rawurlencode($project);}if($status){$parts[]='status='.rawurlencode($status);}return self::proxy('/v1/closed-loop-campaigns?'.implode('&',$parts));}
    public static function closed_loop_get(WP_REST_Request $request){$reconcile=$request->get_param('reconcile');$value=($reconcile===true||$reconcile==='true'||$reconcile==='1')?'true':'false';return self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'?reconcile='.$value);}
    public static function closed_loop_start(WP_REST_Request $request){return self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/start','POST',array(),8388608);}
    public static function closed_loop_pause(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/pause','POST',$p,8388608);}
    public static function closed_loop_resume(WP_REST_Request $request){return self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/resume','POST',array(),8388608);}
    public static function closed_loop_reconcile(WP_REST_Request $request){return self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/reconcile','POST',array(),8388608);}
    public static function closed_loop_cancel(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/cancel','POST',$p,8388608);}
    public static function closed_loop_emergency_stop(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/emergency-stop','POST',$p,8388608);}
    public static function closed_loop_issue(WP_REST_Request $request){return self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/commands/issue','POST',array(),8388608);}
    public static function closed_loop_approve(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/commands/'.rawurlencode($request['command']).'/approve','POST',$p,8388608);}
    public static function closed_loop_dispatch(WP_REST_Request $request){return self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/commands/'.rawurlencode($request['command']).'/dispatch','POST',array(),8388608);}
    public static function closed_loop_measurement(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/measurements','POST',$p,8388608);}
    public static function closed_loop_measurements(WP_REST_Request $request){$limit=max(1,min(5000,intval($request->get_param('limit')?:500)));return self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/measurements?limit='.$limit);}
    public static function closed_loop_timeline(WP_REST_Request $request){$limit=max(1,min(5000,intval($request->get_param('limit')?:500)));return self::proxy('/v1/closed-loop-campaigns/'.rawurlencode($request['loop']).'/timeline?limit='.$limit);}
    public static function closed_loop_tick(){return self::proxy('/v1/closed-loop-campaigns/tick','POST',array(),8388608);}

    public static function model_registry_health(){return self::proxy('/v1/model-registry/health');}
    public static function model_registry_policies(){return self::proxy('/v1/model-registry/policies');}
    public static function model_registry_capture_environment(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-registry/environments/capture','POST',$p,8388608);}
    public static function model_registry_compare_environment(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-registry/environments/compare','POST',$p,8388608);}
    public static function model_registry_validate(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-registry/validate','POST',$p,8388608);}
    public static function model_registry_register(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-registry/models','POST',$p,8388608);}
    public static function model_registry_list(WP_REST_Request $request){$parts=array('limit='.max(1,min(1000,intval($request->get_param('limit')?:100))));$project=sanitize_text_field($request->get_param('projectId')?:'');$channel=sanitize_key($request->get_param('channel')?:'');if($project){$parts[]='projectId='.rawurlencode($project);}if($channel){$parts[]='channel='.rawurlencode($channel);}return self::proxy('/v1/model-registry/models?'.implode('&',$parts));}
    public static function model_registry_get(WP_REST_Request $request){$version=sanitize_text_field($request->get_param('version')?:'');$suffix=$version?'?version='.rawurlencode($version):'';return self::proxy('/v1/model-registry/models/'.rawurlencode($request['model']).$suffix);}
    public static function model_registry_promote(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-registry/models/'.rawurlencode($request['model']).'/'.rawurlencode($request['version']).'/promote','POST',$p,8388608);}
    public static function model_registry_deprecate(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-registry/models/'.rawurlencode($request['model']).'/'.rawurlencode($request['version']).'/deprecate','POST',$p,8388608);}
    public static function model_registry_reproduction(WP_REST_Request $request){$version=sanitize_text_field($request->get_param('version')?:'');$suffix=$version?'?version='.rawurlencode($version):'';return self::proxy('/v1/model-registry/models/'.rawurlencode($request['model']).'/reproduction'.$suffix);}
    public static function model_registry_timeline(WP_REST_Request $request){$limit=max(1,min(5000,intval($request->get_param('limit')?:500)));return self::proxy('/v1/model-registry/models/'.rawurlencode($request['model']).'/timeline?limit='.$limit);}
    public static function model_registry_verify(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/model-registry/reproduction/verify','POST',$p,8388608);}

    public static function ensemble_health(){return self::proxy('/v1/ensemble-studies/health');}
    public static function ensemble_policies(){return self::proxy('/v1/ensemble-studies/policies');}
    public static function ensemble_validate(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/ensemble-studies/validate','POST',$p,8388608);}
    public static function ensemble_create(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/ensemble-studies','POST',$p,8388608);}
    public static function ensemble_list(WP_REST_Request $request){$parts=array('limit='.max(1,min(1000,intval($request->get_param('limit')?:100))));$project=sanitize_text_field($request->get_param('projectId')?:'');$status=sanitize_key($request->get_param('status')?:'');if($project){$parts[]='projectId='.rawurlencode($project);}if($status){$parts[]='status='.rawurlencode($status);}return self::proxy('/v1/ensemble-studies?'.implode('&',$parts));}
    public static function ensemble_get(WP_REST_Request $request){$reconcile=$request->get_param('reconcile');$value=($reconcile===false||$reconcile==='false'||$reconcile==='0')?'false':'true';$limit=max(1,min(200000,intval($request->get_param('evaluationLimit')?:5000)));return self::proxy('/v1/ensemble-studies/'.rawurlencode($request['study']).'?reconcile='.$value.'&evaluationLimit='.$limit);}
    public static function ensemble_start(WP_REST_Request $request){return self::proxy('/v1/ensemble-studies/'.rawurlencode($request['study']).'/start','POST',array(),8388608);}
    public static function ensemble_reconcile(WP_REST_Request $request){return self::proxy('/v1/ensemble-studies/'.rawurlencode($request['study']).'/reconcile','POST',array(),8388608);}
    public static function ensemble_cancel(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/ensemble-studies/'.rawurlencode($request['study']).'/cancel','POST',$p,8388608);}
    public static function ensemble_timeline(WP_REST_Request $request){$limit=max(1,min(5000,intval($request->get_param('limit')?:500)));return self::proxy('/v1/ensemble-studies/'.rawurlencode($request['study']).'/timeline?limit='.$limit);}
    public static function ensemble_record_result(WP_REST_Request $request){$p=self::experiment_campaign_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/ensemble-studies/'.rawurlencode($request['study']).'/evaluations/'.rawurlencode($request['evaluation']).'/result','POST',$p,8388608);}

    private static function team_workspace_payload(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){$p=array();}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes,20000,12);return is_wp_error($clean)?$clean:$clean;}
    public static function team_workspace_health(){return self::proxy('/v1/team-workspaces/health');}
    public static function team_workspace_policies(){return self::proxy('/v1/team-workspaces/policies');}
    public static function team_workspace_create(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces','POST',$p,4194304);}
    public static function team_workspace_list(WP_REST_Request $request){$parts=array('limit='.max(1,min(1000,intval($request->get_param('limit')?:100))));$status=sanitize_key($request->get_param('status')?:'');if($status){$parts[]='status='.rawurlencode($status);}return self::proxy('/v1/team-workspaces?'.implode('&',$parts));}
    public static function team_workspace_accept(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces/invitations/accept','POST',$p,4194304);}
    public static function team_workspace_get(WP_REST_Request $request){return self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']));}
    public static function team_workspace_update(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']),'PATCH',$p,4194304);}
    public static function team_workspace_archive(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/archive','POST',$p,4194304);}
    public static function team_workspace_invite(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/invitations','POST',$p,4194304);}
    public static function team_workspace_member_role(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/members/'.rawurlencode($request['member']),'PATCH',$p,4194304);}
    public static function team_workspace_remove_member(WP_REST_Request $request){$reason=sanitize_text_field($request->get_param('reason')?:'');return self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/members/'.rawurlencode($request['member']).'?reason='.rawurlencode($reason),'DELETE',null,4194304);}
    public static function team_workspace_transfer(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/ownership','POST',$p,4194304);}
    public static function team_workspace_link_resource(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/resources','POST',$p,4194304);}
    public static function team_workspace_unlink_resource(WP_REST_Request $request){$reason=sanitize_text_field($request->get_param('reason')?:'');return self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/resources/'.rawurlencode($request['link']).'?reason='.rawurlencode($reason),'DELETE',null,4194304);}
    public static function team_workspace_authorize(WP_REST_Request $request){$p=self::team_workspace_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/authorize','POST',$p,4194304);}
    public static function team_workspace_timeline(WP_REST_Request $request){$limit=max(1,min(5000,intval($request->get_param('limit')?:500)));return self::proxy('/v1/team-workspaces/'.rawurlencode($request['workspace']).'/timeline?limit='.$limit);}

    private static function surrogate_rom_payload(WP_REST_Request $request){$p=$request->get_json_params();if(!is_array($p)){return new WP_Error('sc_lab_invalid_surrogate_rom_payload','A JSON surrogate or reduced-order payload is required.',array('status'=>400));}$nodes=0;$clean=self::sanitize_tree($p,0,$nodes,500000,16);return is_wp_error($clean)?$clean:$clean;}
    public static function surrogate_rom_health(){return self::proxy('/v1/surrogate-rom/health');}
    public static function surrogate_rom_policies(){return self::proxy('/v1/surrogate-rom/policies');}
    public static function surrogate_rom_validate(WP_REST_Request $request){$p=self::surrogate_rom_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/surrogate-rom/validate','POST',$p,16777216);}
    public static function surrogate_rom_train(WP_REST_Request $request){$p=self::surrogate_rom_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/surrogate-rom/studies','POST',$p,16777216);}
    public static function surrogate_rom_list(WP_REST_Request $request){$parts=array('limit='.max(1,min(1000,intval($request->get_param('limit')?:100))));$project=sanitize_text_field($request->get_param('projectId')?:'');$status=sanitize_key($request->get_param('status')?:'');if($project){$parts[]='projectId='.rawurlencode($project);}if($status){$parts[]='status='.rawurlencode($status);}return self::proxy('/v1/surrogate-rom/studies?'.implode('&',$parts));}
    public static function surrogate_rom_get(WP_REST_Request $request){return self::proxy('/v1/surrogate-rom/studies/'.rawurlencode($request['study']));}
    public static function surrogate_rom_predict(WP_REST_Request $request){$p=self::surrogate_rom_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/surrogate-rom/studies/'.rawurlencode($request['study']).'/predict','POST',$p,16777216);}
    public static function surrogate_rom_register(WP_REST_Request $request){$p=self::surrogate_rom_payload($request);return is_wp_error($p)?$p:self::proxy('/v1/surrogate-rom/studies/'.rawurlencode($request['study']).'/register','POST',$p,16777216);}
    public static function surrogate_rom_timeline(WP_REST_Request $request){$limit=max(1,min(5000,intval($request->get_param('limit')?:500)));return self::proxy('/v1/surrogate-rom/studies/'.rawurlencode($request['study']).'/timeline?limit='.$limit);}


}
