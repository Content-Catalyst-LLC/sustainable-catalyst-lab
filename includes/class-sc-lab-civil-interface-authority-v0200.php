<?php
/**
 * Makes the formula-visible Civil v0.15.0 interface authoritative.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Civil_Interface_Authority_V0200 {
    const VERSION = '0.20.0-civil-repair.1';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'replace_original_script'),
            10000
        );

        add_filter(
            'script_loader_tag',
            array(__CLASS__, 'suppress_original_script_tag'),
            10000,
            3
        );
    }

    private static function asset_url() {
        if (defined('SC_LAB_URL')) {
            return trailingslashit((string) constant('SC_LAB_URL'))
                . 'assets/';
        }

        $plugin_root_file = dirname(__DIR__)
            . '/sustainable-catalyst-lab.php';

        return plugin_dir_url($plugin_root_file) . 'assets/';
    }

    private static function is_original_civil_source($source) {
        $path = wp_parse_url((string) $source, PHP_URL_PATH);

        if (!is_string($path)) {
            return false;
        }

        return (
            substr(
                $path,
                -strlen('/civil-infrastructure-lab.js')
            ) === '/civil-infrastructure-lab.js'
            && strpos(
                $path,
                'civil-infrastructure-lab-v0150.js'
            ) === false
        );
    }

    public static function replace_original_script() {
        global $wp_scripts;

        if (
            is_object($wp_scripts)
            && isset($wp_scripts->registered)
            && is_array($wp_scripts->registered)
        ) {
            foreach (
                $wp_scripts->registered
                as $handle => $registered
            ) {
                $source = isset($registered->src)
                    ? (string) $registered->src
                    : '';

                if (!self::is_original_civil_source($source)) {
                    continue;
                }

                wp_dequeue_script($handle);
                wp_deregister_script($handle);
            }
        }

        wp_enqueue_script(
            'sc-lab-civil-infrastructure-authoritative-v0150',
            self::asset_url()
                . 'js/modules/'
                . 'civil-infrastructure-lab-v0150.js',
            array(),
            self::VERSION,
            true
        );

        wp_add_inline_script(
            'sc-lab-civil-infrastructure-authoritative-v0150',
            <<<'JS'
(() => {
  const initializeCivil = () => {
    const Lab = window.SCLab || {};
    const module = Lab.CivilInfrastructureLab;
    const mount = document.querySelector(
      '[data-civil-infrastructure-root]'
    );

    if (
      !mount
      || !module
      || typeof module.init !== 'function'
    ) {
      return;
    }

    if (String(module.VERSION || '') < '0.15.0') {
      return;
    }

    if (
      mount.dataset.scCivilAuthorityVersion
      === String(module.VERSION)
      && mount.children.length
    ) {
      return;
    }

    mount.replaceChildren();
    module.init(document, Lab.Projects);

    mount.dataset.scCivilAuthorityVersion =
      String(module.VERSION || '0.15.0');
  };

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      initializeCivil,
      { once: true }
    );
  } else {
    initializeCivil();
  }

  document.addEventListener(
    'sc-lab:module-opened',
    initializeCivil
  );

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest(
      '[data-lab-target="civil-infrastructure"],'
      + '[data-module-target="civil-infrastructure"],'
      + '[href*="civil-infrastructure"]'
    );

    if (trigger) {
      window.setTimeout(initializeCivil, 0);
    }
  });
})();
JS,
            'after'
        );
    }

    public static function suppress_original_script_tag(
        $tag,
        $handle,
        $source
    ) {
        if (self::is_original_civil_source($source)) {
            return '';
        }

        return $tag;
    }
}

SC_Lab_Civil_Interface_Authority_V0200::boot();
