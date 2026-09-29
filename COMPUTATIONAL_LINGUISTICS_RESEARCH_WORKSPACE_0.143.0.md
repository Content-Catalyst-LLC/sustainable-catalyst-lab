# Lab v0.143.0 — Computational Linguistics Research Workspace

## Purpose

Provide a reproducible research workspace for corpus linguistics, computational linguistics, multilingual and historical-language analysis without collapsing source text and derived representations.

## Architectural rule

**Original language first. Translation is a derived representation. Every transformation preserves lineage.**

Platform Core defines governed linguistic objects and exchange contracts. Workspace executes linguistic runtimes. Knowledge Library supplies source/document context and ingestion lineage. Research Lab structures experiments, compares analyses, visualizes linguistic objects, records limitations, and packages reproducible research.

## Governed objects

- original-language text objects with BCP 47 language identity and ISO 15924 script identity
- historical language, dialect, region, script and orthographic variants
- derived normalization, OCR/HTR, transcription, transliteration and translation representations
- token, lemma, morphology, POS, syntax, entity, semantic-role, coreference, phonetic/phonological and discourse annotations
- source/target alignment objects with explicit methods and provenance
- corpus definitions with sampling, selection criteria, rights and source references
- deterministic research-session snapshots and reproducibility packages

## Analysis surfaces

Corpus statistics, lexical profiles, n-grams, concordances, annotation matrices, supplied morphology/syntax/phonology/semantic summaries, corpus comparison, transformation lineage, alignment audit and cross-lingual comparison. Heavy linguistic computation remains in Workspace.

## Epistemic boundaries

- translation ≠ source text
- transliteration ≠ source text
- alignment ≠ semantic equivalence
- annotation ≠ ground truth
- corpus frequency ≠ interpretation
- embedding proximity ≠ relationship
- cross-lingual similarity ≠ evidence
- historical/script variation ≠ error
- language identity ≠ ethnicity
- reproducibility ≠ scientific validity
