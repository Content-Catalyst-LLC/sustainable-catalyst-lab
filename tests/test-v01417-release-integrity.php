<?php
$m=json_decode(file_get_contents('build/sc-lab-release-manifest.json'),true); $c=[];
$c['release']=($m['releaseVersion']??'')==='0.141.7';
$c['feature']=($m['embeddingExplorerVersion']??'')==='0.141.7';
$c['routes']=($m['v01417RequiredRouteCount']??0)===33;
$c['workspace']=($m['v01417WorkspaceExecutionAuthority']??false)===true;
$c['extract']=($m['v01417LabExecutesEmbeddingExtraction']??true)===false;
$c['projectionCompute']=($m['v01417LabExecutesDimensionalityReduction']??true)===false;
$c['neighbor']=($m['v01417NearestNeighborIsRelationship']??true)===false;
$c['semantic']=($m['v01417SemanticRelationshipInferred']??true)===false;
$c['faithful']=($m['v01417ProjectionFaithfulnessCertified']??true)===false;
$c['evidence']=($m['v01417EmbeddingIsEvidence']??true)===false;
foreach($c as $k=>$v){if(!$v){fwrite(STDERR,"FAIL $k\n");exit(1);}} echo "PASS v0.141.7 release integrity\n";
