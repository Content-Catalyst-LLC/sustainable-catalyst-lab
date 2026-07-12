const fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..'),out=process.argv[2];fs.mkdirSync(out,{recursive:true});
const context={window:{},localStorage:{getItem(){return null},setItem(){},removeItem(){}},console,TextEncoder,TextDecoder,Uint8Array,Uint32Array};context.window.window=context.window;context.window.localStorage=context.localStorage;vm.createContext(context);
for(const f of ['assets/js/modules/core.js','assets/js/modules/calculators.js','assets/js/modules/method-contracts.js'])vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),context,{filename:f});
const M=context.window.SCLab.MethodContracts;
for(const [id,meta] of Object.entries(M.languages))fs.writeFileSync(path.join(out,`kinetic.${meta.extension}`),M.generate('kinetic',id));
fs.writeFileSync(path.join(out,'kinetic.ipynb'),JSON.stringify(M.notebook('kinetic'),null,2));
