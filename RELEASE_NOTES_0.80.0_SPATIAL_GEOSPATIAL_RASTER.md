# Sustainable Catalyst Lab v0.80.0 — Spatial, Geospatial & Raster Visualization

Visualization Engine 2 advances to **2.7.0** and adds the governed `canvas-spatial` renderer to Graph Studio. v0.80 visualizes explicit vector geometry and explicit raster grids inside a declared coordinate-reference system while preserving the linked-view/faceting/composition layer introduced in v0.79.

## Scientific visualization scope

v0.80 adds:

- declared coordinate-reference metadata and axis order;
- explicit viewport bounds;
- Point, MultiPoint, LineString, MultiLineString, Polygon, and MultiPolygon geometry;
- feature-level source indexes, properties, bounds, and fingerprints;
- explicit raster grids with dimensions, bounds, cell size, nodata handling, scalar statistics, and fingerprints;
- deterministic explicit bounding-box selection over supplied feature bounds;
- mixed vector + raster scientific figures;
- `canvas-spatial` alongside `svg2d`, `canvas3d`, and `canvas4d`;
- v0.79 linked-view compatibility so a spatial panel can participate in declared multi-view compositions.

## Governance boundary

Spatial display does not grant the visualization layer permission to alter spatial evidence. The release therefore keeps all of the following disabled:

- automatic CRS inference;
- automatic reprojection;
- automatic geocoding;
- automatic spatial joins;
- topology repair;
- raster interpolation;
- raster resampling;
- nodata imputation;
- network basemap fetching;
- WebGL claims;
- arbitrary code.

A figure containing layers with different declared CRS identifiers is rejected rather than silently transformed. Raster nodata remains nodata. Feature geometry is preserved as supplied. Bounding-box selection is an explicit intersection operation over stored feature bounds, not a statistical or causal spatial relationship.

## Compatibility

v0.80 preserves the complete visualization line:

- v0.79 Linked Views, Faceting & Figure Composition;
- v0.78 4D, Time & Parameter-Space Visualization;
- v0.77 3D Scientific Scene Engine;
- v0.76 Large-Data Visualization & Adaptive Rendering;
- v0.75 Scientific Data Binding & Transformation;
- v0.74 Advanced 2D Scientific Plot Grammar;
- v0.73 Visualization Engine 2 unified renderer contract.

Platform compatibility remains **1.0.0**.
