#!/usr/bin/env bash
# Source from release.sh; depends on the release driver's rsh(), sha(), die().
# Bounded SSH payloads and a remote SHA/byte receipt prevent a truncated
# WordPress ZIP from ever reaching the install command.

sc_transfer_zip_verified() {
    local zip="$1" want="$2"
    local name bytes part dest received expected_bytes remote_sha remote_bytes
    local block=262144 offset=0 index=0 chunk

    name="$(basename "$zip")"
    [[ "$name" =~ ^[A-Za-z0-9._-]+[.]zip$ ]] || die "unsafe release ZIP name"
    [[ "$(sha "$zip")" == "$want" ]] || die "local ZIP checksum changed before upload"
    bytes="$(wc -c < "$zip" | tr -d '[:space:]')"
    [[ "$bytes" =~ ^[0-9]+$ && "$bytes" -gt 0 ]] || die "invalid local ZIP size"
    dest="sc-releases/artifacts/$name"
    part="sc-releases/artifacts/.$name.partial-$$"

    # The existing one-shot 'cat > remote' silently received 1,769,472 of
    # 7,044,891 bytes on Bluehost. Upload fixed 256-KiB blocks instead and
    # verify the cumulative remote byte count after EVERY block.
    rsh "umask 077; mkdir -p ~/sc-releases/artifacts && : > ~/$part" ||
        die "cannot initialize remote archive transfer"

    while (( offset < bytes )); do
        chunk=$block
        if (( bytes - offset < block )); then chunk=$((bytes - offset)); fi
        expected_bytes=$((offset + chunk))
        received="$(dd if="$zip" bs="$block" skip="$index" count=1 2>/dev/null |
                    rsh "cat >> ~/$part && stat -c %s ~/$part")" ||
                    die "SSH block $index failed before WordPress install"
        [[ "$received" == "$expected_bytes" ]] ||
            die "SSH block $index incomplete: remote has $received of $expected_bytes bytes (no install)"
        offset=$expected_bytes
        index=$((index + 1))
    done

    remote_bytes="$(rsh "stat -c %s ~/$part")" ||
        die "could not verify remote ZIP size"
    remote_sha="$(rsh "sha256sum ~/$part | cut -d' ' -f1")" ||
        die "could not verify remote ZIP checksum"
    [[ "$remote_bytes" == "$bytes" && "$remote_sha" == "$want" ]] ||
        die "remote ZIP validation failed: local $bytes bytes, remote $remote_bytes; SHA match=$([[ "$remote_sha" == "$want" ]] && echo yes || echo no) (no install)"

    # Only publish the complete archive name after both checks succeed.
    rsh "mv -f -- ~/$part ~/$dest" ||
        die "remote ZIP could not be finalized (no install)"
    remote_bytes="$(rsh "stat -c %s ~/$dest")" ||
        die "cannot confirm finalized ZIP"
    remote_sha="$(rsh "sha256sum ~/$dest | cut -d' ' -f1")" ||
        die "cannot hash finalized ZIP"
    [[ "$remote_bytes" == "$bytes" && "$remote_sha" == "$want" ]] ||
        die "final remote ZIP verification failed (no install)"
    echo "remote_artifact=verified bytes=$bytes blocks=$index sha256=$want"
}

# Recheck a previously staged artifact. Always compare BOTH byte length and
# SHA-256 against the local accepted ZIP. Does not modify remote files.
sc_remote_zip_is_verified() {
    local zip="$1" want="$2" name bytes actual
    name="$(basename "$zip")"
    [[ "$name" =~ ^[A-Za-z0-9._-]+[.]zip$ ]] || return 1
    bytes="$(wc -c < "$zip" | tr -d '[:space:]')"
    [[ "$bytes" =~ ^[0-9]+$ && "$bytes" -gt 0 ]] || return 1
    actual="$(rsh "test -f ~/sc-releases/artifacts/$name && stat -c %s ~/sc-releases/artifacts/$name && sha256sum ~/sc-releases/artifacts/$name | cut -d' ' -f1")" ||
        return 1
    [[ "$actual" == "$(printf '%s\n%s' "$bytes" "$want")" ]]
}
