'use strict';
const fs=require('fs');
const read=p=>fs.readFileSync(p,'utf8');
const engine=read('assets/js/modules/scientific-visualization-engine-v0440.js');
const studio=read('assets/js/modules/model-studio-v0440.js');
const numerical=read('assets/js/modules/numerical-visualization-studio.js');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const checks=[
 [engine.includes("VERSION='0.44.0'"),'interactive graph engine release version'],
 [engine.includes('wheel')&&engine.includes('zoom('),'wheel and button zoom implementation'],
 [engine.includes('pointerdown')&&engine.includes('is-panning'),'drag-pan implementation'],
 [engine.includes('ArrowLeft')&&engine.includes("e.key==='0'"),'keyboard pan / reset controls'],
 [engine.includes('sc-sve0440-crosshair'),'crosshair inspection'],
 [engine.includes('sc-sve0440-band'),'confidence-ribbon rendering'],
 [engine.includes('sc-sve0440-error'),'error-bar rendering'],
 [engine.includes('seriesToggle'),'series visibility controls'],
 [engine.includes("button('SVG'")&&engine.includes("button('PNG'")&&engine.includes("button('CSV'")&&engine.includes("button('JSON'"),'publication export toolbar'],
 [engine.includes('Accessible data table')&&engine.includes('focusablePoints'),'accessible graph fallback'],
 [studio.includes("VERSION='0.44.0'"),'Model Studio browser release version'],
 [studio.includes('publicationSpec')&&studio.includes('applyPublication'),'publication figure controls wired'],
 [studio.includes('ScientificVisualizationEngineV0440'),'Model Studio consumes v0.44 shared engine'],
 [numerical.includes('ScientificVisualizationEngineV0440'),'Numerical Visualization consumes v0.44 shared engine'],
 [template.includes('data-ms-v0440-publication-apply'),'publication apply UI'],
 [template.includes('data-ms-v0440-publication-source'),'publication source metadata UI'],
 [template.includes('data-ms-v0440-publication-method'),'publication method metadata UI'],
 [template.includes('data-ms-v0440-publication-aspect'),'publication aspect-ratio UI'],
 [plugin.includes("'scientific-visualization-engine-v0440','model-studio-v0440'"),'v0.44 engine loads before Model Studio'],
 [plugin.includes('sc-lab-scientific-visualization-engine-v0440.css'),'v0.44 engine stylesheet enqueued']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
