const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const js=fs.readFileSync(path.join(root,'assets/js/modules/advanced-visualization-front-door-v0710.js'),'utf8');
const checks=[
 [js.includes("VERSION='0.71.0'"),'v0.71 browser module version'],
 [js.includes('function response(x,y,w)'),'deterministic response field'],
 [js.includes('function rotate4(p,s)'),'4D rotation engine'],
 [js.includes('function drawTesseract'),'projected tesseract renderer'],
 [js.includes('function drawSurface'),'response surface renderer'],
 [js.includes('showVector:true'),'vector field enabled'],
 [js.includes('showUncertainty:true'),'uncertainty guide enabled'],
 [js.includes('showContours:true'),'contours enabled'],
 [js.includes('computeRequired:false'),'front door compute-independent'],
 [!js.includes('fetch('),'front door makes no network fetches']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
