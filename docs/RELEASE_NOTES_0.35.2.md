# Sustainable Catalyst Lab v0.35.2 Release Notes

## Version History, Branching, Merge, and Conflict Resolution

Sustainable Catalyst Lab v0.35.2 adds governed version control to Shared Research Projects and Team Workspaces. The release preserves complete scientific history while allowing teams to create branches, compare immutable snapshots, resolve divergent research changes, and merge approved work into protected branches.

## Capabilities

- Immutable full-tree workspace snapshots with SHA-256 identities
- Named research branches created from an explicit source snapshot
- Optimistic branch-head and revision checks to prevent lost updates
- Snapshot comparison with added, changed, and removed paths
- Restore-as-new-history rather than destructive rollback
- Three-way merge using a common ancestor
- Path-level merge conflict records
- Reviewer resolution from source, target, base, or a governed custom value
- Protected branches and administrator-managed branch policies
- Signed scientific approval gates for protected-branch merges
- Merge request cancellation and immutable merge history
- Durable, hashed workspace-version timelines
- Shared workspace database migration to schema version 3
- Administrator-only WordPress controls
- New Version History, Branching & Merge workspace
- 70 registered Lab panels

## Safety and governance

The versioning system does not rewrite or erase prior snapshots. It does not execute arbitrary Python, shell commands, executable expressions, or callbacks. Protected-branch finalization requires a signed approval from the v0.35.1 scientific review system.

## Compatibility

The cumulative DIRECT_BRIDGE_V17 installer accepts Lab repositories reporting v0.31.0 through v0.35.2 and carries forward the complete distributed compute, workflow, campaign, model, collaboration, and scientific review stack.
