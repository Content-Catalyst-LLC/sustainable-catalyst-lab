'use strict';
const fs=require('fs');const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/scientific-workflow-composer-v0570.js');
const py=read('backend/app/scientific_workflow_composer.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [js.includes("VERSION='0.57.0'")&&js.includes('ScientificWorkflowComposerV0570'),'v0.57 browser contract'],
 [py.includes('run_workflow')&&py.includes('compare_runs')&&py.includes('normalize_workflow'),'workflow normalize/run/compare backend implemented'],
 [py.includes('dataset.profile')&&py.includes('data.transform')&&py.includes('statistics.fit')&&py.includes('uncertainty.correlated')&&py.includes('experiment.design')&&py.includes('report.bundle'),'cross-stage scientific catalog implemented'],
 [py.includes('legacyOperationalOrchestrator')&&py.includes('workflow-orchestration-v0321'),'v0.32 operational orchestrator retained as separate layer'],
 [py.includes('automaticExperimentExecution')&&py.includes('automaticRegistryPromotion')&&py.includes('automaticPublication'),'unsafe automatic actions disabled'],
 [py.includes('workflowHash')&&py.includes('runHash')&&py.includes('outputHash'),'workflow reproducibility hashes implemented'],
 [template.includes('data-scientific-workflow-v0570')&&template.includes('Scientific Workflow Composer'),'composer integrated in existing Scientific Workflows workspace'],
 [template.includes('data-wfc-v0570-run')&&template.includes('data-wfc-v0570-rerun')&&template.includes('data-wfc-v0570-save-workflow'),'run/rerun/save controls rendered'],
 [js.includes('scientificWorkflowsV0570')&&js.includes('scientificWorkflowRunsV0570')&&js.includes('analysisPackets'),'project workflow persistence and reproducibility evidence implemented'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-scientific-workflow-composer-v0570')&&plugin.includes("'scientific-workflow-composer-v0570'"),'v0.57 assets registered'],
 [compute.includes('/compute/core/workflows/v0570/run')&&compute.includes('/compute/core/workflows/v0570/compare'),'WordPress v0.57 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.57 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
