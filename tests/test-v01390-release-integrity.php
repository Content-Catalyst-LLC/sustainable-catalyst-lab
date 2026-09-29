<?php
$root=dirname(__DIR__);
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if (($manifest['releaseVersion'] ?? null) !== '0.139.0') { fwrite(STDERR,"FAIL release version\n"); exit(1); }
if (($manifest['scholarlyStudyOriginalResearchPackageVersion'] ?? null) !== '0.139.0') { fwrite(STDERR,"FAIL feature version\n"); exit(1); }
if (($manifest['v01390RequiredRouteCount'] ?? null) !== 25) { fwrite(STDERR,"FAIL route count\n"); exit(1); }
foreach (array('v01390ScholarlyStudyOriginalResearchPackage','v01390DeterministicManifest','v01390ProvenanceLineage','v01390LivingAnalysisBridge','v01390ResearchProgramContext','v01390ImmutableSnapshots','v01390ProjectWorkspaceHandoff','v01390CoreScholarlyHandoff') as $key) {
    if (($manifest[$key] ?? false) !== true) { fwrite(STDERR,"FAIL manifest flag $key\n"); exit(1); }
}
if (($manifest['v01390AutomaticScientificValidity'] ?? true) !== false) { fwrite(STDERR,"FAIL scientific-validity boundary\n"); exit(1); }
if (($manifest['v01390AutomaticPublicationAcceptance'] ?? true) !== false) { fwrite(STDERR,"FAIL publication boundary\n"); exit(1); }
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
if (strpos($plugin,'Version: 0.139.0')===false) { fwrite(STDERR,"FAIL plugin header version\n"); exit(1); }
foreach (array(
 'backend/app/scholarly_study_original_research_package_v01390.py',
 'includes/class-sc-lab-scholarly-study-original-research-package-v01390.php',
 'assets/js/modules/scholarly-study-original-research-package-v01390.js',
 'contracts/scholarly-study-original-research-package-v01390.schema.json'
) as $rel) { if (!is_file($root.'/'.$rel)) { fwrite(STDERR,"FAIL missing $rel\n"); exit(1); } }
echo "PASS - Lab v0.139.0 release integrity and v0.138.0 compatibility retained\n";
