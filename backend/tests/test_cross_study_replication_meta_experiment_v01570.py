from pathlib import Path
import math
import tempfile
import pytest

from app.cross_study_replication_meta_experiment_v01570 import CrossStudyReplicationMetaExperimentManager, CrossStudyReplicationError


def manager():
    tmp=tempfile.TemporaryDirectory()
    m=CrossStudyReplicationMetaExperimentManager(str(Path(tmp.name)/"meta.sqlite3"), persistent_disk_mounted=True)
    m._tmp=tmp
    return m


def study_payload(title, study_type="primary"):
    return {"title":title,"studyType":study_type,"sourceRef":f"doi:{title.lower().replace(' ','-')}","design":"controlled","population":"adults","outcome":"Outcome A"}


def effect(metric, estimate, se, source):
    return {"metricKey":metric,"effectMeasure":"standardized-mean-difference","estimate":estimate,"standardError":se,"sampleSize":100,"extractionSource":source}


def setup_workspace(m):
    s1=m.create_study("project:test",study_payload("Anchor"),"tester")["study"]
    s2=m.create_study("project:test",study_payload("Direct Rep","direct-replication"),"tester")["study"]
    s3=m.create_study("project:test",study_payload("Concept Rep","conceptual-replication"),"tester")["study"]
    m.add_effect(s1["id"],effect("primary",0.50,0.10,"table 2"),"tester")
    m.add_effect(s2["id"],effect("primary",0.40,0.12,"figure 3"),"tester")
    m.add_effect(s3["id"],effect("primary",0.10,0.20,"supplement"),"tester")
    w=m.create_workspace("project:test",{"title":"Replication set","question":"Does the effect reproduce?","primaryMetricKey":"primary","primaryEffectMeasure":"standardized-mean-difference"},"tester")["workspace"]
    for s,rel in [(s1,"anchor"),(s2,"direct-replication"),(s3,"conceptual-replication")]:
        m.add_study_to_workspace(w["id"],{"studyId":s["id"],"relationType":rel,"inclusionState":"included"},"tester")
    return w,s1,s2,s3


def test_health_and_policies_keep_human_review_boundary():
    m=manager(); h=m.health()
    assert h["version"]=="0.157.0"
    assert h["immutableStudyRevisions"] is True
    assert h["automaticReplicationJudgment"] is False
    assert h["automaticCausalInference"] is False
    assert h["publicationBiasInference"] is False
    assert h["humanScientificReviewRequired"] is True


def test_study_revisions_are_append_only():
    m=manager(); created=m.create_study("project:test",study_payload("Study One"),"a")["study"]
    revised=m.revise_study(created["id"],{**study_payload("Study One Revised"),"methodNotes":"new revision"},"b")["study"]
    old=m.get_study(created["id"],revision=1)["study"]
    assert revised["currentRevision"]==2
    assert revised["definition"]["title"]=="Study One Revised"
    assert old["definition"]["title"]=="Study One"
    assert old["revision"]["revision"]==1


def test_effect_records_are_immutable_and_require_positive_uncertainty():
    m=manager(); s=m.create_study("project:test",study_payload("Study"),"a")["study"]
    e=m.add_effect(s["id"],effect("m",0.4,0.1,"source"),"a")["effect"]
    assert e["immutable"] is True and e["variance"]==pytest.approx(0.01)
    with pytest.raises(CrossStudyReplicationError): m.add_effect(s["id"],effect("m",0.4,0.0,"source"),"a")


def test_workspace_freeze_blocks_membership_mutation():
    m=manager(); w,s1,s2,s3=setup_workspace(m)
    frozen=m.freeze_workspace(w["id"],"reviewer")["workspace"]
    assert frozen["status"]=="frozen" and frozen["frozenAt"]
    extra=m.create_study("project:test",study_payload("Extra"),"tester")["study"]
    with pytest.raises(CrossStudyReplicationError): m.add_study_to_workspace(w["id"],{"studyId":extra["id"],"relationType":"related-study","inclusionState":"included"},"tester")


def test_fixed_random_heterogeneity_and_leave_one_out():
    m=manager(); w,*_=setup_workspace(m)
    s=m.synthesis(w["id"])["synthesis"]
    assert s["k"]==3
    assert math.isfinite(s["fixedEffect"]["estimate"])
    assert math.isfinite(s["randomEffects"]["estimate"])
    assert s["heterogeneity"]["I2Percent"]>=0
    assert s["heterogeneity"]["tau2"]>=0
    assert len(s["leaveOneOut"])==3
    assert s["automaticReplicationJudgment"] is False


def test_human_assessment_is_explicit_not_computed():
    m=manager(); w,s1,*_=setup_workspace(m)
    before=m.get_workspace(w["id"])
    row=next(x for x in before["studies"] if x["studyId"]==s1["id"])
    assert row["assessment"]["state"]=="unreviewed"
    after=m.record_assessment(w["id"],s1["id"],{"assessment":"mixed","rationale":"Direction agrees but context differs."},"reviewer")
    row=next(x for x in after["studies"] if x["studyId"]==s1["id"])
    assert row["assessment"]["state"]=="mixed"


def test_replication_campaign_handoff_is_draft_only():
    m=manager(); w,s1,*_=setup_workspace(m)
    h=m.replication_campaign_handoff(w["id"],s1["id"])["handoff"]
    assert h["targetRelease"]=="0.155.0"
    assert h["automaticCreation"] is False
    assert h["automaticExecution"] is False
    assert h["humanApprovalRequired"] is True


def test_manifest_digest_detects_tampering():
    m=manager(); w,*_=setup_workspace(m)
    manifest=m.manifest(w["id"])["manifest"]
    assert m.verify_manifest(manifest)["verified"] is True
    manifest["workspace"]["title"]="tampered"
    assert m.verify_manifest(manifest)["verified"] is False


def test_mixed_effect_measures_must_be_harmonized_before_pooling():
    m=manager(); w,s1,s2,s3=setup_workspace(m)
    m.add_effect(s3["id"],{"metricKey":"mixed","effectMeasure":"log-odds-ratio","estimate":0.2,"standardError":0.1,"extractionSource":"x"},"tester")
    m.add_effect(s1["id"],{"metricKey":"mixed","effectMeasure":"standardized-mean-difference","estimate":0.2,"standardError":0.1,"extractionSource":"x"},"tester")
    with pytest.raises(CrossStudyReplicationError): m.synthesis(w["id"],"mixed")
