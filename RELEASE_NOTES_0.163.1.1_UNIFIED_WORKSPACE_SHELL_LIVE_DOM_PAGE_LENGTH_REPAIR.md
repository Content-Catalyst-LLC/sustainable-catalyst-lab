# Release notes — Lab v0.163.1.1

- Fixes v0.163.1 shell assets being pruned by the v0.154 `PHP_INT_MAX` frontend asset gate.
- Uses late, dependency-free shell asset enqueue after that gate.
- Adds server-rendered unified-shell markup.
- Corrects the 4D live DOM binding to `[data-v0710-visualizer]`.
- Adds fallback resolver based on the v0.153 project controls.
- Adds first-paint CSS collapse for the v0.153–v0.163 specialist stack.
- Retains one active specialist workspace at a time with preserved state.
- Keeps v0.163.1 as feature version; release version becomes v0.163.1.1.
- Includes backend health/release marker; no scientific backend semantics changed.
