from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile

_TEST_DIR = Path(tempfile.mkdtemp(prefix="sc-lab-v0261-tests-"))
os.environ.setdefault("SC_LAB_JOB_DB_PATH", str(_TEST_DIR / "jobs.sqlite3"))
os.environ.setdefault("SC_LAB_JOB_WORKERS", "2")
os.environ.setdefault("SC_LAB_JOB_SCHEDULER_INTERVAL_SECONDS", "0.05")
os.environ.setdefault("SC_LAB_RETRY_BASE_DELAY_SECONDS", "1")
os.environ.setdefault("SC_LAB_MAX_RETRY_DELAY_SECONDS", "1")
os.environ.setdefault("SC_LAB_LOAD_LEGACY_EXTENSIONS", "0")


def pytest_sessionfinish(session, exitstatus):
    del session, exitstatus
    shutil.rmtree(_TEST_DIR, ignore_errors=True)
