const fs=require('fs'),path=require('path'),root=path.join(__dirname,'..');function must(x,m){if(!x){console.error('FAIL:',m);process.exit(1)}}
const js=fs.readFileSync(path.join(root,'assets/js/modules/soil-organic-carbon-v0890.js'),'utf8');
must(js.includes("DOMAIN='0.6.0'"),'domain version');must(js.includes('profileStockUrl'),'profile route config');must(js.includes('projectPacketUrl'),'project packet route config');must(js.includes("add('carbonCycleRecords'"),'project save');must(js.includes('sc-lab:open-graph-studio'),'Graph Studio handoff');must(js.includes('Fixed-depth'),'fixed-depth boundary visible');
const ws=fs.readFileSync(path.join(root,'assets/js/modules/workspace.js'),'utf8');must(ws.includes("id:'soil-organic-carbon'"),'command search module');
console.log('PASS - Lab v0.89.0 / Carbon & Nature v0.6.0 browser contracts');
