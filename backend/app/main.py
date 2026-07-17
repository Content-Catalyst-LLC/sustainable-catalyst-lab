from __future__ import annotations

import base64
import io
import hmac
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas

from .benchmarks import catalog as benchmark_catalog, resolve as resolve_benchmark, run_benchmark, run_convergence, run_suite
from .compute import ComputeExecutionError, run_compute
from .config import settings
from .extensions import load_legacy_extensions
from .jobs import InvalidJobStateError, PersistentJobQueue, ProjectLimitError, QueueCapacityError
from .precision import policy_catalog, recommend
from .visualization import VisualizationInputError, build_spec as build_visualization_spec, catalog as visualization_catalog, csv_text as visualization_csv
from .datasets import DatasetProfileError, health as dataset_health_payload, profile_dataset
from .reproducibility import ReproducibilityError, build_manifest as build_reproducibility_manifest, compare_manifests, environment_fingerprint, health as reproducibility_health_payload, verify_manifest
from .research_provenance import ProvenanceError, health as research_provenance_health, normalize_source, normalize_evidence, verify_record as verify_provenance_record, build_provenance
from .research_quality import QualityReviewError, compare_reviews as compare_quality_reviews, evaluate_review as evaluate_quality_review, health as research_quality_health, normalize_review as normalize_quality_review, policies as research_quality_policies, verify_review as verify_quality_review
from .external_discovery import DiscoveryError, build_openurl as build_discovery_openurl, deduplicate as deduplicate_discovery, health as external_discovery_health, normalize as normalize_discovery, open_access_lookup, provider_catalog as discovery_provider_catalog, search as search_discovery
from .experiment_framework import ExperimentFrameworkError, build_report as build_experiment_report, build_run as build_experiment_run, compare_runs as compare_experiment_runs, health as experiment_framework_health, normalize_protocol, policies as experiment_framework_policies, validate_protocol, verify as verify_experiment_record
from .design_studies import DesignStudyError, analyze_results as analyze_design_results, build_batch as build_design_batch, generate_design, health as design_studies_health, normalize_study, policies as design_studies_policies, recommend_design, verify as verify_design_record
from .model_calibration import ModelCalibrationError, build_report as build_calibration_report, calibrate as calibrate_model, compare_models, health as model_calibration_health, normalize_study as normalize_calibration_study, policies as model_calibration_policies, validate_result as validate_calibration_result, verify as verify_calibration_record
from .distributed_dispatcher import DispatcherError, policies as distributed_dispatcher_policies
from .persistent_dispatch_queue import PersistentDistributedDispatcher
from .worker_agent_runtime import WorkerAgentError, policies as worker_agent_policies
from .artifact_transport import ArtifactStore, ArtifactTransportError
from .workflow_orchestration import WorkflowError, WorkflowOrchestrator, policies as workflow_policies
from .workflow_scheduling import WorkflowScheduleError, WorkflowScheduler, policies as workflow_scheduling_policies, verify_event_signature
from .experiment_campaigns import ExperimentCampaignError, ExperimentCampaignManager, policies as experiment_campaign_policies
from .closed_loop_campaigns import ClosedLoopError, ClosedLoopCampaignManager, policies as closed_loop_policies
from .model_registry import ModelRegistryError, ScientificModelRegistry, capture_environment, policies as model_registry_policies
from .ensemble_uncertainty import EnsembleError, EnsembleStudyManager, policies as ensemble_policies
from .surrogate_reduced_order import SurrogateROMError, SurrogateReducedOrderManager, policies as surrogate_rom_policies
from .team_workspaces import TeamWorkspaceError, TeamWorkspaceManager, policies as team_workspace_policies
from .workspace_reviews import WorkspaceReviewError, WorkspaceReviewManager, policies as workspace_review_policies
from .workspace_versioning import WorkspaceVersionError, WorkspaceVersionManager, policies as workspace_version_policies
from .registry import catalog, resolve
from .schemas import ComputeRequest, ComputeResponse
from .security import require_compute_auth


jobs = PersistentJobQueue()
dispatcher = PersistentDistributedDispatcher(settings.dispatcher_db_path, settings.dispatcher_worker_stale_seconds, settings.dispatcher_default_lease_seconds, settings.dispatcher_max_workers, settings.dispatcher_max_queue_records, settings.dispatcher_max_attempts, settings.dispatcher_history_limit, settings.dispatcher_retry_base_delay_seconds, settings.dispatcher_retry_max_delay_seconds)
artifacts = ArtifactStore(settings.artifact_root, settings.artifact_db_path, settings.artifact_max_bytes, settings.artifact_chunk_bytes, settings.artifact_upload_ttl_seconds, settings.artifact_retention_seconds)
workflows = WorkflowOrchestrator(settings.workflow_db_path, dispatcher, settings.workflow_max_nodes, settings.workflow_max_runs, settings.workflow_history_limit)
workflow_automation = WorkflowScheduler(settings.workflow_schedule_db_path, workflows, settings.workflow_scheduler_poll_seconds, settings.workflow_scheduler_max_catch_up_runs, settings.workflow_scheduler_history_limit)
experiment_campaigns = ExperimentCampaignManager(settings.experiment_campaign_db_path, workflows, settings.experiment_campaign_poll_seconds, settings.experiment_campaign_max_campaigns, settings.experiment_campaign_max_trials, settings.experiment_campaign_history_limit)
closed_loop_campaigns = ClosedLoopCampaignManager(settings.closed_loop_db_path, experiment_campaigns, settings.closed_loop_poll_seconds, settings.closed_loop_max_loops, settings.closed_loop_max_cycles, settings.closed_loop_history_limit, settings.closed_loop_measurement_secret)
model_registry = ScientificModelRegistry(settings.model_registry_db_path, settings.model_registry_max_models, settings.model_registry_max_versions, settings.model_registry_history_limit)
ensemble_studies = EnsembleStudyManager(settings.ensemble_study_db_path, model_registry, dispatcher, settings.ensemble_max_studies, settings.ensemble_max_evaluations, settings.ensemble_history_limit)
surrogate_rom = SurrogateReducedOrderManager(settings.surrogate_rom_db_path, model_registry, settings.surrogate_rom_max_studies, settings.surrogate_rom_max_training_rows, settings.surrogate_rom_max_snapshot_dimensions, settings.surrogate_rom_history_limit)
team_workspaces = TeamWorkspaceManager(settings.team_workspace_db_path, settings.team_workspace_max_workspaces, settings.team_workspace_max_members, settings.team_workspace_history_limit)
workspace_reviews = WorkspaceReviewManager(settings.team_workspace_db_path, settings.team_workspace_history_limit)
workspace_versions = WorkspaceVersionManager(settings.team_workspace_db_path, settings.team_workspace_history_limit)


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.extensions = (
        load_legacy_extensions(application)
        if settings.extension_loading
        else {"loaded": [], "failed": {}}
    )
    jobs.start()
    workflow_automation.start()
    experiment_campaigns.start()
    closed_loop_campaigns.start()
    yield
    closed_loop_campaigns.stop()
    experiment_campaigns.stop()
    workflow_automation.stop()
    jobs.stop()


app = FastAPI(
    title=settings.service_name,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_limits(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH"}:
        body = await request.body()
        if "/artifacts/uploads/" in request.url.path and request.url.path.endswith("/chunks"):
            limit = settings.artifact_chunk_bytes
        elif request.url.path.startswith("/v1/surrogate-rom/"):
            limit = settings.surrogate_rom_max_request_bytes
        else:
            limit = settings.max_request_bytes
        if len(body) > limit:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request exceeds the configured size limit."},
            )
    return await call_next(request)


def execute_or_http(payload: ComputeRequest, auth: dict[str, str]) -> ComputeResponse:
    try:
        return run_compute(payload, auth)
    except ComputeExecutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


def job_payload(source: dict[str, Any]) -> ComputeRequest:
    return ComputeRequest(
        method=str(source.get("methodId") or source.get("method") or ""),
        version=source.get("version"),
        inputs=source.get("inputs") or {},
        parameters=source.get("parameters") or {},
        units=source.get("units") or {},
        project_id=source.get("project_id") or source.get("projectId"),
        requested_outputs=source.get("requested_outputs") or source.get("requestedOutputs") or ["summary", "values"],
        random_seed=source.get("random_seed") if source.get("random_seed") is not None else source.get("randomSeed"),
        governance=source.get("governance") or {},
    )


@app.get("/health")
def health():
    queue_state = jobs.queue_status()
    return {
        "ok": True,
        "status": "ready",
        "service": settings.service_name,
        "version": settings.version,
        "architecture": "python-compute-core",
        "authMode": settings.auth_mode,
        "methodCount": len(catalog()),
        "benchmarkCount": len(benchmark_catalog()),
        "solverGovernance": {"version": "0.27.3", "profiles": 4, "referenceComparison": True, "unitAwareValidation": True},
        "scientificVisualization": {"version": "0.27.4", "profiles": len(visualization_catalog()["profiles"]), "formats": ["svg", "png", "csv", "json"]},
        "projectWorkspace": {"version": "0.28.0", "contextEnvelope": True, "serverBackedStorage": False},
        "datasetRegistry": {"version": "0.28.1", "profiling": True, "formats": ["csv", "json", "geojson", "netcdf", "tabular"], "serverBackedRegistry": False},
        "reproducibility": {"version": "0.28.2", "manifests": True, "verification": True, "comparison": True, "serverBackedRegistry": False},
        "researchProvenance": {"version":"0.29.0","sources":True,"evidence":True,"citations":True,"assumptions":True,"limitations":True},
        "researchQuality": {"version":"0.29.1","methodReview":True,"benchmarkCoverage":True,"calibration":True,"approvalWorkflow":True,"deprecationHistory":True},
        "externalDiscovery": {"version":"0.29.2","providers":["crossref","openalex","datacite"],"worldCatHandoff":True,"openUrlHandoff":True,"deduplication":True,"sourceImport":True},
        "experimentFramework": {"version":"0.30.0","protocols":True,"runHistories":True,"replications":True,"comparisons":True,"reports":True},
        "designStudies": {"version":"0.30.1","factorial":True,"latinHypercube":True,"responseSurfaces":True,"sensitivity":True,"batchPlans":True},
        "modelCalibration": {"version":"0.30.2","parameterFitting":True,"holdoutValidation":True,"confidenceIntervals":True,"residualDiagnostics":True,"modelComparison":True},
        "distributedDispatcher": {"version":"0.31.0","capabilityDiscovery":True,"workloadRouting":True,"signedDispatchContracts":True,"leases":True},
        "persistentQueueInfrastructure": {"version":"0.31.1","storage":"sqlite-wal","persistentWorkerRegistry":True,"persistentWorkloadQueue":True,"leaseRecovery":True},
        "secureWorkerAgent": {"version":"0.32.1","pullBased":True,"workerScopedCredentials":True,"signedContractVerification":True,"registeredMethodsOnly":True,"leaseRenewal":True,"completionReceipts":True,"artifactTransport":True},
        "artifactTransport": {"version":"0.31.3","contentAddressed":True,"resumable":True,"sha256Verification":True,"resultArtifacts":True,"checkpointArtifacts":True,"retentionControls":True},
        "dispatcherOperations": {"version":"0.31.4","failureClassification":True,"boundedRetries":True,"deadLetterRecovery":True,"operatorReplay":True,"queueMetrics":True,"databaseDiagnostics":True},
        "workflowOrchestration": {"version":"0.32.1","typedDefinitions":True,"dagValidation":True,"dependencyAwareScheduling":True,"parallelReadyNodes":True,"resultBindings":True,"artifactHandoffs":True,"runProvenance":True,"declarativeConditions":True,"checkpointHistory":True,"partialRecovery":True,"recoveryLineage":True},
        "workflowAutomation": {"version":"0.32.2","intervalSchedules":True,"cronUtc":True,"oneTimeSchedules":True,"authenticatedEvents":True,"eventDeduplication":True,"misfireRecovery":True,"concurrencyControls":True},
        "experimentCampaigns": {"version":"0.33.1","adaptiveSequentialDesign":True,"workflowBackedTrials":True,"gaussianProcessSurrogate":True,"predictiveUncertainty":True,"activeLearning":True,"resourceAwareSearch":True,"costAdjustedAcquisition":True},
        "closedLoopCampaigns": {"version":"0.33.2","simulationLoops":True,"instrumentMeasurementIngestion":True,"hybridCampaigns":True,"safetyInterlocks":True,"operatorCommandApproval":True,"checkpointedCycles":True,"directDeviceExecution":False},
        "scientificModelRegistry": {"version":"0.34.0","immutableVersions":True,"environmentCapture":True,"dependencyLocking":True,"reproductionManifests":True,"promotionWorkflow":True,"deprecationHistory":True},
        "ensembleSimulation": {"version":"0.34.1","registeredModelMembers":True,"weightedEnsembles":True,"monteCarlo":True,"latinHypercube":True,"sobolDesign":True,"globalSensitivity":True,"uncertaintyIntervals":True},
        "surrogateReducedOrder": {"version":"0.34.2","surrogateTraining":True,"gaussianProcess":True,"polynomialRidge":True,"radialBasis":True,"properOrthogonalDecomposition":True,"hybridRom":True,"validationMetrics":True,"modelRegistryIntegration":True},
        "sharedResearchWorkspaces": {"version":"0.35.0","roleBasedMembership":True,"singleUseInvitations":True,"governedResourceLinks":True,"ownershipTransfer":True,"archiveWithoutDeletion":True},
        "workspaceReviewSignoff": {"version":"0.35.1","appendOnlyComments":True,"reviewAssignments":True,"approvalGates":True,"optimisticConcurrency":True,"immutableDecisions":True,"immutableScientificSignoff":True},
        "workspaceVersionControl": {"version":"0.35.2","immutableSnapshots":True,"namedBranches":True,"threeWayMerge":True,"pathLevelConflicts":True,"protectedBranches":True,"signedApprovalGate":True,"historyRewrite":False},
        "extensionLoading": settings.extension_loading,
        "extensions": getattr(app.state, "extensions", {"loaded": [], "failed": {}}),
        "queue": {
            "persistent": queue_state["persistent"],
            "storage": queue_state["storage"],
            "schema": queue_state["schema"],
            "deploymentDurability": "persistent-disk" if settings.dispatcher_persistent_disk_mounted else "instance-local",
            "durabilityWarning": None if settings.dispatcher_persistent_disk_mounted else "SQLite queue files are instance-local unless a persistent disk is mounted at /app/data.",
            "activeWorkers": queue_state["activeWorkers"],
            "workerCapacity": queue_state["workerCapacity"],
            "queued": queue_state["counts"]["queued"] + queue_state["counts"]["retrying"],
            "paused": queue_state["counts"]["paused"],
            "checkpointRecovery": queue_state["checkpointRecovery"],
            "priorityScheduling": queue_state["priorityScheduling"],
            "maxActiveJobsPerProject": queue_state["maxActiveJobsPerProject"],
            "cache": queue_state["cache"],
        },
    }


@app.get("/version")
def version():
    return {"version": settings.version, "service": settings.service_name}


@app.get("/v1/capabilities", dependencies=[Depends(require_compute_auth)])
def capabilities():
    return {
        "schema": "sc-lab-compute-capabilities/1.4",
        "version": settings.version,
        "executionTargets": ["python-core-cpu", "isolated-process-worker", "browser-web-worker", "local-python", "raspberry-pi", "institutional-node"],
        "modes": ["synchronous", "persistent-queued", "checkpointed-queued", "cached-queued"],
        "packages": ["numpy", "scipy", "pandas", "sympy", "reportlab"],
        "numericalMethods": {"registeredOnly": True, "differentialEquations": True, "optimization": True, "signalProcessing": True, "uncertainty": True, "sensitivity": True, "parameterSweeps": True, "benchmarkLibrary": True, "knownAnswerFixtures": True, "convergenceDiagnostics": True, "solverGovernance": True, "precisionProfiles": True, "conditionDiagnostics": True, "referenceMethodComparisons": True, "scientificVisualization": True, "accessibleSvg": True, "exportFormats": ["svg", "png", "csv", "json"]},
        "benchmarks": {"count": len(benchmark_catalog()), "crossImplementation": ["python-core", "analytic-reference", "browser-reference"], "toleranceControls": True, "unitAssertions": True},
        "security": {
            "authMode": settings.auth_mode,
            "arbitraryCode": False,
            "registeredMethodsOnly": True,
            "requestLimitBytes": settings.max_request_bytes,
            "hardWorkerTermination": True,
        },
        "jobs": {
            "persistent": True,
            "storage": "sqlite-wal",
            "states": ["queued", "running", "paused", "completed", "failed", "cancelled", "timed_out", "retrying"],
            "workerCount": settings.job_workers,
            "maxQueuedJobs": settings.max_queued_jobs,
            "defaultTimeoutSeconds": settings.default_job_timeout_seconds,
            "maxTimeoutSeconds": settings.max_job_timeout_seconds,
            "defaultAttempts": settings.default_job_attempts,
            "maxAttempts": settings.max_job_attempts,
            "deduplication": True,
            "restartRecovery": True,
            "checkpointRecovery": True,
            "partialResultInspection": True,
            "priorityScheduling": True,
            "resultCaching": True,
            "maxActiveJobsPerProject": settings.max_active_jobs_per_project,
        },
        "solverGovernance": {"version": "0.27.3", "profiles": 4, "manualSolverSelection": True, "automaticRecommendations": True, "unitAwareValidation": True, "referenceMethodComparisons": True, "floatingPointReporting": True},
        "scientificVisualization": {"version": "0.27.4", "profiles": len(visualization_catalog()["profiles"]), "serverNormalizedSpecs": True, "accessibleDescriptions": True, "tabularFallback": True},
        "projectWorkspace": {"version": "0.28.0", "projectContextAccepted": True, "serverBackedStorage": False},
        "datasetRegistry": {"version": "0.28.1", "profileEndpoint": True, "dataDictionary": True, "unitMetadata": True, "lineage": True, "serverBackedRegistry": False},
        "reproducibility": {"version": "0.28.2", "frozenManifests": True, "environmentFingerprint": True, "verification": True, "comparison": True, "portableBundles": True, "serverBackedRegistry": False},
        "researchQuality": {"version":"0.29.1","reviewNormalization":True,"policyEvaluation":True,"hashVerification":True,"revisionComparison":True,"serverBackedRegistry":False},
        "externalDiscovery": {"version":"0.29.2","liveProviders":["crossref","openalex","datacite"],"handoffs":["worldcat","google-scholar","openurl"],"deduplication":True,"sourceImport":True,"arbitraryRemoteFetch":False},
        "experimentFramework": {"version":"0.30.0","protocolNormalization":True,"readinessValidation":True,"runManifests":True,"replicationComparison":True,"reportBuilder":True,"serverBackedRegistry":False},
        "designStudies": {"version":"0.30.1","designGeneration":True,"responseSurfaceAnalysis":True,"sensitivityRanking":True,"optimalDesignRecommendation":True,"queueBatchPlans":True,"serverBackedRegistry":False},
        "persistentQueueInfrastructure": {"version":"0.31.1","storage":"sqlite-wal","persistentWorkerRegistry":True,"persistentWorkloadQueue":True,"leaseRecovery":True,"horizontalCoordinatorSafeClaims":True,"centralHistory":True},
        "secureWorkerAgent": {"version":"0.32.1","pullBased":True,"workerScopedCredentials":True,"credentialRotation":True,"credentialRevocation":True,"signedContractVerification":True,"registeredMethodsOnly":True,"leaseRenewal":True,"completionReceipts":True,"artifactTransport":True},
        "artifactTransport": {"version":"0.31.3","contentAddressed":True,"resumableChunks":True,"sha256Verification":True,"deduplication":True,"inputMaterialization":True,"resultExternalization":True,"checkpointTransport":True,"retentionControls":True},
        "workflowOrchestration": {"version":"0.32.1","typedDefinitions":True,"dagValidation":True,"dependencyAwareScheduling":True,"parallelReadyNodes":True,"resultBindings":True,"artifactHandoffs":True,"runProvenance":True,"serverBackedRegistry":True,"declarativeConditions":True,"checkpointHistory":True,"partialRecovery":True,"recoveryLineage":True},
        "experimentCampaigns": {"version":"0.33.1","adaptiveSequentialDesign":True,"gaussianProcessSurrogate":True,"activeLearning":True,"resourceAwareSearch":True},
        "closedLoopCampaigns": {"version":"0.33.2","simulation":True,"instrument":True,"hybrid":True,"signedMeasurements":True,"safetyInterlocks":True,"operatorApproval":True,"directDeviceExecution":False},
        "scientificModelRegistry": {"version":"0.34.0","modelVersioning":True,"environmentCapture":True,"dependencyLocks":True,"reproductionVerification":True,"promotionChannels":["candidate","production","archived"],"arbitraryCode":False},
        "ensembleSimulation": {"version":"0.34.1","weightedRegisteredModels":True,"samplingDesigns":["monte-carlo","latin-hypercube","sobol","saltelli-sobol"],"uncertaintyPropagation":True,"globalSensitivity":True,"arbitraryCode":False},
        "surrogateReducedOrder": {"version":"0.34.2","algorithms":["polynomial-ridge","radial-basis","gaussian-process"],"properOrthogonalDecomposition":True,"hybridReducedOrderModels":True,"holdoutValidation":True,"errorBounds":True,"registryPublication":True,"arbitraryCode":False},
        "provenanceSchema": "sc-lab-compute-provenance/1.1",
        "methodCount": len(catalog()),
        "legacyExtensions": getattr(app.state, "extensions", {"loaded": [], "failed": {}}),
    }


@app.get("/v1/governance/health")
def governance_health():
    catalog = policy_catalog()
    return {"ok": True, "status": "ready", "version": "0.27.3", "serviceVersion": settings.version, "architecture": "solver-precision-governance", "profileCount": len(catalog["profiles"]), "governedMethodCount": len(catalog["solvers"]), "unitAwareValidation": True, "referenceComparison": True}


@app.get("/v1/governance/policies", dependencies=[Depends(require_compute_auth)])
def governance_policies():
    return policy_catalog()


@app.post("/v1/governance/recommend")
def governance_recommend(payload: ComputeRequest, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        method_record = resolve(payload.method)
        return {"ok": True, "version": "0.27.3", "recommendation": recommend(payload, method_record), "request": payload.model_dump(mode="json", by_alias=True)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/governance/compare", response_model=ComputeResponse)
def governance_compare(payload: ComputeRequest, auth: dict[str, str] = Depends(require_compute_auth)):
    data = payload.model_dump(mode="json", by_alias=True)
    data.setdefault("governance", {})["referenceComparison"] = True
    return execute_or_http(ComputeRequest.model_validate(data), auth)


@app.get("/v1/visualization/health")
def visualization_health():
    catalog_data = visualization_catalog()
    return {"ok": True, "status": "ready", "version": "0.27.4", "serviceVersion": settings.version, "architecture": "governed-numerical-visualization", "profileCount": len(catalog_data["profiles"]), "formats": catalog_data["formats"], "accessibleSvg": True, "tabularFallback": True}


@app.get("/v1/visualization/profiles", dependencies=[Depends(require_compute_auth)])
def visualization_profiles():
    return visualization_catalog()


@app.post("/v1/visualization/spec")
def visualization_spec(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return build_visualization_spec(payload)
    except VisualizationInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/visualization/csv")
def visualization_csv_export(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        spec = build_visualization_spec(payload)
    except VisualizationInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "version": "0.27.4", "mimeType": "text/csv", "filename": "scientific-visualization.csv", "text": visualization_csv(spec), "spec": spec}


@app.get("/v1/datasets/health")
def datasets_health():
    body = dataset_health_payload()
    body["serviceVersion"] = settings.version
    return body


@app.post("/v1/datasets/profile")
def datasets_profile(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return profile_dataset(payload)
    except DatasetProfileError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc



@app.get("/v1/reproducibility/health")
def reproducibility_health():
    body = reproducibility_health_payload(); body["serviceVersion"] = settings.version; return body

@app.get("/v1/reproducibility/environment", dependencies=[Depends(require_compute_auth)])
def reproducibility_environment():
    return {"ok": True, "version": "0.28.2", "environment": environment_fingerprint()}

@app.post("/v1/reproducibility/manifest")
def reproducibility_manifest(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return build_reproducibility_manifest(payload)
    except ReproducibilityError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/reproducibility/verify")
def reproducibility_verify(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return verify_manifest(payload)
    except ReproducibilityError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/reproducibility/compare")
def reproducibility_compare(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return compare_manifests(payload)
    except ReproducibilityError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/research-provenance/health")
def research_provenance_health_route():
    body=research_provenance_health(); body["serviceVersion"]=settings.version; return body

@app.post("/v1/research-provenance/sources/normalize")
def research_source_normalize(payload: dict[str, Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return {"ok":True,"source":normalize_source(payload)}
    except ProvenanceError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/research-provenance/evidence/normalize")
def research_evidence_normalize(payload: dict[str, Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return {"ok":True,"evidence":normalize_evidence(payload)}
    except ProvenanceError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/research-provenance/verify")
def research_provenance_verify_route(payload: dict[str, Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth; return verify_provenance_record(payload)

@app.post("/v1/research-provenance/build")
def research_provenance_build_route(payload: dict[str, Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth; return {"ok":True,"provenance":build_provenance(payload)}


@app.get("/v1/research-quality/health")
def research_quality_health_route():
    body = research_quality_health()
    body["serviceVersion"] = settings.version
    return body


@app.get("/v1/research-quality/policies")
def research_quality_policies_route():
    body = research_quality_policies()
    body["serviceVersion"] = settings.version
    return body


@app.post("/v1/research-quality/reviews/normalize")
def research_quality_normalize_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return {"ok": True, "review": normalize_quality_review(payload)}
    except QualityReviewError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/research-quality/reviews/evaluate")
def research_quality_evaluate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return evaluate_quality_review(payload)
    except QualityReviewError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/research-quality/reviews/verify")
def research_quality_verify_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return verify_quality_review(payload)


@app.post("/v1/research-quality/reviews/compare")
def research_quality_compare_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return compare_quality_reviews(payload)
    except QualityReviewError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/discovery/health")
def discovery_health_route():
    body=external_discovery_health(); body["serviceVersion"]=settings.version; return body


@app.get("/v1/discovery/providers")
def discovery_providers_route():
    body=discovery_provider_catalog(); body["serviceVersion"]=settings.version; return body


@app.post("/v1/discovery/search")
def discovery_search_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return search_discovery(payload)
    except DiscoveryError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/discovery/normalize")
def discovery_normalize_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return normalize_discovery(payload)
    except DiscoveryError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/discovery/deduplicate")
def discovery_deduplicate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return deduplicate_discovery(payload)
    except DiscoveryError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/discovery/open-access")
def discovery_open_access_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return open_access_lookup(payload)
    except DiscoveryError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/discovery/openurl")
def discovery_openurl_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return build_discovery_openurl(payload)
    except DiscoveryError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/methods", dependencies=[Depends(require_compute_auth)])
def methods():
    return {"schema": "sc-lab-method-registry/1.0", "version": settings.version, "methods": catalog()}


@app.get("/v1/methods/{method_id}", dependencies=[Depends(require_compute_auth)])
def method(method_id: str):
    try:
        return resolve(method_id).public()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/v1/benchmarks", dependencies=[Depends(require_compute_auth)])
def benchmarks():
    return {"schema": "sc-lab-numerical-benchmark-catalog/1.0", "version": settings.version, "benchmarkCount": len(benchmark_catalog()), "benchmarks": benchmark_catalog()}


@app.get("/v1/benchmarks/{benchmark_id}", dependencies=[Depends(require_compute_auth)])
def benchmark(benchmark_id: str):
    try:
        return resolve_benchmark(benchmark_id).public()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/v1/benchmarks/run")
def benchmark_run(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    benchmark_id = str(payload.get("benchmarkId") or payload.get("benchmark_id") or "")
    if not benchmark_id:
        raise HTTPException(status_code=422, detail="benchmarkId is required.")
    try:
        return run_benchmark(benchmark_id, lambda request: run_compute(request, auth))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ComputeExecutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@app.post("/v1/benchmarks/run-suite")
def benchmark_suite(payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    benchmark_ids = None
    if isinstance(payload, dict) and isinstance(payload.get("benchmarkIds"), list):
        benchmark_ids = [str(value) for value in payload["benchmarkIds"][:100]]
    try:
        return run_suite(lambda request: run_compute(request, auth), benchmark_ids)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/v1/benchmarks/convergence")
def benchmark_convergence(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    benchmark_id = str(payload.get("benchmarkId") or payload.get("benchmark_id") or "")
    if not benchmark_id:
        raise HTTPException(status_code=422, detail="benchmarkId is required.")
    try:
        return run_convergence(benchmark_id, lambda request: run_compute(request, auth))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ComputeExecutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@app.post("/v1/compute/run", response_model=ComputeResponse)
def compute_run(payload: ComputeRequest, auth: dict[str, str] = Depends(require_compute_auth)):
    return execute_or_http(payload, auth)


@app.get("/v1/languages", dependencies=[Depends(require_compute_auth)])
def languages():
    return {
        "languages": [
            {"id": "python", "status": "native", "version": "3"},
            {"id": "javascript", "status": "browser-fallback"},
            {"id": "typescript", "status": "source-only"},
            {"id": "r", "status": "source-only"},
            {"id": "julia", "status": "source-only"},
            {"id": "rust", "status": "source-only"},
            {"id": "go", "status": "source-only"},
            {"id": "c", "status": "source-only"},
            {"id": "cpp", "status": "source-only"},
            {"id": "fortran", "status": "source-only"},
            {"id": "sql", "status": "source-only"},
            {"id": "haskell", "status": "source-only"},
        ]
    }


@app.post("/v1/validate")
def validate(payload: ComputeRequest, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        method_record = resolve(payload.method)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "method": method_record.public(), "request": payload.model_dump()}


@app.post("/v1/execute")
def execute_compat(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    language = str(payload.get("language") or "python").lower()
    if language != "python":
        raise HTTPException(
            status_code=422,
            detail=f"v0.26.1 executes Python natively; {language} remains a browser/source fallback.",
        )
    request = job_payload(payload)
    result = execute_or_http(request, auth)
    return {
        "ok": True,
        "methodId": payload.get("methodId") or request.method,
        "language": "python",
        "outputs": result.outputs,
        "result": result.model_dump(mode="json", by_alias=True),
        "provenance": result.provenance.model_dump(mode="json", by_alias=True),
    }


@app.post("/v1/compare")
def compare_compat(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    languages_requested = [str(v).lower() for v in payload.get("languages") or []]
    request = job_payload(payload)
    result = execute_or_http(request, auth)
    return {
        "ok": True,
        "methodId": payload.get("methodId"),
        "referenceLanguage": "python",
        "reference": result.outputs,
        "runs": [{"language": "python", "status": "completed", "outputs": result.outputs}]
        if "python" in languages_requested
        else [],
        "unsupported": [lang for lang in languages_requested if lang != "python"],
        "provenance": result.provenance.model_dump(mode="json", by_alias=True),
    }


@app.post("/v1/jobs", status_code=202)
def create_job(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    operation = str(payload.get("operation") or "core_run")
    if operation in {"execute", "core_run"}:
        source = payload.get("execute") or payload.get("request") or payload
    elif operation == "compare":
        source = payload.get("compare") or {}
    else:
        raise HTTPException(status_code=422, detail="Job operation must be execute, core_run, or compare.")

    try:
        request = job_payload(source)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    idempotency_key = str(payload.get("idempotencyKey") or payload.get("idempotency_key") or "") or None
    timeout_seconds = payload.get("timeoutSeconds") or payload.get("timeout_seconds") or source.get("timeoutSeconds")
    max_attempts = payload.get("maxAttempts") or payload.get("max_attempts")
    priority = payload.get("priority")
    cache_mode = payload.get("cacheMode") or payload.get("cache_mode") or "use"
    try:
        record, deduplicated = jobs.submit(
            operation=operation,
            payload=request.model_dump(mode="json"),
            auth=auth,
            timeout_seconds=int(timeout_seconds) if timeout_seconds is not None else None,
            max_attempts=int(max_attempts) if max_attempts is not None else None,
            idempotency_key=idempotency_key,
            priority=int(priority) if priority is not None else None,
            cache_mode=str(cache_mode),
        )
    except (QueueCapacityError, ProjectLimitError) as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    record["deduplicated"] = deduplicated
    return record


@app.get("/v1/jobs", dependencies=[Depends(require_compute_auth)])
def list_jobs(
    status: str | None = Query(default=None),
    project_id: str | None = Query(default=None, max_length=128),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        result = jobs.list(status=status, project_id=project_id, limit=limit, offset=offset)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"schema": "sc-lab-compute-job-list/1.0", **result}


@app.get("/v1/jobs/{job_id}", dependencies=[Depends(require_compute_auth)])
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.delete("/v1/jobs/{job_id}", dependencies=[Depends(require_compute_auth)])
def cancel_job_delete(job_id: str):
    job = jobs.cancel(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.post("/v1/jobs/{job_id}/cancel", dependencies=[Depends(require_compute_auth)])
def cancel_job(job_id: str):
    job = jobs.cancel(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.post("/v1/jobs/{job_id}/retry", dependencies=[Depends(require_compute_auth)])
def retry_job(job_id: str):
    try:
        job = jobs.retry(job_id)
    except InvalidJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.post("/v1/jobs/{job_id}/pause", dependencies=[Depends(require_compute_auth)])
def pause_job(job_id: str):
    try:
        job = jobs.pause(job_id)
    except InvalidJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.post("/v1/jobs/{job_id}/resume", dependencies=[Depends(require_compute_auth)])
def resume_job(job_id: str):
    try:
        job = jobs.resume(job_id)
    except InvalidJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.get("/v1/jobs/{job_id}/checkpoints", dependencies=[Depends(require_compute_auth)])
def job_checkpoints(job_id: str, limit: int = Query(default=20, ge=1, le=200)):
    result = jobs.checkpoints(job_id, limit=limit)
    if not result:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return result


@app.get("/v1/cache/status", dependencies=[Depends(require_compute_auth)])
def cache_status():
    return jobs.cache_status()


@app.delete("/v1/cache", dependencies=[Depends(require_compute_auth)])
def cache_purge():
    return jobs.purge_cache()


@app.get("/v1/workers", dependencies=[Depends(require_compute_auth)])
def workers():
    return jobs.workers_status()


@app.get("/v1/queue/status", dependencies=[Depends(require_compute_auth)])
def queue_status():
    return jobs.queue_status()


@app.post("/v1/reports/validate")
def report_validate(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    errors = []
    if not str(payload.get("title") or "").strip():
        errors.append("title is required")
    analyses = payload.get("analyses")
    if not isinstance(analyses, list) or not analyses:
        errors.append("at least one analysis is required")
    return {"ok": not errors, "valid": not errors, "errors": errors, "schema": "sc-lab-report-validation/1.0"}


@app.post("/v1/reports/pdf")
def report_pdf(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    validation = report_validate(payload, auth)
    if not validation["valid"]:
        raise HTTPException(status_code=422, detail=validation["errors"])
    buffer = io.BytesIO()
    pagesize = A4 if payload.get("pageSize") == "A4" else letter
    pdf = canvas.Canvas(buffer, pagesize=pagesize)
    _, height = pagesize
    pdf.setTitle(str(payload.get("title")))
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(54, height - 54, str(payload.get("title"))[:100])
    y = height - 86
    pdf.setFont("Helvetica", 10)
    for index, analysis in enumerate(payload.get("analyses") or [], 1):
        line = f"{index}. {analysis.get('title') or analysis.get('method') or 'Analysis'}"
        pdf.drawString(54, y, line[:120])
        y -= 16
        if y < 54:
            pdf.showPage()
            y = height - 54
            pdf.setFont("Helvetica", 10)
    pdf.save()
    raw = buffer.getvalue()
    return {
        "ok": True,
        "mimeType": "application/pdf",
        "filename": "sustainable-catalyst-lab-report.pdf",
        "base64": base64.b64encode(raw).decode("ascii"),
        "sizeBytes": len(raw),
    }


@app.post("/v1/handoffs/decision-studio/validate")
def handoff_validate(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    packet = payload.get("packet")
    valid = isinstance(packet, dict) and bool(packet)
    return {
        "ok": valid,
        "valid": valid,
        "errors": [] if valid else ["packet must be a non-empty object"],
        "schema": "sc-lab-decision-handoff-validation/1.0",
    }


@app.get("/v1/experiments/health")
def experiments_health_route():
    body=experiment_framework_health(); body["serviceVersion"]=settings.version; return body

@app.get("/v1/experiments/policies")
def experiments_policies_route():
    body=experiment_framework_policies(); body["serviceVersion"]=settings.version; return body

@app.post("/v1/experiments/protocols/normalize")
def experiments_protocol_normalize_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return normalize_protocol(payload)
    except ExperimentFrameworkError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/experiments/protocols/validate")
def experiments_protocol_validate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return validate_protocol(payload)
    except ExperimentFrameworkError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/experiments/runs/build")
def experiments_run_build_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return build_experiment_run(payload)
    except ExperimentFrameworkError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/experiments/runs/compare")
def experiments_runs_compare_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return compare_experiment_runs(payload)
    except ExperimentFrameworkError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/experiments/reports/build")
def experiments_report_build_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return build_experiment_report(payload)
    except ExperimentFrameworkError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/experiments/verify")
def experiments_verify_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return verify_experiment_record(payload)
    except ExperimentFrameworkError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/design-studies/health")
def design_studies_health_route():
    body=design_studies_health(); body["serviceVersion"]=settings.version; return body

@app.get("/v1/design-studies/policies")
def design_studies_policies_route():
    body=design_studies_policies(); body["serviceVersion"]=settings.version; return body

@app.post("/v1/design-studies/normalize")
def design_studies_normalize_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return normalize_study(payload)
    except DesignStudyError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/design-studies/generate")
def design_studies_generate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return generate_design(payload)
    except DesignStudyError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/design-studies/analyze")
def design_studies_analyze_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return analyze_design_results(payload)
    except DesignStudyError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/design-studies/recommend")
def design_studies_recommend_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return recommend_design(payload)
    except DesignStudyError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/design-studies/batches/build")
def design_studies_batch_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return build_design_batch(payload)
    except DesignStudyError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/design-studies/verify")
def design_studies_verify_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return verify_design_record(payload)
    except DesignStudyError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/model-calibration/health")
def model_calibration_health_route():
    return model_calibration_health()

@app.get("/v1/model-calibration/policies")
def model_calibration_policies_route():
    return model_calibration_policies()

@app.post("/v1/model-calibration/normalize")
def model_calibration_normalize_route(payload: dict[str, Any]):
    try: return {"ok": True, "study": normalize_calibration_study(payload)}
    except ModelCalibrationError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/model-calibration/calibrate")
def model_calibration_calibrate_route(payload: dict[str, Any]):
    try: return calibrate_model(payload)
    except ModelCalibrationError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/model-calibration/validate")
def model_calibration_validate_route(payload: dict[str, Any]):
    try: return validate_calibration_result(payload)
    except ModelCalibrationError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/model-calibration/compare")
def model_calibration_compare_route(payload: dict[str, Any]):
    try: return compare_models(payload)
    except ModelCalibrationError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/model-calibration/reports/build")
def model_calibration_report_route(payload: dict[str, Any]):
    try: return build_calibration_report(payload)
    except ModelCalibrationError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/model-calibration/verify")
def model_calibration_verify_route(payload: dict[str, Any]):
    try: return verify_calibration_record(payload)
    except ModelCalibrationError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/dispatcher/health")
def distributed_dispatcher_health_route():
    body=dispatcher.health(); body["serviceVersion"]=settings.version; return body

@app.get("/v1/dispatcher/policies")
def distributed_dispatcher_policies_route():
    body=distributed_dispatcher_policies(); body["serviceVersion"]=settings.version; return body

@app.get("/v1/dispatcher/workers")
def distributed_dispatcher_workers_route(active_only: bool = Query(False, alias="activeOnly"), auth: dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.list(active_only)

@app.post("/v1/dispatcher/workers/register")
def distributed_dispatcher_register_route(payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return dispatcher.register(payload)
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/workers/{worker_id}/heartbeat")
def distributed_dispatcher_heartbeat_route(worker_id: str, payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return dispatcher.heartbeat(worker_id,payload)
    except DispatcherError as exc: raise HTTPException(status_code=404 if "not found" in str(exc).lower() else 422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/route")
def distributed_dispatcher_route_route(payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return dispatcher.route(payload)
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/contracts/build")
def distributed_dispatcher_contract_build_route(payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return dispatcher.build_contract(payload,settings.dispatcher_contract_secret)
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/contracts/verify")
def distributed_dispatcher_contract_verify_route(payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.verify_contract(payload,settings.dispatcher_contract_secret)

@app.post("/v1/dispatcher/contracts/{contract_id}/acknowledge")
def distributed_dispatcher_contract_ack_route(contract_id: str, payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return dispatcher.acknowledge(contract_id,str(payload.get("workerId") or ""))
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/contracts/{contract_id}/complete")
def distributed_dispatcher_contract_complete_route(contract_id: str, payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return dispatcher.complete(contract_id,payload,str(payload.get("workerId") or ""))
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc


@app.get("/v1/dispatcher/queue/status")
def dispatcher_queue_status_route(auth: dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.status()

@app.post("/v1/dispatcher/queue/enqueue")
def dispatcher_queue_enqueue_route(payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return dispatcher.enqueue(payload)
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/leases/claim")
def dispatcher_lease_claim_route(payload: dict[str,Any], auth: dict[str,str]=Depends(require_compute_auth)):
    del auth
    try: return dispatcher.claim(payload,settings.dispatcher_contract_secret)
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.get("/v1/dispatcher/leases")
def dispatcher_leases_route(limit:int=Query(100,ge=1,le=500), auth: dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.leases(limit)

@app.post("/v1/dispatcher/leases/{lease_id}/renew")
def dispatcher_lease_renew_route(lease_id:str,payload:dict[str,Any],auth:dict[str,str]=Depends(require_compute_auth)):
    del auth
    try:return dispatcher.renew(lease_id,payload)
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/leases/{lease_id}/release")
def dispatcher_lease_release_route(lease_id:str,payload:dict[str,Any],auth:dict[str,str]=Depends(require_compute_auth)):
    del auth
    try:return dispatcher.release(lease_id,payload)
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/recovery/run")
def dispatcher_recovery_route(auth:dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.recover()

@app.get("/v1/dispatcher/history")
def dispatcher_history_route(limit:int=Query(100,ge=1,le=1000),auth:dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.history(limit)

# v0.31.4 Dispatcher Operations, Dead-Letter Recovery, and Observability

@app.get("/v1/dispatcher/operations/health")
def dispatcher_operations_health_route(auth:dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.operations_health()

@app.get("/v1/dispatcher/operations/policies")
def dispatcher_operations_policies_route(auth:dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.failure_policies()

@app.get("/v1/dispatcher/operations/metrics")
def dispatcher_operations_metrics_route(auth:dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.operations_metrics()

@app.get("/v1/dispatcher/operations/diagnostics")
def dispatcher_operations_diagnostics_route(auth:dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.diagnostics()

@app.get("/v1/dispatcher/dead-letters")
def dispatcher_dead_letters_route(limit:int=Query(100,ge=1,le=1000), failure_class:str=Query("",alias="failureClass"), auth:dict[str,str]=Depends(require_compute_auth)):
    del auth; return dispatcher.dead_letters(limit,failure_class)

@app.post("/v1/dispatcher/dead-letters/replay")
def dispatcher_dead_letters_replay_route(payload:dict[str,Any],auth:dict[str,str]=Depends(require_compute_auth)):
    del auth
    try:return dispatcher.replay_many(payload)
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.get("/v1/dispatcher/queue/{queue_id}")
def dispatcher_queue_item_route(queue_id:str,auth:dict[str,str]=Depends(require_compute_auth)):
    del auth
    try:return dispatcher.queue_item(queue_id)
    except DispatcherError as exc: raise HTTPException(status_code=404,detail=str(exc)) from exc

@app.get("/v1/dispatcher/queue/{queue_id}/timeline")
def dispatcher_queue_timeline_route(queue_id:str,limit:int=Query(250,ge=1,le=1000),auth:dict[str,str]=Depends(require_compute_auth)):
    del auth
    try:return dispatcher.timeline(queue_id,limit)
    except DispatcherError as exc: raise HTTPException(status_code=404,detail=str(exc)) from exc

@app.post("/v1/dispatcher/queue/{queue_id}/replay")
def dispatcher_queue_replay_route(queue_id:str,payload:dict[str,Any] | None=None,auth:dict[str,str]=Depends(require_compute_auth)):
    del auth
    try:return dispatcher.replay(queue_id,payload or {})
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/v1/dispatcher/queue/{queue_id}/cancel")
def dispatcher_queue_cancel_route(queue_id:str,payload:dict[str,Any] | None=None,auth:dict[str,str]=Depends(require_compute_auth)):
    del auth
    try:return dispatcher.cancel_queue_item(queue_id,payload or {})
    except DispatcherError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc

# v0.31.3 Distributed Artifact, Result, and Checkpoint Transport

def _artifact_http_error(exc: ArtifactTransportError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


@app.get("/v1/artifacts/health")
def artifact_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = artifacts.health()
    body["serviceVersion"] = settings.version
    body["deploymentDurability"] = "persistent-disk" if settings.artifact_persistent_disk_mounted else "instance-local"
    body["durabilityWarning"] = None if settings.artifact_persistent_disk_mounted else "Artifact files are instance-local unless a persistent disk is mounted."
    return body


@app.get("/v1/artifacts/policies")
def artifact_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return artifacts.policies()


@app.get("/v1/artifacts")
def artifact_list_route(project_id: str = Query("", alias="projectId"), queue_id: str = Query("", alias="queueId"), kind: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return artifacts.list(project_id, queue_id, kind, limit)


@app.get("/v1/artifacts/uploads")
def artifact_sessions_route(limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return artifacts.sessions(limit)


@app.post("/v1/artifacts/uploads")
def artifact_create_upload_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return artifacts.create_upload(payload)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


@app.post("/v1/artifacts/uploads/{session_id}/chunks")
async def artifact_append_chunk_route(session_id: str, request: Request, offset: int = Query(..., ge=0), x_sc_lab_chunk_sha256: str = Header(default=""), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return artifacts.append_chunk(session_id, offset, await request.body(), chunk_sha256=x_sc_lab_chunk_sha256)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


@app.post("/v1/artifacts/uploads/{session_id}/finalize")
def artifact_finalize_route(session_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return artifacts.finalize(session_id, payload or {})
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


@app.get("/v1/artifacts/{artifact_id}")
def artifact_metadata_route(artifact_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return artifacts.get(artifact_id)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


@app.get("/v1/artifacts/{artifact_id}/content")
def artifact_content_route(artifact_id: str, offset: int = Query(0, ge=0), length: int | None = Query(None, ge=0), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        metadata, data = artifacts.read(artifact_id, offset, length)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc
    headers = {"X-SC-Lab-Artifact-SHA256": metadata["sha256"], "X-SC-Lab-Artifact-Size": str(metadata["sizeBytes"]), "Content-Disposition": f'attachment; filename="{metadata["filename"]}"'}
    return Response(content=data, media_type=metadata["mediaType"], headers=headers)


@app.post("/v1/artifacts/manifest")
def artifact_manifest_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        ids = payload.get("artifactIds") if isinstance(payload.get("artifactIds"), list) else []
        return artifacts.manifest([str(item) for item in ids])
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


@app.post("/v1/artifacts/cleanup")
def artifact_cleanup_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return artifacts.cleanup_retention()


@app.delete("/v1/artifacts/{artifact_id}")
def artifact_delete_route(artifact_id: str, reason: str = Query("operator deletion"), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return artifacts.delete(artifact_id, reason)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


# v0.31.3 Secure Worker Agent Runtime and Artifact Transport

def _require_worker_enrollment(presented: str) -> None:
    expected = settings.worker_enrollment_token
    if expected:
        if not presented or not hmac.compare_digest(presented, expected):
            raise HTTPException(status_code=401, detail="Worker enrollment token is invalid.")
        return
    if settings.environment == "production" and not settings.allow_open_worker_enrollment:
        raise HTTPException(status_code=503, detail="Worker enrollment is disabled until SC_LAB_WORKER_ENROLLMENT_TOKEN is configured.")


def _authenticate_worker(worker_id: str, credential: str) -> dict[str, Any]:
    try:
        return dispatcher.authenticate_worker(worker_id, credential)
    except DispatcherError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@app.get("/v1/worker-agent/health")
def worker_agent_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    credentials = dispatcher.credential_status()
    return {
        "ok": True,
        "status": "ready",
        "version": settings.version,
        "architecture": "secure-pull-based-worker-agent-runtime",
        "enrollmentTokenConfigured": bool(settings.worker_enrollment_token),
        "openEnrollment": not bool(settings.worker_enrollment_token) and (settings.environment != "production" or settings.allow_open_worker_enrollment),
        "contractSecretConfigured": bool(settings.dispatcher_contract_secret),
        "credentials": credentials,
        "policies": worker_agent_policies(bool(settings.worker_enrollment_token), bool(settings.dispatcher_contract_secret)),
    }


@app.get("/v1/worker-agent/policies")
def worker_agent_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return worker_agent_policies(bool(settings.worker_enrollment_token), bool(settings.dispatcher_contract_secret))


@app.get("/v1/worker-agent/credentials/status")
def worker_agent_credentials_status_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return dispatcher.credential_status()


@app.post("/v1/worker-agent/enroll")
def worker_agent_enroll_route(payload: dict[str, Any], x_sc_lab_worker_enrollment: str = Header(default="")):
    _require_worker_enrollment(x_sc_lab_worker_enrollment)
    try:
        return dispatcher.enroll(payload)
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/worker-agent/{worker_id}/heartbeat")
def worker_agent_heartbeat_route(worker_id: str, payload: dict[str, Any], x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return dispatcher.heartbeat(worker_id, payload)
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/worker-agent/{worker_id}/claim")
def worker_agent_claim_route(worker_id: str, payload: dict[str, Any], x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return dispatcher.claim({"workerId": worker_id, "leaseSeconds": payload.get("leaseSeconds") or settings.dispatcher_default_lease_seconds}, settings.dispatcher_contract_secret)
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/worker-agent/{worker_id}/contracts/{contract_id}/acknowledge")
def worker_agent_acknowledge_route(worker_id: str, contract_id: str, x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return dispatcher.acknowledge(contract_id, worker_id)
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/worker-agent/{worker_id}/contracts/{contract_id}/complete")
def worker_agent_complete_route(worker_id: str, contract_id: str, payload: dict[str, Any], x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return dispatcher.complete(contract_id, payload, worker_id)
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/worker-agent/{worker_id}/leases/{lease_id}/renew")
def worker_agent_renew_route(worker_id: str, lease_id: str, payload: dict[str, Any], x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return dispatcher.renew(lease_id, {"workerId": worker_id, "leaseSeconds": payload.get("leaseSeconds") or settings.dispatcher_default_lease_seconds})
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/worker-agent/{worker_id}/leases/{lease_id}/release")
def worker_agent_release_route(worker_id: str, lease_id: str, payload: dict[str, Any], x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return dispatcher.release(lease_id, {"workerId": worker_id, "reason": payload.get("reason"), "requeue": payload.get("requeue", True)})
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/worker-agent/{worker_id}/credential/rotate")
def worker_agent_rotate_credential_route(worker_id: str, x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return dispatcher.rotate_worker_credential(worker_id)
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/worker-agent/{worker_id}/artifacts/uploads")
def worker_artifact_create_upload_route(worker_id: str, payload: dict[str, Any], x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return artifacts.create_upload(payload, worker_id)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


@app.post("/v1/worker-agent/{worker_id}/artifacts/uploads/{session_id}/chunks")
async def worker_artifact_append_chunk_route(worker_id: str, session_id: str, request: Request, offset: int = Query(..., ge=0), x_sc_lab_chunk_sha256: str = Header(default=""), x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return artifacts.append_chunk(session_id, offset, await request.body(), worker_id, x_sc_lab_chunk_sha256)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


@app.post("/v1/worker-agent/{worker_id}/artifacts/uploads/{session_id}/finalize")
def worker_artifact_finalize_route(worker_id: str, session_id: str, payload: dict[str, Any] | None = None, x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        return artifacts.finalize(session_id, payload or {}, worker_id)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc


@app.get("/v1/worker-agent/{worker_id}/artifacts/{artifact_id}")
def worker_artifact_metadata_route(worker_id: str, artifact_id: str, x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        metadata = artifacts.get(artifact_id)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc
    if metadata.get("workerId") != worker_id and not dispatcher.artifact_access_allowed(worker_id, artifact_id):
        raise HTTPException(status_code=403, detail="Worker does not have an active artifact grant.")
    return metadata


@app.get("/v1/worker-agent/{worker_id}/artifacts/{artifact_id}/content")
def worker_artifact_content_route(worker_id: str, artifact_id: str, offset: int = Query(0, ge=0), length: int | None = Query(None, ge=0), x_sc_lab_worker_credential: str = Header(default="")):
    _authenticate_worker(worker_id, x_sc_lab_worker_credential)
    try:
        metadata = artifacts.get(artifact_id)
        if metadata.get("workerId") != worker_id and not dispatcher.artifact_access_allowed(worker_id, artifact_id):
            raise HTTPException(status_code=403, detail="Worker does not have an active artifact grant.")
        metadata, data = artifacts.read(artifact_id, offset, length)
    except ArtifactTransportError as exc:
        raise _artifact_http_error(exc) from exc
    headers = {"X-SC-Lab-Artifact-SHA256": metadata["sha256"], "X-SC-Lab-Artifact-Size": str(metadata["sizeBytes"])}
    return Response(content=data, media_type=metadata["mediaType"], headers=headers)


@app.post("/v1/worker-agent/{worker_id}/revoke")
def worker_agent_revoke_route(worker_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return dispatcher.revoke_worker(worker_id, str(payload.get("reason") or "revoked by coordinator"))
    except DispatcherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc



# v0.32.1 Workflow Checkpoints, Conditional Execution, and Partial Recovery

def _workflow_http_error(exc: WorkflowError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


@app.get("/v1/workflows/health")
def workflow_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = workflows.health()
    body["serviceVersion"] = settings.version
    body["deploymentDurability"] = "persistent-disk" if settings.workflow_persistent_disk_mounted else "instance-local"
    body["durabilityWarning"] = None if settings.workflow_persistent_disk_mounted else "Workflow records are instance-local unless a persistent disk is mounted."
    return body


@app.get("/v1/workflows/policies")
def workflow_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return workflow_policies(settings.workflow_max_nodes, settings.workflow_max_runs)


@app.post("/v1/workflows/validate")
def workflow_validate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.validate(payload)
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.post("/v1/workflows")
def workflow_save_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.save(payload)
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.get("/v1/workflows")
def workflow_list_route(project_id: str = Query("", alias="projectId"), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return workflows.list(project_id, limit)


@app.get("/v1/workflows/{workflow_id}")
def workflow_get_route(workflow_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.get(workflow_id)
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.post("/v1/workflows/{workflow_id}/runs")
def workflow_start_run_route(workflow_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.start_run(workflow_id, payload or {})
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.get("/v1/workflow-runs")
def workflow_runs_route(workflow_id: str = Query("", alias="workflowId"), project_id: str = Query("", alias="projectId"), status: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.runs(workflow_id, project_id, status, limit)
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.get("/v1/workflow-runs/{run_id}")
def workflow_run_route(run_id: str, reconcile: bool = Query(True), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.run(run_id, reconcile=reconcile)
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.post("/v1/workflow-runs/{run_id}/reconcile")
def workflow_reconcile_route(run_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.reconcile(run_id)
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.post("/v1/workflow-runs/{run_id}/cancel")
def workflow_cancel_route(run_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.cancel(run_id, payload or {})
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.post("/v1/workflow-runs/{run_id}/recovery-plan")
def workflow_recovery_plan_route(run_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.recovery_plan(run_id, payload or {})
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.post("/v1/workflow-runs/{run_id}/recover")
def workflow_recover_route(run_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.recover(run_id, payload or {})
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.post("/v1/workflow-runs/{run_id}/nodes/{node_id}/restart")
def workflow_restart_node_route(run_id: str, node_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.restart_node(run_id, node_id, payload or {})
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.get("/v1/workflow-runs/{run_id}/nodes/{node_id}/checkpoints")
def workflow_checkpoints_route(run_id: str, node_id: str, limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.checkpoints(run_id, node_id, limit)
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.post("/v1/workflow-runs/{run_id}/nodes/{node_id}/checkpoints")
def workflow_record_checkpoint_route(run_id: str, node_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.record_checkpoint(run_id, node_id, payload or {})
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc


@app.get("/v1/workflow-runs/{run_id}/timeline")
def workflow_timeline_route(run_id: str, limit: int = Query(500, ge=1, le=2000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflows.timeline(run_id, limit)
    except WorkflowError as exc:
        raise _workflow_http_error(exc) from exc

# v0.32.2 Scheduled and Event-Driven Research Runs

def _workflow_schedule_http_error(exc: WorkflowScheduleError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


@app.get("/v1/workflow-automation/health")
def workflow_automation_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = workflow_automation.health()
    body["serviceVersion"] = settings.version
    body["deploymentDurability"] = "persistent-disk" if settings.workflow_schedule_persistent_disk_mounted else "instance-local"
    body["durabilityWarning"] = None if settings.workflow_schedule_persistent_disk_mounted else "Workflow schedules and event receipts are instance-local unless a persistent disk is mounted."
    body["eventHmacConfigured"] = bool(settings.workflow_event_secret)
    return body


@app.get("/v1/workflow-automation/policies")
def workflow_automation_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return workflow_scheduling_policies(settings.workflow_scheduler_max_catch_up_runs)


@app.post("/v1/workflow-automation/schedules/validate")
def workflow_schedule_validate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflow_automation.validate(payload)
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc


@app.post("/v1/workflow-automation/schedules")
def workflow_schedule_save_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflow_automation.save(payload)
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc


@app.get("/v1/workflow-automation/schedules")
def workflow_schedule_list_route(workflow_id: str = Query("", alias="workflowId"), enabled: bool | None = Query(None), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return workflow_automation.list(workflow_id, enabled, limit)


@app.get("/v1/workflow-automation/schedules/{schedule_id}")
def workflow_schedule_get_route(schedule_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflow_automation.get(schedule_id)
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc


@app.delete("/v1/workflow-automation/schedules/{schedule_id}")
def workflow_schedule_delete_route(schedule_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflow_automation.delete(schedule_id)
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc


@app.post("/v1/workflow-automation/schedules/{schedule_id}/enable")
def workflow_schedule_enable_route(schedule_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflow_automation.set_enabled(schedule_id, True)
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc


@app.post("/v1/workflow-automation/schedules/{schedule_id}/disable")
def workflow_schedule_disable_route(schedule_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflow_automation.set_enabled(schedule_id, False)
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc


@app.post("/v1/workflow-automation/schedules/{schedule_id}/trigger")
def workflow_schedule_trigger_route(schedule_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflow_automation.trigger(schedule_id, payload or {})
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc


@app.post("/v1/workflow-automation/tick")
def workflow_schedule_tick_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return workflow_automation.tick()


@app.get("/v1/workflow-automation/firings")
def workflow_schedule_firings_route(schedule_id: str = Query("", alias="scheduleId"), status: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return workflow_automation.firings(schedule_id, status, limit)
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc


@app.get("/v1/workflow-automation/events")
def workflow_events_list_route(event_type: str = Query("", alias="eventType"), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return workflow_automation.events(event_type, limit)


@app.post("/v1/workflow-automation/events")
async def workflow_event_ingest_route(
    request: Request,
    x_sc_lab_event_timestamp: str | None = Header(default=None),
    x_sc_lab_event_signature: str | None = Header(default=None),
    auth: dict[str, str] = Depends(require_compute_auth),
):
    del auth
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="A JSON event payload is required.") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="Event payload must be a JSON object.")
    if settings.workflow_event_secret and not verify_event_signature(payload, x_sc_lab_event_timestamp or "", x_sc_lab_event_signature or "", settings.workflow_event_secret, settings.workflow_event_signature_tolerance_seconds):
        raise HTTPException(status_code=401, detail="Invalid or expired workflow event signature.")
    try:
        return workflow_automation.ingest_event(payload)
    except WorkflowScheduleError as exc:
        raise _workflow_schedule_http_error(exc) from exc

# v0.33.1 Bayesian Optimization, Active Learning, and Resource-Aware Search

def _experiment_campaign_http_error(exc: ExperimentCampaignError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


@app.get("/v1/experiment-campaigns/health")
def experiment_campaign_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = experiment_campaigns.health()
    body["serviceVersion"] = settings.version
    body["deploymentDurability"] = "persistent-disk" if settings.experiment_campaign_persistent_disk_mounted else "instance-local"
    body["durabilityWarning"] = None if settings.experiment_campaign_persistent_disk_mounted else "Experiment campaigns and trial histories are instance-local unless a persistent disk is mounted."
    return body


@app.get("/v1/experiment-campaigns/policies")
def experiment_campaign_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return experiment_campaign_policies(settings.experiment_campaign_max_trials, settings.experiment_campaign_max_campaigns)


@app.post("/v1/experiment-campaigns/validate")
def experiment_campaign_validate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.validate(payload)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns")
def experiment_campaign_save_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.save(payload)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.get("/v1/experiment-campaigns")
def experiment_campaign_list_route(project_id: str = Query("", alias="projectId"), status: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.list(project_id, status, limit)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.get("/v1/experiment-campaigns/{campaign_id}")
def experiment_campaign_get_route(campaign_id: str, reconcile: bool = Query(False), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.get(campaign_id, reconcile=reconcile)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns/{campaign_id}/start")
def experiment_campaign_start_route(campaign_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.start_campaign(campaign_id)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns/{campaign_id}/pause")
def experiment_campaign_pause_route(campaign_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.pause(campaign_id, str((payload or {}).get("reason") or "operator pause"))
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns/{campaign_id}/resume")
def experiment_campaign_resume_route(campaign_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.resume(campaign_id)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns/{campaign_id}/advance")
def experiment_campaign_advance_route(campaign_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        count = (payload or {}).get("count")
        return experiment_campaigns.advance(campaign_id, int(count) if count is not None else None)
    except (ExperimentCampaignError, ValueError) as exc:
        if isinstance(exc, ExperimentCampaignError):
            raise _experiment_campaign_http_error(exc) from exc
        raise HTTPException(status_code=422, detail="count must be an integer") from exc


@app.post("/v1/experiment-campaigns/{campaign_id}/reconcile")
def experiment_campaign_reconcile_route(campaign_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.reconcile(campaign_id, auto_advance=True)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns/{campaign_id}/cancel")
def experiment_campaign_cancel_route(campaign_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.cancel(campaign_id, str((payload or {}).get("reason") or "operator cancellation"))
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns/{campaign_id}/observations")
def experiment_campaign_observe_route(campaign_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.observe(campaign_id, payload)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.get("/v1/experiment-campaigns/{campaign_id}/surrogate")
def experiment_campaign_surrogate_route(campaign_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.surrogate(campaign_id)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns/{campaign_id}/proposal-preview")
def experiment_campaign_proposal_preview_route(campaign_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.preview_proposal(campaign_id)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.get("/v1/experiment-campaigns/{campaign_id}/trials")
def experiment_campaign_trials_route(campaign_id: str, status: str = Query(""), limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.trials(campaign_id, status, limit)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.get("/v1/experiment-campaigns/{campaign_id}/timeline")
def experiment_campaign_timeline_route(campaign_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        return experiment_campaigns.timeline(campaign_id, limit)
    except ExperimentCampaignError as exc:
        raise _experiment_campaign_http_error(exc) from exc


@app.post("/v1/experiment-campaigns/tick")
def experiment_campaign_tick_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return experiment_campaigns.tick()


# v0.34.0 Scientific Model Registry and Environment Reproduction
def _model_registry_http_error(exc: ModelRegistryError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


def _validate_model_registry_reference(payload: dict[str, Any]) -> None:
    source = payload.get("model") if isinstance(payload.get("model"), dict) else payload
    model_type = str(source.get("type") or "registered-method")
    if model_type == "registered-method":
        method_id = str(source.get("methodId") or "").strip()
        try:
            resolve(method_id)
        except KeyError as exc:
            raise ModelRegistryError(str(exc), 422) from exc
    elif model_type == "workflow":
        workflow_id = str(source.get("workflowId") or "").strip()
        try:
            workflows.get(workflow_id)
        except WorkflowError as exc:
            raise ModelRegistryError(f"Unknown registered workflow: {workflow_id}", 422) from exc

@app.get("/v1/model-registry/health")
def model_registry_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    body = model_registry.health(); body["serviceVersion"] = settings.version; body["deploymentDurability"] = "persistent-disk" if settings.model_registry_persistent_disk_mounted else "instance-local"; body["durabilityWarning"] = None if settings.model_registry_persistent_disk_mounted else "Model registry records are instance-local unless a persistent disk is mounted."; return body

@app.get("/v1/model-registry/policies")
def model_registry_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    body = model_registry_policies(settings.model_registry_max_models, settings.model_registry_max_versions); body["serviceVersion"] = settings.version; return body

@app.post("/v1/model-registry/environments/capture")
def model_registry_capture_environment_route(payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    try: return {"ok": True, "environment": capture_environment(payload or {})}
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.post("/v1/model-registry/environments/compare")
def model_registry_compare_environment_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return model_registry.compare_environments(payload)
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.post("/v1/model-registry/validate")
def model_registry_validate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try:
        _validate_model_registry_reference(payload)
        return model_registry.validate(payload)
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.post("/v1/model-registry/models")
def model_registry_register_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try:
        _validate_model_registry_reference(payload)
        return model_registry.register(payload, auth.get("subject", "operator"))
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.get("/v1/model-registry/models")
def model_registry_list_route(project_id: str = Query("", alias="projectId"), channel: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    try: return model_registry.list(project_id, channel, limit)
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.get("/v1/model-registry/models/{model_id}")
def model_registry_get_route(model_id: str, version: str = Query(""), auth: dict[str, str] = Depends(require_compute_auth)):
    try: return model_registry.get(model_id, version)
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.post("/v1/model-registry/models/{model_id}/{model_version}/promote")
def model_registry_promote_route(model_id: str, model_version: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return model_registry.promote(model_id, model_version, str(payload.get("channel") or "candidate"), auth.get("subject", "operator"), str(payload.get("reason") or ""))
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.post("/v1/model-registry/models/{model_id}/{model_version}/deprecate")
def model_registry_deprecate_route(model_id: str, model_version: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return model_registry.deprecate(model_id, model_version, auth.get("subject", "operator"), str(payload.get("reason") or ""))
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.get("/v1/model-registry/models/{model_id}/reproduction")
def model_registry_reproduction_route(model_id: str, version: str = Query(""), auth: dict[str, str] = Depends(require_compute_auth)):
    try: return model_registry.reproduction_manifest(model_id, version)
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.post("/v1/model-registry/reproduction/verify")
def model_registry_verify_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return model_registry.verify_reproduction(payload)
    except ModelRegistryError as exc: raise _model_registry_http_error(exc) from exc

@app.get("/v1/model-registry/models/{model_id}/timeline")
def model_registry_timeline_route(model_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    return model_registry.timeline(model_id, limit)

# v0.34.1 Ensemble Simulation, Global Sensitivity, and Uncertainty
def _ensemble_http_error(exc: EnsembleError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)

@app.get("/v1/ensemble-studies/health")
def ensemble_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = ensemble_studies.health(); body["serviceVersion"] = settings.version; body["deploymentDurability"] = "persistent-disk" if settings.ensemble_persistent_disk_mounted else "instance-local"; body["durabilityWarning"] = None if settings.ensemble_persistent_disk_mounted else "Ensemble study records are instance-local unless a persistent disk is mounted."; return body

@app.get("/v1/ensemble-studies/policies")
def ensemble_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = ensemble_policies(settings.ensemble_max_studies, settings.ensemble_max_evaluations); body["serviceVersion"] = settings.version; return body

@app.post("/v1/ensemble-studies/validate")
def ensemble_validate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return ensemble_studies.validate(payload)
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

@app.post("/v1/ensemble-studies")
def ensemble_create_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return ensemble_studies.create(payload, auth.get("subject", "operator"))
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

@app.get("/v1/ensemble-studies")
def ensemble_list_route(project_id: str = Query("", alias="projectId"), status: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return ensemble_studies.list(project_id, status, limit)
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

@app.get("/v1/ensemble-studies/{study_id}")
def ensemble_get_route(study_id: str, reconcile: bool = Query(True), evaluation_limit: int = Query(5000, alias="evaluationLimit", ge=1, le=200000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return ensemble_studies.get(study_id, reconcile, evaluation_limit)
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

@app.post("/v1/ensemble-studies/{study_id}/start")
def ensemble_start_route(study_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    try: return ensemble_studies.start(study_id, auth.get("subject", "operator"))
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

@app.post("/v1/ensemble-studies/{study_id}/reconcile")
def ensemble_reconcile_route(study_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return ensemble_studies.reconcile(study_id)
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

@app.post("/v1/ensemble-studies/{study_id}/evaluations/{evaluation_id}/result")
def ensemble_record_result_route(study_id: str, evaluation_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return ensemble_studies.record_result(study_id, evaluation_id, payload, auth.get("subject", "operator"))
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

@app.post("/v1/ensemble-studies/{study_id}/cancel")
def ensemble_cancel_route(study_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    body = payload or {}
    try: return ensemble_studies.cancel(study_id, auth.get("subject", "operator"), str(body.get("reason") or "operator cancellation"))
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

@app.get("/v1/ensemble-studies/{study_id}/timeline")
def ensemble_timeline_route(study_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return ensemble_studies.timeline(study_id, limit)
    except EnsembleError as exc: raise _ensemble_http_error(exc) from exc

# v0.34.2 Surrogate Models and Reduced-Order Analysis

def _surrogate_rom_http_error(exc: SurrogateROMError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)

@app.get("/v1/surrogate-rom/health")
def surrogate_rom_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = surrogate_rom.health(); body["serviceVersion"] = settings.version; body["deploymentDurability"] = "persistent-disk" if settings.surrogate_rom_persistent_disk_mounted else "instance-local"; body["durabilityWarning"] = None if settings.surrogate_rom_persistent_disk_mounted else "Surrogate and ROM records are instance-local unless a persistent disk is mounted."; return body

@app.get("/v1/surrogate-rom/policies")
def surrogate_rom_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = surrogate_rom_policies(settings.surrogate_rom_max_studies, settings.surrogate_rom_max_training_rows, settings.surrogate_rom_max_snapshot_dimensions, settings.surrogate_rom_max_request_bytes); body["serviceVersion"] = settings.version; return body

@app.post("/v1/surrogate-rom/validate")
def surrogate_rom_validate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return surrogate_rom.validate(payload)
    except SurrogateROMError as exc: raise _surrogate_rom_http_error(exc) from exc

@app.post("/v1/surrogate-rom/studies")
def surrogate_rom_train_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return surrogate_rom.train(payload, auth.get("subject", "operator"))
    except SurrogateROMError as exc: raise _surrogate_rom_http_error(exc) from exc

@app.get("/v1/surrogate-rom/studies")
def surrogate_rom_list_route(project_id: str = Query("", alias="projectId"), status: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return surrogate_rom.list(project_id, status, limit)
    except SurrogateROMError as exc: raise _surrogate_rom_http_error(exc) from exc

@app.get("/v1/surrogate-rom/studies/{study_id}")
def surrogate_rom_get_route(study_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return surrogate_rom.get(study_id)
    except SurrogateROMError as exc: raise _surrogate_rom_http_error(exc) from exc

@app.post("/v1/surrogate-rom/studies/{study_id}/predict")
def surrogate_rom_predict_route(study_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return surrogate_rom.predict(study_id, payload)
    except SurrogateROMError as exc: raise _surrogate_rom_http_error(exc) from exc

@app.post("/v1/surrogate-rom/studies/{study_id}/register")
def surrogate_rom_register_route(study_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    try: return surrogate_rom.register_model(study_id, payload, auth.get("subject", "operator"))
    except SurrogateROMError as exc: raise _surrogate_rom_http_error(exc) from exc

@app.get("/v1/surrogate-rom/studies/{study_id}/timeline")
def surrogate_rom_timeline_route(study_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return surrogate_rom.timeline(study_id, limit)
    except SurrogateROMError as exc: raise _surrogate_rom_http_error(exc) from exc

# v0.35.0 Shared Research Projects and Team Workspaces

def _team_workspace_actor(auth: dict[str, str]) -> tuple[str, str]:
    return (auth.get("actor") or auth.get("subject") or auth.get("client") or "operator", auth.get("actorName") or auth.get("client") or "Workspace member")

def _team_workspace_http_error(exc: TeamWorkspaceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)

@app.get("/v1/team-workspaces/health")
def team_workspace_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = team_workspaces.health(); body["serviceVersion"] = settings.version; body["deploymentDurability"] = "persistent-disk" if settings.team_workspace_persistent_disk_mounted else "instance-local"; body["durabilityWarning"] = None if settings.team_workspace_persistent_disk_mounted else "Shared workspace records are instance-local unless a persistent disk is mounted."; return body

@app.get("/v1/team-workspaces/policies")
def team_workspace_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = team_workspace_policies(); body["serviceVersion"] = settings.version; return body

@app.post("/v1/team-workspaces")
def team_workspace_create_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, name = _team_workspace_actor(auth)
    try: return team_workspaces.create(payload, actor, name)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.get("/v1/team-workspaces")
def team_workspace_list_route(status: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.list(actor, status or None, limit)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.post("/v1/team-workspaces/invitations/accept")
def team_workspace_accept_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, name = _team_workspace_actor(auth)
    try: return team_workspaces.accept_invitation(payload, actor, name)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}")
def team_workspace_get_route(workspace_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.get(workspace_id, actor)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.patch("/v1/team-workspaces/{workspace_id}")
def team_workspace_update_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.update(workspace_id, payload, actor)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/archive")
def team_workspace_archive_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.archive(workspace_id, actor, str(payload.get("reason") or ""))
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/invitations")
def team_workspace_invite_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.invite(workspace_id, payload, actor)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.patch("/v1/team-workspaces/{workspace_id}/members/{member_id}")
def team_workspace_member_role_route(workspace_id: str, member_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.set_member_role(workspace_id, member_id, payload, actor)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.delete("/v1/team-workspaces/{workspace_id}/members/{member_id}")
def team_workspace_remove_member_route(workspace_id: str, member_id: str, reason: str = Query(""), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.remove_member(workspace_id, member_id, actor, reason)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/ownership")
def team_workspace_transfer_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.transfer_ownership(workspace_id, payload, actor)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/resources")
def team_workspace_link_resource_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.link_resource(workspace_id, payload, actor)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.delete("/v1/team-workspaces/{workspace_id}/resources/{link_id}")
def team_workspace_unlink_resource_route(workspace_id: str, link_id: str, reason: str = Query(""), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.unlink_resource(workspace_id, link_id, actor, reason)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/authorize")
def team_workspace_authorize_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.authorize(workspace_id, payload, actor)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/timeline")
def team_workspace_timeline_route(workspace_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return team_workspaces.timeline(workspace_id, actor, limit)
    except TeamWorkspaceError as exc: raise _team_workspace_http_error(exc) from exc


# v0.35.1 Review, Comments, Approvals, and Scientific Sign-Off
def _workspace_review_http_error(exc: WorkspaceReviewError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)

@app.get("/v1/workspace-reviews/health")
def workspace_review_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    body = workspace_reviews.health(); body["serviceVersion"] = settings.version; body["deploymentDurability"] = "persistent-disk" if settings.team_workspace_persistent_disk_mounted else "instance-local"; return body

@app.get("/v1/workspace-reviews/policies")
def workspace_review_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    body = workspace_review_policies(); body["serviceVersion"] = settings.version; return body

@app.get("/v1/team-workspaces/{workspace_id}/review-threads")
def workspace_review_threads_list_route(workspace_id: str, status: str = Query(""), resourceLinkId: str = Query(""), limit: int = Query(200, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.list_threads(workspace_id, actor, status or None, resourceLinkId or None, limit)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/review-threads")
def workspace_review_thread_create_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.create_thread(workspace_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/review-threads/{thread_id}")
def workspace_review_thread_get_route(workspace_id: str, thread_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.get_thread(workspace_id, thread_id, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/review-threads/{thread_id}/comments")
def workspace_review_comment_create_route(workspace_id: str, thread_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.add_comment(workspace_id, thread_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/review-comments/{comment_id}/withdraw")
def workspace_review_comment_withdraw_route(workspace_id: str, comment_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.withdraw_comment(workspace_id, comment_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/review-threads/{thread_id}/resolve")
def workspace_review_thread_resolve_route(workspace_id: str, thread_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.set_thread_status(workspace_id, thread_id, payload, actor, "resolved")
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/review-threads/{thread_id}/reopen")
def workspace_review_thread_reopen_route(workspace_id: str, thread_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.set_thread_status(workspace_id, thread_id, payload, actor, "open")
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/review-assignments")
def workspace_review_assignments_list_route(workspace_id: str, status: str = Query(""), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.list_assignments(workspace_id, actor, status or None)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/review-assignments")
def workspace_review_assignment_create_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.create_assignment(workspace_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.patch("/v1/team-workspaces/{workspace_id}/review-assignments/{assignment_id}")
def workspace_review_assignment_update_route(workspace_id: str, assignment_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.update_assignment(workspace_id, assignment_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/approval-requests")
def workspace_review_approval_list_route(workspace_id: str, status: str = Query(""), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.list_approvals(workspace_id, actor, status or None)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/approval-requests")
def workspace_review_approval_create_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.create_approval(workspace_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/approval-requests/{approval_id}")
def workspace_review_approval_get_route(workspace_id: str, approval_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.get_approval(workspace_id, approval_id, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/approval-requests/{approval_id}/evaluate")
def workspace_review_approval_evaluate_route(workspace_id: str, approval_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.evaluate_approval(workspace_id, approval_id, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/approval-requests/{approval_id}/decisions")
def workspace_review_decision_create_route(workspace_id: str, approval_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.decide(workspace_id, approval_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/approval-requests/{approval_id}/cancel")
def workspace_review_approval_cancel_route(workspace_id: str, approval_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.cancel_approval(workspace_id, approval_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/approval-requests/{approval_id}/signoff")
def workspace_review_signoff_route(workspace_id: str, approval_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.signoff(workspace_id, approval_id, payload, actor)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/review-timeline")
def workspace_review_timeline_route(workspace_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_reviews.timeline(workspace_id, actor, limit)
    except WorkspaceReviewError as exc: raise _workspace_review_http_error(exc) from exc

# v0.35.2 Version History, Branching, Merge, and Conflict Resolution
def _workspace_version_http_error(exc: WorkspaceVersionError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)

@app.get("/v1/workspace-versions/health")
def workspace_version_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    body = workspace_versions.health(); body["serviceVersion"] = settings.version; body["deploymentDurability"] = "persistent-disk" if settings.team_workspace_persistent_disk_mounted else "instance-local"; return body

@app.get("/v1/workspace-versions/policies")
def workspace_version_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    body = workspace_version_policies(); body["serviceVersion"] = settings.version; return body

@app.post("/v1/team-workspaces/{workspace_id}/versions/bootstrap")
def workspace_version_bootstrap_route(workspace_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.bootstrap(workspace_id, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/branches")
def workspace_version_branches_list_route(workspace_id: str, status: str = Query(""), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.list_branches(workspace_id, actor, status or None)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/branches")
def workspace_version_branch_create_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.create_branch(workspace_id, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.patch("/v1/team-workspaces/{workspace_id}/branches/{branch_ref:path}")
def workspace_version_branch_update_route(workspace_id: str, branch_ref: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.set_branch(workspace_id, branch_ref, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/branches/{branch_ref:path}/snapshots")
def workspace_version_snapshots_list_route(workspace_id: str, branch_ref: str, limit: int = Query(200, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.list_snapshots(workspace_id, branch_ref, actor, limit)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/branches/{branch_ref:path}/snapshots")
def workspace_version_snapshot_create_route(workspace_id: str, branch_ref: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.create_snapshot(workspace_id, branch_ref, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/branches/{branch_ref:path}/restore/{snapshot_id}")
def workspace_version_restore_route(workspace_id: str, branch_ref: str, snapshot_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.restore_snapshot(workspace_id, branch_ref, snapshot_id, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/snapshots/{snapshot_id}")
def workspace_version_snapshot_get_route(workspace_id: str, snapshot_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.get_snapshot(workspace_id, snapshot_id, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/version-compare")
def workspace_version_compare_route(workspace_id: str, fromSnapshotId: str = Query(""), toSnapshotId: str = Query(""), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.compare(workspace_id, fromSnapshotId or None, toSnapshotId or None, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/merge-requests")
def workspace_version_merges_list_route(workspace_id: str, status: str = Query(""), limit: int = Query(200, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.list_merge_requests(workspace_id, actor, status or None, limit)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/merge-requests")
def workspace_version_merge_create_route(workspace_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.create_merge_request(workspace_id, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/merge-requests/{merge_id}")
def workspace_version_merge_get_route(workspace_id: str, merge_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.get_merge_request(workspace_id, merge_id, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/merge-requests/{merge_id}/conflicts/{conflict_id}/resolve")
def workspace_version_conflict_resolve_route(workspace_id: str, merge_id: str, conflict_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.resolve_conflict(workspace_id, merge_id, conflict_id, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/merge-requests/{merge_id}/approval")
def workspace_version_approval_attach_route(workspace_id: str, merge_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.attach_approval(workspace_id, merge_id, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/merge-requests/{merge_id}/finalize")
def workspace_version_merge_finalize_route(workspace_id: str, merge_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.finalize_merge(workspace_id, merge_id, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.post("/v1/team-workspaces/{workspace_id}/merge-requests/{merge_id}/cancel")
def workspace_version_merge_cancel_route(workspace_id: str, merge_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.cancel_merge(workspace_id, merge_id, payload, actor)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

@app.get("/v1/team-workspaces/{workspace_id}/version-timeline")
def workspace_version_timeline_route(workspace_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    actor, _ = _team_workspace_actor(auth)
    try: return workspace_versions.timeline(workspace_id, actor, limit)
    except WorkspaceVersionError as exc: raise _workspace_version_http_error(exc) from exc

# v0.33.2 Closed-Loop Simulation and Instrument Campaigns

@app.get("/v1/closed-loop-campaigns/health")
def closed_loop_health_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = closed_loop_campaigns.health(); body["serviceVersion"] = settings.version; body["deploymentDurability"] = "persistent-disk" if settings.closed_loop_persistent_disk_mounted else "instance-local"; return body

@app.get("/v1/closed-loop-campaigns/policies")
def closed_loop_policies_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = closed_loop_policies(settings.closed_loop_max_loops, settings.closed_loop_max_cycles); body["serviceVersion"] = settings.version; return body

@app.post("/v1/closed-loop-campaigns/validate")
def closed_loop_validate_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.validate(payload)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns")
def closed_loop_save_route(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.save(payload)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.get("/v1/closed-loop-campaigns")
def closed_loop_list_route(project_id: str = Query("", alias="projectId"), status: str = Query(""), limit: int = Query(100, ge=1, le=1000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.list(project_id, status, limit)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.get("/v1/closed-loop-campaigns/{loop_id}")
def closed_loop_get_route(loop_id: str, reconcile: bool = Query(False), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.get(loop_id, reconcile)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/start")
def closed_loop_start_route(loop_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.start_loop(loop_id)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/pause")
def closed_loop_pause_route(loop_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.pause(loop_id, str((payload or {}).get("reason") or "operator pause"))
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/resume")
def closed_loop_resume_route(loop_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.resume(loop_id)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/reconcile")
def closed_loop_reconcile_route(loop_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.reconcile(loop_id)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/cancel")
def closed_loop_cancel_route(loop_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.cancel(loop_id, str((payload or {}).get("reason") or "operator cancellation"))
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/emergency-stop")
def closed_loop_emergency_stop_route(loop_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.emergency_stop(loop_id, str((payload or {}).get("reason") or "operator emergency stop"))
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/commands/preview")
def closed_loop_preview_route(loop_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.preview_command(loop_id)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/commands/issue")
def closed_loop_issue_route(loop_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.issue_next_command(loop_id)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.get("/v1/closed-loop-campaigns/{loop_id}/commands")
def closed_loop_commands_route(loop_id: str, status: str = Query(""), limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.commands(loop_id, status, limit)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/commands/{command_id}/approve")
def closed_loop_approve_route(loop_id: str, command_id: str, payload: dict[str, Any] | None = None, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    body = payload or {}
    try: return closed_loop_campaigns.approve_command(loop_id, command_id, str(body.get("operator") or "operator"), str(body.get("reason") or "approved"))
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/commands/{command_id}/dispatch")
def closed_loop_dispatch_route(loop_id: str, command_id: str, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.dispatch_command(loop_id, command_id)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/{loop_id}/measurements")
def closed_loop_measurement_route(loop_id: str, payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.ingest_measurement(loop_id, payload)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.get("/v1/closed-loop-campaigns/{loop_id}/measurements")
def closed_loop_measurements_route(loop_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.measurements(loop_id, limit)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.get("/v1/closed-loop-campaigns/{loop_id}/timeline")
def closed_loop_timeline_route(loop_id: str, limit: int = Query(500, ge=1, le=5000), auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try: return closed_loop_campaigns.timeline(loop_id, limit)
    except ClosedLoopError as exc: raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

@app.post("/v1/closed-loop-campaigns/tick")
def closed_loop_tick_route(auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    return closed_loop_campaigns.tick()

