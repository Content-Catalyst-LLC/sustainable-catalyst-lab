(function (W, D) {
  'use strict';
  if (W.__SCLabProductionStabilityV0266) return;
  W.__SCLabProductionStabilityV0266 = true;
  const C = W.SCLabProductionConfigV0266 || {};
  const budgets = Object.assign({nodeWarning:5000,nodeLimit:6500,heapGrowthWarningBytes:50331648,heapGrowthLimitBytes:100663296,storageLimitBytes:4194304,longTaskLimit:20,runtimeErrorLimit:50}, C.budgets || {});
  const errors = [];
  const longTasks = [];
  const networkFailures = [];
  const jobKey = 'scLabActiveComputeJobsV0266';
  const state = { version:'0.26.6', release:C.release || '0.26.6', module:C.requestedModule || 'overview', safeMode:!!C.safeMode, ready:false, backend:'unknown', restoredJobs:0, terminalJobs:0, baseline:null, last:null, max:null, startedAt:new Date().toISOString() };
  let banner = null;
  let sampler = null;
  let backendRetry = null;

  function limitedPush(list, item, limit) { list.push(item); if (list.length > limit) list.splice(0, list.length - limit); }
  function message(error) { return String(error?.message || error || 'Unknown error').slice(0, 2000); }
  function recordError(kind, error, detail) {
    limitedPush(errors, {kind, message:message(error), detail:detail || null, at:new Date().toISOString()}, Number(budgets.runtimeErrorLimit || 50));
  }
  W.addEventListener('error', event => recordError('error', event.error || event.message, {source:event.filename || null,line:event.lineno || null,column:event.colno || null}));
  W.addEventListener('unhandledrejection', event => recordError('unhandledrejection', event.reason));

  try {
    if ('PerformanceObserver' in W) {
      const observer = new PerformanceObserver(list => list.getEntries().forEach(entry => limitedPush(longTasks, {name:entry.name,duration:Math.round(entry.duration),startTime:Math.round(entry.startTime)}, 100)));
      observer.observe({type:'longtask', buffered:true});
      W.SCLabLifecycleV0255?.register?.(C.requestedModule || 'overview', () => observer.disconnect());
    }
  } catch (error) { recordError('performance_observer', error); }

  function root() { return D.querySelector('[data-sc-lab-lifecycle="0.25.5"]') || D.querySelector('.sc-lab-app'); }
  function storageBytes() {
    let total = 0;
    try { for (let i=0;i<W.localStorage.length;i++){ const k=W.localStorage.key(i); total += (String(k).length + String(W.localStorage.getItem(k) || '').length) * 2; } } catch (_) {}
    return total;
  }
  function heap() { const m=W.performance?.memory; return m ? {used:m.usedJSHeapSize,total:m.totalJSHeapSize,limit:m.jsHeapSizeLimit} : null; }
  function sample() {
    const r=root();
    const current = {at:new Date().toISOString(),nodes:r?r.querySelectorAll('*').length:0,panels:r?r.querySelectorAll('[data-lab-module]').length:0,storageBytes:storageBytes(),heap:heap(),cleanupCallbacks:W.SCLabLifecycleV0255?.status?.().cleanupCallbacks ?? null,longTasks:longTasks.length,errors:errors.length};
    if (!state.baseline) state.baseline = current;
    state.last = current;
    if (!state.max) state.max = JSON.parse(JSON.stringify(current));
    else {
      state.max.nodes=Math.max(state.max.nodes,current.nodes); state.max.storageBytes=Math.max(state.max.storageBytes,current.storageBytes); state.max.longTasks=Math.max(state.max.longTasks,current.longTasks); state.max.errors=Math.max(state.max.errors,current.errors);
      if (current.heap && (!state.max.heap || current.heap.used > state.max.heap.used)) state.max.heap=current.heap;
    }
    evaluate(current);
    return current;
  }
  function heapGrowth(current) { return current?.heap && state.baseline?.heap ? Math.max(0, current.heap.used - state.baseline.heap.used) : null; }
  function evaluate(current) {
    const over = current.nodes > budgets.nodeLimit || current.storageBytes > budgets.storageLimitBytes || longTasks.length > budgets.longTaskLimit || errors.length >= budgets.runtimeErrorLimit || (heapGrowth(current) !== null && heapGrowth(current) > budgets.heapGrowthLimitBytes);
    const warning = over || current.nodes > budgets.nodeWarning || (heapGrowth(current) !== null && heapGrowth(current) > budgets.heapGrowthWarningBytes);
    D.documentElement.classList.toggle('sc-lab-production-over-budget-v0266', !!over);
    D.documentElement.classList.toggle('sc-lab-production-warning-v0266', !!warning && !over);
    if (over) showBanner('warning', 'Production budget exceeded. Open diagnostics or Safe Start before continuing.');
  }
  function ensureBanner() {
    if (banner?.isConnected) return banner;
    const r=root(); if (!r) return null;
    banner=D.createElement('aside'); banner.className='sc-lab-production-banner-v0266'; banner.hidden=true; banner.setAttribute('role','status'); banner.setAttribute('aria-live','polite');
    banner.innerHTML='<div><strong data-production-banner-title>Lab recovery</strong><span data-production-banner-message></span></div><div><button type="button" data-production-retry-backend>Retry backend</button><button type="button" data-production-export-incident>Export diagnostics</button><a data-production-safe-link>Safe Start</a><button type="button" data-production-dismiss>Dismiss</button></div>';
    const u=new URL(W.location.href); u.searchParams.set('sc_lab_safe','1'); u.searchParams.set('sc_lab_recovery','1'); u.searchParams.delete('sc_lab_module'); banner.querySelector('[data-production-safe-link]').href=u.toString();
    banner.addEventListener('click', event => { if(event.target.closest('[data-production-dismiss]'))banner.hidden=true; if(event.target.closest('[data-production-export-incident]'))exportIncident(); if(event.target.closest('[data-production-retry-backend]'))checkBackend(true); });
    r.prepend(banner); return banner;
  }
  function showBanner(kind, text) { const b=ensureBanner(); if(!b)return; b.hidden=false; b.dataset.kind=kind; b.querySelector('[data-production-banner-title]').textContent=kind==='safe'?'Safe mode':'Lab recovery'; b.querySelector('[data-production-banner-message]').textContent=text; }

  function readJobs() { try { const data=JSON.parse(W.localStorage.getItem(jobKey)||'[]'); return Array.isArray(data)?data:[]; } catch (_) { return []; } }
  function writeJobs(items) { try { W.localStorage.setItem(jobKey,JSON.stringify(items.slice(-100))); } catch (error) { recordError('job_storage',error); } }
  function jobId(record) { return String(record?.jobId || record?.id || record?.job_id || ''); }
  function jobState(record) { return String(record?.status || record?.state || '').toLowerCase(); }
  function terminal(status) { return ['finished','completed','succeeded','failed','cancelled','canceled','timed_out'].includes(String(status||'').toLowerCase()); }
  function trackJob(record, operation) {
    const id=jobId(record); if(!id)return record;
    const jobs=readJobs().filter(item=>item.id!==id); jobs.push({id,operation:operation||'compute',status:jobState(record)||'queued',createdAt:new Date().toISOString(),updatedAt:new Date().toISOString(),module:state.module}); writeJobs(jobs); return record;
  }
  function updateJob(record) {
    const id=jobId(record); if(!id)return;
    const jobs=readJobs(); const index=jobs.findIndex(item=>item.id===id); if(index<0)return;
    jobs[index]=Object.assign({},jobs[index],{status:jobState(record)||jobs[index].status,updatedAt:new Date().toISOString()});
    if(terminal(jobs[index].status)){jobs.splice(index,1);state.terminalJobs++;} writeJobs(jobs);
  }
  async function restoreJobs() {
    const api=W.SCLab?.ComputeClient; if(!api?.job)return;
    const jobs=readJobs(); if(!jobs.length)return;
    let restored=0;
    for(const item of jobs.slice(0,25)){
      try{const record=await api.job(item.id); updateJob(record); if(!terminal(jobState(record)))restored++;}
      catch(error){recordError('job_restore',error,{jobId:item.id}); if(error?.status===404){writeJobs(readJobs().filter(job=>job.id!==item.id));}}
    }
    state.restoredJobs=restored;
    if(restored)showBanner('info',C.strings?.jobsRestored||'Queued compute jobs were restored after page reload.');
    D.dispatchEvent(new CustomEvent('sc:lab:jobs-restored',{detail:{count:restored}}));
  }
  function wrapComputeClient() {
    const api=W.SCLab?.ComputeClient; if(!api || api.__productionWrappedV0266)return false;
    api.__productionWrappedV0266=true;
    ['queueExecute','queueCompare','queueCore'].forEach(name=>{const original=api[name]; if(typeof original!=='function')return; api[name]=async function(){try{const record=await original.apply(api,arguments);return trackJob(record,name);}catch(error){backendFailure(error,name);throw error;}};});
    const originalJob=api.job; if(typeof originalJob==='function')api.job=async function(){try{const record=await originalJob.apply(api,arguments);updateJob(record);return record;}catch(error){backendFailure(error,'job');throw error;}};
    ['status','queueStatus','workers','runCore','execute','compare'].forEach(name=>{const original=api[name];if(typeof original!=='function')return;api[name]=async function(){try{const result=await original.apply(api,arguments);state.backend='online';return result;}catch(error){backendFailure(error,name);throw error;}};});
    restoreJobs(); return true;
  }
  function waitCompute(attempt=0){if(wrapComputeClient())return;if(attempt<40)W.setTimeout(()=>waitCompute(attempt+1),250);}
  function backendFailure(error,operation){state.backend=navigator.onLine?'unavailable':'offline';limitedPush(networkFailures,{operation,message:message(error),at:new Date().toISOString()},50);showBanner('warning',C.strings?.backendOffline||'Python Compute Core is temporarily unavailable.');scheduleBackendRetry();}
  function scheduleBackendRetry(){if(backendRetry)return;backendRetry=W.setTimeout(()=>{backendRetry=null;checkBackend(false);},10000);}
  async function checkBackend(manual){const api=W.SCLab?.ComputeClient;if(!api?.isConfigured?.()){state.backend='not_configured';return {ok:false,state:state.backend};}try{await api.status();state.backend='online';if(banner?.dataset.kind==='warning')banner.hidden=true;return {ok:true,state:'online'};}catch(error){backendFailure(error,manual?'manual_retry':'health_check');return {ok:false,state:state.backend,error:message(error)};}}
  W.addEventListener('online',()=>checkBackend(true)); W.addEventListener('offline',()=>{state.backend='offline';showBanner('warning','The browser is offline. Work remains local and queued jobs will resume when connectivity returns.');});

  function incident() {
    const current=sample();
    return {schema:'sc-lab-production-incident/1.0',version:'0.26.6',release:state.release,generatedAt:new Date().toISOString(),url:{origin:W.location.origin,path:W.location.pathname,module:state.module,safeMode:state.safeMode},runtime:Object.assign({},state,{current,heapGrowthBytes:heapGrowth(current)}),budgets,errors:errors.slice(),longTasks:longTasks.slice(),networkFailures:networkFailures.slice(),storage:W.SCLabProductionStorageV0266?.status?.()||null,activeJobs:readJobs(),lifecycle:W.SCLabLifecycleV0255?.status?.()||null,interface:W.SCLabInterfaceV0265?.status?.()||null,functional:W.SCLabFunctionalValidationV0264?.status?.()||null,navigator:{online:navigator.onLine,userAgent:navigator.userAgent,language:navigator.language,hardwareConcurrency:navigator.hardwareConcurrency||null,deviceMemory:navigator.deviceMemory||null},performance:{navigation:performance.getEntriesByType?.('navigation')?.[0]?.toJSON?.()||null}};
  }
  function download(name,text,type){const blob=new Blob([text],{type:type||'application/json'});const url=URL.createObjectURL(blob);const a=D.createElement('a');a.href=url;a.download=name;D.body.appendChild(a);a.click();a.remove();W.setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function exportIncident(){const data=incident();download(`sustainable-catalyst-lab-incident-${new Date().toISOString().replace(/[:.]/g,'-')}.json`,JSON.stringify(data,null,2));return data;}
  async function sendReport(report){if(!C.reportUrl||!C.nonce)return null;const response=await fetch(C.reportUrl,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-WP-Nonce':C.nonce},body:JSON.stringify(report)});if(!response.ok)throw new Error(`Report save failed with HTTP ${response.status}.`);return response.json();}
  function status(){const current=sample();return {version:'0.26.6',release:state.release,module:state.module,safeMode:state.safeMode,ready:state.ready,backend:state.backend,restoredJobs:state.restoredJobs,activeJobs:readJobs().length,current,baseline:state.baseline,max:state.max,heapGrowthBytes:heapGrowth(current),errors:errors.length,longTasks:longTasks.length,storage:W.SCLabProductionStorageV0266?.status?.()||null,budgets};}
  function boot(){if(state.ready)return;state.ready=true;ensureBanner();if(state.safeMode)showBanner('safe',C.strings?.safeMode||'Safe mode is active.');const storage=W.SCLabProductionStorageV0266?.status?.();if(storage?.repaired)showBanner('warning',C.strings?.storageRepaired||'Damaged project storage was quarantined.');sample();sampler=W.setInterval(sample,10000);W.SCLabLifecycleV0255?.register?.(state.module,()=>W.clearInterval(sampler));waitCompute();W.setTimeout(()=>checkBackend(false),1200);D.dispatchEvent(new CustomEvent('sc:lab:production-ready',{detail:status()}));if(C.stressMode&&W.parent!==W)W.setTimeout(()=>W.parent.postMessage({type:'sc-lab-v0266-ready',payload:status()},W.location.origin),700);}
  W.SCLabProductionV0266={status,sample,incident,exportIncident,sendReport,checkBackend,restoreJobs,trackJob,updateJob,readJobs};
  if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})(window,document);
