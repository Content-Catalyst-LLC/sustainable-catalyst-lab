from __future__ import annotations

import copy
import html
import json
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

VERSION = "0.37.0"
PACKAGE_SCHEMA = "sc-lab-reproducibility-package/0.37.0"
PUBLICATION_SCHEMA = "sc-lab-research-publication/0.37.0"
VERIFICATION_SCHEMA = "sc-lab-reproducibility-verification/0.37.0"
EXPORT_SCHEMA = "sc-lab-publication-export/0.37.0"
EVENT_SCHEMA = "sc-lab-publication-event/0.37.0"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
ROLE_RANK = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
PACKAGE_STATUSES = {"draft", "sealed", "published", "withdrawn"}
PUBLICATION_STATUSES = {"draft", "ready", "published", "withdrawn"}
RESOURCE_TYPES = {"artifact", "dataset", "workflow", "run", "experiment", "campaign", "model", "environment", "source", "evidence", "figure", "table", "software", "other"}
LICENSES = {"CC-BY-4.0", "CC-BY-SA-4.0", "CC0-1.0", "MIT", "Apache-2.0", "GPL-2.0-or-later", "proprietary", "custom"}
FORBIDDEN_KEYS = {"code", "shell", "command", "callback", "callbackurl", "executable", "script", "token", "secret", "password", "privatekey", "bytes", "binary", "rawdata", "datasetbytes"}

class PublicationStudioError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail = detail; self.status_code = status_code

def _now() -> str: return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def _stable(value: Any) -> str: return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def _hash(value: Any) -> str: return sha256(_stable(value).encode()).hexdigest()
def _text(value: Any, limit: int = 1000) -> str: return str(value or "").strip()[:limit]
def _id(value: Any, label: str = "identifier") -> str:
    clean = _text(value, 180)
    if not ID_RE.match(clean): raise PublicationStudioError(f"A valid {label} is required.")
    return clean
def _sha(value: Any, label: str = "SHA-256") -> str:
    clean = _text(value, 64).lower()
    if not SHA_RE.match(clean): raise PublicationStudioError(f"A valid {label} digest is required.")
    return clean
def _safe(value: Any, depth: int = 0) -> Any:
    if depth > 12: raise PublicationStudioError("Nested publication data exceeds the depth limit.", 413)
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            skey = _text(key, 120)
            if skey.lower().replace("_", "").replace("-", "") in FORBIDDEN_KEYS:
                raise PublicationStudioError(f"Executable, secret, or embedded byte field '{skey}' is not permitted.", 422)
            out[skey] = _safe(item, depth + 1)
        return out
    if isinstance(value, list): return [_safe(item, depth + 1) for item in value[:10000]]
    if value is None or isinstance(value, (bool, int, float)): return value
    return _text(value, 20000)
def _json_obj(value: Any, max_bytes: int = 1048576) -> dict[str, Any]:
    if value is None: return {}
    if not isinstance(value, dict): raise PublicationStudioError("A JSON object is required.")
    clean = _safe(copy.deepcopy(value))
    if len(_stable(clean).encode()) > max_bytes: raise PublicationStudioError("Publication payload exceeds the configured limit.", 413)
    return clean

def policies(max_packages: int = 5000, max_publications: int = 5000, max_resources: int = 1000) -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "schema": "sc-lab-publication-studio-policy/0.37.0", "schemas": {"package": PACKAGE_SCHEMA, "publication": PUBLICATION_SCHEMA, "verification": VERIFICATION_SCHEMA, "export": EXPORT_SCHEMA, "event": EVENT_SCHEMA}, "resourceTypes": sorted(RESOURCE_TYPES), "licenses": sorted(LICENSES), "formats": ["json", "markdown", "html", "citation-cff"], "limits": {"packages": max_packages, "publications": max_publications, "resourcesPerPackage": max_resources}, "capabilities": {"immutableSealedPackages": True, "portableLogicalBundles": True, "citationCff": True, "publicationRendering": True, "manifestVerification": True, "workspaceGovernance": True, "scientificSignoffGate": True, "embeddedRestrictedData": False, "arbitraryCode": False, "hardDelete": False}}

class ReproducibilityPublicationStudio:
    def __init__(self, db_path: str, workspaces: Any, max_packages: int = 5000, max_publications: int = 5000, max_resources: int = 1000, history_limit: int = 100000, reviews: Any | None = None):
        self.db_path = str(db_path); self.workspaces = workspaces; self.reviews = reviews; self.max_packages=max(1,int(max_packages)); self.max_publications=max(1,int(max_publications)); self.max_resources=max(1,int(max_resources)); self.history_limit=max(100,int(history_limit))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True); self._init_db()
    def _connect(self):
        con=sqlite3.connect(self.db_path,timeout=30); con.row_factory=sqlite3.Row; con.execute("PRAGMA journal_mode=WAL"); con.execute("PRAGMA foreign_keys=ON"); con.execute("PRAGMA busy_timeout=30000"); return con
    def _init_db(self):
        with self._connect() as con:
            con.executescript('''
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS reproducibility_packages(
              id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,title TEXT NOT NULL,description TEXT,
              status TEXT NOT NULL,version TEXT NOT NULL,license TEXT NOT NULL,resources_json TEXT NOT NULL,
              methods_json TEXT NOT NULL,environment_json TEXT NOT NULL,citations_json TEXT NOT NULL,
              provenance_json TEXT NOT NULL,manifest_json TEXT NOT NULL,package_hash TEXT,
              created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,sealed_at TEXT,withdrawn_at TEXT
            );
            CREATE TABLE IF NOT EXISTS package_verifications(
              id TEXT PRIMARY KEY,package_id TEXT NOT NULL,workspace_id TEXT NOT NULL,ok INTEGER NOT NULL,
              checks_json TEXT NOT NULL,receipt_hash TEXT NOT NULL,verified_by TEXT NOT NULL,verified_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS publications(
              id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,package_id TEXT NOT NULL,title TEXT NOT NULL,subtitle TEXT,
              abstract TEXT NOT NULL,authors_json TEXT NOT NULL,sections_json TEXT NOT NULL,figures_json TEXT NOT NULL,
              tables_json TEXT NOT NULL,citations_json TEXT NOT NULL,license TEXT NOT NULL,status TEXT NOT NULL,
              visibility TEXT NOT NULL,signoff_json TEXT NOT NULL,outputs_json TEXT NOT NULL,publication_hash TEXT NOT NULL,
              canonical_uri TEXT,created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
              ready_at TEXT,published_at TEXT,withdrawn_at TEXT
            );
            CREATE TABLE IF NOT EXISTS publication_events(
              sequence INTEGER PRIMARY KEY AUTOINCREMENT,workspace_id TEXT NOT NULL,entity_type TEXT NOT NULL,
              entity_id TEXT NOT NULL,event_type TEXT NOT NULL,actor_id TEXT NOT NULL,details_json TEXT NOT NULL,
              event_hash TEXT NOT NULL,created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_repro_packages_workspace ON reproducibility_packages(workspace_id,status,updated_at);
            CREATE INDEX IF NOT EXISTS idx_publications_workspace ON publications(workspace_id,status,updated_at);
            CREATE INDEX IF NOT EXISTS idx_verifications_package ON package_verifications(package_id,verified_at);
            CREATE INDEX IF NOT EXISTS idx_publication_events_workspace ON publication_events(workspace_id,sequence);
            ''')
            con.execute("INSERT INTO meta(key,value) VALUES('schema_version','1') ON CONFLICT(key) DO UPDATE SET value='1'")
    def _workspace(self, workspace_id: str, actor_id: str, minimum: str = "viewer", allow_archived: bool = True):
        try: workspace=self.workspaces.get(workspace_id,actor_id,False,False)["workspace"]
        except Exception as exc: raise PublicationStudioError(str(getattr(exc,"detail",exc)),getattr(exc,"status_code",403)) from exc
        if not allow_archived and workspace.get("status")=="archived": raise PublicationStudioError("The workspace is archived and read-only.",409)
        role=((workspace.get("currentMembership") or {}).get("role") or "viewer")
        if ROLE_RANK.get(role,0)<ROLE_RANK[minimum]: raise PublicationStudioError(f"The {minimum} role or higher is required.",403)
        return workspace
    def _event(self, con, workspace_id, entity_type, entity_id, event_type, actor_id, details):
        created=_now(); payload={"schema":EVENT_SCHEMA,"version":VERSION,"workspaceId":workspace_id,"entityType":entity_type,"entityId":entity_id,"eventType":event_type,"actorId":actor_id,"details":details,"createdAt":created}; event_hash=_hash(payload)
        cur=con.execute("INSERT INTO publication_events(workspace_id,entity_type,entity_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",(workspace_id,entity_type,entity_id,event_type,actor_id,_stable(details),event_hash,created)); payload.update({"sequence":cur.lastrowid,"eventHash":event_hash}); return payload
    @staticmethod
    def _resource(item):
        if not isinstance(item,dict): raise PublicationStudioError("Each package resource must be an object.")
        item=_safe(item); rtype=_text(item.get("type"),40) or "other"
        if rtype not in RESOURCE_TYPES: raise PublicationStudioError("Unsupported package resource type.")
        rid=_id(item.get("id"),"resource ID"); digest=_sha(item.get("sha256"),"resource SHA-256")
        return {"id":rid,"type":rtype,"title":_text(item.get("title"),300) or rid,"version":_text(item.get("version"),100),"sha256":digest,"mediaType":_text(item.get("mediaType"),200) or "application/json","uri":_text(item.get("uri"),1000),"role":_text(item.get("role"),100) or "supporting","metadata":_json_obj(item.get("metadata"),262144)}
    def _package_record(self,row):
        return {"schema":PACKAGE_SCHEMA,"version":VERSION,"id":row["id"],"workspaceId":row["workspace_id"],"title":row["title"],"description":row["description"],"status":row["status"],"packageVersion":row["version"],"license":row["license"],"resources":json.loads(row["resources_json"]),"methods":json.loads(row["methods_json"]),"environment":json.loads(row["environment_json"]),"citations":json.loads(row["citations_json"]),"provenance":json.loads(row["provenance_json"]),"manifest":json.loads(row["manifest_json"]),"packageHash":row["package_hash"],"createdBy":row["created_by"],"createdAt":row["created_at"],"updatedAt":row["updated_at"],"sealedAt":row["sealed_at"],"withdrawnAt":row["withdrawn_at"]}
    def _publication_record(self,row):
        return {"schema":PUBLICATION_SCHEMA,"version":VERSION,"id":row["id"],"workspaceId":row["workspace_id"],"packageId":row["package_id"],"title":row["title"],"subtitle":row["subtitle"],"abstract":row["abstract"],"authors":json.loads(row["authors_json"]),"sections":json.loads(row["sections_json"]),"figures":json.loads(row["figures_json"]),"tables":json.loads(row["tables_json"]),"citations":json.loads(row["citations_json"]),"license":row["license"],"status":row["status"],"visibility":row["visibility"],"scientificSignoff":json.loads(row["signoff_json"]),"outputs":json.loads(row["outputs_json"]),"publicationHash":row["publication_hash"],"canonicalUri":row["canonical_uri"],"createdBy":row["created_by"],"createdAt":row["created_at"],"updatedAt":row["updated_at"],"readyAt":row["ready_at"],"publishedAt":row["published_at"],"withdrawnAt":row["withdrawn_at"]}
    def health(self):
        with self._connect() as con:
            integrity=con.execute("PRAGMA integrity_check").fetchone()[0]; schema=int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0]); counts={"packages":con.execute("SELECT COUNT(*) FROM reproducibility_packages").fetchone()[0],"sealedPackages":con.execute("SELECT COUNT(*) FROM reproducibility_packages WHERE status='sealed'").fetchone()[0],"publications":con.execute("SELECT COUNT(*) FROM publications").fetchone()[0],"published":con.execute("SELECT COUNT(*) FROM publications WHERE status='published'").fetchone()[0],"verifications":con.execute("SELECT COUNT(*) FROM package_verifications").fetchone()[0]}
        return {"ok":integrity=="ok","status":"ready" if integrity=="ok" else "degraded","version":VERSION,"schema":"sc-lab-publication-studio-health/0.37.0","database":{"path":self.db_path,"schemaVersion":schema,"integrity":integrity},"counts":counts,"immutableSealedPackages":True,"publicationRendering":True,"scientificSignoffGate":True,"embeddedRestrictedData":False,"arbitraryCode":False,"time":_now()}
    def create_package(self, workspace_id, payload, actor_id):
        workspace_id,actor_id=_id(workspace_id,"workspace ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id,"editor",False)
        package_id=_id(payload.get("id") or ("repro-"+secrets.token_hex(8)),"package ID"); title=_text(payload.get("title"),300) or package_id; license_id=_text(payload.get("license"),80) or "CC-BY-4.0"
        if license_id not in LICENSES: raise PublicationStudioError("Unsupported package license.")
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM reproducibility_packages").fetchone()[0]>=self.max_packages: raise PublicationStudioError("Reproducibility package capacity has been reached.",409)
            if con.execute("SELECT 1 FROM reproducibility_packages WHERE id=?",(package_id,)).fetchone(): raise PublicationStudioError("Package ID already exists.",409)
            now=_now(); con.execute("INSERT INTO reproducibility_packages VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(package_id,workspace_id,title,_text(payload.get("description"),4000),"draft",_text(payload.get("packageVersion"),80) or "1.0.0",license_id,"[]","{}","{}","[]","{}","{}",None,actor_id,now,now,None,None)); self._event(con,workspace_id,"package",package_id,"package-created",actor_id,{"title":title})
            row=con.execute("SELECT * FROM reproducibility_packages WHERE id=?",(package_id,)).fetchone(); return {"ok":True,"package":self._package_record(row)}
    def list_packages(self, workspace_id, actor_id, status="", limit=100):
        workspace_id,actor_id=_id(workspace_id,"workspace ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id)
        args=[workspace_id]; where="workspace_id=?"
        if status:
            if status not in PACKAGE_STATUSES: raise PublicationStudioError("Unsupported package status.")
            where+=" AND status=?"; args.append(status)
        args.append(max(1,min(1000,int(limit))))
        with self._connect() as con: rows=con.execute(f"SELECT * FROM reproducibility_packages WHERE {where} ORDER BY updated_at DESC LIMIT ?",args).fetchall(); return {"ok":True,"version":VERSION,"packages":[self._package_record(r) for r in rows]}
    def get_package(self, workspace_id, package_id, actor_id):
        workspace_id,package_id,actor_id=_id(workspace_id,"workspace ID"),_id(package_id,"package ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id)
        with self._connect() as con:
            row=con.execute("SELECT * FROM reproducibility_packages WHERE id=? AND workspace_id=?",(package_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Reproducibility package not found.",404)
            return {"ok":True,"package":self._package_record(row)}
    def update_package(self, workspace_id, package_id, payload, actor_id):
        workspace_id,package_id,actor_id=_id(workspace_id,"workspace ID"),_id(package_id,"package ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id,"editor",False)
        with self._connect() as con:
            row=con.execute("SELECT * FROM reproducibility_packages WHERE id=? AND workspace_id=?",(package_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Reproducibility package not found.",404)
            if row["status"]!="draft": raise PublicationStudioError("Sealed packages are immutable; create a new package version.",409)
            resources=[self._resource(x) for x in payload.get("resources",json.loads(row["resources_json"]))]
            if len(resources)>self.max_resources: raise PublicationStudioError("The package exceeds the resource limit.",413)
            methods=_json_obj(payload.get("methods",json.loads(row["methods_json"])),524288); environment=_json_obj(payload.get("environment",json.loads(row["environment_json"])),524288); provenance=_json_obj(payload.get("provenance",json.loads(row["provenance_json"])),524288)
            citations=_safe(payload.get("citations",json.loads(row["citations_json"])))
            if not isinstance(citations,list): raise PublicationStudioError("citations must be a JSON array.")
            title=_text(payload.get("title"),300) or row["title"]; description=_text(payload.get("description"),4000) if "description" in payload else row["description"]; version=_text(payload.get("packageVersion"),80) or row["version"]; license_id=_text(payload.get("license"),80) or row["license"]
            if license_id not in LICENSES: raise PublicationStudioError("Unsupported package license.")
            now=_now(); con.execute("UPDATE reproducibility_packages SET title=?,description=?,version=?,license=?,resources_json=?,methods_json=?,environment_json=?,citations_json=?,provenance_json=?,updated_at=? WHERE id=?",(title,description,version,license_id,_stable(resources),_stable(methods),_stable(environment),_stable(citations),_stable(provenance),now,package_id)); self._event(con,workspace_id,"package",package_id,"package-updated",actor_id,{"resourceCount":len(resources)})
            return {"ok":True,"package":self._package_record(con.execute("SELECT * FROM reproducibility_packages WHERE id=?",(package_id,)).fetchone())}
    def _manifest(self,row):
        resources=json.loads(row["resources_json"]); methods=json.loads(row["methods_json"]); environment=json.loads(row["environment_json"]); citations=json.loads(row["citations_json"]); provenance=json.loads(row["provenance_json"])
        core={"schema":PACKAGE_SCHEMA,"version":VERSION,"id":row["id"],"workspaceId":row["workspace_id"],"title":row["title"],"description":row["description"],"packageVersion":row["version"],"license":row["license"],"resources":resources,"methods":methods,"environment":environment,"citations":citations,"provenance":provenance,"createdBy":row["created_by"],"createdAt":row["created_at"]}
        core["componentHashes"]={"resourcesSha256":_hash(resources),"methodsSha256":_hash(methods),"environmentSha256":_hash(environment),"citationsSha256":_hash(citations),"provenanceSha256":_hash(provenance)}; core["packageHash"]=_hash(core); return core
    def seal_package(self, workspace_id, package_id, actor_id):
        workspace_id,package_id,actor_id=_id(workspace_id,"workspace ID"),_id(package_id,"package ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id,"editor",False)
        with self._connect() as con:
            row=con.execute("SELECT * FROM reproducibility_packages WHERE id=? AND workspace_id=?",(package_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Reproducibility package not found.",404)
            if row["status"]=="sealed": return {"ok":True,"package":self._package_record(row)}
            if row["status"]!="draft": raise PublicationStudioError("Only draft packages can be sealed.",409)
            if not json.loads(row["resources_json"]): raise PublicationStudioError("At least one hashed resource is required before sealing.",409)
            if not json.loads(row["methods_json"]): raise PublicationStudioError("A methods record is required before sealing.",409)
            if not json.loads(row["environment_json"]): raise PublicationStudioError("An environment record is required before sealing.",409)
            if not json.loads(row["provenance_json"]): raise PublicationStudioError("A provenance record is required before sealing.",409)
            manifest=self._manifest(row); now=_now(); con.execute("UPDATE reproducibility_packages SET status='sealed',manifest_json=?,package_hash=?,sealed_at=?,updated_at=? WHERE id=?",(_stable(manifest),manifest["packageHash"],now,now,package_id)); self._event(con,workspace_id,"package",package_id,"package-sealed",actor_id,{"packageHash":manifest["packageHash"],"resourceCount":len(manifest["resources"])})
            return {"ok":True,"package":self._package_record(con.execute("SELECT * FROM reproducibility_packages WHERE id=?",(package_id,)).fetchone())}
    def verify_package(self, workspace_id, package_id, actor_id):
        workspace_id,package_id,actor_id=_id(workspace_id,"workspace ID"),_id(package_id,"package ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id,"viewer")
        with self._connect() as con:
            row=con.execute("SELECT * FROM reproducibility_packages WHERE id=? AND workspace_id=?",(package_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Reproducibility package not found.",404)
            expected=json.loads(row["manifest_json"]); actual=self._manifest(row) if row["status"] in {"sealed","published"} else {}
            checks={"sealed":{"ok":row["status"] in {"sealed","published"}},"packageHash":{"expected":row["package_hash"],"actual":actual.get("packageHash"),"ok":bool(actual) and row["package_hash"]==actual.get("packageHash")},"manifestHash":{"expected":_hash(expected) if expected else None,"actual":_hash(actual) if actual else None,"ok":bool(expected) and expected==actual},"resourceHashes":{"ok":all(SHA_RE.match(str(x.get("sha256") or "")) for x in actual.get("resources",[]))}}
            ok=all(x["ok"] for x in checks.values()); verified=_now(); receipt_core={"schema":VERIFICATION_SCHEMA,"version":VERSION,"packageId":package_id,"workspaceId":workspace_id,"ok":ok,"checks":checks,"verifiedBy":actor_id,"verifiedAt":verified}; receipt_hash=_hash(receipt_core); receipt={**receipt_core,"receiptHash":receipt_hash}; rid="verify-"+secrets.token_hex(8)
            con.execute("INSERT INTO package_verifications VALUES(?,?,?,?,?,?,?,?)",(rid,package_id,workspace_id,1 if ok else 0,_stable(checks),receipt_hash,actor_id,verified)); self._event(con,workspace_id,"package",package_id,"package-verified",actor_id,{"ok":ok,"receiptHash":receipt_hash}); return {"ok":ok,"verification":receipt}
    def create_publication(self, workspace_id, payload, actor_id):
        workspace_id,actor_id=_id(workspace_id,"workspace ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id,"editor",False); package_id=_id(payload.get("packageId"),"package ID")
        with self._connect() as con:
            package=con.execute("SELECT * FROM reproducibility_packages WHERE id=? AND workspace_id=?",(package_id,workspace_id)).fetchone()
            if not package or package["status"] not in {"sealed","published"}: raise PublicationStudioError("A sealed reproducibility package is required.",409)
            if con.execute("SELECT COUNT(*) FROM publications").fetchone()[0]>=self.max_publications: raise PublicationStudioError("Publication capacity has been reached.",409)
            pub_id=_id(payload.get("id") or ("publication-"+secrets.token_hex(8)),"publication ID"); authors=_safe(payload.get("authors") or []); sections=_safe(payload.get("sections") or []); figures=_safe(payload.get("figures") or []); tables=_safe(payload.get("tables") or []); citations=_safe(payload.get("citations") or json.loads(package["citations_json"]))
            if not all(isinstance(v,list) for v in (authors,sections,figures,tables,citations)): raise PublicationStudioError("Authors, sections, figures, tables, and citations must be arrays.")
            license_id=_text(payload.get("license"),80) or package["license"]; visibility=_text(payload.get("visibility"),30) or "workspace"
            if license_id not in LICENSES: raise PublicationStudioError("Unsupported publication license.")
            if visibility not in {"private","workspace","public"}: raise PublicationStudioError("Unsupported publication visibility.")
            now=_now(); title=_text(payload.get("title"),300) or package["title"]; abstract=_text(payload.get("abstract"),10000); core={"id":pub_id,"workspaceId":workspace_id,"packageId":package_id,"title":title,"subtitle":_text(payload.get("subtitle"),300),"abstract":abstract,"authors":authors,"sections":sections,"figures":figures,"tables":tables,"citations":citations,"license":license_id,"visibility":visibility,"createdBy":actor_id,"createdAt":now}; publication_hash=_hash(core)
            con.execute("INSERT INTO publications VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(pub_id,workspace_id,package_id,title,core["subtitle"],abstract,_stable(authors),_stable(sections),_stable(figures),_stable(tables),_stable(citations),license_id,"draft",visibility,"{}","{}",publication_hash,None,actor_id,now,now,None,None,None)); self._event(con,workspace_id,"publication",pub_id,"publication-created",actor_id,{"packageId":package_id,"publicationHash":publication_hash}); return {"ok":True,"publication":self._publication_record(con.execute("SELECT * FROM publications WHERE id=?",(pub_id,)).fetchone())}
    def get_publication(self, workspace_id, publication_id, actor_id):
        workspace_id,publication_id,actor_id=_id(workspace_id,"workspace ID"),_id(publication_id,"publication ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id)
        with self._connect() as con:
            row=con.execute("SELECT * FROM publications WHERE id=? AND workspace_id=?",(publication_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Publication not found.",404)
            return {"ok":True,"publication":self._publication_record(row)}

    def list_publications(self, workspace_id, actor_id, status="", limit=100):
        workspace_id,actor_id=_id(workspace_id,"workspace ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id); args=[workspace_id]; where="workspace_id=?"
        if status:
            if status not in PUBLICATION_STATUSES: raise PublicationStudioError("Unsupported publication status.")
            where+=" AND status=?"; args.append(status)
        args.append(max(1,min(1000,int(limit))))
        with self._connect() as con: return {"ok":True,"version":VERSION,"publications":[self._publication_record(r) for r in con.execute(f"SELECT * FROM publications WHERE {where} ORDER BY updated_at DESC LIMIT ?",args).fetchall()]}
    def update_publication(self, workspace_id, publication_id, payload, actor_id):
        workspace_id,publication_id,actor_id=_id(workspace_id,"workspace ID"),_id(publication_id,"publication ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id,"editor",False)
        with self._connect() as con:
            row=con.execute("SELECT * FROM publications WHERE id=? AND workspace_id=?",(publication_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Publication not found.",404)
            if row["status"]!="draft": raise PublicationStudioError("Only draft publications can be edited.",409)
            values={"title":_text(payload.get("title"),300) or row["title"],"subtitle":_text(payload.get("subtitle"),300) if "subtitle" in payload else row["subtitle"],"abstract":_text(payload.get("abstract"),10000) if "abstract" in payload else row["abstract"],"authors":_safe(payload.get("authors",json.loads(row["authors_json"]))),"sections":_safe(payload.get("sections",json.loads(row["sections_json"]))),"figures":_safe(payload.get("figures",json.loads(row["figures_json"]))),"tables":_safe(payload.get("tables",json.loads(row["tables_json"]))),"citations":_safe(payload.get("citations",json.loads(row["citations_json"]))),"license":_text(payload.get("license"),80) or row["license"],"visibility":_text(payload.get("visibility"),30) or row["visibility"]}
            if values["license"] not in LICENSES or values["visibility"] not in {"private","workspace","public"}: raise PublicationStudioError("Unsupported publication policy.")
            core={"id":publication_id,"workspaceId":workspace_id,"packageId":row["package_id"],**values,"createdBy":row["created_by"],"createdAt":row["created_at"]}; publication_hash=_hash(core); now=_now()
            con.execute("UPDATE publications SET title=?,subtitle=?,abstract=?,authors_json=?,sections_json=?,figures_json=?,tables_json=?,citations_json=?,license=?,visibility=?,publication_hash=?,updated_at=? WHERE id=?",(values["title"],values["subtitle"],values["abstract"],_stable(values["authors"]),_stable(values["sections"]),_stable(values["figures"]),_stable(values["tables"]),_stable(values["citations"]),values["license"],values["visibility"],publication_hash,now,publication_id)); self._event(con,workspace_id,"publication",publication_id,"publication-updated",actor_id,{"publicationHash":publication_hash}); return {"ok":True,"publication":self._publication_record(con.execute("SELECT * FROM publications WHERE id=?",(publication_id,)).fetchone())}
    def _render(self,row,package):
        authors=json.loads(row["authors_json"]); sections=json.loads(row["sections_json"]); citations=json.loads(row["citations_json"])
        author_names=[_text(a.get("name") if isinstance(a,dict) else a,300) for a in authors]
        lines=[f"# {row['title']}"]
        if row["subtitle"]: lines += ["",f"## {row['subtitle']}"]
        if author_names: lines += ["", "**Authors:** "+", ".join(author_names)]
        lines += ["", "## Abstract", "", row["abstract"]]
        for section in sections:
            if not isinstance(section,dict): continue
            lines += ["", "## "+(_text(section.get("title"),300) or "Section"), "", _text(section.get("body"),50000)]
        lines += ["", "## Reproducibility", "", f"Package `{package['id']}` · SHA-256 `{package['package_hash']}`", "", "## References", ""]
        for index,citation in enumerate(citations,1): lines.append(f"{index}. "+_text(citation.get("formatted") if isinstance(citation,dict) else citation,5000))
        markdown="\n".join(lines).strip()+"\n"
        html_body="<article><h1>"+html.escape(row["title"])+"</h1>"
        if row["subtitle"]: html_body+="<h2>"+html.escape(row["subtitle"])+"</h2>"
        if author_names: html_body+="<p><strong>Authors:</strong> "+html.escape(", ".join(author_names))+"</p>"
        html_body+="<h2>Abstract</h2><p>"+html.escape(row["abstract"])+"</p>"
        for section in sections:
            if isinstance(section,dict): html_body+="<h2>"+html.escape(_text(section.get("title"),300) or "Section")+"</h2><p>"+html.escape(_text(section.get("body"),50000)).replace("\n","<br>")+"</p>"
        html_body+="<h2>Reproducibility</h2><p>Package <code>"+html.escape(package["id"])+"</code> · SHA-256 <code>"+html.escape(package["package_hash"] or "")+"</code></p><h2>References</h2><ol>"
        for citation in citations: html_body+="<li>"+html.escape(_text(citation.get("formatted") if isinstance(citation,dict) else citation,5000))+"</li>"
        html_body+="</ol></article>"
        cff={"cff-version":"1.2.0","message":"If you use this research package, please cite it using this metadata.","title":row["title"],"type":"article","authors":[{"family-names":_text(a.get("familyName"),200),"given-names":_text(a.get("givenName"),200),"orcid":_text(a.get("orcid"),200)} if isinstance(a,dict) else {"name":_text(a,300)} for a in authors],"version":package["version"],"license":row["license"],"identifiers":[{"type":"other","value":package["package_hash"],"description":"Sustainable Catalyst Lab reproducibility package SHA-256"}]}
        files={"README.md":markdown,"publication.md":markdown,"publication.html":html_body,"publication.json":_stable(self._publication_record(row)),"CITATION.cff":_stable(cff),"manifest.json":package["manifest_json"],"methods.json":package["methods_json"],"environment.json":package["environment_json"],"provenance.json":package["provenance_json"]}
        hashes={name:sha256(content.encode()).hexdigest() for name,content in files.items()}; export={"schema":EXPORT_SCHEMA,"version":VERSION,"publicationId":row["id"],"packageId":package["id"],"files":files,"fileHashes":hashes,"exportHash":_hash(hashes),"createdAt":_now()}; return export
    def render_publication(self, workspace_id, publication_id, actor_id):
        workspace_id,publication_id,actor_id=_id(workspace_id,"workspace ID"),_id(publication_id,"publication ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id)
        with self._connect() as con:
            row=con.execute("SELECT * FROM publications WHERE id=? AND workspace_id=?",(publication_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Publication not found.",404)
            package=con.execute("SELECT * FROM reproducibility_packages WHERE id=?",(row["package_id"],)).fetchone(); export=self._render(row,package); con.execute("UPDATE publications SET outputs_json=?,updated_at=? WHERE id=?",(_stable({"exportHash":export["exportHash"],"fileHashes":export["fileHashes"]}),_now(),publication_id)); self._event(con,workspace_id,"publication",publication_id,"publication-rendered",actor_id,{"exportHash":export["exportHash"],"formats":sorted(export["files"])})
            return {"ok":True,"export":export}
    def mark_ready(self, workspace_id, publication_id, actor_id):
        workspace_id,publication_id,actor_id=_id(workspace_id,"workspace ID"),_id(publication_id,"publication ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id,"reviewer",False)
        with self._connect() as con:
            row=con.execute("SELECT * FROM publications WHERE id=? AND workspace_id=?",(publication_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Publication not found.",404)
            if row["status"]!="draft": raise PublicationStudioError("Only draft publications can be marked ready.",409)
            if not row["abstract"] or not json.loads(row["authors_json"]) or not json.loads(row["sections_json"]): raise PublicationStudioError("Abstract, authors, and at least one section are required.",409)
            latest=con.execute("SELECT ok FROM package_verifications WHERE package_id=? ORDER BY verified_at DESC LIMIT 1",(row["package_id"],)).fetchone()
            if not latest or not latest["ok"]: raise PublicationStudioError("A successful package verification is required.",409)
            now=_now(); con.execute("UPDATE publications SET status='ready',ready_at=?,updated_at=? WHERE id=?",(now,now,publication_id)); self._event(con,workspace_id,"publication",publication_id,"publication-ready",actor_id,{"packageId":row["package_id"]}); return {"ok":True,"publication":self._publication_record(con.execute("SELECT * FROM publications WHERE id=?",(publication_id,)).fetchone())}
    def publish(self, workspace_id, publication_id, payload, actor_id):
        workspace_id,publication_id,actor_id=_id(workspace_id,"workspace ID"),_id(publication_id,"publication ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id,"administrator",False); signoff=_json_obj(payload.get("scientificSignoff"),262144)
        if not _text(signoff.get("id"),180) or not SHA_RE.match(_text(signoff.get("signoffHash"),64).lower()): raise PublicationStudioError("A scientific sign-off ID and SHA-256 signoffHash are required.",409)
        approval_id = _text(payload.get("approvalId") or signoff.get("approvalId"), 180)
        if self.reviews is not None:
            if not approval_id: raise PublicationStudioError("A signed scientific approval request is required.",409)
            try: approval = self.reviews.get_approval(workspace_id, approval_id, actor_id)["approval"]
            except Exception as exc: raise PublicationStudioError(str(getattr(exc,"detail",exc)),getattr(exc,"status_code",403)) from exc
            recorded = approval.get("signoff") or {}
            if approval.get("status") != "signed" or recorded.get("id") != signoff.get("id") or recorded.get("signoffHash") != signoff.get("signoffHash"):
                raise PublicationStudioError("The supplied scientific sign-off does not match the signed workspace approval.",409)
        with self._connect() as con:
            row=con.execute("SELECT * FROM publications WHERE id=? AND workspace_id=?",(publication_id,workspace_id)).fetchone()
            if not row: raise PublicationStudioError("Publication not found.",404)
            if row["status"]=="published": return {"ok":True,"publication":self._publication_record(row)}
            if row["status"]!="ready": raise PublicationStudioError("The publication must be ready before publishing.",409)
            package=con.execute("SELECT * FROM reproducibility_packages WHERE id=?",(row["package_id"],)).fetchone(); export=self._render(row,package); canonical=_text(payload.get("canonicalUri"),1000) or f"urn:sc-lab:publication:{publication_id}:{row['publication_hash']}"; now=_now()
            con.execute("UPDATE publications SET status='published',signoff_json=?,outputs_json=?,canonical_uri=?,published_at=?,updated_at=? WHERE id=?",(_stable(signoff),_stable({"exportHash":export["exportHash"],"fileHashes":export["fileHashes"]}),canonical,now,now,publication_id)); con.execute("UPDATE reproducibility_packages SET status='published',updated_at=? WHERE id=?",(now,row["package_id"])); self._event(con,workspace_id,"publication",publication_id,"publication-published",actor_id,{"canonicalUri":canonical,"approvalId":approval_id or None,"signoffId":signoff["id"],"signoffHash":signoff["signoffHash"],"exportHash":export["exportHash"]}); return {"ok":True,"publication":self._publication_record(con.execute("SELECT * FROM publications WHERE id=?",(publication_id,)).fetchone()),"export":export}
    def timeline(self, workspace_id, actor_id, limit=500):
        workspace_id,actor_id=_id(workspace_id,"workspace ID"),_id(actor_id,"actor ID"); self._workspace(workspace_id,actor_id); limit=max(1,min(self.history_limit,int(limit)))
        with self._connect() as con:
            rows=con.execute("SELECT * FROM publication_events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?",(workspace_id,limit)).fetchall(); events=[]
            for row in rows: events.append({"schema":EVENT_SCHEMA,"version":VERSION,"sequence":row["sequence"],"workspaceId":row["workspace_id"],"entityType":row["entity_type"],"entityId":row["entity_id"],"eventType":row["event_type"],"actorId":row["actor_id"],"details":json.loads(row["details_json"]),"eventHash":row["event_hash"],"createdAt":row["created_at"]})
            return {"ok":True,"version":VERSION,"events":events}
