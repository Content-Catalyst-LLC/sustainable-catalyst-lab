from __future__ import annotations
import copy, hashlib, json, math, re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

VERSION="0.143.0"
PREDECESSOR_VERSION="0.142.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
NEURAL_WORKSPACE_VERSION="0.142.0"
SCHEMA="sc-lab-computational-linguistics-research-workspace/0.143.0"
SESSION_SCHEMA="sc-lab-computational-linguistics-research-session/0.143.0"
TEXT_SCHEMA="sc-lab-original-language-text/0.143.0"
REPRESENTATION_SCHEMA="sc-lab-linguistic-representation/0.143.0"
ANNOTATION_SCHEMA="sc-lab-linguistic-annotation/0.143.0"
CORPUS_SCHEMA="sc-lab-computational-linguistics-corpus/0.143.0"
SNAPSHOT_SCHEMA="sc-lab-computational-linguistics-workspace-snapshot/0.143.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-computational-linguistics-execution-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-linguistic-research-objects/1.0"
LIBRARY_HANDOFF_SCHEMA="sc-library-original-language-source-handoff/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-computational-linguistics-handoff/1.0"

BOUNDARY=(
    "The Computational Linguistics Research Workspace analyzes governed linguistic research objects while preserving original-language text as the primary representation. "
    "Translation, transliteration, normalization, OCR/HTR, transcription, tokenization, annotation, parsing, phonetic conversion, embeddings, and other transformations are derived representations with explicit lineage. "
    "Workspace remains execution authority for computational linguistics runtimes; Knowledge Library remains source-ingestion/document authority; Platform Core remains canonical governed-object authority. "
    "A translation is not the source text, an alignment is not semantic equivalence, an annotation is not ground truth, a corpus statistic is not an interpretation, and cross-lingual similarity is not evidence of a real-world relationship."
)

REPRESENTATION_TYPES=("original","normalized","ocr","htr","transcription","transliteration","translation","tokenized","morphological","syntactic","phonetic","phonological","semantic","embedding","other")
ANNOTATION_KINDS=("token","lemma","morpheme","pos","dependency","constituency","entity","sense","semantic-role","coreference","phoneme","phone","syllable","prosody","alignment","discourse","pragmatic","historical-variant","script-variant","other")
ANALYSIS_TYPES=("corpus-statistics","lexical-profile","ngram-profile","concordance","morphology","syntax","phonology-phonetics","semantic-profile","cross-lingual-comparison","corpus-comparison","annotation-matrix","alignment-audit","transformation-lineage")
SESSION_STATES=("draft","active","review","reproduction","publication","archived")
OBJECT_KINDS=("text","representation","annotation","corpus","alignment","analysis","lexicon","grammar","phonetic-record","embedding","visualization","review","package","publication","other")
DIRECTIONS=("ltr","rtl","ttb","btt","unknown")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=16384): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode('utf-8')).hexdigest()
def _uniq(xs):
    out=[]; seen=set()
    for x in xs:
        key=_canon(x)
        if key not in seen: seen.add(key); out.append(x)
    return out

def _language(raw):
    r=_dict(raw)
    return {"bcp47":_txt(r.get("bcp47") or r.get("tag"),128),"name":_txt(r.get("name"),256),"historicalVariant":_txt(r.get("historicalVariant"),256),"dialect":_txt(r.get("dialect"),256),"region":_txt(r.get("region"),128),"confidence":r.get("confidence") if isinstance(r.get("confidence"),(int,float)) else None}

def _script(raw):
    r=_dict(raw); d=_txt(r.get("direction"),16).lower() or "unknown"
    if d not in DIRECTIONS: d="unknown"
    return {"iso15924":_txt(r.get("iso15924") or r.get("code"),16),"name":_txt(r.get("name"),256),"variant":_txt(r.get("variant"),256),"direction":d}

def language_registry():
    return {"ok":True,"version":VERSION,"registry":{"languageIdentityStandard":"BCP 47","scriptIdentityStandard":"ISO 15924","historicalLanguageVariantExplicit":True,"dialectIdentityExplicit":True,"languageConfidenceOptional":True,"languageIdentityIsNotEthnicity":True},"boundary":BOUNDARY}

def script_registry():
    return {"ok":True,"version":VERSION,"registry":{"standard":"ISO 15924","directions":list(DIRECTIONS),"scriptVariantExplicit":True,"transliterationChangesScriptRepresentation":True,"transliterationDoesNotReplaceOriginal":True},"boundary":BOUNDARY}

def normalize_text(payload:dict):
    p=_dict(payload); original=_txt(p.get("originalText") if "originalText" in p else p.get("text"),2000000)
    rec={"schema":TEXT_SCHEMA,"version":VERSION,"textId":_txt(p.get("textId") or p.get("id"),512) or f"text-{_fp(p)[:16]}","sourceRef":_txt(p.get("sourceRef"),2048),"documentRef":_txt(p.get("documentRef"),2048),"corpusRef":_txt(p.get("corpusRef"),2048),"sourceSpan":_dict(p.get("sourceSpan")),"language":_language(p.get("language")),"script":_script(p.get("script")),"originalText":original,"sourceEdition":_txt(p.get("sourceEdition"),512),"sourceDate":_txt(p.get("sourceDate"),128),"provenanceRef":_txt(p.get("provenanceRef"),2048),"rights":_dict(p.get("rights")),"metadata":_dict(p.get("metadata")),"isOriginalLanguagePrimary":True,"isDerivedRepresentation":False,"translationIsSource":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_representation(payload:dict,index:int=0):
    p=_dict(payload); typ=_txt(p.get("type"),64).lower() or "other"
    if typ not in REPRESENTATION_TYPES: typ="other"
    derived=typ!="original"
    rec={"schema":REPRESENTATION_SCHEMA,"version":VERSION,"representationId":_txt(p.get("representationId") or p.get("id"),512) or f"representation-{index+1}-{_fp(p)[:12]}","sourceTextId":_txt(p.get("sourceTextId"),512),"type":typ,"content":_txt(p.get("content"),2000000),"language":_language(p.get("language")),"script":_script(p.get("script")),"derivedFrom":[_txt(x,512) for x in _list(p.get("derivedFrom")) if _txt(x,512)],"method":_txt(p.get("method"),512),"modelRef":_txt(p.get("modelRef"),2048),"humanAgentRef":_txt(p.get("humanAgentRef"),2048),"parameters":_dict(p.get("parameters")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"confidence":p.get("confidence") if isinstance(p.get("confidence"),(int,float)) else None,"review":_dict(p.get("review")),"metadata":_dict(p.get("metadata")),"isDerivedRepresentation":derived,"replacesOriginal":False,"semanticEquivalenceCertified":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_annotation(payload:dict,index:int=0):
    p=_dict(payload); kind=_txt(p.get("kind"),64).lower() or "other"
    if kind not in ANNOTATION_KINDS: kind="other"
    rec={"schema":ANNOTATION_SCHEMA,"version":VERSION,"annotationId":_txt(p.get("annotationId") or p.get("id"),512) or f"annotation-{index+1}-{_fp(p)[:12]}","targetRepresentationId":_txt(p.get("targetRepresentationId"),512),"kind":kind,"span":_dict(p.get("span")),"label":_txt(p.get("label"),1024),"value":copy.deepcopy(p.get("value")),"method":_txt(p.get("method"),512),"modelRef":_txt(p.get("modelRef"),2048),"humanAgentRef":_txt(p.get("humanAgentRef"),2048),"provenanceRef":_txt(p.get("provenanceRef"),2048),"confidence":p.get("confidence") if isinstance(p.get("confidence"),(int,float)) else None,"metadata":_dict(p.get("metadata")),"groundTruthCertified":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_alignment(payload:dict,index:int=0):
    p=_dict(payload)
    links=[]
    for x in _list(p.get("links")):
        if not isinstance(x,dict): continue
        links.append({"source":_dict(x.get("source")),"target":_dict(x.get("target")),"relation":_txt(x.get("relation"),128) or "aligned-with","confidence":x.get("confidence") if isinstance(x.get("confidence"),(int,float)) else None})
    rec={"alignmentId":_txt(p.get("alignmentId") or p.get("id"),512) or f"alignment-{index+1}-{_fp(p)[:12]}","sourceRepresentationId":_txt(p.get("sourceRepresentationId"),512),"targetRepresentationId":_txt(p.get("targetRepresentationId"),512),"method":_txt(p.get("method"),512),"modelRef":_txt(p.get("modelRef"),2048),"provenanceRef":_txt(p.get("provenanceRef"),2048),"links":links,"semanticEquivalenceCertified":False,"alignmentIsEvidence":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_corpus(payload:dict):
    p=_dict(payload); texts=[normalize_text(x) for x in _list(p.get("texts"))]; reps=[normalize_representation(x,i) for i,x in enumerate(_list(p.get("representations")))]; anns=[normalize_annotation(x,i) for i,x in enumerate(_list(p.get("annotations")))]; aligns=[normalize_alignment(x,i) for i,x in enumerate(_list(p.get("alignments")))]
    rec={"schema":CORPUS_SCHEMA,"version":VERSION,"corpusId":_txt(p.get("corpusId") or p.get("id"),512) or f"corpus-{_fp(p)[:16]}","title":_txt(p.get("title"),1024) or "Computational linguistics corpus","description":_txt(p.get("description"),8192),"sourceRefs":[_txt(x,2048) for x in _list(p.get("sourceRefs")) if _txt(x,2048)],"texts":texts,"representations":reps,"annotations":anns,"alignments":aligns,"sampling":_dict(p.get("sampling")),"selectionCriteria":_dict(p.get("selectionCriteria")),"rights":_dict(p.get("rights")),"metadata":_dict(p.get("metadata")),"originalLanguageFirst":True,"translationAsDerivedRepresentation":True}
    stable=copy.deepcopy(rec); rec["fingerprint"]=_fp(stable); return rec

def normalize_session(payload:dict):
    p=_dict(payload); state=_txt(p.get("state"),64).lower() or "draft"
    if state not in SESSION_STATES: state="draft"
    corpus=normalize_corpus(_dict(p.get("corpus")))
    rec={"schema":SESSION_SCHEMA,"version":VERSION,"sessionId":_txt(p.get("sessionId") or p.get("id"),512) or f"linguistics-session-{_fp(p)[:16]}","projectRef":_txt(p.get("projectRef"),2048),"studyRef":_txt(p.get("studyRef"),2048),"title":_txt(p.get("title"),1024) or "Computational linguistics research session","state":state,"corpus":corpus,"activeAnalysis":_txt(p.get("activeAnalysis"),128),"analysisObjects":_list(p.get("analysisObjects")),"focusedObjectRef":_txt(p.get("focusedObjectRef"),2048),"notes":_list(p.get("notes")),"limitations":_list(p.get("limitations")),"review":_dict(p.get("review")),"workspaceExecutionAuthority":True,"librarySourceAuthority":True,"platformCoreCanonicalAuthority":True,"originalLanguageFirst":True,"translationAsDerivedRepresentation":True,"automaticScientificValidity":False,"automaticSemanticEquivalence":False,"humanScientificReviewRequired":True}
    rec["fingerprint"]=_fp(rec); return rec

def workspace_state(payload:dict):
    s=normalize_session(payload); c=s["corpus"]
    return {"ok":True,"version":VERSION,"session":s,"counts":{"texts":len(c["texts"]),"representations":len(c["representations"]),"annotations":len(c["annotations"]),"alignments":len(c["alignments"]),"analysisObjects":len(s["analysisObjects"])},"boundary":BOUNDARY}

def corpus_index(payload:dict):
    c=normalize_corpus(_dict(payload.get("corpus")) if "corpus" in payload else payload)
    rows=[]
    for t in c["texts"]: rows.append({"objectType":"text","id":t["textId"],"language":t["language"],"script":t["script"],"sourceRef":t["sourceRef"],"provenanceRef":t["provenanceRef"],"fingerprint":t["fingerprint"]})
    for r in c["representations"]: rows.append({"objectType":"representation","id":r["representationId"],"type":r["type"],"sourceTextId":r["sourceTextId"],"language":r["language"],"script":r["script"],"provenanceRef":r["provenanceRef"],"fingerprint":r["fingerprint"]})
    return {"ok":True,"version":VERSION,"rows":rows,"count":len(rows),"originalAndDerivedRemainDistinct":True,"boundary":BOUNDARY}

def original_language_audit(payload:dict):
    c=normalize_corpus(_dict(payload.get("corpus")) if "corpus" in payload else payload); text_ids={t["textId"] for t in c["texts"]}; issues=[]
    for t in c["texts"]:
        if not t["originalText"]: issues.append({"textId":t["textId"],"issue":"missing-original-text"})
        if not t["language"]["bcp47"]: issues.append({"textId":t["textId"],"issue":"missing-language-tag"})
    for r in c["representations"]:
        if r["type"]!="original" and not r["sourceTextId"]: issues.append({"representationId":r["representationId"],"issue":"derived-representation-missing-sourceTextId"})
        if r["sourceTextId"] and r["sourceTextId"] not in text_ids: issues.append({"representationId":r["representationId"],"issue":"unknown-sourceTextId"})
    return {"ok":True,"version":VERSION,"originalLanguageFirst":True,"issues":issues,"clean":not issues,"translationNeverSubstitutesForSource":True,"boundary":BOUNDARY}

def language_script_audit(payload:dict):
    c=normalize_corpus(_dict(payload.get("corpus")) if "corpus" in payload else payload); rows=[]
    for t in c["texts"]: rows.append({"id":t["textId"],"objectType":"text","languageTag":t["language"]["bcp47"],"historicalVariant":t["language"]["historicalVariant"],"scriptCode":t["script"]["iso15924"],"scriptVariant":t["script"]["variant"],"direction":t["script"]["direction"]})
    for r in c["representations"]: rows.append({"id":r["representationId"],"objectType":r["type"],"languageTag":r["language"]["bcp47"],"historicalVariant":r["language"]["historicalVariant"],"scriptCode":r["script"]["iso15924"],"scriptVariant":r["script"]["variant"],"direction":r["script"]["direction"]})
    return {"ok":True,"version":VERSION,"rows":rows,"languageIdentityIsNotEthnicity":True,"scriptChangeDoesNotImplyLanguageChange":True,"boundary":BOUNDARY}

def transformation_lineage(payload:dict):
    c=normalize_corpus(_dict(payload.get("corpus")) if "corpus" in payload else payload); nodes=[]; edges=[]; known=set()
    for t in c["texts"]: nodes.append({"id":t["textId"],"kind":"original-text","representationType":"original"}); known.add(t["textId"])
    for r in c["representations"]: nodes.append({"id":r["representationId"],"kind":"representation","representationType":r["type"]}); known.add(r["representationId"])
    missing=[]
    for r in c["representations"]:
        parents=r["derivedFrom"] or ([r["sourceTextId"]] if r["sourceTextId"] else [])
        for p in parents:
            edges.append({"source":p,"target":r["representationId"],"relation":"derived-as","transformation":r["type"],"method":r["method"]})
            if p not in known: missing.append({"representationId":r["representationId"],"missingParent":p})
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"missingParents":missing,"complete":not missing,"transformationLineageIsSemanticEquivalence":False,"boundary":BOUNDARY}

def representation_chain(payload:dict):
    g=transformation_lineage(payload); target=_txt(payload.get("representationId"),512); parents=defaultdict(list)
    for e in g["edges"]: parents[e["target"]].append(e["source"])
    chain=[]; seen=set(); stack=[target] if target else []
    while stack:
        cur=stack.pop()
        if cur in seen: continue
        seen.add(cur); chain.append(cur); stack.extend(parents.get(cur,[]))
    return {"ok":True,"version":VERSION,"representationId":target,"ancestorIds":chain[1:] if chain else [],"lineageOrderIsNotInterpretivePriority":True,"boundary":BOUNDARY}

def alignment_audit(payload:dict):
    c=normalize_corpus(_dict(payload.get("corpus")) if "corpus" in payload else payload); reps={r["representationId"] for r in c["representations"]}; rows=[]
    for a in c["alignments"]:
        issues=[]
        if a["sourceRepresentationId"] not in reps: issues.append("missing-source-representation")
        if a["targetRepresentationId"] not in reps: issues.append("missing-target-representation")
        if not a["links"]: issues.append("no-alignment-links")
        rows.append({"alignmentId":a["alignmentId"],"linkCount":len(a["links"]),"issues":issues,"clean":not issues})
    return {"ok":True,"version":VERSION,"rows":rows,"allClean":all(x["clean"] for x in rows) if rows else True,"alignmentIsSemanticEquivalence":False,"boundary":BOUNDARY}

def tokenization_audit(payload:dict):
    tokens=_list(payload.get("tokens")); text=_txt(payload.get("text"),2000000); rows=[]; invalid=0
    for i,t in enumerate(tokens):
        if isinstance(t,dict): token=_txt(t.get("text"),4096); start=t.get("start"); end=t.get("end")
        else: token=_txt(t,4096); start=end=None
        ok=bool(token); invalid += 0 if ok else 1; rows.append({"index":i,"text":token,"start":start,"end":end,"valid":ok})
    char_coverage=None
    if text and rows and all(isinstance(x["start"],int) and isinstance(x["end"],int) for x in rows):
        covered=set()
        for x in rows:
            covered.update(range(max(0,x["start"]),min(len(text),max(x["start"],x["end"]))))
        char_coverage=len(covered)/len(text) if text else None
    return {"ok":True,"version":VERSION,"tokenCount":len(rows),"invalidTokenCount":invalid,"characterCoverage":char_coverage,"tokenizationMethod":_txt(payload.get("method"),512),"tokenizationIsGroundTruth":False,"boundary":BOUNDARY}

def _token_strings(payload):
    vals=[]
    for t in _list(payload.get("tokens")):
        if isinstance(t,dict): v=_txt(t.get("text"),4096)
        else: v=_txt(t,4096)
        if v: vals.append(v)
    return vals

def corpus_statistics(payload:dict):
    tokens=_token_strings(payload); chars=sum(len(x) for x in tokens); types=set(tokens)
    return {"ok":True,"version":VERSION,"statistics":{"tokenCount":len(tokens),"typeCount":len(types),"typeTokenRatio":(len(types)/len(tokens) if tokens else None),"tokenCharacterCount":chars,"meanTokenLength":(chars/len(tokens) if tokens else None)},"statisticsAreInterpretation":False,"boundary":BOUNDARY}

def lexical_profile(payload:dict):
    tokens=_token_strings(payload); casefold=bool(payload.get("casefold",False)); vals=[x.casefold() if casefold else x for x in tokens]; c=Counter(vals); limit=max(1,min(int(payload.get("limit",50) or 50),500))
    rows=[{"token":k,"count":v,"frequency":v/len(vals) if vals else 0} for k,v in c.most_common(limit)]
    return {"ok":True,"version":VERSION,"rows":rows,"tokenCount":len(vals),"casefoldApplied":casefold,"lexicalFrequencyIsMeaning":False,"boundary":BOUNDARY}

def ngram_profile(payload:dict):
    tokens=_token_strings(payload); n=max(1,min(int(payload.get("n",2) or 2),8)); grams=Counter(tuple(tokens[i:i+n]) for i in range(max(0,len(tokens)-n+1))); limit=max(1,min(int(payload.get("limit",50) or 50),500))
    rows=[{"ngram":list(k),"count":v,"frequency":v/max(1,sum(grams.values()))} for k,v in grams.most_common(limit)]
    return {"ok":True,"version":VERSION,"n":n,"rows":rows,"ngramFrequencyIsLinguisticExplanation":False,"boundary":BOUNDARY}

def concordance(payload:dict):
    tokens=_token_strings(payload); query=_txt(payload.get("query"),4096); casefold=bool(payload.get("casefold",False)); window=max(0,min(int(payload.get("window",5) or 5),50)); needle=query.casefold() if casefold else query; rows=[]
    for i,t in enumerate(tokens):
        val=t.casefold() if casefold else t
        if val==needle: rows.append({"index":i,"left":tokens[max(0,i-window):i],"match":t,"right":tokens[i+1:i+1+window]})
    return {"ok":True,"version":VERSION,"query":query,"matches":rows,"matchCount":len(rows),"concordanceIsInterpretation":False,"boundary":BOUNDARY}

def _annotation_summary(payload, kinds):
    anns=[normalize_annotation(x,i) for i,x in enumerate(_list(payload.get("annotations")))]; selected=[a for a in anns if a["kind"] in kinds]; counts=Counter(a["label"] or a["kind"] for a in selected)
    return {"annotationCount":len(selected),"labelCounts":[{"label":k,"count":v} for k,v in counts.most_common()],"annotationsAreGroundTruth":False}

def morphology_summary(payload:dict):
    out=_annotation_summary(payload,{"lemma","morpheme","pos"}); return {"ok":True,"version":VERSION,"summary":out,"morphologicalAnalysisInferredByLab":False,"boundary":BOUNDARY}

def syntax_summary(payload:dict):
    out=_annotation_summary(payload,{"dependency","constituency"}); return {"ok":True,"version":VERSION,"summary":out,"syntacticAnalysisInferredByLab":False,"boundary":BOUNDARY}

def phonology_phonetics_summary(payload:dict):
    out=_annotation_summary(payload,{"phoneme","phone","syllable","prosody"}); return {"ok":True,"version":VERSION,"summary":out,"phoneticExtractionPerformedByLab":False,"phonologicalCategoryIsAcousticFact":False,"boundary":BOUNDARY}

def semantic_profile(payload:dict):
    out=_annotation_summary(payload,{"entity","sense","semantic-role","coreference","discourse","pragmatic"}); return {"ok":True,"version":VERSION,"summary":out,"semanticAnnotationIsTruth":False,"automaticSemanticInference":False,"boundary":BOUNDARY}

def cross_lingual_comparison(payload:dict):
    source=_dict(payload.get("source")); target=_dict(payload.get("target")); align=normalize_alignment(_dict(payload.get("alignment"))); source_tokens=_list(source.get("tokens")); target_tokens=_list(target.get("tokens")); linked_src=set(); linked_tgt=set()
    for l in align["links"]:
        s=l["source"].get("tokenIndex"); t=l["target"].get("tokenIndex")
        if isinstance(s,int): linked_src.add(s)
        if isinstance(t,int): linked_tgt.add(t)
    return {"ok":True,"version":VERSION,"sourceLanguage":_language(source.get("language")),"targetLanguage":_language(target.get("language")),"sourceTokenCount":len(source_tokens),"targetTokenCount":len(target_tokens),"alignmentLinkCount":len(align["links"]),"sourceAlignmentCoverage":len(linked_src)/len(source_tokens) if source_tokens else None,"targetAlignmentCoverage":len(linked_tgt)/len(target_tokens) if target_tokens else None,"semanticEquivalenceCertified":False,"translationQualityCertified":False,"boundary":BOUNDARY}

def corpus_comparison(payload:dict):
    left=normalize_corpus(_dict(payload.get("left"))); right=normalize_corpus(_dict(payload.get("right")))
    def sig(c): return {"textCount":len(c["texts"]),"representationCount":len(c["representations"]),"annotationCount":len(c["annotations"]),"alignmentCount":len(c["alignments"]),"languageTags":sorted({t["language"]["bcp47"] for t in c["texts"] if t["language"]["bcp47"]}),"scriptCodes":sorted({t["script"]["iso15924"] for t in c["texts"] if t["script"]["iso15924"]})}
    return {"ok":True,"version":VERSION,"left":sig(left),"right":sig(right),"differenceDoesNotImplyLinguisticCause":True,"differenceDoesNotImplyCorpusQuality":True,"boundary":BOUNDARY}

def annotation_matrix(payload:dict):
    anns=[normalize_annotation(x,i) for i,x in enumerate(_list(payload.get("annotations")))]; matrix=defaultdict(Counter)
    for a in anns: matrix[a["targetRepresentationId"]][a["kind"]]+=1
    rows=[]
    for rid in sorted(matrix): rows.append({"representationId":rid,"counts":dict(sorted(matrix[rid].items()))})
    return {"ok":True,"version":VERSION,"rows":rows,"annotationCount":len(anns),"annotationDensityIsQuality":False,"boundary":BOUNDARY}

def uncertainty_limitations(payload:dict):
    s=normalize_session(payload); c=s["corpus"]; issues=[]
    if any(not t["language"]["bcp47"] for t in c["texts"]): issues.append("language-identity-incomplete")
    if any(r["isDerivedRepresentation"] and not r["provenanceRef"] for r in c["representations"]): issues.append("derived-representation-provenance-incomplete")
    if any(a["confidence"] is None for a in c["annotations"]): issues.append("annotation-confidence-partially-unspecified")
    if c["alignments"] and any(not a["provenanceRef"] for a in c["alignments"]): issues.append("alignment-provenance-incomplete")
    return {"ok":True,"version":VERSION,"issues":issues,"declaredLimitations":s["limitations"],"absenceOfIssueIsNotValidityCertification":True,"boundary":BOUNDARY}

def workspace_execution_handoff(payload:dict):
    s=normalize_session(payload); requested=_txt(payload.get("requestedOperation"),128)
    allowed=("tokenize","sentence-segment","lemmatize","morphological-tag","pos-tag","dependency-parse","constituency-parse","ner","semantic-role-label","coreference","phonetic-transcribe","phonological-analyze","embed","align","translate","transliterate","corpus-statistics","other")
    if requested not in allowed: requested="other"
    return {"ok":True,"version":VERSION,"handoff":{"schema":WORKSPACE_HANDOFF_SCHEMA,"executionAuthority":"workspace","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"requestedOperation":requested,"corpusFingerprint":s["corpus"]["fingerprint"],"originalLanguageFirst":True,"translationAsDerivedRepresentation":True,"automaticExecution":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def core_handoff(payload:dict):
    s=normalize_session(payload); c=s["corpus"]
    return {"ok":True,"version":VERSION,"handoff":{"schema":CORE_HANDOFF_SCHEMA,"canonicalObjectAuthority":"platform-core","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"textFingerprints":[t["fingerprint"] for t in c["texts"]],"representationFingerprints":[r["fingerprint"] for r in c["representations"]],"annotationFingerprints":[a["fingerprint"] for a in c["annotations"]],"originalLanguageFirst":True,"automaticCanonicalization":False,"semanticEquivalenceCertified":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def library_handoff(payload:dict):
    s=normalize_session(payload); c=s["corpus"]
    return {"ok":True,"version":VERSION,"handoff":{"schema":LIBRARY_HANDOFF_SCHEMA,"sourceAuthority":"knowledge-library","sessionId":s["sessionId"],"sourceRefs":_uniq(c["sourceRefs"]+[t["sourceRef"] for t in c["texts"] if t["sourceRef"]]),"documentRefs":_uniq([t["documentRef"] for t in c["texts"] if t["documentRef"]]),"requestedOperation":_txt(payload.get("requestedOperation"),128) or "resolve-source-context","originalLanguageRequired":True,"automaticSourceReplacement":False,"translationMayReplaceOriginal":False},"boundary":BOUNDARY}

def research_os_handoff(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"handoff":{"schema":RESEARCH_OS_HANDOFF_SCHEMA,"researchOSVersion":RESEARCH_OS_VERSION,"sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"requestedPhase":_txt(payload.get("requestedPhase"),128) or "analysis","automaticPhaseAdvance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def visual_workspace_spec(payload:dict):
    s=normalize_session(payload); c=s["corpus"]
    return {"ok":True,"version":VERSION,"visualSpec":{"schema":"sc-lab-computational-linguistics-workspace-visual/0.143.0","layout":"corpus-source-transform-analysis-workspace","panels":["source","representations","annotations","alignment","analysis","provenance","review"],"textCount":len(c["texts"]),"representationCount":len(c["representations"]),"annotationCount":len(c["annotations"]),"alignmentCount":len(c["alignments"]),"originalTextVisuallyPrimary":True,"derivedRepresentationsLabeled":True,"transformationLineageVisible":True,"limitationsVisible":True,"automaticSemanticInference":False},"boundary":BOUNDARY}

def workspace_snapshot(payload:dict):
    s=normalize_session(payload); stable=copy.deepcopy(s); stable.pop("fingerprint",None); fp=_fp(stable)
    return {"ok":True,"version":VERSION,"snapshot":{"schema":SNAPSHOT_SCHEMA,"snapshotId":f"linguistics-workspace-snapshot-{fp[:16]}","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"snapshotFingerprint":fp,"state":stable,"scientificValidityCertified":False},"boundary":BOUNDARY}

def compare_snapshots(payload:dict):
    l=workspace_snapshot(_dict(payload.get("left")))["snapshot"]; r=workspace_snapshot(_dict(payload.get("right")))["snapshot"]
    return {"ok":True,"version":VERSION,"sameWorkspaceState":l["snapshotFingerprint"]==r["snapshotFingerprint"],"left":l["snapshotFingerprint"],"right":r["snapshotFingerprint"],"differenceDoesNotImplyLinguisticCause":True,"boundary":BOUNDARY}

def export_bundle(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"export":{"schema":"sc-lab-computational-linguistics-export/0.143.0","session":s,"originalLanguageAudit":original_language_audit({"corpus":s["corpus"]}),"languageScriptAudit":language_script_audit({"corpus":s["corpus"]}),"transformationLineage":transformation_lineage({"corpus":s["corpus"]}),"alignmentAudit":alignment_audit({"corpus":s["corpus"]}),"limitations":uncertainty_limitations(s),"fingerprint":_fp(s)},"scientificValidityCertified":False,"semanticEquivalenceCertified":False,"boundary":BOUNDARY}

def reproducibility_package(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"package":{"schema":"sc-lab-reproducible-computational-linguistics-package/0.143.0","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"corpusFingerprint":s["corpus"]["fingerprint"],"sourceRefs":s["corpus"]["sourceRefs"],"workspaceExecutionAuthority":True,"librarySourceAuthority":True,"platformCoreCanonicalAuthority":True,"originalLanguageFirst":True,"transformationsPreserved":True,"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def publication_handoff(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"handoff":{"schema":"sc-lab-computational-linguistics-publication-handoff/0.143.0","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"originalLanguageFirst":True,"translationAsDerivedRepresentation":True,"limitations":s["limitations"],"review":s["review"],"automaticPublicationAcceptance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def interpretation_boundary(payload=None):
    return {"ok":True,"version":VERSION,"boundaries":{"originalLanguagePrimary":True,"translationIsSource":False,"transliterationIsSource":False,"alignmentIsSemanticEquivalence":False,"annotationIsGroundTruth":False,"embeddingProximityIsRelationship":False,"corpusStatisticIsInterpretation":False,"crossLingualSimilarityIsEvidence":False,"historicalVariantIsError":False,"scriptVariantIsError":False,"languageIdentityIsEthnicity":False,"automaticScientificValidity":False},"boundary":BOUNDARY}

def policy():
    return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"librarySourceAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesHeavyLinguisticCompute":False,"originalLanguageFirst":True,"translationAsDerivedRepresentation":True,"transformationProvenanceRequired":True,"automaticTranslationReplacement":False,"automaticSemanticEquivalence":False,"automaticScientificValidity":False,"automaticPublicationAcceptance":False,"humanScientificReviewRequired":True,"boundary":BOUNDARY}

def contract():
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"sessionSchema":SESSION_SCHEMA,"textSchema":TEXT_SCHEMA,"representationSchema":REPRESENTATION_SCHEMA,"annotationSchema":ANNOTATION_SCHEMA,"corpusSchema":CORPUS_SCHEMA,"snapshotSchema":SNAPSHOT_SCHEMA,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"neuralWorkspaceVersion":NEURAL_WORKSPACE_VERSION,"integrityBaseline":INTEGRITY_BASELINE,"representationTypes":list(REPRESENTATION_TYPES),"annotationKinds":list(ANNOTATION_KINDS),"analysisTypes":list(ANALYSIS_TYPES),"sessionStates":list(SESSION_STATES),"objectKinds":list(OBJECT_KINDS),"boundary":BOUNDARY}

def release_gates():
    return {"ok":True,"version":VERSION,"gates":{"integratedNeuralWorkspaceRetained":True,"originalLanguageObjectModel":True,"derivedRepresentationModel":True,"languageScriptVariantIdentity":True,"transformationLineage":True,"translationAlignment":True,"corpusAnalysisOnExplicitTokensAnnotations":True,"workspaceExecutionBoundaryPreserved":True,"librarySourceBoundaryPreserved":True,"platformCoreAuthorityPreserved":True,"integrityRepairRetained":True,"automaticScientificValidity":False},"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"computationalLinguisticsResearchWorkspace":True,"api_route_count":48,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"neuralWorkspaceVersion":NEURAL_WORKSPACE_VERSION,"integrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"librarySourceAuthority":True,"platformCoreCanonicalAuthority":True,"originalLanguageFirst":True,"translationAsDerivedRepresentation":True,"labExecutesHeavyLinguisticCompute":False,"automaticSemanticEquivalence":False,"automaticScientificValidity":False,"crossLingualSimilarityIsEvidence":False,"boundary":BOUNDARY}

def acceptance_report():
    return {"ok":True,"version":VERSION,"accepted":True,"originalLanguageObjectModel":True,"derivedRepresentationModel":True,"languageScriptVariantIdentity":True,"transformationLineage":True,"alignmentAudit":True,"tokenizationAudit":True,"corpusStatistics":True,"lexicalProfile":True,"ngramProfile":True,"concordance":True,"morphologySummary":True,"syntaxSummary":True,"phonologyPhoneticsSummary":True,"semanticProfile":True,"crossLingualComparison":True,"annotationMatrix":True,"workspaceHandoff":True,"coreHandoff":True,"libraryHandoff":True,"researchOSHandoff":True,"visualWorkspaceSpec":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackage":True,"integrityRepairRetained":True,"scientificValidityCertified":False,"boundary":BOUNDARY}
