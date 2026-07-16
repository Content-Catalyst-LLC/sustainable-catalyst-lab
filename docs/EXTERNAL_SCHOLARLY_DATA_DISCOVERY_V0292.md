# External Scholarly and Data Discovery — v0.29.2

This release adds allowlisted scholarly metadata discovery over Crossref, OpenAlex, and DataCite, with WorldCat, Google Scholar, DOI, and institutional OpenURL handoffs. Results are normalized, deduplicated, and imported as project-scoped `researchSources` records.

## Security boundary

- No arbitrary URL fetching.
- No Google Scholar scraping.
- WorldCat remains a catalog handoff unless institutional OCLC access is configured.
- Provider results are bounded to 25 per provider and 5 MB per response.
- Imported records retain provider IDs, fingerprints, access status, licenses, citations, and retrieval timestamps.

## Environment variables

- `SC_LAB_DISCOVERY_CONTACT_EMAIL` identifies Crossref/DataCite requests.
- `SC_LAB_OPENALEX_API_KEY` enables OpenAlex live search and DOI access lookup.
- `SC_LAB_OCLC_ACCESS_TOKEN` records institutional OCLC configuration; v0.29.2 does not enable unrestricted WorldCat API fetching.
- `SC_LAB_OPENURL_RESOLVER_BASE` enables server-generated institutional OpenURL links.
- `SC_LAB_DISCOVERY_TIMEOUT_SECONDS` controls provider timeout.
- `SC_LAB_DISCOVERY_MAX_RESULTS` caps results per provider.
