(function (w, d) {
  'use strict';

  const VERSION = '0.152.0.7';
  const RUNTIME = 'interactive-4d-front-door-v015207';
  const roots = new WeakMap();

  const DEMOS = Object.freeze({
    response: { label: 'Nonlinear response surface', boundary: 'Illustrative browser-rendered response field.' },
    dynamic: { label: 'Dynamic system landscape', boundary: 'Illustrative dynamic-system surface; not an observed trajectory.' },
    uncertainty: { label: 'Uncertainty landscape', boundary: 'Illustrative uncertainty topology; not a confidence or credible interval.' },
    sensitivity: { label: 'Sensitivity surface', boundary: 'Illustrative sensitivity field; visual gradient is not causal evidence.' },
    ensemble: { label: 'Ensemble response field', boundary: 'Illustrative ensemble-like variation; not a calibrated forecast.' },
    spatiotemporal: { label: 'Spatiotemporal field', boundary: 'Illustrative spatial-temporal response; not geolocated observations.' },
    compute: { label: 'Python compute parameter sweep', boundary: 'Uses the registered Python Compute Core logistic-growth parameter sweep; the 4D surface is a visualization mapping of returned sweep values.' }
  });

  function all(root, selector) { return root && root.querySelectorAll ? Array.from(root.querySelectorAll(selector)) : []; }
  function one(root, selector) { return root && root.querySelector ? root.querySelector(selector) : null; }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, Number(v) || 0)); }
  function finite(v, fallback) { v = Number(v); return Number.isFinite(v) ? v : fallback; }

  function config() {
    const c = w.SCLabInteractive4DV015207 || {};
    return {
      healthUrl: c.computeHealthUrl || '/wp-json/sc-lab/v1/compute/core/health',
      capabilitiesUrl: c.computeCapabilitiesUrl || '/wp-json/sc-lab/v1/compute/core/capabilities',
      runUrl: c.computeRunUrl || '/wp-json/sc-lab/v1/compute/core/run',
      nonce: c.nonce || ''
    };
  }

  function state(root) {
    if (roots.has(root)) return roots.get(root);
    const s = {
      demo: 'response', w: .37, xw: .34, yw: -.22, zw: .12,
      vector: true, uncertainty: true, contours: true, tesseract: true,
      playing: false, raf: 0, last: 0, phase: 0,
      compute: { status: 'unknown', version: null, methods: null, rows: null, min: null, max: null },
      pointer: null
    };
    roots.set(root, s); return s;
  }

  function field(s, x, y) {
    const wv = s.w;
    if (s.demo === 'dynamic') return 1.05*Math.sin(x*.9 + wv*2.1) + .68*Math.cos(y*1.35 - wv) + .16*x*y;
    if (s.demo === 'uncertainty') return .75*Math.sin(x*1.3)*Math.cos(y*.85) + .55*Math.cos((x-y)*.55 + wv*2.4);
    if (s.demo === 'sensitivity') return .42*x*y + .82*Math.sin((x+wv)*1.1) - .48*Math.cos((y-wv)*1.55);
    if (s.demo === 'ensemble') return .58*Math.sin(x*1.2+wv) + .48*Math.sin(y*1.7-wv*.7) + .31*Math.cos((x+y+wv)*2.2);
    if (s.demo === 'spatiotemporal') return 1.2*Math.exp(-.11*(x*x+y*y))*Math.cos(2.1*Math.hypot(x,y)-wv*3.2) + .18*Math.sin(x-y);
    if (s.demo === 'compute' && Array.isArray(s.compute.rows) && s.compute.rows.length) {
      const t = clamp((wv+1)/2,0,1)*(s.compute.rows.length-1);
      const a = Math.floor(t), b = Math.min(s.compute.rows.length-1,a+1), f=t-a;
      const va=finite(s.compute.rows[a].output,0), vb=finite(s.compute.rows[b].output,va);
      const min=finite(s.compute.min,0), max=finite(s.compute.max,1), span=Math.max(1e-9,max-min);
      const n=((va+(vb-va)*f)-min)/span;
      return (n*2-1)*1.45 + .38*Math.sin(x*1.15)+.28*Math.cos(y*1.35)+.12*x*y;
    }
    return Math.sin(x*1.25 + wv*.9)*Math.cos(y*1.05 - wv*.55) + .34*Math.sin((x+y)*.8 + wv*1.8);
  }

  function project(s, x, y, z, wv, width, height) {
    let c=Math.cos(s.xw), q=Math.sin(s.xw), x1=x*c-wv*q, w1=x*q+wv*c;
    c=Math.cos(s.yw); q=Math.sin(s.yw); let y1=y*c-w1*q, w2=y*q+w1*c;
    c=Math.cos(s.zw); q=Math.sin(s.zw); let z1=z*c-w2*q, w3=z*q+w2*c;
    const yaw=.72, pitch=.61;
    c=Math.cos(yaw); q=Math.sin(yaw); const xx=x1*c-z1*q, zz=x1*q+z1*c;
    c=Math.cos(pitch); q=Math.sin(pitch); const yy=y1*c-zz*q, zc=y1*q+zz*c;
    const p=1/(1+Math.max(-.65,Math.min(.65,w3*.16+zc*.07)));
    const scale=Math.min(width,height)*.105*p;
    return [width*.5+xx*scale, height*.49-yy*scale, zc, w3];
  }

  function resize(canvas) {
    if (!canvas) return null;
    const rect=canvas.getBoundingClientRect();
    const ratio=Math.min(2,w.devicePixelRatio||1);
    const ww=Math.max(320,Math.round(rect.width*ratio)), hh=Math.max(260,Math.round(rect.height*ratio));
    if (canvas.width!==ww || canvas.height!==hh) { canvas.width=ww; canvas.height=hh; }
    return { width:ww, height:hh, ratio:ratio };
  }

  function stroke(ctx, alpha, width) {
    ctx.globalAlpha=alpha; ctx.lineWidth=width; ctx.strokeStyle=getComputedStyle(d.documentElement).color || '#111';
  }

  function drawTesseract(ctx,s,size) {
    if (!s.tesseract) return;
    const vertices=[];
    for(let i=0;i<16;i++) vertices.push([i&1?1:-1,i&2?1:-1,i&4?1:-1,i&8?1:-1]);
    stroke(ctx,.22,1.1*size.ratio);
    for(let i=0;i<16;i++) for(let bit=0;bit<4;bit++) { const j=i^(1<<bit); if(j<i) continue; const a=vertices[i],b=vertices[j]; const pa=project(s,a[0]*2.25,a[1]*2.25,a[2]*.75,a[3]*.7,size.width,size.height); const pb=project(s,b[0]*2.25,b[1]*2.25,b[2]*.75,b[3]*.7,size.width,size.height); ctx.beginPath();ctx.moveTo(pa[0],pa[1]);ctx.lineTo(pb[0],pb[1]);ctx.stroke(); }
  }

  function render(root) {
    const s=state(root), canvas=one(root,'[data-v0710-canvas]'); if(!canvas) return;
    const size=resize(canvas); if(!size) return; const ctx=canvas.getContext('2d'); if(!ctx) return;
    ctx.clearRect(0,0,size.width,size.height);
    const bg=getComputedStyle(canvas).backgroundColor; if(bg && bg!=='rgba(0, 0, 0, 0)'){ctx.fillStyle=bg;ctx.fillRect(0,0,size.width,size.height);}
    const n=31, lo=-2.55, hi=2.55, step=(hi-lo)/(n-1); let peak=-Infinity;
    for(let row=0;row<n;row++) {
      ctx.beginPath();
      for(let col=0;col<n;col++) { const x=lo+col*step,y=lo+row*step,z=field(s,x,y); peak=Math.max(peak,z); const p=project(s,x,y,z,s.w,size.width,size.height); if(col===0)ctx.moveTo(p[0],p[1]); else ctx.lineTo(p[0],p[1]); }
      stroke(ctx,.24,1*size.ratio); ctx.stroke();
    }
    for(let col=0;col<n;col+=2) {
      ctx.beginPath(); for(let row=0;row<n;row++){const x=lo+col*step,y=lo+row*step,z=field(s,x,y);const p=project(s,x,y,z,s.w,size.width,size.height);if(row===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);}
      stroke(ctx,.15,.9*size.ratio);ctx.stroke();
    }
    if(s.contours){for(let ring=1;ring<=4;ring++){ctx.beginPath();for(let a=0;a<=64;a++){const th=a/64*Math.PI*2,r=ring*.5,x=Math.cos(th)*r,y=Math.sin(th)*r,z=field(s,x,y);const p=project(s,x,y,z-.12,s.w,size.width,size.height);if(a===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);}stroke(ctx,.18,.8*size.ratio);ctx.stroke();}}
    if(s.vector){for(let ix=-2;ix<=2;ix++)for(let iy=-2;iy<=2;iy++){const x=ix,y=iy,z=field(s,x,y),eps=.08,gx=(field(s,x+eps,y)-field(s,x-eps,y))/(2*eps),gy=(field(s,x,y+eps)-field(s,x,y-eps))/(2*eps),a=project(s,x,y,z,s.w,size.width,size.height),b=project(s,x+.22*gx,y+.22*gy,z+.10,s.w,size.width,size.height);stroke(ctx,.34,1.15*size.ratio);ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}}
    if(s.uncertainty){ctx.save();ctx.globalAlpha=.08;ctx.fillStyle=getComputedStyle(d.documentElement).color||'#111';for(let i=0;i<45;i++){const x=lo+((i*37)%97)/96*(hi-lo),y=lo+((i*53)%89)/88*(hi-lo),z=field(s,x,y)+.2*Math.sin(i+s.w*4),p=project(s,x,y,z,s.w,size.width,size.height);ctx.beginPath();ctx.arc(p[0],p[1],3.2*size.ratio,0,Math.PI*2);ctx.fill();}ctx.restore();}
    drawTesseract(ctx,s,size);
    ctx.globalAlpha=1;
    const peakNode=one(root,'[data-v0710-metric="peak"]'); if(peakNode) peakNode.textContent=Number.isFinite(peak)?peak.toFixed(2):'—';
    const slice=one(root,'[data-v0710-metric="slice"]'); if(slice) slice.textContent=s.w.toFixed(2);
    const read=one(root,'[data-v0710-readout]'); if(read) read.textContent=(DEMOS[s.demo]||DEMOS.response).label+' · W '+s.w.toFixed(2)+(s.demo==='compute'?' · compute-backed':' · browser rendered');
    const boundary=one(root,'[data-v015207-boundary]'); if(boundary) boundary.textContent=(DEMOS[s.demo]||DEMOS.response).boundary;
  }

  function schedule(root) { w.requestAnimationFrame(function(){ render(root); }); }

  async function getJson(url, opts) {
    const cfg=config(), options=Object.assign({headers:{}},opts||{}); options.headers=Object.assign({},options.headers,{'Accept':'application/json'});
    if(cfg.nonce) options.headers['X-WP-Nonce']=cfg.nonce;
    const response=await fetch(url,options); let body=null; try{body=await response.json();}catch(_){body=null;}
    if(!response.ok) throw new Error(body&&body.message?body.message:'HTTP '+response.status); return body||{};
  }

  function computeLabel(root, text, tone) { const node=one(root,'[data-v0710-compute-state]'); if(node){node.textContent=text;node.dataset.state=tone||'unknown';} }

  async function refreshCompute(root) {
    const s=state(root), cfg=config(); computeLabel(root,'Checking compute','checking');
    try {
      const pair=await Promise.all([getJson(cfg.healthUrl),getJson(cfg.capabilitiesUrl)]);
      const h=pair[0]||{}, c=pair[1]||{}; s.compute.status=h.ok?'ready':'degraded'; s.compute.version=h.version||c.version||null; s.compute.methods=h.methodCount||c.methodCount||null;
      computeLabel(root,h.ok?('Compute ready · '+(s.compute.methods||'?')+' methods'):('Compute '+(h.status||'degraded')),h.ok?'ready':'warning');
      const details=one(root,'[data-v015207-compute-details]'); if(details) details.textContent='Python Core '+(s.compute.version||'—')+' · '+(s.compute.methods||'?')+' registered methods · '+(h.benchmarkCount||'?')+' benchmarks';
      return h;
    } catch (error) { s.compute.status='offline'; computeLabel(root,'Compute unavailable','error'); const details=one(root,'[data-v015207-compute-details]'); if(details) details.textContent=String(error.message||error); return null; }
  }

  async function runComputeSweep(root) {
    const s=state(root), cfg=config(), button=one(root,'[data-v015207-run-compute]'); if(button){button.disabled=true;button.textContent='Computing…';}
    computeLabel(root,'Running parameter sweep','checking');
    try {
      const values=[]; for(let i=0;i<21;i++) values.push(Number((.06+i*.037).toFixed(3)));
      const body=await getJson(cfg.runUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method:'simulation.parameter_sweep',inputs:{model:'logistic_growth',parameter:'rate',values:values,fixed:{initial:10,carryingCapacity:100,time:10}},requested_outputs:['summary','values']})});
      const output=body.output||body.result||body.outputs||body; const rows=Array.isArray(output.rows)?output.rows:(Array.isArray(body.rows)?body.rows:[]);
      if(!rows.length) throw new Error('Compute Core returned no parameter-sweep rows.');
      s.compute.rows=rows.map(function(r){return {parameterValue:finite(r.parameterValue,0),output:finite(r.output,0)};});
      const vals=s.compute.rows.map(r=>r.output);s.compute.min=Math.min.apply(null,vals);s.compute.max=Math.max.apply(null,vals);s.demo='compute';
      const select=one(root,'[data-v015207-demo]'); if(select)select.value='compute';
      computeLabel(root,'Compute-backed surface ready','ready');
      const details=one(root,'[data-v015207-compute-details]'); if(details) details.textContent='Python parameter sweep · '+rows.length+' evaluations · output '+s.compute.min.toFixed(2)+' → '+s.compute.max.toFixed(2);
      schedule(root);
    } catch(error) { computeLabel(root,'Compute run failed','error'); const details=one(root,'[data-v015207-compute-details]'); if(details) details.textContent=String(error.message||error); }
    finally { if(button){button.disabled=false;button.textContent='Run compute sweep';} }
  }

  function exportJson(root) {
    const s=state(root); const payload={schema:'sc-lab-4d-front-door-state/1.0',releaseVersion:VERSION,demo:s.demo,w:s.w,rotation:{xw:s.xw,yw:s.yw,zw:s.zw},layers:{vector:s.vector,uncertainty:s.uncertainty,contours:s.contours,tesseract:s.tesseract},compute:s.compute.rows?{method:'simulation.parameter_sweep',rows:s.compute.rows,minimumOutput:s.compute.min,maximumOutput:s.compute.max}:null,boundary:(DEMOS[s.demo]||DEMOS.response).boundary};
    const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=d.createElement('a');a.href=url;a.download='sustainable-catalyst-lab-4d-state-v015207.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function exportPng(root){const c=one(root,'[data-v0710-canvas]');if(!c)return;const a=d.createElement('a');a.href=c.toDataURL('image/png');a.download='sustainable-catalyst-lab-4d-front-door-v015207.png';a.click();}

  function tick(root, t) { const s=state(root); if(!s.playing){s.raf=0;return;} if(!s.last)s.last=t; const dt=Math.min(.05,(t-s.last)/1000);s.last=t;s.w+=dt*.34;if(s.w>1)s.w=-1;const input=one(root,'[data-v0710-w]');if(input)input.value=String(s.w);render(root);s.raf=w.requestAnimationFrame(function(n){tick(root,n);}); }

  function bind(root) {
    if(!root || root.dataset.v015207Bound==='1')return; root.dataset.v015207Bound='1'; const s=state(root);
    const wInput=one(root,'[data-v0710-w]'),xInput=one(root,'[data-v0710-xw]'),yInput=one(root,'[data-v0710-yw]');
    if(wInput)s.w=finite(wInput.value,.37); if(xInput)s.xw=finite(xInput.value,.34); if(yInput)s.yw=finite(yInput.value,-.22);
    all(root,'[data-v0710-w],[data-v0710-xw],[data-v0710-yw]').forEach(function(input){input.addEventListener('input',function(){s.w=finite(wInput&&wInput.value,s.w);s.xw=finite(xInput&&xInput.value,s.xw);s.yw=finite(yInput&&yInput.value,s.yw);schedule(root);});});
    all(root,'[data-v0710-layer]').forEach(function(button){button.addEventListener('click',function(){const k=button.dataset.v0710Layer;if(k==='vector')s.vector=!s.vector;if(k==='uncertainty')s.uncertainty=!s.uncertainty;if(k==='contours')s.contours=!s.contours;if(k==='tesseract')s.tesseract=!s.tesseract;button.setAttribute('aria-pressed',String(k==='vector'?s.vector:k==='uncertainty'?s.uncertainty:k==='contours'?s.contours:s.tesseract));schedule(root);});});
    const select=one(root,'[data-v015207-demo]'); if(select)select.addEventListener('change',function(){if(select.value==='compute'&&!s.compute.rows){select.value=s.demo;runComputeSweep(root);return;}s.demo=select.value; schedule(root);});
    one(root,'[data-v0710-animate]')?.addEventListener('click',function(event){s.playing=!s.playing;event.currentTarget.setAttribute('aria-pressed',String(s.playing));event.currentTarget.textContent=s.playing?'Pause 4D sweep':'Animate 4D sweep';if(s.playing&&!s.raf){s.last=0;s.raf=w.requestAnimationFrame(function(t){tick(root,t);});}});
    one(root,'[data-v015207-run-compute]')?.addEventListener('click',function(){runComputeSweep(root);});
    one(root,'[data-v015207-refresh-compute]')?.addEventListener('click',function(){refreshCompute(root);});
    one(root,'[data-v015207-export="json"]')?.addEventListener('click',function(){exportJson(root);});
    one(root,'[data-v015207-export="png"]')?.addEventListener('click',function(){exportPng(root);});
    const canvas=one(root,'[data-v0710-canvas]'); if(canvas){canvas.addEventListener('pointermove',function(event){const r=canvas.getBoundingClientRect(),x=((event.clientX-r.left)/Math.max(1,r.width)*5.1-2.55),y=((event.clientY-r.top)/Math.max(1,r.height)*5.1-2.55),z=field(s,x,y),node=one(root,'[data-v0710-pointer]');if(node)node.textContent='x '+x.toFixed(2)+' · y '+y.toFixed(2)+' · response '+z.toFixed(2)+' · w '+s.w.toFixed(2);});}
    if(w.ResizeObserver&&canvas){s.resize=new ResizeObserver(function(){schedule(root);});s.resize.observe(canvas);}
    refreshCompute(root); schedule(root);
  }

  function boot(){all(d,'[data-v0710-visualizer]').forEach(bind);}
  if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
  d.addEventListener('sc-lab:safe-module-opened',function(e){if(e.detail&&e.detail.module==='overview')boot();});
  w.SCLabInteractive4DV015207Runtime=Object.freeze({version:VERSION,runtime:RUNTIME,boot:boot,refreshCompute:refreshCompute,runComputeSweep:runComputeSweep});
})(window, document);
