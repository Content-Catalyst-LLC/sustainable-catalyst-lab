from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import html
import json
import re
from typing import Any, Callable
from urllib.parse import quote, urlencode, urlparse, urlunparse, parse_qsl
from urllib.request import Request, urlopen

from .config import settings

VERSION = "0.29.2"
SEARCH_SCHEMA = "sc-lab-external-discovery-search/0.29.2"
CANDIDATE_SCHEMA = "sc-lab-scholarly-discovery-candidate/0.29.2"
IMPORT_SCHEMA = "sc-lab-discovery-source-import/0.29.2"
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
ALLOWED_PROVIDERS = ("crossref", "openalex", "datacite")
HANDOFF_PROVIDERS = ("worldcat", "google-scholar", "openurl")


class DiscoveryError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _clean(value: Any, limit: int = 4000) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _first(value: Any) -> Any:
    return value[0] if isinstance(value, list) and value else value


def _doi(value: Any) -> str:
    text = _clean(value, 300).lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.strip().rstrip(".")


def _isbn(values: Any) -> list[str]:
    if not isinstance(values, list): values = [values] if values else []
    out=[]
    for value in values:
        digits=re.sub(r"[^0-9Xx]", "", str(value))
        if len(digits) in {10,13} and digits.upper() not in out: out.append(digits.upper())
    return out[:20]


def _year(value: Any) -> int | None:
    try:
        if isinstance(value, list):
            while isinstance(value, list) and value: value=value[0]
        y=int(value)
        return y if 1000 <= y <= 3000 else None
    except (TypeError, ValueError):
        return None


def _author_names(value: Any) -> list[str]:
    if not isinstance(value, list): return []
    names=[]
    for author in value[:100]:
        if isinstance(author, str): name=_clean(author, 300)
        elif isinstance(author, dict):
            name=_clean(author.get("name") or author.get("display_name") or " ".join(x for x in [_clean(author.get("given"),100),_clean(author.get("family"),100)] if x), 300)
        else: name=""
        if name and name not in names: names.append(name)
    return names


def _citation(candidate: dict[str, Any]) -> dict[str, str]:
    authors=candidate.get("authors") or []
    year=candidate.get("year") or "n.d."
    title=candidate.get("title") or "Untitled"
    lead=(authors[0].split()[-1] if authors else (candidate.get("publisher") or title).split()[0])
    in_text=f"({lead}{' et al.' if len(authors)>2 else ''}, {year})"
    authors_text=", ".join(authors) if authors else _clean(candidate.get("publisher") or "Unknown author")
    container=_clean(candidate.get("containerTitle") or candidate.get("publisher"))
    doi=candidate.get("doi") or ""
    bibliography=f"{authors_text} ({year}) {title}."
    if container: bibliography += f" {container}."
    if doi: bibliography += f" https://doi.org/{doi}"
    return {"style":"harvard-author-date","inText":in_text,"bibliography":bibliography}


def _candidate(provider: str, values: dict[str, Any]) -> dict[str, Any]:
    doi=_doi(values.get("doi"))
    title=_clean(values.get("title"), 1200)
    authors=_author_names(values.get("authors"))
    year=_year(values.get("year"))
    record={
        "schema": CANDIDATE_SCHEMA,
        "version": VERSION,
        "recordType": "discovery-candidate",
        "provider": provider,
        "providerId": _clean(values.get("providerId"), 500),
        "title": title,
        "authors": authors,
        "year": year,
        "workType": _clean(values.get("workType"), 120),
        "publisher": _clean(values.get("publisher"), 500),
        "containerTitle": _clean(values.get("containerTitle"), 500),
        "doi": doi,
        "url": _clean(values.get("url"), 2000),
        "abstract": _clean(values.get("abstract"), 8000),
        "subjects": [_clean(v,300) for v in (values.get("subjects") or [])[:100] if _clean(v,300)],
        "identifiers": {k:_clean(v,500) for k,v in (values.get("identifiers") or {}).items() if _clean(v,500)},
        "isbn": _isbn(values.get("isbn")),
        "citationCount": max(0, int(values.get("citationCount") or 0)),
        "isOpenAccess": bool(values.get("isOpenAccess")),
        "openAccessStatus": _clean(values.get("openAccessStatus"), 100) or ("open" if values.get("isOpenAccess") else "unknown"),
        "openAccessUrl": _clean(values.get("openAccessUrl"), 2000),
        "license": _clean(values.get("license"), 1000),
        "retrievedAt": values.get("retrievedAt") or _now(),
        "providers": [provider],
    }
    record["citation"]=_citation(record)
    record["fingerprint"]=_hash({"doi":doi,"title":re.sub(r"[^a-z0-9]+","",title.lower()),"year":year,"authors":authors[:3]})
    return record


def _crossref(item: dict[str, Any]) -> dict[str, Any]:
    date=((item.get("published-print") or item.get("published-online") or item.get("published") or {}).get("date-parts") or [])
    licenses=item.get("license") or []
    return _candidate("crossref", {
        "providerId": item.get("DOI") or item.get("URL"), "title": _first(item.get("title")), "authors": item.get("author"),
        "year": _year(date), "workType": item.get("type"), "publisher": item.get("publisher"), "containerTitle": _first(item.get("container-title")),
        "doi": item.get("DOI"), "url": item.get("URL"), "abstract": item.get("abstract"), "subjects": item.get("subject") or [],
        "isbn": item.get("ISBN") or [], "citationCount": item.get("is-referenced-by-count") or 0,
        "license": _first([x.get("URL") for x in licenses if isinstance(x,dict) and x.get("URL")]) or "",
        "isOpenAccess": bool(licenses), "openAccessStatus": "license-present" if licenses else "unknown",
    })


def _datacite(item: dict[str, Any]) -> dict[str, Any]:
    a=item.get("attributes") or {}
    titles=a.get("titles") or []
    descriptions=[d.get("description") for d in (a.get("descriptions") or []) if isinstance(d,dict) and d.get("descriptionType") in {"Abstract","Other"}]
    rights=a.get("rightsList") or []
    subjects=[s.get("subject") for s in (a.get("subjects") or []) if isinstance(s,dict)]
    identifiers={i.get("identifierType","identifier"):i.get("identifier") for i in (a.get("identifiers") or []) if isinstance(i,dict)}
    return _candidate("datacite", {
        "providerId": item.get("id") or a.get("doi"), "title": _first([t.get("title") for t in titles if isinstance(t,dict)]),
        "authors": a.get("creators") or [], "year": a.get("publicationYear"), "workType": (a.get("types") or {}).get("resourceTypeGeneral") or (a.get("types") or {}).get("resourceType"),
        "publisher": a.get("publisher"), "containerTitle": a.get("container"), "doi": a.get("doi") or item.get("id"), "url": a.get("url"),
        "abstract": _first(descriptions), "subjects": subjects, "identifiers": identifiers, "citationCount": (a.get("citationCount") or 0),
        "license": _first([r.get("rightsUri") or r.get("rights") for r in rights if isinstance(r,dict)]),
        "isOpenAccess": any("open" in _clean(r.get("rights") if isinstance(r,dict) else r).lower() or "creativecommons" in _clean(r.get("rightsUri") if isinstance(r,dict) else "").lower() for r in rights),
        "openAccessStatus": "rights-present" if rights else "unknown",
    })


def _openalex(item: dict[str, Any]) -> dict[str, Any]:
    primary=item.get("primary_location") or {}
    source=primary.get("source") or {}
    oa=item.get("open_access") or {}
    ids=item.get("ids") or {}
    topics=[t.get("display_name") for t in (item.get("topics") or []) if isinstance(t,dict)]
    authors=[{"display_name":((x.get("author") or {}).get("display_name"))} for x in (item.get("authorships") or []) if isinstance(x,dict)]
    return _candidate("openalex", {
        "providerId": item.get("id"), "title": item.get("title") or item.get("display_name"), "authors": authors,
        "year": item.get("publication_year"), "workType": item.get("type"), "publisher": source.get("host_organization_name"), "containerTitle": source.get("display_name"),
        "doi": ids.get("doi") or item.get("doi"), "url": primary.get("landing_page_url") or item.get("id"), "subjects": topics,
        "citationCount": item.get("cited_by_count") or 0, "isOpenAccess": oa.get("is_oa"), "openAccessStatus": oa.get("oa_status"),
        "openAccessUrl": oa.get("oa_url") or primary.get("pdf_url"), "license": primary.get("license") or oa.get("oa_status"),
        "identifiers": {"openalex":item.get("id"),"pmid":ids.get("pmid"),"mag":ids.get("mag")},
    })


def provider_catalog(settings_obj=settings) -> dict[str, Any]:
    contact=bool(getattr(settings_obj,"discovery_contact_email", ""))
    openalex=bool(getattr(settings_obj,"openalex_api_key", ""))
    oclc=bool(getattr(settings_obj,"oclc_access_token", ""))
    resolver=bool(getattr(settings_obj,"openurl_resolver_base", ""))
    return {
        "ok": True, "version": VERSION, "schema":"sc-lab-discovery-provider-catalog/0.29.2",
        "providers":[
            {"id":"crossref","label":"Crossref","mode":"live-api","configured":True,"authentication":"public","contactConfigured":contact,"maxResults":25},
            {"id":"openalex","label":"OpenAlex","mode":"live-api","configured":openalex,"authentication":"api-key","configurationRequired":not openalex,"maxResults":25},
            {"id":"datacite","label":"DataCite","mode":"live-api","configured":True,"authentication":"public","contactConfigured":contact,"maxResults":25},
            {"id":"worldcat","label":"WorldCat","mode":"catalog-handoff","configured":oclc,"authentication":"institutional-oclc-access","handoffOnly":True},
            {"id":"google-scholar","label":"Google Scholar","mode":"search-handoff","configured":True,"authentication":"none","handoffOnly":True,"scraping":False},
            {"id":"openurl","label":"Institutional link resolver","mode":"openurl-handoff","configured":resolver,"authentication":"institution-configured","handoffOnly":True},
        ],
        "arbitraryRemoteFetch": False, "allowedLiveProviders": list(ALLOWED_PROVIDERS), "handoffProviders": list(HANDOFF_PROVIDERS),
    }


def health(settings_obj=settings) -> dict[str, Any]:
    catalog=provider_catalog(settings_obj)
    return {"ok":True,"status":"ready","version":VERSION,"providerCount":len(catalog["providers"]),"liveProviderCount":3,"deduplication":True,"sourceImport":True,"openAccessLookup":True,"openUrlHandoff":True,"worldCatHandoff":True,"googleScholarHandoff":True,"arbitraryRemoteFetch":False,"providers":catalog["providers"]}


def _request_json(url: str, headers: dict[str,str], timeout: int) -> dict[str, Any]:
    host=(urlparse(url).hostname or "").lower()
    allowed={"api.crossref.org","api.openalex.org","api.datacite.org"}
    if host not in allowed: raise DiscoveryError("Remote host is not on the discovery allowlist.")
    request=Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=timeout) as response:
        raw=response.read(MAX_RESPONSE_BYTES+1)
        if len(raw)>MAX_RESPONSE_BYTES: raise DiscoveryError("Provider response exceeded the configured size limit.")
    try: return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise DiscoveryError("Provider returned invalid JSON.") from exc


def _headers(settings_obj, provider: str) -> dict[str,str]:
    email=getattr(settings_obj,"discovery_contact_email", "")
    agent="SustainableCatalystLab/0.29.2 (https://sustainablecatalyst.com/lab/"
    agent += f"; mailto:{email}" if email else ""
    agent += ")"
    return {"Accept":"application/json","User-Agent":agent}


def _with_params(base: str, params: dict[str,Any]) -> str:
    return f"{base}?{urlencode([(k,v) for k,v in params.items() if v not in (None,'')])}"


def _search_crossref(query: str, limit: int, filters: dict[str,Any], settings_obj, fetch_json) -> list[dict[str,Any]]:
    params={"query.bibliographic":query,"rows":limit}
    if getattr(settings_obj,"discovery_contact_email", ""): params["mailto"]=settings_obj.discovery_contact_email
    date_filters=[]
    if filters.get("yearFrom"): date_filters.append(f"from-pub-date:{int(filters['yearFrom'])}-01-01")
    if filters.get("yearTo"): date_filters.append(f"until-pub-date:{int(filters['yearTo'])}-12-31")
    if date_filters: params["filter"]=",".join(date_filters)
    payload=fetch_json(_with_params("https://api.crossref.org/works",params),_headers(settings_obj,"crossref"),settings_obj.discovery_timeout_seconds)
    return [_crossref(x) for x in ((payload.get("message") or {}).get("items") or [])[:limit] if isinstance(x,dict)]


def _search_datacite(query: str, limit: int, filters: dict[str,Any], settings_obj, fetch_json) -> list[dict[str,Any]]:
    params={"query":query,"page[size]":limit,"disable-facets":"true"}
    payload=fetch_json(_with_params("https://api.datacite.org/dois",params),_headers(settings_obj,"datacite"),settings_obj.discovery_timeout_seconds)
    return [_datacite(x) for x in (payload.get("data") or [])[:limit] if isinstance(x,dict)]


def _search_openalex(query: str, limit: int, filters: dict[str,Any], settings_obj, fetch_json) -> list[dict[str,Any]]:
    key=getattr(settings_obj,"openalex_api_key", "")
    if not key: raise DiscoveryError("OpenAlex API key is not configured.")
    params={"search":query,"per-page":limit,"api_key":key}
    payload=fetch_json(_with_params("https://api.openalex.org/works",params),_headers(settings_obj,"openalex"),settings_obj.discovery_timeout_seconds)
    return [_openalex(x) for x in (payload.get("results") or [])[:limit] if isinstance(x,dict)]


def _matches(candidate: dict[str,Any], filters: dict[str,Any]) -> bool:
    y=candidate.get("year")
    if filters.get("yearFrom") and y and y<int(filters["yearFrom"]): return False
    if filters.get("yearTo") and y and y>int(filters["yearTo"]): return False
    work=_clean(filters.get("workType"),100).lower()
    return not work or work in _clean(candidate.get("workType"),100).lower()


def _dedupe_key(candidate: dict[str,Any]) -> str:
    if candidate.get("doi"): return "doi:"+_doi(candidate["doi"])
    if candidate.get("isbn"): return "isbn:"+candidate["isbn"][0]
    title=re.sub(r"[^a-z0-9]+","",_clean(candidate.get("title"),1200).lower())
    lead=(candidate.get("authors") or [""])[0].lower()
    return f"title:{title}:{candidate.get('year') or ''}:{re.sub(r'[^a-z0-9]+','',lead)}"


def _merge(a: dict[str,Any], b: dict[str,Any]) -> dict[str,Any]:
    out=dict(a)
    for field in ["title","authors","year","workType","publisher","containerTitle","doi","url","abstract","subjects","identifiers","isbn","citationCount","isOpenAccess","openAccessStatus","openAccessUrl","license"]:
        av=out.get(field); bv=b.get(field)
        if field in {"authors","subjects","isbn"}:
            out[field]=list(dict.fromkeys((av or [])+(bv or [])))[:100]
        elif field=="identifiers": out[field]={**(av or {}),**(bv or {})}
        elif field=="citationCount": out[field]=max(int(av or 0),int(bv or 0))
        elif field=="isOpenAccess": out[field]=bool(av or bv)
        elif (not av) or (isinstance(av,str) and isinstance(bv,str) and len(bv)>len(av)): out[field]=bv
    out["providers"]=list(dict.fromkeys((a.get("providers") or [a.get("provider")])+(b.get("providers") or [b.get("provider")])))
    out["citation"]=_citation(out)
    out["fingerprint"]=_hash({"key":_dedupe_key(out),"providers":out["providers"]})
    return out


def deduplicate(payload: dict[str,Any] | list[dict[str,Any]]) -> dict[str,Any]:
    candidates=payload if isinstance(payload,list) else payload.get("candidates") or []
    if not isinstance(candidates,list): raise DiscoveryError("candidates must be an array.")
    merged: dict[str,dict[str,Any]]={}
    for raw in candidates[:500]:
        if not isinstance(raw,dict): continue
        provider=_clean(raw.get("provider") or "imported",50)
        candidate=_candidate(provider,raw) if raw.get("schema")!=CANDIDATE_SCHEMA else dict(raw)
        key=_dedupe_key(candidate)
        merged[key]=_merge(merged[key],candidate) if key in merged else candidate
    values=list(merged.values())
    values.sort(key=lambda x:(-int(x.get("citationCount") or 0),-(x.get("year") or 0),x.get("title") or ""))
    return {"ok":True,"version":VERSION,"schema":"sc-lab-discovery-deduplication/0.29.2","inputCount":len(candidates),"resultCount":len(values),"duplicatesRemoved":max(0,len(candidates)-len(values)),"candidates":values}


def handoffs(query: str, candidate: dict[str,Any] | None=None, settings_obj=settings) -> list[dict[str,Any]]:
    candidate=candidate or {}
    title=candidate.get("title") or query
    doi=candidate.get("doi") or ""
    q=quote(title)
    out=[
        {"provider":"worldcat","label":"Search WorldCat","mode":"catalog-handoff","url":f"https://search.worldcat.org/search?q={q}"},
        {"provider":"google-scholar","label":"Search Google Scholar","mode":"search-handoff","url":f"https://scholar.google.com/scholar?q={q}"},
    ]
    if doi: out.insert(0,{"provider":"doi","label":"Open DOI record","mode":"identifier-resolution","url":f"https://doi.org/{quote(doi,safe='/')}",})
    resolver=build_openurl({"candidate":candidate},settings_obj)
    if resolver.get("url"): out.append({"provider":"openurl","label":"Check institutional access","mode":"openurl-handoff","url":resolver["url"]})
    return out


def search(payload: dict[str,Any], settings_obj=settings, fetch_json: Callable | None=None) -> dict[str,Any]:
    if not isinstance(payload,dict): raise DiscoveryError("A discovery search object is required.")
    query=_clean(payload.get("query"),500)
    if len(query)<2: raise DiscoveryError("query must contain at least two characters.")
    requested=payload.get("providers") or ["crossref","datacite"]
    if not isinstance(requested,list): raise DiscoveryError("providers must be an array.")
    providers=[]
    for value in requested[:10]:
        provider=_clean(value,50).lower()
        if provider not in ALLOWED_PROVIDERS: raise DiscoveryError(f"Unsupported live provider: {provider}")
        if provider not in providers: providers.append(provider)
    limit=max(1,min(int(payload.get("maxResults") or 10),min(25,getattr(settings_obj,"discovery_max_results",25))))
    filters=payload.get("filters") or {}
    fetch_json=fetch_json or _request_json
    all_candidates=[]; reports=[]
    functions={"crossref":_search_crossref,"datacite":_search_datacite,"openalex":_search_openalex}
    for provider in providers:
        started=_now()
        try:
            found=functions[provider](query,limit,filters,settings_obj,fetch_json)
            found=[x for x in found if _matches(x,filters)]
            all_candidates.extend(found)
            reports.append({"provider":provider,"ok":True,"count":len(found),"startedAt":started,"completedAt":_now()})
        except Exception as exc:
            reports.append({"provider":provider,"ok":False,"count":0,"error":_clean(str(exc),1000),"startedAt":started,"completedAt":_now()})
    deduped=deduplicate(all_candidates)
    candidates=deduped["candidates"] if payload.get("deduplicate",True) else all_candidates
    for candidate in candidates: candidate["handoffs"]=handoffs(query,candidate,settings_obj)
    return {"ok":True,"version":VERSION,"schema":SEARCH_SCHEMA,"query":query,"providers":providers,"filters":filters,"requestedMaxResults":limit,"providerReports":reports,"rawCandidateCount":len(all_candidates),"candidateCount":len(candidates),"duplicatesRemoved":deduped["duplicatesRemoved"],"candidates":candidates,"handoffs":handoffs(query,None,settings_obj),"retrievedAt":_now()}


def normalize(payload: dict[str,Any]) -> dict[str,Any]:
    candidate=payload.get("candidate") if isinstance(payload,dict) and isinstance(payload.get("candidate"),dict) else payload
    if not isinstance(candidate,dict): raise DiscoveryError("candidate is required.")
    provider=_clean(candidate.get("provider") or "imported",50)
    normalized=_candidate(provider,candidate) if candidate.get("schema")!=CANDIDATE_SCHEMA else dict(candidate)
    source={
        "schema":"sc-lab-research-source/0.29.0","version":VERSION,"recordType":"research-source","collection":"researchSources",
        "id":_clean(payload.get("id") if isinstance(payload,dict) else "",200) or f"src-{normalized['fingerprint'][:16]}",
        "projectId":payload.get("projectId") if isinstance(payload,dict) else None,"title":normalized.get("title"),"authors":normalized.get("authors"),"year":normalized.get("year"),
        "sourceType":normalized.get("workType") or "scholarly-work","publisher":normalized.get("publisher") or normalized.get("containerTitle"),"doi":normalized.get("doi"),"url":normalized.get("url"),
        "license":normalized.get("license"),"citation":normalized.get("citation"),"createdAt":_now(),
        "externalDiscovery":{"schema":IMPORT_SCHEMA,"providers":normalized.get("providers") or [provider],"providerId":normalized.get("providerId"),"fingerprint":normalized.get("fingerprint"),"isOpenAccess":normalized.get("isOpenAccess"),"openAccessStatus":normalized.get("openAccessStatus"),"openAccessUrl":normalized.get("openAccessUrl"),"subjects":normalized.get("subjects"),"identifiers":normalized.get("identifiers"),"retrievedAt":normalized.get("retrievedAt")},
    }
    source["sha256"]=_hash({k:v for k,v in source.items() if k!="sha256"})
    return {"ok":True,"version":VERSION,"source":source}


def build_openurl(payload: dict[str,Any], settings_obj=settings) -> dict[str,Any]:
    candidate=payload.get("candidate") if isinstance(payload,dict) and isinstance(payload.get("candidate"),dict) else payload
    candidate=candidate if isinstance(candidate,dict) else {}
    genre="book" if "book" in _clean(candidate.get("workType"),100).lower() else "article"
    params={"ctx_ver":"Z39.88-2004","rfr_id":"info:sid/sustainablecatalyst.com:lab","rft.genre":genre}
    if candidate.get("doi"): params["rft_id"]="info:doi/"+_doi(candidate.get("doi"))
    if candidate.get("title"): params["rft.atitle" if genre=="article" else "rft.btitle"]=_clean(candidate.get("title"),1200)
    if candidate.get("containerTitle"): params["rft.jtitle"]=_clean(candidate.get("containerTitle"),500)
    if candidate.get("authors"): params["rft.au"]=_clean((candidate.get("authors") or [""])[0],300)
    if candidate.get("year"): params["rft.date"]=str(candidate.get("year"))
    if candidate.get("isbn"): params["rft.isbn"]=(candidate.get("isbn") or [""])[0]
    base=getattr(settings_obj,"openurl_resolver_base", "").strip()
    url=""
    if base:
        parsed=urlparse(base)
        if parsed.scheme not in {"https","http"} or not parsed.netloc: raise DiscoveryError("Configured OpenURL resolver base is invalid.")
        existing=dict(parse_qsl(parsed.query,keep_blank_values=True)); existing.update(params)
        url=urlunparse((parsed.scheme,parsed.netloc,parsed.path,parsed.params,urlencode(existing),parsed.fragment))
    return {"ok":True,"version":VERSION,"configured":bool(base),"url":url,"parameters":params}


def open_access_lookup(payload: dict[str,Any], settings_obj=settings, fetch_json: Callable | None=None) -> dict[str,Any]:
    candidate=payload.get("candidate") if isinstance(payload,dict) and isinstance(payload.get("candidate"),dict) else payload
    candidate=candidate if isinstance(candidate,dict) else {}
    doi=_doi(payload.get("doi") if isinstance(payload,dict) else "") or _doi(candidate.get("doi"))
    if not doi: raise DiscoveryError("A DOI is required for open-access lookup.")
    result={"doi":doi,"isOpenAccess":bool(candidate.get("isOpenAccess")),"status":candidate.get("openAccessStatus") or "unknown","bestUrl":candidate.get("openAccessUrl") or "","license":candidate.get("license") or "","sources":list(candidate.get("providers") or [])}
    key=getattr(settings_obj,"openalex_api_key", "")
    if key:
        fetch_json=fetch_json or _request_json
        params={"filter":f"doi:https://doi.org/{doi}","per-page":1,"api_key":key}
        try:
            payload_oa=fetch_json(_with_params("https://api.openalex.org/works",params),_headers(settings_obj,"openalex"),settings_obj.discovery_timeout_seconds)
            rows=payload_oa.get("results") or []
            if rows:
                oa=_openalex(rows[0]); result.update({"isOpenAccess":oa.get("isOpenAccess"),"status":oa.get("openAccessStatus"),"bestUrl":oa.get("openAccessUrl") or oa.get("url"),"license":oa.get("license")}); result["sources"]=list(dict.fromkeys(result["sources"]+["openalex"]))
        except Exception as exc: result["warning"]=_clean(str(exc),1000)
    result["doiUrl"]=f"https://doi.org/{quote(doi,safe='/')}"
    return {"ok":True,"version":VERSION,"lookup":result,"retrievedAt":_now()}
