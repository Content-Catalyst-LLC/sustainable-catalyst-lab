# Scientific Source Registry

The initial Lab source layer uses official or primary scientific services:

- USGS FDSN Event Web Service for parameterized earthquake records.
- NASA EONET v3 for curated near-real-time natural-event metadata.
- NASA Global Imagery Browse Services for standards-based Earth imagery.
- NASA Image and Video Library for public astronomy and mission media records.
- Ocean Biodiversity Information System API v3 for marine occurrence records.
- NCBI E-utilities for PubMed search and summary metadata.
- arXiv public Atom API for physics, astronomy, materials, and engineering preprints.

Each normalized record includes source, domain, observation or publication time where supplied, retrieval time, original URL, provenance, and location data where available. WordPress transient caching reduces repeated upstream requests.

Source records are evidence candidates, not automatically validated conclusions. Users should inspect the original record, methods, uncertainty, revisions, and source-specific limitations before relying on a record in analysis or documentation.
