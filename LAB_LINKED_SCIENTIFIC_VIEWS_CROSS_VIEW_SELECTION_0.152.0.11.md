# Sustainable Catalyst Lab v0.152.0.11

## Linked Scientific Views & Cross-View Selection

v0.152.0.11 extends the stabilized 4D scientific front door with a shared, provenance-preserving selection state across the response surface, parameter snapshot, Monte Carlo uncertainty diagnostic, local-sensitivity diagnostic, seed-replication ensemble diagnostic, and selection inspector.

### Core behavior

- Clicking the 4D response surface creates a `sc-lab-linked-selection/1.0` object with model identity, X/Y/W axis values, Z response, fixed parameters, grid indices, release version, and timestamp.
- Clicking the uncertainty, sensitivity, or ensemble diagnostic creates a diagnostic-specific selection that retains its own model identity.
- Every selection is emitted as `sc-lab:linked-selection`, rendered in the shared inspector, and retained in a bounded 12-entry browser history.
- Up to eight selections can be pinned for comparison.
- A selected state can be exported as JSON or handed to Graph Studio through a `sc-lab-graph-studio-selection-handoff/1.0` session packet.
- Reopening a historical 4D selection restores its W hyperslice before redrawing the surface marker.

### Scientific boundary

Cross-view linkage is an inspection and provenance mechanism. A selection in one scientific model or diagnostic is not automatically equivalent to a point in another model. Linking views does not establish causality, evidence, statistical significance, calibration, forecast skill, or scientific validity.

### Runtime architecture

The release retains the bounded safe shell and does not restore the historical eager module fleet. Compute remains explicit user action; v0.152.0.11 adds no backend scientific methods and changes no backend behavior.
