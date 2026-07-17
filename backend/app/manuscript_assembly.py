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

VERSION = "0.37.1"
ASSEMBLY_SCHEMA = "sc-lab-research-assembly/0.37.1"
SECTION_SCHEMA = "sc-lab-assembly-section/0.37.1"
EXPORT_SCHEMA = "sc-lab-assembly-export/0.37.1"
EVENT_SCHEMA = "sc-lab-assembly-event/0.37.1"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
ROLE_RANK = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
DOCUMENT_TYPES = {"manuscript", "report", "notebook", "methods-supplement", "research-dossier"}
TEMPLATES = {"imrad", "technical-report", "methods-supplement", "reproducibility-dossier", "notebook-narrative", "custom"}
SECTION_KINDS = {"title", "abstract", "introduction", "background", "methods", "results", "discussion", "conclusion", "references", "appendix", "figure", "table", "notebook-markdown", "notebook-output", "custom"}
STATUSES = {"draft", "sealed", "withdrawn"}
FORBIDDEN_KEYS = {"code", "sourcecode", "shell", "command", "callback", "callbackurl", "executable", "script", "token", "secret", "password", "privatekey", "bytes", "binary", "rawdata", "datasetbytes"}


class ManuscriptAssemblyError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, label: str = "identifier") -> str:
    clean = _text(value, 180)
    if not ID_RE.match(clean):
        raise ManuscriptAssemblyError(f"A valid {label} is required.")
    return clean


def _safe(value: Any, depth: int = 0) -> Any:
    if depth > 12:
        raise ManuscriptAssemblyError("Nested assembly data exceeds the depth limit.", 413)
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            skey = _text(key, 120)
            normalized = skey.lower().replace("_", "").replace("-", "")
            if normalized in FORBIDDEN_KEYS:
                raise ManuscriptAssemblyError(f"Executable, secret, or embedded byte field '{skey}' is not permitted.", 422)
            out[skey] = _safe(item, depth + 1)
        return out
    if isinstance(value, list):
        return [_safe(item, depth + 1) for item in value[:10000]]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _text(value, 100000)


def _obj(value: Any, max_bytes: int = 8 * 1024 * 1024) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ManuscriptAssemblyError("A JSON object is required.")
    clean = _safe(copy.deepcopy(value))
    if len(_stable(clean).encode("utf-8")) > max_bytes:
        raise ManuscriptAssemblyError("Assembly payload exceeds the configured limit.", 413)
    return clean


def policies(max_assemblies: int = 5000, max_sections: int = 20000, max_sections_per_assembly: int = 500) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-manuscript-assembly-policy/0.37.1",
        "schemas": {"assembly": ASSEMBLY_SCHEMA, "section": SECTION_SCHEMA, "export": EXPORT_SCHEMA, "event": EVENT_SCHEMA},
        "documentTypes": sorted(DOCUMENT_TYPES),
        "templates": sorted(TEMPLATES),
        "sectionKinds": sorted(SECTION_KINDS),
        "formats": ["markdown", "html", "jats-lite", "jupyter-notebook", "json", "bibtex", "methods-markdown"],
        "limits": {"assemblies": max_assemblies, "sectionLibrary": max_sections, "sectionsPerAssembly": max_sections_per_assembly},
        "capabilities": {
            "reusableSections": True,
            "structuredMethodsNarrative": True,
            "outputOnlyNotebooks": True,
            "crossFormatRendering": True,
            "immutableSealedAssemblies": True,
            "revisionLineage": True,
            "arbitraryCode": False,
            "embeddedRestrictedData": False,
            "hardDelete": False,
        },
    }


class ManuscriptAssemblyStudio:
    def __init__(
        self,
        db_path: str,
        workspaces: Any,
        publication_studio: Any,
        max_assemblies: int = 5000,
        max_sections: int = 20000,
        max_sections_per_assembly: int = 500,
        history_limit: int = 100000,
    ):
        self.db_path = str(db_path)
        self.workspaces = workspaces
        self.publication_studio = publication_studio
        self.max_assemblies = max(1, int(max_assemblies))
        self.max_sections = max(1, int(max_sections))
        self.max_sections_per_assembly = max(1, int(max_sections_per_assembly))
        self.history_limit = max(100, int(history_limit))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        con = sqlite3.connect(self.db_path, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _init_db(self):
        with self._connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS assembly_sections(
                  id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,title TEXT NOT NULL,kind TEXT NOT NULL,
                  content_json TEXT NOT NULL,revision INTEGER NOT NULL,content_hash TEXT NOT NULL,
                  created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_by TEXT NOT NULL,updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS research_assemblies(
                  id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,package_id TEXT,publication_id TEXT,
                  title TEXT NOT NULL,document_type TEXT NOT NULL,template_id TEXT NOT NULL,status TEXT NOT NULL,
                  citation_style TEXT NOT NULL,metadata_json TEXT NOT NULL,sections_json TEXT NOT NULL,
                  parent_assembly_id TEXT,parent_assembly_hash TEXT,assembly_hash TEXT,render_json TEXT NOT NULL,
                  created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_by TEXT NOT NULL,updated_at TEXT NOT NULL,sealed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS assembly_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT,workspace_id TEXT NOT NULL,entity_type TEXT NOT NULL,
                  entity_id TEXT NOT NULL,event_type TEXT NOT NULL,actor_id TEXT NOT NULL,details_json TEXT NOT NULL,
                  event_hash TEXT NOT NULL,created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_assembly_sections_workspace ON assembly_sections(workspace_id,kind,updated_at);
                CREATE INDEX IF NOT EXISTS idx_research_assemblies_workspace ON research_assemblies(workspace_id,status,updated_at);
                CREATE INDEX IF NOT EXISTS idx_assembly_events_workspace ON assembly_events(workspace_id,sequence);
                """
            )
            con.execute("INSERT INTO meta(key,value) VALUES('schema_version','1') ON CONFLICT(key) DO UPDATE SET value='1'")

    def _workspace(self, workspace_id: str, actor_id: str, minimum: str = "viewer", allow_archived: bool = True):
        try:
            workspace = self.workspaces.get(workspace_id, actor_id, False, False)["workspace"]
        except Exception as exc:
            raise ManuscriptAssemblyError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 403)) from exc
        if not allow_archived and workspace.get("status") == "archived":
            raise ManuscriptAssemblyError("The workspace is archived and read-only.", 409)
        role = ((workspace.get("currentMembership") or {}).get("role") or "viewer")
        if ROLE_RANK.get(role, 0) < ROLE_RANK[minimum]:
            raise ManuscriptAssemblyError(f"The {minimum} role or higher is required.", 403)
        return workspace

    def _event(self, con, workspace_id: str, entity_type: str, entity_id: str, event_type: str, actor_id: str, details: dict[str, Any]):
        created = _now()
        payload = {"schema": EVENT_SCHEMA, "version": VERSION, "workspaceId": workspace_id, "entityType": entity_type, "entityId": entity_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created}
        event_hash = _hash(payload)
        cur = con.execute(
            "INSERT INTO assembly_events(workspace_id,entity_type,entity_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (workspace_id, entity_type, entity_id, event_type, actor_id, _stable(details), event_hash, created),
        )
        payload.update({"sequence": cur.lastrowid, "eventHash": event_hash})
        return payload

    @staticmethod
    def _section_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": SECTION_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "title": row["title"], "kind": row["kind"], "content": json.loads(row["content_json"]), "revision": row["revision"], "contentHash": row["content_hash"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedBy": row["updated_by"], "updatedAt": row["updated_at"]}

    @staticmethod
    def _assembly_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": ASSEMBLY_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "packageId": row["package_id"], "publicationId": row["publication_id"], "title": row["title"], "documentType": row["document_type"], "template": row["template_id"], "status": row["status"], "citationStyle": row["citation_style"], "metadata": json.loads(row["metadata_json"]), "sections": json.loads(row["sections_json"]), "parentAssemblyId": row["parent_assembly_id"], "parentAssemblyHash": row["parent_assembly_hash"], "assemblyHash": row["assembly_hash"], "render": json.loads(row["render_json"]), "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedBy": row["updated_by"], "updatedAt": row["updated_at"], "sealedAt": row["sealed_at"]}

    def create_section(self, workspace_id: str, payload: dict[str, Any], actor_id: str):
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "contributor", False)
        payload = _obj(payload)
        kind = _text(payload.get("kind"), 40) or "custom"
        if kind not in SECTION_KINDS:
            raise ManuscriptAssemblyError("Unsupported section kind.")
        content = _obj(payload.get("content") or {"body": _text(payload.get("body"), 100000)})
        sid = _id(payload.get("id") or ("section-" + secrets.token_hex(8)), "section ID")
        now = _now()
        content_hash = _hash({"kind": kind, "content": content})
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM assembly_sections").fetchone()[0] >= self.max_sections:
                raise ManuscriptAssemblyError("Section-library capacity has been reached.", 409)
            try:
                con.execute("INSERT INTO assembly_sections VALUES(?,?,?,?,?,?,?,?,?,?,?)", (sid, workspace_id, _text(payload.get("title"), 300) or sid, kind, _stable(content), 1, content_hash, actor_id, now, actor_id, now))
            except sqlite3.IntegrityError as exc:
                raise ManuscriptAssemblyError("A section with this ID already exists.", 409) from exc
            self._event(con, workspace_id, "section", sid, "section-created", actor_id, {"kind": kind, "contentHash": content_hash})
            row = con.execute("SELECT * FROM assembly_sections WHERE id=?", (sid,)).fetchone()
            return {"ok": True, "section": self._section_record(row)}

    def update_section(self, workspace_id: str, section_id: str, payload: dict[str, Any], actor_id: str):
        workspace_id, section_id, actor_id = _id(workspace_id, "workspace ID"), _id(section_id, "section ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        payload = _obj(payload)
        with self._connect() as con:
            row = con.execute("SELECT * FROM assembly_sections WHERE id=? AND workspace_id=?", (section_id, workspace_id)).fetchone()
            if not row:
                raise ManuscriptAssemblyError("Section not found.", 404)
            kind = _text(payload.get("kind"), 40) or row["kind"]
            if kind not in SECTION_KINDS:
                raise ManuscriptAssemblyError("Unsupported section kind.")
            content = _obj(payload["content"]) if "content" in payload else json.loads(row["content_json"])
            title = _text(payload.get("title"), 300) or row["title"]
            revision = row["revision"] + 1
            content_hash = _hash({"kind": kind, "content": content})
            now = _now()
            con.execute("UPDATE assembly_sections SET title=?,kind=?,content_json=?,revision=?,content_hash=?,updated_by=?,updated_at=? WHERE id=?", (title, kind, _stable(content), revision, content_hash, actor_id, now, section_id))
            self._event(con, workspace_id, "section", section_id, "section-revised", actor_id, {"revision": revision, "contentHash": content_hash})
            return {"ok": True, "section": self._section_record(con.execute("SELECT * FROM assembly_sections WHERE id=?", (section_id,)).fetchone())}

    def list_sections(self, workspace_id: str, actor_id: str, kind: str = "", limit: int = 200):
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id)
        args: list[Any] = [workspace_id]
        where = "workspace_id=?"
        if kind:
            if kind not in SECTION_KINDS:
                raise ManuscriptAssemblyError("Unsupported section kind.")
            where += " AND kind=?"
            args.append(kind)
        args.append(max(1, min(2000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM assembly_sections WHERE {where} ORDER BY updated_at DESC LIMIT ?", args).fetchall()
            return {"ok": True, "version": VERSION, "sections": [self._section_record(r) for r in rows]}

    def _normalize_section_ref(self, item: Any, con: sqlite3.Connection, workspace_id: str) -> dict[str, Any]:
        if not isinstance(item, dict):
            raise ManuscriptAssemblyError("Each assembly section must be an object.")
        item = _safe(item)
        ref = _text(item.get("librarySectionId"), 180)
        if ref:
            row = con.execute("SELECT * FROM assembly_sections WHERE id=? AND workspace_id=?", (ref, workspace_id)).fetchone()
            if not row:
                raise ManuscriptAssemblyError(f"Section library item '{ref}' was not found.", 404)
            source = self._section_record(row)
            content = source["content"]
            kind = source["kind"]
            title = source["title"]
            source_hash = source["contentHash"]
            source_revision = source["revision"]
        else:
            kind = _text(item.get("kind"), 40) or "custom"
            if kind not in SECTION_KINDS:
                raise ManuscriptAssemblyError("Unsupported assembly section kind.")
            title = _text(item.get("title"), 300) or kind.replace("-", " ").title()
            content = _obj(item.get("content") or {"body": _text(item.get("body"), 100000)})
            source_hash = None
            source_revision = None
        return {"id": _id(item.get("id") or ("part-" + secrets.token_hex(6)), "assembly section ID"), "kind": kind, "title": title, "content": content, "librarySectionId": ref or None, "libraryRevision": source_revision, "sourceHash": source_hash, "included": bool(item.get("included", True))}

    def create_assembly(self, workspace_id: str, payload: dict[str, Any], actor_id: str):
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "contributor", False)
        payload = _obj(payload)
        dtype = _text(payload.get("documentType"), 40) or "manuscript"
        template = _text(payload.get("template"), 60) or "imrad"
        if dtype not in DOCUMENT_TYPES or template not in TEMPLATES:
            raise ManuscriptAssemblyError("Unsupported document type or template.")
        aid = _id(payload.get("id") or ("assembly-" + secrets.token_hex(8)), "assembly ID")
        package_id = _text(payload.get("packageId"), 180) or None
        if package_id:
            try:
                self.publication_studio.get_package(workspace_id, package_id, actor_id)
            except Exception as exc:
                raise ManuscriptAssemblyError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 404)) from exc
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM research_assemblies").fetchone()[0] >= self.max_assemblies:
                raise ManuscriptAssemblyError("Assembly capacity has been reached.", 409)
            raw_sections = payload.get("sections") or []
            if not isinstance(raw_sections, list) or len(raw_sections) > self.max_sections_per_assembly:
                raise ManuscriptAssemblyError("Assembly sections exceed the configured limit.", 413)
            sections = [self._normalize_section_ref(item, con, workspace_id) for item in raw_sections]
            now = _now()
            try:
                con.execute("INSERT INTO research_assemblies VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (aid, workspace_id, package_id, _text(payload.get("publicationId"), 180) or None, _text(payload.get("title"), 300) or aid, dtype, template, "draft", _text(payload.get("citationStyle"), 60) or "Harvard", _stable(_obj(payload.get("metadata") or {})), _stable(sections), _text(payload.get("parentAssemblyId"), 180) or None, _text(payload.get("parentAssemblyHash"), 64) or None, None, "{}", actor_id, now, actor_id, now, None))
            except sqlite3.IntegrityError as exc:
                raise ManuscriptAssemblyError("An assembly with this ID already exists.", 409) from exc
            self._event(con, workspace_id, "assembly", aid, "assembly-created", actor_id, {"documentType": dtype, "template": template, "packageId": package_id})
            return {"ok": True, "assembly": self._assembly_record(con.execute("SELECT * FROM research_assemblies WHERE id=?", (aid,)).fetchone())}

    def list_assemblies(self, workspace_id: str, actor_id: str, status: str = "", limit: int = 200):
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id)
        args: list[Any] = [workspace_id]
        where = "workspace_id=?"
        if status:
            if status not in STATUSES:
                raise ManuscriptAssemblyError("Unsupported assembly status.")
            where += " AND status=?"
            args.append(status)
        args.append(max(1, min(2000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM research_assemblies WHERE {where} ORDER BY updated_at DESC LIMIT ?", args).fetchall()
            return {"ok": True, "version": VERSION, "assemblies": [self._assembly_record(r) for r in rows]}

    def get_assembly(self, workspace_id: str, assembly_id: str, actor_id: str):
        workspace_id, assembly_id, actor_id = _id(workspace_id, "workspace ID"), _id(assembly_id, "assembly ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id)
        with self._connect() as con:
            row = con.execute("SELECT * FROM research_assemblies WHERE id=? AND workspace_id=?", (assembly_id, workspace_id)).fetchone()
            if not row:
                raise ManuscriptAssemblyError("Assembly not found.", 404)
            return {"ok": True, "assembly": self._assembly_record(row)}

    def update_assembly(self, workspace_id: str, assembly_id: str, payload: dict[str, Any], actor_id: str):
        workspace_id, assembly_id, actor_id = _id(workspace_id, "workspace ID"), _id(assembly_id, "assembly ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        payload = _obj(payload)
        with self._connect() as con:
            row = con.execute("SELECT * FROM research_assemblies WHERE id=? AND workspace_id=?", (assembly_id, workspace_id)).fetchone()
            if not row:
                raise ManuscriptAssemblyError("Assembly not found.", 404)
            if row["status"] != "draft":
                raise ManuscriptAssemblyError("Only draft assemblies can be updated.", 409)
            dtype = _text(payload.get("documentType"), 40) or row["document_type"]
            template = _text(payload.get("template"), 60) or row["template_id"]
            if dtype not in DOCUMENT_TYPES or template not in TEMPLATES:
                raise ManuscriptAssemblyError("Unsupported document type or template.")
            sections = json.loads(row["sections_json"])
            if "sections" in payload:
                if not isinstance(payload["sections"], list) or len(payload["sections"]) > self.max_sections_per_assembly:
                    raise ManuscriptAssemblyError("Assembly sections exceed the configured limit.", 413)
                sections = [self._normalize_section_ref(item, con, workspace_id) for item in payload["sections"]]
            package_id = _text(payload.get("packageId"), 180) if "packageId" in payload else row["package_id"]
            if package_id:
                try:
                    self.publication_studio.get_package(workspace_id, package_id, actor_id)
                except Exception as exc:
                    raise ManuscriptAssemblyError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 404)) from exc
            now = _now()
            con.execute("UPDATE research_assemblies SET package_id=?,publication_id=?,title=?,document_type=?,template_id=?,citation_style=?,metadata_json=?,sections_json=?,updated_by=?,updated_at=?,render_json='{}' WHERE id=?", (package_id or None, _text(payload.get("publicationId"), 180) if "publicationId" in payload else row["publication_id"], _text(payload.get("title"), 300) or row["title"], dtype, template, _text(payload.get("citationStyle"), 60) or row["citation_style"], _stable(_obj(payload["metadata"]) if "metadata" in payload else json.loads(row["metadata_json"])), _stable(sections), actor_id, now, assembly_id))
            self._event(con, workspace_id, "assembly", assembly_id, "assembly-updated", actor_id, {"sectionCount": len(sections), "documentType": dtype, "template": template})
            return {"ok": True, "assembly": self._assembly_record(con.execute("SELECT * FROM research_assemblies WHERE id=?", (assembly_id,)).fetchone())}

    def generate_methods(self, workspace_id: str, assembly_id: str, actor_id: str):
        workspace_id, assembly_id, actor_id = _id(workspace_id, "workspace ID"), _id(assembly_id, "assembly ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        with self._connect() as con:
            row = con.execute("SELECT * FROM research_assemblies WHERE id=? AND workspace_id=?", (assembly_id, workspace_id)).fetchone()
            if not row:
                raise ManuscriptAssemblyError("Assembly not found.", 404)
            if row["status"] != "draft":
                raise ManuscriptAssemblyError("Only draft assemblies can receive generated methods.", 409)
            if not row["package_id"]:
                raise ManuscriptAssemblyError("A reproducibility package is required to generate methods.", 409)
            package = self.publication_studio.get_package(workspace_id, row["package_id"], actor_id)["package"]
            methods = package.get("methods") or {}
            environment = package.get("environment") or {}
            protocol = _text(methods.get("protocol") if isinstance(methods, dict) else "", 50000)
            registered = methods.get("registeredMethods") if isinstance(methods, dict) else []
            if not isinstance(registered, list):
                registered = []
            env_parts = []
            for key, value in sorted(environment.items()) if isinstance(environment, dict) else []:
                if isinstance(value, (str, int, float, bool)):
                    env_parts.append(f"{key}: {value}")
                elif isinstance(value, dict):
                    env_parts.append(f"{key}: " + ", ".join(f"{k} {v}" for k, v in sorted(value.items())))
            paragraphs = []
            if protocol:
                paragraphs.append(protocol.rstrip("." ) + ".")
            if registered:
                paragraphs.append("The analysis used the following governed Sustainable Catalyst Lab methods: " + ", ".join(_text(v, 180) for v in registered) + ".")
            if env_parts:
                paragraphs.append("The reproducibility environment was recorded as " + "; ".join(env_parts) + ".")
            paragraphs.append(f"The complete reproducibility package is `{package['id']}` with SHA-256 `{package.get('packageHash') or 'unsealed'}`.")
            section = {"id": "generated-methods", "kind": "methods", "title": "Methods", "content": {"body": "\n\n".join(paragraphs), "generatedFromPackageId": package["id"], "packageHash": package.get("packageHash"), "registeredMethods": registered, "environment": environment}, "librarySectionId": None, "libraryRevision": None, "sourceHash": _hash({"methods": methods, "environment": environment}), "included": True}
            sections = [s for s in json.loads(row["sections_json"]) if s.get("id") != "generated-methods"]
            sections.append(section)
            now = _now()
            con.execute("UPDATE research_assemblies SET sections_json=?,updated_by=?,updated_at=?,render_json='{}' WHERE id=?", (_stable(sections), actor_id, now, assembly_id))
            self._event(con, workspace_id, "assembly", assembly_id, "methods-generated", actor_id, {"packageId": package["id"], "sourceHash": section["sourceHash"]})
            return {"ok": True, "section": section, "assembly": self._assembly_record(con.execute("SELECT * FROM research_assemblies WHERE id=?", (assembly_id,)).fetchone())}

    def validate(self, workspace_id: str, assembly_id: str, actor_id: str):
        record = self.get_assembly(workspace_id, assembly_id, actor_id)["assembly"]
        issues: list[dict[str, str]] = []
        included = [s for s in record["sections"] if s.get("included", True)]
        if not record["title"]:
            issues.append({"severity": "error", "code": "title-required", "message": "A title is required."})
        if not included:
            issues.append({"severity": "error", "code": "sections-required", "message": "At least one included section is required."})
        if record["documentType"] == "manuscript" and not any(s.get("kind") == "abstract" for s in included):
            issues.append({"severity": "warning", "code": "abstract-recommended", "message": "A manuscript should include an abstract."})
        if record["documentType"] == "notebook" and not any(s.get("kind") in {"notebook-markdown", "notebook-output"} for s in included):
            issues.append({"severity": "error", "code": "notebook-cells-required", "message": "A notebook assembly requires notebook-markdown or notebook-output sections."})
        if not record["packageId"]:
            issues.append({"severity": "warning", "code": "package-recommended", "message": "Link a reproducibility package for complete methods and environment provenance."})
        validation = {"schema": "sc-lab-assembly-validation/0.37.1", "version": VERSION, "assemblyId": assembly_id, "ok": not any(i["severity"] == "error" for i in issues), "issues": issues, "sectionCount": len(included), "validationHash": _hash({"assembly": record, "issues": issues}), "validatedAt": _now()}
        return {"ok": validation["ok"], "validation": validation}

    @staticmethod
    def _section_body(section: dict[str, Any]) -> str:
        content = section.get("content") or {}
        if isinstance(content, dict):
            if "body" in content:
                return _text(content.get("body"), 100000)
            if "text" in content:
                return _text(content.get("text"), 100000)
            if section.get("kind") == "table":
                return _stable(content)
            if section.get("kind") == "figure":
                return _text(content.get("caption"), 10000)
            if section.get("kind") == "notebook-output":
                return _stable(content.get("output") if "output" in content else content)
        return _text(content, 100000)

    def _render(self, row: sqlite3.Row) -> dict[str, Any]:
        record = self._assembly_record(row)
        sections = [s for s in record["sections"] if s.get("included", True)]
        metadata = record["metadata"]
        authors = metadata.get("authors") if isinstance(metadata.get("authors"), list) else []
        citations = metadata.get("citations") if isinstance(metadata.get("citations"), list) else []
        md = [f"# {record['title']}"]
        if authors:
            md += ["", "**Authors:** " + ", ".join(_text(a.get("name") if isinstance(a, dict) else a, 300) for a in authors)]
        for section in sections:
            title = _text(section.get("title"), 300) or "Section"
            body = self._section_body(section)
            md += ["", f"## {title}", "", body]
        markdown = "\n".join(md).strip() + "\n"
        html_parts = ["<article>", "<h1>" + html.escape(record["title"]) + "</h1>"]
        if authors:
            html_parts.append("<p><strong>Authors:</strong> " + html.escape(", ".join(_text(a.get("name") if isinstance(a, dict) else a, 300) for a in authors)) + "</p>")
        for section in sections:
            html_parts.append("<section><h2>" + html.escape(_text(section.get("title"), 300) or "Section") + "</h2><p>" + html.escape(self._section_body(section)).replace("\n", "<br>") + "</p></section>")
        html_parts.append("</article>")
        jats = ["<article><front><article-meta><title-group><article-title>" + html.escape(record["title"]) + "</article-title></title-group></article-meta></front><body>"]
        for section in sections:
            jats.append("<sec><title>" + html.escape(_text(section.get("title"), 300) or "Section") + "</title><p>" + html.escape(self._section_body(section)) + "</p></sec>")
        jats.append("</body></article>")
        notebook_cells = []
        for section in sections:
            source = [line + "\n" for line in ("## " + (_text(section.get("title"), 300) or "Section") + "\n\n" + self._section_body(section)).splitlines()]
            notebook_cells.append({"cell_type": "markdown" if section.get("kind") != "notebook-output" else "raw", "metadata": {"scLabSectionId": section.get("id"), "scLabKind": section.get("kind")}, "source": source})
        notebook = {"cells": notebook_cells, "metadata": {"kernelspec": {"display_name": "No execution — reproducibility output", "language": "text", "name": "sc-lab-output-only"}, "language_info": {"name": "text"}, "scLab": {"assemblyId": record["id"], "assemblyHash": record.get("assemblyHash"), "outputOnly": True}}, "nbformat": 4, "nbformat_minor": 5}
        bib_lines = []
        for idx, citation in enumerate(citations, 1):
            if isinstance(citation, dict):
                key = _text(citation.get("key"), 120) or f"reference{idx}"
                title = _text(citation.get("title") or citation.get("formatted"), 1000)
                author = _text(citation.get("author"), 1000)
                year = _text(citation.get("year"), 20)
                bib_lines.append(f"@misc{{{key},\n  title = {{{title}}},\n  author = {{{author}}},\n  year = {{{year}}}\n}}")
            else:
                bib_lines.append(f"@misc{{reference{idx},\n  note = {{{_text(citation, 2000)}}}\n}}")
        methods = "\n\n".join(self._section_body(s) for s in sections if s.get("kind") == "methods").strip() + "\n"
        files = {
            "assembly.json": _stable(record),
            "manuscript.md": markdown,
            "report.html": "".join(html_parts),
            "manuscript.xml": "".join(jats),
            "notebook.ipynb": _stable(notebook),
            "methods.md": methods,
            "references.bib": "\n\n".join(bib_lines) + ("\n" if bib_lines else ""),
        }
        hashes = {name: sha256(content.encode("utf-8")).hexdigest() for name, content in files.items()}
        export = {"schema": EXPORT_SCHEMA, "version": VERSION, "assemblyId": record["id"], "documentType": record["documentType"], "files": files, "fileHashes": hashes, "exportHash": _hash(hashes), "createdAt": _now()}
        export["files"]["export-manifest.json"] = _stable({"assemblyId": record["id"], "fileHashes": hashes, "exportHash": export["exportHash"]})
        return export

    def render(self, workspace_id: str, assembly_id: str, actor_id: str):
        workspace_id, assembly_id, actor_id = _id(workspace_id, "workspace ID"), _id(assembly_id, "assembly ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id)
        with self._connect() as con:
            row = con.execute("SELECT * FROM research_assemblies WHERE id=? AND workspace_id=?", (assembly_id, workspace_id)).fetchone()
            if not row:
                raise ManuscriptAssemblyError("Assembly not found.", 404)
            export = self._render(row)
            summary = {"exportHash": export["exportHash"], "fileHashes": export["fileHashes"], "formats": sorted(export["files"])}
            con.execute("UPDATE research_assemblies SET render_json=?,updated_at=? WHERE id=?", (_stable(summary), _now(), assembly_id))
            self._event(con, workspace_id, "assembly", assembly_id, "assembly-rendered", actor_id, summary)
            return {"ok": True, "export": export}

    def seal(self, workspace_id: str, assembly_id: str, actor_id: str):
        workspace_id, assembly_id, actor_id = _id(workspace_id, "workspace ID"), _id(assembly_id, "assembly ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        validation = self.validate(workspace_id, assembly_id, actor_id)["validation"]
        if not validation["ok"]:
            raise ManuscriptAssemblyError("Assembly validation must pass before sealing.", 409)
        with self._connect() as con:
            row = con.execute("SELECT * FROM research_assemblies WHERE id=? AND workspace_id=?", (assembly_id, workspace_id)).fetchone()
            if row["status"] == "sealed":
                return {"ok": True, "assembly": self._assembly_record(row)}
            if row["status"] != "draft":
                raise ManuscriptAssemblyError("Only draft assemblies can be sealed.", 409)
            core = self._assembly_record(row)
            core.pop("assemblyHash", None)
            core.pop("render", None)
            core.pop("updatedBy", None)
            core.pop("updatedAt", None)
            assembly_hash = _hash(core)
            now = _now()
            con.execute("UPDATE research_assemblies SET status='sealed',assembly_hash=?,sealed_at=?,updated_by=?,updated_at=? WHERE id=?", (assembly_hash, now, actor_id, now, assembly_id))
            self._event(con, workspace_id, "assembly", assembly_id, "assembly-sealed", actor_id, {"assemblyHash": assembly_hash, "validationHash": validation["validationHash"]})
            return {"ok": True, "assembly": self._assembly_record(con.execute("SELECT * FROM research_assemblies WHERE id=?", (assembly_id,)).fetchone())}

    def revise(self, workspace_id: str, assembly_id: str, payload: dict[str, Any], actor_id: str):
        workspace_id, assembly_id, actor_id = _id(workspace_id, "workspace ID"), _id(assembly_id, "assembly ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        payload = _obj(payload)
        source = self.get_assembly(workspace_id, assembly_id, actor_id)["assembly"]
        if source["status"] != "sealed":
            raise ManuscriptAssemblyError("Only sealed assemblies can be revised.", 409)
        new_id = _id(payload.get("id") or (assembly_id + "-revision-" + secrets.token_hex(4)), "revision assembly ID")
        create_payload = {"id": new_id, "title": _text(payload.get("title"), 300) or source["title"], "documentType": source["documentType"], "template": source["template"], "packageId": source["packageId"], "publicationId": source["publicationId"], "citationStyle": source["citationStyle"], "metadata": source["metadata"], "sections": source["sections"], "parentAssemblyId": source["id"], "parentAssemblyHash": source["assemblyHash"]}
        result = self.create_assembly(workspace_id, create_payload, actor_id)
        with self._connect() as con:
            self._event(con, workspace_id, "assembly", new_id, "assembly-revision-created", actor_id, {"parentAssemblyId": source["id"], "parentAssemblyHash": source["assemblyHash"]})
        return result

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500):
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id)
        limit = max(1, min(self.history_limit, int(limit)))
        with self._connect() as con:
            rows = con.execute("SELECT * FROM assembly_events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?", (workspace_id, limit)).fetchall()
            events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": row["sequence"], "workspaceId": row["workspace_id"], "entityType": row["entity_type"], "entityId": row["entity_id"], "eventType": row["event_type"], "actorId": row["actor_id"], "details": json.loads(row["details_json"]), "eventHash": row["event_hash"], "createdAt": row["created_at"]} for row in rows]
            return {"ok": True, "version": VERSION, "events": events}

    def health(self):
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            schema = int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
            assemblies = con.execute("SELECT COUNT(*) FROM research_assemblies").fetchone()[0]
            sections = con.execute("SELECT COUNT(*) FROM assembly_sections").fetchone()[0]
        return {"ok": integrity == "ok", "version": VERSION, "status": "ready" if integrity == "ok" else "degraded", "database": {"integrity": integrity, "schemaVersion": schema, "assemblies": assemblies, "sectionLibrary": sections, "path": self.db_path}, "capabilities": policies(self.max_assemblies, self.max_sections, self.max_sections_per_assembly)["capabilities"]}
