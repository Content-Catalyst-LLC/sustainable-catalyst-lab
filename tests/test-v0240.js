'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
global.window={SCLab:{}};
require(path.resolve(__dirname,'../assets/js/modules/genetics-genomics-sequence-analysis-v0240.js'));
const api=global.window.SCLab.GeneticsGenomicsSequenceAnalysis;
assert.equal(api.VERSION,'0.24.0');
assert.equal(api.definitions.length,48);
assert.equal(api.benchmarks.length,48);
assert.equal(api.categories.length,8);
for(const b of api.benchmarks){
 const got=api.execute(b.methodId,b.inputs).value, exp=b.expected;
 if(typeof exp==='number')assert.ok(Math.abs(got-exp)<=Math.max(b.tolerance,Math.abs(exp)*1e-8),`${b.methodId}: ${got} != ${exp}`);
 else assert.deepEqual(got,exp,b.methodId);
}
const batch=api.batchExecute([{methodId:'gc-content',inputs:{sequence:'ACGT'}},{methodId:'hamming-distance',inputs:{reference:'AC',query:'A'}}]);
assert.equal(batch.successCount,1);assert.equal(batch.errorCount,1);
console.log('Lab v0.24.0 JS tests passed: 48 methods, 48 benchmarks, 8 categories, batch isolation.');
