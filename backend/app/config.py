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
    version: str = "0.32.1"
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

    @property
    def auth_mode(self) -> str:
        if self.signing_secret:
            return "hmac-sha256"
        if self.api_key:
            return "api-key"
        return "open-development"


settings = Settings()
