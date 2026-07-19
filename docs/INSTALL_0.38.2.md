# Install Sustainable Catalyst Lab v0.38.2

Keep these files together in `~/Downloads`:

- `sustainable-catalyst-lab-v0.38.2-upgrade-DIRECT-BRIDGE-V26.zip`
- `install_and_push_sustainable_catalyst_lab_v0_38_2_DIRECT_BRIDGE_V26_macos.sh`

Run:

```bash
cd ~/Downloads
chmod 700 install_and_push_sustainable_catalyst_lab_v0_38_2_DIRECT_BRIDGE_V26_macos.sh
./install_and_push_sustainable_catalyst_lab_v0_38_2_DIRECT_BRIDGE_V26_macos.sh
```

The cumulative installer finds the Lab Git repository, verifies the complete source payload, creates a timestamped safety backup, installs v0.38.2, validates release contracts and focused tests, commits and pushes the release, and generates WordPress, backend, source, Python SDK, TypeScript SDK, and browser embed packages.

Use `--no-push` to install, validate, commit, and package without pushing.

## Render configuration

```text
SC_LAB_PUBLIC_INTEGRATION_DB_PATH=/app/data/sc-lab-public-research-integrations.sqlite3
SC_LAB_PUBLIC_API_KEY=<strong-random-key>
SC_LAB_PUBLIC_API_SCOPES=research:read,research:write,webhooks:read,webhooks:write,webhooks:emit,embeds:write
SC_LAB_WEBHOOK_SIGNING_SECRET=<strong-random-secret>
SC_LAB_WEBHOOK_DELIVERY_ENABLED=0
SC_LAB_PUBLIC_INTEGRATION_MAX_SUBSCRIPTIONS=5000
SC_LAB_PUBLIC_INTEGRATION_MAX_DELIVERIES=250000
SC_LAB_PUBLIC_INTEGRATION_PERSISTENT_DISK_MOUNTED=1
```

`SC_LAB_PUBLIC_API_KEY` falls back to the configured Compute Core API key. `SC_LAB_WEBHOOK_SIGNING_SECRET` falls back to the interoperability receipt or Compute Core signing secret, but a dedicated production secret is recommended.

Keep `SC_LAB_WEBHOOK_DELIVERY_ENABLED=0` until outbound HTTPS delivery and network policy have been reviewed. After the Git push, deploy the latest `main` commit in Render using **Clear build cache & deploy**.
