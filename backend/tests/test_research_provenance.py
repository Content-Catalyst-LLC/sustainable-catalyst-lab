from app.research_provenance import normalize_source, normalize_evidence, verify_record, build_provenance
def test_source_and_evidence():
 s=normalize_source({"title":"Planetary Boundaries","authors":["Rockström, Johan"],"year":2009,"sourceType":"journal-article"}); assert s["citation"]["inText"]=="(Rockström, 2009)"; assert verify_record({"record":s})["ok"]
 e=normalize_evidence({"sourceId":s["id"],"excerpt":"A safe operating space.","claim":"Boundaries define risk."}); assert verify_record({"record":e})["ok"]
 p=build_provenance({"subjectId":"calc-1","sourceIds":[s["id"]],"evidenceIds":[e["id"]]}); assert p["sourceIds"]==[s["id"]]
