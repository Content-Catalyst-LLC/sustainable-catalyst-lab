(() => {
  'use strict';

  const Lab = window.SCLab = window.SCLab || {};
  const VERSION = '0.20.0-civil-runtime.1';
  const MINIMUM_MODULE_VERSION = '0.15.0';
  const selector = '[data-civil-infrastructure-root]';

  let initializing = false;
  let initializedVersion = null;
  let observer = null;

  function versionParts(version) {
    return String(version || '')
      .split('.')
      .map((part) => Number.parseInt(part, 10) || 0);
  }

  function versionAtLeast(actual, required) {
    const left = versionParts(actual);
    const right = versionParts(required);
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

  function mounts() {
    return Array.from(document.querySelectorAll(selector));
  }

  function moduleReady() {
    const module = Lab.CivilInfrastructureLab;

    if (
      !module
      || typeof module.init !== 'function'
      || !versionAtLeast(
        module.VERSION,
        MINIMUM_MODULE_VERSION
      )
    ) {
      return null;
    }

    return module;
  }

  function status() {
    const module = moduleReady();
    const civilMounts = mounts();

    return {
      runtimeVersion: VERSION,
      moduleVersion: module
        ? String(module.VERSION || '')
        : null,
      mountCount: civilMounts.length,
      renderedMounts: civilMounts.filter(
        (mount) => mount.children.length > 0
      ).length,
      initializedVersion,
      scripts: Array.from(document.scripts)
        .map((script) => script.src)
        .filter(
          (source) => source.includes(
            'civil-infrastructure'
          )
        ),
    };
  }

  function initialize() {
    if (initializing) {
      return false;
    }

    const module = moduleReady();
    const civilMounts = mounts();

    if (!module || !civilMounts.length) {
      return false;
    }

    const moduleVersion = String(
      module.VERSION || MINIMUM_MODULE_VERSION
    );

    if (
      initializedVersion === moduleVersion
      && civilMounts.every(
        (mount) => mount.children.length > 0
      )
    ) {
      return true;
    }

    initializing = true;

    try {
      civilMounts.forEach((mount) => {
        mount.replaceChildren();
        mount.dataset.scCivilRuntime = 'initializing';
      });

      module.init(document, Lab.Projects);

      civilMounts.forEach((mount) => {
        mount.dataset.scCivilRuntime =
          mount.children.length > 0
            ? 'ready'
            : 'empty';
        mount.dataset.scCivilRuntimeVersion = VERSION;
        mount.dataset.scCivilModuleVersion = moduleVersion;
      });

      initializedVersion = moduleVersion;

      return civilMounts.some(
        (mount) => mount.children.length > 0
      );
    } catch (error) {
      civilMounts.forEach((mount) => {
        mount.dataset.scCivilRuntime = 'error';
      });

      console.error(
        '[Sustainable Catalyst Lab] '
        + 'Civil runtime initialization failed.',
        error
      );

      return false;
    } finally {
      initializing = false;
    }
  }

  function schedule() {
    initialize();
    window.requestAnimationFrame(initialize);
    window.setTimeout(initialize, 80);
    window.setTimeout(initialize, 250);
  }

  function observe() {
    if (observer || !document.documentElement) {
      return;
    }

    observer = new MutationObserver((mutations) => {
      const relevant = mutations.some((mutation) => {
        if (mutation.type === 'attributes') {
          return (
            mutation.target.matches
            && (
              mutation.target.matches(selector)
              || mutation.target.matches(
                '[data-lab-module="civil-infrastructure"],'
                + '[data-module-panel="civil-infrastructure"]'
              )
            )
          );
        }

        return Array.from(mutation.addedNodes).some(
          (node) => (
            node.nodeType === Node.ELEMENT_NODE
            && (
              node.matches?.(selector)
              || node.querySelector?.(selector)
            )
          )
        );
      });

      if (relevant) {
        schedule();
      }
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: [
        'hidden',
        'class',
        'style',
        'aria-hidden',
      ],
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      () => {
        observe();
        schedule();
      },
      { once: true }
    );
  } else {
    observe();
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

  Lab.CivilRuntime = {
    VERSION,
    init: schedule,
    status,
  };
})();
