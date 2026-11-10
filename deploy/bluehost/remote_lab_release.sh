#!/usr/bin/env bash
# Runs ON the WordPress host (uploaded and sha256-checked by release.sh). Shared-hosting safe:
# needs only bash, wp-cli, tar, gzip, unzip, rsync, sha256sum. Never prints option values or secrets.
#
#   remote_lab_release.sh preflight
#   remote_lab_release.sh backup <label> [--with-db]
#   remote_lab_release.sh verify-backup <backup-dir>
#   remote_lab_release.sh deploy <zip> <sha256> <backup-dir>
#   remote_lab_release.sh verify-deployed <zip>
#   remote_lab_release.sh rollback <backup-dir>
#   remote_lab_release.sh preview <on|off>
#
# Environment: SC_WP_ROOT (WordPress root), SC_WP ("wp" or "none" for a file-only sandbox),
# SC_RELEASE_HOME (default ~/sc-releases). Backups go to $SC_RELEASE_HOME/backups, mode 700.
set -euo pipefail
umask 077

SLUG="sustainable-catalyst-lab"
WP_ROOT="${SC_WP_ROOT:?SC_WP_ROOT is required}"
WP_MODE="${SC_WP:-wp}"
REL_HOME="${SC_RELEASE_HOME:-$HOME/sc-releases}"
PLUGIN_DIR="$WP_ROOT/wp-content/plugins/$SLUG"
OPTION="sc_lab_fig02a_plotly_preview_enabled"

SCRATCH=()
cleanup() { local d; for d in "${SCRATCH[@]+"${SCRATCH[@]}"}"; do rm -rf "$d"; done; }
trap cleanup EXIT
# Sets TMP_DIR (not via $(...), which would lose the cleanup registration in a subshell).
scratch() { TMP_DIR="$(mktemp -d)"; SCRATCH+=("$TMP_DIR"); }
say() { printf '%s\n' "$*"; }
die() { printf 'FAIL - %s\n' "$*" >&2; exit 1; }
wpc() { [[ "$WP_MODE" == "wp" ]] || return 0; wp --path="$WP_ROOT" --skip-plugins --skip-themes "$@"; }
# Sorted "sha256  ./relative/path" manifest of a directory tree.
tree_manifest() { (cd "$1" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum); }

cmd_preflight() {
    [[ -d "$PLUGIN_DIR" ]] || die "plugin directory not found under SC_WP_ROOT"
    say "plugin_files=$(find "$PLUGIN_DIR" -type f | wc -l)"
    say "plugin_tree_sha256=$(tree_manifest "$PLUGIN_DIR" | sha256sum | cut -d' ' -f1)"
    say "plugin_version=$(sed -n 's/^[ *]*Version:[[:space:]]*//p' "$PLUGIN_DIR/$SLUG.php" | head -1 | tr -d '[:space:]')"
    if [[ "$WP_MODE" == "wp" ]]; then
        say "wp_core=$(wpc core version)"
        say "plugin_active=$(wpc plugin is-active "$SLUG" && echo yes || echo no)"
        say "preview_option=$(wpc option get "$OPTION" 2>/dev/null || echo unset)"
    fi
    say "free_kb=$(df -Pk "$HOME" | awk 'NR==2{print $4}')"
}

cmd_backup() {
    local label="${1:?label}"; local with_db="${2:-}"
    [[ "$label" =~ ^[A-Za-z0-9._-]+$ ]] || die "label must be [A-Za-z0-9._-]"
    local final="$REL_HOME/backups/$(date -u +%Y%m%dT%H%M%SZ)-$label"
    # Written under .partial and renamed only after the restore test, so a failed run never looks usable.
    local dir="$final.partial"
    mkdir -p "$dir"; chmod 700 "$REL_HOME" "$REL_HOME/backups" "$dir"
    tar -C "$(dirname "$PLUGIN_DIR")" -czf "$dir/plugin.tar.gz" "$SLUG"
    tree_manifest "$PLUGIN_DIR" > "$dir/plugin.manifest"
    if [[ "$with_db" == "--with-db" ]]; then
        [[ "$WP_MODE" == "wp" ]] || die "--with-db needs wp-cli"
        # Consistent InnoDB snapshot without locking the live site.
        wpc db export - --single-transaction --quick | gzip -6 > "$dir/db.sql.gz"
        # One table per line; `db export` dumps every table in the database, not only the WP prefix.
        wpc db tables --all-tables | LC_ALL=C sort > "$dir/db.tables"
    fi
    if [[ "$WP_MODE" == "wp" ]]; then
        { wpc core version; wpc plugin get "$SLUG" --field=version; wpc plugin is-active "$SLUG" && echo active || echo inactive
          wpc option get "$OPTION" 2>/dev/null || echo unset; } > "$dir/state.txt"
    fi
    (cd "$dir" && sha256sum -- * > SHA256SUMS)
    chmod 600 "$dir"/*
    cmd_verify_backup "$dir"
    mv "$dir" "$final"
    say "backup_dir=$final"
}

cmd_verify_backup() {
    local dir="${1:?backup dir}"
    [[ -f "$dir/SHA256SUMS" ]] || die "no SHA256SUMS in backup"
    (cd "$dir" && sha256sum -c --quiet SHA256SUMS) || die "backup checksum mismatch"
    gzip -t "$dir/plugin.tar.gz" || die "plugin archive corrupt"
    # Restore test: extract to scratch and compare to the manifest captured at backup time.
    scratch; local tmp="$TMP_DIR"
    tar -C "$tmp" -xzf "$dir/plugin.tar.gz"
    diff -q <(tree_manifest "$tmp/$SLUG") "$dir/plugin.manifest" >/dev/null || die "plugin archive does not restore to its manifest"
    say "plugin_restore_test=pass files=$(wc -l < "$dir/plugin.manifest")"
    if [[ -f "$dir/db.sql.gz" ]]; then
        gzip -t "$dir/db.sql.gz" || die "database dump corrupt"
        local want got
        want="$(wc -l < "$dir/db.tables")"
        got="$(zcat "$dir/db.sql.gz" | grep -c '^CREATE TABLE ')"
        [[ "$want" == "$got" ]] || die "database dump has $got tables, expected $want"
        zcat "$dir/db.sql.gz" | tail -1 | grep -q '^-- Dump completed' || die "database dump incomplete"
        say "db_dump_check=pass tables=$got bytes=$(stat -c %s "$dir/db.sql.gz")"
    fi
}

cmd_deploy() {
    local zip="${1:?zip}" sha="${2:?sha256}" backup="${3:?backup dir}"
    [[ "$(sha256sum "$zip" | cut -d' ' -f1)" == "$sha" ]] || die "zip sha256 does not match the accepted artifact"
    cmd_verify_backup "$backup" >/dev/null
    [[ "$(tree_manifest "$PLUGIN_DIR" | sha256sum)" == "$(sha256sum < "$backup/plugin.manifest")" ]] \
        || die "live plugin changed since backup; take a new backup"
    scratch; local tmp="$TMP_DIR"
    unzip -q "$zip" -d "$tmp"
    [[ -f "$tmp/$SLUG/$SLUG.php" ]] || die "zip does not contain $SLUG/$SLUG.php"
    [[ "$(find "$tmp" -mindepth 1 -maxdepth 1 | wc -l)" == 1 ]] || die "zip has entries outside $SLUG/"
    chmod -R u=rwX,go=rX "$tmp/$SLUG"
    rsync -a --delete "$tmp/$SLUG/" "$PLUGIN_DIR/"
    wpc cache flush >/dev/null 2>&1 || true
    cmd_verify_deployed "$zip"
}

cmd_verify_deployed() {
    local zip="${1:?zip}"
    scratch; local tmp="$TMP_DIR"
    unzip -q "$zip" -d "$tmp"
    diff -q <(tree_manifest "$tmp/$SLUG") <(tree_manifest "$PLUGIN_DIR") >/dev/null || die "deployed tree differs from the zip"
    if [[ "$WP_MODE" == "wp" ]]; then
        wpc plugin is-active "$SLUG" || die "plugin is not active"
    fi
    say "deployed_tree=match files=$(find "$PLUGIN_DIR" -type f | wc -l) tree_sha256=$(tree_manifest "$PLUGIN_DIR" | sha256sum | cut -d' ' -f1)"
}

cmd_rollback() {
    local backup="${1:?backup dir}"
    cmd_verify_backup "$backup" >/dev/null
    scratch; local tmp="$TMP_DIR"
    tar -C "$tmp" -xzf "$backup/plugin.tar.gz"
    rsync -a --delete "$tmp/$SLUG/" "$PLUGIN_DIR/"
    diff -q <(tree_manifest "$PLUGIN_DIR") "$backup/plugin.manifest" >/dev/null || die "rollback tree differs from backup manifest"
    if [[ -f "$backup/state.txt" && "$WP_MODE" == "wp" ]]; then
        local opt; opt="$(sed -n 4p "$backup/state.txt")"
        if [[ "$opt" == "unset" ]]; then wpc option delete "$OPTION" >/dev/null 2>&1 || true; else wpc option update "$OPTION" "$opt" >/dev/null; fi
    fi
    wpc cache flush >/dev/null 2>&1 || true
    say "rollback=pass files=$(wc -l < "$backup/plugin.manifest")"
}

cmd_preview() {
    case "${1:?on|off}" in
        on) wpc option update "$OPTION" 1 >/dev/null ;;
        off) wpc option update "$OPTION" 0 >/dev/null ;;
        *) die "preview takes on|off" ;;
    esac
    wpc cache flush >/dev/null 2>&1 || true
    say "preview_option=$(wpc option get "$OPTION")"
}

sub="${1:-}"; shift || true
case "$sub" in
    preflight) cmd_preflight ;;
    backup) cmd_backup "$@" ;;
    verify-backup) cmd_verify_backup "$@" ;;
    deploy) cmd_deploy "$@" ;;
    verify-deployed) cmd_verify_deployed "$@" ;;
    rollback) cmd_rollback "$@" ;;
    preview) cmd_preview "$@" ;;
    *) die "unknown command '$sub'" ;;
esac
