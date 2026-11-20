# EPA soil carbon importer

SC-RVF-01 starts with a native producer inside Lab's existing visualization API. Master issue: https://github.com/Content-Catalyst-LLC/ucd-sustainable-development-research/issues/2

The original publisher PDF snapshot and acknowledgment are in backend/app/publisher_sources. The importer verifies its pinned SHA256 and emits the existing sc-lab-scientific-visualization/1.0 grammar. It selects the Table 2.4 non-peat Grassland + Rough grazing (average) and Arable lands columns, preserving t C/ha, standard errors and overlapping cumulative depths. No field data or CO2 removal is inferred. Human extraction review is pending; Library/Core registration fields stay null.

## Existing API

POST /v1/visualization/spec with the normal existing compute authentication and body:

```json
{"publisherSource":{"id":"epa-136-table-2.4","pdf_sha256":"9cc7ef390d6b19bd4d1a89d3b1d9c9d8c1c81e1adf8e40b6c4267d4fb93ae27a"}}
```

The API selects only the packaged publisher snapshot, preserving the existing request-size limit. Changed PDF bytes, unsupported source IDs/hashes and value/semantic overrides are rejected. POST /v1/visualization/csv accepts the same request and returns the categorical table with SE values. No endpoint or authentication dependency was replaced. This importer does not retrieve arbitrary URLs or write project storage.

## Reproduce locally

```sh
PYTHONPATH=backend python backend/scripts/import_epa_soil_carbon.py backend/app/publisher_sources/epa-report-136.pdf figure.json
PYTHONPATH=backend python -m pytest -o addopts='' -q backend/tests/test_publisher_soil_carbon.py backend/tests/test_scientific_visualization_v0274.py
npm ci --prefix tests/renderer --ignore-scripts
node --test tests/sc-rvf-native-heatmap.cjs
```

Load figure.json in the existing Lab renderer or stage it with Workspace's existing private project uploader. The receiving Workspace SC-RVF branch extends its existing Lab heatmap adapter; choose t C/ha, modeled classification, record citation/rights and reproduction references, preview, then save a reporting revision. Exported Word includes an editable data table and exact source JSON/SVG attachments; PDF/PNG/SVG/CSV retain source values. This is manual file-mediated handoff, not an authenticated live service-to-service integration.

The existing native v0440 renderer now supports category ticks, SE labels, keyboard/pointer inspection, source metadata, overlap warning, accessible table and SVG/PNG/CSV/JSON exports. Ordinal zoom is disabled. No new plotting engine, report application, database or production deployment is introduced. Other newer Lab renderer paths have not been certified for these extensions.

## Remaining integration

Persist the source through Library's actual owned artifact/source services and register real Core source/figure identity/version/permissions; wire the existing Lab project/vault picker to this importer; connect Workbench and Decision Studio using their existing contracts. The current importer deliberately cannot claim completion of those operations. Staging, real-account browser/SSO, durable cross-product references and private-paper visual parity remain acceptance gates.
