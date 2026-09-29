# Lab v0.146.0 — Graph & Network Science Research Workspace

## Purpose
Provides a governed research workspace for classical graph and network science: graph construction and provenance, structural summaries, connectivity, paths/distances, centrality, communities, clustering, motifs, core/periphery, rich-club, flow/cuts, bridges/articulation, bipartite, temporal, multilayer/multiplex networks, null models, network comparison, sensitivity, uncertainty, visualization and reproducibility.

## Architecture
Platform Core defines canonical graph/network objects. Workspace executes large or expensive graph algorithms. Workbench supports prototypes. Research Lab governs study design, returned analysis objects, comparison, interpretation, review, visualization and reproducibility. Graph Studio provides interactive graph visualization surfaces.

## Scientific boundaries
- An edge means only the relationship semantics declared by its source.
- Similarity/correlation/candidate edges are not established relationships.
- Connectivity is not causality.
- Centrality is not universal substantive importance.
- Community detection is not ground-truth grouping.
- Motif or null-model enrichment is not a demonstrated mechanism.
- A graph metric is not evidence by itself.
- Reproducibility does not certify scientific validity.

## Roadmap boundary
v0.146.0 covers classical graph/network science. Learned graph representations, node/edge classification, link prediction and GNN workflows remain in the planned v0.147.0 Graph Machine Learning Experiment Workspace.
