# Scientific Artifact Repository and Data Federation v0.36.0

Sustainable Catalyst Lab v0.36.0 introduces a governed repository for scientific artifacts and a manifest-based federation layer for sharing versioned research records across institutional nodes.

## Architecture

The release separates three responsibilities:

1. **Artifact transport** retains content-addressed binary objects and verifies their bytes.
2. **Scientific artifact repository** records versioned scientific meaning, provenance, canonical identifiers, collections, and workspace access.
3. **Data federation** exchanges canonical manifests supplied through authenticated operations without opening arbitrary remote callbacks.

Repository records may reference an existing transport artifact or represent a verified remote artifact whose content remains at another institution. Every record has a stable record hash, version, integrity state, provenance object, and canonical URI.

## Workspace governance

Collections and federation sources belong to a v0.35.x shared research workspace. The existing workspace roles govern repository actions:

- viewers and reviewers may inspect collections, manifests, synchronization history, and timelines;
- contributors may register artifacts and run approved manifest synchronization;
- editors, administrators, and owners may resolve federation conflicts;
- administrators and owners may register federation sources and archive collections.

The backend performs all role decisions independently of the WordPress interface.

## Collections and artifact versions

Collections provide durable scientific groupings for datasets, results, figures, reports, checkpoints, models, evidence, and other registered artifact types. Artifact versions are immutable repository records. Re-registering the same canonical identity and record hash is idempotent rather than duplicative.

A transport-backed record can be verified against the existing content-addressed artifact store. The resulting verification record includes a SHA-256 verification hash.

## Federation protocol

Federation uses canonical JSON manifests with:

- node and collection identities;
- cursor and generation timestamps;
- artifact versions, SHA-256 hashes, sizes, media types, canonical URIs, status, provenance, and metadata;
- a manifest SHA-256 hash calculated over the canonical manifest body.

Supported trust modes are `strict`, `hash-verified`, and `manual-review`. Supported conflict policies are `reject`, `retain-both`, and `prefer-newer`.

The coordinator does not crawl remote systems or execute callback URLs. An authenticated operator or separately governed connector supplies the remote manifest to the synchronization route.

## Synchronization and conflict handling

Synchronization is durable and idempotent. It records imports, updates, unchanged records, tombstones, conflicts, cursors, manifest hashes, and run hashes. A remote tombstone marks the federated record as tombstoned without silently erasing history.

Conflicts preserve the incoming record and local identity. Authorized operators can:

- keep the local record;
- accept the remote record;
- retain both versions under distinct canonical identities;
- dismiss the conflict while retaining the record of the decision.

Every resolution is recorded in the repository timeline.

## Persistence and deployment

The repository uses SQLite WAL. `SC_LAB_ARTIFACT_REPOSITORY_DB_PATH` controls the database path. `SC_LAB_ARTIFACT_REPOSITORY_PERSISTENT_DISK_MOUNTED` reports whether deployment persistence has been explicitly configured. A paid disk remains optional; the health response distinguishes instance-local from persistent storage.

## Safety boundary

v0.36.0 does not execute arbitrary code, shell commands, executable expressions, remote callbacks, or untrusted device instructions. Federation exchanges records and integrity metadata only. Existing worker, dispatcher, workflow, review, and workspace controls remain in force.
