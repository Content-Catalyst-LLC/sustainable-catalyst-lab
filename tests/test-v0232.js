'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
global.window = { SCLab:{}, setTimeout:()=>0 };
require(path.resolve(__dirname,'../assets/js/modules/biosignal-visualization-comparison-v0232.js'));
const api=global.window.SCLab.BiosignalVisualizationComparison;
assert.ok(api); assert.equal(api.VERSION,'0.23.2'); assert.equal(api.modes.length,8); assert.equal(api.analysisMethods.length,16); assert.equal(api.benchmarks.length,16); assert.equal(api.annotationTypes.length,6);
function equivalent(actual, expected) {
  if (typeof expected === 'number') return Math.abs(Number(actual)-expected) <= Math.max(1e-8,Math.abs(expected)*1e-8);
  if (Array.isArray(expected)) return Array.isArray(actual)&&actual.length===expected.length&&actual.every((item,index)=>equivalent(item,expected[index]));
  if (expected && typeof expected === 'object') return actual&&Object.keys(expected).length===Object.keys(actual).length&&Object.entries(expected).every(([key,value])=>equivalent(actual[key],value));
  return actual===expected;
}
for (const benchmark of api.benchmarks) { const result=api.execute(benchmark.methodId,benchmark.inputs); assert.ok(equivalent(result.value,benchmark.expected),benchmark.methodId); }
const dataset=api.parseMultiChannelCsv('timeSeconds,ecg,ppg\n0,0,0\n0.5,1,0.4\n1,0,1');
assert.deepEqual(dataset.channelIds,['ecg','ppg']); assert.equal(dataset.times.length,3); assert.equal(dataset.sampleRateHz,2);
const lag=api.bestLagCorrelation([1,4,2,5,0,3],[4,2,5,0,3,9],2); assert.equal(lag.bestLagSamples,1); assert.ok(Math.abs(lag.bestCorrelation-1)<1e-12);
const annotation=api.createAnnotation('artifact',0.2,0.6,'motion'); const analysis=api.buildAnalysisRecord(dataset,{channelIds:['ecg','ppg'],referenceId:'ecg',comparisonId:'ppg',maxLagSamples:1,annotations:[annotation],smoothingWindow:2}); assert.equal(analysis.version,'0.23.2'); assert.equal(analysis.dataset.channelIds.length,2); assert.equal(analysis.annotations.length,1);
const svg=api.buildSvg(dataset,{channelIds:['ecg','ppg'],annotations:[annotation],smoothingWindow:2}); assert.match(svg,/sc-bv-svg/); assert.match(svg,/motion/); assert.match(svg,/Filtered/);
console.log('Lab v0.23.2 JS tests passed: 8 modes, 16 methods, 16 benchmarks, annotations, lag analysis, synchronized SVG.');
