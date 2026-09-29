"""Lab v0.139.0.1 release-manifest scope and integrity repair diagnostics."""
from __future__ import annotations

VERSION = "0.139.0.1"
BASE_RELEASE = "0.139.0"
BOUNDARY = (
    "This patch repairs release packaging and integrity diagnostics only. "
    "It does not alter scientific results, scholarly-package semantics, review state, "
    "reproducibility conclusions, or publication status."
)


def health() -> dict:
    return {
        "ok": True,
        "version": VERSION,
        "baseRelease": BASE_RELEASE,
        "repair": "wordpress-release-manifest-scope",
        "wordpressManifestScopeRepair": True,
        "backendScientificRuntimeChanged": False,
        "boundary": BOUNDARY,
    }


def policy() -> dict:
    return {
        "ok": True,
        "version": VERSION,
        "policy": {
            "wordpressCriticalFiles": "must contain only files shipped in the WordPress plugin package",
            "backendCriticalFiles": "must contain only files shipped in the backend package",
            "missingPackagedCriticalFilesPermitted": False,
            "scientificSemanticsChanged": False,
            "upgradeGate": "runtime/health must report verified before v0.140.0",
        },
        "boundary": BOUNDARY,
    }
