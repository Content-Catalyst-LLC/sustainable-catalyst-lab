(function(w){'use strict';
const V='0.139.0';
const arr=v=>Array.isArray(v)?v:[];
const ref=x=>typeof x==='string'?x:(x&&((x.ref||x.objectRef||x.object_ref||x.id)))||null;
function artifactRefs(p){
  const out=[];['methods','datasets','executions','models','analyses','figures','tables','claims','evidence','findings','manuscripts','reviews','reproductionPackages'].forEach(k=>arr(p&&p[k]).forEach(x=>{const r=ref(x);if(r&&!out.includes(r))out.push(r);}));
  return out;
}
w.SCLabScholarlyStudyOriginalResearchPackageV01390={version:V,artifactRefs:artifactRefs,packet:function(p){return {schema:'sc-lab-original-research-package-client/0.139.0',version:V,package:p||{},artifactRefs:artifactRefs(p||{}),sourceAuthorityPreserved:true,automaticScientificValidity:false,automaticPublicationAcceptance:false};}};
})(window);
