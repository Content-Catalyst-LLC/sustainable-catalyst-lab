(function (W, D) {
  'use strict';
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.27.2';
  const state = { mounted:false, selectedJobId:null, jobs:[], queue:null, cache:null, checkpoints:null, lastError:null, timer:null };
  const root = () => D.querySelector('[data-lab-module="long-running-jobs"]');
  const el = key => root()?.querySelector(`[data-longjobs-${key}]`);
  const pretty = value => JSON.stringify(value, null, 2);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const activeProjectId = () => root()?.closest('.sc-lab-app')?._scLabProjects?.get?.()?.id || '';
  function announce(message, tone='ready') { const node=el('status'); if(node){node.textContent=message;node.dataset.state=tone;} W.dispatchEvent(new CustomEvent('sc-lab:long-job-status',{detail:{message,tone,version:VERSION}})); }
  function duration(seconds) { if(seconds===null||seconds===undefined||!Number.isFinite(Number(seconds)))return '—'; const n=Math.max(0,Number(seconds)); return n<60?`${Math.round(n)}s`:`${Math.floor(n/60)}m ${Math.round(n%60)}s`; }
  function renderMetrics() {
    const q=state.queue||{}, counts=q.counts||{}, cache=state.cache||{};
    const metrics=[['Active',q.activeWorkers??0],['Queued',(counts.queued||0)+(counts.retrying||0)],['Paused',counts.paused||0],['Cache hits',cache.hits||q.cache?.hits||0]];
    el('metrics').innerHTML=metrics.map(([label,value])=>`<div class="sc-longjobs-metric"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join('');
  }
  function renderJobs() {
    const list=el('list'); if(!list)return;
    if(!state.jobs.length){list.innerHTML='<div class="sc-lab-data-note">No compute jobs have been recorded for this project.</div>';return;}
    list.innerHTML=state.jobs.map(job=>`<button type="button" class="sc-longjobs-row" data-job-id="${esc(job.jobId)}" aria-current="${job.jobId===state.selectedJobId?'true':'false'}"><span><strong>${esc(job.method)}</strong><br><small>${esc(job.progressMessage||job.status)}</small></span><span>${esc(job.status)} · P${esc(job.priority??50)}</span><span class="sc-longjobs-progress" aria-label="${esc(job.progress)} percent complete"><span style="width:${Math.max(0,Math.min(100,Number(job.progress||0)))}%"></span></span></button>`).join('');
    list.querySelectorAll('[data-job-id]').forEach(button=>button.addEventListener('click',()=>selectJob(button.dataset.jobId)));
  }
  function actionEnabled(job, action) {
    const status=String(job?.status||'');
    if(action==='pause')return ['queued','retrying','running'].includes(status);
    if(action==='resume')return ['paused','failed','timed_out','cancelled'].includes(status);
    if(action==='cancel')return !['completed','failed','cancelled','timed_out'].includes(status);
    if(action==='retry')return ['failed','timed_out','cancelled'].includes(status);
    return false;
  }
  function renderDetail() {
    const job=state.jobs.find(item=>item.jobId===state.selectedJobId);
    const detail=el('detail'); if(!detail)return;
    if(!job){detail.innerHTML='<div class="sc-lab-data-note">Select a job to inspect progress, checkpoints, partial outputs, and recovery controls.</div>';return;}
    const checkpointRows=state.checkpoints?.history||[];
    detail.innerHTML=`<h4>${esc(job.method)}</h4><p><strong>${esc(job.status)}</strong> · ${esc(job.progress)}% · priority ${esc(job.priority)} · ETA ${esc(duration(job.estimatedRemainingSeconds))}</p><p>${esc(job.progressMessage||'')}</p><div class="sc-longjobs-actions"><button class="sc-lab-button" data-job-action="pause" ${actionEnabled(job,'pause')?'':'disabled'}>Pause</button><button class="sc-lab-button" data-job-action="resume" ${actionEnabled(job,'resume')?'':'disabled'}>Resume</button><button class="sc-lab-button" data-job-action="cancel" ${actionEnabled(job,'cancel')?'':'disabled'}>Cancel</button><button class="sc-lab-button" data-job-action="retry" ${actionEnabled(job,'retry')?'':'disabled'}>Retry</button><button class="sc-lab-button" data-job-action="save" ${job.result?'':'disabled'}>Save result</button></div><h5>Partial result</h5><pre>${esc(pretty(job.partialResult||state.checkpoints?.partialResult||{}))}</pre><h5>Checkpoint history</h5><div class="sc-longjobs-checkpoints">${checkpointRows.length?checkpointRows.map(row=>`<div class="sc-longjobs-checkpoint"><strong>#${esc(row.sequence)} · ${esc(row.progress)}%</strong><br>${esc(row.message)}<br><small>${esc(row.createdAt)}</small></div>`).join(''):'<div class="sc-lab-data-note">No checkpoints recorded yet.</div>'}</div><h5>Result / error</h5><pre>${esc(pretty(job.result||job.error||{}))}</pre>`;
    detail.querySelectorAll('[data-job-action]').forEach(button=>button.addEventListener('click',()=>perform(button.dataset.jobAction,job)));
  }
  async function selectJob(jobId) {
    state.selectedJobId=jobId; renderJobs();
    try { state.checkpoints=await Lab.ComputeClient.checkpoints(jobId,20); } catch(_){ state.checkpoints=null; }
    renderDetail();
  }
  async function perform(action,job) {
    try {
      announce(`${action} requested for ${job.method}.`,'loading');
      if(action==='pause')await Lab.ComputeClient.pause(job.jobId);
      else if(action==='resume')await Lab.ComputeClient.resume(job.jobId);
      else if(action==='cancel')await Lab.ComputeClient.cancel(job.jobId);
      else if(action==='retry')await Lab.ComputeClient.retry(job.jobId);
      else if(action==='save'){
        const projects=root()?.closest('.sc-lab-app')?._scLabProjects;
        if(!projects?.add)throw new Error('The active project store is unavailable.');
        projects.add('executionJobs',{type:'checkpointed-compute-job',job,checkpoints:state.checkpoints,recordedAt:new Date().toISOString()},`Compute job saved: ${job.method}`);
      }
      await refresh(); announce(`${action} completed.`,'ready');
    } catch(error){state.lastError={message:error.message,at:new Date().toISOString()};announce(error.message,'error');}
  }
  function examplePayload() {
    const type=el('example')?.value||'sweep';
    const projectId=activeProjectId();
    if(type==='bootstrap')return {method:'uncertainty.bootstrap_mean_interval',inputs:{values:[12.1,11.8,12.5,12.0,11.9,12.3,12.2,11.7],resamples:20000},parameters:{confidence:.95,checkpointChunkSize:250},random_seed:27,project_id:projectId,requested_outputs:['summary','values']};
    const values=Array.from({length:1000},(_,index)=>Number(((index+1)/1000).toFixed(4)));
    return {method:'simulation.parameter_sweep',inputs:{model:'logistic_growth',parameter:'rate',values,fixed:{initial:10,carryingCapacity:100,time:10}},parameters:{checkpointChunkSize:50},project_id:projectId,requested_outputs:['summary','values']};
  }
  async function submitExample() {
    try {
      announce('Submitting checkpointed numerical job…','loading');
      const priority=Number(el('priority')?.value||50), cacheMode=el('cache')?.value||'use';
      const job=await Lab.ComputeClient.queueCore(examplePayload(),{priority,cacheMode,timeoutSeconds:600,maxAttempts:2,idempotencyKey:`v0272-${Date.now()}`});
      state.selectedJobId=job.jobId; await refresh(); announce(`Job ${job.jobId} submitted.`,'ready');
    } catch(error){state.lastError={message:error.message,at:new Date().toISOString()};announce(error.message,'error');}
  }
  async function refresh() {
    if(!Lab.ComputeClient?.isConfigured?.()){announce('Configure the Python Compute Core to use checkpointed long-running jobs.','warning');return;}
    const projectId=activeProjectId();
    try {
      const [queue,cache,jobs]=await Promise.all([Lab.ComputeClient.queueStatus(),Lab.ComputeClient.cacheStatus(),Lab.ComputeClient.listJobs({project_id:projectId,limit:50})]);
      state.queue=queue;state.cache=cache;state.jobs=jobs.jobs||[];
      if(state.selectedJobId&&!state.jobs.some(job=>job.jobId===state.selectedJobId))state.selectedJobId=null;
      if(!state.selectedJobId&&state.jobs.length)state.selectedJobId=state.jobs[0].jobId;
      renderMetrics();renderJobs();
      if(state.selectedJobId){try{state.checkpoints=await Lab.ComputeClient.checkpoints(state.selectedJobId,20);}catch(_){state.checkpoints=null;}}
      renderDetail();announce(`Queue ready: ${state.jobs.length} project jobs loaded.`,'ready');
    } catch(error){state.lastError={message:error.message,at:new Date().toISOString()};announce(error.message,'error');}
  }
  async function purgeCache(){if(!W.confirm('Purge all cached compute results?'))return;try{await Lab.ComputeClient.purgeCache();await refresh();announce('Compute result cache purged.','ready');}catch(error){announce(error.message,'error');}}
  function mount(){const panel=root();if(!panel||panel.dataset.scLongJobsMounted==='1')return;panel.dataset.scLongJobsMounted='1';state.mounted=true;el('refresh')?.addEventListener('click',refresh);el('submit')?.addEventListener('click',submitExample);el('purge')?.addEventListener('click',purgeCache);refresh();state.timer=W.setInterval(()=>{if(root()&&!root().hidden)refresh();},4000);D.addEventListener('sc-lab:module-unmounting',()=>{if(state.timer)W.clearInterval(state.timer);},{once:true});}
  function status(){return Object.assign({},state,{version:VERSION,backendConfigured:!!Lab.ComputeClient?.isConfigured?.(),projectId:activeProjectId()});}
  Lab.LongRunningJobsStudio={version:VERSION,init:mount,refresh,status};W.SCLabLongJobsV0272={status,refresh,submitExample};
  if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
})(window,document);
