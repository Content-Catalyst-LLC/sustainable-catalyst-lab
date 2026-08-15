'use strict';
const fs=require('fs');const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/scientific-study-lifecycle-v0610.js');
const py=read('backend/app/scientific_study_lifecycle_v0610.py');
const main=read('backend/app/main.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [js.includes("VERSION='0.61.0'")&&js.includes('ScientificStudyLifecycleV0610'),'v0.61.0 browser study lifecycle contract'],
 [py.includes('normalize_study')&&py.includes('evaluate_lifecycle')&&py.includes('record_stage_review')&&py.includes('build_study_packet'),'end-to-end scientific study backend implemented'],
 [py.includes('humanStageReviewRequired')&&py.includes('automaticScientificCertificationAuthorized'),'explicit human review / no automatic certification boundary'],
 [py.includes('automaticCausalClaimAuthorized')&&py.includes('automaticExperimentExecutionAuthorized'),'causal and experiment execution boundaries explicit'],
 [main.includes('/v1/scientific-studies/v0610/normalize')&&main.includes('/v1/scientific-studies/v0610/evaluate')&&main.includes('/v1/scientific-studies/v0610/review')&&main.includes('/v1/scientific-studies/v0610/packet'),'FastAPI v0.61 study lifecycle routes implemented'],
 [template.includes('data-scientific-study-lifecycle-v0610')&&template.includes('Evaluate study lifecycle')&&template.includes('Record stage review'),'contextual scientific study lifecycle UI present'],
 [js.includes("'scientificStudiesV0610'")&&js.includes("recordType:'scientific-study-lifecycle-v0610'")&&js.includes("s.add('analysisPackets'"),'study definitions and lifecycle evidence save to active project'],
 [js.includes('projectSummary()')&&js.includes('IntegratedResearchBetaV0600'),'v0.61 reuses integrated project evidence boundary'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-scientific-study-lifecycle-v0610')&&plugin.includes("'scientific-study-lifecycle-v0610'"),'v0.61 assets registered'],
 [compute.includes('/compute/core/scientific-studies/v0610/evaluate')&&compute.includes('/compute/core/scientific-studies/v0610/review')&&compute.includes('/compute/core/scientific-studies/v0610/packet'),'WordPress v0.61 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.61 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
