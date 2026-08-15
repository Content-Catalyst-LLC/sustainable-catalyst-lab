'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/data-transformations-v0550.js');
const py=read('backend/app/data_transformations.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const graph=read('assets/js/modules/graph-studio-v0470.js');
const pkg=read('assets/js/modules/reproducible-model-package-v0500.js');
const app=read('assets/js/sc-lab-app.js');
const checks=[
 [js.includes("VERSION='0.55.0'")&&js.includes('DataTransformationsV0550'),'v0.55 browser contract'],
 [py.includes('normalize_plan')&&py.includes('transform_dataset')&&py.includes('join_datasets'),'governed transformation backend implemented'],
 [py.includes('compile_equation')&&py.includes('evaluate(compiled'),'derived variables reuse safe equation grammar'],
 [py.includes('_UNIT_CATALOG')&&py.includes('convert_unit_value'),'governed unit conversion catalog implemented'],
 [py.includes('inputHash')&&py.includes('outputHash')&&py.includes('operationHash')&&py.includes('resultHash'),'reproducible transformation lineage hashes implemented'],
 [py.includes('automaticUnitInference')&&py.includes('automaticImputation')&&py.includes('automaticFeatureEngineering'),'scientific preprocessing boundaries explicit'],
 [template.includes('data-data-transform-v0550')&&template.includes('Scientific data transformation &amp; derived variables'),'v0.55 remains contextual inside Dataset Inspector'],
 [template.includes('data-dt-v0550-plan')&&template.includes('data-dt-v0550-lineage'),'plan and lineage controls rendered'],
 [template.includes('data-dt-v0550-join')&&template.includes('Governed dataset join'),'bounded join controls rendered'],
 [app.includes('_scLabGetCurrentDataset')&&app.includes('_scLabSetCurrentDataset'),'current dataset bridge exposed without new navigation'],
 [js.includes('sc-lab:open-graph-studio')&&graph.includes('openHandoff'),'transformed variables hand off to Graph Studio'],
 [pkg.includes("'analysisPackets'")&&js.includes('data-transformation-v0550'),'v0.50 reproducible package path receives transformation lineage'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-data-transformations-v0550')&&plugin.includes("'data-transformations-v0550'"),'v0.55 assets registered'],
 [compute.includes('/compute/core/datasets/v0550/transform')&&compute.includes('/compute/core/datasets/v0550/join'),'WordPress v0.55 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.55 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
