#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/public_html/sustainable-catalyst-lab-v0.157.0.1-wordpress.zip}"
WP_ROOT="${2:-$HOME/public_html}"
cd "$WP_ROOT"
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab"; [ -d "$SRC" ] || { echo 'ERROR: WordPress payload not found' >&2; exit 1; }
PLUGIN_DIR="$WP_ROOT/wp-content/plugins/sustainable-catalyst-lab"
BACKUP="$WP_ROOT/wp-content/plugins/sustainable-catalyst-lab.backup-v0.157.0.1-$(date -u +%Y%m%dT%H%M%SZ)"
[ ! -d "$PLUGIN_DIR" ] || cp -a "$PLUGIN_DIR" "$BACKUP"
mkdir -p "$PLUGIN_DIR"; rsync -a --delete "$SRC/" "$PLUGIN_DIR/"
if command -v wp >/dev/null 2>&1; then
  wp plugin activate sustainable-catalyst-lab --path="$WP_ROOT" >/dev/null || true
  wp cache flush --path="$WP_ROOT" >/dev/null || true
fi
echo 'PASS - WordPress Lab v0.157.0.1 files deployed'
[ -d "$BACKUP" ] && echo "Backup: $BACKUP" || true
