const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const loop=fs.readFileSync(path.join(root,'assets/js/modules/homepage-biodiversity-loop-v0721.js'),'utf8');
const renderer=fs.readFileSync(path.join(root,'assets/js/modules/advanced-visualization-front-door-v0710.js'),'utf8');
const checks=[
 [loop.includes("VERSION='0.72.1'"),'v0.72.1 loop module version'],
 [loop.includes('data-v0721-autoplay-loop'), 'homepage autoplay selector'],
 [loop.includes("prefers-reduced-motion: reduce"),'reduced-motion preference honored'],
 [loop.includes('button.click()'),'existing renderer animation control reused'],
 [loop.includes('event.matches?stop(root):start(root)'),'runtime reduced-motion stop/resume'],
 [!loop.includes('fetch('),'autoplay module remains network-independent'],
 [renderer.includes("(Math.sin(ts/2400)+1)/2"),'existing seamless biodiversity 0-1-0 loop preserved'],
 [renderer.includes("'Pause time sweep'"),'user pause control preserved']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
