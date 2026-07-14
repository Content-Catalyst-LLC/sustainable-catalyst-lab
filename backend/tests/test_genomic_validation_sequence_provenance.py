from copy import deepcopy
from app.genomic_validation_sequence_provenance import contract,create_dossier,create_manifest,create_record,evaluate,verify_ledger
def test_contract_and_profiles():
 c=contract();assert c["version"]=="0.24.3";assert len(c["profiles"])==8;assert len(c["eventTypes"])==6
def test_validation_profiles():
 assert evaluate("sequence-record-integrity",[{"sequenceId":"s1","sequence":"ACGTN","alphabet":"DNA"}])["decision"]=="pass"
 assert evaluate("variant-record-integrity",[{"variantId":"v1","referenceBase":"A","alternateBase":"G","position":10,"readDepth":30,"alternateDepth":12}])["decision"]=="pass"
 assert evaluate("release-readiness",[{"checkId":"c1","critical":True,"status":"pass","evidence":"record://1"}])["decision"]=="pass"
def test_manifest_ledger_and_tamper():
 manifest=create_manifest([{"id":"s1","sequence":"ACGT"}],[{"sequenceId":"s1"}],{"build":"GRCh38"},[{"step":"align"}],[],[])
 first=create_record(manifest,{"recordId":"r1","timestamp":"2026-07-14T00:00:00+00:00","eventType":"sequence-import","datasetId":"d1"})
 second=create_record({"decision":"pass"},{"recordId":"r2","timestamp":"2026-07-14T00:01:00+00:00","eventType":"validation-decision","datasetId":"d1"},first["recordHash"])
 assert verify_ledger([first,second])["valid"] is True
 tampered=deepcopy([first,second]);tampered[1]["payload"]["decision"]="fail";assert verify_ledger(tampered)["valid"] is False
 dossier=create_dossier([evaluate("sequence-record-integrity",[{"sequenceId":"s1","sequence":"ACGT","alphabet":"DNA"}])],manifest,[first,second],"release")
 assert dossier["summary"]["releaseReady"] is True and len(dossier["dossierHash"])==64
