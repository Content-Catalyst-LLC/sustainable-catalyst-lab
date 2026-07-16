# Secure Worker Agent Runtime and Pull-Based Execution v0.31.2

Sustainable Catalyst Lab v0.31.2 converts the distributed dispatcher and persistent queue into an end-to-end execution system. A worker node can enroll with the coordinator, pull a compatible lease, verify the signed contract locally, execute only a registered Lab method, renew the lease while work is active, and return an idempotent result receipt.

## Architecture

The coordinator remains the source of truth for workers, queue items, contracts, leases, credentials, and terminal results. Workers initiate all network traffic. No inbound callback endpoint, arbitrary callback URL, shell command, source-code payload, dynamic import, or unregistered method is accepted.

Each enrolled worker receives a one-time credential. The coordinator stores only its SHA-256 digest. The credential is bound to the worker identifier and gates heartbeat, claim, acknowledgement, renewal, release, completion, and credential rotation routes. An administrator can revoke a worker, which also quarantines its registry record.

The contract signature is verified by the worker before execution. Verification binds the worker identifier, contract identifier, lease identifier, workload, method, issuance time, and expiration. The worker then converts the governed workload into the existing `ComputeRequest` model and resolves it through the registered Python Compute Core method registry.

## Coordinator configuration

Required production variables:

```text
SC_LAB_DISPATCHER_CONTRACT_SECRET=<strong-random-secret>
SC_LAB_WORKER_ENROLLMENT_TOKEN=<strong-random-token>
SC_LAB_DISPATCHER_DB_PATH=/app/data/sc-lab-dispatcher.sqlite3
```

`SC_LAB_DISPATCHER_CONTRACT_SECRET` must also be supplied to trusted worker nodes as `SC_LAB_WORKER_CONTRACT_SECRET`. `SC_LAB_WORKER_ENROLLMENT_TOKEN` is used only for first enrollment and can be removed from a worker after its credential has been stored.

Open enrollment is disabled in production unless `SC_LAB_ALLOW_OPEN_WORKER_ENROLLMENT=1` is explicitly set. That override is intended only for controlled development environments.

## Starting a worker

From the backend directory:

```bash
cp examples/worker-agent/sc-lab-worker-agent.env.example .worker-agent.env
# Edit the coordinator URL, enrollment token, and contract secret.
set -a
source .worker-agent.env
set +a
python3 -m worker_agent --validate-config
python3 -m worker_agent
```

Useful commands:

```bash
python3 -m worker_agent --print-capabilities
python3 -m worker_agent --once
python3 -m worker_agent --rotate-credential
```

Linux systemd and macOS launchd examples are provided under `backend/examples/worker-agent/`.

## Worker lifecycle

1. Enroll and securely store the one-time credential with file mode `0600`.
2. Send an authenticated heartbeat and capability profile.
3. Pull a compatible workload lease.
4. Verify the signed contract locally and acknowledge it.
5. Execute the registered method through the governed Compute Core.
6. Renew the lease automatically during long execution.
7. Submit a terminal execution receipt or release the lease according to retryability.
8. Continue polling until stopped, then report a draining state.

## Completion receipts

Receipts use `sc-lab-worker-execution-receipt/0.31.2` and include:

- worker, contract, lease, queue, workload, method, and method-version identifiers;
- start and completion timestamps and elapsed milliseconds;
- Python and platform runtime metadata;
- the governed `ComputeResponse` including provenance;
- a deterministic result hash and receipt hash.

Coordinator completion is idempotent. Repeating the same terminal receipt returns the recorded contract. A conflicting receipt for an already completed contract is rejected.

## Deployment durability

The default Render blueprint writes dispatcher and job databases under `/app/data`, but no paid persistent disk is forced. Health reports distinguish an instance-local filesystem from a mounted persistent disk. Queue records survive process restarts on the same instance; survival across instance replacement requires a persistent disk or an external durable database.

A non-invasive disk configuration example is provided in `backend/render-persistent-disk-snippet.yaml.example`.

## WordPress operations workspace

The new **Secure worker agents** panel exposes coordinator health, enrollment and contract-secret readiness, credential counts, worker inventory, runtime policy output, and startup instructions. It does not expose credential values.
