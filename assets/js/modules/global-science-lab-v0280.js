(() => {
  'use strict';
  const cfg = window.SCLabGlobalScienceV0280Config || {};
  const roots = [...document.querySelectorAll('[data-global-science-v0280-root]')];
  if (!roots.length) return;
  const jsonHeaders = {'Content-Type':'application/json','X-WP-Nonce':cfg.nonce || ''};
  const api = async (path, options={}) => {
    const res = await fetch(`${cfg.restBase}${path}`, {credentials:'same-origin', ...options, headers:{...jsonHeaders,...(options.headers||{})}});
    const body = await res.json().catch(()=>({message:`HTTP ${res.status}`}));
    if (!res.ok) throw new Error(body.message || body.code || `HTTP ${res.status}`);
    return body;
  };
  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
  const saveBlob = (name, data, type) => { const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([data],{type})); a.download=name; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),1000); };
  roots.forEach(root => {
    const status=root.querySelector('[data-gs-status]');
    const setStatus=(text,state='unavailable')=>{status.textContent=text;status.dataset.state=state;};
    root.querySelectorAll('[data-gs-tab]').forEach(btn=>btn.addEventListener('click',()=>{
      root.querySelectorAll('[data-gs-tab]').forEach(x=>x.setAttribute('aria-selected',String(x===btn)));
      root.querySelectorAll('[data-gs-panel]').forEach(p=>p.hidden=p.dataset.gsPanel!==btn.dataset.gsTab);
    }));
    api('/health').then(h=>setStatus(h.message||h.state,h.state)).catch(e=>setStatus(e.message));
    const form=root.querySelector('[data-gs-search-form]');
    form?.addEventListener('submit',async ev=>{
      ev.preventDefault(); const target=root.querySelector('[data-gs-results]'); target.innerHTML='<p>Searching official records…</p>';
      const qs=new URLSearchParams(new FormData(form)); qs.set('limit','40');
      try {
        const body=await api(`/records?${qs}`); const records=Array.isArray(body)?body:(body.records||body.items||body.data||[]);
        if(!records.length){target.innerHTML='<p class="sc-gs-empty">No matching records were returned.</p>';return;}
        target.innerHTML=records.map(r=>`<article class="sc-gs-card"><p class="sc-gs-card-type">${escapeHtml(r.discipline||r.record_type||'Scientific record')}</p><h3>${escapeHtml(r.title||r.name||r.dataset_id||r.id)}</h3><p>${escapeHtml(r.description||r.summary||'Official source record')}</p><dl><dt>Provider</dt><dd>${escapeHtml(r.provider||r.source_id||r.source||'Official source')}</dd><dt>Updated</dt><dd>${escapeHtml(r.updated_at||r.observed_at||r.temporal_end||'Latest available')}</dd></dl><button type="button" data-gs-select-record="${escapeHtml(r.id||r.record_id||r.dataset_id||'')}">Select</button></article>`).join('');
        target.querySelectorAll('[data-gs-select-record]').forEach(b=>b.addEventListener('click',()=>{ const input=root.querySelector('[data-gs-export-record]'); input.value=b.dataset.gsSelectRecord; root.querySelector('[data-gs-tab="export"]').click(); }));
      } catch(e){target.innerHTML=`<p class="sc-gs-error">${escapeHtml(e.message)}</p>`;}
    });
    root.querySelector('[data-gs-series-form]')?.addEventListener('submit',async ev=>{
      ev.preventDefault(); const id=new FormData(ev.currentTarget).get('series_id'); const out=root.querySelector('[data-gs-series-output]'); out.textContent='Loading…';
      try { const body=await api(`/timeseries?series_id=${encodeURIComponent(id)}`); const points=body.points||body.items||body.data||body; out.textContent=JSON.stringify({series_id:id,points:Array.isArray(points)?points.slice(0,100):points},null,2); } catch(e){out.textContent=e.message;}
    });
    root.querySelector('[data-gs-compare]')?.addEventListener('click',async()=>{
      const parse=s=>s.split(/[\s,;]+/).filter(Boolean).map(Number).filter(Number.isFinite); const out=root.querySelector('[data-gs-compare-output]');
      try { const body=await api('/compare',{method:'POST',body:JSON.stringify({a:parse(root.querySelector('[data-gs-series-a]').value),b:parse(root.querySelector('[data-gs-series-b]').value)})}); out.textContent=JSON.stringify(body,null,2); } catch(e){out.textContent=e.message;}
    });
    root.querySelector('[data-gs-notebook]')?.addEventListener('click',async()=>{
      const id=root.querySelector('[data-gs-export-record]').value.trim(); const out=root.querySelector('[data-gs-export-status]');
      try { const nb=await api('/notebook',{method:'POST',body:JSON.stringify({record_id:id})}); saveBlob(`sc-lab-${id||'global-science'}.ipynb`,JSON.stringify(nb,null,2),'application/x-ipynb+json'); out.textContent='Notebook downloaded without embedded credentials.'; } catch(e){out.textContent=e.message;}
    });
    root.querySelector('[data-gs-workbench]')?.addEventListener('click',()=>{
      const recordId=root.querySelector('[data-gs-export-record]').value.trim(); const payload={schema:'sc-lab-workbench-handoff/1.0',release:'0.28.0',record_id:recordId,source:'research-lab-global-science'};
      localStorage.setItem('sc_workbench_handoff',JSON.stringify(payload)); window.dispatchEvent(new CustomEvent('sc:workbench-handoff',{detail:payload})); root.querySelector('[data-gs-export-status]').textContent='Workbench handoff prepared.';
    });
  });
  window.SCLabGlobalScienceV0280={version:'0.28.0',status:()=>({roots:roots.length,configured:Boolean(cfg.restBase)})};
})();
