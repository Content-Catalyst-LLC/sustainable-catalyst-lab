(() => {
  'use strict';

  const Lab = window.SCLab = window.SCLab || {};
  const STATE = 'scEngineeringInterfaceRepair';

  const definitions = [
    {
      name: 'electrical-embedded',
      selector: '[data-electrical-embedded-root]',
      resolve: () => Lab.ElectricalEmbedded,
      minimumVersion: null,
      force: false,
    },
    {
      name: 'mechanical-thermal',
      selector: '[data-mechanical-thermal-root]',
      resolve: () => Lab.MechanicalThermalLab,
      minimumVersion: null,
      force: false,
    },
    {
      name: 'civil-infrastructure',
      selector: '[data-civil-infrastructure-root]',
      resolve: () => Lab.CivilInfrastructureLab,
      minimumVersion: '0.15.0',
      force: true,
    },
  ];

  function versionParts(version) {
    return String(version || '')
      .split('.')
      .map((part) => Number.parseInt(part, 10) || 0);
  }

  function versionAtLeast(actual, required) {
    if (!required) {
      return true;
    }

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

  function initialize(definition) {
    const mounts = Array.from(
      document.querySelectorAll(definition.selector)
    );

    if (!mounts.length) {
      return;
    }

    const module = definition.resolve();

    if (!module || typeof module.init !== 'function') {
      return;
    }

    if (!versionAtLeast(module.VERSION, definition.minimumVersion)) {
      return;
    }

    mounts.forEach((mount) => {
      if (mount.dataset[STATE] === 'ready') {
        return;
      }

      if (definition.force) {
        mount.replaceChildren();
      } else if (mount.children.length > 0) {
        mount.dataset[STATE] = 'ready';
        return;
      }

      try {
        module.init(document, Lab.Projects);
        mount.dataset[STATE] = 'ready';
        mount.dataset.scEngineeringModule =
          definition.name;
        mount.dataset.scEngineeringVersion =
          String(module.VERSION || 'unknown');
      } catch (error) {
        mount.dataset[STATE] = 'error';
        console.error(
          `[Sustainable Catalyst Lab] ${definition.name} initialization failed.`,
          error
        );
      }
    });
  }

  function initializeAll() {
    definitions.forEach(initialize);
  }

  function initializeAfterLayout() {
    initializeAll();

    window.setTimeout(initializeAll, 0);
    window.setTimeout(initializeAll, 120);
  }

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      initializeAfterLayout,
      { once: true }
    );
  } else {
    initializeAfterLayout();
  }

  document.addEventListener(
    'sc-lab:module-opened',
    initializeAfterLayout
  );

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest(
      '[data-lab-target], [data-module-target], '
      + '[href*="electrical-embedded"], '
      + '[href*="mechanical-thermal"], '
      + '[href*="civil-infrastructure"]'
    );

    if (trigger) {
      window.setTimeout(initializeAfterLayout, 0);
    }
  });

  Lab.EngineeringInterfaceRepair = {
    VERSION: '0.20.0-repair.1',
    init: initializeAfterLayout,
    definitions,
  };
})();
