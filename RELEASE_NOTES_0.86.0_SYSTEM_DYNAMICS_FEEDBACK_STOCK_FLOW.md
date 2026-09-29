# Sustainable Catalyst Lab v0.86.0 — System Dynamics, Feedback Loops & Stock-Flow Modeling

## Purpose

v0.86.0 adds a governed Meadows-style systems modeling layer to Lab while preserving the v0.85 WebGL2 visualization engine.

## Capabilities

- Explicit causal-loop diagrams with positive/negative polarity and declared delays.
- Reinforcing and balancing feedback-loop detection from declared structure.
- Stock-flow models with stocks, flows, parameters and auxiliary variables.
- Safe scientific equation evaluation; no arbitrary Python or user executable code.
- Euler and fourth-order Runge-Kutta integration.
- Scenario parameter overrides without changing the authoritative model definition.
- Structural leverage indicators based on degree, feedback-loop participation and delay connections.
- Governed Graph Studio handoff and provenance fingerprints.

## Scientific boundaries

Lab does not infer causal links, generate equations automatically, rank Meadows leverage points normatively, infer paradigms, hide delays, clamp stocks silently, convert units automatically, or execute arbitrary code. Structural leverage indicators are descriptive model diagnostics, not policy recommendations.

## Compatibility

The v0.85.0 WebGL2 Scientific Renderer remains Visualization Engine 2.12.0. v0.86.0 adds System Dynamics Engine 1.0.0 as a separate component and preserves the canonical public Lab release identity.
