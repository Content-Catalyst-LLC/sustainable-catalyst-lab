# Institutional Node Federation and Local-Data Execution — v0.36.1

This release adds governed compute federation for research institutions that cannot centralize confidential or restricted datasets.

## Security boundary

- Data records contain metadata, schema hashes, classifications, and export policies; restricted bytes stay local.
- Execution requests can reference only registered Lab methods allowed by the selected node.
- The coordinator signs canonical execution envelopes with HMAC-SHA256.
- Nodes authenticate claims with a node-scoped secret and attest results with HMAC-SHA256.
- Restricted and confidential datasets cannot use artifact-export output policy.
- Arbitrary Python, shell commands, executable expressions, and unrestricted callbacks are rejected.

## Operations

Workspace administrators register and suspend nodes. Editors register local assets and cancel work. Contributors can submit governed local runs. Reviewers and viewers can inspect nodes, requests, receipts, and the hashed event timeline.

## Durability

The federation database uses SQLite WAL. `SC_LAB_INSTITUTIONAL_NODE_PERSISTENT_DISK_MOUNTED` reports whether deployment persistence has been explicitly configured.
