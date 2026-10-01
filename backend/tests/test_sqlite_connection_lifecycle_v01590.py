import sqlite3
import tempfile
from pathlib import Path

from app.batch_experiment_sweep_ensemble_v01550 import BatchExperimentCampaignManager
from app.distributed_hpc_accelerated_coordination_v01560 import DistributedHPCCoordinationManager
from app.cross_study_replication_meta_experiment_v01570 import CrossStudyReplicationMetaExperimentManager
from app.scientific_reproduction_independent_replication_network_v01580 import ScientificReproductionIndependentReplicationNetworkManager
from app.integrated_scientific_review_validation_publication_gate_v01590 import IntegratedScientificReviewValidationPublicationGateManager


def _assert_context_closes(manager):
    with manager._connect() as db:
        db.execute("SELECT 1").fetchone()
    try:
        db.execute("SELECT 1")
    except sqlite3.ProgrammingError as exc:
        assert "closed" in str(exc).lower()
    else:
        raise AssertionError("SQLite connection remained open after context exit")


def test_v01550_v01590_sqlite_contexts_close_file_descriptors():
    with tempfile.TemporaryDirectory() as t:
        root=Path(t)
        managers=[
            BatchExperimentCampaignManager(str(root/"155.sqlite3")),
            DistributedHPCCoordinationManager(str(root/"156.sqlite3")),
            CrossStudyReplicationMetaExperimentManager(str(root/"157.sqlite3")),
            ScientificReproductionIndependentReplicationNetworkManager(str(root/"158.sqlite3")),
            IntegratedScientificReviewValidationPublicationGateManager(str(root/"159.sqlite3")),
        ]
        for manager in managers:
            for _ in range(25):
                _assert_context_closes(manager)
