# Exploratory Data Analysis Studio 0.120.0

## Purpose
Provide a reproducible, provenance-aware exploratory analysis environment that can inspect declared tabular research data without converting exploratory patterns into confirmatory scientific conclusions.

## Analysis families
- Dataset normalization and structural typing
- Numeric/categorical descriptive profiles
- Missingness and co-missingness structure
- Numeric and categorical distributions
- Pearson and Spearman association summaries (no p-values)
- Descriptive grouped summaries and two-group contrasts
- IQR, modified-z, and z-score outlier flagging without row deletion
- Pairwise relationship summaries and descriptive linear fit
- Explicit transformation plans and non-mutating previews
- PCA exploration with declared standardization and component count
- Visualization plans that reuse v0.114/v0.115/v0.116 visual systems
- Reproducible analysis snapshots and export plans
- Reference-first Platform Core artifact plans

## Scientific boundary
The EDA Studio is exploratory, not confirmatory. It does not automatically claim statistical significance, select hypotheses, infer causality, infer missingness mechanisms, exclude data, certify model quality/scientific validity, or determine truth.

## Data authority
Source rows are immutable in the EDA runtime. Transformations create previews with hashes and generated column names; source datasets remain authoritative.
