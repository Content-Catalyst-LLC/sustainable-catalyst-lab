#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/sustainable-catalyst-lab-v0.155.0-wordpress.zip}"
WP_ROOT="${2:-$HOME/public_html}"
PLUGIN_DIR="$WP_ROOT/wp-content/plugins/sustainable-catalyst-lab"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
unzip -q "$ZIP" -d "$TMP"; SRC="$TMP/sustainable-catalyst-lab"; [ -f "$SRC/sustainable-catalyst-lab.php" ] || { echo 'ERROR: invalid WordPress package' >&2; exit 1; }
[ -d "$PLUGIN_DIR" ] && cp -a "$PLUGIN_DIR" "$PLUGIN_DIR.backup-v0.155.0-$STAMP"
mkdir -p "$PLUGIN_DIR"; rsync -a --delete "$SRC/" "$PLUGIN_DIR/"
cd "$WP_ROOT"
if command -v wp >/dev/null 2>&1; then wp plugin activate sustainable-catalyst-lab >/dev/null; wp cache flush >/dev/null 2>&1 || true; fi
php -l "$PLUGIN_DIR/sustainable-catalyst-lab.php" >/dev/null
echo 'PASS - WordPress Lab v0.155.0 installed. Verify /wp-json/sc-lab/v1/runtime/health and the Lab front door.'
