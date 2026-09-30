(function(w,d){'use strict';
  const VERSION='0.152.0.2';
  function roots(){return Array.from(d.querySelectorAll('.sc-lab-app'));}
  function canonical(id){return w.SCLabRuntimeV02631?.resolveModule?.(id)||String(id||'overview');}
  function open(root,id){
    id=canonical(id);
    const panels=Array.from(root.querySelectorAll('[data-lab-module]'));
    const panel=panels.find(p=>p.dataset.labModule===id);
    if(!panel){w.SCLabRuntimeV02631?.navigate?.(id);return false;}
    panels.forEach(p=>{p.hidden=p!==panel;});
    root.querySelectorAll('[data-lab-module-button]').forEach(b=>b.classList.toggle('is-active',canonical(b.dataset.labModuleButton)===id));
    root.dataset.activeModule=id;
    root.dispatchEvent(new CustomEvent('sc-lab:module-opened',{detail:{module:id,recovery:true,version:VERSION}}));
    root.querySelector('[data-lab-nav]')?.classList.remove('is-open');
    root.querySelector('[data-lab-nav-toggle]')?.setAttribute('aria-expanded','false');
    try{panel.scrollIntoView({block:'start'});}catch(_){}
    return true;
  }
  function bind(root){
    if(root.dataset.scLabNavigationRecoveryBound==='1')return;
    root.dataset.scLabNavigationRecoveryBound='1';
    root.addEventListener('click',e=>{
      const b=e.target.closest('[data-lab-module-button],[data-open-module]');
      if(!b||!root.contains(b))return;
      // The full app owns navigation once it is healthy. Recovery only intervenes if it has not booted.
      if(root.dataset.scLabAppReady==='1'&&root.dataset.scLabAppFailed!=='1')return;
      const id=b.dataset.labModuleButton||b.dataset.openModule;
      if(id){e.preventDefault();open(root,id);}
    },true);
    root.dataset.scLabNavigationRecoveryVersion=VERSION;
    root.dataset.scLabPanelRetentionRecovery='1';
  }
  function boot(){roots().forEach(bind);}
  if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',boot,{once:true}); else boot();
  d.addEventListener('sc-lab:app-error',e=>{const r=e.detail?.root;if(r){bind(r);r.dataset.scLabNavigationRecoveryActive='1';}});
  w.SCLabNavigationRecoveryV015201={version:VERSION,open,bind,status:()=>({version:VERSION,roots:roots().length,ready:roots().filter(r=>r.dataset.scLabAppReady==='1').length,failed:roots().filter(r=>r.dataset.scLabAppFailed==='1').length})};
})(window,document);
