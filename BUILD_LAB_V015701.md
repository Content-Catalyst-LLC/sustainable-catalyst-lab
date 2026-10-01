# Sustainable Catalyst Lab v0.157.0.1

## Canonical Release Identity, Front-Door Synchronization & Workspace Authorization Repair

This repair release corrects the Lab page presentation observed after v0.157.0: the canonical runtime reached v0.157.0 while stale global page/card and application-shell labels could still present v0.154.0, and logged-out server-backed project panels surfaced raw WordPress authorization errors.

### Repairs
- Canonical release identity is v0.157.0.1; feature identity remains v0.157.0.
- The Lab application shell, public Lab card, release console and canonical-runtime label are synchronized to the canonical release at runtime.
- Feature-introduction labels remain historically accurate: 4D workspace v0.153.0, Protocol + Notebook v0.154.0, Batch Campaigns v0.155.0, Distributed/HPC v0.156.0, Cross-Study v0.157.0.
- Logged-out visitors no longer receive raw `Sorry, you are not allowed to do that.` messages from protected project routes. The UI presents an explicit sign-in requirement instead.
- Protected project REST permissions are not relaxed and private project data is not exposed publicly.
- The v0.157.0 cross-study fetch helper explicitly preserves same-origin WordPress credentials.
- Backend artifacts are included and synchronized; scientific backend behavior remains v0.157.0.

### Architecture
The repair does not change scientific calculations, study synthesis, HPC coordination, campaign orchestration or provenance semantics.
