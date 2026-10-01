'use strict';
const fs=require('fs'),path=require('path');const root=path.resolve(__dirname,'..');
const js=fs.readFileSync(path.join(root,'assets/js/sc-lab-research-program-portfolio-v01610.js'),'utf8');
const required=['0.161.0','Research Program &amp; Portfolio Orchestration','data-v01610-workspace','data-v01610-program-create','data-v01610-add-project','data-v01610-objective','data-v01610-milestone','data-v01610-program-transition','data-v01610-portfolio-create','data-v01610-add-program','data-v01610-portfolio-transition','humanAuthorization:true','automatic prioritization'];
for(const needle of required){if(!js.includes(needle)){throw new Error('Missing v0.161.0 frontend contract: '+needle)}}
if(/credentials\s*:\s*['"]omit['"]/.test(js))throw new Error('v0.161.0 must preserve same-origin WordPress credentials');
console.log('PASS - v0.161.0 frontend static contract');
