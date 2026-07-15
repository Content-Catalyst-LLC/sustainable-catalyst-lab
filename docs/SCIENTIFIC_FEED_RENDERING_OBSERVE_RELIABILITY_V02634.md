# Scientific Feed Rendering and Observe Data Reliability — v0.26.3.4

This release prevents the Marine Biology and Space Observations panels from rendering as blank regions. Each panel automatically performs an initial query, renders a loading skeleton immediately, and reports whether data came through the WordPress proxy or a browser-direct official source request.

## Source order

1. WordPress REST proxy and transient cache
2. Browser-direct NASA Image Library or OBIS request
3. Explicit diagnostic state with retry and source endpoint links

No source failure is silently converted into an empty panel.
