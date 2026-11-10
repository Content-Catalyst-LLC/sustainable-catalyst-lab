#!/usr/bin/env bash
# Local driver for Lab WordPress releases on SSH-accessible hosting (e.g. Bluehost shared hosting).
# Host facts (SSH alias, WordPress root, site URL) come from the environment, never from this repo.
#
#   SC_BH_SSH=<ssh alias> SC_BH_WP_ROOT=<remote wp root> SC_BH_SITE_URL=<https://site> \
#     deploy/bluehost/release.sh <command> [args]
#
# Commands:
#   preflight                         read-only state of the live plugin
#   backup <label> [--with-db]        plugin tree (+ database) backup with restore test
#   deploy <zip> <sha256> <backup>    install the exact accepted zip; verifies tree and live health
#   rollback <backup>                 restore the plugin tree (and preview option) from a backup
#   preview <on|off>                  switch the FIG-02A preview option
#   verify                            live HTTP checks only
#
# Optional: SC_BH_SSH_OPTS (extra ssh options), SC_BH_WP=none (file-only sandbox, no wp-cli),
# SC_BH_LAB_PATH (default /lab/).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SSH_TARGET="${SC_BH_SSH:?SC_BH_SSH (ssh alias) is required}"
WP_ROOT="${SC_BH_WP_ROOT:?SC_BH_WP_ROOT is required}"
SITE="${SC_BH_SITE_URL:-}"
WP_MODE="${SC_BH_WP:-wp}"
LAB_PATH="${SC_BH_LAB_PATH:-/lab/}"
read -r -a SSH_OPTS <<<"${SC_BH_SSH_OPTS:-}"
REMOTE_BIN='sc-releases/bin'
REMOTE_SCRIPT="$REMOTE_BIN/remote_lab_release.sh"

# One multiplexed connection per run: shared hosts rate-limit new SSH connections.
CTL_DIR="$(mktemp -d)"
trap 'ssh -o ControlPath="$CTL_DIR/c" -O exit "$SSH_TARGET" >/dev/null 2>&1 || true; rm -rf "$CTL_DIR"' EXIT
rsh() { ssh -o BatchMode=yes -o ControlMaster=auto -o ControlPath="$CTL_DIR/c" -o ControlPersist=120 \
            "${SSH_OPTS[@]+"${SSH_OPTS[@]}"}" "$SSH_TARGET" "$@"; }
sha() { (command -v sha256sum >/dev/null && sha256sum "$1" || shasum -a 256 "$1") | cut -d' ' -f1; }
die() { printf 'FAIL - %s\n' "$*" >&2; exit 1; }

push_script() {
    local want; want="$(sha "$HERE/remote_lab_release.sh")"
    rsh "mkdir -p ~/$REMOTE_BIN && chmod 700 ~/sc-releases ~/$REMOTE_BIN && cat > ~/$REMOTE_SCRIPT && chmod 700 ~/$REMOTE_SCRIPT" < "$HERE/remote_lab_release.sh"
    [[ "$(rsh "sha256sum ~/$REMOTE_SCRIPT" | cut -d' ' -f1)" == "$want" ]] || die "remote script upload mismatch"
}

remote() {
    local q=() a
    for a in "$@"; do q+=("$(printf '%q' "$a")"); done
    rsh "SC_WP_ROOT=$(printf '%q' "$WP_ROOT") SC_WP=$(printf '%q' "$WP_MODE") ~/$REMOTE_SCRIPT ${q[*]}"
}

verify_http() {
    [[ -n "$SITE" ]] || { echo "http_checks=skipped (no SC_BH_SITE_URL)"; return 0; }
    local code health
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$SITE$LAB_PATH")"
    [[ "$code" == 200 ]] || die "$SITE$LAB_PATH returned HTTP $code"
    health="$(curl -s --max-time 30 "$SITE/wp-json/sc-lab/v1/graph-studio-plotly-preview/fig02a/health")"
    python3 -c 'import json,sys; d=json.loads(sys.argv[1]); assert d["ok"] and d["plotlyJsSha256Verified"] and not d["cdnUsed"] and not d["publicationPerformed"], d; print("health=ok enabled=%s" % d["enabled"])' "$health" \
        || die "FIG-02A health route failed"
    echo "lab_page=200"
}

cmd="${1:-}"; shift || true
case "$cmd" in
    preflight) push_script; remote preflight ;;
    backup) push_script; remote backup "$@" ;;
    deploy)
        zip="${1:?zip}"; want="${2:?sha256}"; backup="${3:?backup dir}"
        [[ "$(sha "$zip")" == "$want" ]] || die "local zip sha256 does not match the accepted artifact"
        push_script
        name="$(basename "$zip")"
        rsh "mkdir -p ~/sc-releases/artifacts && cat > ~/sc-releases/artifacts/$(printf '%q' "$name")" < "$zip"
        # ssh starts in $HOME, so the relative artifact path resolves there.
        remote deploy "sc-releases/artifacts/$name" "$want" "$backup"
        verify_http ;;
    rollback) push_script; remote rollback "${1:?backup dir}"; verify_http ;;
    preview) push_script; remote preview "${1:?on|off}"; verify_http ;;
    verify) verify_http ;;
    *) sed -n '2,21p' "$0"; exit 2 ;;
esac
