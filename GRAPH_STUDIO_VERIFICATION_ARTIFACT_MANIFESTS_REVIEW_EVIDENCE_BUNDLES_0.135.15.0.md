# Graph Studio Verification Artifact Manifests & Review Evidence Bundles — v0.135.15.0

v0.135.15.0 extends the v0.135.14.0 review state machine without modifying its historical audit contract. The new layer records the concrete scientific artifacts inspected during a `verification-recorded` event and binds the audit event to a typed evidence bundle.

The principal relationship is:

`review annotation → v0.135.13 resolution action → v0.135.14 verification event → v0.135.15 verification artifact bundle`

The v0.135.14.0 audit event uses the v0.135.15.0 bundle ID as its `verificationRef`. The bundle then stores the corresponding `verificationEventId`, creating an explicit bidirectional reference at the application-contract level.

Supported artifact types are dataset, method, execution, figure, model, notebook, document, evidence-source, reproduction-result, code, environment, and other. Each artifact requires a stable artifact reference and may additionally record a title, version/revision reference, SHA-256 digest, source-object reference, execution reference, URI, media type, capture timestamp, and reviewer note.

Bundles are stored in the `graphStudioVerificationArtifactBundles` project collection and can contain up to 100 artifacts. Backend normalization, binding validation, manifest fingerprints, duplicate detection, bundle comparison, summaries, and Project Workspace packets are included.

A bundle documents what was inspected. A SHA-256 digest documents byte identity when supplied. A passing verification outcome records a review workflow result. None of those mechanisms independently establish scientific truth, causal validity, evidentiary weight, or a preferred interpretation.
