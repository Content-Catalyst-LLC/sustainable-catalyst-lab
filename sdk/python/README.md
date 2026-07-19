# Sustainable Catalyst Lab Python SDK v0.39.1

A standard-library-only client for typed research handoffs, webhooks, embeds, and institutional governance.

```python
from sustainable_catalyst_lab import LabClient

client = LabClient("https://lab.example.org", api_key="...", actor_id="principal-123")
print(client.governance_policies())
print(client.list_institutions())
```

The client sends both the public integration and compute-key headers so the same credential can be routed through installations that expose either authenticated surface.
