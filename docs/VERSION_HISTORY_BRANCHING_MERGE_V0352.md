# Sustainable Catalyst Lab v0.35.2

## Version History, Branching, Merge, and Conflict Resolution

v0.35.2 adds immutable version control for shared research workspaces. A snapshot stores a canonical JSON tree and SHA-256 identity. Branches reference immutable snapshots; branch heads move only through new snapshot or merge records.

Three-way merge compares a common base with source and target heads. Non-overlapping changes merge automatically. Concurrent edits to the same path create durable conflict records containing base, source, and target values. Resolution creates a new record and never overwrites the original conflict evidence.

The protected `main` branch requires a signed v0.35.1 scientific approval before a merge can be finalized. Restoring an earlier state creates a new descendant snapshot rather than rewriting or deleting history.

The shared workspace SQLite database migrates in place to schema version 3. Existing membership, invitations, resources, comments, reviews, approvals, and sign-offs remain intact.
