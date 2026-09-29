# Sustainable Catalyst Lab v0.141.7 — Embedding Explorer

## Purpose

Embedding Explorer is the research-facing inspection layer for vector representations produced by Sustainable Catalyst neural workflows. It lets Lab organize, compare, audit, and visualize embedding spaces while preserving the Platform Core → Workspace → Lab architecture: Core defines governed objects, Workspace performs extraction/projection execution, and Lab performs research inspection and interpretation.

## Capabilities

- Governed embedding study specifications linked to experiment, model, checkpoint, layer, dataset, split, and environment references.
- Normalized embedding-vector records with immutable vector fingerprints and explicit extraction/normalization metadata.
- Dimension-consistency and provenance audits before distance or neighborhood analysis.
- Explicit cosine, Euclidean, Manhattan, or dot-product geometry; the metric is never silently inferred.
- Nearest-neighbor queries with a strict rule that proximity does not establish semantic, causal, evidentiary, or real-world relationships.
- Imported projection registries for PCA, t-SNE, UMAP, PaCMAP, random projection, user-supplied, and extensible methods.
- Projection audits that preserve method, parameters, seed, source set, and provenance, and label 2D/3D coordinates as derived representations.
- Cluster and label overlays without automatic interpretation of cluster meaning.
- Embedding drift and space-comparison summaries without inferring the cause or meaning of movement.
- Platform Core visual-object handoff, deterministic snapshots, export bundles, and reproducibility packages.

## Epistemic boundary

Embedding geometry is a model-derived analytical representation. A nearest neighbor is not evidence of a real-world relationship. Cluster membership is not a semantic fact. A projected 2D/3D layout is a derived view and is not certified as preserving the full high-dimensional geometry. Reproducing an embedding analysis does not certify the model, the embedding, or an interpretation as scientifically valid.

## Execution authority

Workspace remains authoritative for model execution, embedding extraction, and dimensionality-reduction jobs. Lab can calculate transparent descriptive distances over returned vectors, but it does not perform the underlying model inference or silently generate dimensionality-reduction results.
