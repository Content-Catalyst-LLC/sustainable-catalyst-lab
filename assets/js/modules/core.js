(function(w){'use strict';
const Lab=w.SCLab=w.SCLab||{};
Lab.util={
 uid(prefix='id'){return prefix+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8)},
 now(){return new Date().toISOString()},
 esc(value){return String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))},
 download(name,text,type='text/plain'){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},0)},
 fmt(date){if(!date)return 'Unknown';const d=new Date(date);return Number.isNaN(d.getTime())?String(date):d.toLocaleString()},
 fingerprint(value){let h=2166136261;const s=JSON.stringify(value);for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16)},
 toast(root,message){const el=root.querySelector('[data-lab-toast]');if(!el)return;el.textContent=message;el.hidden=false;clearTimeout(el._t);el._t=setTimeout(()=>el.hidden=true,2800)},
 fetchJson(url,options={}){return fetch(url,options).then(async r=>{const body=await r.json().catch(()=>({}));if(!r.ok)throw new Error(body.message||`HTTP ${r.status}`);return body})}
};
})(window);
