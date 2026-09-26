function assert(x,m){if(!x)throw new Error(m)}
const nodes=[{id:'data',label:'Dataset',type:'dataset',objectRef:'data'},{id:'method',label:'Method',type:'method',objectRef:'method'},{id:'run',label:'Run',type:'execution',objectRef:'run'},{id:'fig',label:'Figure',type:'figure',objectRef:'fig'},{id:'claim',label:'Claim',type:'claim',objectRef:'claim'}];
const edges=[{id:'e1',from:'data',to:'method',relation:'input-to'},{id:'e2',from:'method',to:'run',relation:'executed-by'},{id:'e3',from:'run',to:'fig',relation:'generated'},{id:'e4',from:'fig',to:'claim',relation:'reported-as'}];
const m={nodes,edges,nodeMap:new Map(nodes.map(n=>[n.id,n]))};
const native={buildModel:()=>m,status:()=>({selectedNode:'method'})};
global.window={SCLab:{GraphStudioNativeProvenanceV013585:native},SCLabGraphStudioNativeProvenanceV013585:native,setTimeout:()=>0,requestAnimationFrame:f=>f(),sessionStorage:{setItem(){},getItem(){return null}}};
global.document={readyState:'complete',querySelector:()=>null,getElementById:()=>null,addEventListener:()=>{}};global.CustomEvent=function(){};
require('../assets/js/modules/graph-studio-revision-impact-v0135160.js');
const api=window.SCLab.GraphStudioRevisionImpactV0135160;
const a=api.analyze({seedId:'method',direction:'both',maxDepth:6,revisionAction:'revise-method',revisionRef:'method-v2'});
assert(a&&a.seedId==='method','analysis');assert(a.downstream.affectedNodeIds.join(',')==='run,fig,claim','downstream order');assert(a.downstream.directCount===1,'direct');assert(a.downstream.transitiveCount===2,'transitive');assert(a.upstream.affectedNodeIds[0]==='data','upstream');assert(api.status().fullGraphRedrawForImpact===false,'incremental');assert(api.status().automaticScientificInvalidation===false,'no invalidation');
console.log('PASS - v0.135.16.0 revision impact runtime');
