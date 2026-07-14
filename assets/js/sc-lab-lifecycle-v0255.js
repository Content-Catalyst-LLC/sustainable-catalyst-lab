(function (W, D) {
  'use strict';
  if (W.__SCLabLifecycleV0255) return;
  W.__SCLabLifecycleV0255 = true;
  const C = W.SCLabLifecycleConfigV0255 || {};
  const cleanups = new Map();
  let active = String(C.module || 'overview');
  let cleaned = false;

  function root() { return D.querySelector('[data-sc-lab-lifecycle="0.25.5"]'); }
  function addCleanup(module, fn) {
    module = String(module || active);
    if (typeof fn !== 'function') return fn;
    if (!cleanups.has(module)) cleanups.set(module, new Set());
    cleanups.get(module).add(fn);
    return fn;
  }
  function cleanup(module, reason) {
    const groups = module === '*' ? Array.from(cleanups.keys()) : [String(module || active)];
    groups.forEach(key => {
      const set = cleanups.get(key);
      if (!set) return;
      Array.from(set).reverse().forEach(fn => { try { fn(reason || 'unmount'); } catch (e) { console.warn('[SC Lab lifecycle cleanup]', e); } });
      set.clear(); cleanups.delete(key);
    });
  }
  function scope(module) {
    module = String(module || active);
    return {
      cleanup: fn => addCleanup(module, fn),
      timeout(fn, ms) { const id = W.setTimeout(fn, ms); addCleanup(module, () => W.clearTimeout(id)); return id; },
      interval(fn, ms) { const id = W.setInterval(fn, ms); addCleanup(module, () => W.clearInterval(id)); return id; },
      frame(fn) { const id = W.requestAnimationFrame(fn); addCleanup(module, () => W.cancelAnimationFrame(id)); return id; },
      observer(observer) { if (observer && typeof observer.disconnect === 'function') addCleanup(module, () => observer.disconnect()); return observer; },
      controller(controller) { if (controller && typeof controller.abort === 'function') addCleanup(module, () => controller.abort()); return controller; },
      listen(target, type, listener, options) { if (!target?.addEventListener) return listener; target.addEventListener(type, listener, options); addCleanup(module, () => target.removeEventListener(type, listener, options)); return listener; }
    };
  }
  function heap() { const p = W.performance; return p?.memory ? { usedJSHeapSize:p.memory.usedJSHeapSize,totalJSHeapSize:p.memory.totalJSHeapSize,jsHeapSizeLimit:p.memory.jsHeapSizeLimit } : null; }
  function status() {
    const r = root();
    return { version:'0.25.5', mode:'isolated-module-lifecycle', activeModule:active, panelCount:r?r.querySelectorAll('[data-lab-module]').length:0, nodeCount:r?r.querySelectorAll('*').length:0, cleanupScopes:cleanups.size, cleanupCallbacks:Array.from(cleanups.values()).reduce((n,s)=>n+s.size,0), heap:heap(), duplicateGuard:true, fullTeardownNavigation:true };
  }
  function announce(name, detail) { D.dispatchEvent(new CustomEvent(name,{detail:detail||{}})); }
  function destination(module) { const u=new URL(W.location.href); u.searchParams.set('sc_lab_module',module); u.searchParams.delete('sc_lab_safe'); return u.toString(); }
  function navigate(module) {
    module=/^[a-z0-9][a-z0-9-]{0,79}$/.test(String(module||''))?String(module):'overview';
    announce('sc:lab:module-unmounting',{module:active,nextModule:module,version:'0.25.5'});
    announce('sc-lab:module-unmounting',{module:active,nextModule:module,version:'0.25.5'});
    cleanup(active,'navigation');
    cleaned=true;
    W.location.assign(destination(module));
  }
  function diagnostics() {
    const r=root(), out=r?.querySelector('[data-sc-lab-lifecycle-diagnostics]');
    if (!out) return;
    out.hidden=!out.hidden; out.textContent=JSON.stringify(status(),null,2);
  }
  function click(event) {
    const r=root(); if (!r) return;
    const action=event.target.closest('[data-sc-lab-lifecycle-action]');
    if (action && r.contains(action)) { event.preventDefault(); event.stopImmediatePropagation(); const a=action.dataset.scLabLifecycleAction; if(a==='overview')navigate('overview'); else if(a==='reload')W.location.reload(); else diagnostics(); return; }
    const nav=event.target.closest('[data-lab-module-button],[data-open-module]');
    if (nav && r.contains(nav)) { const module=nav.dataset.labModuleButton||nav.dataset.openModule; if(module){event.preventDefault();event.stopImmediatePropagation();navigate(module);} }
  }
  function boot() {
    const r=root(); if(!r||r.dataset.scLabLifecycleBooted==='1')return;
    r.dataset.scLabLifecycleBooted='1'; active=r.dataset.scLabActiveModule||active;
    D.addEventListener('click',click,true);
    W.addEventListener('pagehide',()=>{ if(!cleaned)cleanup('*','pagehide'); },{once:true});
    W.addEventListener('beforeunload',()=>{ if(!cleaned)cleanup('*','beforeunload'); },{once:true});
    D.addEventListener('visibilitychange',()=>{ if(D.hidden){ const s=status(); r.dataset.scLabLastNodeCount=String(s.nodeCount); } });
    const detail={module:active,panel:r.querySelector('[data-lab-module]'),version:'0.25.5',lifecycle:scope(active)};
    announce('sc:lab:module-mounted',detail);
    announce('sc-lab:module-mounted',detail);
    announce('sc-lab:module-opened',detail);
    const s=status();
    if(s.nodeCount>Number(C.warningBudget||5000)) console.warn('[Sustainable Catalyst Lab v0.25.5] DOM warning budget exceeded',s);
    if(s.nodeCount>Number(C.nodeBudget||6500)) r.classList.add('sc-lab-over-budget-v0255');
  }
  W.SCLabLifecycleV0255={scope,register:addCleanup,cleanup,status,navigate};
  if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})(window,document);
