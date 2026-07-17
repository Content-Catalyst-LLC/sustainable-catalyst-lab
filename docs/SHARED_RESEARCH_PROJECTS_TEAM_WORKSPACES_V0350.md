# Shared Research Projects and Team Workspaces — v0.35.0

Sustainable Catalyst Lab v0.35.0 introduces private collaboration workspaces above the existing scientific project, workflow, model, dataset, artifact, and evidence layers.

## Governance model

Each workspace has exactly one owner and any number of active members. Roles are ordered as viewer, reviewer, contributor, editor, administrator, and owner. The Python coordinator—not browser JavaScript—performs every permission decision. Ownership transfer preserves the former owner as an administrator so historical responsibility is not erased.

## Invitations

Invitation tokens are generated with cryptographic randomness, returned once, and stored only as SHA-256 digests. Invitations can be targeted to a specific actor, expire automatically, and cannot be reused. Archiving a workspace revokes pending invitations.

## Shared resources

A workspace can link existing Lab projects, datasets, workflows, runs, experiments, campaigns, models, surrogates, ensembles, artifacts, notebooks, sources, evidence, and reports. Each link declares a minimum role. The link is a governance record; it does not copy, mutate, or execute the underlying resource.

## Lifecycle and evidence

Workspaces are archived rather than hard-deleted. Creation, updates, invitations, membership changes, ownership transfer, resource links, access decisions, and archival actions produce durable events with SHA-256 event hashes.

## Deferred to v0.35.1

Comments, threaded review, approval decisions, and scientific sign-off are deliberately excluded from this release.
