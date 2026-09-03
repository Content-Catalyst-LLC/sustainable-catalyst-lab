# Sustainable Catalyst Lab v0.81.0 — Annotation, Measurement & Scientific Markup

Visualization Engine 2 advances to **2.8.0** with a renderer-independent scientific markup overlay.

## Capabilities
- Explicit point, label, arrow, line, polyline, region, and threshold annotations.
- Coordinate, Euclidean distance, polyline-length, angle, and planar area measurements.
- Declared coordinate spaces and units with measurement provenance.
- Markup layers that attach to existing svg2d, canvas3d, canvas4d, and canvas-spatial figures without mutating the authoritative base figure.
- Graph Studio controls for annotation JSON, measurement JSON, explicit bounds, and a deterministic markup example.

## Scientific boundaries
Annotations are presentation/review objects, **not observations**. Measurements are derived from explicit markup coordinates and do not become observations. v0.81 performs no automatic unit conversion, geodesic approximation, geometry snapping, uncertainty inference, or scientific interpretation. Geographic distance/area is refused until a governed geodesy layer is available.

## Compatibility
v0.81 preserves v0.80 spatial/raster, v0.79 linked views/faceting/composition, v0.78 4D/time/parameter, v0.77 3D, v0.76 adaptive rendering, v0.75 data binding, and the established visualization/model/workflow line.
