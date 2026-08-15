'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const pa=read('assets/js/modules/probabilistic-analysis-v0480.js');
const py=read('backend/app/correlated_uncertainty.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const graph=read('assets/js/modules/graph-studio-v0470.js');
const pkg=read('assets/js/modules/reproducible-model-package-v0500.js');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const checks=[
 [pa.includes("FEATURE_VERSION='0.53.0'")&&pa.includes('CorrelatedUncertaintyV0530'),'v0.53 correlated uncertainty browser contract'],
 [pa.includes('probabilistic/v0530/')&&pa.includes("api0530('analyze'"),'v0.53 governed compute route used'],
 [py.includes('gaussian-copula')&&py.includes('_correlation_sqrt'),'Gaussian copula dependency sampler implemented'],
 [py.includes('matrixType')&&py.includes('covariance')&&py.includes('positive semidefinite'),'correlation/covariance validation implemented'],
 [py.includes('Saltelli–Sobol sensitivity is not available for dependent inputs'),'dependent Saltelli-Sobol blocked'],
 [py.includes('automaticDependencyInference')&&py.includes('automaticCausalInterpretation'),'dependency governance boundaries explicit'],
 [template.includes('Input dependence')&&template.includes('data-pa-v0530-matrix')&&template.includes('Gaussian copula'),'dependency controls rendered in existing uncertainty workspace'],
 [template.includes('data-pa-v0480-graph="dependency"')&&template.includes('Dependency diagnostics'),'dependency visualization/evidence rendered'],
 [pa.includes('sc-lab:open-graph-studio')&&graph.includes('openHandoff'),'dependency figures hand off to Graph Studio'],
 [pkg.includes("'analysisPackets'")&&pa.includes('correlated-uncertainty-v0530'),'v0.50 reproducible package path receives v0.53 evidence'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-correlated-uncertainty-v0530'),'v0.53 stylesheet enqueued'],
 [compute.includes('/compute/core/model-studio/probabilistic/v0530/analyze')&&compute.includes('estimate-dependency'),'WordPress v0.53 compute proxies registered']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
