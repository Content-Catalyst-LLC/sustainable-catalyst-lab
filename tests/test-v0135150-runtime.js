function assert(x,m){if(!x)throw new Error(m)}
const events=[];
const packet={thread:{id:'t1',title:'Review',annotations:[{id:'a1',kind:'observation',scope:'path',targetId:'path:0'}]},resolutionRecord:{id:'rr1'},auditRecord:{id:'au1',events}};
const audit={contextPacket:()=>packet,appendEvent:(x)=>{if(!x.verificationRef)return false;events.push({id:'e1',...x});return true}};
global.window={SCLab:{GraphStudioReviewAuditV0135140:audit},setTimeout:()=>0,requestAnimationFrame:(f)=>f(),sessionStorage:{setItem(){},getItem(){return null}}};
global.document={readyState:'complete',querySelector:()=>null,getElementById:()=>null,addEventListener:()=>{}};
global.CustomEvent=function(){};
require('../assets/js/modules/graph-studio-verification-artifacts-v0135150.js');
const api=window.SCLab.GraphStudioVerificationArtifactsV0135150;
const b=api.recordVerificationBundle({annotationId:'a1',outcome:'passed',verificationMethod:'method-check',verificationScope:'method + rerun',note:'checked',artifacts:[{artifactType:'method',artifactRef:'method-rev-2',versionRef:'rev2',sha256:'a'.repeat(64)},{artifactType:'execution',artifactRef:'run-7',executionRef:'run-7'}]});
assert(b&&b.id,'bundle recorded');assert(events.length===1,'one audit event');assert(events[0].verificationRef===b.id,'audit verificationRef binds bundle id');assert(b.verificationEventId==='e1','bundle binds audit event');assert(b.artifacts.length===2,'multi artifact');assert(api.status().bundleCount===1,'status bundle count');assert(api.status().artifactCount===2,'status artifact count');assert(api.status().fullGraphRedrawForVerificationArtifacts===false,'incremental contract');
console.log('PASS - v0.135.15.0 verification bundle runtime');
