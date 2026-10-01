# Lab v0.163.1 — Unified Workspace Shell & Progressive Module Navigation

This release converts the accumulated Lab specialist workspaces from one long vertical page into a unified application shell with progressive navigation.

## User-interface changes
- Overview landing surface inside the Lab application shell.
- Collapsible desktop workspace rail and responsive horizontal navigation on smaller screens.
- One specialist workspace visible at a time; inactive modules preserve state without contributing page height.
- Workspace search/filter and session-level active-workspace preservation.
- Existing v0.153–v0.163 specialist modules remain intact and are moved into a managed stage rather than rewritten.
- Repeated module boundary text is consolidated into a contextual **Methods & governance** drawer.
- Mutation-observer registration captures modules that initialize after the shell.

## Backend
The backend is included and synchronized in this release. Scientific compute behavior is unchanged. `/health` advertises the v0.163.1 workspace-shell release marker while retaining v0.163.0 governance and the v0.163.0.1 startup repair.

## Authority boundaries
Platform Core remains canonical object authority. Workspace remains execution authority. Research OS remains project-lifecycle authority. The shell changes navigation and presentation only; it does not automate scientific judgment, execution, review, publication, prioritization, or resource allocation.
