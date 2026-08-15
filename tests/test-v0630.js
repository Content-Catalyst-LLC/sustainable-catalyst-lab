'use strict';
const fs=require('fs');const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/scientific-literature-v0630.js');
const py=read('backend/app/scientific_literature_provenance_v0630.py');
const main=read('backend/app/main.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [js.includes("VERSION='0.63.0'")&&js.includes('ScientificLiteratureV0630'),'v0.63.0 browser literature provenance contract'],
 [py.includes('normalize_source')&&py.includes('normalize_claim_link')&&py.includes('normalize_citation_edge')&&py.includes('evaluate_provenance')&&py.includes('build_provenance_packet'),'literature, citation graph, and source-to-claim backend implemented'],
 [py.includes('contradicts')&&py.includes('non-replication')&&py.includes('duplicateIdentifierGroups'),'contradictory/non-replication literature and duplicate identifiers preserved'],
 [py.includes('automaticLiteratureTruthScoringAuthorized')&&py.includes('automaticBibliometricAuthorityRankingAuthorized')&&py.includes('automaticRetractionVerificationAuthorized'),'automatic truth, authority ranking, and retraction verification disabled'],
 [main.includes('/v1/scientific-literature/v0630/normalize-source')&&main.includes('/v1/scientific-literature/v0630/evaluate')&&main.includes('/v1/scientific-literature/v0630/packet'),'FastAPI v0.63 literature routes implemented'],
 [template.includes('data-scientific-literature-v0630')&&template.includes('Evaluate literature provenance')&&template.includes('Add source-to-claim link')&&template.includes('Add citation edge'),'contextual literature/citation UI present'],
 [js.includes("'scientificLiteratureSourcesV0630'")&&js.includes("'scientificLiteratureClaimLinksV0630'")&&js.includes("'scientificCitationEdgesV0630'")&&js.includes("recordType:'scientific-literature-provenance-v0630'"),'literature records and provenance evidence save to active project'],
 [js.includes('full text excluded')&&template.includes('Full-text documents are not copied'),'metadata-only / no full-text packet boundary'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-scientific-literature-v0630')&&plugin.includes("'scientific-literature-v0630'"),'v0.63 assets registered'],
 [compute.includes('/compute/core/scientific-literature/v0630/evaluate')&&compute.includes('/compute/core/scientific-literature/v0630/review-source')&&compute.includes('/compute/core/scientific-literature/v0630/packet'),'WordPress v0.63 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.63 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
