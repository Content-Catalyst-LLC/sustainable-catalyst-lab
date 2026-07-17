# Install Sustainable Catalyst Lab v0.37.0

Place these files together in `~/Downloads`:

- `sustainable-catalyst-lab-v0.37.0-upgrade-DIRECT-BRIDGE-V21.zip`
- `install_and_push_sustainable_catalyst_lab_v0_37_0_DIRECT_BRIDGE_V21_macos.sh`

Run:

```bash
cd ~/Downloads
chmod 700 install_and_push_sustainable_catalyst_lab_v0_37_0_DIRECT_BRIDGE_V21_macos.sh
./install_and_push_sustainable_catalyst_lab_v0_37_0_DIRECT_BRIDGE_V21_macos.sh
```

The installer auto-detects the Lab Git repository, verifies the embedded source checksums, creates a timestamped safety backup, installs the cumulative release, validates version and release contracts, creates a Git commit, pushes the active branch, and generates deployment ZIPs.

It supports repositories reporting v0.31.0 through v0.37.0.

After the push, deploy the latest `main` commit in Render with **Clear build cache & deploy**.

Publication records are instance-local by default. Durable production storage may use:

```text
SC_LAB_PUBLICATION_STUDIO_DB_PATH=/app/data/sc-lab-publication-studio.sqlite3
SC_LAB_PUBLICATION_STUDIO_PERSISTENT_DISK_MOUNTED=1
```

Only set the persistent-disk flag when `/app/data` is actually mounted on durable storage.
