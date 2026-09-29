(function(w){'use strict';
const NS='SCLabReproducibleNeuralResearchPackageV01418';
function components(pkg){return Array.isArray(pkg?.components)?pkg.components:[];}
function sectionCount(pkg,section){return components(pkg).filter(x=>x?.section===section).length;}
function verificationBadge(component){const s=component?.verificationState||'unverified';return String(s).replaceAll('-',' ');}
function completenessLabel(report){const f=Number(report?.descriptiveCompletenessFraction);return Number.isFinite(f)?`${Math.round(f*100)}% declared completeness`:'completeness not calculated';}
w[NS]={version:'0.141.8',components,sectionCount,verificationBadge,completenessLabel,workspaceExecutionAuthority:true,platformCoreCanonicalAuthority:true,labExecutesTraining:false,labExecutesReproduction:false,automaticScientificValidity:false,automaticReproductionCertification:false,automaticReplicationCertification:false,packageCompletenessIsScientificValidity:false,packageCompletenessIsReproduction:false,packageCompletenessIsReplication:false,predictionIsEvidence:false,boundary:'A complete research package records materials and instructions; it does not by itself certify scientific validity, successful reproduction, independent replication, or publication acceptance.'};
})(window);
