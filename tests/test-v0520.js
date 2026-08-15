'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const bayes=read('assets/js/modules/bayesian-inference-v0520.js');
const py=read('backend/app/bayesian_inference.py');
const css=read('assets/css/sc-lab-bayesian-inference-v0520.css');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const pkg=read('assets/js/modules/reproducible-model-package-v0500.js');
const checks=[
 [bayes.includes("VERSION='0.52.0'"),'v0.52.0 Bayesian browser runtime'],
 [bayes.includes('compute/core/model-studio/bayesian/')&&bayes.includes("api('fit'")&&bayes.includes("api('posterior-predictive'"),'governed Bayesian compute routes wired'],
 [py.includes('gibbs-normal-inverse-gamma')&&py.includes('adaptive-random-walk-metropolis'),'Gaussian Gibbs and GLM Metropolis samplers implemented'],
 [py.includes('split-Rhat')&&py.includes('autocorrelation ESS')&&py.includes('mcseMean'),'posterior diagnostics implemented'],
 [py.includes('automaticConvergenceCertification": False')&&py.includes('automaticPriorSelection'),'automatic convergence/prior selection disabled'],
 [py.includes('FORBIDDEN_EXECUTABLE_KEYS')&&py.includes('_reject_executable_fields'),'executable Bayesian payload fields rejected'],
 [bayes.includes('analysisPackets')&&bayes.includes('bayesian-inference-v0520'),'Bayesian evidence saved to active project'],
 [bayes.includes('sc-lab:open-graph-studio')&&bayes.includes('ScientificVisualizationEngineV0440'),'shared graph engine and Graph Studio handoff preserved'],
 [bayes.includes('MutationObserver')===false,'v0.52.0 introduces no MutationObserver'],
 [pkg.includes("'analysisPackets'")&&pkg.includes("VERSION='0.50.0'"),'v0.50 reproducible packages capture Bayesian evidence'],
 [template.includes('data-bayesian-inference-v0520')&&template.includes('Bayesian inference, posterior diagnostics &amp; posterior predictive modeling'),'Bayesian Model Studio workspace rendered'],
 [template.includes('Sample posterior')&&template.includes('Posterior predictive')&&template.includes('Open figure in Graph Studio'),'Bayesian actions visible'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'v0.48.3 six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes("'bayesian-inference-v0520'")&&plugin.includes('sc-lab-bayesian-inference-v0520'),'v0.52.0 JS/CSS assets enqueued'],
 [css.includes('.sc-bayes0520')&&css.includes('@media'),'Bayesian workspace has responsive styling']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
