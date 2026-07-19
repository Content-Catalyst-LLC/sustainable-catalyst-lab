# Sustainable Catalyst Lab v0.38.1 Release Notes

## Typed Cross-Product Research Handoffs

v0.38.1 converts the generic v0.38.0 interoperability layer into operational, product-aware research handoffs. The release adds executable adapters for 13 products, deterministic route planning, contract inference, target bindings, dry-run validation, route and plan hashes, and governed handoff creation.

### Product adapters

Sustainable Catalyst Lab, Decision Studio, Catalyst Data, Catalyst AnalyticsR, Catalyst Canvas, Sustainable Catalyst Workbench, Site Intelligence, Knowledge Library, Research Librarian, Catalyst Finance, Catalyst Grit, Catalyst Narrative Risk, and Global Impact Catalyst.

### Safety boundary

Adapters run locally and prepare metadata-only governed envelopes. They do not execute arbitrary code, call remote callbacks, transmit credentials, or embed restricted dataset bytes. Persistence, workspace authorization, hashing, sealing, receipts, and immutable history continue to be enforced by the v0.38.0 interoperability engine.
