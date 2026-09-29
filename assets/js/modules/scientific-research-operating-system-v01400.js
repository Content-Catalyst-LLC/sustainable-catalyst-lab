(function(w){'use strict';
const V='0.140.0';
const phases=['question','design','data','compute','analysis','evidence','interpretation','review','reproduction','publication','living-research','research-program'];
function packet(x){x=x||{};return {schema:'sc-lab-scientific-research-os-client/0.140.0',version:V,projectId:x.projectId||x.studyId||null,studyId:x.studyId||x.projectId||null,declaredPhase:phases.includes(x.phase)?x.phase:'question',phaseDeclaredByUser:true,sourceAuthorityPreserved:true,automaticPhaseAdvance:false,automaticScientificValidity:false,automaticPublicationAcceptance:false};}
w.SCLabScientificResearchOperatingSystemV01400={version:V,phases:phases.slice(),packet};
})(window);
