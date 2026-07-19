# Install Sustainable Catalyst Lab v0.39.1

Keep the cumulative upgrade ZIP and the V28 macOS installer together in `~/Downloads`, then run the installer.

For production secret operations, configure a 32-byte key:

```bash
python3 - <<'PY'
import base64, secrets
print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('='))
PY
```

Store the result as `SC_LAB_SECRET_MASTER_KEY`. Configure an independent `SC_LAB_AUDIT_SIGNING_SECRET`, mount persistent storage, and use:

```text
SC_LAB_SECURITY_PRIVACY_DB_PATH=/app/data/sc-lab-security-privacy.sqlite3
SC_LAB_SECURITY_REPLAY_DB_PATH=/app/data/sc-lab-request-replay.sqlite3
SC_LAB_SECURITY_PRIVACY_PERSISTENT_DISK_MOUNTED=1
```

During key rotation, keep old keys available through `SC_LAB_SECRET_PREVIOUS_MASTER_KEYS` until all retained records have been re-encrypted or expired.
