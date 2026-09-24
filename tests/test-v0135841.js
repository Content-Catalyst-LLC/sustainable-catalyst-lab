const fs=require('fs'); const path=require('path'); const root=path.resolve(__dirname,'..');
const src=fs.readFileSync(path.join(root,'assets/js/modules/graph-studio-live-binding-v013584.js'),'utf8');
function ok(v,m){if(!v)throw new Error(m)}
ok(!src.includes('layoutButton?.click()'),'synthetic layout click must be removed');
ok(src.includes("addEventListener('click',e=>") && src.includes('},true)'),'persistent stage click delegation must use capture');
ok(src.includes('applyProvenanceLayout(stage,state.layout)'),'layout restore must use direct geometry');
ok(src.includes("setAttribute('transform'"),'layout switch must update existing node geometry');
ok(src.includes('programmaticLayoutClick:false'),'public status must report no synthetic clicks');
console.log('PASS - v0.135.8.4.1 JS provenance interaction regression contract');
