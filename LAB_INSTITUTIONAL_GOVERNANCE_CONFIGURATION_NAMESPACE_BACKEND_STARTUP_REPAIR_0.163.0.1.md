# Institutional Governance Configuration Namespace & Backend Startup Repair — v0.163.0.1

The v0.163.0 Institutional Research Governance & Review Federation remains the active feature. This patch isolates its backend configuration from the older Lab institutional-governance subsystem.

The federation now uses `SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_*`. The legacy subsystem continues to use `SC_LAB_INSTITUTIONAL_GOVERNANCE_*`. No database is shared between the two managers by default.

The patch does not alter reviewer-selection policy, ethics authority, scientific-validity semantics, resource/funding authority, execution authority, or publication authority. Existing human-control boundaries remain intact.
