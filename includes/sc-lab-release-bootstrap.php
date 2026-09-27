<?php
/**
 * Canonical Sustainable Catalyst Lab release identity bootstrap.
 *
 * This file intentionally has no WordPress dependency so release identity can
 * be tested before plugin bootstrap. Product release identity comes from the
 * signed/hash-verified release manifest; subsystem compatibility versions are
 * separate values.
 */
if (!function_exists('sc_lab_read_release_manifest')) {
    function sc_lab_read_release_manifest($plugin_dir) {
        $path = rtrim((string) $plugin_dir, '/\\') . '/build/sc-lab-release-manifest.json';
        if (!is_file($path)) { return array(); }
        $decoded = json_decode((string) file_get_contents($path), true);
        return is_array($decoded) ? $decoded : array();
    }
}

if (!function_exists('sc_lab_manifest_semver')) {
    function sc_lab_manifest_semver($manifest, $key, $fallback) {
        $value = is_array($manifest) && isset($manifest[$key]) ? trim((string) $manifest[$key]) : '';
        if (preg_match('/^\\d+\\.\\d+\\.\\d+(?:[-+][0-9A-Za-z.-]+)?$/', $value)) { return $value; }
        return (string) $fallback;
    }
}
