#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/sustainable-catalyst-lab-v0.152.0.11-wordpress.zip}"
WP_ROOT="${2:-$HOME/public_html}"
PLUGIN="$WP_ROOT/wp-content/plugins/sustainable-catalyst-lab"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
[ -d "$WP_ROOT/wp-content/plugins" ] || { echo "ERROR: invalid WordPress root $WP_ROOT" >&2; exit 1; }
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab"
[ -d "$SRC" ] || { echo 'ERROR: WordPress payload not found' >&2; exit 1; }
if [ -d "$PLUGIN" ]; then (cd "$WP_ROOT/wp-content/plugins" && zip -qr "$HOME/sc-lab-wordpress-backup-$STAMP.zip" sustainable-catalyst-lab); fi
rsync -a --delete "$SRC/" "$PLUGIN/"
cd "$WP_ROOT"
wp cache flush || true
wp transient delete --all || true
wp plugin list | grep sustainable-catalyst-lab
wp eval 'echo "SC_LAB_RELEASE_VERSION=" . SC_LAB_RELEASE_VERSION . PHP_EOL; echo "SC_LAB_FEATURE_VERSION=" . SC_LAB_FEATURE_VERSION . PHP_EOL;'
echo "Backup: $HOME/sc-lab-wordpress-backup-$STAMP.zip"
