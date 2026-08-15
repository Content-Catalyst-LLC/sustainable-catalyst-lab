'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const pa=read('assets/js/modules/probabilistic-analysis-v0480.js');
const model=read('assets/js/modules/model-studio-v0460.js');
const graph=read('assets/js/modules/graph-studio-v0470.js');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const workspace=read('assets/js/modules/workspace.js');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const checks=[
 [pa.includes("VERSION='0.48.0'")&&pa.includes('ProbabilisticAnalysisV0480'),'v0.48 browser release contract'],
 [pa.includes('latin-hypercube')&&pa.includes('saltelli-sobol'),'probabilistic sampling designs exposed'],
 [pa.includes('ScientificVisualizationEngineV0440'),'probabilistic visualizations use shared graph engine'],
 [pa.includes("sc-lab:open-graph-studio")&&pa.includes('openGraphStudio'),'probabilistic figure handoff to Graph Studio'],
 [pa.includes("sc-lab:open-probabilistic-analysis")&&pa.includes('loadModel'),'Model Studio handoff receiver'],
 [template.includes('Integrated Uncertainty, Sensitivity &amp; Probabilistic Visualization')&&template.includes('data-lab-module="probabilistic-analysis"'),'dedicated uncertainty and sensitivity panel'],
 [template.includes('Distributions are never inferred silently'),'uncertainty assumptions remain explicit'],
 [template.includes("'probabilistic-analysis' => 'Uncertainty & sensitivity'")&&template.includes("'ensemble-uncertainty' => 'Registered-model ensembles'"),'modern and legacy uncertainty workflows distinguished'],
 [template.includes('data-ms-v0460-open-probabilistic'),'Model Studio probabilistic handoff control'],
 [model.includes('openProbabilistic')&&model.includes('currentModel:()=>state.model||buildModel()'),'Model Studio exposes governed probabilistic handoff'],
 [workspace.includes("id:'probabilistic-analysis'")&&workspace.includes("label:'Uncertainty & sensitivity'"),'command search includes uncertainty studio'],
 [plugin.includes("'probabilistic-analysis-v0480'")&&plugin.includes('sc-lab-probabilistic-analysis-v0480'),'v0.48 runtime JS and CSS loaded'],
 [compute.includes('/compute/core/model-studio/probabilistic/analyze')&&compute.includes('model_studio_probabilistic_analyze'),'WordPress probabilistic compute proxy registered'],
 [graph.includes('openHandoff'),'Graph Studio remains available as the figure destination']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
