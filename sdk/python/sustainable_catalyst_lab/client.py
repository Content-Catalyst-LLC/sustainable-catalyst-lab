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


def verify_webhook(secret: str, timestamp: str, body: bytes, signature: str) -> bool:
    expected = hmac.new(secret.encode("utf-8"), timestamp.encode("utf-8") + b"." + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
