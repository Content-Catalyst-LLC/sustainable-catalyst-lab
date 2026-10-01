#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/public_html/sustainable-catalyst-lab-v0.163.1.3-wordpress.zip}"
WP_ROOT="${2:-$HOME/public_html}"; PLUGINS="$WP_ROOT/wp-content/plugins"; CANON="$PLUGINS/sustainable-catalyst-lab"; STAMP="$(date +%Y%m%d-%H%M%S)"
[ -f "$ZIP" ] || { echo "ERROR: WordPress zip not found: $ZIP" >&2; exit 1; }
cd "$WP_ROOT"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"; SRC="$TMP/sustainable-catalyst-lab"
[ -f "$SRC/sustainable-catalyst-lab.php" ] || { echo 'ERROR: plugin package root invalid' >&2; exit 1; }
mkdir -p "$PLUGINS"
if [ -d "$CANON" ]; then mv "$CANON" "$HOME/sustainable-catalyst-lab.backup-v0.163.1.3-$STAMP"; fi
for d in "$PLUGINS"/sustainable-catalyst-lab-*; do [ -d "$d" ] || continue; mv "$d" "$HOME/$(basename "$d").moved-$STAMP"; done
cp -a "$SRC" "$CANON"; wp plugin activate sustainable-catalyst-lab >/dev/null; wp cache flush >/dev/null || true
VER="$(wp plugin get sustainable-catalyst-lab --field=version)"; [ "$VER" = '0.163.1.3' ] || { echo "ERROR: installed plugin version is $VER" >&2; exit 1; }
for f in includes/class-sc-lab-4d-front-door-visual-polish-v016313.php assets/js/sc-lab-4d-front-door-visual-polish-v016313.js assets/css/sc-lab-4d-front-door-visual-polish-v016313.css; do [ -s "$CANON/$f" ] || { echo "ERROR: missing v0.163.1.3 polish file: $f" >&2; exit 1; }; done
grep -q 'advancedPanelsProgressive' "$CANON/includes/class-sc-lab-4d-front-door-visual-polish-v016313.php" || { echo 'ERROR: compact progressive-controls configuration missing after install' >&2; exit 1; }
grep -q 'sc-lab-v016313-metrics-strip' "$CANON/assets/css/sc-lab-4d-front-door-visual-polish-v016313.css" || { echo 'ERROR: compact 4D metric-strip styling missing after install' >&2; exit 1; }
grep -q '\[data-overview-signals\]{display:block!important}' "$CANON/assets/css/sc-lab-4d-front-door-visual-polish-v016313.css" || { echo 'ERROR: Scientific signals retention guard missing after install' >&2; exit 1; }
echo 'PASS - WordPress Lab v0.163.1.3 installed and activated; 4D front-door visual polish assets are present.'
