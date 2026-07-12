# Sustainable Catalyst Lab Compute and Report Service v0.9.4

This FastAPI service executes only curated, versioned method contracts and generates validated scientific reports. Requests can provide an allowlisted method identifier, language identifier, numerical inputs, or a bounded structured report contract. The API does not accept arbitrary source code, shell commands, unrestricted SQL, filesystem paths, or package installation requests.

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
POST   /v1/reports/validate
POST   /v1/reports/pdf
POST   /v1/handoffs/decision-studio/validate
```

## Report service

The report service validates `sc-lab-report/1.0` payloads and generates text-selectable vector PDFs with ReportLab. It supports LETTER and A4 output and the following report types:

```text
technical-report
decision-brief
evidence-packet
executive-summary
```

A report can contain one to twelve analyses. The service limits text, table rows, payload size, nesting depth, and total response size. The returned JSON includes the base64 PDF, byte length, page count, report fingerprint, PDF fingerprint, filename, and engine metadata.

Decision Studio validation accepts `scientific-analysis` and `scientific-report` packets and returns a deterministic packet fingerprint plus chart, scene, table, and analysis counts.

## Native worker languages

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

R, Julia, SQL, and Haskell remain source-generation targets until dedicated workers are added.

## Local development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
PYTHONPATH=. uvicorn app.main:app --reload
```

Without `REDIS_URL`, asynchronous jobs use a bounded in-memory thread pool. The Render Blueprint provisions a Key Value queue and a separate RQ worker.

## Security and audit boundary

- Curated method allowlist
- Strict Pydantic request models
- Numerical input validation from method contracts
- Bounded report and handoff payloads
- Per-IP rate limiting
- Compile, execution, and proxy timeouts
- Temporary isolated working directories
- Restricted subprocess environment
- Output-size limits
- Thread-safe subprocess launch
- Optional GNU `prlimit` wrapper on Linux
- No arbitrary source or shell endpoint
- Optional shared API key in `X-SC-Lab-Key`
- Report, analysis, packet, input, output, and PDF fingerprints

Render container limits remain the primary production resource boundary.
