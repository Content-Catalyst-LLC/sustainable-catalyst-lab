#!/usr/bin/env bash
# SC-LAB-RELEASE-01: regress deterministic-mtime/same-size WordPress manifest repair.
# Entirely synthetic: temp files only, no SSH, no WordPress, no production data.
set -euo pipefail
cd "$(dirname "$0")/.."
source_file="deploy/bluehost/remote_lab_release.sh"
grep -Fq 'rsync -ac --delete "$tmp/$SLUG/" "$PLUGIN_DIR/"' "$source_file"
[[ "$(grep -Fc 'rsync -ac --delete "$tmp/$SLUG/" "$PLUGIN_DIR/"' "$source_file")" == 2 ]] ||
  { echo "FAIL - deploy AND rollback require --checksum" >&2; exit 1; }
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/src" "$tmp/dest"
# Same size, same reproducible mtime, different content. Ordinary rsync -a skips.
printf 'sha=NEW1\n' > "$tmp/src/release.manifest"
printf 'sha=OLD1\n' > "$tmp/dest/release.manifest"
touch -t 202611100000 "$tmp/src/release.manifest" "$tmp/dest/release.manifest"
rsync -a --delete "$tmp/src/" "$tmp/dest/"
[[ "$(cat "$tmp/dest/release.manifest")" == 'sha=OLD1' ]] ||
  { echo "FAIL - original regression was not reproduced" >&2; exit 1; }
rsync -ac --delete "$tmp/src/" "$tmp/dest/"
cmp -s "$tmp/src/release.manifest" "$tmp/dest/release.manifest" ||
  { echo "FAIL - checksum-aware deploy missed same-size change" >&2; exit 1; }
# Rollback must also overwrite the same-size, fixed-mtime manifest.
printf 'sha=OLD1\n' > "$tmp/src/release.manifest"
touch -t 202611100000 "$tmp/src/release.manifest"
rsync -ac --delete "$tmp/src/" "$tmp/dest/"
cmp -s "$tmp/src/release.manifest" "$tmp/dest/release.manifest" ||
  { echo "FAIL - checksum-aware rollback missed same-size change" >&2; exit 1; }
echo 'PASS - SC-LAB-RELEASE-01 deterministic timestamps, same-size manifest, checksum-aware deploy and rollback'
