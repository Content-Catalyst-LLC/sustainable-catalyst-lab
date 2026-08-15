'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const ui=read('assets/js/modules/presentation-repair-v0481.js');
const css=read('assets/css/sc-lab-presentation-v0481.css');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const app=read('assets/js/sc-lab-app.js');
const checks=[
 [ui.includes("VERSION='0.48.1'")&&ui.includes('PresentationRepairV0481'),'v0.48.1 browser presentation contract'],
 [template.includes('data-v0481-workspace-switcher')&&template.includes('Model Studio')&&template.includes('Graph Studio'),'persistent primary workspace switcher'],
 [template.includes('data-v0481-overview-canvas')&&template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front-door canvas'],
 [ui.includes('ScientificVisualizationEngineV0440')&&ui.includes('figures(app)'),'overview uses shared graph engine and project figure preview'],
 [ui.includes('threeApplicationCardRowPreserved')===false,'browser module does not rewrite outer application cards'],
 [template.includes("'Research operations' => array(")&&template.includes("'Project' => array(")&&template.includes("'Visualize' => array("),'sidebar information architecture reorganized'],
 [template.includes('sc-lab-secondary-drawer-v0481')&&template.includes('Scientific tool library'),'specialist tools demoted to secondary drawers'],
 [css.includes('.sc-lab-overview-stage-v0481')&&css.includes('min-height:520px'),'large graph-forward scientific workspace'],
 [css.includes('.sc-lab-workspace-switcher')&&css.includes('.sc-lab-overview-launcher-v0481'),'workspace switcher and research launcher styling'],
 [app.includes("new CustomEvent('sc-lab:module-opened'")&&app.includes("['Figures', (project.visualizations || []).length"),'core app publishes module state and concise overview metrics'],
 [plugin.includes('sc-lab-presentation-v0481')&&plugin.includes("'presentation-repair-v0481'"),'v0.48.1 CSS and JS enqueued'],
 [template.includes('Open full application')&&template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'related application links retained inside Lab navigation']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
