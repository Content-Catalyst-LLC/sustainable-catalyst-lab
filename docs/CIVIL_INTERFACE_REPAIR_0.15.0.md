# Civil and Infrastructure Formula-Interface Repair

The original v0.12 Civil Engineering and Infrastructure Systems catalog contains 48 valid methods and formulas. The blank interface was caused by the browser module's dependency on central plugin-class enqueue and initializer anchors.

v0.15.0 repairs the presentation path with:

1. a standalone WordPress integration loaded directly from the plugin bootstrap
2. conditional loading for both the main Lab and focused Civil shortcode
3. late-priority shortcode registration to replace the fragile original focused renderer
4. browser auto-initialization on DOM readiness and Lab module-open events
5. support for every matching `data-civil-infrastructure-root` mount
6. prominent formula rendering
7. open executable-expression rendering
8. formula-completeness and execution tests

The repair does not change or remove the Civil calculation catalog. It makes the existing formulas reliably visible and usable.
