from copy import deepcopy
import pytest

from app.scientific_literature_provenance_v0630 import (
    ScientificLiteratureProvenanceError, build_provenance_packet, evaluate_provenance,
    health, normalize_citation_edge, normalize_claim_link, normalize_source, policies,
    record_source_review, verify_provenance_packet,
)
from app.scientific_claims_traceability_v0620 import record_claim_review


def _source(source_id="source-a", status="active", decision=None, doi="10.1000/example"):
    src = {
        "id": source_id, "sourceType": "journal-article", "title": f"Study {source_id}",
        "authors": ["A. Researcher", "B. Scientist"], "publicationYear": 2025,
        "containerTitle": "Journal of Governed Science", "identifiers": {"doi": doi},
        "sourceUrl": "https://doi.org/10.1000/example", "origin": "doi", "status": status,
        "peerReviewStatus": "peer-reviewed", "scopeNote": "Population and methods reviewed manually.",
    }
    if decision:
        src = record_source_review({"source": src, "review": {"decision": decision, "rationale": "Methods and applicability were reviewed."}})["source"]
    return src


def _claim(qualified=False):
    claim = {
        "id": "claim-1", "studyId": "study-1", "statement": "The observed intervention is associated with improved outcome.",
        "claimType": "associational", "status": "active", "scopeNote": "Bounded population only.",
        "evidenceLinks": [{"role": "supports", "sourceType": "analysis", "ref": "analysis-1"}, {"role": "uncertainty", "sourceType": "analysis", "ref": "uncertainty-1"}],
    }
    if qualified:
        claim = record_claim_review({"claim": claim, "review": {"decision": "accept-with-qualification", "rationale": "Contradictory literature and scope limits were reviewed."}})["claim"]
    return claim


def _link(role="supports", source_id="source-a"):
    return {"claimId": "claim-1", "sourceId": source_id, "role": role, "locator": "Results §3.2", "note": "Researcher-mapped literature provenance."}


def test_health_and_policy_keep_literature_human_governed():
    h = health(); p = policies()
    assert h["status"] == "scientific-literature-provenance-ready"
    assert p["humanSourceReviewRequired"] is True
    assert p["automaticLiteratureTruthScoringAuthorized"] is False
    assert p["networkFetchDuringEvaluationAuthorized"] is False


def test_source_normalization_is_deterministic_and_normalizes_doi():
    a = normalize_source(_source()); b = normalize_source(_source())
    assert a["sourceHash"] == b["sourceHash"]
    assert a["identifiers"]["doi"] == "10.1000/example"
    assert a["schema"] == "sc-lab-scientific-literature-source/0.63.0"


def test_source_layer_rejects_full_text_credentials_callbacks_and_code():
    for extra in ({"fullText": "paper"}, {"credentials": {"token": "x"}}, {"callbackUrl": "https://x"}, {"code": "print(1)"}):
        with pytest.raises(ScientificLiteratureProvenanceError):
            normalize_source({**_source(), **extra})


def test_source_url_must_be_http_or_https():
    with pytest.raises(ScientificLiteratureProvenanceError):
        normalize_source({**_source(), "sourceUrl": "file:///tmp/paper.pdf"})


def test_source_review_requires_rationale_and_is_hash_chained():
    with pytest.raises(ScientificLiteratureProvenanceError):
        record_source_review({"source": _source(), "review": {"decision": "include", "rationale": ""}})
    out = record_source_review({"source": _source(), "review": {"decision": "include-with-caution", "rationale": "Population differs from the active study."}})
    assert len(out["review"]["reviewHash"]) == 64
    assert out["source"]["reviewHistory"][-1]["decision"] == "include-with-caution"


def test_claim_link_and_citation_edge_are_typed_and_hashed():
    link = normalize_claim_link(_link())
    edge = normalize_citation_edge({"fromSourceId": "source-a", "toSourceId": "source-b", "relation": "replicates"})
    assert link["role"] == "supports" and len(link["linkHash"]) == 64
    assert edge["relation"] == "replicates" and len(edge["edgeHash"]) == 64


def test_unreviewed_literature_does_not_count_as_traceable():
    result = evaluate_provenance({"sources": [_source()], "claims": [_claim()], "claimLinks": [_link()], "citationEdges": []})
    assert result["gate"] == "needs-source-review"
    assert result["claimRows"][0]["reviewedSourceLinkCount"] == 0


def test_reviewed_source_makes_claim_literature_traceable_without_truth_claim():
    result = evaluate_provenance({"sources": [_source(decision="include")], "claims": [_claim()], "claimLinks": [_link()], "citationEdges": []})
    assert result["gate"] == "traceable"
    assert result["claimRows"][0]["automaticTruthClaim"] is False
    assert result["boundaries"]["automaticAuthorityRanking"] is False


def test_contradictory_literature_is_preserved_and_requires_qualified_claim_review():
    sources = [_source("source-a", decision="include"), _source("source-b", decision="include", doi="10.1000/other")]
    links = [_link("supports", "source-a"), _link("contradicts", "source-b")]
    result = evaluate_provenance({"sources": sources, "claims": [_claim()], "claimLinks": links, "citationEdges": []})
    assert result["gate"] == "contested"
    qualified = evaluate_provenance({"sources": sources, "claims": [_claim(True)], "claimLinks": links, "citationEdges": []})
    assert qualified["gate"] == "traceable"


def test_retracted_or_excluded_source_does_not_satisfy_reviewed_source_gate():
    retracted = _source(status="retracted", decision="include")
    excluded = _source("source-b", decision="exclude", doi="10.1000/excluded")
    result = evaluate_provenance({"sources": [retracted, excluded], "claims": [_claim()], "claimLinks": [_link("supports", "source-a"), _link("contextualizes", "source-b")], "citationEdges": []})
    assert result["gate"] == "needs-source-review"
    assert {row["gate"] for row in result["sourceRows"]} == {"unusable-status", "excluded"}


def test_unresolved_citation_edges_and_orphan_sources_are_visible():
    result = evaluate_provenance({
        "sources": [_source(decision="include"), _source("source-b", decision="include", doi="10.1000/other")],
        "claims": [_claim()], "claimLinks": [_link()],
        "citationEdges": [{"fromSourceId": "source-a", "toSourceId": "missing-source", "relation": "cites"}],
    })
    assert result["gate"] == "needs-source"
    assert result["unresolvedCitationEdges"][0]["missingSourceIds"] == ["missing-source"]
    assert "source-b" in result["orphanSourceIds"]


def test_duplicate_identifiers_are_flagged_but_not_auto_merged():
    a = _source("source-a", decision="include", doi="10.1000/same")
    b = _source("source-b", decision="include", doi="10.1000/same")
    result = evaluate_provenance({"sources": [a, b], "claims": [_claim()], "claimLinks": [_link()], "citationEdges": []})
    assert result["duplicateIdentifierGroups"][0]["identifier"] == "doi:10.1000/same"
    assert result["sourceCount"] == 2


def test_provenance_packet_is_deterministic_metadata_only_and_tamper_evident():
    payload = {
        "sources": [_source(decision="include")], "claims": [_claim()], "conclusions": [],
        "claimLinks": [_link()], "citationEdges": [],
    }
    first = build_provenance_packet(payload)["packet"]
    second = build_provenance_packet(payload)["packet"]
    assert first["packetHash"] == second["packetHash"]
    assert first["boundaries"]["rawFullTextIncluded"] is False
    assert verify_provenance_packet({"packet": first})["ok"] is True
    broken = deepcopy(first); broken["gate"] = "contested"
    assert verify_provenance_packet({"packet": broken})["ok"] is False
