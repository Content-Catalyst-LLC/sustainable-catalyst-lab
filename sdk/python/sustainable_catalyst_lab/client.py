from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class LabAPIError(RuntimeError):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _segment(value: Any) -> str:
    return quote(str(value), safe="-._~")


class LabClient:
    def __init__(self, base_url: str, api_key: str = "", actor_id: str = "sdk-client", timeout: float = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.actor_id = actor_id
        self.timeout = timeout

    def request(self, method: str, path: str, payload: Any = None) -> Any:
        body = None if payload is None else json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        headers = {"Accept": "application/json", "X-SC-Lab-Actor": self.actor_id}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.api_key:
            headers["X-SC-Lab-API-Key"] = self.api_key
            headers["X-SC-Lab-Key"] = self.api_key
        try:
            with urlopen(Request(self.base_url + path, data=body, headers=headers, method=method), timeout=self.timeout) as response:
                return json.loads(response.read())
        except HTTPError as exc:
            try:
                detail = json.loads(exc.read()).get("detail", str(exc))
            except Exception:
                detail = str(exc)
            raise LabAPIError(exc.code, detail) from exc
        except URLError as exc:
            raise LabAPIError(0, str(exc.reason or exc)) from exc

    def catalog(self):
        return self.request("GET", "/v1/public-research-api")

    def sdk_manifest(self):
        return self.request("GET", "/v1/research-integrations/sdk")

    def integration_health(self):
        return self.request("GET", "/v1/research-integrations/health")

    def adapters(self):
        return self.request("GET", "/v1/typed-cross-product-handoffs/adapters")

    def plan_handoff(self, workspace_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/typed-research-handoffs/plan", payload)

    def create_handoff(self, workspace_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/typed-research-handoffs", payload)

    def list_webhooks(self, workspace_id: str, status: str = ""):
        query = f"?status={_segment(status)}" if status else ""
        return self.request("GET", f"/v1/team-workspaces/{_segment(workspace_id)}/webhooks{query}")

    def register_webhook(self, workspace_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/webhooks", payload)

    def update_webhook(self, workspace_id: str, subscription_id: str, payload: Any):
        return self.request("PATCH", f"/v1/team-workspaces/{_segment(workspace_id)}/webhooks/{_segment(subscription_id)}", payload)

    def emit_event(self, workspace_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/webhook-events", payload)

    def list_deliveries(self, workspace_id: str, status: str = "", limit: int = 200):
        query = f"?limit={max(1, min(int(limit), 2000))}"
        if status:
            query += f"&status={_segment(status)}"
        return self.request("GET", f"/v1/team-workspaces/{_segment(workspace_id)}/webhook-deliveries{query}")

    def dispatch_webhook(self, workspace_id: str, delivery_id: str):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/webhook-deliveries/{_segment(delivery_id)}/dispatch", {})

    def create_embed(self, workspace_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/research-embeds", payload)

    def read_embed(self, token: str):
        return self.request("GET", f"/v1/public/research-embeds/{_segment(token)}")

    def governance_health(self):
        return self.request("GET", "/v1/institutional-governance/health")

    def governance_policies(self):
        return self.request("GET", "/v1/institutional-governance/policies")

    def list_institutions(self):
        return self.request("GET", "/v1/institutions")

    def create_institution(self, payload: Any):
        return self.request("POST", "/v1/institutions", payload)

    def get_institution(self, institution_id: str):
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}")

    def list_units(self, institution_id: str):
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/units")

    def create_unit(self, institution_id: str, payload: Any):
        return self.request("POST", f"/v1/institutions/{_segment(institution_id)}/units", payload)

    def list_principals(self, institution_id: str, status: str = ""):
        query = f"?status={_segment(status)}" if status else ""
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/principals{query}")

    def create_principal(self, institution_id: str, payload: Any):
        return self.request("POST", f"/v1/institutions/{_segment(institution_id)}/principals", payload)

    def list_role_bindings(self, institution_id: str, principal_id: str = "", workspace_id: str = ""):
        params = []
        if principal_id:
            params.append(f"principalId={_segment(principal_id)}")
        if workspace_id:
            params.append(f"workspaceId={_segment(workspace_id)}")
        query = "?" + "&".join(params) if params else ""
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/role-bindings{query}")

    def grant_role(self, institution_id: str, payload: Any):
        return self.request("POST", f"/v1/institutions/{_segment(institution_id)}/role-bindings", payload)

    def revoke_role(self, institution_id: str, binding_id: str):
        return self.request("DELETE", f"/v1/institutions/{_segment(institution_id)}/role-bindings/{_segment(binding_id)}")

    def list_retention_policies(self, institution_id: str):
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/retention-policies")

    def create_retention_policy(self, institution_id: str, payload: Any):
        return self.request("POST", f"/v1/institutions/{_segment(institution_id)}/retention-policies", payload)

    def get_workspace_governance(self, workspace_id: str):
        return self.request("GET", f"/v1/team-workspaces/{_segment(workspace_id)}/institutional-governance")

    def configure_workspace_governance(self, workspace_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/institutional-governance", payload)

    def evaluate_governance(self, workspace_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/institutional-governance/evaluate", payload)

    def list_governance_approvals(self, workspace_id: str, status: str = ""):
        query = f"?status={_segment(status)}" if status else ""
        return self.request("GET", f"/v1/team-workspaces/{_segment(workspace_id)}/governance-approvals{query}")

    def create_governance_approval(self, workspace_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/governance-approvals", payload)

    def decide_governance_approval(self, workspace_id: str, request_id: str, payload: Any):
        return self.request("POST", f"/v1/team-workspaces/{_segment(workspace_id)}/governance-approvals/{_segment(request_id)}/decisions", payload)

    def governance_dashboard(self, institution_id: str):
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/governance-dashboard")

    def governance_timeline(self, institution_id: str, limit: int = 500):
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/governance-timeline?limit={max(1, min(int(limit), 5000))}")

    def security_privacy_health(self):
        return self.request("GET", "/v1/security-privacy/health")

    def security_privacy_policies(self):
        return self.request("GET", "/v1/security-privacy/policies")

    def list_secrets(self, institution_id: str, name: str = ""):
        query = f"?name={_segment(name)}" if name else ""
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/secrets{query}")

    def put_secret(self, institution_id: str, payload: Any):
        return self.request("POST", f"/v1/institutions/{_segment(institution_id)}/secrets", payload)

    def list_service_credentials(self, institution_id: str, principal_id: str = ""):
        query = f"?principalId={_segment(principal_id)}" if principal_id else ""
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/service-credentials{query}")

    def issue_service_credential(self, institution_id: str, principal_id: str, payload: Any):
        return self.request("POST", f"/v1/institutions/{_segment(institution_id)}/principals/{_segment(principal_id)}/service-credentials", payload)

    def revoke_service_credential(self, institution_id: str, credential_id: str):
        return self.request("DELETE", f"/v1/institutions/{_segment(institution_id)}/service-credentials/{_segment(credential_id)}")

    def privacy_scan(self, payload: Any):
        return self.request("POST", "/v1/security-privacy/privacy-scan", payload)

    def privacy_redact(self, payload: Any):
        return self.request("POST", "/v1/security-privacy/privacy-redact", payload)

    def list_privacy_requests(self, institution_id: str, status: str = ""):
        query = f"?status={_segment(status)}" if status else ""
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/privacy-requests{query}")

    def create_privacy_request(self, institution_id: str, payload: Any):
        return self.request("POST", f"/v1/institutions/{_segment(institution_id)}/privacy-requests", payload)

    def verify_security_audit(self, institution_id: str):
        return self.request("GET", f"/v1/institutions/{_segment(institution_id)}/security-audit/verify")


def verify_webhook(secret: str, timestamp: str, body: bytes, signature: str) -> bool:
    expected = hmac.new(secret.encode("utf-8"), timestamp.encode("utf-8") + b"." + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
