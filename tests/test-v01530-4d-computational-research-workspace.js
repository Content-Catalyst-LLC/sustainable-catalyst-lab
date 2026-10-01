const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const safe=fs.readFileSync(path.join(root,'assets/js/sc-lab-safe-bootstrap-v01530.js'),'utf8');
const linked=fs.readFileSync(path.join(root,'assets/js/sc-lab-linked-scientific-views-v01530.js'),'utf8');
const persistence=fs.readFileSync(path.join(root,'assets/js/sc-lab-scene-persistence-provenance-handoff-v01530.js'),'utf8');
const workspace=fs.readFileSync(path.join(root,'assets/js/sc-lab-4d-computational-research-workspace-v01530.js'),'utf8');
const checks={
 'safe release':safe.includes("const VERSION = '0.153.0'"),
 'safe authority':safe.includes("labPresentationAuthority = 'v01530'"),
 'linked release':linked.includes("const VERSION = '0.153.0'"),
 'explicit grid palette retained':linked.includes("grid:'#d9e2ea'"),
 'explicit accent palette retained':linked.includes("accent:'#ff3842'"),
 'no document root color dependency':!linked.includes('getComputedStyle(d.documentElement).color'),
 'persistence release':persistence.includes("const VERSION='0.153.0'"),
 'browser scene migration key retained':persistence.includes("'sc-lab-v015212-scenes'"),
 'workspace release':workspace.includes("const VERSION='0.153.0'"),
 'promote scene action':workspace.includes('Promoting scene into the project workspace'),
 'immutable revision action':workspace.includes('Creating immutable workspace revision'),
 'fork action':workspace.includes('Forking workspace asset with explicit lineage'),
 'descriptive compare':workspace.includes('No scientific conclusion was inferred'),
 'restore without compute':workspace.includes('restored without rerunning computation'),
 'no mutation observer':!workspace.includes('MutationObserver'),
 'no interval polling':!workspace.includes('setInterval(')
};
for(const [n,ok] of Object.entries(checks)){console.log((ok?'PASS':'FAIL')+' - '+n);if(!ok)process.exit(1)}
