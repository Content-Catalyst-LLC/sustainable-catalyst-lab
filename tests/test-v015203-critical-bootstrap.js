const fs=require('fs');
const plugin=fs.readFileSync('includes/class-sc-lab-plugin.php','utf8');
const app=fs.readFileSync('assets/js/sc-lab-app.js','utf8');
if(!plugin.includes("$critical_modules = array('core','projects','workspace','feeds','project-workspace-v0280');")) process.exit(1);
if(!app.includes('function workspaceApi()')) process.exit(2);
if(!app.includes("workspaceApi().traceCounts(projects.get())")) process.exit(3);
if(!app.includes('workspaceApi().projectTotal(project)')) process.exit(4);
if(!app.includes("if (!Lab.Feeds || typeof Lab.Feeds.load !== 'function')")) process.exit(5);
console.log('PASS - v0.152.0.3 JS bootstrap guard');
