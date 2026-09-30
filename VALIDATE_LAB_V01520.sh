#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
echo '=== VALIDATE LAB v0.152.0 — CROSS-WORKSPACE RESEARCH DEPENDENCY GRAPH ==='
python3 -m py_compile backend/app/cross_workspace_research_dependency_graph_v01520.py backend/app/scientific_workflow_experiment_orchestration_v01510.py backend/app/integrated_computational_research_laboratory_v01500.py backend/app/scientific_model_validation_benchmark_laboratory_v01490.py backend/app/multimodal_scientific_experiment_workspace_v01480.py backend/app/graph_machine_learning_experiment_workspace_v01470.py backend/app/graph_network_science_research_workspace_v01460.py backend/app/simulation_computational_experiment_workspace_v01450.py backend/app/statistical_econometric_research_workspace_v01440.py backend/app/computational_linguistics_research_workspace_v01430.py backend/app/integrated_neural_research_workspace_v01420.py backend/app/reproducible_neural_research_package_v01418.py backend/app/embedding_explorer_v01417.py backend/app/neural_explainability_workspace_v01416.py backend/app/ablation_study_framework_v01415.py backend/app/hyperparameter_study_search_results_v01414.py backend/app/model_comparison_experiment_matrix_v01413.py backend/app/training_curves_metrics_checkpoint_visualization_v01412.py backend/app/neural_architecture_training_configuration_v01411.py backend/app/machine_learning_experiment_workspace_v01410.py backend/app/scientific_research_operating_system_v01400.py backend/app/main.py
PYTHONPATH=backend pytest -q \
 backend/tests/test_cross_workspace_research_dependency_graph_v01520.py \
 backend/tests/test_scientific_workflow_experiment_orchestration_v01510.py \
 backend/tests/test_integrated_computational_research_laboratory_v01500.py \
 backend/tests/test_scientific_model_validation_benchmark_laboratory_v01490.py \
 backend/tests/test_multimodal_scientific_experiment_workspace_v01480.py \
 backend/tests/test_graph_machine_learning_experiment_workspace_v01470.py \
 backend/tests/test_graph_network_science_research_workspace_v01460.py \
 backend/tests/test_simulation_computational_experiment_workspace_v01450.py \
 backend/tests/test_statistical_econometric_research_workspace_v01440.py \
 backend/tests/test_computational_linguistics_research_workspace_v01430.py \
 backend/tests/test_integrated_neural_research_workspace_v01420.py \
 backend/tests/test_reproducible_neural_research_package_v01418.py \
 backend/tests/test_embedding_explorer_v01417.py \
 backend/tests/test_neural_explainability_workspace_v01416.py \
 backend/tests/test_ablation_study_framework_v01415.py \
 backend/tests/test_hyperparameter_study_search_results_v01414.py \
 backend/tests/test_model_comparison_experiment_matrix_v01413.py \
 backend/tests/test_training_curves_metrics_checkpoint_visualization_v01412.py \
 backend/tests/test_neural_architecture_training_configuration_v01411.py \
 backend/tests/test_machine_learning_experiment_workspace_v01410.py \
 backend/tests/test_scientific_research_operating_system_v01400.py
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-cross-workspace-research-dependency-graph-v01520.php >/dev/null
php -l includes/class-sc-lab-scientific-workflow-experiment-orchestration-v01510.php >/dev/null
php tests/test-v01520-release-integrity.php
node tests/test-v01520.js
python3 - <<'PY2'
import json,re,hashlib
from pathlib import Path
root=Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.152.0' and m['featureVersion']=='0.152.0' and m['releaseName']=='Cross-Workspace Research Dependency Graph'
assert m['crossWorkspaceResearchDependencyGraphVersion']=='0.152.0' and m['scientificWorkflowExperimentOrchestrationVersion']=='0.151.0'
for k,v in {'v01520RequiredRouteCount':120,'v01520WorkspaceCount':14,'v01520NodeTypeCount':32,'v01520EdgeTypeCount':21,'v01520DependencyClassCount':13}.items(): assert m[k]==v,(k,m[k])
for k in ['v01520PersistentNodeAndEdgeObjects','v01520ExplicitEdgeSemantics','v01520CrossWorkspaceDependencyGraph','v01520LineageTraversal','v01520ReferenceIntegrityAudit','v01520ProvenanceAudit','v01520ImpactAnalysis','v01520StalenessCandidateModel','v01520RevalidationPlanning','v01520RecomputePlanning','v01520ReviewImpactPlanning','v01520PublicationImpactPlanning','v01520SnapshotAndDiff','v01520GraphStudioVisualization','v01520WorkflowOrchestrationHandoff','v01520ReproducibilityPackage','v01520PlatformCoreCanonicalAuthority','v01520WorkspaceExecutionAuthority','v01520WorkbenchPrototypeExecutionAuthority','v01520KnowledgeLibrarySourceAuthority','v01520LabDependencyAnalysisAuthority','v01520HumanScientificReviewRequired','v01520BackwardCompatibleV01510','v01520ManifestScopeRepairRetainedV014001']: assert m[k] is True,k
for k in ['v01520LabExecutesHeavyCompute','v01520AutomaticGraphMutation','v01520AutomaticStalenessInvalidation','v01520AutomaticRecompute','v01520AutomaticRevalidation','v01520AutomaticRetraction','v01520AutomaticScientificValidity','v01520DependencyEdgeIsCausalProof','v01520DependencyEdgeIsEvidence','v01520ImpactCandidateIsScientificInvalidation','v01520StalenessCandidateIsScientificInvalidation','v01520ShortestPathIsMechanism','v01520DegreeIsScientificImportance','v01520ReproducibilityIsScientificValidity']: assert m[k] is False,k
assert m['v014001WordPressInstalledRuntimeScope'] is True and m['v014001MutableDataExcluded'] is True
s=(root/'backend/app/main.py').read_text(); patterns={
'v01520':r'@app\.(?:get|post)\("/v1/cross-workspace-research-dependency-graph/v01520/',
'v01510':r'@app\.(?:get|post)\("/v1/scientific-workflow-experiment-orchestration/v01510/',
'v01500':r'@app\.(?:get|post)\("/v1/integrated-computational-research-laboratory/v01500/',
'v01490':r'@app\.(?:get|post)\("/v1/scientific-model-validation-benchmark-laboratory/v01490/',
'v01480':r'@app\.(?:get|post)\("/v1/multimodal-scientific-experiment-workspace/v01480/',
'v01470':r'@app\.(?:get|post)\("/v1/graph-machine-learning-experiment-workspace/v01470/',
'v01460':r'@app\.(?:get|post)\("/v1/graph-network-science-research-workspace/v01460/',
'v01450':r'@app\.(?:get|post)\("/v1/simulation-computational-experiment-workspace/v01450/',
'v01440':r'@app\.(?:get|post)\("/v1/statistical-econometric-research-workspace/v01440/',
'v01430':r'@app\.(?:get|post)\("/v1/computational-linguistics-research-workspace/v01430/',
'v01420':r'@app\.(?:get|post)\("/v1/integrated-neural-research-workspace/v01420/',
'v01418':r'@app\.(?:get|post)\("/v1/reproducible-neural-research-package/v01418/',
'v01417':r'@app\.(?:get|post)\("/v1/embedding-explorer/v01417/',
'v01416':r'@app\.(?:get|post)\("/v1/neural-explainability-workspace/v01416/',
'v01415':r'@app\.(?:get|post)\("/v1/ablation-study-framework/v01415/',
'v01414':r'@app\.(?:get|post)\("/v1/hyperparameter-study-search-results/v01414/',
'v01413':r'@app\.(?:get|post)\("/v1/model-comparison-experiment-matrix/v01413/',
'v01412':r'@app\.(?:get|post)\("/v1/training-curves-metrics-checkpoint-visualization/v01412/',
'v01411':r'@app\.(?:get|post)\("/v1/neural-architecture-training-configuration/v01411/',
'v01410':r'@app\.(?:get|post)\("/v1/machine-learning-experiment-workspace/v01410/',
'v01400':r'@app\.(?:get|post)\("/v1/scientific-research-operating-system/v01400/'}
counts={k:len(re.findall(v,s)) for k,v in patterns.items()}; expected={'v01520':120,'v01510':103,'v01500':86,'v01490':78,'v01480':73,'v01470':65,'v01460':61,'v01450':56,'v01440':52,'v01430':48,'v01420':39,'v01418':36,'v01417':33,'v01416':31,'v01415':30,'v01414':31,'v01413':30,'v01412':29,'v01411':33,'v01410':27,'v01400':25}; assert counts==expected,(counts,expected)
plugin=(root/'includes/class-sc-lab-plugin.php').read_text(); bootstrap=(root/'sustainable-catalyst-lab.php').read_text()
for x in ['cross-workspace-research-dependency-graph-v01520','project-workspace-research-dependency-v01520','scientific-workflow-experiment-orchestration-v01510']: assert x in plugin,x
assert 'class-sc-lab-cross-workspace-research-dependency-graph-v01520.php' in bootstrap
for rel,expected_hash in m.get('wordpressCriticalFiles',{}).items():
    f=root/rel; assert f.exists(),f'missing WordPress critical file {rel}'; assert hashlib.sha256(f.read_bytes()).hexdigest()==expected_hash,f'WordPress hash mismatch {rel}'
for rel,expected_hash in m.get('backendCriticalFiles',{}).items():
    f=root/rel; assert f.exists(),f'missing backend critical file {rel}'; assert hashlib.sha256(f.read_bytes()).hexdigest()==expected_hash,f'backend hash mismatch {rel}'
print('PASS:',counts); print('PASS: WordPress critical-file manifest verifies',len(m.get('wordpressCriticalFiles',{})),'files'); print('PASS: backend critical-file manifest verifies',len(m.get('backendCriticalFiles',{})),'files')
PY2
echo 'PASS - Lab v0.152.0 local validation complete.'
