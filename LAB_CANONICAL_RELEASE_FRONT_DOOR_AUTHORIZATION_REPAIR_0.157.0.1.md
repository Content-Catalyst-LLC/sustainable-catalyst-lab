# Lab v0.157.0.1 — Canonical Release Identity, Front-Door Synchronization & Workspace Authorization Repair

The release adds a final front-door authority that reads `SC_LAB_RELEASE_VERSION` and synchronizes global Lab identity in the rendered application and the surrounding Lab landing card. A MutationObserver keeps cached or late-rendered page-builder content synchronized without rewriting version labels that identify the introduction version of a subsystem.

For server-backed workspaces, project operations remain authenticated WordPress REST operations. Logged-out access is intercepted only at the presentation layer and receives a sign-in state. The release does not make project-list, project-read or project-write endpoints public.

`releaseVersion = 0.157.0.1`

`featureVersion = 0.157.0`
