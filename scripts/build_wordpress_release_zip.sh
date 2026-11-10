#!/usr/bin/env bash
# Reproducible WordPress plugin zip for a committed Lab revision.
#
#   scripts/build_wordpress_release_zip.sh <git-rev> <out-dir>
#
# The zip is built from `git archive <rev>` only (never the working tree), with the
# development-only trees removed, a fixed mtime, sorted entries and no extra attributes,
# so the same revision always yields the same sha256. The sha256 printed here is the
# identity that staging acceptance and production deployment must both reference.
set -euo pipefail
umask 022

REV="${1:?usage: build_wordpress_release_zip.sh <git-rev> <out-dir>}"
OUT="${2:?usage: build_wordpress_release_zip.sh <git-rev> <out-dir>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="sustainable-catalyst-lab"
# Not shipped to WordPress: Python backend, tests, build scripts, docs, examples, SDK, staging deploy files.
EXCLUDE=(backend tests scripts docs examples sdk deploy)

FULL="$(git -C "$ROOT" rev-parse --verify "$REV^{commit}")"
VERSION="$(git -C "$ROOT" show "$FULL:$SLUG.php" | sed -n 's/^[ *]*Version:[[:space:]]*//p' | head -1 | tr -d '[:space:]')"
[[ -n "$VERSION" ]] || { echo "FAIL: no Version header in $SLUG.php at $FULL" >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/$SLUG" "$OUT"
git -C "$ROOT" archive "$FULL" | tar -x -C "$WORK/$SLUG"
for d in "${EXCLUDE[@]}"; do rm -rf "${WORK:?}/$SLUG/$d"; done
find "$WORK/$SLUG" \( -name '.DS_Store' -o -name '._*' -o -name '__MACOSX' \) -prune -exec rm -rf {} +
find "$WORK/$SLUG" -exec touch -h -t 202611100000 {} +

NAME="$SLUG-$VERSION-${FULL:0:12}.zip"
rm -f "$OUT/$NAME"
(cd "$WORK" && find "$SLUG" -type f | LC_ALL=C sort | zip -X -q -@ "$OUT/$NAME.tmp")
mv "$OUT/$NAME.tmp" "$OUT/$NAME"

SHA="$( (command -v sha256sum >/dev/null && sha256sum "$OUT/$NAME" || shasum -a 256 "$OUT/$NAME") | cut -d' ' -f1)"
COUNT="$(unzip -Z1 "$OUT/$NAME" | wc -l | tr -d ' ')"
printf '{"revision":"%s","version":"%s","zip":"%s","sha256":"%s","files":%s}\n' "$FULL" "$VERSION" "$NAME" "$SHA" "$COUNT"
