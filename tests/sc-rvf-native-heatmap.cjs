'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{execFileSync}=require('node:child_process');
const {JSDOM}=require(process.env.SC_RVF_JSDOM||'./renderer/node_modules/jsdom');
const root=path.resolve(__dirname,'..');
function figure(){return JSON.parse(execFileSync(process.env.SC_RVF_PYTHON||'python3',['-c',"import json; from pathlib import Path; from app.publisher_soil_carbon import ingest_pdf; print(json.dumps(ingest_pdf(Path('backend/app/publisher_sources/epa-report-136.pdf').read_bytes())))"],{cwd:root,env:{...process.env,PYTHONPATH:'backend'},encoding:'utf8'}));}
function render(spec){const dom=new JSDOM('<div id="plot"></div>',{runScripts:'outside-only'});dom.window.eval(fs.readFileSync(path.join(root,'assets/js/modules/scientific-visualization-engine-v0440.js'),'utf8'));const result=dom.window.SCLab.ScientificVisualizationEngineV0440.render(dom.window.document.getElementById('plot'),spec,{width:960,height:620});return{dom,result};}
test('native Lab renderer preserves categories, SE, source and cumulative-depth warning',()=>{
 const {dom,result}=render(figure());
 assert.equal(result.svg.querySelectorAll('.sc-sve0440-heat').length,8);
 const ticks=[...result.svg.querySelectorAll('.sc-sve0440-tick')].map(x=>x.textContent);
 assert.deepEqual(ticks,['0-10','0-30','0-50','0-100','Grassland + rough grazing','Arable lands']);
 assert.match(result.svg.textContent,/213.8 ± 4.5 SE/);assert.match(result.svg.textContent,/Cumulative depths overlap/);
 assert.equal(JSON.parse(result.svg.querySelector('metadata').textContent).scientificContext.source.table,'2.4');
 const table=dom.window.document.querySelector('table');assert.match(table.textContent,/Grassland \+ rough grazing/);assert.match(table.textContent,/SE/);
 dom.window.close();
});
test('native heatmap cell supports keyboard inspection and disables ordinal zoom',()=>{
 const {dom,result}=render(figure()),cell=result.svg.querySelector('.sc-sve0440-heat');
 assert.equal(cell.getAttribute('tabindex'),'0');cell.dispatchEvent(new dom.window.Event('focus'));
 const tooltip=dom.window.document.querySelector('.sc-sve0440-tooltip');assert.equal(tooltip.hidden,false);assert.match(tooltip.textContent,/52.2 ± 0.6 SE/);
 const before=result.getViewDomain();result.zoomIn();assert.deepEqual(result.getViewDomain(),before);
 dom.window.close();
});
test('ordinary numeric heatmaps retain numeric ticks and no scientific metadata',()=>{
 const {dom,result}=render({kind:'heatmap',title:'Synthetic numeric grid',xValues:[0,1],yValues:[0,1],cells:[{x:0,y:0,z:1,xIndex:0,yIndex:0},{x:1,y:1,z:2,xIndex:1,yIndex:1}],domain:{x:[-.5,1.5],y:[-.5,1.5],z:[1,2]}});
 assert.equal(result.svg.querySelector('metadata'),null);assert.ok(result.svg.querySelectorAll('.sc-sve0440-tick').length>4);dom.window.close();
});
