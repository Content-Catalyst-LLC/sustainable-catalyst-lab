# Three-Dimensional and Projected Four-Dimensional Visualization

The dimensional viewer represents scene vertices with either three coordinates `(x, y, z)` or four coordinates `(x, y, z, w)`.

A four-dimensional view follows this pipeline:

```text
4D vertices
→ rotation in XY, XZ, XW, YZ, YW, and ZW planes
→ perspective projection from 4D to 3D
→ X, Y, and Z camera rotation
→ perspective projection from 3D to 2D
→ SVG rendering
```

## Included reference scenes

- 3D cube: 8 vertices and 12 edges
- 4D tesseract: 16 vertices and 32 edges
- 4D simplex / 5-cell: 5 vertices and 10 edges
- 4D 16-cell: 8 vertices and 24 edges

## Analysis-derived scenes

When a result includes records with at least three or four numerical fields, the viewer maps those fields directly and independently normalizes each field to `[-1, 1]`. Field names and normalization rules remain in scene metadata.

When no direct dimensional data exist, the viewer can construct a normalized result-space glyph. This is explicitly marked as derived and must not be interpreted as physical geometry or a causal model.

## Export and handoff

The current projected view can be exported as SVG, PNG, PDF, scene JSON, or an analysis package. Decision Studio receives both the rendered figure and the complete scene specification, including original vertices, edges, dimensions, semantic type, rotation and projection metadata, and audit fingerprints.
