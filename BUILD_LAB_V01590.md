# Build Lab v0.159.0

Baseline: Lab v0.158.0.

Run `VALIDATE_LAB_V01590.sh`, then `PACKAGE_LAB_V01590.sh`. The backend is included. Git push, Contabo deployment and WordPress deployment remain explicit separate actions.

Final builder note: cumulative SQLite managers v0.155.0-v0.159.0 use close-on-context-exit connections; validation includes the lifecycle regression test.
