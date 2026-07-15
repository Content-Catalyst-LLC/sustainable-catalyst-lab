# Sustainable Catalyst Lab v0.26.5

## Mobile, Accessibility, and Interface Reliability

This release adds a non-destructive interface reliability layer that enhances the active laboratory after every lifecycle mount. It does not replace domain calculators, scientific feeds, or project records.

### Mobile and touch

- Responsive phone, tablet, and landscape layouts.
- Minimum 44-pixel controls and touch-friendly navigation.
- Mobile navigation scrim, Escape-key close, focus restoration, and scroll locking.
- Single-column toolbars and action groups at narrow widths.
- Safe horizontal scrolling for data tables.
- Responsive charts, maps, forms, code, and result output.

### Accessibility

- Skip link and explicit main-workspace landmark.
- Visible keyboard focus.
- WAI-ARIA tab semantics with Arrow, Home, and End navigation.
- Accessible names for unlabeled legacy controls and scientific visualizations.
- Live regions for loading, results, validation, and source errors.
- Table header scope, scroll-region labels, dialog semantics, and result focusability.
- Reduced-motion, increased-contrast, and forced-colors support.

### Interface health

**Settings → Lab Interface Health** runs the same Lab at phone, tablet, and desktop dimensions. It reports horizontal overflow, undersized targets, missing names and labels, incomplete tab semantics, inaccessible tables or visualizations, duplicate IDs, and active-panel integrity. Reports use `sc-lab-interface-health/1.0` and can be saved or exported as JSON.
