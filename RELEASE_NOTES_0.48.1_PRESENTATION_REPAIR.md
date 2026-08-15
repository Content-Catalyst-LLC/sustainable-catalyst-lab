# Sustainable Catalyst Lab v0.48.1

## Graph Studio Front Door & Scientific Workspace Presentation Repair

v0.48.1 is a presentation and research-workflow repair over the validated v0.48.0 scientific stack. It does not add new model families or change the governed numerical engines. Its purpose is to make the sophistication already present in Lab immediately visible and usable on the first screen.

### Front-door repair

- Adds a persistent four-workspace switcher for **Model Studio**, **Graph Studio**, **Experiments**, and **Observations**.
- Replaces the dashboard-first Overview hierarchy with a large **Graph Studio scientific-canvas preview**.
- Shows the latest saved project figure on the Overview when one exists; otherwise displays an explicitly labeled illustrative preview.
- Adds direct access to the project figure library and latest figure.
- Reduces Overview metrics to six research-relevant counts: models, figures, datasets, experiments, evidence, and notes.
- Adds a restrained dark research launcher beside the scientific canvas.

### Navigation repair

- Keeps the dedicated **MODEL** and **VISUALIZE** groups introduced in v0.47.0.
- Splits advanced workflow/governance modules into **Research operations** so the Project group no longer carries the entire platform history.
- Defaults specialist groups to collapsed on first v0.48.1 use while preserving user-controlled collapse state thereafter.
- Keeps all prior modules reachable through navigation and command search.

### Secondary-content repair

- Moves live scientific signals, the large specialist tool catalog, and traceability/activity detail into collapsed secondary drawers on the Overview.
- Keeps these tools fully available without allowing them to dominate the scientific front door.

### WordPress page-shell behavior

- **Preserves the existing three-card application row** for Prototyping Workbench, Decision Studio, and Site Intelligence.
- Refines the row with tighter institutional card styling rather than replacing it with a text utility strip.
- Synchronizes the outer Lab version badge to the installed `0.48.1` release when the standard `sc-lab-frame` markup is present.
- Keeps the outer Lab frame intact; the visual transformation is concentrated in the scientific workspace beneath the application cards.

### Scientific architecture preserved

- Probabilistic analysis remains v0.48.0.
- Graph Studio remains v0.47.0.
- Response surfaces remain v0.46.0.
- Dynamic systems remain v0.45.0.
- Scientific Visualization Engine remains v0.44.0 and is reused for the front-door graph preview.
- Diagnostics/cross-validation remain v0.43.0.
- Safe equation execution remains v0.42.0.
- Stable platform compatibility remains v1.0.0.
- Arbitrary code execution remains disabled.

### Release acceptance criteria

The v0.48.1 gate requires:

- the Graph Studio preview canvas to exist on the Overview;
- the four primary workspace switcher controls to exist;
- the scientific preview to use the shared v0.44 renderer;
- the specialist tool catalog to be secondary rather than front-door content;
- the three related Sustainable Catalyst applications to remain represented;
- the WordPress-facing release to be `0.48.1` while platform compatibility remains `1.0.0`;
- all v0.48 scientific/modeling regression tests to remain green.
