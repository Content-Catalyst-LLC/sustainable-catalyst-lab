const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const engine=fs.readFileSync(path.join(root,'assets/js/modules/scientific-visualization-engine-v0730.js'),'utf8');
const studio=fs.readFileSync(path.join(root,'assets/js/modules/graph-studio-v0730.js'),'utf8');
const template=fs.readFileSync(path.join(root,'templates/lab-app.php'),'utf8');
const checks=[
 [engine.includes("VERSION='0.73.0'")&&engine.includes("ENGINE_VERSION='2.0.0'"),'Visualization Engine 2 browser contract'],
 [engine.includes("svg2d")&&engine.includes("canvas4d"),'Renderer registry exposes SVG and 4D canvas adapters'],
 [engine.includes("'surface-4d'")&&engine.includes('advanced-visualization-front-door-v0710'),'4D surface delegates to the existing v0.71 renderer'],
 [engine.includes('scientific-visualization-engine-v0440'),'legacy 2D delegates to the existing shared SVG renderer'],
 [engine.includes('function capture(host,spec)'),'interactive 4D state capture is available for saved figures'],
 [studio.includes("VERSION='0.73.0'")&&studio.includes("FIGURE_SCHEMA='sc-lab-scientific-figure/0.73.0'"),'Graph Studio v0.73 saved-figure contract'],
 [studio.includes("kind:'surface-4d'")&&studio.includes('load4DExample'),'Graph Studio exposes first-class 4D figure construction'],
 [studio.includes('ScientificVisualizationEngineV0730'),'Graph Studio uses Visualization Engine 2 rather than a parallel renderer'],
 [studio.includes("recordType:'scientific-figure-v0730'"),'new project figures persist as v0.73 scientific figures'],
 [studio.includes("v.recordType==='scientific-figure-v0470'"),'legacy v0.47 saved figures remain discoverable'],
 [template.includes('4D response surface · Canvas'),'Graph Studio UI exposes the 4D renderer'],
 [template.includes('data-gs-v0730-renderer-badge'),'Graph Studio shows active renderer identity']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
