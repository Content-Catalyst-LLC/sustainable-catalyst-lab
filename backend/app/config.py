from __future__ import annotations

from dataclasses import dataclass
import os


def _int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


@dataclass(frozen=True)
class Settings:
    version: str = "1.0.0"
    service_name: str = "Sustainable Catalyst Python Compute Core"
    environment: str = os.getenv("SC_LAB_ENVIRONMENT", "production")
    api_key: str = os.getenv("SC_LAB_COMPUTE_API_KEY", os.getenv("SC_LAB_API_KEY", "")).strip()
    signing_secret: str = os.getenv("SC_LAB_COMPUTE_SIGNING_SECRET", "").strip()
    signature_tolerance_seconds: int = _int("SC_LAB_SIGNATURE_TOLERANCE_SECONDS", 300, 30, 900)
    max_request_bytes: int = _int("SC_LAB_MAX_REQUEST_BYTES", 262144, 16384, 2097152)
    max_array_items: int = _int("SC_LAB_MAX_ARRAY_ITEMS", 100000, 100, 1000000)
    max_job_records: int = _int("SC_LAB_MAX_JOB_RECORDS", 500, 10, 5000)
    max_queued_jobs: int = _int("SC_LAB_MAX_QUEUED_JOBS", 100, 1, 10000)
    job_workers: int = _int("SC_LAB_JOB_WORKERS", 2, 1, 16)
    default_job_timeout_seconds: int = _int("SC_LAB_DEFAULT_JOB_TIMEOUT_SECONDS", 60, 1, 3600)
    max_job_timeout_seconds: int = _int("SC_LAB_MAX_JOB_TIMEOUT_SECONDS", 900, 5, 86400)
    default_job_attempts: int = _int("SC_LAB_DEFAULT_JOB_ATTEMPTS", 2, 1, 10)
    max_job_attempts: int = _int("SC_LAB_MAX_JOB_ATTEMPTS", 5, 1, 20)
    retry_base_delay_seconds: int = _int("SC_LAB_RETRY_BASE_DELAY_SECONDS", 2, 1, 300)
    max_retry_delay_seconds: int = _int("SC_LAB_MAX_RETRY_DELAY_SECONDS", 60, 1, 3600)
    job_dedupe_window_seconds: int = _int("SC_LAB_JOB_DEDUPE_WINDOW_SECONDS", 86400, 60, 604800)
    job_retention_seconds: int = _int("SC_LAB_JOB_RETENTION_SECONDS", 604800, 3600, 31536000)
    job_scheduler_interval_seconds: float = max(0.05, min(5.0, float(os.getenv("SC_LAB_JOB_SCHEDULER_INTERVAL_SECONDS", "0.2"))))
    job_db_path: str = os.getenv("SC_LAB_JOB_DB_PATH", "./data/sc-lab-compute-jobs.sqlite3").strip()
    extension_loading: bool = os.getenv("SC_LAB_LOAD_LEGACY_EXTENSIONS", "1").lower() not in {"0", "false", "no"}
    max_active_jobs_per_project: int = _int("SC_LAB_MAX_ACTIVE_JOBS_PER_PROJECT", 5, 1, 100)
    checkpoint_retention_per_job: int = _int("SC_LAB_CHECKPOINT_RETENTION_PER_JOB", 20, 1, 200)
    max_checkpoint_bytes: int = _int("SC_LAB_MAX_CHECKPOINT_BYTES", 8388608, 65536, 67108864)
    result_cache_ttl_seconds: int = _int("SC_LAB_RESULT_CACHE_TTL_SECONDS", 86400, 60, 2592000)
    max_cache_records: int = _int("SC_LAB_MAX_CACHE_RECORDS", 250, 1, 5000)
    default_job_priority: int = _int("SC_LAB_DEFAULT_JOB_PRIORITY", 50, 0, 100)
    discovery_contact_email: str = os.getenv("SC_LAB_DISCOVERY_CONTACT_EMAIL", "").strip()
    openalex_api_key: str = os.getenv("SC_LAB_OPENALEX_API_KEY", "").strip()
    oclc_access_token: str = os.getenv("SC_LAB_OCLC_ACCESS_TOKEN", "").strip()
    openurl_resolver_base: str = os.getenv("SC_LAB_OPENURL_RESOLVER_BASE", "").strip()
    discovery_timeout_seconds: int = _int("SC_LAB_DISCOVERY_TIMEOUT_SECONDS", 15, 3, 60)
    discovery_max_results: int = _int("SC_LAB_DISCOVERY_MAX_RESULTS", 25, 1, 50)
    dispatcher_worker_stale_seconds: int = _int("SC_LAB_DISPATCHER_WORKER_STALE_SECONDS", 120, 30, 3600)
    dispatcher_default_lease_seconds: int = _int("SC_LAB_DISPATCHER_DEFAULT_LEASE_SECONDS", 300, 30, 3600)
    dispatcher_max_workers: int = _int("SC_LAB_DISPATCHER_MAX_WORKERS", 500, 1, 5000)
    dispatcher_db_path: str = os.getenv("SC_LAB_DISPATCHER_DB_PATH", "./data/sc-lab-dispatcher.sqlite3").strip()
    dispatcher_max_queue_records: int = _int("SC_LAB_DISPATCHER_MAX_QUEUE_RECORDS", 5000, 100, 100000)
    dispatcher_max_attempts: int = _int("SC_LAB_DISPATCHER_MAX_ATTEMPTS", 5, 1, 20)
    dispatcher_history_limit: int = _int("SC_LAB_DISPATCHER_HISTORY_LIMIT", 10000, 100, 1000000)
    dispatcher_retry_base_delay_seconds: int = _int("SC_LAB_DISPATCHER_RETRY_BASE_DELAY_SECONDS", 15, 1, 3600)
    dispatcher_retry_max_delay_seconds: int = _int("SC_LAB_DISPATCHER_RETRY_MAX_DELAY_SECONDS", 900, 1, 86400)
    dispatcher_contract_secret: str = os.getenv("SC_LAB_DISPATCHER_CONTRACT_SECRET", os.getenv("SC_LAB_COMPUTE_SIGNING_SECRET", "")).strip()
    worker_enrollment_token: str = os.getenv("SC_LAB_WORKER_ENROLLMENT_TOKEN", "").strip()
    allow_open_worker_enrollment: bool = os.getenv("SC_LAB_ALLOW_OPEN_WORKER_ENROLLMENT", "0").lower() in {"1", "true", "yes"}
    dispatcher_persistent_disk_mounted: bool = os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0").lower() in {"1", "true", "yes"}
    artifact_root: str = os.getenv("SC_LAB_ARTIFACT_ROOT", "./data/artifacts").strip()
    artifact_db_path: str = os.getenv("SC_LAB_ARTIFACT_DB_PATH", "").strip()
    artifact_max_bytes: int = _int("SC_LAB_ARTIFACT_MAX_BYTES", 268435456, 1048576, 2147483648)
    artifact_chunk_bytes: int = _int("SC_LAB_ARTIFACT_CHUNK_BYTES", 1048576, 65536, 8388608)
    artifact_upload_ttl_seconds: int = _int("SC_LAB_ARTIFACT_UPLOAD_TTL_SECONDS", 86400, 300, 604800)
    artifact_retention_seconds: int = _int("SC_LAB_ARTIFACT_RETENTION_SECONDS", 2592000, 3600, 31536000)
    worker_result_artifact_threshold_bytes: int = _int("SC_LAB_WORKER_RESULT_ARTIFACT_THRESHOLD_BYTES", 262144, 1024, 16777216)
    artifact_persistent_disk_mounted: bool = os.getenv("SC_LAB_ARTIFACT_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    workflow_db_path: str = os.getenv("SC_LAB_WORKFLOW_DB_PATH", "./data/sc-lab-workflows.sqlite3").strip()
    workflow_max_nodes: int = _int("SC_LAB_WORKFLOW_MAX_NODES", 100, 1, 1000)
    workflow_max_runs: int = _int("SC_LAB_WORKFLOW_MAX_RUNS", 5000, 100, 100000)
    workflow_history_limit: int = _int("SC_LAB_WORKFLOW_HISTORY_LIMIT", 20000, 100, 1000000)
    workflow_persistent_disk_mounted: bool = os.getenv("SC_LAB_WORKFLOW_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    workflow_schedule_db_path: str = os.getenv("SC_LAB_WORKFLOW_SCHEDULE_DB_PATH", "./data/sc-lab-workflow-schedules.sqlite3").strip()
    workflow_scheduler_poll_seconds: float = max(1.0, min(3600.0, float(os.getenv("SC_LAB_WORKFLOW_SCHEDULER_POLL_SECONDS", "30"))))
    workflow_scheduler_max_catch_up_runs: int = _int("SC_LAB_WORKFLOW_SCHEDULER_MAX_CATCH_UP_RUNS", 10, 1, 100)
    workflow_scheduler_history_limit: int = _int("SC_LAB_WORKFLOW_SCHEDULER_HISTORY_LIMIT", 20000, 100, 1000000)
    workflow_event_secret: str = os.getenv("SC_LAB_WORKFLOW_EVENT_SECRET", "").strip()
    workflow_event_signature_tolerance_seconds: int = _int("SC_LAB_WORKFLOW_EVENT_SIGNATURE_TOLERANCE_SECONDS", 300, 30, 3600)
    workflow_schedule_persistent_disk_mounted: bool = os.getenv("SC_LAB_WORKFLOW_SCHEDULE_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_WORKFLOW_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    experiment_campaign_db_path: str = os.getenv("SC_LAB_EXPERIMENT_CAMPAIGN_DB_PATH", "./data/sc-lab-experiment-campaigns.sqlite3").strip()
    experiment_campaign_poll_seconds: float = max(1.0, min(3600.0, float(os.getenv("SC_LAB_EXPERIMENT_CAMPAIGN_POLL_SECONDS", "30"))))
    experiment_campaign_max_campaigns: int = _int("SC_LAB_EXPERIMENT_CAMPAIGN_MAX_CAMPAIGNS", 1000, 1, 100000)
    experiment_campaign_max_trials: int = _int("SC_LAB_EXPERIMENT_CAMPAIGN_MAX_TRIALS", 10000, 1, 1000000)
    experiment_campaign_history_limit: int = _int("SC_LAB_EXPERIMENT_CAMPAIGN_HISTORY_LIMIT", 30000, 100, 1000000)
    experiment_campaign_persistent_disk_mounted: bool = os.getenv("SC_LAB_EXPERIMENT_CAMPAIGN_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_WORKFLOW_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    closed_loop_db_path: str = os.getenv("SC_LAB_CLOSED_LOOP_DB_PATH", "./data/sc-lab-closed-loop-campaigns.sqlite3").strip()
    closed_loop_poll_seconds: float = max(1.0, min(3600.0, float(os.getenv("SC_LAB_CLOSED_LOOP_POLL_SECONDS", "30"))))
    closed_loop_max_loops: int = _int("SC_LAB_CLOSED_LOOP_MAX_LOOPS", 1000, 1, 100000)
    closed_loop_max_cycles: int = _int("SC_LAB_CLOSED_LOOP_MAX_CYCLES", 100000, 1, 1000000)
    closed_loop_history_limit: int = _int("SC_LAB_CLOSED_LOOP_HISTORY_LIMIT", 30000, 100, 1000000)
    closed_loop_measurement_secret: str = os.getenv("SC_LAB_CLOSED_LOOP_MEASUREMENT_SECRET", "").strip()
    closed_loop_persistent_disk_mounted: bool = os.getenv("SC_LAB_CLOSED_LOOP_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_EXPERIMENT_CAMPAIGN_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    model_registry_db_path: str = os.getenv("SC_LAB_MODEL_REGISTRY_DB_PATH", "./data/sc-lab-model-registry.sqlite3").strip()
    model_registry_max_models: int = _int("SC_LAB_MODEL_REGISTRY_MAX_MODELS", 5000, 1, 100000)
    model_registry_max_versions: int = _int("SC_LAB_MODEL_REGISTRY_MAX_VERSIONS", 50000, 1, 1000000)
    model_registry_history_limit: int = _int("SC_LAB_MODEL_REGISTRY_HISTORY_LIMIT", 50000, 100, 1000000)
    model_registry_persistent_disk_mounted: bool = os.getenv("SC_LAB_MODEL_REGISTRY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    ensemble_study_db_path: str = os.getenv("SC_LAB_ENSEMBLE_STUDY_DB_PATH", "./data/sc-lab-ensemble-studies.sqlite3").strip()
    ensemble_max_studies: int = _int("SC_LAB_ENSEMBLE_MAX_STUDIES", 2000, 1, 100000)
    ensemble_max_evaluations: int = _int("SC_LAB_ENSEMBLE_MAX_EVALUATIONS", 200000, 100, 2000000)
    ensemble_history_limit: int = _int("SC_LAB_ENSEMBLE_HISTORY_LIMIT", 50000, 100, 1000000)
    ensemble_persistent_disk_mounted: bool = os.getenv("SC_LAB_ENSEMBLE_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_MODEL_REGISTRY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    surrogate_rom_db_path: str = os.getenv("SC_LAB_SURROGATE_ROM_DB_PATH", "./data/sc-lab-surrogate-rom.sqlite3").strip()
    surrogate_rom_max_request_bytes: int = _int("SC_LAB_SURROGATE_ROM_MAX_REQUEST_BYTES", 16777216, 262144, 67108864)
    surrogate_rom_max_studies: int = _int("SC_LAB_SURROGATE_ROM_MAX_STUDIES", 2000, 1, 100000)
    surrogate_rom_max_training_rows: int = _int("SC_LAB_SURROGATE_ROM_MAX_TRAINING_ROWS", 50000, 4, 1000000)
    surrogate_rom_max_snapshot_dimensions: int = _int("SC_LAB_SURROGATE_ROM_MAX_SNAPSHOT_DIMENSIONS", 5000, 2, 100000)
    surrogate_rom_history_limit: int = _int("SC_LAB_SURROGATE_ROM_HISTORY_LIMIT", 50000, 100, 1000000)
    surrogate_rom_persistent_disk_mounted: bool = os.getenv("SC_LAB_SURROGATE_ROM_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_MODEL_REGISTRY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    team_workspace_db_path: str = os.getenv("SC_LAB_TEAM_WORKSPACE_DB_PATH", "./data/sc-lab-team-workspaces.sqlite3").strip()
    team_workspace_max_workspaces: int = _int("SC_LAB_TEAM_WORKSPACE_MAX_WORKSPACES", 5000, 1, 100000)
    team_workspace_max_members: int = _int("SC_LAB_TEAM_WORKSPACE_MAX_MEMBERS", 100000, 10, 2000000)
    team_workspace_history_limit: int = _int("SC_LAB_TEAM_WORKSPACE_HISTORY_LIMIT", 100000, 100, 2000000)
    team_workspace_persistent_disk_mounted: bool = os.getenv("SC_LAB_TEAM_WORKSPACE_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    artifact_repository_db_path: str = os.getenv("SC_LAB_ARTIFACT_REPOSITORY_DB_PATH", "./data/sc-lab-artifact-repository.sqlite3").strip()
    artifact_repository_max_collections: int = _int("SC_LAB_ARTIFACT_REPOSITORY_MAX_COLLECTIONS", 5000, 1, 100000)
    artifact_repository_max_records: int = _int("SC_LAB_ARTIFACT_REPOSITORY_MAX_RECORDS", 250000, 100, 5000000)
    artifact_repository_max_manifest_records: int = _int("SC_LAB_ARTIFACT_REPOSITORY_MAX_MANIFEST_RECORDS", 10000, 1, 100000)
    artifact_repository_history_limit: int = _int("SC_LAB_ARTIFACT_REPOSITORY_HISTORY_LIMIT", 100000, 100, 2000000)
    artifact_repository_persistent_disk_mounted: bool = os.getenv("SC_LAB_ARTIFACT_REPOSITORY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_ARTIFACT_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    institutional_node_db_path: str = os.getenv("SC_LAB_INSTITUTIONAL_NODE_DB_PATH", "./data/sc-lab-institutional-nodes.sqlite3").strip()
    institutional_node_coordinator_secret: str = os.getenv("SC_LAB_INSTITUTIONAL_NODE_COORDINATOR_SECRET", os.getenv("SC_LAB_DISPATCHER_CONTRACT_SECRET", os.getenv("SC_LAB_COMPUTE_SIGNING_SECRET", ""))).strip()
    institutional_node_max_nodes: int = _int("SC_LAB_INSTITUTIONAL_NODE_MAX_NODES", 1000, 1, 100000)
    institutional_node_max_data_assets: int = _int("SC_LAB_INSTITUTIONAL_NODE_MAX_DATA_ASSETS", 100000, 1, 5000000)
    institutional_node_max_requests: int = _int("SC_LAB_INSTITUTIONAL_NODE_MAX_REQUESTS", 250000, 100, 5000000)
    institutional_node_history_limit: int = _int("SC_LAB_INSTITUTIONAL_NODE_HISTORY_LIMIT", 100000, 100, 2000000)
    institutional_node_persistent_disk_mounted: bool = os.getenv("SC_LAB_INSTITUTIONAL_NODE_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_ARTIFACT_REPOSITORY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    edge_sync_db_path: str = os.getenv("SC_LAB_EDGE_SYNC_DB_PATH", "./data/sc-lab-edge-sync.sqlite3").strip()
    edge_sync_max_devices: int = _int("SC_LAB_EDGE_SYNC_MAX_DEVICES", 10000, 1, 1000000)
    edge_sync_max_packages: int = _int("SC_LAB_EDGE_SYNC_MAX_PACKAGES", 100000, 1, 2000000)
    edge_sync_max_changes: int = _int("SC_LAB_EDGE_SYNC_MAX_CHANGES", 1000000, 100, 10000000)
    edge_sync_max_batch: int = _int("SC_LAB_EDGE_SYNC_MAX_BATCH", 500, 1, 5000)
    edge_sync_history_limit: int = _int("SC_LAB_EDGE_SYNC_HISTORY_LIMIT", 200000, 100, 5000000)
    edge_sync_persistent_disk_mounted: bool = os.getenv("SC_LAB_EDGE_SYNC_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_INSTITUTIONAL_NODE_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}

    publication_studio_db_path: str = os.getenv("SC_LAB_PUBLICATION_STUDIO_DB_PATH", "./data/sc-lab-publication-studio.sqlite3").strip()
    publication_studio_max_packages: int = _int("SC_LAB_PUBLICATION_STUDIO_MAX_PACKAGES", 5000, 1, 100000)
    publication_studio_max_publications: int = _int("SC_LAB_PUBLICATION_STUDIO_MAX_PUBLICATIONS", 5000, 1, 100000)
    publication_studio_max_resources: int = _int("SC_LAB_PUBLICATION_STUDIO_MAX_RESOURCES", 1000, 1, 10000)
    publication_studio_history_limit: int = _int("SC_LAB_PUBLICATION_STUDIO_HISTORY_LIMIT", 100000, 100, 2000000)
    publication_studio_persistent_disk_mounted: bool = os.getenv("SC_LAB_PUBLICATION_STUDIO_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_ARTIFACT_REPOSITORY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    manuscript_assembly_db_path: str = os.getenv("SC_LAB_MANUSCRIPT_ASSEMBLY_DB_PATH", "./data/sc-lab-manuscript-assembly.sqlite3").strip()
    manuscript_assembly_max_assemblies: int = _int("SC_LAB_MANUSCRIPT_ASSEMBLY_MAX_ASSEMBLIES", 5000, 1, 100000)
    manuscript_assembly_max_sections: int = _int("SC_LAB_MANUSCRIPT_ASSEMBLY_MAX_SECTIONS", 20000, 1, 500000)
    manuscript_assembly_max_sections_per_assembly: int = _int("SC_LAB_MANUSCRIPT_ASSEMBLY_MAX_SECTIONS_PER_ASSEMBLY", 500, 1, 5000)
    manuscript_assembly_history_limit: int = _int("SC_LAB_MANUSCRIPT_ASSEMBLY_HISTORY_LIMIT", 100000, 100, 2000000)
    manuscript_assembly_persistent_disk_mounted: bool = os.getenv("SC_LAB_MANUSCRIPT_ASSEMBLY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_PUBLICATION_STUDIO_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    public_reproduction_db_path: str = os.getenv("SC_LAB_PUBLIC_REPRODUCTION_DB_PATH", "./data/sc-lab-public-reproduction.sqlite3").strip()
    public_reproduction_receipt_secret: str = os.getenv("SC_LAB_PUBLIC_REPRODUCTION_RECEIPT_SECRET", os.getenv("SC_LAB_COMPUTE_SIGNING_SECRET", "")).strip()
    public_reproduction_max_records: int = _int("SC_LAB_PUBLIC_REPRODUCTION_MAX_RECORDS", 10000, 1, 200000)
    public_reproduction_max_challenges: int = _int("SC_LAB_PUBLIC_REPRODUCTION_MAX_CHALLENGES", 250000, 100, 5000000)
    public_reproduction_challenge_ttl_seconds: int = _int("SC_LAB_PUBLIC_REPRODUCTION_CHALLENGE_TTL_SECONDS", 86400, 300, 604800)
    public_reproduction_history_limit: int = _int("SC_LAB_PUBLIC_REPRODUCTION_HISTORY_LIMIT", 200000, 100, 5000000)
    public_reproduction_persistent_disk_mounted: bool = os.getenv("SC_LAB_PUBLIC_REPRODUCTION_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_PUBLICATION_STUDIO_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    interoperability_db_path: str = os.getenv("SC_LAB_INTEROPERABILITY_DB_PATH", "./data/sc-lab-research-interoperability.sqlite3").strip()
    interoperability_receipt_secret: str = os.getenv("SC_LAB_INTEROPERABILITY_RECEIPT_SECRET", os.getenv("SC_LAB_COMPUTE_SIGNING_SECRET", "")).strip()
    interoperability_max_profiles: int = _int("SC_LAB_INTEROPERABILITY_MAX_PROFILES", 5000, 1, 100000)
    interoperability_max_handoffs: int = _int("SC_LAB_INTEROPERABILITY_MAX_HANDOFFS", 250000, 100, 5000000)
    interoperability_history_limit: int = _int("SC_LAB_INTEROPERABILITY_HISTORY_LIMIT", 250000, 100, 5000000)
    interoperability_persistent_disk_mounted: bool = os.getenv("SC_LAB_INTEROPERABILITY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_TEAM_WORKSPACE_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED", "0"))).lower() in {"1", "true", "yes"}
    public_integration_db_path: str = os.getenv("SC_LAB_PUBLIC_INTEGRATION_DB_PATH", "./data/sc-lab-public-research-integrations.sqlite3").strip()
    public_api_key: str = os.getenv("SC_LAB_PUBLIC_API_KEY", os.getenv("SC_LAB_COMPUTE_API_KEY", os.getenv("SC_LAB_API_KEY", ""))).strip()
    public_api_scopes: str = os.getenv("SC_LAB_PUBLIC_API_SCOPES", "research:read,research:write,webhooks:read,webhooks:write,webhooks:emit,embeds:write").strip()
    webhook_signing_secret: str = os.getenv("SC_LAB_WEBHOOK_SIGNING_SECRET", os.getenv("SC_LAB_INTEROPERABILITY_RECEIPT_SECRET", os.getenv("SC_LAB_COMPUTE_SIGNING_SECRET", ""))).strip()
    webhook_delivery_enabled: bool = os.getenv("SC_LAB_WEBHOOK_DELIVERY_ENABLED", "0").lower() in {"1", "true", "yes"}
    public_integration_max_subscriptions: int = _int("SC_LAB_PUBLIC_INTEGRATION_MAX_SUBSCRIPTIONS", 5000, 1, 100000)
    public_integration_max_deliveries: int = _int("SC_LAB_PUBLIC_INTEGRATION_MAX_DELIVERIES", 250000, 100, 5000000)
    public_integration_persistent_disk_mounted: bool = os.getenv("SC_LAB_PUBLIC_INTEGRATION_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_INTEROPERABILITY_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    institutional_governance_db_path: str = os.getenv("SC_LAB_INSTITUTIONAL_GOVERNANCE_DB_PATH", "./data/sc-lab-institutional-governance.sqlite3").strip()
    institutional_governance_max_institutions: int = _int("SC_LAB_INSTITUTIONAL_GOVERNANCE_MAX_INSTITUTIONS", 1000, 1, 100000)
    institutional_governance_max_principals: int = _int("SC_LAB_INSTITUTIONAL_GOVERNANCE_MAX_PRINCIPALS", 250000, 100, 5000000)
    institutional_governance_history_limit: int = _int("SC_LAB_INSTITUTIONAL_GOVERNANCE_HISTORY_LIMIT", 250000, 100, 5000000)
    institutional_governance_persistent_disk_mounted: bool = os.getenv("SC_LAB_INSTITUTIONAL_GOVERNANCE_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_TEAM_WORKSPACE_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    security_privacy_db_path: str = os.getenv("SC_LAB_SECURITY_PRIVACY_DB_PATH", "./data/sc-lab-security-privacy.sqlite3").strip()
    secret_master_key: str = os.getenv("SC_LAB_SECRET_MASTER_KEY", "").strip()
    secret_previous_master_keys: str = os.getenv("SC_LAB_SECRET_PREVIOUS_MASTER_KEYS", "").strip()
    audit_signing_secret: str = os.getenv("SC_LAB_AUDIT_SIGNING_SECRET", os.getenv("SC_LAB_COMPUTE_SIGNING_SECRET", "")).strip()
    security_privacy_max_secrets: int = _int("SC_LAB_SECURITY_PRIVACY_MAX_SECRETS", 100000, 1, 2000000)
    security_privacy_max_credentials: int = _int("SC_LAB_SECURITY_PRIVACY_MAX_CREDENTIALS", 250000, 1, 5000000)
    security_privacy_history_limit: int = _int("SC_LAB_SECURITY_PRIVACY_HISTORY_LIMIT", 500000, 100, 10000000)
    service_credential_ttl_days: int = _int("SC_LAB_SERVICE_CREDENTIAL_TTL_DAYS", 90, 1, 365)
    security_require_request_nonce: bool = os.getenv("SC_LAB_REQUIRE_REQUEST_NONCE", "1").lower() not in {"0", "false", "no"}
    security_replay_db_path: str = os.getenv("SC_LAB_SECURITY_REPLAY_DB_PATH", "./data/sc-lab-request-replay.sqlite3").strip()
    security_privacy_persistent_disk_mounted: bool = os.getenv("SC_LAB_SECURITY_PRIVACY_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_INSTITUTIONAL_GOVERNANCE_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}

    multi_instance_operations_db_path: str = os.getenv("SC_LAB_MULTI_INSTANCE_OPERATIONS_DB_PATH", "./data/sc-lab-multi-instance-operations.sqlite3").strip()
    multi_instance_backup_root: str = os.getenv("SC_LAB_BACKUP_ROOT", "./data/sc-lab-backups").strip()
    instance_id: str = os.getenv("SC_LAB_INSTANCE_ID", "").strip()
    instance_name: str = os.getenv("SC_LAB_INSTANCE_NAME", "Sustainable Catalyst Lab").strip()
    instance_environment: str = os.getenv("SC_LAB_INSTANCE_ENVIRONMENT", "development").strip()
    instance_region: str = os.getenv("SC_LAB_INSTANCE_REGION", "local").strip()
    instance_public_url: str = os.getenv("SC_LAB_INSTANCE_PUBLIC_URL", "").strip()
    backup_signing_secret: str = os.getenv("SC_LAB_BACKUP_SIGNING_SECRET", os.getenv("SC_LAB_AUDIT_SIGNING_SECRET", os.getenv("SC_LAB_COMPUTE_SIGNING_SECRET", ""))).strip()
    multi_instance_max_backups: int = _int("SC_LAB_MULTI_INSTANCE_MAX_BACKUPS", 1000, 1, 100000)
    multi_instance_max_bundle_bytes: int = _int("SC_LAB_MULTI_INSTANCE_MAX_BUNDLE_BYTES", 2147483648, 1048576, 1099511627776)
    multi_instance_history_limit: int = _int("SC_LAB_MULTI_INSTANCE_HISTORY_LIMIT", 250000, 100, 10000000)
    recovery_rpo_hours: int = _int("SC_LAB_RECOVERY_RPO_HOURS", 24, 1, 8760)
    recovery_rto_minutes: int = _int("SC_LAB_RECOVERY_RTO_MINUTES", 240, 1, 10080)
    multi_instance_persistent_disk_mounted: bool = os.getenv("SC_LAB_MULTI_INSTANCE_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_SECURITY_PRIVACY_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    performance_validation_db_path: str = os.getenv("SC_LAB_PERFORMANCE_VALIDATION_DB_PATH", "./data/sc-lab-performance-validation.sqlite3").strip()
    performance_validation_max_concurrency: int = _int("SC_LAB_PERFORMANCE_VALIDATION_MAX_CONCURRENCY", 32, 1, 128)
    performance_validation_max_iterations: int = _int("SC_LAB_PERFORMANCE_VALIDATION_MAX_ITERATIONS", 2000, 1, 100000)
    performance_validation_history_limit: int = _int("SC_LAB_PERFORMANCE_VALIDATION_HISTORY_LIMIT", 10000, 100, 1000000)
    performance_validation_default_p95_ms: int = _int("SC_LAB_PERFORMANCE_VALIDATION_DEFAULT_P95_MS", 250, 1, 60000)
    performance_validation_default_error_rate_ppm: int = _int("SC_LAB_PERFORMANCE_VALIDATION_DEFAULT_ERROR_RATE_PPM", 10000, 0, 1000000)
    performance_validation_persistent_disk_mounted: bool = os.getenv("SC_LAB_PERFORMANCE_VALIDATION_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_MULTI_INSTANCE_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    platform_beta_db_path: str = os.getenv("SC_LAB_PLATFORM_BETA_DB_PATH", "./data/sc-lab-platform-beta.sqlite3").strip()
    platform_beta_telemetry_enabled: bool = os.getenv("SC_LAB_PLATFORM_BETA_TELEMETRY_ENABLED", "0").lower() in {"1", "true", "yes"}
    platform_beta_history_limit: int = _int("SC_LAB_PLATFORM_BETA_HISTORY_LIMIT", 250000, 100, 5000000)
    platform_beta_max_records: int = _int("SC_LAB_PLATFORM_BETA_MAX_RECORDS", 100000, 100, 2000000)
    platform_beta_persistent_disk_mounted: bool = os.getenv("SC_LAB_PLATFORM_BETA_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_PERFORMANCE_VALIDATION_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    interface_finalization_db_path: str = os.getenv("SC_LAB_INTERFACE_FINALIZATION_DB_PATH", "./data/sc-lab-interface-finalization.sqlite3").strip()
    interface_offline_shell_enabled: bool = os.getenv("SC_LAB_INTERFACE_OFFLINE_SHELL_ENABLED", "1").lower() not in {"0", "false", "no"}
    interface_finalization_history_limit: int = _int("SC_LAB_INTERFACE_FINALIZATION_HISTORY_LIMIT", 250000, 100, 5000000)
    interface_max_snapshot_assets: int = _int("SC_LAB_INTERFACE_MAX_SNAPSHOT_ASSETS", 5000, 1, 100000)
    interface_max_queue_records: int = _int("SC_LAB_INTERFACE_MAX_QUEUE_RECORDS", 100000, 100, 2000000)
    interface_finalization_persistent_disk_mounted: bool = os.getenv("SC_LAB_INTERFACE_FINALIZATION_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_PLATFORM_BETA_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    public_release_hardening_db_path: str = os.getenv("SC_LAB_PUBLIC_RELEASE_HARDENING_DB_PATH", "./data/sc-lab-public-release-hardening.sqlite3").strip()
    public_release_hardening_history_limit: int = _int("SC_LAB_PUBLIC_RELEASE_HARDENING_HISTORY_LIMIT", 250000, 100, 5000000)
    public_release_migration_execution_enabled: bool = os.getenv("SC_LAB_PUBLIC_RELEASE_MIGRATION_EXECUTION_ENABLED", "0").lower() in {"1", "true", "yes"}
    public_release_hardening_persistent_disk_mounted: bool = os.getenv("SC_LAB_PUBLIC_RELEASE_HARDENING_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_INTERFACE_FINALIZATION_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}
    stable_platform_db_path: str = os.getenv("SC_LAB_STABLE_PLATFORM_DB_PATH", "./data/sc-lab-stable-platform.sqlite3").strip()
    stable_platform_history_limit: int = _int("SC_LAB_STABLE_PLATFORM_HISTORY_LIMIT", 250000, 100, 5000000)
    stable_platform_persistent_disk_mounted: bool = os.getenv("SC_LAB_STABLE_PLATFORM_PERSISTENT_DISK_MOUNTED", os.getenv("SC_LAB_PUBLIC_RELEASE_HARDENING_PERSISTENT_DISK_MOUNTED", "0")).lower() in {"1", "true", "yes"}

    @property
    def auth_mode(self) -> str:
        if self.signing_secret:
            return "hmac-sha256"
        if self.api_key:
            return "api-key"
        return "open-development"


settings = Settings()
