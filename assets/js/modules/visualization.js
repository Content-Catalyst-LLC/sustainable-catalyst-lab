(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const PREF_KEY = 'scLabVisualizationPrefsV092';
  const HANDOFF_KEY = 'scLabDecisionStudioHandoffV2';
  const VERSION = '0.14.0';

  const themes = {
    scientific: { label:'Scientific Light', bg:'#ffffff', panel:'#f6f7f8', text:'#111820', muted:'#59636d', grid:'#d9dee3', axis:'#2d363e', colors:['#c60000','#1f5c78','#5a6d2a','#805a82','#b36b16','#27746a'] },
    institutional: { label:'Institutional', bg:'#fbfaf7', panel:'#f0eee8', text:'#0a0a0a', muted:'#57534e', grid:'#d7d2c8', axis:'#151515', colors:['#d00000','#202020','#6c7177','#8b2f2f','#44636f','#7c6441'] },
    publication: { label:'Publication', bg:'#ffffff', panel:'#ffffff', text:'#111111', muted:'#444444', grid:'#dddddd', axis:'#111111', colors:['#111111','#555555','#888888','#bbbbbb','#333333','#777777'] },
    dark: { label:'Scientific Dark', bg:'#101418', panel:'#171d22', text:'#f5f7f8', muted:'#aab3bb', grid:'#313b44', axis:'#dce3e8', colors:['#ff4d4d','#58a6c8','#a2c66c','#c495c7','#f1a64b','#5dc2b0'] },
    accessible: { label:'Accessibility', bg:'#ffffff', panel:'#f7f7f7', text:'#111111', muted:'#4b4b4b', grid:'#d0d0d0', axis:'#111111', colors:['#0072b2','#d55e00','#009e73','#cc79a7','#e69f00','#56b4e9'] }
  };

  function safeParse(value) {
    if (value && typeof value === 'object') return value;
    const text = String(value || '').trim();
    if (!text || /^Error:/i.test(text)) return null;
    try { return JSON.parse(text); } catch (_) { return { value:text }; }
  }
  function number(value) { const n=Number(value); return Number.isFinite(n) ? n : null; }
  function numericEntries(value, prefix='', depth=0, out=[]) {
    if (!value || depth > 2 || out.length >= 18) return out;
    if (Array.isArray(value)) return out;
    Object.entries(value).forEach(([key, val]) => {
      if (key.startsWith('_') || ['series','points','trajectory','curve','history','records','validation'].includes(key)) return;
      const label = prefix ? `${prefix}.${key}` : key;
      const n=number(val);
      if (n !== null) out.push({ label, value:n });
      else if (val && typeof val === 'object') numericEntries(val,label,depth+1,out);
    });
    return out;
  }
  function findSeries(value, path='', depth=0) {
    if (!value || depth > 4) return null;
    if (Array.isArray(value) && value.length >= 2) {
      if (value.every(item => typeof item === 'number' && Number.isFinite(item))) {
        return { path, rows:value.map((y,i)=>({x:i,y:Number(y)})), xKey:'x', yKeys:['y'] };
      }
      if (value.every(item => item && typeof item === 'object')) {
        const keys=[...new Set(value.flatMap(item=>Object.keys(item)))];
        const numericKeys=keys.filter(key=>value.filter(item=>number(item[key])!==null).length>=Math.max(2,Math.floor(value.length*0.65)));
        if (numericKeys.length >= 2) {
          const xKey=numericKeys[0], yKeys=numericKeys.slice(1,5);
          return { path, rows:value.map(item=>Object.fromEntries([xKey,...yKeys].map(k=>[k,number(item[k])]))), xKey, yKeys };
        }
      }
    }
    if (typeof value === 'object') {
      const preferred=['series','points','trajectory','curve','profile','samples','data','rows'];
      for (const key of preferred) if (key in value) { const found=findSeries(value[key],path?`${path}.${key}`:key,depth+1); if(found)return found; }
      for (const [key,val] of Object.entries(value)) { const found=findSeries(val,path?`${path}.${key}`:key,depth+1); if(found)return found; }
    }
    return null;
  }
  function slug(text) { return String(text || 'analysis').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,80) || 'analysis'; }
  function selectedTheme(name) { return themes[name] || themes.scientific; }
  function loadPrefs() {
    try { return Object.assign({theme:'scientific',chartType:'auto',aspect:'16:9',showGrid:true,showLegend:true},JSON.parse(localStorage.getItem(PREF_KEY)||'{}')); }
    catch (_) { return {theme:'scientific',chartType:'auto',aspect:'16:9',showGrid:true,showLegend:true}; }
  }
  function savePrefs(prefs) { localStorage.setItem(PREF_KEY,JSON.stringify(prefs)); }

  function makeContract(payload={}) {
    const outputs=safeParse(payload.outputs) || {};
    const project=payload.project || null;
    const contract={
      schema:'sc-lab-analysis/1.0', schemaVersion:'1.0', id:payload.id||U.uid('analysis'),
      methodId:payload.methodId||'unclassified.analysis', methodVersion:payload.methodVersion||VERSION,
      title:payload.title||'Scientific analysis', subtitle:payload.subtitle||'', domain:payload.domain||'scientific-analysis',
      createdAt:payload.createdAt||U.now(), status:payload.status||outputs?._validation?.status||payload.validation?.status||'unreviewed',
      inputs:payload.inputs||{}, outputs, equation:payload.equation||'', assumptions:payload.assumptions||[],
      warnings:payload.warnings||outputs?._validation?.warnings||payload.validation?.warnings||[],
      validation:payload.validation||outputs?._validation||null, sources:payload.sources||[],
      project:project?{id:project.id,name:project.name,schemaVersion:project.schemaVersion}:null,
      sourceModule:payload.sourceModule||payload.domain||'lab', sourceCollection:payload.sourceCollection||'calculations',
      chartSpec:null, sceneSpec:payload.sceneSpec||null, svg:payload.svg||'', audit:{}
    };
    contract.chartSpec=inferChartSpec(contract,payload.chartType||'auto');
    contract.audit={application:'Sustainable Catalyst Lab',applicationVersion:VERSION,contractVersion:'1.0',inputFingerprint:U.fingerprint(contract.inputs),outputFingerprint:U.fingerprint(contract.outputs),chartFingerprint:U.fingerprint(contract.chartSpec),generatedAt:contract.createdAt};
    return contract;
  }

  function inferChartSpec(contract, preferred='auto') {
    const series=findSeries(contract.outputs);
    const scalars=numericEntries(contract.outputs);
    let type=preferred;
    if (type==='auto') type=series?'line':scalars.length?'bar':'summary';
    if (series) return { version:'1.0',type,title:contract.title,subtitle:contract.subtitle,xKey:series.xKey,yKeys:series.yKeys,data:series.rows,sourcePath:series.path,xLabel:series.xKey,yLabel:series.yKeys.join(' / '),theme:'scientific' };
    if (scalars.length) return { version:'1.0',type:type==='line'?'bar':type,title:contract.title,subtitle:contract.subtitle,xKey:'label',yKeys:['value'],data:scalars,xLabel:'Result',yLabel:'Value',theme:'scientific' };
    return { version:'1.0',type:'summary',title:contract.title,subtitle:contract.subtitle,data:[],theme:'scientific' };
  }

  function escXml(value){return U.esc(value);}
  function nice(value){
    const n=Number(value); if(!Number.isFinite(n))return String(value??'');
    const a=Math.abs(n); if((a>=1e5)||(a>0&&a<1e-3))return n.toExponential(3);
    return Number(n.toPrecision(6)).toLocaleString(undefined,{maximumFractionDigits:6});
  }
  function dimensions(aspect='16:9') { const map={'16:9':[960,540],'4:3':[900,675],'1:1':[760,760],'3:2':[900,600]}; return map[aspect]||map['16:9']; }
  function range(values){const nums=values.filter(Number.isFinite);if(!nums.length)return[0,1];let min=Math.min(...nums),max=Math.max(...nums);if(min===max){const p=Math.abs(min||1)*0.15;min-=p;max+=p;}const pad=(max-min)*0.08;return[min-pad,max+pad];}
  function pathFor(rows,xKey,yKey,xScale,yScale){return rows.map((r,i)=>`${i?'L':'M'} ${xScale(number(r[xKey])??i).toFixed(2)} ${yScale(number(r[yKey])??0).toFixed(2)}`).join(' ');}

  function renderSVG(spec, options={}) {
    const prefs=Object.assign(loadPrefs(),options); const theme=selectedTheme(prefs.theme||spec.theme); const [W,H]=dimensions(prefs.aspect);
    const m={l:84,r:34,t:92,b:72}; const iw=W-m.l-m.r, ih=H-m.t-m.b;
    const title=options.title||spec.title||'Scientific analysis'; const subtitle=options.subtitle??spec.subtitle??'';
    const data=Array.isArray(spec.data)?spec.data:[]; const xKey=spec.xKey||'x'; const yKeys=(spec.yKeys||['y']).slice(0,6);
    const footer=`Sustainable Catalyst Lab v${VERSION} · ${new Date().toISOString().slice(0,10)}`;
    if(spec.type==='summary'||!data.length){return `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="chart-title chart-desc" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><title id="chart-title">${escXml(title)}</title><desc id="chart-desc">Structured scientific result without a numeric plotting series.</desc><rect width="100%" height="100%" fill="${theme.bg}"/><text x="48" y="70" font-family="system-ui,sans-serif" font-size="28" font-weight="700" fill="${theme.text}">${escXml(title)}</text><text x="48" y="104" font-family="system-ui,sans-serif" font-size="15" fill="${theme.muted}">${escXml(subtitle)}</text><rect x="48" y="145" width="${W-96}" height="${H-230}" rx="8" fill="${theme.panel}" stroke="${theme.grid}"/><text x="${W/2}" y="${H/2}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="16" fill="${theme.muted}">No numeric series detected. Export the structured JSON or table.</text><text x="48" y="${H-30}" font-family="ui-monospace,monospace" font-size="11" fill="${theme.muted}">${escXml(footer)}</text></svg>`;}
    if(spec.type==='bar'){
      const rows=data.slice(0,16);const vals=rows.map(r=>number(r[yKeys[0]])||0);const [y0,y1]=range([0,...vals]);const yScale=v=>m.t+ih-(v-y0)/(y1-y0)*ih;const bw=Math.max(8,iw/rows.length*0.62);const step=iw/rows.length;
      const grid=prefs.showGrid!==false?[0,.25,.5,.75,1].map(t=>{const y=m.t+ih*t,val=y1-(y1-y0)*t;return `<line x1="${m.l}" y1="${y}" x2="${W-m.r}" y2="${y}" stroke="${theme.grid}"/><text x="${m.l-12}" y="${y+4}" text-anchor="end" font-family="ui-monospace,monospace" font-size="11" fill="${theme.muted}">${escXml(nice(val))}</text>`}).join(''):'';
      const bars=rows.map((r,i)=>{const val=vals[i],x=m.l+i*step+(step-bw)/2,y=yScale(Math.max(0,val)),zero=yScale(0),h=Math.max(1,Math.abs(zero-y));const yy=val>=0?y:zero;const label=String(r[xKey]??i);return `<g><rect x="${x}" y="${yy}" width="${bw}" height="${h}" rx="3" fill="${theme.colors[i%theme.colors.length]}"/><title>${escXml(label)}: ${escXml(nice(val))}</title><text transform="translate(${x+bw/2} ${H-m.b+14}) rotate(-35)" text-anchor="end" font-family="system-ui,sans-serif" font-size="10" fill="${theme.muted}">${escXml(label.slice(0,24))}</text></g>`}).join('');
      return `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="chart-title chart-desc" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><title id="chart-title">${escXml(title)}</title><desc id="chart-desc">Bar chart of numeric calculation outputs.</desc><rect width="100%" height="100%" fill="${theme.bg}"/><text x="${m.l}" y="42" font-family="system-ui,sans-serif" font-size="26" font-weight="700" fill="${theme.text}">${escXml(title)}</text><text x="${m.l}" y="68" font-family="system-ui,sans-serif" font-size="14" fill="${theme.muted}">${escXml(subtitle)}</text>${grid}<line x1="${m.l}" y1="${yScale(0)}" x2="${W-m.r}" y2="${yScale(0)}" stroke="${theme.axis}"/>${bars}<text x="${W/2}" y="${H-12}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="11" fill="${theme.muted}">${escXml(footer)}</text></svg>`;
    }
    const rows=data.filter(r=>number(r[xKey])!==null);const xs=rows.map(r=>number(r[xKey]));const ys=rows.flatMap(r=>yKeys.map(k=>number(r[k])).filter(v=>v!==null));const [x0,x1]=range(xs.length?xs:rows.map((_,i)=>i));const [y0,y1]=range(ys);const xScale=v=>m.l+(v-x0)/(x1-x0)*iw;const yScale=v=>m.t+ih-(v-y0)/(y1-y0)*ih;
    const grid=prefs.showGrid!==false?[0,.25,.5,.75,1].map(t=>{const x=m.l+iw*t,y=m.t+ih*t;return `<line x1="${x}" y1="${m.t}" x2="${x}" y2="${m.t+ih}" stroke="${theme.grid}"/><line x1="${m.l}" y1="${y}" x2="${m.l+iw}" y2="${y}" stroke="${theme.grid}"/><text x="${x}" y="${m.t+ih+20}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="11" fill="${theme.muted}">${escXml(nice(x0+(x1-x0)*t))}</text><text x="${m.l-12}" y="${y+4}" text-anchor="end" font-family="ui-monospace,monospace" font-size="11" fill="${theme.muted}">${escXml(nice(y1-(y1-y0)*t))}</text>`}).join(''):'';
    const marks=yKeys.map((key,si)=>{const color=theme.colors[si%theme.colors.length];if(spec.type==='scatter')return rows.map((r,i)=>`<circle cx="${xScale(number(r[xKey])??i)}" cy="${yScale(number(r[key])??0)}" r="4" fill="${color}"><title>${escXml(key)}: ${escXml(nice(r[key]))}</title></circle>`).join('');return `<path d="${pathFor(rows,xKey,key,xScale,yScale)}" fill="none" stroke="${color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>${rows.length<=80?rows.map((r,i)=>`<circle cx="${xScale(number(r[xKey])??i)}" cy="${yScale(number(r[key])??0)}" r="2.5" fill="${color}"/>`).join(''):''}`}).join('');
    const legend=prefs.showLegend!==false?yKeys.map((key,i)=>`<g transform="translate(${m.l+i*150} 78)"><line x1="0" y1="0" x2="22" y2="0" stroke="${theme.colors[i%theme.colors.length]}" stroke-width="4"/><text x="29" y="4" font-family="system-ui,sans-serif" font-size="12" fill="${theme.text}">${escXml(key)}</text></g>`).join(''):'';
    return `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="chart-title chart-desc" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><title id="chart-title">${escXml(title)}</title><desc id="chart-desc">${escXml(spec.type)} chart generated from a Sustainable Catalyst Lab analysis.</desc><rect width="100%" height="100%" fill="${theme.bg}"/><text x="${m.l}" y="42" font-family="system-ui,sans-serif" font-size="26" font-weight="700" fill="${theme.text}">${escXml(title)}</text><text x="${m.l}" y="64" font-family="system-ui,sans-serif" font-size="14" fill="${theme.muted}">${escXml(subtitle)}</text>${legend}${grid}<line x1="${m.l}" y1="${m.t+ih}" x2="${m.l+iw}" y2="${m.t+ih}" stroke="${theme.axis}"/><line x1="${m.l}" y1="${m.t}" x2="${m.l}" y2="${m.t+ih}" stroke="${theme.axis}"/>${marks}<text x="${m.l+iw/2}" y="${H-34}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="${theme.muted}">${escXml(spec.xLabel||xKey)}</text><text transform="translate(22 ${m.t+ih/2}) rotate(-90)" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="${theme.muted}">${escXml(spec.yLabel||yKeys.join(' / '))}</text><text x="${W/2}" y="${H-12}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="11" fill="${theme.muted}">${escXml(footer)}</text></svg>`;
  }

  function csv(contract) {
    const spec=contract.chartSpec||{};const rows=spec.data||[];
    if(rows.length){const keys=[...new Set(rows.flatMap(r=>Object.keys(r)))];return [keys.join(','),...rows.map(r=>keys.map(k=>{const s=String(r[k]??'');return /[",\n]/.test(s)?`"${s.replace(/"/g,'""')}"`:s}).join(','))].join('\n');}
    const entries=numericEntries(contract.outputs);return ['metric,value',...entries.map(r=>`"${r.label.replace(/"/g,'""')}",${r.value}`)].join('\n');
  }
  function analysisPackageEntries(contract,svg){
    const packet=analysisPacket(contract,svg);
    const entries={
      'analysis.json':JSON.stringify(contract,null,2),
      'chart.svg':svg,
      'chart-data.csv':csv(contract),
      'audit.json':JSON.stringify(contract.audit||{},null,2),
      'decision-studio-packet.json':JSON.stringify(packet,null,2),
      'README.md':`# ${contract.title}\n\nGenerated by Sustainable Catalyst Lab v${VERSION}.\n\nMethod: ${contract.methodId}\nStatus: ${contract.status}\nCreated: ${contract.createdAt}\n\nThe archive preserves the structured analysis, source chart, data table, audit metadata, and Decision Studio handoff packet.\n`
    };
    if(contract.sceneSpec)entries['scene.json']=JSON.stringify(contract.sceneSpec,null,2);
    return entries;
  }
  async function exportPackage(contract,svg,filename){
    if(!Lab.DataManagement?.makeZip)throw new Error('Workspace packaging engine is unavailable.');
    const entries=analysisPackageEntries(contract,svg);
    const canvas=await svgToCanvas(svg,2);
    const pngBlob=await new Promise((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(new Error('PNG export failed.')),'image/png'));
    entries['chart.png']=new Uint8Array(await pngBlob.arrayBuffer());
    entries['analysis.pdf']=makeJpegPdf(canvas.toDataURL('image/jpeg',0.92),canvas.width,canvas.height,contract.title);
    const bytes=Lab.DataManagement.makeZip(entries);
    downloadBinary(filename||`${slug(contract.title)}-analysis-package.zip`,bytes,'application/zip');
    return bytes;
  }
  function downloadBlob(name,blob){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},50);}
  function downloadBinary(name,bytes,type){downloadBlob(name,new Blob([bytes],{type}));}
  function exportSvg(contract,svg,filename){U.download(filename||`${slug(contract.title)}.svg`,svg,'image/svg+xml');}
  function svgToCanvas(svg,scale=2,bg='#ffffff'){
    return new Promise((resolve,reject)=>{const img=new Image();const blob=new Blob([svg],{type:'image/svg+xml'});const url=URL.createObjectURL(blob);img.onload=()=>{try{const canvas=document.createElement('canvas');canvas.width=Math.max(1,img.naturalWidth||960)*scale;canvas.height=Math.max(1,img.naturalHeight||540)*scale;const ctx=canvas.getContext('2d');ctx.fillStyle=bg;ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0,canvas.width,canvas.height);URL.revokeObjectURL(url);resolve(canvas);}catch(e){reject(e);}};img.onerror=()=>{URL.revokeObjectURL(url);reject(new Error('The SVG could not be rasterized.'));};img.src=url;});
  }
  async function exportPng(contract,svg,filename,scale=2){const canvas=await svgToCanvas(svg,scale);canvas.toBlob(blob=>downloadBlob(filename||`${slug(contract.title)}.png`,blob),'image/png');}
  function pdfEscape(text){return String(text).replace(/\\/g,'\\\\').replace(/\(/g,'\\(').replace(/\)/g,'\\)');}
  function makeJpegPdf(jpegDataUrl,width,height,title){
    const binary=atob(jpegDataUrl.split(',')[1]);const jpg=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)jpg[i]=binary.charCodeAt(i);
    const pageW=792,pageH=612,margin=36,head=48;const maxW=pageW-margin*2,maxH=pageH-margin*2-head;const scale=Math.min(maxW/width,maxH/height);const drawW=width*scale,drawH=height*scale,x=(pageW-drawW)/2,y=margin;
    const objects=[];const add=s=>{objects.push(typeof s==='string'?new TextEncoder().encode(s):s);return objects.length;};
    add('<< /Type /Catalog /Pages 2 0 R >>');
    add('<< /Type /Pages /Kids [3 0 R] /Count 1 >>');
    add('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 792 612] /Resources << /XObject << /Im0 5 0 R >> /Font << /F1 6 0 R >> >> /Contents 4 0 R >>');
    const content=`BT /F1 18 Tf 36 576 Td (${pdfEscape(title)}) Tj ET\nq ${drawW.toFixed(2)} 0 0 ${drawH.toFixed(2)} ${x.toFixed(2)} ${y.toFixed(2)} cm /Im0 Do Q`;
    add(`<< /Length ${content.length} >>\nstream\n${content}\nendstream`);
    const imageHead=new TextEncoder().encode(`<< /Type /XObject /Subtype /Image /Width ${width} /Height ${height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpg.length} >>\nstream\n`);const imageTail=new TextEncoder().encode('\nendstream');const image=new Uint8Array(imageHead.length+jpg.length+imageTail.length);image.set(imageHead);image.set(jpg,imageHead.length);image.set(imageTail,imageHead.length+jpg.length);add(image);
    add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>');
    const header=new TextEncoder().encode('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');let size=header.length;const offsets=[0];objects.forEach((obj,i)=>{offsets.push(size);size+=new TextEncoder().encode(`${i+1} 0 obj\n`).length+obj.length+new TextEncoder().encode('\nendobj\n').length;});const xrefOffset=size;let xref=`xref\n0 ${objects.length+1}\n0000000000 65535 f \n`;for(let i=1;i<offsets.length;i++)xref+=String(offsets[i]).padStart(10,'0')+' 00000 n \n';const trailer=`trailer\n<< /Size ${objects.length+1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
    const tail=new TextEncoder().encode(xref+trailer);const out=new Uint8Array(size+tail.length);let pos=0;out.set(header,pos);pos+=header.length;objects.forEach((obj,i)=>{const h=new TextEncoder().encode(`${i+1} 0 obj\n`),f=new TextEncoder().encode('\nendobj\n');out.set(h,pos);pos+=h.length;out.set(obj,pos);pos+=obj.length;out.set(f,pos);pos+=f.length;});out.set(tail,pos);return out;
  }
  async function exportPdf(contract,svg,filename){const canvas=await svgToCanvas(svg,2);const data=canvas.toDataURL('image/jpeg',0.92);const pdf=makeJpegPdf(data,canvas.width,canvas.height,contract.title);downloadBinary(filename||`${slug(contract.title)}.pdf`,pdf,'application/pdf');}
  function analysisPacket(contract,svg){if(Lab.Reporting?.makeReport&&Lab.Reporting?.makeDecisionStudioPacket){const report=Lab.Reporting.makeReport({title:contract.title,subtitle:contract.subtitle,reportType:'technical-report',project:contract.project,analyses:[Object.assign({},contract,{svg})]});const packet=Lab.Reporting.makeDecisionStudioPacket(report);packet.packetType='scientific-analysis';return packet;}return {packetType:'scientific-analysis',schemaVersion:'2.0',origin:{application:'Sustainable Catalyst Lab',version:VERSION},createdAt:U.now(),project:contract.project,report:{title:contract.title,reportType:'technical-report'},analysis:contract,analyses:[contract],charts:contract.sceneSpec?[]:[{chartId:contract.chartSpec?.id||`${contract.id}-chart`,title:contract.title,chartSpec:contract.chartSpec,svg,data:contract.chartSpec?.data||[],caption:contract.subtitle||`Generated from ${contract.methodId}.`,methodId:contract.methodId,validationState:contract.status}],scenes:contract.sceneSpec?[Lab.DimensionalVisualization?.scenePacket(contract.sceneSpec,svg,contract)||{sceneSpec:contract.sceneSpec,svg}]:[],tables:[],claims:[],assumptions:contract.assumptions,uncertainties:[],warnings:contract.warnings,evidence:[],sources:contract.sources,codeRuntimes:[],validationRecords:contract.validation?[contract.validation]:[],audit:contract.audit};}

  function inputsFrom(container){const out={};container.querySelectorAll('input,select,textarea').forEach((el,i)=>{if(el.type==='file'||el.type==='button'||el.type==='submit')return;const key=Object.entries(el.dataset||{}).find(([k])=>/Field$/.test(k))?.[1]||el.name||el.id||el.closest('label')?.textContent?.trim().slice(0,80)||`input${i+1}`;out[key]=el.type==='checkbox'?el.checked:el.value;});return out;}
  function dataId(container){const pairs=Object.entries(container.dataset||{});const pair=pairs.find(([k])=>/Tool$/.test(k));return pair?pair[1]:container.dataset.calculatorId||slug(container.querySelector('h4,h3')?.textContent||'analysis');}
  function findContainer(button){return button.closest('[data-energy-tool],[data-earth-tool],[data-materials-tool],[data-astronomy-tool],[data-biology-tool],[data-physics-tool],.sc-lab-calculator-form,.sc-lab-tool')||button.closest('[data-analysis-pane="spectrometry"],[data-lab-module]');}
  function outputFrom(container){const candidates=[...container.querySelectorAll('pre,[data-calc-result],[data-spectrum-output]')].filter(el=>el.textContent.trim()&&!/^Ready\.?$/i.test(el.textContent.trim()));for(const el of candidates){const p=safeParse(el.textContent);if(p)return p;}return null;}
  function equationFrom(container){return container.querySelector('details code,.sc-lab-equation code,code')?.textContent?.trim()||'';}
  function assumptionsFrom(container){return [...container.querySelectorAll('details li')].map(li=>li.textContent.trim()).filter(Boolean);}
  function existingSvg(container){return container.querySelector('.sc-lab-chart svg,[data-spectrum-chart] svg,svg')?.outerHTML||'';}

  function toolbarHtml(){return `<div class="sc-lab-universal-export" data-universal-export><span>VISUALIZE / EXPORT</span><button type="button" data-viz-open>Studio</button><button type="button" data-viz-scene>3D/4D</button><button type="button" data-viz-code>Code</button><button type="button" data-viz-report>Report</button><button type="button" data-viz-svg>SVG</button><button type="button" data-viz-png>PNG</button><button type="button" data-viz-pdf>PDF</button><button type="button" data-viz-csv>CSV</button><button type="button" data-viz-json>JSON</button><button type="button" data-viz-package>Package</button><button type="button" data-viz-handoff>Decision Studio</button></div>`;}
  function attachToolbar(root,projects,container,contract){
    let toolbar=container.querySelector(':scope > [data-universal-export]');if(!toolbar){container.insertAdjacentHTML('beforeend',toolbarHtml());toolbar=container.querySelector(':scope > [data-universal-export]');}
    container._scLabContract=contract;
    const current=()=>container._scLabContract;const svg=()=>renderSVG(current().chartSpec,Object.assign(loadPrefs(),{title:current().title,subtitle:current().subtitle}));
    toolbar.querySelector('[data-viz-open]').onclick=()=>{root._scLabLatestResult=current();root.dispatchEvent(new CustomEvent('sc-lab:open-visualization',{detail:current()}));};
    toolbar.querySelector('[data-viz-scene]').onclick=()=>{root._scLabLatestResult=current();root.dispatchEvent(new CustomEvent('sc-lab:open-visualization',{detail:current()}));setTimeout(()=>root.dispatchEvent(new CustomEvent('sc-lab:dimensional-contract',{detail:current()})),30);};
    toolbar.querySelector('[data-viz-code]').onclick=()=>{root._scLabLatestResult=current();root.dispatchEvent(new CustomEvent('sc-lab:open-code',{detail:current()}));};
    toolbar.querySelector('[data-viz-report]').onclick=()=>{root._scLabLatestResult=current();root.dispatchEvent(new CustomEvent('sc-lab:open-report',{detail:current()}));};
    toolbar.querySelector('[data-viz-svg]').onclick=()=>exportSvg(current(),svg());
    toolbar.querySelector('[data-viz-png]').onclick=()=>exportPng(current(),svg()).catch(e=>U.toast(root,e.message));
    toolbar.querySelector('[data-viz-pdf]').onclick=()=>exportPdf(current(),svg()).catch(e=>U.toast(root,e.message));
    toolbar.querySelector('[data-viz-csv]').onclick=()=>U.download(`${slug(current().title)}.csv`,csv(current()),'text/csv');
    toolbar.querySelector('[data-viz-json]').onclick=()=>U.download(`${slug(current().title)}-analysis.json`,JSON.stringify(current(),null,2),'application/json');
    toolbar.querySelector('[data-viz-package]').onclick=()=>exportPackage(current(),svg()).catch(e=>U.toast(root,e.message));
    toolbar.querySelector('[data-viz-handoff]').onclick=()=>handoff(root,projects,current(),svg());
  }
  function capture(root,projects,button){
    const container=findContainer(button);if(!container)return null;const outputs=outputFrom(container);if(!outputs)return null;
    const panel=container.closest('[data-lab-module]');const title=container.querySelector('h4,h3')?.textContent?.trim()||button.textContent.trim()||'Scientific analysis';
    const contract=makeContract({methodId:dataId(container),title,domain:panel?.dataset.labModule||'lab',sourceModule:panel?.dataset.labModule||'lab',inputs:inputsFrom(container),outputs,equation:equationFrom(container),assumptions:assumptionsFrom(container),svg:existingSvg(container),project:projects.get()});
    root._scLabLatestResult=contract;attachToolbar(root,projects,container,contract);refreshStudio(root,projects,contract);return contract;
  }
  function shouldCapture(button){return button.matches('[data-calc-run],[data-formula-run],[data-percent-run],[data-empirical-run],[data-molecular-run],[data-balance-run],[data-limit-run],[data-yield-run],[data-spectrum-load],[data-spectrum-peaks],[data-spectrum-baseline],[data-spectrum-smooth],[data-spectrum-normalize],[data-spectrum-derivative],[data-spectrum-convert]')||Object.keys(button.dataset||{}).some(k=>/Run$/.test(k));}

  function studioElements(root){return {status:root.querySelector('[data-viz-status]'),title:root.querySelector('[data-viz-title]'),subtitle:root.querySelector('[data-viz-subtitle]'),type:root.querySelector('[data-viz-type]'),theme:root.querySelector('[data-viz-theme]'),aspect:root.querySelector('[data-viz-aspect]'),grid:root.querySelector('[data-viz-grid]'),legend:root.querySelector('[data-viz-legend]'),chart:root.querySelector('[data-viz-chart]'),meta:root.querySelector('[data-viz-meta]')};}
  function refreshStudio(root,projects,contract=root._scLabLatestResult){const el=studioElements(root);if(!el.chart)return;if(!contract){el.status.textContent='Run any calculation to create a visualization-ready result.';el.chart.innerHTML='<div class="sc-lab-data-note">No analysis has been captured yet.</div>';return;}const prefs=loadPrefs();el.title.value=contract.title;el.subtitle.value=contract.subtitle||'';el.type.value=contract.chartSpec?.type||'auto';el.theme.value=prefs.theme;el.aspect.value=prefs.aspect;el.grid.checked=prefs.showGrid!==false;el.legend.checked=prefs.showLegend!==false;const spec=inferChartSpec(contract,el.type.value);contract.chartSpec=Object.assign(spec,{theme:el.theme.value});const svg=renderSVG(contract.chartSpec,{theme:el.theme.value,aspect:el.aspect.value,showGrid:el.grid.checked,showLegend:el.legend.checked,title:el.title.value,subtitle:el.subtitle.value});el.chart.innerHTML=svg;el.status.textContent=`${contract.methodId} · ${contract.status} · captured ${U.fmt(contract.createdAt)}`;el.meta.textContent=JSON.stringify({methodId:contract.methodId,methodVersion:contract.methodVersion,domain:contract.domain,inputFingerprint:contract.audit.inputFingerprint,outputFingerprint:contract.audit.outputFingerprint,project:contract.project},null,2);root._scLabLatestSvg=svg;}
  function updateStudio(root,projects){const el=studioElements(root),contract=root._scLabLatestResult;if(!contract)return;contract.title=el.title.value||contract.title;contract.subtitle=el.subtitle.value;contract.chartSpec=inferChartSpec(contract,el.type.value);contract.chartSpec.theme=el.theme.value;const prefs={theme:el.theme.value,chartType:el.type.value,aspect:el.aspect.value,showGrid:el.grid.checked,showLegend:el.legend.checked};savePrefs(prefs);refreshStudio(root,projects,contract);}
  function handoff(root,projects,contract,svg){const packet=analysisPacket(contract,svg||renderSVG(contract.chartSpec,loadPrefs()));localStorage.setItem(HANDOFF_KEY,JSON.stringify(packet));projects.add('analysisPackets',{type:'decision-studio-handoff',title:contract.title,packet,methodId:contract.methodId},`Decision Studio packet prepared: ${contract.title}`);U.download(`${slug(contract.title)}-decision-studio-packet.json`,JSON.stringify(packet,null,2),'application/json');const url=(w.SCLabConfig?.routes?.decisionStudio||'').trim();if(url&&url!=='#')w.open(`${url}${url.includes('?')?'&':'?'}sc_lab_handoff=1`,'_blank','noopener');U.toast(root,'Decision Studio packet prepared and saved.');return packet;}

  function init(root,projects,config={}){
    root.addEventListener('click',event=>{const button=event.target.closest('button');if(!button||!shouldCapture(button))return;setTimeout(()=>capture(root,projects,button),40);});
    root.addEventListener('sc-lab:analysis',event=>{const contract=makeContract(Object.assign({},event.detail,{project:projects.get()}));root._scLabLatestResult=contract;if(event.detail?.container)attachToolbar(root,projects,event.detail.container,contract);refreshStudio(root,projects,contract);});
    root.addEventListener('sc-lab:open-visualization',event=>{root._scLabLatestResult=event.detail;const button=root.querySelector('[data-lab-module-button="visualization-studio"]');button?.click();setTimeout(()=>refreshStudio(root,projects,event.detail),20);});
    const el=studioElements(root);if(!el.chart)return;
    Object.entries(themes).forEach(([key,t])=>el.theme.add(new Option(t.label,key)));
    root.querySelector('[data-viz-render]').addEventListener('click',()=>updateStudio(root,projects));
    ['title','subtitle','type','theme','aspect','grid','legend'].forEach(key=>el[key]?.addEventListener('change',()=>updateStudio(root,projects)));
    root.querySelector('[data-viz-export-svg]').addEventListener('click',()=>{if(root._scLabLatestResult)exportSvg(root._scLabLatestResult,root._scLabLatestSvg);});
    root.querySelector('[data-viz-export-png]').addEventListener('click',()=>{if(root._scLabLatestResult)exportPng(root._scLabLatestResult,root._scLabLatestSvg).catch(e=>U.toast(root,e.message));});
    root.querySelector('[data-viz-export-pdf]').addEventListener('click',()=>{if(root._scLabLatestResult)exportPdf(root._scLabLatestResult,root._scLabLatestSvg).catch(e=>U.toast(root,e.message));});
    root.querySelector('[data-viz-export-csv]').addEventListener('click',()=>{const c=root._scLabLatestResult;if(c)U.download(`${slug(c.title)}.csv`,csv(c),'text/csv');});
    root.querySelector('[data-viz-export-json]').addEventListener('click',()=>{const c=root._scLabLatestResult;if(c)U.download(`${slug(c.title)}-analysis.json`,JSON.stringify(c,null,2),'application/json');});
    root.querySelector('[data-viz-save]').addEventListener('click',()=>{const c=root._scLabLatestResult;if(!c)return;projects.add('visualizations',{type:'universal-visualization',title:c.title,contract:c,svg:root._scLabLatestSvg,chartSpec:c.chartSpec},`Visualization saved: ${c.title}`);U.toast(root,'Visualization saved to the active project.');});
    root.querySelector('[data-viz-notebook]').addEventListener('click',()=>{const c=root._scLabLatestResult;if(!c)return;projects.add('notes',{title:`Visualization: ${c.title}`,body:JSON.stringify({methodId:c.methodId,outputs:c.outputs,chartSpec:c.chartSpec},null,2),tags:['visualization','analysis']},`Visualization added to notebook: ${c.title}`);U.toast(root,'Visualization added to notebook.');});
    root.querySelector('[data-viz-export-package]').addEventListener('click',()=>{const c=root._scLabLatestResult;if(c)exportPackage(c,root._scLabLatestSvg).catch(e=>U.toast(root,e.message));});
    root.querySelector('[data-viz-handoff-studio]').addEventListener('click',()=>{const c=root._scLabLatestResult;if(c)handoff(root,projects,c,root._scLabLatestSvg);});
    refreshStudio(root,projects);
  }

  Lab.Visualization={VERSION,themes,makeContract,inferChartSpec,renderSVG,csv,analysisPacket,makeJpegPdf,analysisPackageEntries,exportPackage,loadPrefs,savePrefs,exportSvg,exportPng,exportPdf,handoff,init,capture};
})(window);
