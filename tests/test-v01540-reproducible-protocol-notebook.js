const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const safe=fs.readFileSync(path.join(root,'assets/js/sc-lab-safe-bootstrap-v01540.js'),'utf8');
const linked=fs.readFileSync(path.join(root,'assets/js/sc-lab-linked-scientific-views-v01540.js'),'utf8');
const persistence=fs.readFileSync(path.join(root,'assets/js/sc-lab-scene-persistence-provenance-handoff-v01540.js'),'utf8');
const workspace=fs.readFileSync(path.join(root,'assets/js/sc-lab-4d-computational-research-workspace-v01540.js'),'utf8');
const notebook=fs.readFileSync(path.join(root,'assets/js/sc-lab-reproducible-protocol-notebook-v01540.js'),'utf8');
const checks={
 'safe release':safe.includes("const VERSION = '0.154.0'"),
 'safe authority':safe.includes("labPresentationAuthority = 'v01540'"),
 'linked release':linked.includes("const VERSION = '0.154.0'"),
 'explicit grid palette retained':linked.includes("grid:'#d9e2ea'"),
 'explicit accent palette retained':linked.includes("accent:'#ff3842'"),
 'no document root color dependency':!linked.includes('getComputedStyle(d.documentElement).color'),
 'scene storage migration retained':persistence.includes("'sc-lab-v015212-scenes'"),
 'workspace release':workspace.includes("const VERSION='0.154.0'") || workspace.includes("const VERSION = '0.154.0'"),
 'restore without compute retained':workspace.includes('restored without rerunning computation'),
 'notebook release':notebook.includes("const VERSION='0.154.0'"),
 'explicit registered compute cell execution':notebook.includes('Running registered Compute Core method'),
 'compute call uses governed endpoint':notebook.includes('computeRunUrl'),
 'manifest verification':notebook.includes('Build') || notebook.includes('reproduction manifest'),
 'no eval':!notebook.includes('eval('),
 'no Function constructor':!notebook.includes('new Function('),
 'no mutation observer':!notebook.includes('MutationObserver'),
 'no interval polling':!notebook.includes('setInterval('),
 'arbitrary code claim false':notebook.includes('arbitraryCodeExecution:false')
};
for(const [n,ok] of Object.entries(checks)){console.log((ok?'PASS':'FAIL')+' - '+n);if(!ok)process.exit(1)}
