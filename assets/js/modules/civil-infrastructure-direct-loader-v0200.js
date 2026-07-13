(() => {
  'use strict';

  const Lab = window.SCLab = window.SCLab || {};
  const loaderElement = document.currentScript;
  const readyMarker = 'scCivilDirectLoaderVersion';
  const minimumVersion = '0.15.0';

  function parts(version) {
    return String(version || '')
      .split('.')
      .map((value) => Number.parseInt(value, 10) || 0);
  }

  function versionAtLeast(actual, required) {
    const left = parts(actual);
    const right = parts(required);
    const length = Math.max(left.length, right.length);

    for (let index = 0; index < length; index += 1) {
      const a = left[index] || 0;
      const b = right[index] || 0;

      if (a > b) {
        return true;
      }

      if (a < b) {
        return false;
      }
    }

    return true;
  }

  function authoritativeModule() {
    const module = Lab.CivilInfrastructureLab;

    if (
      !module
      || typeof module.init !== 'function'
      || !versionAtLeast(module.VERSION, minimumVersion)
    ) {
      return null;
    }

    return module;
  }

  function initialize() {
    const mount = document.querySelector(
      '[data-civil-infrastructure-root]'
    );
    const module = authoritativeModule();

    if (!mount || !module) {
      return false;
    }

    if (
      mount.dataset[readyMarker]
      === String(module.VERSION)
      && mount.children.length
    ) {
      return true;
    }

    mount.replaceChildren();

    try {
      module.init(document, Lab.Projects);
      mount.dataset[readyMarker] =
        String(module.VERSION || minimumVersion);
      mount.dataset.scCivilDirectLoader = 'ready';
      return true;
    } catch (error) {
      mount.dataset.scCivilDirectLoader = 'error';
      console.error(
        '[Sustainable Catalyst Lab] Civil direct loader failed.',
        error
      );
      return false;
    }
  }

  function repairSourceUrl() {
    if (!loaderElement || !loaderElement.src) {
      return null;
    }

    const url = new URL(loaderElement.src, window.location.href);
    url.pathname = url.pathname.replace(
      /civil-infrastructure-direct-loader-v0200\.js$/,
      'civil-infrastructure-lab-v0150.js'
    );
    url.search = '?ver=0.20.0-civil-direct.1';

    return url.href;
  }

  function loadAuthoritativeModule() {
    if (initialize()) {
      return;
    }

    const source = repairSourceUrl();

    if (!source) {
      return;
    }

    const existing = Array.from(document.scripts).find(
      (script) => script.src.includes(
        'civil-infrastructure-lab-v0150.js'
      )
    );

    if (existing) {
      existing.addEventListener('load', initialize, {
        once: true,
      });

      window.setTimeout(initialize, 0);
      window.setTimeout(initialize, 120);
      return;
    }

    const script = document.createElement('script');
    script.src = source;
    script.async = false;
    script.dataset.scCivilAuthoritative = '0.20.0';
    script.addEventListener('load', initialize, {
      once: true,
    });
    script.addEventListener('error', () => {
      const mount = document.querySelector(
        '[data-civil-infrastructure-root]'
      );

      if (mount) {
        mount.dataset.scCivilDirectLoader = 'load-error';
      }

      console.error(
        '[Sustainable Catalyst Lab] Repaired Civil module '
        + 'could not be loaded.',
        source
      );
    });

    document.head.appendChild(script);
  }

  function schedule() {
    loadAuthoritativeModule();
    window.setTimeout(loadAuthoritativeModule, 0);
    window.setTimeout(loadAuthoritativeModule, 150);
  }

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      schedule,
      { once: true }
    );
  } else {
    schedule();
  }

  document.addEventListener(
    'sc-lab:module-opened',
    schedule
  );

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest(
      '[data-lab-target="civil-infrastructure"],'
      + '[data-module-target="civil-infrastructure"],'
      + '[href*="civil-infrastructure"]'
    );

    if (trigger) {
      window.setTimeout(schedule, 0);
    }
  });

  Lab.CivilDirectLoader = {
    VERSION: '0.20.0-civil-direct.1',
    init: schedule,
  };
})();
