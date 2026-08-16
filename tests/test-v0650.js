const fs=require('fs'),path=require('path'),root=path.join(__dirname,'..');
function text(p){return fs.readFileSync(path.join(root,p),'utf8')} function pass(x,m){if(!x)throw new Error('FAIL - '+m);console.log('PASS - '+m)}
const js=text('assets/js/modules/evidence-grading-v0650.js'),tpl=text('templates/lab-app.php'),plugin=text('includes/class-sc-lab-plugin.php'),core=text('includes/class-sc-lab-python-compute-core-v0261.php');
pass(js.includes("VERSION='0.65.0'"),'v0.65 browser module version');
pass(js.includes('scientificEvidenceGradingAssessmentsV0650'),'evidence boundary assessment project collection');
pass(js.includes("recordType:'scientific-evidence-consensus-v0650'"),'evidence/consensus packet enters analysisPackets');
pass(js.includes("recordType==='systematic-evidence-synthesis-v0640'"),'v0.64 synthesis evidence reused');
pass(js.includes('scientificLiteratureClaimLinksV0630'),'v0.63 literature provenance reused');
pass(js.includes('scientificClaimsV0620'),'v0.62 claims reused');
pass(js.includes('no numeric truth score'),'numeric truth score boundary explicit');
pass(!js.includes('MutationObserver'),'v0.65 introduces no MutationObserver');
pass(tpl.includes('data-evidence-grading-v0650'),'contextual evidence grading panel present');
pass((tpl.match(/data-v0483-primary=/g)||[]).length===6,'six-destination rail preserved');
pass(tpl.includes('Prototyping Workbench')&&tpl.includes('Decision Studio')&&tpl.includes('Site Intelligence'),'three application card row preserved');
pass(tpl.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved');
pass(plugin.includes("'evidence-grading-v0650'"),'v0.65 JS module registered');
pass(plugin.includes('sc-lab-evidence-grading-v0650'),'v0.65 stylesheet registered');
pass(core.includes('/compute/core/evidence-grading/v0650/evaluate'),'WordPress v0.65 evaluate proxy registered');
