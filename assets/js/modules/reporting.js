(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const VERSION = '0.10.0';
  const HANDOFF_KEY = 'scLabDecisionStudioHandoffV2';
  const REPORT_PREF_KEY = 'scLabReportPrefsV094';

  function slug(value) {
    return String(value || 'lab-report').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 80) || 'lab-report';
  }
  function safe(value, fallback = '') { return value === null || value === undefined ? fallback : String(value); }
  function list(value) { return Array.isArray(value) ? value : value === null || value === undefined || value === '' ? [] : [value]; }
  function unique(items) {
    const seen = new Set();
    return items.filter(item => {
      const key = item?.id || `${item?.methodId || ''}:${item?.createdAt || ''}:${U.fingerprint(item || {})}`;
      if (seen.has(key)) return false;
      seen.add(key); return true;
    });
  }
  function flatten(value, prefix = '', depth = 0, rows = []) {
    if (rows.length >= 80) return rows;
    if (depth > 4) { rows.push([prefix || 'value', safe(value).slice(0, 800)]); return rows; }
    if (Array.isArray(value)) {
      if (value.length <= 12 && value.every(item => !item || typeof item !== 'object')) rows.push([prefix || 'value', value.join(', ')]);
      else rows.push([prefix || 'value', `${value.length} records`]);
      return rows;
    }
    if (value && typeof value === 'object') {
      Object.entries(value).forEach(([key, item]) => flatten(item, prefix ? `${prefix}.${key}` : key, depth + 1, rows));
      return rows;
    }
    rows.push([prefix || 'value', safe(value).slice(0, 1200)]);
    return rows;
  }
  function loadPrefs() {
    try { return Object.assign({ reportType:'technical-report', pageSize:'LETTER', includeAudit:true }, JSON.parse(localStorage.getItem(REPORT_PREF_KEY) || '{}')); }
    catch (_) { return { reportType:'technical-report', pageSize:'LETTER', includeAudit:true }; }
  }
  function savePrefs(prefs) { localStorage.setItem(REPORT_PREF_KEY, JSON.stringify(prefs)); }

  function analysisTable(analysis) {
    const rows = [];
    flatten(analysis.outputs || {}, '', 0, rows);
    return { id:`${analysis.id || analysis.methodId}-outputs`, title:`${analysis.title || analysis.methodId} outputs`, columns:['Field','Value'], rows };
  }

  function makeReport(payload = {}) {
    const analyses = unique(list(payload.analyses).filter(item => item && typeof item === 'object')).slice(0, 12);
    if (!analyses.length) throw new Error('At least one analysis is required for a report.');
    const project = payload.project || analyses[0]?.project || null;
    const report = {
      schema:'sc-lab-report/1.0', schemaVersion:'1.0', id:payload.id || U.uid('report'),
      reportType:payload.reportType || 'technical-report',
      title:payload.title || `${project?.name || 'Sustainable Catalyst Lab'} analysis report`,
      subtitle:payload.subtitle || 'Auditable calculations, figures, assumptions, validation, and provenance',
      executiveSummary:payload.executiveSummary || '', pageSize:payload.pageSize || 'LETTER',
      createdAt:payload.createdAt || U.now(), project, analyses, composition:payload.composition || null, sections:payload.sections || ['executive-summary','analysis','figures','tables','assumptions','warnings','sources','code-runtime','audit'],
      includeAudit:payload.includeAudit !== false,
      figures:analyses.flatMap(analysis => analysis.sceneSpec ? [] : [{
        id:`${analysis.id || analysis.methodId}-figure`, title:analysis.title || analysis.methodId,
        caption:analysis.subtitle || `Generated from ${analysis.methodId}.`, methodId:analysis.methodId,
        validationState:analysis.status || 'unreviewed', chartSpec:analysis.chartSpec || null, svg:analysis.svg || ''
      }]),
      scenes:analyses.filter(analysis => analysis.sceneSpec).map(analysis => ({
        id:`${analysis.id || analysis.methodId}-scene`, title:analysis.title || analysis.methodId,
        caption:analysis.subtitle || `Dimensional scene from ${analysis.methodId}.`, methodId:analysis.methodId,
        validationState:analysis.status || 'unreviewed', sceneSpec:analysis.sceneSpec, svg:analysis.svg || '',
        dimensions:analysis.sceneSpec.dimensions, vertices:analysis.sceneSpec.vertices || [], edges:analysis.sceneSpec.edges || [],
        faces:analysis.sceneSpec.faces || [], cells:analysis.sceneSpec.cells || [], projection:analysis.sceneSpec.projection || null,
        metadata:analysis.sceneSpec.metadata || {}
      })),
      tables:analyses.map(analysisTable), audit:{}
    };
    report.audit = {
      application:'Sustainable Catalyst Lab', applicationVersion:VERSION, reportContractVersion:'1.0',
      reportFingerprint:U.fingerprint({ title:report.title, reportType:report.reportType, analyses:report.analyses.map(a => a.audit || a.id || a.methodId), createdAt:report.createdAt }),
      analysisFingerprints:report.analyses.map(a => a.audit?.outputFingerprint || U.fingerprint(a.outputs || {})), compositionFingerprint:report.composition?U.fingerprint(report.composition):null,
      generatedAt:report.createdAt
    };
    return report;
  }

  function makeDecisionStudioPacket(report) {
    const analyses = report.analyses || [];
    const packet = {
      packetType:'scientific-report', schemaVersion:'2.0',
      origin:{ application:'Sustainable Catalyst Lab', version:VERSION, reportSchema:report.schema },
      createdAt:U.now(), project:report.project || null,
      report:{ id:report.id, reportType:report.reportType, title:report.title, subtitle:report.subtitle, executiveSummary:report.executiveSummary, sections:report.sections, composition:report.composition || null, audit:report.audit },
      analysis:analyses[0] || {}, analyses,
      charts:report.figures || [], scenes:report.scenes || [], tables:report.tables || [], claims:[],
      assumptions:analyses.flatMap(a => list(a.assumptions)),
      uncertainties:analyses.flatMap(a => list(a.validation?.uncertainties || a.uncertainties)),
      warnings:analyses.flatMap(a => list(a.warnings)),
      evidence:analyses.flatMap(a => list(a.evidence)), sources:analyses.flatMap(a => list(a.sources)),
      codeRuntimes:analyses.flatMap(a => list(a.runtime || a.execution || a.codeRuntime)),
      validationRecords:analyses.map(a => a.validation).filter(Boolean), audit:{}
    };
    packet.audit = {
      packetFingerprint:U.fingerprint(packet), reportFingerprint:report.audit?.reportFingerprint || U.fingerprint(report),
      analysisCount:analyses.length, chartCount:packet.charts.length, sceneCount:packet.scenes.length,
      generatedAt:packet.createdAt
    };
    return packet;
  }

  function pdfEscape(value) { return safe(value).replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)').replace(/[\r\n]+/g, ' '); }
  function ascii(value) { return safe(value).normalize('NFKD').replace(/[^\x20-\x7E]/g, '?'); }
  function wrap(value, width = 92) {
    const words = ascii(value).split(/\s+/).filter(Boolean), lines = []; let line = '';
    words.forEach(word => {
      if (!line) line = word;
      else if (`${line} ${word}`.length <= width) line += ` ${word}`;
      else { lines.push(line); line = word; }
    });
    if (line) lines.push(line);
    return lines.length ? lines : [''];
  }
  function fmt(value) {
    const n = Number(value); if (!Number.isFinite(n)) return safe(value);
    const a = Math.abs(n); return (a >= 1e5 || (a > 0 && a < 1e-3)) ? n.toExponential(4) : Number(n.toPrecision(7)).toString();
  }
  function chartCommands(spec, x, y, width, height) {
    if (!spec || !Array.isArray(spec.data) || spec.data.length < 2) return [];
    const data = spec.data.slice(0, 140), xKey = spec.xKey || 'x', yKeys = (spec.yKeys || ['y']).slice(0, 4), type = spec.type || 'line';
    const numeric = value => { const n=Number(value); return Number.isFinite(n) ? n : null; };
    const xv = data.map((row,i) => numeric(row?.[xKey]) ?? i), yv = data.flatMap(row => yKeys.map(k => numeric(row?.[k]))).filter(v => v !== null);
    if (!yv.length) return [];
    let xmin=Math.min(...xv), xmax=Math.max(...xv), ymin=Math.min(0,...yv), ymax=Math.max(0,...yv);
    if (xmin===xmax)xmax=xmin+1;if(ymin===ymax)ymax=ymin+1;const pad=(ymax-ymin)*.08;ymin-=pad;ymax+=pad;
    const l=44,b=28,r=12,t=12,pw=width-l-r,ph=height-b-t,sx=v=>x+l+(v-xmin)/(xmax-xmin)*pw,sy=v=>y+b+(v-ymin)/(ymax-ymin)*ph;
    const cmd=['0.82 0.85 0.87 RG 0.5 w',`${x} ${y} ${width} ${height} re S`];
    for(let i=0;i<5;i++){const yy=y+b+ph*i/4;cmd.push('0.88 0.90 0.91 RG 0.35 w',`${x+l} ${yy} m ${x+l+pw} ${yy} l S`);}
    cmd.push('0.15 0.18 0.20 RG 0.8 w',`${x+l} ${y+b} m ${x+l+pw} ${y+b} l S`,`${x+l} ${y+b} m ${x+l} ${y+b+ph} l S`);
    const colors=[[.78,0,0],[.12,.36,.47],[.35,.43,.16],[.5,.35,.51]];
    if(type==='bar'){
      const key=yKeys[0], zero=sy(0), bw=Math.max(3,pw/data.length*.62);data.forEach((row,i)=>{const v=numeric(row?.[key]);if(v===null)return;const xx=x+l+(i+.5)/data.length*pw-bw/2,yy=sy(v);cmd.push(`${colors[0].join(' ')} rg`,`${xx.toFixed(2)} ${Math.min(yy,zero).toFixed(2)} ${bw.toFixed(2)} ${Math.max(.7,Math.abs(yy-zero)).toFixed(2)} re f`);});
    } else {
      yKeys.forEach((key,si)=>{let prev=null;cmd.push(`${colors[si%colors.length].join(' ')} RG 1.5 w`);data.forEach((row,i)=>{const v=numeric(row?.[key]);if(v===null){prev=null;return;}const point=[sx(xv[i]),sy(v)];if(type!=='scatter'&&prev)cmd.push(`${prev[0].toFixed(2)} ${prev[1].toFixed(2)} m ${point[0].toFixed(2)} ${point[1].toFixed(2)} l S`);cmd.push(`${colors[si%colors.length].join(' ')} rg`,`${(point[0]-1.5).toFixed(2)} ${(point[1]-1.5).toFixed(2)} 3 3 re f`);prev=point;});});
    }
    return cmd;
  }

  function makePdf(report) {
    const page = report.pageSize === 'A4' ? [595.28,841.89] : [612,792], [PW,PH]=page, margin=42, top=PH-48, bottom=42;
    const pages=[];let commands=[], y=top;
    const addPage=()=>{if(commands.length)pages.push(commands.join('\n'));commands=[];y=top;commands.push('0.78 0 0 RG 1.2 w',`${margin} ${PH-28} m ${PW-margin} ${PH-28} l S`);};
    const ensure=(need=20)=>{if(y-need<bottom){pages.push(commands.join('\n'));commands=[];y=top;commands.push('0.78 0 0 RG 1.2 w',`${margin} ${PH-28} m ${PW-margin} ${PH-28} l S`);}};
    const text=(value,size=9,font='F1',indent=0,leading=size*1.35)=>{wrap(value,Math.max(36,Math.floor((PW-margin*2-indent)/(size*.52)))).forEach(line=>{ensure(leading+2);commands.push('BT',`/${font} ${size} Tf`,`${margin+indent} ${y} Td`,`(${pdfEscape(line)}) Tj`,'ET');y-=leading;});};
    const heading=(value,level=1)=>{const size=level===1?16:11.5;ensure(size*2.2);y-=level===1?5:2;text(value,size,'F2',0,size*1.35);y-=4;};
    const kv=(rows)=>{rows.slice(0,80).forEach(([k,v])=>{ensure(18);commands.push('0.93 0.94 0.95 rg',`${margin} ${y-11} ${PW-margin*2} 16 re f`);commands.push('BT','/F2 7.5 Tf',`${margin+5} ${y-7} Td`,`(${pdfEscape(ascii(k).slice(0,40))}) Tj`,'ET');commands.push('BT','/F1 7.5 Tf',`${margin+150} ${y-7} Td`,`(${pdfEscape(ascii(v).slice(0,92))}) Tj`,'ET');y-=18;});y-=4;};
    addPage();
    text(report.title,23,'F2',0,28);if(report.subtitle)text(report.subtitle,11,'F1',0,15);y-=10;
    kv([['Report type',report.reportType],['Project',report.project?.name||'Unassigned'],['Generated',report.createdAt],['Analyses',report.analyses.length],['Fingerprint',report.audit?.reportFingerprint||'']]);
    if(report.executiveSummary){heading('Executive summary');text(report.executiveSummary,9.5,'F1',0,13);}
    if(report.composition?.sections?.length){heading('Composed report sections');report.composition.sections.filter(section=>section&&section.enabled!==false).forEach(section=>{heading(section.title||section.type||'Report section',2);if(section.content)text(section.content,9,'F1',0,12.5);});} heading('Audit boundary');text('This report preserves supplied calculations, equations, assumptions, warnings, sources, validation states, and software metadata. Results remain bounded by the stated method domain and do not replace professional review where required.',9,'F1',0,12.5);
    report.analyses.forEach((analysis,index)=>{
      ensure(80);heading(`${index+1}. ${analysis.title||analysis.methodId}`);kv([['Method',analysis.methodId],['Version',analysis.methodVersion||''],['Domain',analysis.domain||''],['Status',analysis.status||'unreviewed'],['Created',analysis.createdAt||'']]);
      if(analysis.equation){heading('Equation or method',2);text(analysis.equation,8,'F3',4,11);}
      const inputs=flatten(analysis.inputs||{});if(inputs.length){heading('Inputs',2);kv(inputs);}
      const outputs=flatten(analysis.outputs||{});if(outputs.length){heading('Outputs',2);kv(outputs);}
      if(analysis.chartSpec?.data?.length>=2){ensure(250);heading('Figure',2);commands.push(...chartCommands(analysis.chartSpec,margin,y-225,PW-margin*2,220));y-=235;text(analysis.chartSpec.subtitle||`Generated from ${analysis.methodId}.`,7.5,'F1',0,10);}
      const assumptions=list(analysis.assumptions);if(assumptions.length){heading('Assumptions',2);assumptions.forEach(item=>text(`- ${safe(item)}`,8.5,'F1',8,11.5));}
      const warnings=list(analysis.warnings);if(warnings.length){heading('Warnings and limitations',2);warnings.forEach(item=>text(`- ${safe(item)}`,8.5,'F1',8,11.5));}
      if(analysis.validation){heading('Validation record',2);kv(flatten(analysis.validation));}
      if(report.includeAudit!==false&&analysis.audit){heading('Analysis audit',2);kv(flatten(analysis.audit));}
      if(index<report.analyses.length-1){pages.push(commands.join('\n'));commands=[];y=top;commands.push('0.78 0 0 RG 1.2 w',`${margin} ${PH-28} m ${PW-margin} ${PH-28} l S`);}
    });
    if(commands.length)pages.push(commands.join('\n'));
    const objects=[];const add=value=>{objects.push(typeof value==='string'?new TextEncoder().encode(value):value);return objects.length;};
    add('');const pagesId=add('');const fontRegular=add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>');const fontBold=add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>');const fontMono=add('<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>');
    const pageIds=[];pages.forEach((content,index)=>{const footer=`BT /F1 7 Tf ${margin} 20 Td (Sustainable Catalyst Lab - auditable scientific report) Tj ET BT /F1 7 Tf ${PW-margin-38} 20 Td (Page ${index+1}) Tj ET`;const stream=`${content}\n${footer}`;const contentId=add(`<< /Length ${new TextEncoder().encode(stream).length} >>\nstream\n${stream}\nendstream`);const pageId=add(`<< /Type /Page /Parent ${pagesId} 0 R /MediaBox [0 0 ${PW} ${PH}] /Resources << /Font << /F1 ${fontRegular} 0 R /F2 ${fontBold} 0 R /F3 ${fontMono} 0 R >> >> /Contents ${contentId} 0 R >>`);pageIds.push(pageId);});
    objects[pagesId-1]=new TextEncoder().encode(`<< /Type /Pages /Kids [${pageIds.map(id=>`${id} 0 R`).join(' ')}] /Count ${pageIds.length} >>`);objects[0]=new TextEncoder().encode(`<< /Type /Catalog /Pages ${pagesId} 0 R >>`);
    const header=new TextEncoder().encode('%PDF-1.4\n%SC-LAB\n');let size=header.length;const offsets=[0];objects.forEach((obj,i)=>{offsets.push(size);size+=new TextEncoder().encode(`${i+1} 0 obj\n`).length+obj.length+8;});const xrefOffset=size;let xref=`xref\n0 ${objects.length+1}\n0000000000 65535 f \n`;for(let i=1;i<offsets.length;i++)xref+=String(offsets[i]).padStart(10,'0')+' 00000 n \n';const trailer=`trailer\n<< /Size ${objects.length+1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
    const tail=new TextEncoder().encode(xref+trailer), out=new Uint8Array(size+tail.length);let pos=0;out.set(header,pos);pos+=header.length;objects.forEach((obj,i)=>{const h=new TextEncoder().encode(`${i+1} 0 obj\n`),f=new TextEncoder().encode('\nendobj\n');out.set(h,pos);pos+=h.length;out.set(obj,pos);pos+=obj.length;out.set(f,pos);pos+=f.length;});out.set(tail,pos);return out;
  }

  function downloadBytes(filename, bytes, type='application/octet-stream') {
    const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([bytes],{type}));a.download=filename;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},80);
  }
  function base64Bytes(value) { const binary=atob(value), out=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)out[i]=binary.charCodeAt(i);return out; }

  function availableAnalyses(root, projects) {
    const p=projects.get(), rows=[];
    if(root._scLabLatestResult)rows.push(root._scLabLatestResult);
    (p.visualizations||[]).forEach(item=>{if(item.contract)rows.push(item.contract);});
    (p.analysisPackets||[]).forEach(item=>{const packet=item.packet||item;(packet.analyses||[]).forEach(a=>rows.push(a));if(packet.analysis)rows.push(packet.analysis);});
    return unique(rows).slice(0,40);
  }
  function reportElements(root) { return {
    title:root.querySelector('[data-report-title]'),subtitle:root.querySelector('[data-report-subtitle]'),type:root.querySelector('[data-report-type]'),pageSize:root.querySelector('[data-report-page-size]'),summary:root.querySelector('[data-report-summary]'),audit:root.querySelector('[data-report-audit]'),list:root.querySelector('[data-report-analysis-list]'),status:root.querySelector('[data-report-status]'),preview:root.querySelector('[data-report-preview]'),meta:root.querySelector('[data-report-meta]')
  };}
  function renderAnalysisList(root,projects) {
    const el=reportElements(root), rows=availableAnalyses(root,projects);root._scLabReportAnalyses=rows;
    el.list.innerHTML=rows.length?rows.map((analysis,index)=>`<label class="sc-lab-report-analysis-option"><input type="checkbox" data-report-analysis-index="${index}" ${index===0?'checked':''}><span><strong>${U.esc(analysis.title||analysis.methodId)}</strong><small>${U.esc(analysis.methodId||'analysis')} · ${U.esc(analysis.status||'unreviewed')} · ${U.esc(U.fmt(analysis.createdAt))}</small></span></label>`).join(''):'<div class="sc-lab-data-note">Run a calculation or save a visualization before composing a report.</div>';
    el.status.textContent=rows.length?`${rows.length} report-ready analyses are available.`:'No report-ready analyses are available.';
  }
  function selectedAnalyses(root) { const rows=root._scLabReportAnalyses||[];return [...root.querySelectorAll('[data-report-analysis-index]:checked')].map(input=>rows[Number(input.dataset.reportAnalysisIndex)]).filter(Boolean).slice(0,12); }
  function reportComposition(root) { return root._scLabReportComposition || w.SCLabV095CurrentComposition || null; } function compositionSections(root) { const composition=reportComposition(root); const sections=(composition?.sections||[]).filter(section=>section&&section.enabled!==false).map(section=>section.type); return sections.length?sections:undefined; } function buildFromForm(root,projects) { const el=reportElements(root), prefs={reportType:el.type.value,pageSize:el.pageSize.value,includeAudit:el.audit.checked};savePrefs(prefs);return makeReport({title:el.title.value.trim(),subtitle:el.subtitle.value.trim(),reportType:el.type.value,pageSize:el.pageSize.value,executiveSummary:el.summary.value.trim(),includeAudit:el.audit.checked,project:{id:projects.get().id,name:projects.get().name,schemaVersion:projects.get().schemaVersion},composition:reportComposition(root),sections:compositionSections(root),analyses:selectedAnalyses(root)}); }
  function renderPreview(root,report) { const el=reportElements(root);root._scLabCurrentReport=report;el.preview.innerHTML=`<header><span>${U.esc(report.reportType.replace(/-/g,' ').toUpperCase())}</span><h4>${U.esc(report.title)}</h4><p>${U.esc(report.subtitle)}</p></header>${report.executiveSummary?`<section><h5>Executive summary</h5><p>${U.esc(report.executiveSummary)}</p></section>`:''}<section><h5>Included analyses</h5>${report.analyses.map((a,i)=>`<article><strong>${i+1}. ${U.esc(a.title||a.methodId)}</strong><span>${U.esc(a.methodId)} · ${U.esc(a.status||'unreviewed')}</span><p>${U.esc(a.equation||'Structured calculation and audit record.')}</p></article>`).join('')}</section><footer>Report fingerprint: <code>${U.esc(report.audit.reportFingerprint)}</code></footer>`;el.meta.textContent=JSON.stringify({schema:report.schema,reportType:report.reportType,analysisCount:report.analyses.length,figureCount:report.figures.length,sceneCount:report.scenes.length,tableCount:report.tables.length,audit:report.audit},null,2);el.status.textContent=`Report prepared with ${report.analyses.length} analyses, ${report.figures.length} figures, and ${report.tables.length} tables.`;return report; }
  function compose(root,projects) { try{return renderPreview(root,buildFromForm(root,projects));}catch(error){U.toast(root,error.message);reportElements(root).status.textContent=error.message;return null;} }
  function saveReport(root,projects,report) { projects.add('reports',{type:report.reportType,title:report.title,report,audit:report.audit},`PDF report saved: ${report.title}`);(report.figures||[]).forEach(figure=>projects.add('reportFigures',{title:figure.title,figure,reportId:report.id},`Report figure saved: ${figure.title}`));U.toast(root,'Report and figures saved to the active project.'); }
  function handoff(root,projects,report) { const packet=makeDecisionStudioPacket(report);localStorage.setItem(HANDOFF_KEY,JSON.stringify(packet));projects.add('decisionStudioHandoffs',{type:'scientific-report',title:report.title,packet,reportId:report.id},`Decision Studio report handoff prepared: ${report.title}`);projects.add('analysisPackets',{type:'decision-studio-report-handoff',title:report.title,packet,reportId:report.id},`Decision Studio packet saved: ${report.title}`);U.download(`${slug(report.title)}-decision-studio-packet.json`,JSON.stringify(packet,null,2),'application/json');const url=(w.SCLabConfig?.routes?.decisionStudio||'').trim();if(url&&url!=='#')w.open(`${url}${url.includes('?')?'&':'?'}sc_lab_handoff=2&packet=${encodeURIComponent(packet.audit.packetFingerprint)}`,'_blank','noopener');U.toast(root,'Decision Studio report packet prepared and saved.');return packet; }

  function init(root,projects) {
    const panel=root.querySelector('[data-lab-module="report-studio"]');if(!panel)return;const el=reportElements(root),prefs=loadPrefs();el.type.value=prefs.reportType;el.pageSize.value=prefs.pageSize;el.audit.checked=prefs.includeAudit!==false;
    const refresh=()=>renderAnalysisList(root,projects);refresh();
    document.addEventListener('sc-lab-report-composition-applied',event=>{root._scLabReportComposition=event.detail?.composition||null;if(selectedAnalyses(root).length)compose(root,projects);}); root.addEventListener('sc-lab:analysis',()=>setTimeout(refresh,60));
    root.addEventListener('sc-lab:open-report',event=>{if(event.detail)root._scLabLatestResult=event.detail;root.querySelector('[data-lab-module-button="report-studio"]')?.click();setTimeout(()=>{refresh();const first=root.querySelector('[data-report-analysis-index]');if(first)first.checked=true;compose(root,projects);},30);});
    root.querySelector('[data-report-load-current]').addEventListener('click',()=>{refresh();const first=root.querySelector('[data-report-analysis-index]');if(first)first.checked=true;compose(root,projects);});
    root.querySelector('[data-report-select-all]').addEventListener('click',()=>{root.querySelectorAll('[data-report-analysis-index]').forEach((input,index)=>input.checked=index<12);compose(root,projects);});
    root.querySelector('[data-report-clear-selection]').addEventListener('click',()=>{root.querySelectorAll('[data-report-analysis-index]').forEach(input=>input.checked=false);el.status.textContent='Select at least one analysis.';});
    root.querySelector('[data-report-compose]').addEventListener('click',()=>compose(root,projects));
    root.querySelector('[data-report-download-pdf]').addEventListener('click',()=>{const report=compose(root,projects);if(report)downloadBytes(`${slug(report.title)}.pdf`,makePdf(report),'application/pdf');});
    root.querySelector('[data-report-download-render]').addEventListener('click',async()=>{const report=compose(root,projects);if(!report)return;try{el.status.textContent='Requesting vector PDF from the Render report engine…';const result=await Lab.ComputeClient.reportPdf(report);downloadBytes(result.filename||`${slug(report.title)}-render.pdf`,base64Bytes(result.dataBase64),'application/pdf');projects.add('reportExports',{title:report.title,reportId:report.id,engine:result.engine,pdfFingerprint:result.pdfFingerprint,pageCount:result.pageCount,byteLength:result.byteLength},`Render PDF exported: ${report.title}`);el.status.textContent=`Render PDF generated: ${result.pageCount} pages, ${result.byteLength.toLocaleString()} bytes.`;}catch(error){el.status.textContent=`Render report unavailable: ${error.message}`;U.toast(root,error.message);}});
    root.querySelector('[data-report-download-json]').addEventListener('click',()=>{const report=compose(root,projects);if(report)U.download(`${slug(report.title)}-report.json`,JSON.stringify(report,null,2),'application/json');});
    root.querySelector('[data-report-download-packet]').addEventListener('click',()=>{const report=compose(root,projects);if(report){const packet=makeDecisionStudioPacket(report);U.download(`${slug(report.title)}-decision-studio-packet.json`,JSON.stringify(packet,null,2),'application/json');}});
    root.querySelector('[data-report-save]').addEventListener('click',()=>{const report=compose(root,projects);if(report)saveReport(root,projects,report);});
    root.querySelector('[data-report-handoff]').addEventListener('click',()=>{const report=compose(root,projects);if(report)handoff(root,projects,report);});
    root.querySelector('[data-report-validate]').addEventListener('click',async()=>{const report=compose(root,projects);if(!report)return;try{const local=makeDecisionStudioPacket(report);const result=Lab.ComputeClient.isConfigured()?await Lab.ComputeClient.validateHandoff(local):{status:'LOCAL_VALIDATION',packetFingerprint:local.audit.packetFingerprint,analysisCount:local.analyses.length};el.status.textContent=`Decision Studio packet ${result.status}: ${result.analysisCount} analyses · ${result.packetFingerprint}.`;}catch(error){el.status.textContent=error.message;U.toast(root,error.message);}});
    ['title','subtitle','type','pageSize','summary','audit'].forEach(key=>el[key]?.addEventListener('change',()=>{if(selectedAnalyses(root).length)compose(root,projects);}));
  }

  Lab.Reporting={VERSION,makeReport,makeDecisionStudioPacket,makePdf,flatten,chartCommands,availableAnalyses,init};
})(window);
