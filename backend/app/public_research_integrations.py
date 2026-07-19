from __future__ import annotations

import base64
import copy
import hmac
import ipaddress
import json
import secrets
import socket
import sqlite3
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

VERSION = "0.38.2"
POLICY_SCHEMA = "sc-public-research-integration-policy/0.38.2"
WEBHOOK_SCHEMA = "sc-research-webhook-subscription/0.38.2"
DELIVERY_SCHEMA = "sc-research-webhook-delivery/0.38.2"
EVENT_SCHEMA = "sc-research-webhook-event/0.38.2"
EMBED_SCHEMA = "sc-research-embed-manifest/0.38.2"
SDK_SCHEMA = "sc-research-sdk-manifest/0.38.2"

EVENT_TYPES = {
    "research.handoff.created", "research.handoff.sealed", "research.handoff.accepted",
    "research.handoff.rejected", "research.handoff.needs_changes", "research.handoff.withdrawn",
    "research.publication.published", "research.reproduction.verified", "research.artifact.registered",
    "research.workflow.completed", "research.experiment.completed", "research.dataset.updated",
}
EMBED_VIEWS = {"handoff", "publication", "reproduction", "artifact", "dataset", "research-brief"}
SCOPES = {
    "research:read": "Read public and workspace-authorized research integration records.",
    "research:write": "Create governed handoffs and integration resources.",
    "webhooks:read": "Read webhook subscriptions and delivery history.",
    "webhooks:write": "Register, pause, update, and revoke webhook subscriptions.",
    "webhooks:emit": "Create signed webhook events and queued deliveries.",
    "embeds:write": "Create signed, expiring research embed manifests.",
}
ROLE_RANKS = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
FORBIDDEN_PUBLIC_KEYS = {"bytes", "rawdata", "restricteddata", "credentials", "secrets", "secret", "password", "accesstoken", "refreshtoken", "code", "executable", "callback"}
MAX_PUBLIC_PAYLOAD_BYTES = 4 * 1024 * 1024

class IntegrationError(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail); self.detail = detail; self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()

def _id(value: Any, label: str = "identifier") -> str:
    text = str(value or "").strip().lower()
    if not text or len(text) > 160 or not all(c.isalnum() or c in "-_.:" for c in text):
        raise IntegrationError(f"A valid {label} is required.")
    return text

def _secret(master: str, subscription_id: str) -> str:
    if not master:
        raise IntegrationError("Webhook signing is unavailable until SC_LAB_WEBHOOK_SIGNING_SECRET is configured.", 503)
    raw = hmac.new(master.encode(), f"subscription:{subscription_id}".encode(), sha256).digest()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")

def _signature(secret: str, timestamp: str, body: str) -> str:
    return hmac.new(secret.encode(), f"{timestamp}.{body}".encode(), sha256).hexdigest()

def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")

def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

def _normalized_key(value: Any) -> str:
    return "".join(character for character in str(value or "").lower() if character.isalnum())

def validate_public_payload(value: Any, label: str = "public research payload", depth: int = 0) -> Any:
    if depth > 16:
        raise IntegrationError(f"The {label} exceeds the maximum nesting depth.")
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            text_key = str(key)
            if _normalized_key(text_key) in FORBIDDEN_PUBLIC_KEYS:
                raise IntegrationError(f"The {label} contains a prohibited field: {text_key}.")
            clean[text_key] = validate_public_payload(item, label, depth + 1)
        result: Any = clean
    elif isinstance(value, list):
        result = [validate_public_payload(item, label, depth + 1) for item in value]
    elif value is None or isinstance(value, (str, int, float, bool)):
        result = value
    else:
        raise IntegrationError(f"The {label} contains an unsupported value type.")
    if depth == 0 and len(_stable(result).encode("utf-8")) > MAX_PUBLIC_PAYLOAD_BYTES:
        raise IntegrationError(f"The {label} exceeds the 4 MiB request limit.", 413)
    return result


def validate_webhook_url(value: Any, resolve_dns: bool = False) -> str:
    url = str(value or "").strip()
    if len(url) > 2048: raise IntegrationError("Webhook URL is too long.")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise IntegrationError("Webhook endpoints must be credential-free HTTPS URLs.")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".localhost")):
        raise IntegrationError("Local and internal webhook destinations are not allowed.")
    addresses: list[str] = []
    try:
        addresses.append(str(ipaddress.ip_address(host)))
    except ValueError:
        if resolve_dns:
            try: addresses.extend(sorted({row[4][0] for row in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}))
            except OSError as exc: raise IntegrationError("Webhook hostname could not be resolved.") from exc
    for item in addresses:
        ip = ipaddress.ip_address(item)
        if not ip.is_global:
            raise IntegrationError("Webhook endpoints may not resolve to private, loopback, link-local, multicast, or reserved addresses.")
    return url


def policies(delivery_enabled: bool = False, persistent: bool = False) -> dict[str, Any]:
    return {
        "ok": True, "version": VERSION, "schema": POLICY_SCHEMA,
        "api": {"baseVersion": "v1", "openApi": "/openapi.json", "catalog": "/v1/public-research-api", "maxRequestBytes": 4 * 1024 * 1024},
        "scopes": SCOPES,
        "webhooks": {"eventTypes": sorted(EVENT_TYPES), "httpsOnly": True, "ssrfProtection": True, "hmacSha256": True, "deliveryEnabled": bool(delivery_enabled), "deliveryMode": "https-dispatch" if delivery_enabled else "signed-queue"},
        "embeds": {"views": sorted(EMBED_VIEWS), "signed": True, "expiring": True, "maxTtlSeconds": 604800, "restrictedData": False},
        "sdk": {"python": True, "typescript": True, "zeroRuntimeDependencies": True},
        "durability": "persistent-disk" if persistent else "instance-local",
    }


def sdk_manifest() -> dict[str, Any]:
    body = {
        "ok": True, "schema": SDK_SCHEMA, "version": VERSION, "apiVersion": "v1",
        "packages": [
            {"language": "python", "package": "sustainable-catalyst-lab", "path": "sdk/python", "minimum": "3.10", "runtimeDependencies": []},
            {"language": "typescript", "package": "@sustainable-catalyst/lab-sdk", "path": "sdk/typescript", "minimum": "ES2022", "runtimeDependencies": []},
            {"language": "browser", "package": "SustainableCatalystResearchEmbed", "path": "sdk/embed", "minimum": "ES2020", "runtimeDependencies": []},
        ],
        "capabilities": ["typed-handoff-planning", "typed-handoff-creation", "webhook-administration", "webhook-event-emission", "signed-embed-manifests"],
    }
    body["manifestHash"] = _hash(body)
    return body


def public_api_catalog() -> dict[str, Any]:
    endpoints = [
        {"method":"GET","path":"/v1/public-research-api","auth":"public","purpose":"Stable API, policy, SDK, and schema discovery."},
        {"method":"GET","path":"/v1/research-integrations/health","auth":"integration-key","scope":"research:read"},
        {"method":"GET","path":"/v1/research-integrations/policies","auth":"public"},
        {"method":"GET","path":"/v1/research-integrations/sdk","auth":"public"},
        {"method":"GET","path":"/v1/team-workspaces/{workspaceId}/webhooks","auth":"integration-key","scope":"webhooks:read"},
        {"method":"POST","path":"/v1/team-workspaces/{workspaceId}/webhooks","auth":"integration-key","scope":"webhooks:write"},
        {"method":"PATCH","path":"/v1/team-workspaces/{workspaceId}/webhooks/{subscriptionId}","auth":"integration-key","scope":"webhooks:write"},
        {"method":"POST","path":"/v1/team-workspaces/{workspaceId}/webhook-events","auth":"integration-key","scope":"webhooks:emit"},
        {"method":"GET","path":"/v1/team-workspaces/{workspaceId}/webhook-deliveries","auth":"integration-key","scope":"webhooks:read"},
        {"method":"POST","path":"/v1/team-workspaces/{workspaceId}/webhook-deliveries/{deliveryId}/dispatch","auth":"integration-key","scope":"webhooks:emit"},
        {"method":"POST","path":"/v1/team-workspaces/{workspaceId}/research-embeds","auth":"integration-key","scope":"embeds:write"},
        {"method":"GET","path":"/v1/public/research-embeds/{token}","auth":"signed-token"},
    ]
    body = {"ok": True, "version": VERSION, "apiVersion": "v1", "schemas": [POLICY_SCHEMA, WEBHOOK_SCHEMA, DELIVERY_SCHEMA, EVENT_SCHEMA, EMBED_SCHEMA, SDK_SCHEMA], "endpoints": endpoints}
    body["catalogHash"] = _hash(body)
    return body


class PublicResearchIntegrationGateway:
    def __init__(self, db_path: str, workspaces: Any, signing_secret: str, delivery_enabled: bool = False, persistent_disk_mounted: bool = False, max_subscriptions: int = 5000, max_deliveries: int = 250000):
        self.db_path = str(db_path); self.workspaces = workspaces; self.signing_secret = str(signing_secret or "")
        self.delivery_enabled = bool(delivery_enabled); self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_subscriptions = max(1, int(max_subscriptions)); self.max_deliveries = max(100, int(max_deliveries))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True); self._init_db()

    def _connect(self):
        con=sqlite3.connect(self.db_path, timeout=30); con.row_factory=sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL"); con.execute("PRAGMA foreign_keys=ON"); con.execute("PRAGMA busy_timeout=30000"); return con

    def _init_db(self):
        with self._connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS webhook_subscriptions(
              id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,url TEXT NOT NULL,status TEXT NOT NULL,events_json TEXT NOT NULL,
              description TEXT NOT NULL,secret_fingerprint TEXT NOT NULL,created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
              UNIQUE(workspace_id,url)
            );
            CREATE INDEX IF NOT EXISTS idx_webhooks_workspace ON webhook_subscriptions(workspace_id,status,updated_at);
            CREATE TABLE IF NOT EXISTS webhook_events(
              id TEXT NOT NULL,workspace_id TEXT NOT NULL,event_type TEXT NOT NULL,request_hash TEXT NOT NULL,event_hash TEXT NOT NULL,
              event_json TEXT NOT NULL,created_at TEXT NOT NULL,PRIMARY KEY(workspace_id,id)
            );
            CREATE TABLE IF NOT EXISTS webhook_deliveries(
              id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,subscription_id TEXT NOT NULL,event_id TEXT NOT NULL,event_type TEXT NOT NULL,status TEXT NOT NULL,
              attempt INTEGER NOT NULL,envelope_json TEXT NOT NULL,envelope_hash TEXT NOT NULL,signature TEXT NOT NULL,
              response_code INTEGER,response_excerpt TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
              FOREIGN KEY(subscription_id) REFERENCES webhook_subscriptions(id)
            );
            CREATE INDEX IF NOT EXISTS idx_webhook_events_workspace ON webhook_events(workspace_id,created_at);
            CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_workspace ON webhook_deliveries(workspace_id,status,updated_at);
            """)
            columns={row[1] for row in con.execute("PRAGMA table_info(webhook_deliveries)").fetchall()}
            if "event_id" not in columns:
                con.execute("ALTER TABLE webhook_deliveries ADD COLUMN event_id TEXT NOT NULL DEFAULT ''")
                con.execute("UPDATE webhook_deliveries SET event_id='legacy-' || id WHERE event_id='' OR event_id IS NULL")
            con.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_webhook_delivery_idempotency ON webhook_deliveries(subscription_id,event_id)")

    def _workspace(self, workspace_id: str, actor_id: str, minimum: str = "viewer"):
        try:
            workspace = self.workspaces.get(workspace_id, actor_id, False, False)["workspace"]
        except Exception as exc:
            raise IntegrationError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 403)) from exc
        membership = workspace.get("currentMembership") or {}
        role = str(membership.get("role") or "viewer")
        if ROLE_RANKS.get(role, 0) < ROLE_RANKS.get(minimum, 0):
            raise IntegrationError(f"The {minimum} role or higher is required.", 403)
        return workspace

    def _require_signing(self) -> None:
        if not self.signing_secret:
            raise IntegrationError("Research integration signing is unavailable until SC_LAB_WEBHOOK_SIGNING_SECRET is configured.", 503)

    @staticmethod
    def _subscription(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema":WEBHOOK_SCHEMA,"version":VERSION,"id":row["id"],"workspaceId":row["workspace_id"],"url":row["url"],"status":row["status"],"events":json.loads(row["events_json"]),"description":row["description"],"secretFingerprint":row["secret_fingerprint"],"createdBy":row["created_by"],"createdAt":row["created_at"],"updatedAt":row["updated_at"]}

    @staticmethod
    def _delivery(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema":DELIVERY_SCHEMA,"version":VERSION,"id":row["id"],"workspaceId":row["workspace_id"],"subscriptionId":row["subscription_id"],"eventId":row["event_id"],"eventType":row["event_type"],"status":row["status"],"attempt":row["attempt"],"envelope":json.loads(row["envelope_json"]),"envelopeHash":row["envelope_hash"],"signature":row["signature"],"responseCode":row["response_code"],"responseExcerpt":row["response_excerpt"],"createdAt":row["created_at"],"updatedAt":row["updated_at"]}

    def register_webhook(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id,actor_id,"editor"); self._require_signing()
        body=validate_public_payload(copy.deepcopy(payload or {}), "webhook subscription"); sid=_id(body.get("id") or f"wh-{secrets.token_hex(8)}","webhook identifier")
        url=validate_webhook_url(body.get("url"), bool(body.get("resolveDns",False)))
        events=sorted(set(str(x).strip() for x in (body.get("events") or [])))
        if not events or any(x not in EVENT_TYPES for x in events): raise IntegrationError("At least one supported webhook event type is required.")
        description=str(body.get("description") or "").strip()[:500]
        secret=_secret(self.signing_secret,sid); fingerprint=sha256(secret.encode()).hexdigest()[:16]; now=_now()
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM webhook_subscriptions").fetchone()[0] >= self.max_subscriptions: raise IntegrationError("Webhook subscription capacity reached.",409)
            try: con.execute("INSERT INTO webhook_subscriptions VALUES(?,?,?,?,?,?,?,?,?,?)",(sid,workspace_id,url,"active",_stable(events),description,fingerprint,actor_id,now,now))
            except sqlite3.IntegrityError as exc: raise IntegrationError("The webhook identifier or workspace URL is already registered.",409) from exc
            row=con.execute("SELECT * FROM webhook_subscriptions WHERE id=?",(sid,)).fetchone()
        return {"ok":True,"subscription":self._subscription(row),"signingSecret":secret,"secretDisclosure":"one-time","signatureHeader":"X-SC-Lab-Signature","timestampHeader":"X-SC-Lab-Timestamp"}

    def list_webhooks(self, workspace_id: str, actor_id: str, status: str = "") -> dict[str, Any]:
        self._workspace(workspace_id,actor_id,"viewer"); args=[workspace_id]; sql="SELECT * FROM webhook_subscriptions WHERE workspace_id=?"
        if status: sql+=" AND status=?"; args.append(status)
        sql+=" ORDER BY updated_at DESC"
        with self._connect() as con: rows=con.execute(sql,args).fetchall()
        return {"ok":True,"count":len(rows),"subscriptions":[self._subscription(r) for r in rows]}

    def update_webhook(self, workspace_id: str, subscription_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id,actor_id,"editor"); self._require_signing()
        sid=_id(subscription_id); body=validate_public_payload(payload or {}, "webhook subscription update"); status=str(body.get("status") or "active").strip().lower()
        if status not in {"active","paused","revoked"}: raise IntegrationError("Webhook status must be active, paused, or revoked.")
        with self._connect() as con:
            row=con.execute("SELECT * FROM webhook_subscriptions WHERE id=? AND workspace_id=?",(sid,workspace_id)).fetchone()
            if not row: raise IntegrationError("Webhook subscription not found.",404)
            events=json.loads(row["events_json"])
            if "events" in body:
                events=sorted(set(str(x).strip() for x in (body.get("events") or [])))
                if not events or any(x not in EVENT_TYPES for x in events): raise IntegrationError("At least one supported webhook event type is required.")
            url=validate_webhook_url(body["url"],bool(body.get("resolveDns",False))) if "url" in body else row["url"]
            description=str(body.get("description",row["description"]))[:500]; now=_now()
            con.execute("UPDATE webhook_subscriptions SET url=?,status=?,events_json=?,description=?,updated_at=? WHERE id=?",(url,status,_stable(events),description,now,sid))
            updated=con.execute("SELECT * FROM webhook_subscriptions WHERE id=?",(sid,)).fetchone()
        return {"ok":True,"subscription":self._subscription(updated)}

    def emit_event(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id,actor_id,"contributor"); self._require_signing()
        body=validate_public_payload(copy.deepcopy(payload or {}), "webhook event")
        event_type=str(body.get("eventType") or "").strip()
        if event_type not in EVENT_TYPES: raise IntegrationError("A supported webhook eventType is required.")
        data=body.get("data") or {}
        if not isinstance(data,dict): raise IntegrationError("Webhook event data must be an object.")
        event_id=_id(body.get("id") or f"evt-{secrets.token_hex(12)}","event identifier")
        subject=str(body.get("subject") or "").strip()[:500]
        request_hash=_hash({"workspaceId":workspace_id,"id":event_id,"eventType":event_type,"subject":subject,"data":data})
        with self._connect() as con:
            existing=con.execute("SELECT * FROM webhook_events WHERE workspace_id=? AND id=?",(workspace_id,event_id)).fetchone()
            if existing:
                if existing["request_hash"] != request_hash:
                    raise IntegrationError("The webhook event identifier is already bound to a different payload.",409)
                event=json.loads(existing["event_json"])
                rows=con.execute("SELECT * FROM webhook_deliveries WHERE workspace_id=? AND event_id=? ORDER BY created_at",(workspace_id,event_id)).fetchall()
                return {"ok":True,"idempotent":True,"event":event,"deliveryMode":"https-dispatch" if self.delivery_enabled else "signed-queue","count":len(rows),"deliveries":[self._delivery(row) for row in rows]}
            event={"schema":EVENT_SCHEMA,"version":VERSION,"id":event_id,"workspaceId":workspace_id,"eventType":event_type,"occurredAt":str(body.get("occurredAt") or _now()),"actorId":actor_id,"data":data}
            if subject: event["subject"] = subject
            event["eventHash"]=_hash(event); raw=_stable(event); timestamp=str(int(datetime.now(timezone.utc).timestamp()))
            rows=con.execute("SELECT * FROM webhook_subscriptions WHERE workspace_id=? AND status='active'",(workspace_id,)).fetchall()
            matching=[row for row in rows if event_type in json.loads(row["events_json"])]
            current=con.execute("SELECT COUNT(*) FROM webhook_deliveries").fetchone()[0]
            if current + len(matching) > self.max_deliveries:
                raise IntegrationError("Webhook delivery capacity reached.",409)
            con.execute("INSERT INTO webhook_events VALUES(?,?,?,?,?,?,?)",(event_id,workspace_id,event_type,request_hash,event["eventHash"],raw,_now()))
            deliveries=[]
            for row in matching:
                did=f"del-{secrets.token_hex(12)}"; secret=_secret(self.signing_secret,row["id"]); signature=_signature(secret,timestamp,raw)
                envelope={"event":event,"deliveryId":did,"subscriptionId":row["id"],"timestamp":timestamp}
                envelope_hash=_hash(envelope); now=_now(); status="queued"
                con.execute("INSERT INTO webhook_deliveries (id,workspace_id,subscription_id,event_id,event_type,status,attempt,envelope_json,envelope_hash,signature,response_code,response_excerpt,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(did,workspace_id,row["id"],event_id,event_type,status,0,_stable(envelope),envelope_hash,signature,None,None,now,now))
                deliveries.append({"schema":DELIVERY_SCHEMA,"version":VERSION,"id":did,"workspaceId":workspace_id,"subscriptionId":row["id"],"eventId":event_id,"eventType":event_type,"url":row["url"],"status":status,"attempt":0,"envelope":envelope,"envelopeHash":envelope_hash,"signature":signature,"responseCode":None,"responseExcerpt":None,"createdAt":now,"updatedAt":now})
        return {"ok":True,"idempotent":False,"event":event,"deliveryMode":"https-dispatch" if self.delivery_enabled else "signed-queue","count":len(deliveries),"deliveries":deliveries}

    def list_deliveries(self, workspace_id: str, actor_id: str, status: str = "", limit: int = 200) -> dict[str, Any]:
        self._workspace(workspace_id,actor_id,"viewer"); args=[workspace_id]; sql="SELECT * FROM webhook_deliveries WHERE workspace_id=?"
        if status: sql+=" AND status=?"; args.append(status)
        sql+=" ORDER BY updated_at DESC LIMIT ?"; args.append(max(1,min(int(limit),2000)))
        with self._connect() as con: rows=con.execute(sql,args).fetchall()
        return {"ok":True,"count":len(rows),"deliveries":[self._delivery(r) for r in rows]}


    def dispatch_delivery(self, workspace_id: str, delivery_id: str, actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id,actor_id,"contributor")
        if not self.delivery_enabled:
            raise IntegrationError("Outbound webhook delivery is disabled. Set SC_LAB_WEBHOOK_DELIVERY_ENABLED=1 after configuring a signing secret and approved network policy.",503)
        did=_id(delivery_id,"delivery identifier")
        with self._connect() as con:
            row=con.execute("SELECT d.*,s.url,s.status AS subscription_status FROM webhook_deliveries d JOIN webhook_subscriptions s ON s.id=d.subscription_id WHERE d.id=? AND d.workspace_id=?",(did,workspace_id)).fetchone()
            if not row: raise IntegrationError("Webhook delivery not found.",404)
            if row["subscription_status"]!="active": raise IntegrationError("The webhook subscription is not active.",409)
            url=validate_webhook_url(row["url"],True)
            envelope=json.loads(row["envelope_json"]); event_raw=_stable(envelope["event"]).encode("utf-8")
            headers={"Content-Type":"application/json","User-Agent":f"Sustainable-Catalyst-Lab/{VERSION}","X-SC-Lab-Delivery":did,"X-SC-Lab-Event":row["event_type"],"X-SC-Lab-Timestamp":envelope["timestamp"],"X-SC-Lab-Signature":row["signature"]}
            now=_now(); attempt=int(row["attempt"])+1
            con.execute("UPDATE webhook_deliveries SET status='delivering',attempt=?,updated_at=? WHERE id=?",(attempt,now,did))
        code=None; excerpt=""; status="failed"
        try:
            with urlopen(Request(url,data=event_raw,headers=headers,method="POST"),timeout=15) as response:
                code=int(getattr(response,"status",response.getcode())); excerpt=response.read(4096).decode("utf-8",errors="replace"); status="delivered" if 200<=code<300 else "failed"
        except HTTPError as exc:
            code=int(exc.code); excerpt=exc.read(4096).decode("utf-8",errors="replace"); status="failed"
        except (URLError,OSError) as exc:
            excerpt=str(exc)[:4096]; status="failed"
        with self._connect() as con:
            con.execute("UPDATE webhook_deliveries SET status=?,response_code=?,response_excerpt=?,updated_at=? WHERE id=?",(status,code,excerpt,_now(),did))
            updated=con.execute("SELECT * FROM webhook_deliveries WHERE id=?",(did,)).fetchone()
        return {"ok":status=="delivered","delivery":self._delivery(updated)}

    def create_embed(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id,actor_id,"viewer"); self._require_signing()
        body=validate_public_payload(copy.deepcopy(payload or {}), "research embed")
        view=str(body.get("view") or "").strip().lower()
        if view not in EMBED_VIEWS: raise IntegrationError("A supported research embed view is required.")
        resource=body.get("resource") or {}
        if not isinstance(resource,dict) or not resource.get("id"): raise IntegrationError("Embed resource.id is required.")
        ttl=max(60,min(int(body.get("ttlSeconds") or 3600),604800)); issued=datetime.now(timezone.utc); expires=issued+timedelta(seconds=ttl)
        metadata=body.get("metadata") or {}
        if not isinstance(metadata,dict): raise IntegrationError("Embed metadata must be an object.")
        manifest={"schema":EMBED_SCHEMA,"version":VERSION,"workspaceId":workspace_id,"view":view,"resource":resource,"metadata":metadata,"theme":str(body.get("theme") or "system")[:32],"title":str(body.get("title") or "")[:300],"issuedAt":issued.isoformat(),"expiresAt":expires.isoformat()}
        manifest["manifestHash"]=_hash(manifest); payload64=_b64(_stable(manifest).encode()); signature=_signature(self.signing_secret,"embed",payload64); token=f"{payload64}.{signature}"
        return {"ok":True,"manifest":manifest,"token":token,"embedPath":f"/v1/public/research-embeds/{token}","iframeSandbox":"allow-scripts allow-same-origin"}

    def verify_embed(self, token: str) -> dict[str, Any]:
        self._require_signing()
        try: payload64, signature=token.split(".",1); expected=_signature(self.signing_secret,"embed",payload64)
        except Exception as exc: raise IntegrationError("Invalid research embed token.",404) from exc
        if not hmac.compare_digest(signature,expected): raise IntegrationError("Research embed signature is invalid.",403)
        try: manifest=json.loads(_unb64(payload64))
        except Exception as exc: raise IntegrationError("Research embed payload is invalid.",422) from exc
        if _hash({k:v for k,v in manifest.items() if k!="manifestHash"}) != manifest.get("manifestHash"): raise IntegrationError("Research embed manifest integrity check failed.",409)
        expires=datetime.fromisoformat(manifest["expiresAt"])
        if expires <= datetime.now(timezone.utc): raise IntegrationError("Research embed token has expired.",410)
        return {"ok":True,"manifest":manifest,"cacheControl":"public, max-age=60, stale-while-revalidate=300"}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            subscriptions=con.execute("SELECT COUNT(*) FROM webhook_subscriptions").fetchone()[0]; deliveries=con.execute("SELECT COUNT(*) FROM webhook_deliveries").fetchone()[0]
        return {"ok":True,"status":"ready" if self.signing_secret else "configuration-required","version":VERSION,"schema":"sc-public-research-integration-health/0.38.2","signingConfigured":bool(self.signing_secret),"subscriptionCount":subscriptions,"deliveryCount":deliveries,"eventTypes":sorted(EVENT_TYPES),"embedViews":sorted(EMBED_VIEWS),"policy":policies(self.delivery_enabled,self.persistent_disk_mounted),"sdk":sdk_manifest()}
