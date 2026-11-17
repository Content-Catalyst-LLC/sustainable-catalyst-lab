#!/usr/bin/env bash
# Sandbox test of remote_lab_release.sh: a throwaway WordPress tree and a stub `wp` that keeps options in files.
# Exercises backup + restore test, deploy, tamper refusals, rollback and the plugin selection (SC_PLUGIN_SLUG).
# Old and new test files share size and mtime on purpose: an rsync quick check would skip them.
# No network, no real WordPress, no host. Run: bash deploy/bluehost/tests/test_remote_release.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$HERE/../remote_lab_release.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0; ok() { pass=$((pass+1)); echo "ok $pass - $*"; }
fail() { echo "not ok - $*"; exit 1; }

mkdir -p "$T/bin" "$T/opts" "$T/wp/wp-content/plugins"
cat > "$T/bin/wp" <<'STUB'
#!/usr/bin/env bash
# Minimal wp-cli stand-in: options live in $OPTS/<name>; plugins are active when their directory exists.
args=(); for a in "$@"; do case "$a" in --path=*|--skip-plugins|--skip-themes) ;; *) args+=("$a");; esac; done
set -- "${args[@]}"
case "$1 $2" in
  "core version") echo 7.1.4 ;;
  "plugin is-active") [[ -d "$WPROOT/wp-content/plugins/$3" ]] ;;
  "plugin get") sed -n 's/^[ *]*Version:[[:space:]]*//p' "$WPROOT/wp-content/plugins/$3/$3.php" | head -1 ;;
  "option get") [[ -f "$OPTS/$3" ]] && cat "$OPTS/$3" || exit 1 ;;
  "option update") printf '%s' "$4" > "$OPTS/$3"; echo "update $3" >> "$OPTS/.log" ;;
  "option delete") rm -f "$OPTS/$3"; echo "delete $3" >> "$OPTS/.log" ;;
  "cache flush"|"eval "*) : ;;
  *) [[ "$1" == eval ]] && echo "page_cache=none" ;;
esac
STUB
chmod +x "$T/bin/wp"
export PATH="$T/bin:$PATH" OPTS="$T/opts" WPROOT="$T/wp" SC_WP_ROOT="$T/wp" SC_WP=wp SC_RELEASE_HOME="$T/rel"

plugin() {  # plugin <slug> <version> <dir>
    mkdir -p "$3/$1/assets"; printf '<?php\n/*\n * Plugin Name: %s\n * Version: %s\n */\n' "$1" "$2" > "$3/$1/$1.php"
    printf 'js %s\n' "$2" > "$3/$1/assets/app.js"
}
zipof() { (cd "$1" && zip -qr "$2" .); sha256sum "$2" | cut -d' ' -f1; }
P="$T/wp/wp-content/plugins"

# --- Research bridge selected by SC_PLUGIN_SLUG ------------------------------------------------------------
export SC_PLUGIN_SLUG=sc-research-bridge
plugin sc-research-bridge 0.2.4 "$P"; plugin sustainable-catalyst-lab 0.163.1.10 "$P"
printf 1 > "$OPTS/sc_lab_fig02a_plotly_preview_enabled"
mkdir -p "$T/new"; plugin sc-research-bridge 0.6.0 "$T/new"; echo extra > "$T/new/sc-research-bridge/assets/extra.js"
sha="$(zipof "$T/new" "$T/bridge.zip")"
lab_before="$(cd "$P/sustainable-catalyst-lab" && find . -type f -exec sha256sum {} + | sort | sha256sum)"

out="$(bash "$R" preflight)"; [[ "$out" == *plugin_version=0.2.4* && "$out" != *preview_option* ]] && ok "preflight reads the bridge, not the Lab option" || fail "preflight: $out"
B="$(bash "$R" backup pre-bridge | sed -n 's/^backup_dir=//p')"; [[ -d "$B" && "$(sed -n 4p "$B/state.txt")" == none ]] && ok "backup restore-tested; no Lab option recorded" || fail backup
bash "$R" deploy "$T/bridge.zip" deadbeef "$B" >/dev/null 2>&1 && fail "wrong sha accepted" || ok "deploy refuses a zip that is not the accepted artifact"
out="$(bash "$R" deploy "$T/bridge.zip" "$sha" "$B")"; [[ "$out" == *deployed_tree=match* && "$(sed -n 's/^ \* Version: //p' "$P/sc-research-bridge/sc-research-bridge.php")" == 0.6.0 ]] && ok "deploy installs 0.6.0 exactly" || fail "deploy: $out"
bash "$R" preview on >/dev/null 2>&1 && fail "preview ran for the bridge" || ok "preview refuses a non-Lab plugin"
bash "$R" deploy "$T/bridge.zip" "$sha" "$B" >/dev/null 2>&1 && fail "deploy over a changed live tree" || ok "deploy refuses when the live plugin changed since the backup"
out="$(bash "$R" rollback "$B")"; [[ "$out" == *rollback=pass* && "$(sed -n 's/^ \* Version: //p' "$P/sc-research-bridge/sc-research-bridge.php")" == 0.2.4 && ! -e "$P/sc-research-bridge/assets/extra.js" ]] && ok "rollback restores 0.2.4 exactly" || fail "rollback: $out"
[[ "$(cat "$OPTS/sc_lab_fig02a_plotly_preview_enabled")" == 1 && ! -f "$OPTS/.log" ]] && ok "the Lab preview option was never written" || fail "Lab option touched"
[[ "$(cd "$P/sustainable-catalyst-lab" && find . -type f -exec sha256sum {} + | sort | sha256sum)" == "$lab_before" ]] && ok "the Lab plugin tree is untouched" || fail "Lab tree changed"
mkdir -p "$T/bad"; plugin sc-research-bridge 0.6.0 "$T/bad"; echo x > "$T/bad/stray.php"; bsha="$(zipof "$T/bad" "$T/bad.zip")"
B2="$(bash "$R" backup pre-bad | sed -n 's/^backup_dir=//p')"
bash "$R" deploy "$T/bad.zip" "$bsha" "$B2" >/dev/null 2>&1 && fail "zip with stray entry accepted" || ok "deploy refuses a zip with entries outside the plugin"
SC_PLUGIN_SLUG='../wp-content' bash "$R" preflight >/dev/null 2>&1 && fail "path slug accepted" || ok "an unsafe slug is refused"

# --- Default stays the Lab plugin, with its preview option recorded and restored ----------------------------
unset SC_PLUGIN_SLUG
out="$(bash "$R" preflight)"; [[ "$out" == *plugin_version=0.163.1.10* && "$out" == *preview_option=1* ]] && ok "default slug is the Lab plugin with its preview option" || fail "lab preflight: $out"
L="$(bash "$R" backup pre-lab | sed -n 's/^backup_dir=//p')"
bash "$R" preview off >/dev/null; [[ "$(cat "$OPTS/sc_lab_fig02a_plotly_preview_enabled")" == 0 ]] && ok "Lab preview switches" || fail "lab preview"
bash "$R" rollback "$L" >/dev/null; [[ "$(cat "$OPTS/sc_lab_fig02a_plotly_preview_enabled")" == 1 ]] && ok "Lab rollback restores its preview option" || fail "lab option restore"
echo "1..$pass"
