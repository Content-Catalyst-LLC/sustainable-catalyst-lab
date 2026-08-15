'use strict';
const fs=require('fs');const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/scientific-claims-v0620.js');
const py=read('backend/app/scientific_claims_traceability_v0620.py');
const main=read('backend/app/main.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [js.includes("VERSION='0.62.0'")&&js.includes('ScientificClaimsV0620'),'v0.62.0 browser claims traceability contract'],
 [py.includes('normalize_claim')&&py.includes('normalize_conclusion')&&py.includes('evaluate_matrix')&&py.includes('build_traceability_packet'),'scientific claims/evidence backend implemented'],
 [py.includes('contradicts')&&py.includes('uncertainty')&&py.includes('limitation'),'contradicting evidence and uncertainty/limitation roles preserved'],
 [py.includes('automaticClaimInferenceAuthorized')&&py.includes('automaticCausalClaimAuthorized')&&py.includes('automaticConclusionGenerationAuthorized'),'automatic inference, causal claim, and conclusion generation disabled'],
 [main.includes('/v1/scientific-claims/v0620/normalize-claim')&&main.includes('/v1/scientific-claims/v0620/evaluate')&&main.includes('/v1/scientific-claims/v0620/packet'),'FastAPI v0.62 claims routes implemented'],
 [template.includes('data-scientific-claims-v0620')&&template.includes('Evaluate evidence matrix')&&template.includes('Record claim review')&&template.includes('Record conclusion review'),'contextual claims/evidence UI present'],
 [js.includes("'scientificClaimsV0620'")&&js.includes("'scientificConclusionsV0620'")&&js.includes("recordType:'scientific-claims-evidence-matrix-v0620'"),'claims, conclusions, and matrix evidence save to active project'],
 [js.includes('evidenceCatalog()')&&js.includes('raw scientific data was not copied'),'metadata-only project evidence catalog boundary'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-scientific-claims-v0620')&&plugin.includes("'scientific-claims-v0620'"),'v0.62 assets registered'],
 [compute.includes('/compute/core/scientific-claims/v0620/evaluate')&&compute.includes('/compute/core/scientific-claims/v0620/review-claim')&&compute.includes('/compute/core/scientific-claims/v0620/packet'),'WordPress v0.62 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.62 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
