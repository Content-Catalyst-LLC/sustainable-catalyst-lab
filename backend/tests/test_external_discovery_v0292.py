from types import SimpleNamespace
import pytest

from app.external_discovery import DiscoveryError, build_openurl, deduplicate, health, normalize, open_access_lookup, provider_catalog, search


def settings(**kwargs):
    base=dict(discovery_contact_email="lab@example.org",openalex_api_key="",oclc_access_token="",openurl_resolver_base="https://library.example.org/openurl",discovery_timeout_seconds=5,discovery_max_results=25)
    base.update(kwargs); return SimpleNamespace(**base)


def fixture_fetch(url, headers, timeout):
    if "crossref" in url:
        return {"message":{"items":[{"DOI":"10.1234/example","title":["Climate systems"],"author":[{"given":"Amina","family":"Khan"}],"published":{"date-parts":[[2025]]},"type":"journal-article","publisher":"Example Press","container-title":["Journal of Systems"],"URL":"https://doi.org/10.1234/example","subject":["Climate"],"is-referenced-by-count":12,"license":[{"URL":"https://creativecommons.org/licenses/by/4.0/"}]}]}}
    if "datacite" in url:
        return {"data":[{"id":"10.1234/example","attributes":{"doi":"10.1234/example","titles":[{"title":"Climate systems"}],"creators":[{"name":"Khan, Amina"}],"publicationYear":2025,"publisher":"Example Repository","types":{"resourceTypeGeneral":"Dataset"},"url":"https://example.org/data","subjects":[{"subject":"climate"}],"rightsList":[{"rights":"Open Access","rightsUri":"https://creativecommons.org/licenses/by/4.0/"}]}}]}
    if "openalex" in url:
        return {"results":[{"id":"https://openalex.org/W1","title":"Climate systems","publication_year":2025,"type":"article","authorships":[{"author":{"display_name":"Amina Khan"}}],"ids":{"doi":"https://doi.org/10.1234/example"},"primary_location":{"landing_page_url":"https://example.org/paper","source":{"display_name":"Journal of Systems"},"license":"cc-by"},"open_access":{"is_oa":True,"oa_status":"gold","oa_url":"https://example.org/paper.pdf"},"cited_by_count":13}]}
    raise AssertionError(url)


def test_provider_catalog_configuration():
    p=provider_catalog(settings())
    openalex=next(x for x in p["providers"] if x["id"]=="openalex")
    assert openalex["configurationRequired"] is True
    assert p["arbitraryRemoteFetch"] is False


def test_crossref_and_datacite_search_and_deduplication():
    result=search({"query":"climate systems","providers":["crossref","datacite"],"maxResults":10},settings(),fixture_fetch)
    assert result["rawCandidateCount"]==2
    assert result["candidateCount"]==1
    assert result["duplicatesRemoved"]==1
    assert set(result["candidates"][0]["providers"])=={"crossref","datacite"}
    assert result["candidates"][0]["doi"]=="10.1234/example"


def test_openalex_key_and_open_access_lookup():
    s=settings(openalex_api_key="free-key")
    result=search({"query":"climate","providers":["openalex"]},s,fixture_fetch)
    assert result["candidates"][0]["isOpenAccess"] is True
    lookup=open_access_lookup({"doi":"10.1234/example"},s,fixture_fetch)
    assert lookup["lookup"]["status"]=="gold"
    assert lookup["lookup"]["bestUrl"].endswith("paper.pdf")


def test_openalex_without_key_is_reported_not_crash():
    result=search({"query":"climate","providers":["openalex"]},settings(),fixture_fetch)
    assert result["providerReports"][0]["ok"] is False
    assert "not configured" in result["providerReports"][0]["error"]


def test_normalize_candidate_to_research_source():
    candidate=search({"query":"climate","providers":["crossref"]},settings(),fixture_fetch)["candidates"][0]
    source=normalize({"candidate":candidate,"projectId":"p-1"})["source"]
    assert source["recordType"]=="research-source"
    assert source["projectId"]=="p-1"
    assert source["citation"]["style"]=="harvard-author-date"
    assert len(source["sha256"])==64


def test_deduplication_title_year_fallback():
    result=deduplicate({"candidates":[{"provider":"a","title":"A Study","authors":["N. One"],"year":2020},{"provider":"b","title":"A Study","authors":["N. One"],"year":2020,"url":"https://example.org"}]})
    assert result["resultCount"]==1
    assert set(result["candidates"][0]["providers"])=={"a","b"}


def test_openurl_builder_is_metadata_only():
    result=build_openurl({"candidate":{"title":"Climate systems","doi":"10.1234/example","authors":["Amina Khan"],"year":2025,"workType":"article"}},settings())
    assert result["configured"] is True
    assert "ctx_ver=Z39.88-2004" in result["url"]
    assert "rft_id=info%3Adoi%2F10.1234%2Fexample" in result["url"]


def test_unknown_live_provider_is_rejected():
    with pytest.raises(DiscoveryError):
        search({"query":"climate","providers":["arbitrary-url"]},settings(),fixture_fetch)


def test_health_reports_governed_handoffs():
    body=health(settings(openalex_api_key="x"))
    assert body["liveProviderCount"]==3
    assert body["worldCatHandoff"] is True
    assert body["arbitraryRemoteFetch"] is False
