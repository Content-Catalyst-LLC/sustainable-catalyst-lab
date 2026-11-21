#!/usr/bin/env bash
# SC-LAB-UI-02 direct production hotfix; owner explicitly declined staging.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export SC_BH_SSH="pctrqumy@pct.rqu.mybluehost.me"
export SC_BH_WP_ROOT="/home1/pctrqumy/public_html"
export SC_BH_SITE_URL="https://sustainablecatalyst.com"
PY="$ROOT/.venv-lab-ui/bin/python"
[[ -x "$PY" ]] || { echo "FAIL: Run from Mac with previously installed .venv-lab-ui/Playwright." >&2; exit 1; }

echo "=== Unit tests and real Graph Studio browser fixtures ==="
node tests/test-v015206-safe-controls.js
node tests/test-v015206-safe-boot-stabilization.js
node tests/test-v015206-graph-renderer.js
bash tests/test-bluehost-rsync-content-identity.sh
if command -v php >/dev/null 2>&1; then
 php tests/test-fig041-plugin-compatibility.php
 php -l includes/class-sc-lab-production-safe-boot-v015206.php
fi
OUT="$HOME/sc-lab-graph-hotfix"
mkdir -p "$OUT"
"$PY" scripts/run_chromium_lab_frontdoor.py "$OUT"
"$PY" - "$OUT/acceptance.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
assert d["state"]=="pass" and len(d["results"])==4,d
assert len([r for r in d["results"] if r.get("fixture")=="graph-renderer" and r["state"]=="pass"])==2,d
print("browser_acceptance=pass")
PY

echo "=== Reproducible, version-locked ZIP ==="
REV="$(git rev-parse HEAD)"
BUILD_OUT="$OUT/release"
mkdir -p "$BUILD_OUT"
BUILD_JSON="$(scripts/build_wordpress_release_zip.sh "$REV" "$BUILD_OUT")"
printf '%s\n' "$BUILD_JSON"
NAME="$(printf '%s\n' "$BUILD_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["zip"])')"
SHA256="$(printf '%s\n' "$BUILD_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["sha256"])')"
VERSION="$(printf '%s\n' "$BUILD_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])')"
[[ "$VERSION" == "0.163.1.9" ]] || { echo "FAIL: not compatible with deployed Research Bridge." >&2; exit 1; }
ZIP="$BUILD_OUT/$NAME"
echo "$SHA256  $ZIP" | shasum -a 256 -c -

echo "=== Production preflight, fresh plugin backup ==="
PREFLIGHT="$(deploy/bluehost/release.sh preflight)"
printf '%s\n' "$PREFLIGHT"
printf '%s\n' "$PREFLIGHT" | grep -q '^plugin_version=0.163.1.9$'
printf '%s\n' "$PREFLIGHT" | grep -q '^plugin_active=yes$'
BRIDGE="$(ssh -o BatchMode=yes "$SC_BH_SSH" "wp --path='$SC_BH_WP_ROOT' plugin get sc-research-bridge --field=version")"
[[ "$BRIDGE" == "0.6.1" ]] || { echo "FAIL: unexpected Bridge $BRIDGE" >&2; exit 1; }
BACKUP_RESULT="$(deploy/bluehost/release.sh backup lab-graph-ui-02)"
printf '%s\n' "$BACKUP_RESULT"
BACKUP_DIR="$(printf '%s\n' "$BACKUP_RESULT" | sed -n 's/^backup_dir=//p' | tail -1)"
[[ "$BACKUP_DIR" == /home1/pctrqumy/sc-releases/backups/* ]] || { echo "FAIL: backup path missing" >&2; exit 1; }
ssh -o BatchMode=yes "$SC_BH_SSH" "test -f '$BACKUP_DIR/SHA256SUMS'"

echo "=== Direct deployment and production browser verification ==="
status=0
deploy/bluehost/release.sh deploy "$ZIP" "$SHA256" "$BACKUP_DIR" || status=1
if [[ "$status" == 0 ]]; then deploy/bluehost/release.sh verify || status=1; fi
if [[ "$status" == 0 ]]; then
 curl -fsSL --max-time 40 "$SC_BH_SITE_URL/lab/?sc_lab_module=graph-studio" > "$OUT/served-lab.html" || status=1
 grep -q 'scientific-visualization-engine-v0440.js' "$OUT/served-lab.html" || status=1
 grep -q 'graph-studio-v0470.js' "$OUT/served-lab.html" || status=1
fi
if [[ "$status" == 0 ]]; then
 "$PY" - "$SC_BH_SITE_URL" "$OUT" <<'PY' || status=1
import json,sys
from playwright.sync_api import sync_playwright
site,out=sys.argv[1],sys.argv[2]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={"width":1280,"height":900})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    probe="""() => {
      const root=document.querySelector('.sc-lab-app');
      const overview=root?.querySelector('[data-lab-module="overview"]');
      const graph=root?.querySelector('[data-lab-module="graph-studio"]');
      const svg=graph?.querySelector('svg[data-sve-version]');
      return !!(root?.dataset.activeModule==='graph-studio' && svg &&
        getComputedStyle(overview).display==='none' &&
        getComputedStyle(graph).display!=='none' &&
        svg.querySelectorAll('path,polyline,circle,rect,line').length>4);
    }"""
    try:
        page.goto(site+"/lab/?sc_lab_module=graph-studio",wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function(probe,timeout=25000)
        page.screenshot(path=out+"/live-graph-visible.png",full_page=True)
        page.locator('.sc-lab-primary-rail-v0483 [data-open-module="overview"]').click(timeout=10000)
        assert page.evaluate("document.querySelector('.sc-lab-app').dataset.activeModule")=="overview"
        page.locator('.sc-lab-primary-rail-v0483 [data-open-module="graph-studio"]').click(timeout=10000)
        page.wait_for_function(probe,timeout=10000)
        print("LIVE_GRAPH_STUDIO=PASS: real SVG; Overview hidden; navigation verified")
        print("pageErrors",json.dumps(errors[:5]))
    finally:
        browser.close()
PY
fi
if [[ "$status" != 0 ]]; then
 echo "LIVE GRAPH CHECK FAILED — restoring previous Lab plugin." >&2
 deploy/bluehost/release.sh rollback "$BACKUP_DIR" || {
  echo "URGENT: rollback failed. Restore manually from: $BACKUP_DIR" >&2
  exit 2
 }
 exit 1
fi
echo "LAB_GRAPH_HOTFIX=DEPLOYED_AND_BROWSER_VERIFIED"
echo "revision=$REV"
echo "sha256=$SHA256"
echo "backup=$BACKUP_DIR"
echo "live_screenshot=$OUT/live-graph-visible.png"
