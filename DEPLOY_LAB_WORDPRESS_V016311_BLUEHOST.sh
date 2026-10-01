#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/public_html/sustainable-catalyst-lab-v0.163.1.1-wordpress.zip}"
WP_ROOT="${2:-$HOME/public_html}"
PLUGINS="$WP_ROOT/wp-content/plugins"
CANON="$PLUGINS/sustainable-catalyst-lab"
STAMP="$(date +%Y%m%d-%H%M%S)"
[ -f "$ZIP" ] || { echo "ERROR: WordPress zip not found: $ZIP" >&2; exit 1; }
cd "$WP_ROOT"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab"
[ -f "$SRC/sustainable-catalyst-lab.php" ] || { echo 'ERROR: plugin package root invalid' >&2; exit 1; }
mkdir -p "$PLUGINS"
if [ -d "$CANON" ]; then mv "$CANON" "$HOME/sustainable-catalyst-lab.backup-v0.163.1.1-$STAMP"; fi
for d in "$PLUGINS"/sustainable-catalyst-lab-*; do [ -d "$d" ] || continue; mv "$d" "$HOME/$(basename "$d").moved-$STAMP"; done
cp -a "$SRC" "$CANON"
wp plugin activate sustainable-catalyst-lab >/dev/null
wp cache flush >/dev/null || true
VER="$(wp plugin get sustainable-catalyst-lab --field=version)"
[ "$VER" = '0.163.1.1' ] || { echo "ERROR: installed plugin version is $VER" >&2; exit 1; }
for f in \
  includes/class-sc-lab-unified-workspace-shell-v016311.php \
  assets/js/sc-lab-unified-workspace-shell-v016311.js \
  assets/css/sc-lab-unified-workspace-shell-v016311.css; do
  [ -s "$CANON/$f" ] || { echo "ERROR: missing v0.163.1.1 live shell file: $f" >&2; exit 1; }
done
echo 'PASS - WordPress Lab v0.163.1.1 installed and activated; live-DOM shell repair assets are present and duplicate Lab folders were moved outside wp-content/plugins.'
