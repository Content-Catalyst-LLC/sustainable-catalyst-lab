# Scientific Model Registry and Environment Reproduction — v0.34.0

Sustainable Catalyst Lab v0.34.0 adds a durable governance layer for scientific models, calibrated systems, surrogates, registered methods, and workflow-backed models.

## Registry model

Each model version is immutable and identified by:

- a stable model ID;
- a semantic model version;
- a canonical SHA-256 model hash;
- an exact reproduction-environment lock;
- declared input and output schemas;
- default inputs and governed parameters;
- source revision and artifact references;
- research provenance and metadata.

Changing model logic, dependencies, runtime, artifacts, parameters, or reproducibility metadata requires a new semantic version.

## Environment reproduction

Environment locks capture the runtime implementation and Python version, operating-system and machine information, container image and digest, dependency versions and optional package hashes, source revision, build identifier, and the names of environment variables required at execution time. Secret values are never stored.

The environment lock hash excludes transient capture timestamps and paths that do not affect scientific identity. This allows identical environments captured on different machines or at different times to deduplicate while retaining their complete capture records.

## Promotion and retirement

Versions begin in the `draft` channel. Operators may promote reviewed versions to `candidate`, `production`, or `archived` aliases. Deprecation requires a reason, removes aliases that point to the version, and preserves the full event history. Hard deletion is not exposed through the model-registry API.

## Reproduction manifests

Portable manifests contain the exact model hash, environment lock, artifacts, input schema and defaults, source revision, provenance, and execution constraints. Verification checks model identity, environment identity, source revision, artifact membership, and the manifest hash.

## Safety boundary

The registry stores declarative model metadata only. It does not accept arbitrary Python, shell commands, executable callbacks, or unregistered compute operations. Registered-method and workflow references remain subject to the existing Lab compute and workflow governance layers.


## Reference validation

Unknown registered compute methods and unknown saved workflows are rejected before validation or registration. Environment IDs are immutable and cannot be reused for a different dependency/runtime lock.
