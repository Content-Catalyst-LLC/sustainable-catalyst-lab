#!/usr/bin/env bash
# SC-LAB-RELEASE-02. Purely synthetic transfer tests; zero network/WordPress access.
set -euo pipefail
cd "$(dirname "$0")/.."
source deploy/bluehost/verified_zip_transfer.sh

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
MOCK_HOME="$TMP/mock-remote"
mkdir -p "$MOCK_HOME"
sha() {
    if command -v sha256sum >/dev/null; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}
die() { printf 'FAIL - %s\n' "$*" >&2; exit 1; }
# Run the remote command in an isolated mock HOME and pass its stdin through.
# On macOS emulate Linux's remote stat/sha256sum commands.
rsh() {
    local command="$1"
    if [[ "$(uname)" == "Darwin" ]]; then
        command="${command//stat -c %s/stat -f %z}"
        command="${command//sha256sum /shasum -a 256 }"
    fi
    if [[ "${MOCK_SHORT_WRITE:-no}" == yes && "$command" == *"cat >> "* ]]; then
        # Behaves like the Bluehost truncated-stream failure. Despite exit=0
        # (or a producer SIGPIPE), block byte-count checking must reject it.
        command="${command/cat >>/head -c 131072 >>}"
    fi
    HOME="$MOCK_HOME" bash -c "$command"
}

ZIP="$TMP/synthetic-release.zip"
dd if=/dev/urandom of="$ZIP" bs=262144 count=11 2>/dev/null
DIGEST="$(sha "$ZIP")"
receipt="$(sc_transfer_zip_verified "$ZIP" "$DIGEST")"
printf '%s\n' "$receipt"
remote_file="$MOCK_HOME/sc-releases/artifacts/$(basename "$ZIP")"
cmp -s "$ZIP" "$remote_file" || die "synthetic upload was not byte-identical"
[[ "$receipt" == *"remote_artifact=verified"* ]] || die "missing transport receipt"
echo "PASS - SC-LAB-RELEASE-02 transfer of >2.8 MB archive, remote byte count and SHA-256"

# An incorrect local digest must not create an installed artifact.
BAD_ZIP="$TMP/synthetic-wrong-sha.zip"
cp "$ZIP" "$BAD_ZIP"
if (sc_transfer_zip_verified "$BAD_ZIP" "0000000000000000000000000000000000000000000000000000000000000000") >"$TMP/rejected-local.log" 2>&1; then
    die "bad local SHA was accepted"
fi
[[ ! -e "$MOCK_HOME/sc-releases/artifacts/$(basename "$BAD_ZIP")" ]] ||
    die "bad local SHA created a final archive"
echo "PASS - SC-LAB-RELEASE-02 rejects a bad local SHA before transfer"

# A short write must not promote a partial archive to the final artifact name.
FAIL_ZIP="$TMP/synthetic-short-write.zip"
cp "$ZIP" "$FAIL_ZIP"
export MOCK_SHORT_WRITE=yes
if (sc_transfer_zip_verified "$FAIL_ZIP" "$(sha "$FAIL_ZIP")") >"$TMP/rejected-remote.log" 2>&1; then
    die "short SSH write was accepted"
fi
[[ ! -e "$MOCK_HOME/sc-releases/artifacts/$(basename "$FAIL_ZIP")" ]] ||
    die "short SSH write was promoted to the final artifact"
grep -Eq 'incomplete|failed before WordPress install' "$TMP/rejected-remote.log" ||
    die "short write failure did not produce a clear diagnostic"
echo "PASS - SC-LAB-RELEASE-02 rejects truncated remote upload without installation"
