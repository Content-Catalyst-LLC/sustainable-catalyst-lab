from app import computational_linguistics_research_workspace_v01430 as m

CORPUS={
 "corpusId":"corp-1","title":"Parallel historical corpus","sourceRefs":["lib:doc-1"],
 "texts":[{"textId":"t1","sourceRef":"lib:doc-1","language":{"bcp47":"ar","name":"Arabic","historicalVariant":"Classical Arabic"},"script":{"iso15924":"Arab","direction":"rtl"},"originalText":"السلام عليكم","provenanceRef":"prov:t1"}],
 "representations":[
  {"representationId":"tr1","sourceTextId":"t1","type":"transliteration","content":"al-salāmu ʿalaykum","language":{"bcp47":"ar-Latn"},"script":{"iso15924":"Latn","direction":"ltr"},"derivedFrom":["t1"],"method":"manual scholarly transliteration","provenanceRef":"prov:tr1"},
  {"representationId":"en1","sourceTextId":"t1","type":"translation","content":"Peace be upon you","language":{"bcp47":"en"},"script":{"iso15924":"Latn","direction":"ltr"},"derivedFrom":["t1"],"method":"human translation","provenanceRef":"prov:en1"}
 ],
 "annotations":[{"annotationId":"a1","targetRepresentationId":"tr1","kind":"pos","span":{"start":0,"end":1},"label":"NOUN","method":"tagger","provenanceRef":"prov:a1","confidence":0.92}],
 "alignments":[{"alignmentId":"al1","sourceRepresentationId":"tr1","targetRepresentationId":"en1","method":"manual","provenanceRef":"prov:al1","links":[{"source":{"tokenIndex":0},"target":{"tokenIndex":0}}]}]
}
P={"sessionId":"s1","projectRef":"proj:1","state":"active","corpus":CORPUS,"limitations":["small corpus"],"review":{"status":"in-review"}}

def test_health_and_contract():
    h=m.health(); assert h["version"]=="0.143.0" and h["api_route_count"]==48 and h["originalLanguageFirst"] is True and h["crossLingualSimilarityIsEvidence"] is False
    c=m.contract(); assert c["predecessorVersion"]=="0.142.0" and "translation" in c["representationTypes"] and "dependency" in c["annotationKinds"]

def test_original_language_primary_and_derived_translation():
    t=m.normalize_text(CORPUS["texts"][0]); assert t["isOriginalLanguagePrimary"] is True and t["translationIsSource"] is False
    r=m.normalize_representation(CORPUS["representations"][1]); assert r["isDerivedRepresentation"] is True and r["replacesOriginal"] is False and r["semanticEquivalenceCertified"] is False

def test_corpus_and_audits():
    c=m.normalize_corpus(CORPUS); assert len(c["texts"])==1 and len(c["representations"])==2 and c["translationAsDerivedRepresentation"] is True
    assert m.original_language_audit({"corpus":CORPUS})["clean"] is True
    rows=m.language_script_audit({"corpus":CORPUS})["rows"]; assert any(x["scriptCode"]=="Arab" for x in rows) and any(x["scriptCode"]=="Latn" for x in rows)

def test_lineage_and_alignment_boundaries():
    g=m.transformation_lineage({"corpus":CORPUS}); assert g["complete"] is True and len(g["edges"])==2 and g["transformationLineageIsSemanticEquivalence"] is False
    a=m.alignment_audit({"corpus":CORPUS}); assert a["allClean"] is True and a["alignmentIsSemanticEquivalence"] is False

def test_explicit_token_descriptives_only():
    p={"tokens":["the","cat","the","cat","sat"]}
    s=m.corpus_statistics(p)["statistics"]; assert s["tokenCount"]==5 and s["typeCount"]==3
    l=m.lexical_profile(p); assert l["rows"][0]["count"]==2 and l["lexicalFrequencyIsMeaning"] is False
    n=m.ngram_profile({**p,"n":2}); assert n["n"]==2 and n["ngramFrequencyIsLinguisticExplanation"] is False
    q=m.concordance({**p,"query":"cat","window":1}); assert q["matchCount"]==2 and q["concordanceIsInterpretation"] is False

def test_supplied_annotations_are_summarized_not_inferred():
    anns=[{"targetRepresentationId":"r1","kind":"pos","label":"NOUN"},{"targetRepresentationId":"r1","kind":"dependency","label":"nsubj"},{"targetRepresentationId":"r1","kind":"phoneme","label":"k"},{"targetRepresentationId":"r1","kind":"semantic-role","label":"ARG0"}]
    assert m.morphology_summary({"annotations":anns})["morphologicalAnalysisInferredByLab"] is False
    assert m.syntax_summary({"annotations":anns})["syntacticAnalysisInferredByLab"] is False
    assert m.phonology_phonetics_summary({"annotations":anns})["phoneticExtractionPerformedByLab"] is False
    assert m.semantic_profile({"annotations":anns})["automaticSemanticInference"] is False

def test_cross_lingual_comparison_is_not_equivalence():
    x=m.cross_lingual_comparison({"source":{"language":{"bcp47":"ar"},"tokens":["a","b"]},"target":{"language":{"bcp47":"en"},"tokens":["x","y"]},"alignment":CORPUS["alignments"][0]})
    assert x["alignmentLinkCount"]==1 and x["semanticEquivalenceCertified"] is False and x["translationQualityCertified"] is False

def test_handoffs_preserve_authority_boundaries():
    w=m.workspace_execution_handoff({**P,"requestedOperation":"dependency-parse"})["handoff"]; assert w["executionAuthority"]=="workspace" and w["automaticExecution"] is False
    c=m.core_handoff(P)["handoff"]; assert c["canonicalObjectAuthority"]=="platform-core" and c["automaticCanonicalization"] is False
    l=m.library_handoff(P)["handoff"]; assert l["sourceAuthority"]=="knowledge-library" and l["translationMayReplaceOriginal"] is False
    r=m.research_os_handoff(P)["handoff"]; assert r["automaticPhaseAdvance"] is False

def test_snapshot_determinism_and_export():
    a=m.workspace_snapshot(P)["snapshot"]; b=m.workspace_snapshot(P)["snapshot"]; assert a["snapshotFingerprint"]==b["snapshotFingerprint"]
    assert m.compare_snapshots({"left":P,"right":P})["sameWorkspaceState"] is True
    e=m.export_bundle(P); assert e["scientificValidityCertified"] is False and e["semanticEquivalenceCertified"] is False
    rp=m.reproducibility_package(P)["package"]; assert rp["reproductionCertified"] is False and rp["replicationCertified"] is False

def test_interpretation_boundary():
    b=m.interpretation_boundary()["boundaries"]
    assert b["translationIsSource"] is False and b["alignmentIsSemanticEquivalence"] is False and b["annotationIsGroundTruth"] is False and b["crossLingualSimilarityIsEvidence"] is False
