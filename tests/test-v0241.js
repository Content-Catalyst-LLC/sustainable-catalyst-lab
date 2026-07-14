'use strict';const assert=require('node:assert/strict');const path=require('node:path');
global.window={SCLab:{GeneticsGenomicsSequenceAnalysis:{definitions:Array(48),benchmarks:Array(48),categories:Array(8)}},setTimeout:()=>0,addEventListener:()=>{}};
require(path.resolve(__dirname,'../assets/js/modules/genomics-production-v0241.js'));
const api=window.SCLab.GenomicsProduction;assert.equal(api.VERSION,'0.24.1');assert.equal(api.ENGINE_VERSION,'0.24.0');assert.equal(api.health().methodCount,48);assert.equal(typeof api.repair,'function');
console.log('Lab v0.24.1 JS structural tests passed: production API and preserved 48/48/8 contract.');
