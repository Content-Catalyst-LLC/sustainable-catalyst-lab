# Sustainable Catalyst Lab v0.132.0 — Method Selection Intelligence

## Purpose

Method Selection Intelligence connects structured research questions and hypotheses to candidate analytical and experimental methods without making the scientific decision for the researcher. It evaluates declared compatibility across estimands, data types, study designs, sample structure, temporal/spatial structure, assumptions, uncertainty requirements, diagnostics, and validation needs.

## Core behavior

- Transparent candidate construction across 20 built-in cross-Lab method definitions.
- States: `eligible`, `needs-information`, and `incompatible`; each state carries explicit reasons.
- No numeric ranking or automatic winner. Input order and plausible alternatives remain visible.
- Explicit data, estimand, design, sample, temporal/spatial, and uncertainty profiles.
- Requirement-gap and assumption matrices.
- Estimand/data/design alignment reports.
- Diagnostic, sensitivity, validation, and pre-analysis plans.
- Researcher-declared shortlist and method-decision records.
- Reference-first handoff to downstream Lab products and Platform Core.
- Deterministic snapshots, revision plans, provenance, project/session bindings, and exports.

## Scientific boundaries

An `eligible` method is not automatically valid, and an `incompatible` catalog state is not a proof that a method can never be used. Scientific appropriateness remains context-dependent. The Studio does not automatically select or rank methods, satisfy assumptions, choose a hypothesis, infer causality, certify scientific validity, generalize results, determine truth, or submit objects to Platform Core.

## Platform boundary

Lab owns scientific method-selection workflow intelligence. Platform Core may receive reference-first governed research objects and lineage, but Core does not choose or execute the method through this contract.
