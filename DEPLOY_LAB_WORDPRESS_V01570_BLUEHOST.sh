#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/sustainable-catalyst-lab-v0.157.0-wordpress.zip}"
WP_ROOT="${2:-$HOME/public_html}"
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
cd "$WP_ROOT"
command -v wp >/dev/null 2>&1 || { echo 'ERROR: wp-cli not available' >&2; exit 1; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab"; [ -d "$SRC" ] || { echo 'ERROR: WordPress payload not found' >&2; exit 1; }
PLUGIN_DIR="$WP_ROOT/wp-content/plugins/sustainable-catalyst-lab"
BACKUP="$WP_ROOT/wp-content/plugins/sustainable-catalyst-lab.backup-v0.157.0-$(date -u +%Y%m%dT%H%M%SZ)"
[ -d "$PLUGIN_DIR" ] && cp -a "$PLUGIN_DIR" "$BACKUP"
mkdir -p "$PLUGIN_DIR"; rsync -a --delete "$SRC/" "$PLUGIN_DIR/"
wp plugin activate sustainable-catalyst-lab >/dev/null
wp eval 'echo defined("SC_LAB_RELEASE_VERSION") ? SC_LAB_RELEASE_VERSION : "missing";' | grep -qx '0.157.0'
echo 'PASS - WordPress Lab plugin reports v0.157.0'
