# Secure Worker Agent v0.31.3

The worker agent enrolls with a coordinator, stores its returned worker credential in a mode-0600 local file, polls for compatible leases, verifies each signed dispatch contract, executes only methods registered in the Lab Python Compute Core, renews active leases, and submits provenance-bearing completion receipts.

## Start locally

```bash
cd backend
cp examples/worker-agent/sc-lab-worker-agent.env.example .worker-agent.env
set -a; source .worker-agent.env; set +a
python3 -m worker_agent --validate-config
python3 -m worker_agent
```

Use `python3 -m worker_agent --once` for a single poll-and-execute cycle. Use `--rotate-credential` to replace the locally stored worker credential after authenticating with the current credential.

The contract verification secret must match `SC_LAB_DISPATCHER_CONTRACT_SECRET` on the coordinator. The enrollment token must match `SC_LAB_WORKER_ENROLLMENT_TOKEN`. Never place either secret in WordPress, browser JavaScript, a public repository, or a dispatch workload.

## Artifact transport

The v0.31.3 agent downloads lease-granted input artifacts with SHA-256 verification and uploads large results through resumable, content-addressed artifact sessions. Configure `SC_LAB_WORKER_ARTIFACT_CHUNK_BYTES` and `SC_LAB_WORKER_RESULT_ARTIFACT_THRESHOLD_BYTES` as needed.
