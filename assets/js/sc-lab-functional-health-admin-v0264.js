(function (W, D) {
  'use strict';
  const config = W.SCLabFunctionalHealthAdminConfigV0264 || {};
  const root = D.querySelector('[data-sc-lab-functional-admin-v0264]');
  if (!root) return;
  const registry = Array.isArray(config.registry) ? config.registry : [];
  const rows = root.querySelector('[data-functional-rows]');
  const summary = root.querySelector('[data-functional-summary]');
  const progress = root.querySelector('[data-functional-progress]');
  const progressLabel = root.querySelector('[data-functional-progress-label]');
  const frame = root.querySelector('[data-functional-frame]');
  const raw = root.querySelector('[data-functional-json]');
  const server = root.querySelector('[data-functional-server]');
  const results = new Map(); let stopped = false; let activeResolve = null;

  function esc(value) { const div=D.createElement('div'); div.textContent=String(value ?? ''); return div.innerHTML; }
  function statusLabel(status) { return String(status || 'not_run').replaceAll('_', ' '); }
  function badge(status) { return `<span class="sc-lab-functional-badge-v0264 is-${esc(status || 'not-run')}">${esc(statusLabel(status))}</span>`; }
  function renderRows() {
    rows.innerHTML = registry.map(spec => {
      const r=results.get(spec.module); const url=new URL(config.labUrl, W.location.origin); url.searchParams.set('sc_lab_module',spec.module);
      return `<tr data-functional-row="${esc(spec.module)}"><td><strong>${esc(spec.label)}</strong><br><small>${esc(spec.module)}</small></td><td>${r?badge(r.panel?'pass':'fail'):'—'}</td><td>${r?badge(r.controller?'pass':'fail'):'—'}</td><td>${r?.action===null?'structural':r?badge(r.action?'pass':'fail'):'—'}</td><td>${r?badge(r.result?'pass':'fail'):'—'}</td><td>${r?esc((r.errors||[]).length):'—'}</td><td>${r?badge(r.status):badge('not-run')}</td><td><a href="${esc(url.toString())}" target="_blank" rel="noopener">Open</a></td></tr>`;
    }).join('');
  }
  function report() {
    const list=[...results.values()]; const counts={}; list.forEach(r=>counts[r.status]=(counts[r.status]||0)+1);
    return { schema:'sc-lab-functional-health/1.0', version:config.version, release:config.release, generatedAt:new Date().toISOString(), userAgent:navigator.userAgent, summary:{ total:list.length, functional:list.filter(r=>/^functional/.test(r.status)).length, failed:list.filter(r=>['panel_missing','controller_missing','action_missing','output_missing','calculation_failed','result_not_observed','empty_panel'].includes(r.status)).length, degraded:list.filter(r=>['backend_required','external_source_unavailable','functional_with_errors'].includes(r.status)).length, counts }, results:list };
  }
  function refreshSummary(message) {
    const rep=report(); summary.innerHTML=`<strong>${esc(message || 'Functional health')}</strong><span>${rep.summary.functional} functional · ${rep.summary.degraded} degraded · ${rep.summary.failed} failed</span>`;
    raw.textContent=JSON.stringify(rep,null,2);
  }
  function moduleUrl(module) { const url=new URL(config.labUrl,W.location.origin); url.searchParams.set('sc_lab_module',module); url.searchParams.set('sc_lab_validation','1'); url.searchParams.set('_sc_lab_validation_run',Date.now().toString()); return url.toString(); }
  function runOne(spec) {
    return new Promise(resolve => {
      let timer=null;
      const done=result=>{ if(timer)clearTimeout(timer); activeResolve=null; resolve(result); };
      activeResolve=done;
      timer=setTimeout(()=>done({module:spec.module,label:spec.label,panel:false,controller:false,action:false,result:false,status:'runner_timeout',message:'The isolated validation frame did not return a result.',errors:[]}),Math.max(30000,Number(spec.timeoutMs||8000)+9000));
      frame.src=moduleUrl(spec.module);
    });
  }
  W.addEventListener('message',event=>{ if(event.origin!==W.location.origin||event.data?.type!=='sc-lab-functional-result-v0264')return; const result=event.data.result; if(activeResolve&&result?.module)activeResolve(result); });
  async function runSet(specs) {
    stopped=false; results.clear(); renderRows(); progress.max=specs.length; progress.value=0; progressLabel.textContent=`0 / ${specs.length}`;
    for(let i=0;i<specs.length;i++) { if(stopped)break; const spec=specs[i]; refreshSummary(`Testing ${spec.label}…`); const result=await runOne(spec); results.set(spec.module,result); progress.value=i+1; progressLabel.textContent=`${i+1} / ${specs.length}`; renderRows(); }
    frame.src='about:blank'; refreshSummary(stopped?'Validation stopped.':'Validation completed.'); if(!stopped) await saveReport();
  }
  async function saveReport() { try { await fetch(config.saveUrl,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-WP-Nonce':config.nonce},body:JSON.stringify(report())}); } catch(_){} }
  async function serverHealth() { server.textContent='Checking server and source health…'; try { const response=await fetch(config.serverHealthUrl,{credentials:'same-origin',cache:'no-store'}); const data=await response.json(); server.innerHTML=`<strong>Server health: ${esc(data.ok?'ready':'degraded')}</strong><span>${esc(data.moduleCount)} registered panels · feeds ${data.features?.feedsEnabled?'enabled':'disabled'} · climate maps ${data.features?.climateMapsEnabled?'enabled':'disabled'} · Python compute ${data.features?.remoteComputeEnabled?'enabled':'optional/off'}</span>`; } catch(error){ server.textContent=`Server health endpoint failed: ${error.message}`; } }
  function exportReport() { const blob=new Blob([JSON.stringify(report(),null,2)],{type:'application/json'}); const a=D.createElement('a'); a.href=URL.createObjectURL(blob); a.download=`sustainable-catalyst-lab-functional-health-${new Date().toISOString().replace(/[:.]/g,'-')}.json`; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),1000); }
  root.querySelector('[data-functional-run-priority]').addEventListener('click',()=>runSet(registry.filter(x=>x.priority)));
  root.querySelector('[data-functional-run-all]').addEventListener('click',()=>runSet(registry));
  root.querySelector('[data-functional-stop]').addEventListener('click',()=>{stopped=true;if(activeResolve)activeResolve({module:'current',status:'stopped',errors:[]});});
  root.querySelector('[data-functional-export]').addEventListener('click',exportReport);
  root.querySelector('[data-functional-refresh-server]').addEventListener('click',serverHealth);
  renderRows(); refreshSummary('Ready to run checks.'); serverHealth();
})(window, document);
