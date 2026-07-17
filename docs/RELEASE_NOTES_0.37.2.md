# Sustainable Catalyst Lab v0.37.2 Release Notes

## Public Reproduction and Verification Portal

Sustainable Catalyst Lab v0.37.2 extends the publication and manuscript system with a safe public verification surface for independently checking published research packages.

### New capabilities

- Public, immutable reproduction records derived only from published research and sealed packages.
- Safe snapshots that exclude private workspace data, credentials, executable code, callbacks, and restricted dataset bytes.
- Public verification manifests with stable SHA-256 identities.
- Nonce-bound, expiring reproduction challenges.
- Independent evidence submission for publication, package, assembly, resource, environment, and result hashes.
- Immutable successful and failed verification receipts.
- Optional HMAC-SHA256 receipt signatures.
- Receipt integrity verification and retained withdrawal tombstones.
- Workspace-governed publishing and challenge-history review.
- New Public Reproduction & Verification Portal WordPress workspace.

### Safety boundary

The public portal never executes submitted code, exposes private workspace resources, distributes restricted data, or accepts unrestricted callbacks. Verification compares canonical identities and retained evidence only.
