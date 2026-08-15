'use strict';
const fs=require('fs');const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/integrated-research-beta-v0600.js');
const py=read('backend/app/integrated_research_beta_v0600.py');
const main=read('backend/app/main.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [js.includes("VERSION='0.60.0'")&&js.includes('IntegratedResearchBetaV0600'),'v0.60 browser beta contract'],
 [py.includes('capability_matrix')&&py.includes('beta_readiness')&&py.includes('build_beta_packet'),'integrated beta backend implemented'],
 [py.includes('metadata summaries only')&&py.includes('rawSensitiveDataInBetaPacket'),'metadata-only readiness boundary implemented'],
 [py.includes('automaticScientificCertificationAuthorized')&&py.includes('automaticPublicationAuthorized'),'automatic certification/publication disabled'],
 [main.includes('/v1/integrated-research/v0600/readiness')&&main.includes('/v1/integrated-research/v0600/packet'),'FastAPI v0.60 routes implemented'],
 [template.includes('data-integrated-research-beta-v0600')&&template.includes('Assess integrated research journey'),'integrated beta contextual UI present'],
 [js.includes("recordType:'integrated-research-beta-v0600'")&&js.includes("s.add('analysisPackets'"),'beta evidence saves to active project'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-integrated-research-beta-v0600')&&plugin.includes("'integrated-research-beta-v0600'"),'v0.60 assets registered'],
 [compute.includes('/compute/core/integrated-research/v0600/readiness')&&compute.includes('/compute/core/integrated-research/v0600/packet'),'WordPress v0.60 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.60 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
