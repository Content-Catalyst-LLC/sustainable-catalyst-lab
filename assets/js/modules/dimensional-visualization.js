(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const VERSION = '0.9.4';
  const PREF_KEY = 'scLabDimensionalPrefsV092';

  const defaultTheme = {
    bg:'#ffffff', panel:'#f4f6f7', text:'#111820', muted:'#5f6a73', grid:'#d8dde1', axis:'#202a31',
    colors:['#d00000','#1f5c78','#5a6d2a','#805a82','#b36b16','#27746a']
  };

  function finite(value, fallback = 0) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
  }
  function deg(value) { return finite(value) * Math.PI / 180; }
  function esc(value) { return U?.esc ? U.esc(value) : String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c])); }
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function uid(prefix) { return U?.uid ? U.uid(prefix) : `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2,8)}`; }

  function rotatePlane(point, a, b, angleDegrees) {
    const p = point.slice();
    const angle = deg(angleDegrees);
    const c = Math.cos(angle), s = Math.sin(angle);
    const va = finite(p[a]), vb = finite(p[b]);
    p[a] = va * c - vb * s;
    p[b] = va * s + vb * c;
    return p;
  }

  function rotate4(point, angles = {}) {
    let p = [finite(point[0]), finite(point[1]), finite(point[2]), finite(point[3])];
    [['xy',0,1],['xz',0,2],['xw',0,3],['yz',1,2],['yw',1,3],['zw',2,3]].forEach(([key,a,b]) => { p = rotatePlane(p,a,b,angles[key] || 0); });
    return p;
  }

  function rotate3(point, angles = {}) {
    let p = [finite(point[0]), finite(point[1]), finite(point[2])];
    p = rotatePlane(p,1,2,angles.x || 0);
    p = rotatePlane(p,0,2,angles.y || 0);
    p = rotatePlane(p,0,1,angles.z || 0);
    return p;
  }

  function project4To3(point, distance = 4) {
    const d = Math.max(1.25, finite(distance,4));
    const denom = Math.max(0.12, d - finite(point[3]));
    const scale = d / denom;
    return [finite(point[0]) * scale, finite(point[1]) * scale, finite(point[2]) * scale];
  }

  function project3To2(point, distance = 6) {
    const d = Math.max(2, finite(distance,6));
    const denom = Math.max(0.18, d - finite(point[2]));
    const scale = d / denom;
    return [finite(point[0]) * scale, finite(point[1]) * scale, finite(point[2]), scale];
  }

  function differsByOneCoordinate(a,b) {
    let changes = 0;
    for (let i=0;i<a.length;i++) if (a[i] !== b[i]) changes++;
    return changes === 1;
  }

  function cube3d() {
    const vertices=[];
    [-1,1].forEach(x=>[-1,1].forEach(y=>[-1,1].forEach(z=>vertices.push([x,y,z]))));
    const edges=[];
    for(let i=0;i<vertices.length;i++) for(let j=i+1;j<vertices.length;j++) if(differsByOneCoordinate(vertices[i],vertices[j])) edges.push([i,j]);
    return {schema:'sc-lab-scene/1.0',id:'cube-3d',title:'Three-dimensional cube',dimensions:3,semanticType:'reference-geometry',vertices,edges,faces:[],metadata:{reference:true,description:'Reference 3D cube.'}};
  }

  function tesseract4d() {
    const vertices=[];
    [-1,1].forEach(x=>[-1,1].forEach(y=>[-1,1].forEach(z=>[-1,1].forEach(wv=>vertices.push([x,y,z,wv])))));
    const edges=[];
    for(let i=0;i<vertices.length;i++) for(let j=i+1;j<vertices.length;j++) if(differsByOneCoordinate(vertices[i],vertices[j])) edges.push([i,j]);
    return {schema:'sc-lab-scene/1.0',id:'tesseract-4d',title:'Four-dimensional tesseract projection',dimensions:4,semanticType:'reference-polytope',vertices,edges,faces:[],cells:[],metadata:{reference:true,polytope:'tesseract',schlafliSymbol:'{4,3,3}',description:'True four-coordinate vertices projected from 4D to 3D and then to 2D.'}};
  }

  function simplex4d() {
    const s = Math.sqrt(5);
    const vertices=[[1,1,1,-1/s],[1,-1,-1,-1/s],[-1,1,-1,-1/s],[-1,-1,1,-1/s],[0,0,0,4/s]];
    const edges=[];
    for(let i=0;i<vertices.length;i++) for(let j=i+1;j<vertices.length;j++) edges.push([i,j]);
    return {schema:'sc-lab-scene/1.0',id:'simplex-4d',title:'Four-dimensional simplex projection',dimensions:4,semanticType:'reference-polytope',vertices,edges,faces:[],cells:[],metadata:{reference:true,polytope:'5-cell',schlafliSymbol:'{3,3,3}',description:'Regular 4-simplex represented by five four-coordinate vertices.'}};
  }

  function crossPolytope4d() {
    const vertices=[];
    for(let axis=0;axis<4;axis++) for(const sign of [-1,1]) { const p=[0,0,0,0]; p[axis]=sign; vertices.push(p); }
    const edges=[];
    for(let i=0;i<vertices.length;i++) for(let j=i+1;j<vertices.length;j++) {
      const dot=vertices[i].reduce((sum,v,k)=>sum+v*vertices[j][k],0);
      if(dot > -0.999 && dot < 0.999) edges.push([i,j]);
    }
    return {schema:'sc-lab-scene/1.0',id:'cross-polytope-4d',title:'Four-dimensional 16-cell projection',dimensions:4,semanticType:'reference-polytope',vertices,edges,faces:[],cells:[],metadata:{reference:true,polytope:'16-cell',schlafliSymbol:'{3,3,4}',description:'Four-dimensional cross polytope with eight vertices and twenty-four edges.'}};
  }

  const presets = {
    cube3d,
    tesseract4d,
    simplex4d,
    crossPolytope4d
  };

  function normalizeColumns(rows, keys) {
    const ranges = keys.map(key => {
      const values = rows.map(row => finite(row[key],NaN)).filter(Number.isFinite);
      const min = Math.min(...values), max = Math.max(...values);
      return {min:Number.isFinite(min)?min:0,max:Number.isFinite(max)?max:1};
    });
    return rows.map(row => keys.map((key,i) => {
      const {min,max}=ranges[i]; const value=finite(row[key]);
      return min===max ? 0 : ((value-min)/(max-min))*2-1;
    }));
  }

  function findPointArray(value, dimensions, path = '', depth = 0) {
    if (!value || depth > 5) return null;
    if (Array.isArray(value) && value.length >= 2 && value.every(item => item && typeof item === 'object' && !Array.isArray(item))) {
      const keys=[...new Set(value.flatMap(item=>Object.keys(item)))];
      const numeric=keys.filter(key=>value.filter(item=>Number.isFinite(Number(item[key]))).length>=Math.max(2,Math.ceil(value.length*.65)));
      if(numeric.length>=dimensions) return {rows:value,keys:numeric.slice(0,dimensions),path};
    }
    if (typeof value === 'object') {
      const preferred=['series','points','trajectory','curve','profile','samples','data','rows','vertices'];
      for(const key of preferred) if(key in value){const result=findPointArray(value[key],dimensions,path?`${path}.${key}`:key,depth+1);if(result)return result;}
      for(const [key,val] of Object.entries(value)){const result=findPointArray(val,dimensions,path?`${path}.${key}`:key,depth+1);if(result)return result;}
    }
    return null;
  }

  function numericLeaves(value, prefix='', depth=0, out=[]) {
    if(value===null||value===undefined||depth>4||out.length>=24)return out;
    if(Array.isArray(value))return out;
    if(typeof value==='object'){
      Object.entries(value).forEach(([key,val])=>{
        if(key.startsWith('_')||['validation','series','points','trajectory','curve','history'].includes(key))return;
        numericLeaves(val,prefix?`${prefix}.${key}`:key,depth+1,out);
      });
    } else if(Number.isFinite(Number(value))) out.push({label:prefix||`value${out.length+1}`,value:Number(value)});
    return out;
  }

  function derivedGlyph(contract, dimensions=4) {
    const leaves=[...numericLeaves(contract?.outputs||{}),...numericLeaves(contract?.inputs||{},'input')].slice(0,18);
    if(!leaves.length)return null;
    const maxAbs=Math.max(...leaves.map(item=>Math.abs(item.value)),1);
    const maxLog=Math.log10(maxAbs+1)||1;
    const total=leaves.reduce((sum,item)=>sum+Math.abs(item.value),0)||1;
    let cumulative=0;
    const vertices=leaves.map((item,index)=>{
      cumulative+=Math.abs(item.value);
      const x=leaves.length===1?0:(index/(leaves.length-1))*2-1;
      const y=item.value/maxAbs;
      const z=Math.sign(item.value||1)*(Math.log10(Math.abs(item.value)+1)/maxLog);
      const wv=(cumulative/total)*2-1;
      return dimensions===3?[x,y,z]:[x,y,z,wv];
    });
    const edges=vertices.slice(1).map((_,i)=>[i,i+1]);
    return {schema:'sc-lab-scene/1.0',id:uid('derived-scene'),title:`${contract?.title||'Analysis'} — derived ${dimensions}D result space`,dimensions,semanticType:'derived-result-space',vertices,edges,labels:leaves.map(item=>item.label),metadata:{derived:true,warning:'This is a normalized result-space glyph, not a physical geometry or causal model.',sourceMethodId:contract?.methodId||'',fieldMapping:{x:'result index',y:'signed normalized value',z:'signed logarithmic magnitude',w:'cumulative absolute contribution'},inputFingerprint:contract?.audit?.inputFingerprint||'',outputFingerprint:contract?.audit?.outputFingerprint||''}};
  }

  function sceneFromContract(contract, dimensions=4) {
    const found=findPointArray(contract?.outputs||{},dimensions);
    if(found){
      const vertices=normalizeColumns(found.rows,found.keys);
      const edges=vertices.slice(1).map((_,i)=>[i,i+1]);
      return {schema:'sc-lab-scene/1.0',id:uid('analysis-scene'),title:`${contract.title} — ${dimensions}D data view`,dimensions,semanticType:'analysis-data',vertices,edges,labels:found.rows.map((_,i)=>String(i+1)),metadata:{derived:false,sourceMethodId:contract.methodId,sourcePath:found.path,fieldMapping:Object.fromEntries(['x','y','z','w'].slice(0,dimensions).map((axis,i)=>[axis,found.keys[i]])),normalization:'Each selected field independently scaled to [-1, 1].',inputFingerprint:contract.audit?.inputFingerprint||'',outputFingerprint:contract.audit?.outputFingerprint||''}};
    }
    return derivedGlyph(contract,dimensions);
  }

  function normalizeScene(raw) {
    if(!raw||typeof raw!=='object')throw new Error('Scene must be a JSON object.');
    const dimensions=Number(raw.dimensions);
    if(![3,4].includes(dimensions))throw new Error('Scene dimensions must be 3 or 4.');
    if(!Array.isArray(raw.vertices)||raw.vertices.length<1)throw new Error('Scene must include at least one vertex.');
    const vertices=raw.vertices.map((vertex,index)=>{
      if(!Array.isArray(vertex)||vertex.length<dimensions)throw new Error(`Vertex ${index+1} does not contain ${dimensions} coordinates.`);
      const point=vertex.slice(0,dimensions).map(Number);
      if(point.some(value=>!Number.isFinite(value)))throw new Error(`Vertex ${index+1} contains a non-numeric coordinate.`);
      return point;
    });
    const edges=(Array.isArray(raw.edges)?raw.edges:[]).map((edge,index)=>{
      if(!Array.isArray(edge)||edge.length<2)throw new Error(`Edge ${index+1} is invalid.`);
      const a=Number(edge[0]),b=Number(edge[1]);
      if(!Number.isInteger(a)||!Number.isInteger(b)||a<0||b<0||a>=vertices.length||b>=vertices.length)throw new Error(`Edge ${index+1} references an invalid vertex.`);
      return [a,b];
    });
    return Object.assign({schema:'sc-lab-scene/1.0',id:uid('scene'),title:'Dimensional scene',semanticType:'custom',labels:[],faces:[],cells:[],metadata:{}},clone(raw),{dimensions,vertices,edges});
  }

  function parseScene(text) { return normalizeScene(JSON.parse(String(text||''))); }

  function loadPrefs() {
    const fallback={preset:'tesseract4d',theme:'scientific',showVertices:true,showEdges:true,showLabels:false,rotation3:{x:18,y:-24,z:8},rotation4:{xy:0,xz:0,xw:22,yz:0,yw:-18,zw:14},distance3:6,distance4:4,scale:1};
    try{return Object.assign(fallback,JSON.parse(localStorage.getItem(PREF_KEY)||'{}'));}catch(_){return fallback;}
  }
  function savePrefs(value){localStorage.setItem(PREF_KEY,JSON.stringify(value));}

  function renderSVG(sceneInput, options={}) {
    const scene=normalizeScene(sceneInput);
    const prefs=Object.assign(loadPrefs(),options);
    const theme=(Lab.Visualization?.themes?.[prefs.theme])||defaultTheme;
    const W=960,H=620,plot={x:42,y:92,w:876,h:456};
    const r4=prefs.rotation4||{},r3=prefs.rotation3||{};
    const transformed=scene.vertices.map((vertex,index)=>{
      const p4=scene.dimensions===4?rotate4(vertex,r4):vertex.slice(0,3);
      const p3=scene.dimensions===4?project4To3(p4,prefs.distance4):p4;
      const rotated=rotate3(p3,r3);
      const p2=project3To2(rotated,prefs.distance3);
      return {index,raw:vertex,p3:rotated,x:p2[0],y:p2[1],z:p2[2],perspective:p2[3]};
    });
    const extent=Math.max(...transformed.flatMap(p=>[Math.abs(p.x),Math.abs(p.y)]),1);
    const scale=Math.min(plot.w,plot.h)/(extent*2.35)*finite(prefs.scale,1);
    transformed.forEach(p=>{p.sx=plot.x+plot.w/2+p.x*scale;p.sy=plot.y+plot.h/2-p.y*scale;});
    const edgeRows=scene.edges.map((edge,index)=>({edge,index,depth:(transformed[edge[0]].z+transformed[edge[1]].z)/2})).sort((a,b)=>a.depth-b.depth);
    const pointRows=transformed.slice().sort((a,b)=>a.z-b.z);
    const edgeSvg=prefs.showEdges===false?'':edgeRows.map(({edge,depth})=>{
      const a=transformed[edge[0]],b=transformed[edge[1]],opacity=.28+.52*((depth+extent)/(2*extent));
      return `<line x1="${a.sx.toFixed(2)}" y1="${a.sy.toFixed(2)}" x2="${b.sx.toFixed(2)}" y2="${b.sy.toFixed(2)}" stroke="${theme.colors[1]}" stroke-width="${Math.max(1.1,1.8*(a.perspective+b.perspective)/2).toFixed(2)}" opacity="${Math.max(.2,Math.min(.88,opacity)).toFixed(2)}"/>`;
    }).join('');
    const vertexSvg=prefs.showVertices===false?'':pointRows.map(point=>{
      const radius=Math.max(2.6,4.1*point.perspective);
      const color=scene.dimensions===4?(point.raw[3]>=0?theme.colors[0]:theme.colors[2]):theme.colors[0];
      const label=(scene.labels||[])[point.index]||String(point.index+1);
      return `<g><circle cx="${point.sx.toFixed(2)}" cy="${point.sy.toFixed(2)}" r="${radius.toFixed(2)}" fill="${color}" stroke="${theme.bg}" stroke-width="1.2"><title>${esc(label)} · ${esc(point.raw.join(', '))}</title></circle>${prefs.showLabels?`<text x="${(point.sx+7).toFixed(2)}" y="${(point.sy-7).toFixed(2)}" font-family="ui-monospace,monospace" font-size="9" fill="${theme.text}">${esc(label)}</text>`:''}</g>`;
    }).join('');
    const axis=[['x',theme.colors[0],[1,0,0]],['y',theme.colors[2],[0,1,0]],['z',theme.colors[1],[0,0,1]]].map(([label,color,v])=>{
      const p=project3To2(rotate3(v.map(n=>n*1.35),r3),prefs.distance3);
      const x=plot.x+plot.w/2+p[0]*scale,y=plot.y+plot.h/2-p[1]*scale;
      return `<line x1="${plot.x+plot.w/2}" y1="${plot.y+plot.h/2}" x2="${x}" y2="${y}" stroke="${color}" stroke-width="2"/><text x="${x+5}" y="${y-5}" font-family="ui-monospace,monospace" font-size="10" fill="${color}">${label}</text>`;
    }).join('');
    const mode=scene.dimensions===4?'4D → 3D → 2D projected view':'3D → 2D projected view';
    const warning=scene.metadata?.warning||scene.metadata?.description||'';
    return `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="dim-title dim-desc" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><title id="dim-title">${esc(scene.title)}</title><desc id="dim-desc">${esc(mode)}. ${esc(warning)}</desc><rect width="100%" height="100%" fill="${theme.bg}"/><text x="42" y="42" font-family="system-ui,sans-serif" font-size="25" font-weight="700" fill="${theme.text}">${esc(scene.title)}</text><text x="42" y="67" font-family="ui-monospace,monospace" font-size="11" fill="${theme.muted}">${esc(mode)} · ${scene.vertices.length} vertices · ${scene.edges.length} edges</text><rect x="${plot.x}" y="${plot.y}" width="${plot.w}" height="${plot.h}" fill="${theme.panel}" stroke="${theme.grid}"/>${axis}${edgeSvg}${vertexSvg}<text x="42" y="580" font-family="system-ui,sans-serif" font-size="11" fill="${theme.muted}">${esc(warning.slice(0,145))}</text><text x="918" y="600" text-anchor="end" font-family="ui-monospace,monospace" font-size="10" fill="${theme.muted}">Sustainable Catalyst Lab v${VERSION}</text></svg>`;
  }

  function scenePacket(scene,svg,contract) {
    return {sceneId:scene.id,title:scene.title,dimensions:scene.dimensions,semanticType:scene.semanticType,sceneSpec:scene,svg,projection:{fourToThree:scene.dimensions===4?'perspective':'not-applicable',threeToTwo:'perspective'},methodId:contract?.methodId||scene.metadata?.sourceMethodId||'visualization.dimensional',validationState:contract?.status||'unreviewed',audit:{applicationVersion:VERSION,sceneFingerprint:U?.fingerprint?U.fingerprint(scene):'',generatedAt:U?.now?U.now():new Date().toISOString()}};
  }

  function sceneContract(scene,svg,project,sourceContract) {
    return Lab.Visualization.makeContract({id:uid('dimensional-analysis'),methodId:sourceContract?.methodId||'visualization.dimensional',methodVersion:sourceContract?.methodVersion||VERSION,title:scene.title,subtitle:scene.metadata?.warning||scene.metadata?.description||'',domain:'dimensional-visualization',inputs:{rotation:loadPrefs()},outputs:{dimensions:scene.dimensions,vertices:scene.vertices.length,edges:scene.edges.length},assumptions:[scene.metadata?.warning||scene.metadata?.description||'Projected dimensional scene.'],project,sceneSpec:scene,svg});
  }

  function controls(root){return {
    preset:root.querySelector('[data-dim-preset]'),custom:root.querySelector('[data-dim-custom]'),status:root.querySelector('[data-dim-status]'),chart:root.querySelector('[data-dim-chart]'),meta:root.querySelector('[data-dim-meta]'),
    showVertices:root.querySelector('[data-dim-show-vertices]'),showEdges:root.querySelector('[data-dim-show-edges]'),showLabels:root.querySelector('[data-dim-show-labels]'),theme:root.querySelector('[data-dim-theme]'),
    distance3:root.querySelector('[data-dim-distance3]'),distance4:root.querySelector('[data-dim-distance4]'),scale:root.querySelector('[data-dim-scale]'),
    rotations:Object.fromEntries(['x','y','z','xy','xz','xw','yz','yw','zw'].map(key=>[key,root.querySelector(`[data-dim-rotation="${key}"]`)]))
  };}

  function prefsFromControls(el){return {preset:el.preset.value,theme:el.theme.value,showVertices:el.showVertices.checked,showEdges:el.showEdges.checked,showLabels:el.showLabels.checked,distance3:finite(el.distance3.value,6),distance4:finite(el.distance4.value,4),scale:finite(el.scale.value,1),rotation3:{x:finite(el.rotations.x.value),y:finite(el.rotations.y.value),z:finite(el.rotations.z.value)},rotation4:{xy:finite(el.rotations.xy.value),xz:finite(el.rotations.xz.value),xw:finite(el.rotations.xw.value),yz:finite(el.rotations.yz.value),yw:finite(el.rotations.yw.value),zw:finite(el.rotations.zw.value)}};}

  function applyPrefs(el,prefs){el.preset.value=prefs.preset||'tesseract4d';el.theme.value=prefs.theme||'scientific';el.showVertices.checked=prefs.showVertices!==false;el.showEdges.checked=prefs.showEdges!==false;el.showLabels.checked=!!prefs.showLabels;el.distance3.value=prefs.distance3||6;el.distance4.value=prefs.distance4||4;el.scale.value=prefs.scale||1;Object.entries(prefs.rotation3||{}).forEach(([k,v])=>{if(el.rotations[k])el.rotations[k].value=v;});Object.entries(prefs.rotation4||{}).forEach(([k,v])=>{if(el.rotations[k])el.rotations[k].value=v;});}

  function init(root,projects){
    const el=controls(root);if(!el.chart)return;
    Object.entries(Lab.Visualization?.themes||{scientific:{label:'Scientific Light'}}).forEach(([key,value])=>el.theme.add(new Option(value.label||key,key)));
    applyPrefs(el,loadPrefs());
    let scene=presets.tesseract4d(); let svg=''; let sourceContract=null; let animation=null;

    function selectScene(){
      const name=el.preset.value;
      if(name==='current4d')return sceneFromContract(sourceContract||root._scLabLatestResult,4)||tesseract4d();
      if(name==='current3d')return sceneFromContract(sourceContract||root._scLabLatestResult,3)||cube3d();
      if(name==='custom')return parseScene(el.custom.value);
      return presets[name]?presets[name]():tesseract4d();
    }
    function render(){
      try{const prefs=prefsFromControls(el);savePrefs(prefs);scene=selectScene();svg=renderSVG(scene,prefs);el.chart.innerHTML=svg;el.status.textContent=`${scene.dimensions}D scene · ${scene.vertices.length} vertices · ${scene.edges.length} edges · ${scene.semanticType}`;el.meta.textContent=JSON.stringify({sceneId:scene.id,dimensions:scene.dimensions,semanticType:scene.semanticType,metadata:scene.metadata,rotation3:prefs.rotation3,rotation4:prefs.rotation4,distance3:prefs.distance3,distance4:prefs.distance4},null,2);root._scLabLatestDimensional={scene,svg,contract:sourceContract};return true;}catch(error){el.status.textContent=error.message;return false;}
    }
    function stop(){if(animation){cancelAnimationFrame(animation);animation=null;root.querySelector('[data-dim-animate]').textContent='Animate';}}
    function animate(){if(animation){stop();return;}root.querySelector('[data-dim-animate]').textContent='Stop';const tick=()=>{el.rotations.y.value=(finite(el.rotations.y.value)+.45)%360;if(scene.dimensions===4)el.rotations.xw.value=(finite(el.rotations.xw.value)+.65)%360;render();animation=requestAnimationFrame(tick);};animation=requestAnimationFrame(tick);}

    root.querySelector('[data-dim-render]').addEventListener('click',render);
    root.querySelector('[data-dim-reset]').addEventListener('click',()=>{stop();applyPrefs(el,{preset:el.preset.value,theme:el.theme.value,showVertices:true,showEdges:true,showLabels:false,rotation3:{x:18,y:-24,z:8},rotation4:{xy:0,xz:0,xw:22,yz:0,yw:-18,zw:14},distance3:6,distance4:4,scale:1});render();});
    root.querySelector('[data-dim-animate]').addEventListener('click',animate);
    [...Object.values(el.rotations),el.distance3,el.distance4,el.scale,el.showVertices,el.showEdges,el.showLabels,el.theme,el.preset].forEach(control=>control?.addEventListener('input',()=>{stop();render();}));
    root.querySelector('[data-dim-load-analysis]').addEventListener('click',()=>{sourceContract=root._scLabLatestResult;if(!sourceContract){el.status.textContent='Run a calculation before loading current analysis data.';return;}el.preset.value='current4d';render();});
    root.querySelector('[data-dim-export-svg]').addEventListener('click',()=>{if(!svg)render();Lab.Visualization.exportSvg(sceneContract(scene,svg,projects.get(),sourceContract),svg,`${scene.id}.svg`);});
    root.querySelector('[data-dim-export-png]').addEventListener('click',()=>{if(!svg)render();Lab.Visualization.exportPng(sceneContract(scene,svg,projects.get(),sourceContract),svg,`${scene.id}.png`,3).catch(error=>U.toast(root,error.message));});
    root.querySelector('[data-dim-export-pdf]').addEventListener('click',()=>{if(!svg)render();Lab.Visualization.exportPdf(sceneContract(scene,svg,projects.get(),sourceContract),svg,`${scene.id}.pdf`).catch(error=>U.toast(root,error.message));});
    root.querySelector('[data-dim-export-json]').addEventListener('click',()=>U.download(`${scene.id}.scene.json`,JSON.stringify(scene,null,2),'application/json'));
    root.querySelector('[data-dim-export-package]').addEventListener('click',()=>{if(!svg)render();const contract=sceneContract(scene,svg,projects.get(),sourceContract);Lab.Visualization.exportPackage(contract,svg,`${scene.id}-analysis-package.zip`).catch(error=>U.toast(root,error.message));});
    root.querySelector('[data-dim-save]').addEventListener('click',()=>{if(!svg)render();const contract=sceneContract(scene,svg,projects.get(),sourceContract);projects.add('dimensionalScenes',{type:'dimensional-scene',title:scene.title,sceneSpec:scene,svg,contract},`Dimensional visualization saved: ${scene.title}`);U.toast(root,'Dimensional visualization saved to the active project.');});
    root.querySelector('[data-dim-handoff]').addEventListener('click',()=>{if(!svg)render();const contract=sceneContract(scene,svg,projects.get(),sourceContract);contract.sceneSpec=scene;Lab.Visualization.handoff(root,projects,contract,svg);});
    root.addEventListener('sc-lab:dimensional-contract',event=>{sourceContract=event.detail||root._scLabLatestResult;el.preset.value='current4d';render();});
    render();
  }

  Lab.DimensionalVisualization={VERSION,PREF_KEY,presets,rotatePlane,rotate4,rotate3,project4To3,project3To2,normalizeScene,parseScene,sceneFromContract,derivedGlyph,renderSVG,scenePacket,sceneContract,loadPrefs,savePrefs,init};
})(window);
