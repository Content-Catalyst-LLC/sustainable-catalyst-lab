# Install Sustainable Catalyst Lab v0.38.1

Keep these files together in `~/Downloads`:

- `sustainable-catalyst-lab-v0.38.1-upgrade-DIRECT-BRIDGE-V25.zip`
- `install_and_push_sustainable_catalyst_lab_v0_38_1_DIRECT_BRIDGE_V25_macos.sh`

Run:

```bash
cd ~/Downloads
chmod 700 install_and_push_sustainable_catalyst_lab_v0_38_1_DIRECT_BRIDGE_V25_macos.sh
./install_and_push_sustainable_catalyst_lab_v0_38_1_DIRECT_BRIDGE_V25_macos.sh
```

The installer verifies the cumulative source payload, finds the Lab repository, creates a safety backup, installs v0.38.1, runs release validation, commits and pushes the release, and generates deployment ZIPs. Use `--no-push` to install, validate, commit, and package without pushing.
