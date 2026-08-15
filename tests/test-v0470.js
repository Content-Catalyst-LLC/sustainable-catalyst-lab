'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const studio=read('assets/js/modules/graph-studio-v0470.js');
const interfaceJs=read('assets/js/modules/interface-reorganization-v0470.js');
const model=read('assets/js/modules/model-studio-v0460.js');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const workspace=read('assets/js/modules/workspace.js');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const checks=[
 [studio.includes("VERSION='0.47.0'")&&studio.includes('FIGURE_SCHEMA'),'Graph Studio browser release contract'],
 [studio.includes('buildGraph')&&studio.includes('refreshLibrary')&&studio.includes('openHandoff'),'dedicated figure workspace workflow'],
 [studio.includes('ScientificVisualizationEngineV0440'),'Graph Studio consumes shared v0.44 graph engine'],
 [studio.includes("['svg','png','csv','json']")||studio.includes("['svg', 'png', 'csv', 'json']")||studio.includes("exports:['svg','png','csv','json']"),'publication export contract retained'],
 [template.includes('Scientific Figure Workspace')&&template.includes('data-lab-module="graph-studio"'),'dedicated Graph Studio panel'],
 [template.includes("'Model' => array(")&&template.includes("'Visualize' => array("),'Model and Visualize navigation groups'],
 [template.includes('data-lab-nav-group-toggle'),'collapsible navigation controls'],
 [template.includes('data-open-module="graph-studio"'),'Overview Graph Studio front door'],
 [template.includes('data-ms-v0460-open-graph-studio'),'Model Studio graph handoff control'],
 [model.includes("sc-lab:open-graph-studio")&&model.includes('openGraphStudio'),'Model Studio dispatches Graph Studio handoff'],
 [interfaceJs.includes('is-collapsed')&&interfaceJs.includes('scLabNavGroupsV0470'),'navigation collapse persistence'],
 [workspace.includes("id:'graph-studio'")&&workspace.includes("group:'Visualize'"),'command search includes Graph Studio'],
 [plugin.includes("'graph-studio-v0470','interface-reorganization-v0470'"),'Graph Studio and interface runtime modules loaded'],
 [compute.includes('/compute/core/graph-studio/figures/normalize')&&compute.includes('/compute/core/graph-studio/workspaces/build'),'WordPress Graph Studio compute proxies registered']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
