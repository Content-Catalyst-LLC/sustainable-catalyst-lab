# Release notes — Lab v0.141.7 Embedding Explorer

Lab v0.141.7 adds a governed Embedding Explorer over the v0.141.6 Neural Explainability Workspace. The release introduces embedding-study and vector records, distance and neighborhood analysis, projection registries and audits, cluster/label overlays, embedding drift and cross-space comparison, provenance matrices, visual specifications, Platform Core handoff, deterministic snapshots, exports, and reproducibility packages.

The release keeps Workspace as the execution authority for embedding extraction and dimensionality reduction. Lab records and analyzes returned vector/projection objects. Distance metric, model/checkpoint/layer, source dataset/split, extraction configuration, normalization, projection method, parameters, and seed remain explicit.

Scientific guardrails are first-class: embedding proximity is not evidence of a real-world relationship; cluster membership is not semantic truth; projected geometry is a derived representation; projection faithfulness is not automatically certified; and no embedding result automatically endorses a model.
