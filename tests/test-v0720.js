const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const js=fs.readFileSync(path.join(root,'assets/js/modules/advanced-visualization-front-door-v0710.js'),'utf8');
const css=fs.readFileSync(path.join(root,'assets/css/sc-lab-homepage-biodiversity-v0720.css'),'utf8');
const checks=[
 [js.includes("VERSION='0.71.0'"),'v0.71 shared 4D renderer preserved'],
 [js.includes("v0710Profile==='biodiversity'"),'biodiversity profile selection'],
 [js.includes('function biodiversityResponse(x,y,t)'),'deterministic biodiversity response field'],
 [js.includes("axis:['Habitat quality','Climate stress','Biodiversity response']"),'biodiversity axis semantics'],
 [js.includes("dimensionLabel:'Time / disturbance progression'"),'fourth-dimension time semantics'],
 [js.includes("profiles:['generic','biodiversity']"),'shared renderer exposes both profiles'],
 [js.includes('function rotate4(p,s)'),'4D rotation engine preserved'],
 [js.includes('function drawTesseract'),'tesseract projection preserved'],
 [js.includes('drawBiodiversitySamples'),'synthetic sample overlay'],
 [!js.includes('fetch('),'homepage renderer remains network-independent'],
 [css.includes('.sc-lab-home-v0720__stage'),'homepage scientific stage styling'],
 [css.includes('@media(prefers-reduced-motion:reduce)'),'reduced-motion homepage handling']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
