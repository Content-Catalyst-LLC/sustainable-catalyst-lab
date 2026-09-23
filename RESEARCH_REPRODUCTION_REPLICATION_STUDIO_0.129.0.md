# Sustainable Catalyst Lab v0.129.0 — Research Reproduction & Replication Studio

## Purpose
v0.129.0 turns Lab's existing reproducibility, provenance, execution-lineage, model-package, investigation-package, publication, and Platform Core integration capabilities into a dedicated research reproduction and replication workflow.

## Distinction
- **Reproduction**: reconstruct the original analysis as closely as possible from declared data, environment, methods, parameters, random seeds, figures, and execution artifacts.
- **Replication**: independently test a declared research claim with an explicitly documented relationship to the original population, data, method, and analysis plan.

Neither path automatically confirms or falsifies a scientific claim.

## Method families
1. Artifact inventory
2. Input integrity
3. Environment locking
4. Method reconstruction
5. Execution reproduction
6. Output comparison
7. Numerical tolerance
8. Figure reproduction
9. Provenance reconstruction
10. Deviation register
11. Replication protocol
12. Independent replication
13. Claim linkage
14. Reproducibility matrix
15. Package assembly

## Research controls
The Studio records artifact hashes, environment locks, dependency references, method steps, parameters, seeds, output tolerances, deviations, execution lineage, claim/evidence links, and package identity. Tolerances are researcher-declared; they are never optimized after seeing the result.

## Boundaries
A successful rerun means only that the declared computational reconstruction completed and produced the recorded comparison outcome. Numerical agreement does not establish scientific truth. A replication result is recorded without automatic success/failure labels, evidentiary weighting, claim-state mutation, causal interpretation, scientific-validity certification, or Core submission.
