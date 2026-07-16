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
    version: str = "0.29.0"
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

    @property
    def auth_mode(self) -> str:
        if self.signing_secret:
            return "hmac-sha256"
        if self.api_key:
            return "api-key"
        return "open-development"


settings = Settings()
