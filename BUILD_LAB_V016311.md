# Sustainable Catalyst Lab v0.163.1.1
## Unified Workspace Shell Live-DOM Binding & Page-Length Repair

Repair release for the v0.163.1 shell that updated release identity but did not take control of the live Lab page.

### Root causes fixed
1. The v0.154 frontend gate runs at `PHP_INT_MAX` and can prune the v0.163.1 shell assets that were enqueued at priority 240.
2. The v0.163.1 4D selector assumed `[data-v01530-workspace]`, while the live 4D runtime actually binds `[data-v0710-visualizer]`.
3. The v0.163.1 shell existed only as a client-side insertion, so a delivery/runtime failure left the entire specialist stack visible.

### Repair
- enqueue replacement shell assets at `PHP_INT_MAX`, after the legacy gate;
- remove the old v0.163.1 shell handles;
- render the shell structure server-side through the Lab content filter;
- bind the actual live module roots, including `[data-v0710-visualizer]`;
- progressively adopt v0.154–v0.163 specialist modules into one stage;
- CSS first-paint fail-safe collapses the old vertical module stack even if JavaScript does not run;
- retain v0.163.1 as the feature version while advancing release identity to v0.163.1.1;
- backend package and health marker included; scientific backend semantics unchanged.
