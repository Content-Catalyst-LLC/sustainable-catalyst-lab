# Sustainable Catalyst Lab Compute Dispatcher v0.9.3

This FastAPI service executes only curated, versioned method contracts from `backend/catalog/methods.json`. Requests provide a method identifier, language identifier, and numerical inputs. The API does not accept source code, shell commands, file paths, package names, or arbitrary SQL.

## Endpoints

```text
GET    /health
GET    /version
GET    /v1/methods
GET    /v1/languages
POST   /v1/validate
POST   /v1/execute
POST   /v1/compare
POST   /v1/jobs
GET    /v1/jobs/{job_id}
DELETE /v1/jobs/{job_id}
```

## Native worker languages in v0.9.3

```text
Python
JavaScript
TypeScript
C
C++
Fortran
Rust
Go
```

R, Julia, SQL, and Haskell remain source-generation targets in Code Studio. They are declared as source-only until dedicated workers and runtime validation are added.

## Local development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
PYTHONPATH=. uvicorn app.main:app --reload
```

Without `REDIS_URL`, asynchronous jobs use a bounded in-memory thread pool. The Render Blueprint provisions a Key Value queue and a separate RQ background worker.

## Security boundary

- Curated method allowlist
- Pydantic models with unknown fields rejected
- Numerical input validation from the method contract
- 64 KiB request and output limits
- Per-IP fixed-window rate limiting
- Compile and execution timeouts
- Temporary working directories
- Process, file, memory, CPU, and file-descriptor limits on POSIX workers
- Minimal subprocess environment
- No arbitrary source or shell execution endpoint
- Optional shared API key in `X-SC-Lab-Key`

Generated programs contain only constants, validated numerical inputs, mathematical expressions, and structured result output. Production deployment should still use the API key, a private queue, normal Render access controls, logs, and resource monitoring.
