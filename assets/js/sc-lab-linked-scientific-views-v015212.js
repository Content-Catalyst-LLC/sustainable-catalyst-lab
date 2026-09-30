(function (w, d) {
  'use strict';

  const VERSION = '0.152.0.12';
  const RUNTIME = 'linked-scientific-views-v015212';
  const STORAGE_KEY = 'sc-lab-v015211-response-surface-configs';
  const HANDOFF_KEY = 'sc-lab-v015212-graph-studio-handoff';
  const roots = new WeakMap();

  const DEMOS = Object.freeze({
    response: { label: 'Nonlinear response surface', boundary: 'Illustrative browser-rendered response field.' },
    dynamic: { label: 'Dynamic system landscape', boundary: 'Illustrative dynamic-system surface; not an observed trajectory.' },
    uncertainty: { label: 'Uncertainty landscape', boundary: 'Illustrative uncertainty topology; not a confidence or credible interval.' },
    sensitivity: { label: 'Sensitivity surface', boundary: 'Illustrative sensitivity field; visual gradient is not causal evidence.' },
    ensemble: { label: 'Ensemble response field', boundary: 'Illustrative ensemble-like variation; not a calibrated forecast.' },
    spatiotemporal: { label: 'Spatiotemporal field', boundary: 'Illustrative spatial-temporal response; not geolocated observations.' },
    'compute-grid': { label: 'Compute-backed response surface', boundary: 'Uses registered Python Compute Core parameter sweeps over a bounded X/Y/W grid. Interpolation between computed grid points is a visualization operation.' }
  });

  const MODELS = Object.freeze({
    logistic_growth: {
      label: 'Logistic growth', output: 'population',
      params: [
        {id:'initial',label:'Initial population',min:1,max:40,def:10,step:1},
        {id:'rate',label:'Growth rate',min:0.05,max:1.0,def:0.5,step:0.01},
        {id:'carryingCapacity',label:'Carrying capacity',min:50,max:250,def:100,step:1},
        {id:'time',label:'Time',min:1,max:25,def:10,step:0.5}
      ], axes:{x:'rate',y:'initial',w:'time'}
    },
    projectile_range: {
      label: 'Projectile range', output: 'range',
      params: [
        {id:'speed',label:'Speed',min:5,max:80,def:20,step:1},
        {id:'angleDeg',label:'Launch angle (deg)',min:5,max:85,def:45,step:1},
        {id:'gravity',label:'Gravity',min:1.6,max:15,def:9.80665,step:0.1}
      ], axes:{x:'speed',y:'angleDeg',w:'gravity'}
    },
    photovoltaic_output: {
      label: 'Photovoltaic output', output: 'power',
      params: [
        {id:'irradiance',label:'Irradiance',min:100,max:1200,def:1000,step:10},
        {id:'area',label:'Area',min:1,max:50,def:10,step:1},
        {id:'efficiency',label:'Efficiency',min:0.05,max:0.35,def:0.2,step:0.01},
        {id:'systemFactor',label:'System factor',min:0.5,max:1,def:0.85,step:0.01}
      ], axes:{x:'irradiance',y:'area',w:'efficiency'}
    },
    michaelis_menten: {
      label: 'Michaelis–Menten kinetics', output: 'reaction rate',
      params: [
        {id:'vmax',label:'Vmax',min:1,max:30,def:10,step:0.5},
        {id:'substrate',label:'Substrate',min:0,max:30,def:5,step:0.5},
        {id:'km',label:'Km',min:0.1,max:15,def:2,step:0.1}
      ], axes:{x:'substrate',y:'vmax',w:'km'}
    }
  });

  function all(root, selector) { return root && root.querySelectorAll ? Array.from(root.querySelectorAll(selector)) : []; }
  function one(root, selector) { return root && root.querySelector ? root.querySelector(selector) : null; }
  function finite(v, fallback) { v=Number(v); return Number.isFinite(v)?v:fallback; }
  function clamp(v, lo, hi) { return Math.max(lo,Math.min(hi,finite(v,lo))); }
  function linspace(lo, hi, n) { n=Math.max(2,Math.floor(n)); const out=[]; for(let i=0;i<n;i++)out.push(lo+(hi-lo)*(i/(n-1))); return out; }
  function deepCopy(value) { return JSON.parse(JSON.stringify(value)); }
  function sameNumbers(a,b) { return Array.isArray(a)&&Array.isArray(b)&&a.length===b.length&&a.every((v,i)=>Math.abs(v-b[i])<1e-9); }
  function format(v) { if(!Number.isFinite(Number(v)))return '—'; const n=Number(v); return Math.abs(n)>=1000?n.toPrecision(5):Number(n.toFixed(5)).toString(); }

  function config() {
    const c=w.SCLabLinkedViewsV015212||{};
    return {
      healthUrl:c.computeHealthUrl||'/wp-json/sc-lab/v1/compute/core/health',
      capabilitiesUrl:c.computeCapabilitiesUrl||'/wp-json/sc-lab/v1/compute/core/capabilities',
      runUrl:c.computeRunUrl||'/wp-json/sc-lab/v1/compute/core/run',
      nonce:c.nonce||'', maxXSamples:Number(c.maxXSamples)||41, maxYLevels:Number(c.maxYLevels)||7,
      maxWSlices:Number(c.maxWSlices)||5, maxParallelRequests:Number(c.maxParallelRequests)||3,
      maxMonteCarloSamples:Number(c.maxMonteCarloSamples)||50000, maxEnsembleMembers:Number(c.maxEnsembleMembers)||7,
      selectionHistoryLimit:Number(c.selectionHistoryLimit)||12, pinLimit:Number(c.pinLimit)||8, graphStudioModule:c.graphStudioModule||'graph-studio'
    };
  }

  function state(root) {
    if(roots.has(root))return roots.get(root);
    const s={demo:'response',w:.37,xw:.34,yw:-.22,zw:.12,vector:true,uncertainty:true,contours:true,tesseract:true,playing:false,raf:0,last:0,
      model:'logistic_growth',axes:{x:'rate',y:'initial',w:'time'},zMode:'output',fixed:{},surface:null,baseline:null,
      compute:{status:'unknown',version:null,methods:null,benchmarks:null},analysis:{mode:null,result:null,ensemble:null,sensitivity:null},
      linked:{enabled:true,current:null,history:[],pins:[],analysisPlot:null},resize:null};
    roots.set(root,s); return s;
  }

  function profile(s){return MODELS[s.model]||MODELS.logistic_growth;}
  function param(profile,id){return profile.params.find(p=>p.id===id)||profile.params[0];}
  function defaultFixed(p){const out={};p.params.forEach(x=>out[x.id]=x.def);return out;}
  function normalizedToActual(values,n){if(!values||!values.length)return n;const t=clamp((n+1)/2,0,1)*(values.length-1),a=Math.floor(t),b=Math.min(values.length-1,a+1),f=t-a;return values[a]+(values[b]-values[a])*f;}

  function configFromUi(root) {
    const s=state(root), p=profile(s);
    const axes={x:one(root,'[data-v015209-axis="x"]')?.value||p.axes.x,y:one(root,'[data-v015209-axis="y"]')?.value||p.axes.y,w:one(root,'[data-v015209-axis="w"]')?.value||p.axes.w};
    const range={}; ['x','y','w'].forEach(k=>{range[k]={min:finite(one(root,'[data-v015209-range="'+k+'-min"]')?.value,param(p,axes[k]).min),max:finite(one(root,'[data-v015209-range="'+k+'-max"]')?.value,param(p,axes[k]).max)};});
    const resolution={x:Math.min(config().maxXSamples,Math.max(11,finite(one(root,'[data-v015209-resolution="x"]')?.value,21))),y:Math.min(config().maxYLevels,Math.max(3,finite(one(root,'[data-v015209-resolution="y"]')?.value,5))),w:Math.min(config().maxWSlices,Math.max(3,finite(one(root,'[data-v015209-resolution="w"]')?.value,3)))};
    const fixed={}; all(root,'[data-v015209-fixed-param]').forEach(input=>fixed[input.dataset.v015209FixedParam]=finite(input.value,0));
    return {schema:'sc-lab-response-surface-config/1.0',model:s.model,axes:axes,zMode:one(root,'[data-v015209-z-mode]')?.value||'output',range:range,resolution:resolution,fixed:fixed};
  }

  function validateConfig(c) {
    if(!MODELS[c.model])throw new Error('Unknown model family.');
    if(new Set([c.axes.x,c.axes.y,c.axes.w]).size!==3)throw new Error('X, Y and W parameters must be different.');
    for(const k of ['x','y','w'])if(!(c.range[k].max>c.range[k].min))throw new Error(k.toUpperCase()+' maximum must be greater than minimum.');
    const requests=c.resolution.y*c.resolution.w, evaluations=c.resolution.x*requests;
    if(requests>35||evaluations>1435)throw new Error('Requested grid exceeds the bounded execution budget.');
    return {requests:requests,evaluations:evaluations};
  }

  function updateBudget(root) { try{const c=configFromUi(root),b=validateConfig(c),n=one(root,'[data-v015209-budget]');if(n)n.textContent=b.evaluations+' evaluations · '+b.requests+' bounded requests';}catch(e){const n=one(root,'[data-v015209-budget]');if(n)n.textContent=e.message;} }

  function populateModel(root, modelId, preserved) {
    const s=state(root), p=MODELS[modelId]||MODELS.logistic_growth; s.model=modelId in MODELS?modelId:'logistic_growth'; s.axes=Object.assign({},p.axes); s.fixed=defaultFixed(p);
    const model=one(root,'[data-v015209-model]'); if(model){model.innerHTML='';Object.entries(MODELS).forEach(([id,m])=>{const o=d.createElement('option');o.value=id;o.textContent=m.label;model.appendChild(o);});model.value=s.model;}
    for(const k of ['x','y','w']){const sel=one(root,'[data-v015209-axis="'+k+'"]');if(!sel)continue;sel.innerHTML='';p.params.forEach(pp=>{const o=d.createElement('option');o.value=pp.id;o.textContent=pp.label;sel.appendChild(o);});sel.value=(preserved&&preserved.axes&&p.params.some(x=>x.id===preserved.axes[k]))?preserved.axes[k]:p.axes[k];s.axes[k]=sel.value;}
    syncRanges(root,preserved); renderFixedControls(root,preserved); updateBudget(root);
  }

  function syncRanges(root,preserved) {
    const s=state(root),p=profile(s); for(const k of ['x','y','w']){const sel=one(root,'[data-v015209-axis="'+k+'"]'),id=sel?sel.value:s.axes[k],pp=param(p,id);s.axes[k]=id;const saved=preserved&&preserved.range&&preserved.range[k];const mn=one(root,'[data-v015209-range="'+k+'-min"]'),mx=one(root,'[data-v015209-range="'+k+'-max"]');if(mn){mn.value=String(saved?finite(saved.min,pp.min):pp.min);mn.step=String(pp.step||'any');}if(mx){mx.value=String(saved?finite(saved.max,pp.max):pp.max);mx.step=String(pp.step||'any');}}
    if(preserved&&preserved.resolution)for(const k of ['x','y','w']){const n=one(root,'[data-v015209-resolution="'+k+'"]');if(n&&preserved.resolution[k])n.value=String(preserved.resolution[k]);}
    const z=one(root,'[data-v015209-z-mode]'); if(z&&preserved&&preserved.zMode)z.value=preserved.zMode;
  }

  function renderFixedControls(root,preserved) {
    const s=state(root),p=profile(s),host=one(root,'[data-v015209-fixed-controls]');if(!host)return;host.innerHTML='';const used=new Set([one(root,'[data-v015209-axis="x"]')?.value,one(root,'[data-v015209-axis="y"]')?.value,one(root,'[data-v015209-axis="w"]')?.value]);p.params.filter(pp=>!used.has(pp.id)).forEach(pp=>{const label=d.createElement('label');label.innerHTML='<span></span><input type="number" step="'+pp.step+'" data-v015209-fixed-param="'+pp.id+'">';label.querySelector('span').textContent=pp.label;const input=label.querySelector('input');input.value=String(preserved&&preserved.fixed&&Number.isFinite(Number(preserved.fixed[pp.id]))?preserved.fixed[pp.id]:pp.def);host.appendChild(label);});
  }

  async function getJson(url,opts){const cfg=config(),options=Object.assign({headers:{}},opts||{});options.headers=Object.assign({},options.headers,{'Accept':'application/json'});if(cfg.nonce)options.headers['X-WP-Nonce']=cfg.nonce;const response=await fetch(url,options);let body=null;try{body=await response.json();}catch(_){body=null;}if(!response.ok)throw new Error(body&&body.message?body.message:'HTTP '+response.status);return body||{};}
  function computeLabel(root,text,tone){const n=one(root,'[data-v0710-compute-state]');if(n){n.textContent=text;n.dataset.state=tone||'unknown';}}
  async function refreshCompute(root){const s=state(root),cfg=config();computeLabel(root,'Checking compute','checking');try{const [h,c]=await Promise.all([getJson(cfg.healthUrl),getJson(cfg.capabilitiesUrl)]);s.compute.status=h.ok?'ready':'degraded';s.compute.version=h.version||c.version||null;s.compute.methods=h.methodCount||c.methodCount||null;s.compute.benchmarks=h.benchmarkCount||null;computeLabel(root,h.ok?'Compute ready · '+(s.compute.methods||'?')+' methods':'Compute '+(h.status||'degraded'),h.ok?'ready':'warning');const details=one(root,'[data-v015209-compute-details]');if(details)details.textContent='Python Core '+(s.compute.version||'—')+' · '+(s.compute.methods||'?')+' registered methods · '+(s.compute.benchmarks||'?')+' benchmarks';return h;}catch(error){s.compute.status='offline';computeLabel(root,'Compute unavailable','error');const details=one(root,'[data-v015209-compute-details]');if(details)details.textContent=String(error.message||error);return null;}}

  async function computeTask(cfg,task,xValues){const fixed=Object.assign({},cfg.fixed);fixed[cfg.axes.y]=task.y;fixed[cfg.axes.w]=task.w;const body=await getJson(config().runUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method:'simulation.parameter_sweep',inputs:{model:cfg.model,parameter:cfg.axes.x,values:xValues,fixed:fixed},requested_outputs:['summary','values']})});const output=body.output||body.result||body.outputs||body,rows=Array.isArray(output.rows)?output.rows:(Array.isArray(body.rows)?body.rows:[]);if(rows.length!==xValues.length)throw new Error('Compute Core returned '+rows.length+' rows; expected '+xValues.length+'.');return rows.map(r=>finite(r.output,NaN));}

  async function runSurface(root) {
    const s=state(root),button=one(root,'[data-v015209-run-surface]');let cfg,budget;try{cfg=configFromUi(root);budget=validateConfig(cfg);}catch(error){computeLabel(root,'Configuration invalid','error');one(root,'[data-v015209-run-meta]').textContent=error.message;return;}
    if(s.compute.status!=='ready')await refreshCompute(root);
    if(button){button.disabled=true;button.textContent='Computing surface…';}computeLabel(root,'Running bounded response surface','checking');
    const started=performance.now(),startedAt=new Date().toISOString(),xValues=linspace(cfg.range.x.min,cfg.range.x.max,cfg.resolution.x),yValues=linspace(cfg.range.y.min,cfg.range.y.max,cfg.resolution.y),wValues=linspace(cfg.range.w.min,cfg.range.w.max,cfg.resolution.w);
    const tasks=[];wValues.forEach((wv,wi)=>yValues.forEach((yv,yi)=>tasks.push({wi:wi,yi:yi,w:wv,y:yv})));const grid=Array.from({length:wValues.length},()=>Array.from({length:yValues.length},()=>null));let done=0,idx=0;const progress=one(root,'[data-v015209-progress]'),bar=one(root,'[data-v015209-progress-bar]');if(progress)progress.hidden=false;
    async function worker(){while(true){const i=idx++;if(i>=tasks.length)return;const task=tasks[i];grid[task.wi][task.yi]=await computeTask(cfg,task,xValues);done++;if(bar)bar.style.width=((done/tasks.length)*100).toFixed(1)+'%';const meta=one(root,'[data-v015209-run-meta]');if(meta)meta.textContent='Computing '+done+' / '+tasks.length+' bounded sweeps…';}}
    try{
      const workers=[];for(let i=0;i<Math.min(config().maxParallelRequests,tasks.length);i++)workers.push(worker());await Promise.all(workers);
      const flat=grid.flat(2).filter(Number.isFinite);if(!flat.length)throw new Error('Response surface returned no finite output values.');
      const elapsed=Math.max(0,performance.now()-started);s.surface={schema:'sc-lab-response-surface-result/1.0',releaseVersion:VERSION,config:deepCopy(cfg),xValues:xValues,yValues:yValues,wValues:wValues,grid:grid,min:Math.min.apply(null,flat),max:Math.max.apply(null,flat),runMetadata:{startedAt:startedAt,elapsedMs:Math.round(elapsed),requestCount:budget.requests,evaluationCount:budget.evaluations,computeMethod:'simulation.parameter_sweep',model:cfg.model}};s.demo='compute-grid';s.zMode=cfg.zMode;const demo=one(root,'[data-v015209-demo]');if(demo)demo.value='compute-grid';const wm=one(root,'[data-v015209-w-value]');if(wm)wm.textContent=param(profile(s),cfg.axes.w).label+' '+format(normalizedToActual(wValues,s.w));computeLabel(root,'Compute-backed surface ready','ready');updateRunMeta(root);schedule(root);
    }catch(error){computeLabel(root,'Response surface failed','error');const meta=one(root,'[data-v015209-run-meta]');if(meta)meta.textContent=String(error.message||error);}
    finally{if(button){button.disabled=false;button.textContent='Run response surface';}if(progress)progress.hidden=true;if(bar)bar.style.width='0%';}
  }

  function baselineCompatible(s){if(!s.surface||!s.baseline)return false;const a=s.surface,b=s.baseline;return a.config.model===b.config.model&&a.config.axes.x===b.config.axes.x&&a.config.axes.y===b.config.axes.y&&a.config.axes.w===b.config.axes.w&&sameNumbers(a.xValues,b.xValues)&&sameNumbers(a.yValues,b.yValues)&&sameNumbers(a.wValues,b.wValues);}
  function interp1(values,t){if(values.length===1)return [0,0,0];const x=clamp(t,0,1)*(values.length-1),a=Math.floor(x),b=Math.min(values.length-1,a+1);return[a,b,x-a];}
  function sampleGrid(surface,xn,yn,wn){if(!surface)return NaN;const [xa,xb,xf]=interp1(surface.xValues,xn),[ya,yb,yf]=interp1(surface.yValues,yn),[wa,wb,wf]=interp1(surface.wValues,wn);const val=(wi,yi,xi)=>finite(surface.grid?.[wi]?.[yi]?.[xi],NaN);function bil(wi){const q00=val(wi,ya,xa),q10=val(wi,ya,xb),q01=val(wi,yb,xa),q11=val(wi,yb,xb);if([q00,q10,q01,q11].some(v=>!Number.isFinite(v)))return NaN;const a=q00+(q10-q00)*xf,b=q01+(q11-q01)*xf;return a+(b-a)*yf;}const a=bil(wa),b=bil(wb);return Number.isFinite(a)&&Number.isFinite(b)?a+(b-a)*wf:NaN;}
  function rawResponse(s,x,y){if(!s.surface)return NaN;const xn=clamp((x+2.55)/5.1,0,1),yn=clamp((y+2.55)/5.1,0,1),wn=clamp((s.w+1)/2,0,1);return sampleGrid(s.surface,xn,yn,wn);}
  function mappedCompute(s,x,y){const v=rawResponse(s,x,y);if(!Number.isFinite(v))return 0;if(s.zMode==='delta'&&baselineCompatible(s)){const xn=clamp((x+2.55)/5.1,0,1),yn=clamp((y+2.55)/5.1,0,1),wn=clamp((s.w+1)/2,0,1),base=sampleGrid(s.baseline,xn,yn,wn),delta=v-base;const span=Math.max(1e-9,Math.max(Math.abs(s.surface.max-s.baseline.min),Math.abs(s.baseline.max-s.surface.min)));return clamp(delta/span,-1,1)*1.45;}const span=Math.max(1e-9,s.surface.max-s.surface.min),n=(v-s.surface.min)/span;return(n*2-1)*1.45;}
  function field(s,x,y){const wv=s.w;if(s.demo==='compute-grid'&&s.surface)return mappedCompute(s,x,y);if(s.demo==='dynamic')return 1.05*Math.sin(x*.9+wv*2.1)+.68*Math.cos(y*1.35-wv)+.16*x*y;if(s.demo==='uncertainty')return .75*Math.sin(x*1.3)*Math.cos(y*.85)+.55*Math.cos((x-y)*.55+wv*2.4);if(s.demo==='sensitivity')return .42*x*y+.82*Math.sin((x+wv)*1.1)-.48*Math.cos((y-wv)*1.55);if(s.demo==='ensemble')return .58*Math.sin(x*1.2+wv)+.48*Math.sin(y*1.7-wv*.7)+.31*Math.cos((x+y+wv)*2.2);if(s.demo==='spatiotemporal')return 1.2*Math.exp(-.11*(x*x+y*y))*Math.cos(2.1*Math.hypot(x,y)-wv*3.2)+.18*Math.sin(x-y);return Math.sin(x*1.25+wv*.9)*Math.cos(y*1.05-wv*.55)+.34*Math.sin((x+y)*.8+wv*1.8);}

  function project(s,x,y,z,wv,width,height){let c=Math.cos(s.xw),q=Math.sin(s.xw),x1=x*c-wv*q,w1=x*q+wv*c;c=Math.cos(s.yw);q=Math.sin(s.yw);let y1=y*c-w1*q,w2=y*q+w1*c;c=Math.cos(s.zw);q=Math.sin(s.zw);let z1=z*c-w2*q,w3=z*q+w2*c;const yaw=.72,pitch=.61;c=Math.cos(yaw);q=Math.sin(yaw);const xx=x1*c-z1*q,zz=x1*q+z1*c;c=Math.cos(pitch);q=Math.sin(pitch);const yy=y1*c-zz*q,zc=y1*q+zz*c,p=1/(1+Math.max(-.65,Math.min(.65,w3*.16+zc*.07))),scale=Math.min(width,height)*.105*p;return[width*.5+xx*scale,height*.49-yy*scale,zc,w3];}
  function resize(canvas){if(!canvas)return null;const r=canvas.getBoundingClientRect(),ratio=Math.min(2,w.devicePixelRatio||1),ww=Math.max(320,Math.round(r.width*ratio)),hh=Math.max(260,Math.round(r.height*ratio));if(canvas.width!==ww||canvas.height!==hh){canvas.width=ww;canvas.height=hh;}return{width:ww,height:hh,ratio:ratio};}
  function stroke(ctx,alpha,width){ctx.globalAlpha=alpha;ctx.lineWidth=width;ctx.strokeStyle=getComputedStyle(d.documentElement).color||'#111';}
  function drawTesseract(ctx,s,size){if(!s.tesseract)return;const v=[];for(let i=0;i<16;i++)v.push([i&1?1:-1,i&2?1:-1,i&4?1:-1,i&8?1:-1]);stroke(ctx,.22,1.1*size.ratio);for(let i=0;i<16;i++)for(let bit=0;bit<4;bit++){const j=i^(1<<bit);if(j<i)continue;const a=v[i],b=v[j],pa=project(s,a[0]*2.25,a[1]*2.25,a[2]*.75,a[3]*.7,size.width,size.height),pb=project(s,b[0]*2.25,b[1]*2.25,b[2]*.75,b[3]*.7,size.width,size.height);ctx.beginPath();ctx.moveTo(pa[0],pa[1]);ctx.lineTo(pb[0],pb[1]);ctx.stroke();}}
  function render(root){const s=state(root),canvas=one(root,'[data-v0710-canvas]');if(!canvas)return;const size=resize(canvas);if(!size)return;const ctx=canvas.getContext('2d');if(!ctx)return;ctx.clearRect(0,0,size.width,size.height);const bg=getComputedStyle(canvas).backgroundColor;if(bg&&bg!=='rgba(0, 0, 0, 0)'){ctx.fillStyle=bg;ctx.fillRect(0,0,size.width,size.height);}const n=s.demo==='compute-grid'&&s.surface?Math.min(41,s.surface.xValues.length):31,lo=-2.55,hi=2.55,step=(hi-lo)/(n-1);let peak=-Infinity;for(let row=0;row<n;row++){ctx.beginPath();for(let col=0;col<n;col++){const x=lo+col*step,y=lo+row*step,z=field(s,x,y);peak=Math.max(peak,z);const p=project(s,x,y,z,s.w,size.width,size.height);if(col===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);}stroke(ctx,.24,1*size.ratio);ctx.stroke();}for(let col=0;col<n;col+=2){ctx.beginPath();for(let row=0;row<n;row++){const x=lo+col*step,y=lo+row*step,z=field(s,x,y),p=project(s,x,y,z,s.w,size.width,size.height);if(row===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);}stroke(ctx,.15,.9*size.ratio);ctx.stroke();}if(s.contours){for(let ring=1;ring<=4;ring++){ctx.beginPath();for(let a=0;a<=64;a++){const th=a/64*Math.PI*2,r=ring*.5,x=Math.cos(th)*r,y=Math.sin(th)*r,z=field(s,x,y),p=project(s,x,y,z-.12,s.w,size.width,size.height);if(a===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);}stroke(ctx,.18,.8*size.ratio);ctx.stroke();}}if(s.vector){for(let ix=-2;ix<=2;ix++)for(let iy=-2;iy<=2;iy++){const x=ix,y=iy,z=field(s,x,y),eps=.08,gx=(field(s,x+eps,y)-field(s,x-eps,y))/(2*eps),gy=(field(s,x,y+eps)-field(s,x,y-eps))/(2*eps),a=project(s,x,y,z,s.w,size.width,size.height),b=project(s,x+.22*gx,y+.22*gy,z+.10,s.w,size.width,size.height);stroke(ctx,.34,1.15*size.ratio);ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}}if(s.uncertainty){ctx.save();ctx.globalAlpha=.08;ctx.fillStyle=getComputedStyle(d.documentElement).color||'#111';for(let i=0;i<45;i++){const x=lo+((i*37)%97)/96*(hi-lo),y=lo+((i*53)%89)/88*(hi-lo),z=field(s,x,y)+.2*Math.sin(i+s.w*4),p=project(s,x,y,z,s.w,size.width,size.height);ctx.beginPath();ctx.arc(p[0],p[1],3.2*size.ratio,0,Math.PI*2);ctx.fill();}ctx.restore();}drawTesseract(ctx,s,size);drawLinkedSurfaceSelection(ctx,s,size);ctx.globalAlpha=1;const peakNode=one(root,'[data-v0710-metric="peak"]');if(peakNode)peakNode.textContent=Number.isFinite(peak)?peak.toFixed(2):'—';const slice=one(root,'[data-v0710-metric="slice"]');if(slice)slice.textContent=s.w.toFixed(2);const read=one(root,'[data-v0710-readout]');if(read)read.textContent=(DEMOS[s.demo]||DEMOS.response).label+' · W '+s.w.toFixed(2)+(s.demo==='compute-grid'?' · compute-backed':' · browser rendered');const boundary=one(root,'[data-v015209-boundary]');if(boundary)boundary.textContent=(DEMOS[s.demo]||DEMOS.response).boundary;if(s.surface){const wm=one(root,'[data-v015209-w-value]');if(wm)wm.textContent=param(profile(s),s.surface.config.axes.w).label+' '+format(normalizedToActual(s.surface.wValues,s.w));}}
  function schedule(root){w.requestAnimationFrame(()=>render(root));}

  function updateRunMeta(root){const s=state(root),n=one(root,'[data-v015209-run-meta]');if(!n)return;if(!s.surface){n.textContent='No compute-backed surface has been run yet.';return;}const r=s.surface.runMetadata,c=s.surface.config,p=MODELS[c.model];n.textContent='Run '+r.startedAt+' · '+p.label+' · X '+param(p,c.axes.x).label+' · Y '+param(p,c.axes.y).label+' · W '+param(p,c.axes.w).label+' · '+r.evaluationCount+' evaluations / '+r.requestCount+' requests · '+r.elapsedMs+' ms · output '+format(s.surface.min)+' → '+format(s.surface.max)+(s.baseline?' · baseline available':'');}
  function setBaseline(root){const s=state(root);if(!s.surface)return;s.baseline=deepCopy(s.surface);updateRunMeta(root);const b=one(root,'[data-v015209-compare]');if(b)b.disabled=false;}
  function compare(root){const s=state(root);if(!baselineCompatible(s)){const n=one(root,'[data-v015209-run-meta]');if(n)n.textContent='Baseline is not compatible with the current model, axes, or grid.';return;}s.zMode='delta';const z=one(root,'[data-v015209-z-mode]');if(z)z.value='delta';schedule(root);}

  function currentConfig(root){const c=configFromUi(root);return c;}
  function readConfigs(){try{const x=JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]');return Array.isArray(x)?x:[];}catch(_){return[];}}
  function writeConfigs(items){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(items.slice(-20)));return true;}catch(_){return false;}}
  function refreshSaved(root){const sel=one(root,'[data-v015209-saved-configs]');if(!sel)return;const previous=sel.value;sel.innerHTML='<option value="">Saved configurations</option>';readConfigs().forEach((item,i)=>{const o=d.createElement('option');o.value=String(i);o.textContent=item.name;sel.appendChild(o);});if(previous&&Number(previous)<sel.options.length-1)sel.value=previous;}
  function saveConfig(root){const input=one(root,'[data-v015209-config-name]'),items=readConfigs(),name=String(input?.value||'').trim()||((MODELS[state(root).model]||MODELS.logistic_growth).label+' '+new Date().toLocaleString());items.push({name:name,savedAt:new Date().toISOString(),config:currentConfig(root)});writeConfigs(items);if(input)input.value='';refreshSaved(root);}
  function applyConfig(root,c){if(!c||!MODELS[c.model])return;populateModel(root,c.model,c);state(root).zMode=c.zMode||'output';updateBudget(root);schedule(root);}
  function loadConfig(root){const sel=one(root,'[data-v015209-saved-configs]'),i=Number(sel?.value);const items=readConfigs();if(Number.isInteger(i)&&items[i])applyConfig(root,items[i].config);}
  function deleteConfig(root){const sel=one(root,'[data-v015209-saved-configs]'),i=Number(sel?.value),items=readConfigs();if(Number.isInteger(i)&&items[i]){items.splice(i,1);writeConfigs(items);refreshSaved(root);}}
  function reset(root){const s=state(root);s.surface=null;s.baseline=null;s.demo='response';s.zMode='output';populateModel(root,'logistic_growth',null);const demo=one(root,'[data-v015209-demo]');if(demo)demo.value='response';const z=one(root,'[data-v015209-z-mode]');if(z)z.value='output';updateRunMeta(root);schedule(root);}

  function exportJson(root){const s=state(root),payload={schema:'sc-lab-response-surface-export/1.0',releaseVersion:VERSION,configuration:currentConfig(root),surface:s.surface,baseline:s.baseline?{configuration:s.baseline.config,runMetadata:s.baseline.runMetadata,min:s.baseline.min,max:s.baseline.max}:null,scientificBoundary:(DEMOS[s.demo]||DEMOS.response).boundary};const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=d.createElement('a');a.href=url;a.download='sustainable-catalyst-lab-response-surface-v015211.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function exportCsv(root){const s=state(root);if(!s.surface)return;const c=s.surface.config,rows=['xParameter,xValue,yParameter,yValue,wParameter,wValue,output'];s.surface.wValues.forEach((wv,wi)=>s.surface.yValues.forEach((yv,yi)=>s.surface.xValues.forEach((xv,xi)=>rows.push([c.axes.x,xv,c.axes.y,yv,c.axes.w,wv,s.surface.grid[wi][yi][xi]].join(',')))));const blob=new Blob([rows.join('\n')+'\n'],{type:'text/csv'}),url=URL.createObjectURL(blob),a=d.createElement('a');a.href=url;a.download='sustainable-catalyst-lab-response-surface-v015211.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function exportPng(root){const c=one(root,'[data-v0710-canvas]');if(!c)return;const a=d.createElement('a');a.href=c.toDataURL('image/png');a.download='sustainable-catalyst-lab-response-surface-v015211.png';a.click();}

  function analysisConfig(root){
    const model=one(root,'[data-v015210-analysis-model]')?.value||'product';
    const samples=Math.max(500,Math.min(config().maxMonteCarloSamples||50000,Math.floor(finite(one(root,'[data-v015210-samples]')?.value,5000))));
    const confidence=clamp(finite(one(root,'[data-v015210-confidence]')?.value,.95),.51,.999);
    const members=Math.max(3,Math.min(config().maxEnsembleMembers||7,Math.floor(finite(one(root,'[data-v015210-members]')?.value,5))));
    const seed=Math.max(0,Math.floor(finite(one(root,'[data-v015210-seed]')?.value,2026)));
    const exponent=finite(one(root,'[data-v015210-exponent]')?.value,2);
    const vars=[];
    all(root,'[data-v015210-variable]').forEach(row=>{
      const id=row.dataset.v015210Variable;
      const mean=finite(one(row,'[data-v015210-mean]')?.value,1);
      const rel=Math.max(0,finite(one(row,'[data-v015210-rel]')?.value,5));
      vars.push({name:id,mean:mean,rel:rel,stdDev:Math.max(Math.abs(mean)*rel/100,1e-9)});
    });
    const count=model==='power'?1:(model==='ratio'?2:3);
    return {model:model,samples:samples,confidence:confidence,members:members,seed:seed,exponent:exponent,variables:vars.slice(0,count)};
  }
  function analysisParameters(c){
    const p={confidence:c.confidence};
    if(c.model==='linear'){p.coefficients=c.variables.map(()=>1);p.intercept=0;}
    if(c.model==='power')p.exponent=c.exponent;
    return p;
  }
  function analysisStatus(root,text,tone){const n=one(root,'[data-v015210-status]');if(n){n.textContent=text;n.dataset.tone=tone||'neutral';}}
  function analysisMetrics(root,items){
    const box=one(root,'[data-v015210-metrics]');if(!box)return;box.innerHTML='';
    items.forEach(item=>{const el=d.createElement('div');el.className='sc-lab-v015210-metric';const small=d.createElement('small');small.textContent=item.label;const strong=d.createElement('strong');strong.textContent=item.value;const em=d.createElement('em');em.textContent=item.note||'';el.append(small,strong,em);box.appendChild(el);});
  }
  function drawAnalysis(root,kind,payload){
    const canvas=one(root,'[data-v015210-analysis-canvas]');if(!canvas)return;const s=state(root),size=resize(canvas);if(!size)return;const ctx=canvas.getContext('2d');if(!ctx)return;ctx.clearRect(0,0,size.width,size.height);const W=size.width,H=size.height,pad=30*size.ratio;ctx.save();ctx.strokeStyle='currentColor';ctx.fillStyle='currentColor';ctx.globalAlpha=.8;ctx.lineWidth=1*size.ratio;
    if(kind==='uncertainty'&&payload?.histogram){const counts=payload.histogram.counts||[],max=Math.max(1,...counts);const bw=(W-2*pad)/Math.max(1,counts.length);counts.forEach((v,i)=>{const h=(H-2*pad)*(v/max);ctx.globalAlpha=.48;ctx.fillRect(pad+i*bw,H-pad-h,Math.max(1,bw-1),h);});ctx.globalAlpha=.8;ctx.fillText('Monte Carlo output histogram',pad,18*size.ratio);}
    else if(kind==='sensitivity'&&Array.isArray(payload?.sensitivities)){const rows=payload.sensitivities,max=Math.max(1e-12,...rows.map(r=>Math.abs(Number(r.elasticity??r.derivative)||0)));const bh=(H-2*pad)/Math.max(1,rows.length);rows.forEach((r,i)=>{const v=Math.abs(Number(r.elasticity??r.derivative)||0);const ww=(W-2*pad)*(v/max);ctx.globalAlpha=.5;ctx.fillRect(pad,pad+i*bh,ww,Math.max(2,bh*.58));ctx.globalAlpha=.9;ctx.fillText(r.variable,pad+4,pad+i*bh+Math.max(12,bh*.45));});ctx.fillText('Local sensitivity magnitude',pad,18*size.ratio);}
    else if(kind==='ensemble'&&Array.isArray(payload?.members)){const rows=payload.members,max=Math.max(1e-12,...rows.map(r=>Math.abs(Number(r.mean)||0)));const gap=(W-2*pad)/Math.max(1,rows.length);rows.forEach((r,i)=>{const x=pad+i*gap+gap*.5,y=H-pad-(H-2*pad)*(Number(r.mean)/max);ctx.globalAlpha=.75;ctx.beginPath();ctx.arc(x,y,4*size.ratio,0,Math.PI*2);ctx.fill();if(i){const prev=rows[i-1],px=pad+(i-1)*gap+gap*.5,py=H-pad-(H-2*pad)*(Number(prev.mean)/max);ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(x,y);ctx.stroke();}});ctx.fillText('Seed-replication ensemble means',pad,18*size.ratio);}
    drawLinkedAnalysisSelection(ctx,s,size,kind,payload);
    ctx.restore();
  }
  async function runUncertainty(root){
    const s=state(root),c=analysisConfig(root);analysisStatus(root,'Running Monte Carlo uncertainty…','loading');
    try{const body=await getJson(config().runUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method:'uncertainty.monte_carlo_propagation',inputs:{model:c.model,samples:c.samples,distributions:c.variables.map(v=>({name:v.name,distribution:'normal',mean:v.mean,stdDev:v.stdDev}))},parameters:analysisParameters(c),random_seed:c.seed,requested_outputs:['summary','values']})});const out=body.output||body.result||body.outputs||body;s.analysis.mode='uncertainty';s.analysis.result=out;analysisStatus(root,'Monte Carlo uncertainty ready','ready');analysisMetrics(root,[{label:'Mean',value:format(out.mean),note:c.samples+' samples'},{label:'Std. deviation',value:format(out.standardDeviation),note:'modeled output spread'},{label:Math.round(c.confidence*100)+'% interval',value:(out.confidenceInterval||[]).map(format).join(' → '),note:'Monte Carlo interval'},{label:'Median',value:format(out.median),note:'simulation median'}]);drawAnalysis(root,'uncertainty',out);}
    catch(e){analysisStatus(root,String(e.message||e),'error');}
  }
  async function runSensitivity(root){
    const s=state(root),c=analysisConfig(root),baseline={};c.variables.forEach(v=>baseline[v.name]=v.mean);analysisStatus(root,'Running local sensitivity…','loading');
    try{const body=await getJson(config().runUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method:'sensitivity.local_finite_difference',inputs:{model:c.model,baseline:baseline},parameters:Object.assign(analysisParameters(c),{relativeStep:0.0001,absoluteStep:1e-8}),requested_outputs:['summary','values']})});const out=body.output||body.result||body.outputs||body;s.analysis.mode='sensitivity';s.analysis.sensitivity=out;const top=(out.sensitivities||[])[0]||{};analysisStatus(root,'Local sensitivity ready','ready');analysisMetrics(root,[{label:'Baseline output',value:format(out.baselineOutput),note:c.model+' model'},{label:'Largest derivative',value:format(top.derivative),note:top.variable||'—'},{label:'Elasticity',value:format(top.elasticity),note:'local, not causal'},{label:'Variables',value:String((out.sensitivities||[]).length),note:'finite-difference diagnostics'}]);drawAnalysis(root,'sensitivity',out);}
    catch(e){analysisStatus(root,String(e.message||e),'error');}
  }
  async function runEnsemble(root){
    const s=state(root),c=analysisConfig(root);analysisStatus(root,'Running seed-replication ensemble…','loading');
    try{const tasks=[];for(let i=0;i<c.members;i++){const seed=c.seed+i;tasks.push(getJson(config().runUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method:'uncertainty.monte_carlo_propagation',inputs:{model:c.model,samples:c.samples,distributions:c.variables.map(v=>({name:v.name,distribution:'normal',mean:v.mean,stdDev:v.stdDev}))},parameters:analysisParameters(c),random_seed:seed,requested_outputs:['summary']})}).then(body=>{const out=body.output||body.result||body.outputs||body;return {seed:seed,mean:Number(out.mean),standardDeviation:Number(out.standardDeviation),confidenceInterval:out.confidenceInterval};}));}
      const members=await Promise.all(tasks),means=members.map(x=>x.mean),mean=means.reduce((a,b)=>a+b,0)/means.length,spread=Math.sqrt(means.reduce((a,b)=>a+(b-mean)*(b-mean),0)/Math.max(1,means.length-1));const out={schema:'sc-lab-seed-replication-ensemble/1.0',members:members,memberCount:members.length,ensembleMean:mean,betweenSeedStandardDeviation:spread,samplesPerMember:c.samples};s.analysis.mode='ensemble';s.analysis.ensemble=out;analysisStatus(root,'Seed-replication ensemble ready','ready');analysisMetrics(root,[{label:'Ensemble mean',value:format(mean),note:c.members+' independent seeds'},{label:'Between-seed spread',value:format(spread),note:'replication stability'},{label:'Members',value:String(c.members),note:c.samples+' samples each'},{label:'Total simulations',value:String(c.members*c.samples),note:'bounded explicit compute'}]);drawAnalysis(root,'ensemble',out);}
    catch(e){analysisStatus(root,String(e.message||e),'error');}
  }
  function updateAnalysisModel(root){const c=analysisConfig(root),rows=all(root,'[data-v015210-variable]');rows.forEach((row,i)=>row.hidden=i>=c.variables.length);const exp=one(root,'[data-v015210-exponent-wrap]');if(exp)exp.hidden=c.model!=='power';}
  function bindAnalysis(root){if(!root||root.dataset.v015210AnalysisBound==='1')return;root.dataset.v015210AnalysisBound='1';one(root,'[data-v015210-analysis-model]')?.addEventListener('change',()=>updateAnalysisModel(root));one(root,'[data-v015210-run-uncertainty]')?.addEventListener('click',()=>runUncertainty(root));one(root,'[data-v015210-run-sensitivity]')?.addEventListener('click',()=>runSensitivity(root));one(root,'[data-v015210-run-ensemble]')?.addEventListener('click',()=>runEnsemble(root));updateAnalysisModel(root);analysisStatus(root,'Ready. Compute runs only on explicit action.','ready');}

  function nearestIndex(values,value){if(!Array.isArray(values)||!values.length)return 0;let best=0,dist=Infinity;values.forEach((v,i)=>{const d=Math.abs(Number(v)-Number(value));if(d<dist){dist=d;best=i;}});return best;}
  function selectionId(){return 'sel-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,7);}
  function linkedStatus(root,text,tone){const n=one(root,'[data-v015211-status]');if(n){n.textContent=text;n.dataset.tone=tone||'neutral';}}
  function selectionSummary(sel){if(!sel)return 'No selection';if(sel.source==='4d-response-surface')return 'Surface · '+(sel.model||'model')+' · '+format(sel.values&&sel.values.z);if(sel.source==='uncertainty-diagnostic')return 'Uncertainty · bin '+String((sel.analysis&&sel.analysis.index)||0);if(sel.source==='sensitivity-diagnostic')return 'Sensitivity · '+String(sel.analysis&&sel.analysis.variable||'variable');if(sel.source==='ensemble-diagnostic')return 'Ensemble · seed '+String((sel.analysis&&sel.analysis.seed)!=null?sel.analysis.seed:'—');return String(sel.source||'selection');}
  function parameterRows(sel){const rows=[];if(sel&&sel.parameters){Object.entries(sel.parameters).forEach(([key,value])=>rows.push({name:key,value:value,role:(sel.axes&&Object.values(sel.axes).includes(key))?'axis':'fixed'}));}if(sel&&sel.values){for(const k of ['x','y','w','z'])if(Object.prototype.hasOwnProperty.call(sel.values,k))rows.push({name:k.toUpperCase(),value:sel.values[k],role:k==='z'?'response':'selected'});}return rows;}
  function renderLinked(root){const s=state(root),l=s.linked,sel=l.current;all(root,'[data-v015211-view]').forEach(v=>v.dataset.active=sel&&((v.dataset.v015211View==='selection')||(v.dataset.v015211View==='parameters'&&sel.source==='4d-response-surface')||(v.dataset.v015211View==='history'))?'true':'false');const set=(k,v)=>{const n=one(root,'[data-v015211-field="'+k+'"]');if(n){n.textContent=v==null?'—':String(v);n.classList.toggle('sc-lab-v015211-empty',!sel&&k==='source');}};set('source',sel?sel.source:'No selection');set('model',sel?(sel.model||sel.mode||'—'):'—');set('x',sel&&sel.values&&sel.values.x!=null?format(sel.values.x):'—');set('y',sel&&sel.values&&sel.values.y!=null?format(sel.values.y):'—');set('w',sel&&sel.values&&sel.values.w!=null?format(sel.values.w):'—');set('z',sel&&sel.values&&sel.values.z!=null?format(sel.values.z):(sel&&sel.analysis&&sel.analysis.value!=null?format(sel.analysis.value):'—'));
    const table=one(root,'[data-v015211-table]');if(table){table.innerHTML='';const rows=parameterRows(sel);if(!rows.length){const tr=d.createElement('tr'),td=d.createElement('td');td.colSpan=3;td.className='sc-lab-v015211-empty';td.textContent='No parameter snapshot for this selection.';tr.appendChild(td);table.appendChild(tr);}else rows.forEach(row=>{const tr=d.createElement('tr');[row.name,format(row.value),row.role].forEach(value=>{const td=d.createElement('td');td.textContent=String(value);tr.appendChild(td);});table.appendChild(tr);});}
    const history=one(root,'[data-v015211-history]');if(history){history.innerHTML='';if(!l.history.length){const li=d.createElement('li');li.className='sc-lab-v015211-empty';li.textContent='No selections yet.';history.appendChild(li);}else l.history.forEach((item,i)=>{const li=d.createElement('li'),b=d.createElement('button');b.type='button';b.dataset.v015211History=String(i);b.textContent=selectionSummary(item);li.appendChild(b);history.appendChild(li);});}
    const pins=one(root,'[data-v015211-pins]');if(pins)pins.textContent=l.pins.length+' pinned selection'+(l.pins.length===1?'':'s');all(root,'[data-v015211-pin],[data-v015211-clear],[data-v015211-export],[data-v015211-graph]').forEach(b=>b.disabled=!sel);const toggle=one(root,'[data-v015211-toggle]');if(toggle){toggle.setAttribute('aria-pressed',String(l.enabled));toggle.textContent=l.enabled?'Linked selection on':'Linked selection off';}linkedStatus(root,l.enabled?(sel?'Linked · '+selectionSummary(sel):'Linked · select a point or diagnostic element'):'Linked selection paused',l.enabled?'ready':'warning');}
  function emitLinked(root,sel){try{root.dispatchEvent(new CustomEvent('sc-lab:linked-selection',{detail:deepCopy(sel)}));d.dispatchEvent(new CustomEvent('sc-lab:linked-selection',{detail:deepCopy(sel)}));}catch(_){}}
  function setLinkedSelection(root,selection,record){const s=state(root),l=s.linked;if(!l.enabled||!selection)return;selection.id=selection.id||selectionId();selection.schema='sc-lab-linked-selection/1.0';selection.releaseVersion=VERSION;selection.timestamp=selection.timestamp||new Date().toISOString();l.current=selection;if(record!==false){l.history.unshift(deepCopy(selection));l.history=l.history.slice(0,config().selectionHistoryLimit);}renderLinked(root);emitLinked(root,selection);schedule(root);if(s.analysis.mode){const payload=s.analysis.mode==='uncertainty'?s.analysis.result:s.analysis.mode==='sensitivity'?s.analysis.sensitivity:s.analysis.ensemble;if(payload)drawAnalysis(root,s.analysis.mode,payload);}}
  function surfaceSelection(root,event){const s=state(root),canvas=one(root,'[data-v0710-canvas]');if(!canvas||!s.linked.enabled)return;const r=canvas.getBoundingClientRect(),px=clamp((event.clientX-r.left)/Math.max(1,r.width),0,1),py=clamp((event.clientY-r.top)/Math.max(1,r.height),0,1),planeX=px*5.1-2.55,planeY=py*5.1-2.55;if(s.demo==='compute-grid'&&s.surface){const c=s.surface.config,xv=s.surface.xValues[0]+px*(s.surface.xValues.at(-1)-s.surface.xValues[0]),yv=s.surface.yValues[0]+py*(s.surface.yValues.at(-1)-s.surface.yValues[0]),wv=normalizedToActual(s.surface.wValues,s.w),raw=rawResponse(s,planeX,planeY),params=Object.assign({},c.fixed);params[c.axes.x]=xv;params[c.axes.y]=yv;params[c.axes.w]=wv;setLinkedSelection(root,{source:'4d-response-surface',model:c.model,mode:'compute-grid',axes:deepCopy(c.axes),parameters:params,values:{x:xv,y:yv,w:wv,z:raw},normalized:{x:px,y:py,w:s.w},indices:{x:nearestIndex(s.surface.xValues,xv),y:nearestIndex(s.surface.yValues,yv),w:nearestIndex(s.surface.wValues,wv)},plane:{x:planeX,y:planeY}},true);}else{setLinkedSelection(root,{source:'4d-response-surface',model:'browser-demonstration',mode:s.demo,values:{x:planeX,y:planeY,w:s.w,z:field(s,planeX,planeY)},normalized:{x:px,y:py,w:s.w},plane:{x:planeX,y:planeY}},true);}}
  function analysisSelection(root,event){const s=state(root),canvas=one(root,'[data-v015210-analysis-canvas]');if(!canvas||!s.linked.enabled||!s.analysis.mode)return;const r=canvas.getBoundingClientRect(),px=clamp((event.clientX-r.left)/Math.max(1,r.width),0,1),py=clamp((event.clientY-r.top)/Math.max(1,r.height),0,1),kind=s.analysis.mode;if(kind==='uncertainty'){const out=s.analysis.result||{},counts=(out.histogram&&out.histogram.counts)||[],edges=(out.histogram&&out.histogram.edges)||[],idx=Math.max(0,Math.min(Math.max(0,counts.length-1),Math.floor(px*Math.max(1,counts.length))));let value=idx;if(edges.length>idx+1)value=(Number(edges[idx])+Number(edges[idx+1]))/2;setLinkedSelection(root,{source:'uncertainty-diagnostic',model:analysisConfig(root).model,mode:kind,analysis:{index:idx,count:counts[idx]??null,value:value,confidenceInterval:out.confidenceInterval||null},values:{z:value}},true);}else if(kind==='sensitivity'){const out=s.analysis.sensitivity||{},rows=out.sensitivities||[],idx=Math.max(0,Math.min(Math.max(0,rows.length-1),Math.floor(py*Math.max(1,rows.length)))),item=rows[idx]||{};setLinkedSelection(root,{source:'sensitivity-diagnostic',model:analysisConfig(root).model,mode:kind,analysis:{index:idx,variable:item.variable||null,derivative:item.derivative??null,elasticity:item.elasticity??null,value:item.elasticity??item.derivative??null},values:{z:item.elasticity??item.derivative??null}},true);}else if(kind==='ensemble'){const out=s.analysis.ensemble||{},rows=out.members||[],idx=Math.max(0,Math.min(Math.max(0,rows.length-1),Math.floor(px*Math.max(1,rows.length)))),item=rows[idx]||{};setLinkedSelection(root,{source:'ensemble-diagnostic',model:analysisConfig(root).model,mode:kind,analysis:{index:idx,seed:item.seed??null,mean:item.mean??null,standardDeviation:item.standardDeviation??null,value:item.mean??null},values:{z:item.mean??null}},true);}}
  function drawLinkedSurfaceSelection(ctx,s,size){const sel=s.linked&&s.linked.current;if(!sel||sel.source!=='4d-response-surface'||!sel.plane)return;const z=Number(sel.values&&sel.values.z);if(!Number.isFinite(z))return;const p=project(s,Number(sel.plane.x),Number(sel.plane.y),z,s.w,size.width,size.height);ctx.save();ctx.globalAlpha=.95;ctx.strokeStyle='currentColor';ctx.fillStyle='currentColor';ctx.lineWidth=1.5*size.ratio;ctx.beginPath();ctx.arc(p[0],p[1],7*size.ratio,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(p[0]-11*size.ratio,p[1]);ctx.lineTo(p[0]+11*size.ratio,p[1]);ctx.moveTo(p[0],p[1]-11*size.ratio);ctx.lineTo(p[0],p[1]+11*size.ratio);ctx.stroke();ctx.restore();}
  function drawLinkedAnalysisSelection(ctx,s,size,kind,payload){const sel=s.linked&&s.linked.current;if(!sel||sel.mode!==kind||!sel.analysis)return;const W=size.width,H=size.height,pad=30*size.ratio;ctx.save();ctx.strokeStyle='currentColor';ctx.lineWidth=2*size.ratio;ctx.globalAlpha=.95;if(kind==='uncertainty'&&payload?.histogram){const counts=payload.histogram.counts||[],bw=(W-2*pad)/Math.max(1,counts.length),i=Math.max(0,Math.min(counts.length-1,Number(sel.analysis.index)||0));ctx.strokeRect(pad+i*bw,pad,Math.max(1,bw),H-2*pad);}else if(kind==='sensitivity'&&Array.isArray(payload?.sensitivities)){const rows=payload.sensitivities,bh=(H-2*pad)/Math.max(1,rows.length),i=Math.max(0,Math.min(rows.length-1,Number(sel.analysis.index)||0));ctx.strokeRect(pad,pad+i*bh,W-2*pad,bh);}else if(kind==='ensemble'&&Array.isArray(payload?.members)){const rows=payload.members,max=Math.max(1e-12,...rows.map(r=>Math.abs(Number(r.mean)||0))),gap=(W-2*pad)/Math.max(1,rows.length),i=Math.max(0,Math.min(rows.length-1,Number(sel.analysis.index)||0)),item=rows[i]||{},x=pad+i*gap+gap*.5,y=H-pad-(H-2*pad)*(Number(item.mean||0)/max);ctx.beginPath();ctx.arc(x,y,8*size.ratio,0,Math.PI*2);ctx.stroke();}ctx.restore();}
  function restoreHistorySelection(root,index){const s=state(root),sel=s.linked.history[index];if(!sel)return;if(sel.source==='4d-response-surface'&&sel.normalized&&Number.isFinite(Number(sel.normalized.w))){s.w=Number(sel.normalized.w);const input=one(root,'[data-v0710-w]');if(input)input.value=String(s.w);}setLinkedSelection(root,deepCopy(sel),false);}
  function pinSelection(root){const s=state(root),sel=s.linked.current;if(!sel)return;if(s.linked.pins.some(p=>p.id===sel.id))return;s.linked.pins.unshift(deepCopy(sel));s.linked.pins=s.linked.pins.slice(0,config().pinLimit);renderLinked(root);}
  function clearSelection(root){const s=state(root);s.linked.current=null;renderLinked(root);schedule(root);if(s.analysis.mode){const payload=s.analysis.mode==='uncertainty'?s.analysis.result:s.analysis.mode==='sensitivity'?s.analysis.sensitivity:s.analysis.ensemble;if(payload)drawAnalysis(root,s.analysis.mode,payload);}}
  function exportSelection(root){const sel=state(root).linked.current;if(!sel)return;const payload={schema:'sc-lab-linked-selection-export/1.0',releaseVersion:VERSION,selection:sel,pins:state(root).linked.pins,scientificBoundary:'Linked selection preserves inspection state and provenance; it does not establish cross-model equivalence, causality, evidence, significance, calibration, or validity.'};const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=d.createElement('a');a.href=url;a.download='sustainable-catalyst-lab-linked-selection-v015211.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function graphStudioHandoff(root){const sel=state(root).linked.current;if(!sel)return;const packet={schema:'sc-lab-graph-studio-selection-handoff/1.0',releaseVersion:VERSION,createdAt:new Date().toISOString(),sourceRuntime:RUNTIME,selection:deepCopy(sel),pins:deepCopy(state(root).linked.pins),scientificBoundary:'Handoff transfers selected state and provenance only; it does not assert cross-model equivalence or scientific validity.'};try{w.sessionStorage.setItem(HANDOFF_KEY,JSON.stringify(packet));}catch(_){}try{d.dispatchEvent(new CustomEvent('sc-lab:graph-studio-handoff',{detail:deepCopy(packet)}));}catch(_){}const button=one(root,'[data-open-module="'+config().graphStudioModule+'"]');if(button)button.click();}
  function bindLinked(root){if(!root||root.dataset.v015211LinkedBound==='1')return;root.dataset.v015211LinkedBound='1';const s=state(root),surface=one(root,'[data-v0710-canvas]'),analysis=one(root,'[data-v015210-analysis-canvas]');if(surface)surface.addEventListener('click',e=>surfaceSelection(root,e));if(analysis)analysis.addEventListener('click',e=>analysisSelection(root,e));one(root,'[data-v015211-toggle]')?.addEventListener('click',e=>{s.linked.enabled=!s.linked.enabled;e.currentTarget.setAttribute('aria-pressed',String(s.linked.enabled));renderLinked(root);});one(root,'[data-v015211-pin]')?.addEventListener('click',()=>pinSelection(root));one(root,'[data-v015211-clear]')?.addEventListener('click',()=>clearSelection(root));one(root,'[data-v015211-export]')?.addEventListener('click',()=>exportSelection(root));one(root,'[data-v015211-graph]')?.addEventListener('click',()=>graphStudioHandoff(root));one(root,'[data-v015211-history]')?.addEventListener('click',e=>{const b=e.target.closest('[data-v015211-history]');if(b)restoreHistorySelection(root,Number(b.dataset.v015211History));});renderLinked(root);}


  function sceneSnapshot(root){
    const s=state(root);
    return deepCopy({
      schema:'sc-lab-4d-scene-state/1.0',
      releaseVersion:VERSION,
      sourceRuntime:RUNTIME,
      capturedAt:new Date().toISOString(),
      demo:s.demo,
      model:s.model,
      axes:s.axes,
      zMode:s.zMode,
      fixed:s.fixed,
      view:{w:s.w,xw:s.xw,yw:s.yw,zw:s.zw,layers:{vector:s.vector,uncertainty:s.uncertainty,contours:s.contours,tesseract:s.tesseract}},
      surface:s.surface,
      baseline:s.baseline,
      compute:s.compute,
      analysis:s.analysis,
      linked:{current:s.linked.current,history:s.linked.history,pins:s.linked.pins}
    });
  }

  function restoreScene(root,snapshot){
    if(!root||!snapshot||snapshot.schema!=='sc-lab-4d-scene-state/1.0')throw new Error('Unsupported 4D scene snapshot.');
    const s=state(root), p=MODELS[snapshot.model]||MODELS.logistic_growth;
    populateModel(root,snapshot.model||'logistic_growth',snapshot.surface&&snapshot.surface.config?snapshot.surface.config:null);
    s.model=snapshot.model||'logistic_growth';
    s.axes=Object.assign({},snapshot.axes||p.axes);
    s.zMode=snapshot.zMode||'output';
    s.fixed=Object.assign(defaultFixed(p),snapshot.fixed||{});
    const v=snapshot.view||{};
    s.w=finite(v.w,.37);s.xw=finite(v.xw,.34);s.yw=finite(v.yw,-.22);s.zw=finite(v.zw,.12);
    const layers=v.layers||{};
    if(typeof layers.vector==='boolean')s.vector=layers.vector;
    if(typeof layers.uncertainty==='boolean')s.uncertainty=layers.uncertainty;
    if(typeof layers.contours==='boolean')s.contours=layers.contours;
    if(typeof layers.tesseract==='boolean')s.tesseract=layers.tesseract;
    s.surface=snapshot.surface?deepCopy(snapshot.surface):null;
    s.baseline=snapshot.baseline?deepCopy(snapshot.baseline):null;
    if(snapshot.compute)s.compute=deepCopy(snapshot.compute);
    if(snapshot.analysis)s.analysis=deepCopy(snapshot.analysis);
    if(snapshot.linked){
      s.linked.current=snapshot.linked.current?deepCopy(snapshot.linked.current):null;
      s.linked.history=Array.isArray(snapshot.linked.history)?deepCopy(snapshot.linked.history).slice(0,config().selectionHistoryLimit):[];
      s.linked.pins=Array.isArray(snapshot.linked.pins)?deepCopy(snapshot.linked.pins).slice(0,config().pinLimit):[];
    }
    s.demo=s.surface?'compute-grid':(snapshot.demo||'response');
    const demo=one(root,'[data-v015209-demo]');if(demo)demo.value=s.demo;
    const wInput=one(root,'[data-v0710-w]'),xInput=one(root,'[data-v0710-xw]'),yInput=one(root,'[data-v0710-yw]');
    if(wInput)wInput.value=String(s.w);if(xInput)xInput.value=String(s.xw);if(yInput)yInput.value=String(s.yw);
    all(root,'[data-v0710-layer]').forEach(button=>{const k=button.dataset.v0710Layer;const on=k==='vector'?s.vector:k==='uncertainty'?s.uncertainty:k==='contours'?s.contours:s.tesseract;button.setAttribute('aria-pressed',String(on));});
    updateRunMeta(root);renderLinked(root);schedule(root);
    if(s.analysis&&s.analysis.mode){const payload=s.analysis.mode==='uncertainty'?s.analysis.result:s.analysis.mode==='sensitivity'?s.analysis.sensitivity:s.analysis.ensemble;if(payload)drawAnalysis(root,s.analysis.mode,payload);}
    try{root.dispatchEvent(new CustomEvent('sc-lab:scene-restored',{detail:{version:VERSION,schema:snapshot.schema}}));}catch(_){}
    return true;
  }

  function tick(root,t){const s=state(root);if(!s.playing){s.raf=0;return;}if(!s.last)s.last=t;const dt=Math.min(.05,(t-s.last)/1000);s.last=t;s.w+=dt*.34;if(s.w>1)s.w=-1;const input=one(root,'[data-v0710-w]');if(input)input.value=String(s.w);render(root);s.raf=w.requestAnimationFrame(n=>tick(root,n));}

  function bind(root){if(!root||root.dataset.v015209Bound==='1')return;root.dataset.v015209Bound='1';const s=state(root),wInput=one(root,'[data-v0710-w]'),xInput=one(root,'[data-v0710-xw]'),yInput=one(root,'[data-v0710-yw]');if(wInput)s.w=finite(wInput.value,.37);if(xInput)s.xw=finite(xInput.value,.34);if(yInput)s.yw=finite(yInput.value,-.22);
    all(root,'[data-v0710-w],[data-v0710-xw],[data-v0710-yw]').forEach(input=>input.addEventListener('input',()=>{s.w=finite(wInput&&wInput.value,s.w);s.xw=finite(xInput&&xInput.value,s.xw);s.yw=finite(yInput&&yInput.value,s.yw);schedule(root);}));
    all(root,'[data-v0710-layer]').forEach(button=>button.addEventListener('click',()=>{const k=button.dataset.v0710Layer;if(k==='vector')s.vector=!s.vector;if(k==='uncertainty')s.uncertainty=!s.uncertainty;if(k==='contours')s.contours=!s.contours;if(k==='tesseract')s.tesseract=!s.tesseract;button.setAttribute('aria-pressed',String(k==='vector'?s.vector:k==='uncertainty'?s.uncertainty:k==='contours'?s.contours:s.tesseract));schedule(root);}));
    one(root,'[data-v0710-animate]')?.addEventListener('click',event=>{s.playing=!s.playing;event.currentTarget.setAttribute('aria-pressed',String(s.playing));event.currentTarget.textContent=s.playing?'Pause 4D sweep':'Animate 4D sweep';if(s.playing&&!s.raf){s.last=0;s.raf=w.requestAnimationFrame(t=>tick(root,t));}});
    const demo=one(root,'[data-v015209-demo]');if(demo)demo.addEventListener('change',()=>{if(demo.value==='compute-grid'&&!s.surface){demo.value=s.demo;return;}s.demo=demo.value;schedule(root);});
    const model=one(root,'[data-v015209-model]');if(model)model.addEventListener('change',()=>{populateModel(root,model.value,null);});
    all(root,'[data-v015209-axis]').forEach(sel=>sel.addEventListener('change',()=>{const c={axes:{x:one(root,'[data-v015209-axis="x"]')?.value,y:one(root,'[data-v015209-axis="y"]')?.value,w:one(root,'[data-v015209-axis="w"]')?.value}};syncRanges(root,c);renderFixedControls(root,null);updateBudget(root);}));
    all(root,'[data-v015209-range],[data-v015209-resolution]').forEach(n=>n.addEventListener('input',()=>updateBudget(root)));
    one(root,'[data-v015209-z-mode]')?.addEventListener('change',e=>{s.zMode=e.target.value;schedule(root);});
    one(root,'[data-v015209-run-surface]')?.addEventListener('click',()=>runSurface(root));one(root,'[data-v015209-refresh-compute]')?.addEventListener('click',()=>refreshCompute(root));one(root,'[data-v015209-set-baseline]')?.addEventListener('click',()=>setBaseline(root));one(root,'[data-v015209-compare]')?.addEventListener('click',()=>compare(root));one(root,'[data-v015209-reset]')?.addEventListener('click',()=>reset(root));one(root,'[data-v015209-save-config]')?.addEventListener('click',()=>saveConfig(root));one(root,'[data-v015209-load-config]')?.addEventListener('click',()=>loadConfig(root));one(root,'[data-v015209-delete-config]')?.addEventListener('click',()=>deleteConfig(root));
    all(root,'[data-v015209-export]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.v015209Export;if(k==='png')exportPng(root);if(k==='json')exportJson(root);if(k==='csv')exportCsv(root);}));
    const canvas=one(root,'[data-v0710-canvas]');if(canvas){canvas.addEventListener('pointermove',event=>{const r=canvas.getBoundingClientRect(),px=clamp((event.clientX-r.left)/Math.max(1,r.width),0,1),py=clamp((event.clientY-r.top)/Math.max(1,r.height),0,1),x=px*5.1-2.55,y=py*5.1-2.55,node=one(root,'[data-v0710-pointer]');if(s.demo==='compute-grid'&&s.surface){const c=s.surface.config,xv=s.surface.xValues[0]+px*(s.surface.xValues.at(-1)-s.surface.xValues[0]),yv=s.surface.yValues[0]+py*(s.surface.yValues.at(-1)-s.surface.yValues[0]),wv=normalizedToActual(s.surface.wValues,s.w),raw=rawResponse(s,x,y);if(node)node.textContent=c.axes.x+' '+format(xv)+' · '+c.axes.y+' '+format(yv)+' · '+c.axes.w+' '+format(wv)+' · output '+format(raw);}else if(node)node.textContent='x '+x.toFixed(2)+' · y '+y.toFixed(2)+' · response '+field(s,x,y).toFixed(2)+' · w '+s.w.toFixed(2);});}
    if(w.ResizeObserver&&canvas){s.resize=new ResizeObserver(()=>schedule(root));s.resize.observe(canvas);}populateModel(root,'logistic_growth',null);refreshSaved(root);refreshCompute(root);updateRunMeta(root);bindAnalysis(root);bindLinked(root);schedule(root);
  }
  function boot(){all(d,'[data-v0710-visualizer]').forEach(bind);}
  if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
  d.addEventListener('sc-lab:safe-module-opened',e=>{if(e.detail&&e.detail.module==='overview')boot();});
  w.SCLabLinkedViewsV015212Runtime=Object.freeze({version:VERSION,runtime:RUNTIME,boot:boot,refreshCompute:refreshCompute,runSurface:runSurface,runUncertainty:runUncertainty,runSensitivity:runSensitivity,runEnsemble:runEnsemble,setSelection:setLinkedSelection,clearSelection:clearSelection,graphStudioHandoff:graphStudioHandoff,sceneSnapshot:sceneSnapshot,restoreScene:restoreScene});
})(window, document);
