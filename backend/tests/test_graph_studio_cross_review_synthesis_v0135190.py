from app import graph_studio_cross_review_synthesis_v0135190 as m
BASE={
 "projectId":"project-1",
 "reviewThreads":[{"id":"thread-1","title":"Method review","status":"open","subjectRefs":["claim-1"]},{"id":"thread-2","title":"Figure review","status":"resolved","subjectRefs":["figure-2"]}],
 "resolutionRecords":[{"id":"res-1","threadId":"thread-1","resolutions":[{"id":"action-1","status":"open"}]},{"id":"res-2","threadId":"thread-2","resolutions":[{"id":"action-2","status":"resolved"}]}],
 "reviewerPanels":[{"id":"panel-1","threadId":"thread-1","reviewers":[{"reviewerId":"a"},{"reviewerId":"b"}],"assessments":[{"reviewerId":"a","assessmentState":"addressed"},{"reviewerId":"b","assessmentState":"further-revision"}],"signoffs":[{"reviewerId":"a","signoffState":"signed"},{"reviewerId":"b","signoffState":"withheld"}],"dissents":[{"id":"d-1","reviewerId":"b","dissentKind":"methodological","statement":"Alternative method remains plausible."}]}],
 "verificationBundles":[{"id":"vb-1","threadId":"thread-1","verificationOutcome":"passed","artifacts":[{"artifactRef":"run-1"}]}],
 "reproductionBridges":[{"id":"rb-1","threadId":"thread-1","revisionAction":"rerun-analysis","status":"completed"}],
 "impactAnalyses":[{"id":"ia-1","threadId":"thread-1","seedId":"model-1","potentiallyAffectedNodeIds":["figure-1","claim-1"],"dependencyNodeIds":["data-1"]}],
 "auditRecords":[{"id":"audit-1","threadId":"thread-1","events":[{"id":"e-1","eventType":"verification-recorded","createdAt":"2026-09-26T01:00:00Z"}]}]
}
def test_normalize_validate():
 n=m.normalize_synthesis(BASE); assert n['ok'] and n['record']['collection']=='graphStudioCrossReviewSyntheses' and len(n['record']['fingerprint'])==64
 v=m.validate_synthesis(BASE); assert v['ok'] and not v['errors']
def test_resolution_matrix_preserves_workflow_meaning():
 x=m.resolution_matrix(BASE); assert x['ok'] and x['row_count']==2 and x['consensus_score'] is None and x['winner'] is None
 r={z['thread_id']:z for z in x['rows']}; assert r['thread-1']['administratively_open'] and r['thread-1']['dissent_count']==1 and r['thread-1']['verification_bundle_count']==1 and r['thread-1']['reproduction_bridge_count']==1
 assert r['thread-1']['scientifically_resolved'] is None and not r['thread-1']['automatic_resolution']
def test_open_items_are_not_severity_ranked():
 x=m.open_items(BASE); assert x['count']==1 and x['items'][0]['thread_id']=='thread-1' and not x['priority_ranking'] and not x['scientific_severity_scoring']
def test_dissent_register_preserved():
 x=m.disagreement_register(BASE); assert x['count']==1 and x['items'][0]['reviewer_id']=='b' and x['minority_views_preserved'] and not x['consensus_inferred']
def test_supporting_matrices():
 assert m.verification_matrix(BASE)['count']==1
 assert m.reproduction_matrix(BASE)['count']==1
 assert m.revision_impact_matrix(BASE)['items'][0]['potentially_affected_count']==2
 assert m.resolution_history(BASE)['count']==3
 assert m.subject_index(BASE)['count']==2
def test_snapshot_compare():
 a=m.snapshot({**BASE,'snapshotId':'a'})['snapshot']; b=m.snapshot({**BASE,'snapshotId':'b'})['snapshot']; c=m.compare_snapshots({'before':a,'after':b}); assert c['ok'] and not c['changed_thread_ids'] and not c['scientific_improvement_inferred']
def test_packet_synthesis_and_boundaries():
 s=m.synthesize(BASE); assert s['ok'] and not s['result']['consensus_inferred'] and not s['result']['automatic_scientific_resolution']
 p=m.project_workspace_packet(BASE); assert p['ok'] and p['packet']['consensus_score'] is None and not p['packet']['truth_ranking']
 a=m.audit_event_draft(BASE); assert a['ok'] and not a['automatic_append'] and not a['automatic_resolution']
def test_health_contract_acceptance():
 h=m.health(); assert h['api_route_count']==21 and h['backward_compatible_v0135180']
 c=m.contract(); assert not c['majority_voting'] and not c['consensus_scoring'] and not c['reviewer_ranking']
 a=m.acceptance_report(); assert a['cross_review_synthesis'] and a['dissent_register'] and not a['automatic_scientific_validity']
