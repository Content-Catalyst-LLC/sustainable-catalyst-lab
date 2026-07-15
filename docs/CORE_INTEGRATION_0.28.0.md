# Core integration — Research Lab v0.28.0

Recommended Core: v2.8.0.

The WordPress plugin proxies public Core endpoints server-side so the browser never receives the Core API key. Supported public Core surfaces include science records, scientific assets, time series, GeoJSON features, and STAC search.

The bridge strips credential-like fields, removes URL query strings, bounds response depth and item counts, applies short-lived WordPress transients, and reports unavailable instead of inventing records.

Workbench handoffs use `sc-lab-workbench-handoff/1.0`. Notebook exports use `sc-lab-notebook/1.0` and reference environment variables rather than embedding credentials.
