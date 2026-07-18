# Install Sustainable Catalyst Lab v0.38.0

Place these files in `~/Downloads`:

- `sustainable-catalyst-lab-v0.38.0-upgrade-DIRECT-BRIDGE-V24.zip`
- `install_and_push_sustainable_catalyst_lab_v0_38_0_DIRECT_BRIDGE_V24_macos.sh`

Run:

```bash
cd ~/Downloads
chmod 700 install_and_push_sustainable_catalyst_lab_v0_38_0_DIRECT_BRIDGE_V24_macos.sh
./install_and_push_sustainable_catalyst_lab_v0_38_0_DIRECT_BRIDGE_V24_macos.sh
```

The installer:

- Auto-detects the Sustainable Catalyst Lab Git repository.
- Accepts repositories reporting v0.31.0 through v0.38.0.
- Extracts and verifies the cumulative source payload.
- Creates a timestamped safety backup.
- Validates release metadata, contracts, PHP, JavaScript, and Python sources.
- Commits and pushes v0.38.0.
- Generates WordPress, Python Compute Core, and complete-source deployment packages.

After the push, deploy the latest `main` commit in Render using **Clear build cache & deploy**.

A paid persistent disk remains optional. To persist interoperability records, configure:

```text
SC_LAB_INTEROPERABILITY_DB_PATH=/app/data/sc-lab-research-interoperability.sqlite3
SC_LAB_INTEROPERABILITY_PERSISTENT_DISK_MOUNTED=1
```

Optional HMAC receipt signing can use:

```text
SC_LAB_INTEROPERABILITY_RECEIPT_SECRET=<strong-random-secret>
```

When that setting is absent, receipt integrity is still protected by canonical SHA-256 receipt hashes.
