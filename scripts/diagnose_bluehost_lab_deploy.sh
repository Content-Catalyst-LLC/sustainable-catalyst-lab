#!/usr/bin/env bash
# SC-LAB-UI-04 — read-only triage after the last silent pre-install abort.
# No install, cache purge, rollback, or WordPress/database writes.
set -euo pipefail
cd "$(dirname "$0")/.."
SC_BH_SSH="pctrqumy@pct.rqu.mybluehost.me"
SC_BH_WP_ROOT="/home1/pctrqumy/public_html"
ZIP="$HOME/sc-lab-graph-hotfix/release/sustainable-catalyst-lab-0.163.1.9-894a2493332b.zip"
BACKUP="/home1/pctrqumy/sc-releases/backups/20261121T051215Z-lab-graph-ui-02"
EXPECTED="accffa30141e117bcadf068884f47d529723040c94be02002c04ae68c23d2a2f"
echo "=== SC-LAB-UI-04 READ-ONLY deployment triage ==="
echo "=== Local accepted release artifact ==="
test -f "$ZIP" || { echo "local_zip=missing"; exit 1; }
echo "$EXPECTED  $ZIP" | shasum -a 256 -c -
echo "local_zip_bytes=$(wc -c < "$ZIP" | tr -d ' ')"
echo "=== Remote artifact, backup and installed plugin ==="
ssh -o BatchMode=yes -o ConnectTimeout=20 "$SC_BH_SSH" \
 "SC_WP_ROOT=$(printf '%q' "$SC_BH_WP_ROOT") bash -s -- $(printf '%q' "$(basename "$ZIP")") $(printf '%q' "$EXPECTED") $(printf '%q' "$BACKUP")" <<'REMOTE'
set -euo pipefail
name="$1"
expected="$2"
backup="$3"
artifact="$HOME/sc-releases/artifacts/$name"
plugin="$SC_WP_ROOT/wp-content/plugins/sustainable-catalyst-lab"
echo "remote_connection=ok"
echo "remote_date_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
if [[ -f "$artifact" ]]; then
  echo "remote_artifact=present"
  got="$(sha256sum "$artifact" | awk '{print $1}')"
  if [[ "$got" == "$expected" ]]; then echo "remote_artifact_sha256=match"; else echo "remote_artifact_sha256=MISMATCH"; fi
  echo "remote_artifact_bytes=$(wc -c < "$artifact" | tr -d ' ')"
else
  echo "remote_artifact=MISSING"
fi
if [[ -f "$backup/SHA256SUMS" ]]; then
  echo "backup_manifest=present"
  if (cd "$backup" && sha256sum -c --quiet SHA256SUMS); then
    echo "backup_checksum=pass"
  else
    echo "backup_checksum=FAIL"
  fi
else
  echo "backup_manifest=MISSING"
fi
if [[ -d "$plugin" ]]; then
  echo "live_plugin=present"
  echo "live_plugin_files=$(find "$plugin" -type f | wc -l | tr -d ' ')"
  echo "live_plugin_version=$(sed -n 's/^[ *]*Version:[[:space:]]*//p' "$plugin/sustainable-catalyst-lab.php" | head -1 | tr -d '[:space:]')"
  if [[ -f "$backup/plugin.manifest" ]]; then
    echo "live_tree_comparison=started"
    tmp="$(mktemp)"
    trap 'rm -f "$tmp"' EXIT
    (cd "$plugin" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum) > "$tmp"
    if cmp -s "$tmp" "$backup/plugin.manifest"; then
      echo "live_tree_vs_backup=match"
    else
      echo "live_tree_vs_backup=DIFFERS"
      echo "live_tree_manifest_lines=$(wc -l < "$tmp" | tr -d ' ')"
      echo "backup_manifest_lines=$(wc -l < "$backup/plugin.manifest" | tr -d ' ')"
    fi
  fi
else
  echo "live_plugin=MISSING"
fi
df -Pk "$HOME" | awk 'NR==2 {print "remote_free_kb="$4}'
df -Pi "$HOME" | awk 'NR==2 {print "remote_inode_free="$4}'
echo "read_only_diagnostics=complete"
REMOTE
