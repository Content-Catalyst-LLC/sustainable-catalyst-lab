(function (W, D) {
  'use strict';
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.27.1';
  const state = {
    ready:false, mounted:false, benchmarkCount:0, selected:null, running:false,
    lastResult:null, lastSuite:null, lastConvergence:null, lastError:null,
    catalogSource:null, events:[]
  };
  let benchmarks = [];

  function panel(){ return D.querySelector('[data-lab-module="numerical-validation"]'); }
  function el(name){ return panel()?.querySelector(`[data-benchmark-${name}]`) || null; }
  function esc(value){ return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[ch])); }
  function pretty(value){ return JSON.stringify(value, null, 2); }
  function event(name, detail={}){ state.events.push({at:new Date().toISOString(),name,detail}); if(state.events.length>100)state.events.shift(); }
  function announce(message,tone='info'){ const target=el('status'); if(target){target.textContent=message;target.dataset.tone=tone;} event('status',{message,tone}); }
  function setBusy(value){ state.running=!!value; panel()?.classList.toggle('is-running',!!value); ['run','run-all','convergence'].forEach(name=>{const node=el(name);if(node)node.disabled=!!value;}); }
  function config(){ return W.SCLabConfig || {}; }
  async function fetchJSON(url){
    if(!url) throw new Error('Benchmark catalog endpoint is not configured.');
    const response=await fetch(url,{credentials:'same-origin',headers:{Accept:'application/json','X-WP-Nonce':config().nonce||''}});
    const body=await response.json().catch(()=>({}));
    if(!response.ok) throw new Error(body?.message||body?.detail||`HTTP ${response.status}`);
    return body;
  }
  function current(){ return benchmarks.find(row=>row.id===el('select')?.value)||benchmarks[0]||null; }
  function assertionLabel(row){
    const unit=row.unit?` ${row.unit}`:'';
    return `${row.path} · ${row.operation}${row.expected!==undefined?` · expected ${JSON.stringify(row.expected)}${unit}`:''}`;
  }
  function renderSelector(){
    const select=el('select'); if(!select)return;
    const groups=new Map();
    benchmarks.forEach(row=>{const key=String(row.domain||'other').replace(/-/g,' ');if(!groups.has(key))groups.set(key,[]);groups.get(key).push(row);});
    select.innerHTML=[...groups.entries()].map(([domain,rows])=>`<optgroup label="${esc(domain.replace(/\b\w/g,c=>c.toUpperCase()))}">${rows.map(row=>`<option value="${esc(row.id)}">${esc(row.title)}</option>`).join('')}</optgroup>`).join('');
    if(benchmarks[0])select.value=benchmarks[0].id;
    selectedChanged();
  }
  function selectedChanged(){
    const row=current(); if(!row)return;
    state.selected=row.id;
    if(el('title'))el('title').textContent=row.title;
    if(el('id'))el('id').textContent=`${row.id} · ${row.method}`;
    if(el('description'))el('description').textContent=row.description||'';
    if(el('tags'))el('tags').textContent=(row.tags||[]).join(' · ')||'known-answer benchmark';
    const list=el('assertions'); if(list)list.innerHTML=(row.assertions||[]).map(a=>`<li>${esc(assertionLabel(a))}</li>`).join('');
    const conv=el('convergence'); if(conv)conv.disabled=!row.convergence || state.running;
    const browser=browserReference(row);
    const ref=el('browser-reference');
    if(ref)ref.textContent=browser?pretty(browser):'No independent browser reference is registered for this benchmark.';
  }
  function mergeCatalog(localRows,remoteRows){
    const local=new Map((localRows||[]).map(row=>[row.id,row]));
    const remote=new Map((remoteRows||[]).map(row=>[row.id,row]));
    return [...new Set([...local.keys(),...remote.keys()])].map(id=>Object.assign({},local.get(id)||{},remote.get(id)||{}, {id})).sort((a,b)=>String(a.domain).localeCompare(String(b.domain))||String(a.title).localeCompare(String(b.title)));
  }
  async function loadCatalog(){
    const localUrl=config()?.validation?.catalogUrl||`${String(config().restBase||'').replace(/\/?$/,'/')}numerical/v0271/benchmarks`;
    const local=await fetchJSON(localUrl).catch(error=>{event('local-catalog-error',{message:error.message});return{benchmarks:[]};});
    let remote={benchmarks:[]};
    if(Lab.ComputeClient?.isConfigured?.()){
      try{remote=await Lab.ComputeClient.benchmarks();state.catalogSource='python-core';}
      catch(error){event('remote-catalog-error',{message:error.message});state.catalogSource='wordpress-catalog';}
    } else state.catalogSource='wordpress-catalog';
    benchmarks=mergeCatalog(local.benchmarks,remote.benchmarks);
    state.benchmarkCount=benchmarks.length;
    if(!benchmarks.length)throw new Error('No numerical benchmarks are available.');
    renderSelector(); state.ready=true; event('catalog-ready',{count:benchmarks.length,source:state.catalogSource});
  }
  function browserReference(row){
    switch(row?.id){
      case 'root.sqrt2.brentq': return {implementation:'browser-analytic',root:Math.sqrt(2),functionValue:0};
      case 'quadrature.polynomial.exact': return {implementation:'browser-analytic',integral:12};
      case 'interpolation.linear.reference': return {implementation:'browser-linear',values:[1,3]};
      case 'ode.exponential.analytic': return {implementation:'browser-analytic',finalValue:2*Math.E};
      case 'eigen.symmetric.2x2': return {implementation:'browser-analytic',eigenvalues:[1,3],trace:4,determinant:3};
      case 'optimization.quadratic.minimum': return {implementation:'browser-analytic',x:2,minimum:3};
      case 'sweep.photovoltaic.monotonic': return {implementation:'browser-formula',minimumOutput:800,maximumOutput:2000,monotonicIncreasing:true};
      case 'linear-system.reference.2x2': return {implementation:'browser-elimination',solution:[0,2.5],residualNorm:0};
      case 'sampled-integration.parabola': return {implementation:'browser-simpson',simpson:1/3,trapezoid:0.34375};
      default:return null;
    }
  }
  function renderAssertions(rows){
    const body=el('assertion-results'); if(!body)return;
    body.innerHTML=(rows||[]).map(row=>`<tr data-pass="${row.passed?'1':'0'}"><td>${row.passed?'PASS':'FAIL'}</td><td>${esc(row.path)}</td><td>${esc(row.operation)}</td><td><code>${esc(JSON.stringify(row.expected))}</code></td><td><code>${esc(JSON.stringify(row.actual))}</code></td><td>${esc(row.unit||'')}</td></tr>`).join('')||'<tr><td colspan="6">No assertion results.</td></tr>';
  }
  function renderSingle(result){
    state.lastResult=result; state.lastError=null;
    const summary=el('summary');
    if(summary)summary.innerHTML=`<strong>${result.passed?'Benchmark passed':'Benchmark failed'}</strong><span>${esc(result?.benchmark?.title||'')}</span><small>${Number(result.benchmarkRuntimeMs||0).toFixed(2)} ms · ${esc(result.methodVersion||'')}</small>`;
    renderAssertions(result.assertions);
    if(el('python-output'))el('python-output').textContent=pretty(result.outputs||{});
    if(el('provenance'))el('provenance').textContent=pretty(result.provenance||{});
    const browser=browserReference(result.benchmark); if(el('browser-reference'))el('browser-reference').textContent=browser?pretty(browser):'No independent browser reference is registered for this benchmark.';
    const exp=el('export'); if(exp)exp.disabled=false;
  }
  function renderSuite(result){
    state.lastSuite=result;
    const table=el('suite-results'); if(!table)return;
    table.innerHTML=(result.results||[]).map(row=>`<tr data-pass="${row.passed?'1':'0'}"><td>${row.passed?'PASS':'FAIL'}</td><td>${esc(row?.benchmark?.title||row?.benchmark?.id||'')}</td><td><code>${esc(row?.benchmark?.method||'')}</code></td><td>${Number(row.benchmarkRuntimeMs||0).toFixed(2)} ms</td><td>${esc(row.error||'')}</td></tr>`).join('');
    if(el('suite-summary'))el('suite-summary').textContent=`${result.passed}/${result.benchmarkCount} passed in ${Number(result.runtimeMs||0).toFixed(2)} ms`;
    const exp=el('export'); if(exp)exp.disabled=false;
  }
  function renderConvergence(result){
    state.lastConvergence=result;
    const body=el('convergence-results'); if(!body)return;
    body.innerHTML=(result.rows||[]).map(row=>`<tr><td>${row.level}</td><td><code>${esc(JSON.stringify(row.parameters))}</code></td><td>${Number(row.actual).toPrecision(10)}</td><td>${Number(row.absoluteError).toExponential(4)}</td><td>${Number(row.runtimeMs||0).toFixed(3)} ms</td></tr>`).join('');
    if(el('convergence-summary'))el('convergence-summary').textContent=result.passed?'Convergence trend passed.':'Convergence trend requires review.';
  }
  async function runSelected(){
    if(!Lab.ComputeClient?.isConfigured?.()){announce('Python Compute Core must be configured to run benchmarks.','error');return;}
    const row=current(); if(!row)return;
    setBusy(true); announce(`Running ${row.title}…`,'loading');
    try{const result=await Lab.ComputeClient.runBenchmark(row.id);renderSingle(result);announce(result.passed?`${row.title} passed.`:`${row.title} failed one or more assertions.`,result.passed?'ready':'error');event('benchmark-complete',{id:row.id,passed:result.passed});}
    catch(error){state.lastError={message:error.message,at:new Date().toISOString()};announce(error.message,'error');event('benchmark-error',state.lastError);}
    finally{setBusy(false);selectedChanged();}
  }
  async function runAll(){
    if(!Lab.ComputeClient?.isConfigured?.()){announce('Python Compute Core must be configured to run the benchmark suite.','error');return;}
    setBusy(true); announce(`Running ${benchmarks.length} numerical benchmarks…`,'loading');
    try{const result=await Lab.ComputeClient.runBenchmarkSuite([]);renderSuite(result);announce(result.success?`All ${result.passed} benchmarks passed.`:`${result.failed} benchmark(s) failed.`,result.success?'ready':'error');event('suite-complete',{passed:result.passed,failed:result.failed});}
    catch(error){state.lastError={message:error.message,at:new Date().toISOString()};announce(error.message,'error');}
    finally{setBusy(false);selectedChanged();}
  }
  async function runConvergence(){
    const row=current(); if(!row?.convergence)return;
    if(!Lab.ComputeClient?.isConfigured?.()){announce('Python Compute Core must be configured to run convergence diagnostics.','error');return;}
    setBusy(true);announce(`Running convergence series for ${row.title}…`,'loading');
    try{const result=await Lab.ComputeClient.runBenchmarkConvergence(row.id);renderConvergence(result);announce(result.passed?'Convergence diagnostics passed.':'Convergence diagnostics require review.',result.passed?'ready':'warning');}
    catch(error){state.lastError={message:error.message,at:new Date().toISOString()};announce(error.message,'error');}
    finally{setBusy(false);selectedChanged();}
  }
  function download(){
    const payload={schema:'sc-lab-numerical-validation-export/1.0',version:VERSION,exportedAt:new Date().toISOString(),selectedBenchmark:state.selected,result:state.lastResult,suite:state.lastSuite,convergence:state.lastConvergence};
    const text=pretty(payload);
    if(Lab.util?.download)Lab.util.download('sc-lab-numerical-validation-report.json',text,'application/json');
    else{const blob=new Blob([text],{type:'application/json'});const link=D.createElement('a');link.href=URL.createObjectURL(blob);link.download='sc-lab-numerical-validation-report.json';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);}
  }
  function bind(){
    const root=panel(); if(!root||root.dataset.scBenchmarkMounted==='1')return;
    root.dataset.scBenchmarkMounted='1';state.mounted=true;
    el('select')?.addEventListener('change',selectedChanged);
    el('run')?.addEventListener('click',runSelected);
    el('run-all')?.addEventListener('click',runAll);
    el('convergence')?.addEventListener('click',runConvergence);
    el('export')?.addEventListener('click',download);
    loadCatalog().then(()=>announce(Lab.ComputeClient?.isConfigured?.()?`Benchmark Library ready with ${benchmarks.length} known-answer cases.`:`Loaded ${benchmarks.length} benchmark definitions. Configure Python Compute Core to execute them.`,Lab.ComputeClient?.isConfigured?.()?'ready':'warning')).catch(error=>{state.lastError={message:error.message,at:new Date().toISOString()};announce(error.message,'error');});
  }
  function status(){return Object.assign({},state,{benchmarkCount:benchmarks.length,backendConfigured:!!Lab.ComputeClient?.isConfigured?.()});}
  Lab.NumericalValidationStudio={version:VERSION,init:bind,runSelected,runAll,runConvergence,status,benchmarks:()=>benchmarks.slice()};
  W.SCLabNumericalValidationV0271={status,runSelected,runAll,runConvergence};
  if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
})(window,document);
