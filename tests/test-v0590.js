'use strict';
const fs=require('fs');const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/scientific-audit-v0590.js');
const py=read('backend/app/scientific_audit_v0590.py');
const main=read('backend/app/main.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [js.includes("VERSION='0.59.0'")&&js.includes('ScientificAuditV0590'),'v0.59 browser contract'],
 [py.includes('scan_surface')&&py.includes('EXECUTABLE_KEYS')&&py.includes('SECRET_KEYS'),'threat-surface and secret leakage scan implemented'],
 [py.includes('data_minimization_review')&&py.includes('rawValuesReturned'),'data minimization review avoids raw-value return'],
 [py.includes('build_redacted_export')&&py.includes('exportHash'),'deterministic redacted export implemented'],
 [py.includes('reproducibility_audit')&&py.includes('verify_model_package'),'reproducibility/model package audit implemented'],
 [py.includes('automaticCertificationAuthorized')&&py.includes('automaticHighStakesDecisionAuthorized'),'automatic certification and high-stakes decisions disabled'],
 [main.includes('/v1/scientific-audit/v0590/audit')&&main.includes('/v1/scientific-audit/v0590/redact-export'),'FastAPI v0.59 audit routes implemented'],
 [template.includes('data-scientific-audit-v0590')&&template.includes('Audit current workflow'),'scientific audit integrated contextually'],
 [js.includes("s.add('analysisPackets'")&&js.includes('scientific-audit-v0590'),'audit evidence saves to active project'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-scientific-audit-v0590')&&plugin.includes("'scientific-audit-v0590'"),'v0.59 assets registered'],
 [compute.includes('/compute/core/scientific-audit/v0590/audit')&&compute.includes('/compute/core/scientific-audit/v0590/minimize'),'WordPress v0.59 audit proxies registered'],
 [!js.includes('MutationObserver'),'v0.59 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
