# Review, Comments, Approvals, and Scientific Sign-Off — v0.35.1

Sustainable Catalyst Lab v0.35.1 extends shared research workspaces with governed scientific review and publication approval.

## Review discussions

Review threads may be attached to any governed workspace resource. Comments are append-only, hash-addressed, and may be nested. A comment can be withdrawn with a reason, but its original body, hash, author, and timestamp remain in the record.

## Assignments and concurrency

Editors, administrators, and owners may assign reviewer-capable workspace members. Every mutable review object carries a revision. State-changing requests must include `expectedRevision`; stale requests receive HTTP 409 rather than overwriting newer work.

## Approval gates

Approval requests can require a declared number of approvals, no unresolved review threads, and completion of all review assignments. Reviewer decisions are immutable and include a rationale, evidence references, timestamp, and SHA-256 decision hash.

## Scientific sign-off

Once all gates pass, an administrator or owner may create a single immutable scientific sign-off. The signed record binds the workspace identity, resource link, approval request, all decisions, signatory role, statement, and creation time into one canonical SHA-256 record.

## Safety boundary

This release does not execute arbitrary code, automate scientific judgment, silently edit comments or decisions, or hard-delete review history. It records accountable human review around resources already governed by Lab.
