# Lab v0.157.0 — Cross-Study Replication & Meta-Experiment Workspace

The v0.157.0 workspace treats replication as a structured relationship between versioned studies rather than a binary automated label. Each study can carry provenance references to publications, protocols, campaigns, and parent studies. Effect records are immutable and preserve extraction source, effect measure, uncertainty, sample size, units, and harmonization references.

Meta-experiment workspaces define a question, primary metric/effect measure, inclusion/exclusion criteria, hypothesis, and analysis plan. Study membership records the replication relationship and inclusion state. A workspace can be frozen to preserve the planned synthesis set.

The synthesis runtime performs transparent inverse-variance fixed-effect and DerSimonian-Laird random-effects summaries from supplied effect estimates and variances. It reports Q, I², τ², approximate 95% confidence/prediction intervals, study contributions, direction counts, and leave-one-out sensitivity. These outputs remain descriptive scientific evidence; interpretation is not automated.

Explicit reviewer assessments may be recorded as unreviewed, consistent, inconsistent, mixed, or not-assessable, always with human rationale for substantive judgments. A replication-campaign handoff can draft a v0.155.0 repeated-trial campaign, but campaign creation and execution are never automatic.
