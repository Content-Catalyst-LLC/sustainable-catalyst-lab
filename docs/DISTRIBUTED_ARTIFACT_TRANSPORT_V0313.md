# Distributed Artifact, Result, and Checkpoint Transport v0.31.3

Sustainable Catalyst Lab v0.31.3 adds a governed transport layer between the Python coordinator and secure pull-based workers. The transport is designed for scientific inputs, large compute results, long-running-job checkpoints, logs, reports, datasets, and provenance records that should not be embedded directly in queue or completion JSON.

## Storage architecture

- SQLite WAL metadata and event index
- SHA-256 content-addressed filesystem blobs
- Atomic finalization from private temporary upload files
- Deduplication within project and artifact kind
- Bounded artifact sizes and bounded chunk sizes
- Upload expiration and artifact retention controls

The default Render blueprint keeps artifacts under `/app/data` but reports them as instance-local until a persistent disk is explicitly mounted. No paid disk is required by the release.

## Upload protocol

1. Create an upload session with kind, filename, media type, expected size, expected SHA-256, and provenance metadata.
2. Send sequential chunks using the exact `nextOffset` returned by the coordinator.
3. Optionally verify every chunk with `X-SC-Lab-Chunk-SHA256`.
4. Finalize the session.
5. The coordinator verifies the complete size and SHA-256, moves the content into the content-addressed store, and returns an artifact record.

Offset conflicts are rejected without corrupting the session. Final hash or size failures quarantine the upload rather than publishing it.

## Worker security

Workers authenticate with their worker-scoped credential. A worker may upload artifacts under its own identity. A worker may download a coordinator-owned input artifact only when that artifact is referenced by a workload currently leased to the worker. Releasing, completing, or expiring the lease removes that access path.

Artifact references do not permit arbitrary URLs, callbacks, executable code, serialized Python objects, or shell commands.

## Input materialization

A workload may contain `artifactInputs` records with:

- `artifactId`
- `inputKey`
- `format`: `json`, `text`, or `binary-base64`
- optional expected `sha256`

The worker downloads and verifies each artifact, decodes it according to the governed format, and merges it into the registered compute request inputs. The original signed contract remains the authority for the references.

## Result externalization

When a worker result exceeds `SC_LAB_WORKER_RESULT_ARTIFACT_THRESHOLD_BYTES`, the agent serializes the result as canonical JSON, uploads it through the resumable transport, and replaces the inline result with an artifact reference. The completion receipt retains the original result hash plus artifact ID, SHA-256, size, media type, queue ID, contract ID, worker ID, method, and receipt provenance.

## Checkpoints and other artifacts

The same transport accepts `checkpoint`, `input`, `result`, `log`, `report`, `dataset`, and `provenance` kinds. This establishes the storage and transfer contract needed for later workflow orchestration and partial-recovery releases without coupling the transport to one numerical method.
