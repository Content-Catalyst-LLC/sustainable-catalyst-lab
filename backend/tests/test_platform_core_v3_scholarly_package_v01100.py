from app.platform_core_v3_scholarly_package_v01100 import (
    build_core_package_binding, build_provenance_manifest, build_publication_binding,
    build_scholarly_interoperability_plan, build_scholarly_package_envelope,
    build_validation_record, bridge_citations, bridge_datasets_notebooks,
    health, manifest, map_legacy_package, normalize_package,
)

CTX={"project_ref":"project:p1","session_id":"9","session_key":"s1","title":"Study","workflow_ref":"lab:workflow:w1","project_state_ref":"core:state:1","researcher_ref":"researcher:r1"}

def package():
    return {"schema":"sc-lab-reproducibility-package/0.37.0","id":"pkg1","title":"Replication package","packageVersion":"1.2.0","packageHash":"a"*64,"resources":[{"id":"d1","object_ref":"lab:dataset:d1"},{"id":"fig1","object_ref":"lab:visual:fig1"}],"citations":[{"cited_object_ref":"library:source:s1","citation_format":"csl-json","citation_data":{"title":"Source"}}],"datasets":[{"id":"d1","dataset_ref":"lab:dataset:d1","content_hash":"b"*64}],"notebooks":[{"id":"n1","notebook_ref":"lab:notebook:n1","environment_ref":"lab:env:e1","execution_ref":"lab:execution:r1"}],"provenance":{"producer":"lab"}}

def test_normalize_and_binding():
    n=normalize_package({"context":CTX,"package":package()}); p=n["package"]
    assert p["package_type"]=="replication_package" and p["package_ref"]=="lab:reproducibility-package:pkg1"
    b=build_core_package_binding({"context":CTX,"package":package()})
    assert b["automatic_submission"] is False and b["data"]["session_id"]=="9"
    assert b["data"]["package_ref"]=="lab:reproducibility-package:pkg1" and len(b["data"]["member_refs"])==2

def test_scholarly_envelope_and_plan():
    e=build_scholarly_package_envelope({"context":CTX,"package":package()})
    assert e["data"]["package_type"]=="replication_package" and e["automatic_submission"] is False
    plan=build_scholarly_interoperability_plan({"context":CTX,"package":package()})
    assert plan["operation_count"]>=5 and plan["requires_core_package_id_after_create"] is True
    assert all(op["request_body"]=={"data":op["data"]} for op in plan["operations"])

def test_citation_and_descriptors_require_created_core_package_id():
    c=bridge_citations({"context":CTX,"package":package()}); d=bridge_datasets_notebooks({"context":CTX,"package":package()})
    assert c["count"]==1 and c["requires_core_package_id"] is True
    assert d["count"]==2 and d["requires_core_package_id"] is True
    assert c["operations"][0]["data"]["package_id"]=="$CORE_PACKAGE_ID"

def test_provenance_validation_publication_boundaries():
    prov=build_provenance_manifest({"context":CTX,"package":package()}); assert prov["lineage_is_declared_not_inferred"] is True
    val=build_validation_record({"context":CTX,"package":package(),"validation":{"validation_type":"manifest-integrity","evidence":["lab:artifact:receipt1"]}})
    assert val["core_certifies_reproducibility"] is False and val["core_validates_scientific_content"] is False
    pub={**package(),"schema":"sc-lab-research-publication/0.37.0","id":"pub1","publicationHash":"c"*64,"packageHash":None,"publication_ref":"lab:publication:pub1"}
    pb=build_publication_binding({"context":CTX,"package":pub}); assert pb["automatic_publication"] is False

def test_legacy_mapping_and_manifest():
    m=map_legacy_package({"context":CTX,"package":package()}); assert m["automatic_certification"] is False
    h=health(); mf=manifest(); assert h["lab_release_version"]=="0.110.0" and h["minimum_core_release"]=="3.0.0"
    assert mf["boundaries"]["core_publishes_packages"] is False and mf["boundaries"]["core_mints_identifiers"] is False
