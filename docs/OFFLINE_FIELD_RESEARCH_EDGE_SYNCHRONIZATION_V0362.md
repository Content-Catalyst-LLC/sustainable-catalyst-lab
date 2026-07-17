# Offline Field Research and Edge Synchronization — v0.36.2

Sustainable Catalyst Lab v0.36.2 packages protocols, forms, registered method identifiers, artifact references, and policy constraints for disconnected field use. Edge devices synchronize signed change batches through resumable sessions when connectivity returns.

## Safety and privacy boundary

- Restricted institutional data bytes are not included in field packages.
- Device secrets are returned once and belong only in encrypted edge runtimes.
- Arbitrary code, shell commands, executable expressions, and callback URLs are rejected.
- Conflicts produce retained records and explicit resolutions rather than silent overwrites.
- Precise location capture is not required; projects may use coarse or no location metadata.
