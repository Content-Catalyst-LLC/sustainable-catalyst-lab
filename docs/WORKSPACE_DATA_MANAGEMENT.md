# Workspace Data Management

Version 0.9.2 adds local workspace backup, restore, selective clearing, and complete reset controls.

## Backup

- Workspace JSON
- Uncompressed ZIP compatible with the built-in browser restore reader
- Per-project JSON
- Notebook Markdown
- Observation CSV
- Visualization JSON
- Decision Studio packet JSON
- Manifest and README

## Restore modes

- Import as copies: assigns new project identifiers and retains existing projects
- Merge by project identifier
- Replace the current workspace

All imported projects pass through the current non-destructive project normalizer.

## Reset scopes

- Interface and visualization preferences
- Notes, observations, citations, and map annotations
- Calculation and analysis history
- Active-project reset while retaining its shell
- Active-project deletion
- Complete local Lab factory reset

The interface calculates the selected project-record count before deletion. Destructive actions require the user to type `RESET`. A backup can be downloaded first. The deletion receipt stores only scope, version, counts, timestamp, and whether a backup was requested; it does not retain deleted scientific content.
