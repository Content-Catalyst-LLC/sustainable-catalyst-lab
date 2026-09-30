# Sustainable Catalyst Lab v0.152.0.3

## Critical Bootstrap Dependency & Lab Navigation Recovery

This hotfix repairs the startup regression that could leave the Lab in a persistent **Loading** state with non-responsive Model Studio, Graph Studio, Experiments, Observations, and related navigation controls.

The v0.152.0.1 loader correctly removed the 247-module cumulative dependency chain, but its reduced critical dependency set did not include the Workspace and Feeds browser APIs consumed by the Overview bootstrap. v0.152.0.3 makes those dependencies explicit and adds graceful client-side fallbacks so optional-module timing cannot abort core Lab navigation.

The v0.152.0 dependency graph, scientific contracts, and backend remain unchanged.
