# Sustainable Catalyst Lab v0.25.5

## Module Lifecycle and Memory Management

The public Lab now renders one `data-lab-module` panel per page lifecycle. Selecting another laboratory performs an explicit unmount event, runs registered cleanup callbacks, and navigates to a fresh isolated lifecycle. This intentionally favors stability and deterministic memory release over fragile in-place transitions.

### Browser API

```javascript
window.SCLabLifecycleV0255.status()
window.SCLabLifecycleV0255.scope("laboratory-slug")
window.SCLabLifecycleV0255.cleanup("laboratory-slug")
```

A lifecycle scope can register timeouts, intervals, animation frames, observers, abort controllers, event listeners, and custom cleanup callbacks.
