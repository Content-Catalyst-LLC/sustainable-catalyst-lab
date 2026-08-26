(function(W,D){
'use strict';
const Lab=W.SCLab=W.SCLab||{}, VERSION='0.71.0';
const states=new WeakMap();
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,t)=>a+(b-a)*t;
function qs(root,s){return root?.querySelector(s);}
function qsa(root,s){return Array.from(root?.querySelectorAll(s)||[]);}
function stateFor(root){
  let s=states.get(root);
  if(!s){s={w:0.37,xw:0.34,yw:-0.22,zw:0.12,animate:false,showVector:true,showUncertainty:true,showContours:true,frame:0,lastTs:0,raf:0,resize:null};states.set(root,s);}
  return s;
}
function response(x,y,w){
  const p1=2.18*Math.exp(-(((x+0.8+0.35*w)**2)/1.05+((y-0.25*w)**2)/0.78));
  const p2=1.24*Math.exp(-(((x-1.15+0.18*w)**2)/1.55+((y+0.85-0.2*w)**2)/1.08));
  const saddle=0.28*Math.sin(1.35*x+0.55*w)*Math.cos(1.1*y-0.35*w);
  return 0.36+p1+p2+saddle;
}
function uncertainty(x,y,w){
  return 0.075+0.08*(Math.abs(x)/2.5)+0.055*(Math.abs(y)/2.5)+0.025*Math.abs(w);
}
function project3(x,y,z,cx,cy,scale){return{x:cx+(x-y)*scale*0.64,y:cy+(x+y)*scale*0.27-z*scale*0.74};}
function rotate4(p,s){
  let {x,y,z,w}=p;
  let c=Math.cos(s.xw),sn=Math.sin(s.xw),nx=x*c-w*sn,nw=x*sn+w*c;x=nx;w=nw;
  c=Math.cos(s.yw);sn=Math.sin(s.yw);let ny=y*c-w*sn;nw=y*sn+w*c;y=ny;w=nw;
  c=Math.cos(s.zw);sn=Math.sin(s.zw);let nz=z*c-w*sn;nw=z*sn+w*c;z=nz;w=nw;
  const perspective=2.8/(3.45-w);
  return{x:x*perspective,y:y*perspective,z:z*perspective,w};
}
function drawArrow(ctx,a,b,alpha){
  const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy);if(len<2)return;
  const ux=dx/len,uy=dy/len,head=4;
  ctx.globalAlpha=alpha;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
  ctx.beginPath();ctx.moveTo(b.x,b.y);ctx.lineTo(b.x-head*(ux-uy*.7),b.y-head*(uy+ux*.7));ctx.lineTo(b.x-head*(ux+uy*.7),b.y-head*(uy-ux*.7));ctx.closePath();ctx.fill();ctx.globalAlpha=1;
}
function drawContours(ctx,cx,cy,scale,s){
  if(!s.showContours)return;
  ctx.save();ctx.lineWidth=1;
  const groups=[[-0.8,0,0.85],[1.05,-0.8,0.72]];
  groups.forEach((g,gi)=>{
    for(let i=1;i<=6;i++){
      const center=project3(g[0]+s.w*(gi?-.12:.16),g[1],0,cx,cy,scale);
      ctx.beginPath();ctx.strokeStyle=i%2?'rgba(232,27,35,.56)':'rgba(255,255,255,.18)';
      ctx.ellipse(center.x,center.y,scale*g[2]*i*.17,scale*g[2]*i*.073,-0.38,0,Math.PI*2);ctx.stroke();
    }
  });
  ctx.restore();
}
function drawSurface(ctx,width,height,s){
  const cx=width*.49,cy=height*.72,scale=Math.min(width/7.7,height/4.65);const n=30,range=2.55;
  ctx.save();ctx.lineWidth=0.8;
  const points=[];
  for(let yi=0;yi<=n;yi++){
    const row=[];const y=-range+(2*range*yi/n);
    for(let xi=0;xi<=n;xi++){
      const x=-range+(2*range*xi/n),z=response(x,y,s.w);row.push({x,y,z,p:project3(x,y,z,cx,cy,scale)});
    }points.push(row);
  }
  drawContours(ctx,cx,cy,scale,s);
  for(let yi=n;yi>=0;yi--){
    ctx.beginPath();
    points[yi].forEach((pt,xi)=>{if(xi===0)ctx.moveTo(pt.p.x,pt.p.y);else ctx.lineTo(pt.p.x,pt.p.y);});
    const t=yi/n;ctx.strokeStyle=`rgba(${Math.round(lerp(255,232,t))},${Math.round(lerp(255,28,t*.9))},${Math.round(lerp(255,35,t*.9))},${0.2+0.36*t})`;ctx.stroke();
  }
  for(let xi=0;xi<=n;xi++){
    ctx.beginPath();for(let yi=0;yi<=n;yi++){const p=points[yi][xi].p;if(yi===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);}ctx.strokeStyle='rgba(255,255,255,.16)';ctx.stroke();
  }
  if(s.showUncertainty){
    ctx.lineWidth=2.1;
    for(let yi=2;yi<n;yi+=5){ctx.beginPath();for(let xi=0;xi<=n;xi++){const pt=points[yi][xi],u=uncertainty(pt.x,pt.y,s.w),p=project3(pt.x,pt.y,pt.z+u,cx,cy,scale);if(xi===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);}ctx.strokeStyle='rgba(255,255,255,.10)';ctx.stroke();}
  }
  if(s.showVector){
    ctx.strokeStyle='rgba(255,255,255,.84)';ctx.fillStyle='rgba(255,255,255,.84)';ctx.lineWidth=1;
    for(let yi=3;yi<n;yi+=4){for(let xi=3;xi<n;xi+=4){const pt=points[yi][xi],e=.07,dx=(response(pt.x+e,pt.y,s.w)-response(pt.x-e,pt.y,s.w))/(2*e),dy=(response(pt.x,pt.y+e,s.w)-response(pt.x,pt.y-e,s.w))/(2*e),mag=Math.hypot(dx,dy)||1;const step=.19,a=pt.p,b=project3(pt.x+dx/mag*step,pt.y+dy/mag*step,pt.z+.05,cx,cy,scale);drawArrow(ctx,a,b,.72);}}
  }
  let peak={z:-Infinity,x:0,y:0,p:null};for(const row of points)for(const pt of row)if(pt.z>peak.z)peak=pt;
  ctx.beginPath();ctx.fillStyle='#ff2934';ctx.shadowColor='rgba(255,20,32,.95)';ctx.shadowBlur=16;ctx.arc(peak.p.x,peak.p.y,4.2,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
  ctx.restore();return {peak:peak.z,cx,cy,scale};
}
function drawTesseract(ctx,width,height,s){
  const ox=width*.82,oy=height*.245,sc=Math.min(width,height)*.072,verts=[];
  for(let i=0;i<16;i++)verts.push({x:(i&1)?1:-1,y:(i&2)?1:-1,z:(i&4)?1:-1,w:(i&8)?1:-1});
  const projected=verts.map(v=>{const r=rotate4(v,s),p=project3(r.x,r.y,r.z,ox,oy,sc);return{...p,w:r.w};});
  ctx.save();ctx.lineWidth=1;
  for(let i=0;i<16;i++)for(let bit=0;bit<4;bit++){const j=i^(1<<bit);if(j<i)continue;const a=projected[i],b=projected[j];ctx.strokeStyle=bit===3?'rgba(255,35,45,.68)':'rgba(255,255,255,.24)';ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
  projected.forEach((p,i)=>{ctx.beginPath();ctx.fillStyle=(i&8)?'rgba(255,35,45,.88)':'rgba(255,255,255,.64)';ctx.arc(p.x,p.y,(i&8)?2.4:1.8,0,Math.PI*2);ctx.fill();});
  ctx.font='600 10px ui-monospace,SFMono-Regular,Menlo,monospace';ctx.fillStyle='rgba(255,255,255,.7)';ctx.fillText('4D PROJECTION',ox-sc*1.7,oy-sc*1.7);ctx.fillStyle='rgba(255,45,55,.88)';ctx.fillText(`w = ${s.w.toFixed(2)}`,ox-sc*1.7,oy-sc*1.45);ctx.restore();
}
function drawAxes(ctx,width,height,geom){
  const {cx,cy,scale}=geom;ctx.save();ctx.strokeStyle='rgba(255,255,255,.32)';ctx.fillStyle='rgba(255,255,255,.62)';ctx.lineWidth=1;ctx.font='10px ui-monospace,SFMono-Regular,Menlo,monospace';
  const o=project3(-2.55,-2.55,0,cx,cy,scale),x=project3(2.55,-2.55,0,cx,cy,scale),y=project3(-2.55,2.55,0,cx,cy,scale),z=project3(-2.55,-2.55,2.9,cx,cy,scale);
  [[o,x,'Descriptor 1'],[o,y,'Descriptor 2'],[o,z,'Response']].forEach(([a,b,label])=>{ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();ctx.fillText(label,b.x+(label==='Descriptor 2'?-68:6),b.y+(label==='Response'?-6:13));});ctx.restore();
}
function fitCanvas(canvas){const rect=canvas.getBoundingClientRect(),dpr=Math.min(2,W.devicePixelRatio||1),w=Math.max(320,Math.round(rect.width*dpr)),h=Math.max(260,Math.round(rect.height*dpr));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}return{width:w,height:h,dpr};}
function render(root){
  const canvas=qs(root,'[data-v0710-canvas]');if(!canvas)return;const s=stateFor(root),size=fitCanvas(canvas),ctx=canvas.getContext('2d');if(!ctx)return;const {width,height}=size;
  ctx.clearRect(0,0,width,height);const g=ctx.createLinearGradient(0,0,0,height);g.addColorStop(0,'#050607');g.addColorStop(1,'#0b0c0e');ctx.fillStyle=g;ctx.fillRect(0,0,width,height);
  ctx.save();ctx.strokeStyle='rgba(255,255,255,.055)';ctx.lineWidth=1;for(let x=0;x<width;x+=Math.max(24,width/32)){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,height);ctx.stroke();}for(let y=0;y<height;y+=Math.max(24,height/20)){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(width,y);ctx.stroke();}ctx.restore();
  const geom=drawSurface(ctx,width,height,s);drawAxes(ctx,width,height,geom);drawTesseract(ctx,width,height,s);
  const peak=qs(root,'[data-v0710-metric="peak"]'),slice=qs(root,'[data-v0710-metric="slice"]');if(peak)peak.textContent=geom.peak.toFixed(2);if(slice)slice.textContent=s.w.toFixed(2);
  const readout=qs(root,'[data-v0710-readout]');if(readout)readout.textContent=`Projected 4D response field · w ${s.w.toFixed(2)} · XW ${(s.xw*180/Math.PI).toFixed(0)}° · YW ${(s.yw*180/Math.PI).toFixed(0)}°`;
}
function computeState(root){
  const node=qs(root,'[data-v0710-compute-state]');if(!node)return;let b='unknown';try{b=W.SCLabProductionV0266?.status?.().backend||'unknown';}catch(_){b='unknown';}
  const map={online:'Compute online',unavailable:'Compute reconnecting',offline:'Browser offline',not_configured:'Browser visualization only',unknown:'Checking compute'};node.textContent=map[b]||'Checking compute';node.dataset.state=b;
}
function tick(root,ts){const s=stateFor(root);if(!s.animate){s.raf=0;return;}if(!s.lastTs)s.lastTs=ts;const dt=Math.min(50,ts-s.lastTs);s.lastTs=ts;s.w=Math.sin(ts/2400)*.92;const input=qs(root,'[data-v0710-w]');if(input)input.value=String(s.w);render(root);s.raf=W.requestAnimationFrame(t=>tick(root,t));}
function schedule(root){W.requestAnimationFrame(()=>render(root));}
function bind(root){
  if(!root||root.dataset.v0710Mounted==='1')return;root.dataset.v0710Mounted='1';const s=stateFor(root);
  const canvas=qs(root,'[data-v0710-canvas]');
  qsa(root,'[data-v0710-w],[data-v0710-xw],[data-v0710-yw]').forEach(input=>input.addEventListener('input',()=>{s.w=Number(qs(root,'[data-v0710-w]')?.value||s.w);s.xw=Number(qs(root,'[data-v0710-xw]')?.value||s.xw);s.yw=Number(qs(root,'[data-v0710-yw]')?.value||s.yw);schedule(root);}));
  qsa(root,'[data-v0710-layer]').forEach(button=>button.addEventListener('click',()=>{const key=button.dataset.v0710Layer;if(key==='vector')s.showVector=!s.showVector;if(key==='uncertainty')s.showUncertainty=!s.showUncertainty;if(key==='contours')s.showContours=!s.showContours;button.setAttribute('aria-pressed',String(key==='vector'?s.showVector:key==='uncertainty'?s.showUncertainty:s.showContours));schedule(root);}));
  qs(root,'[data-v0710-animate]')?.addEventListener('click',event=>{s.animate=!s.animate;event.currentTarget.setAttribute('aria-pressed',String(s.animate));event.currentTarget.textContent=s.animate?'Pause 4D sweep':'Animate 4D sweep';if(s.animate&&!s.raf)s.raf=W.requestAnimationFrame(t=>tick(root,t));});
  canvas?.addEventListener('pointermove',event=>{const r=canvas.getBoundingClientRect(),x=((event.clientX-r.left)/r.width*5.1-2.55),y=((event.clientY-r.top)/r.height*5.1-2.55),node=qs(root,'[data-v0710-pointer]');if(node)node.textContent=`x ${x.toFixed(2)} · y ${y.toFixed(2)} · response ${response(x,y,s.w).toFixed(2)}`;});
  s.resize=new ResizeObserver(()=>schedule(root));if(canvas)s.resize.observe(canvas);schedule(root);computeState(root);W.setInterval(()=>computeState(root),5000);
}
function boot(){D.querySelectorAll('[data-v0710-visualizer]').forEach(bind);}
if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
D.addEventListener('sc-lab:app-ready',boot);W.addEventListener('pageshow',boot);
Lab.AdvancedVisualizationFrontDoorV0710={version:VERSION,boot,render,response,uncertainty,status:()=>({version:VERSION,browserRendered:true,dimensions:4,computeRequired:false})};
})(window,document);
