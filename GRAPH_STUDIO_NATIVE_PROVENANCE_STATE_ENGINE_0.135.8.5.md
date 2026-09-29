# Native provenance architecture — v0.135.8.5

Scientific/project objects → normalized ProvenanceGraph → single GraphStateController → Renderer 3.1 projection. The DOM is a projection of state, not the authority. Native traversal computes reachable subgraphs; layout is controller-owned; inspector derives from selected node/edge state; project presentation state persists layout/focus/filter/viewport separately from scientific records.
