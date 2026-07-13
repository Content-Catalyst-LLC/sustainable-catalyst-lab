(() => {
  'use strict';

  const rootWindow = typeof window !== 'undefined'
    ? window
    : globalThis;
  const Lab = rootWindow.SCLab = rootWindow.SCLab || {};
  const CONFIG =
    rootWindow.SCLabBiochemistryProductionConfig || {};
  const VERSION = '0.21.1';
  const MODULE_ID = 'biochemistry-molecular-analysis';
  const PANEL_SELECTOR = [
    `[data-lab-module="${MODULE_ID}"]`,
    `[data-module-panel="${MODULE_ID}"]`,
  ].join(',');
  const MOUNT_SELECTOR =
    '[data-biochemistry-molecular-analysis-root]';
  const RETRY_DELAYS = [0, 40, 120, 300, 700, 1400];

  const state = {
    attempts: 0,
    initializedAt: null,
    lastReason: null,
    lastError: null,
    lastHealth: null,
    observerActive: false,
  };

  function panel() {
    return document.querySelector(PANEL_SELECTOR);
  }

  function ensurePanel() {
    const target = panel();

    if (!target) {
      return null;
    }

    target.classList.add(
      'sc-lab-panel',
      'sc-lab-module'
    );
    target.setAttribute(
      'data-lab-module',
      MODULE_ID
    );
    target.setAttribute(
      'data-module-panel',
      MODULE_ID
    );
    target.dataset.scBiochemistryProduction =
      VERSION;

    return target;
  }

  function ensureMount() {
    const targetPanel = ensurePanel();

    if (!targetPanel) {
      return null;
    }

    let mount = targetPanel.querySelector(
      MOUNT_SELECTOR
    );

    if (!mount) {
      mount = document.createElement('div');
      mount.setAttribute(
        'data-biochemistry-molecular-analysis-root',
        ''
      );
      targetPanel.appendChild(mount);
    }

    return mount;
  }

  function controls(mount) {
    if (!mount) {
      return {
        shell: 0,
        category: 0,
        method: 0,
        inputs: 0,
        run: 0,
        benchmark: 0,
      };
    }

    return {
      shell: mount.querySelectorAll(
        '.sc-bma-shell'
      ).length,
      category: mount.querySelectorAll(
        '[data-bma-category]'
      ).length,
      method: mount.querySelectorAll(
        '[data-bma-method]'
      ).length,
      inputs: mount.querySelectorAll(
        '[data-bma-inputs]'
      ).length,
      run: mount.querySelectorAll(
        '[data-bma-run]'
      ).length,
      benchmark: mount.querySelectorAll(
        '[data-bma-benchmarks]'
      ).length,
    };
  }

  function isRendered(mount) {
    const found = controls(mount);

    return (
      found.shell === 1
      && found.category === 1
      && found.method === 1
      && found.inputs === 1
      && found.run === 1
      && found.benchmark === 1
    );
  }

  function analysisModule() {
    const candidate =
      Lab.BiochemistryMolecularAnalysis;

    if (
      candidate
      && typeof candidate.init === 'function'
      && typeof candidate.runBenchmarks === 'function'
    ) {
      return candidate;
    }

    return null;
  }

  function clearStaleMarker(mount) {
    if (!mount || isRendered(mount)) {
      return false;
    }

    if (
      mount.dataset.scBiochemistryVersion
      || mount.children.length === 0
    ) {
      delete mount.dataset.scBiochemistryVersion;
      delete mount.dataset.scBiochemistryProductionState;

      if (mount.children.length) {
        mount.replaceChildren();
      }

      return true;
    }

    return false;
  }

  function initialize(reason = 'manual', force = false) {
    if (typeof document === 'undefined') {
      return false;
    }

    state.attempts += 1;
    state.lastReason = reason;
    state.lastError = null;

    const mount = ensureMount();
    const moduleApi = analysisModule();

    if (!mount) {
      state.lastError = 'Biochemistry panel not found.';
      return false;
    }

    if (!moduleApi) {
      state.lastError =
        'Biochemistry analysis module is unavailable.';
      mount.dataset.scBiochemistryProductionState =
        'module-unavailable';
      return false;
    }

    if (force || !isRendered(mount)) {
      clearStaleMarker(mount);
    }

    try {
      moduleApi.init(document);
    } catch (error) {
      state.lastError = String(
        error && error.message
          ? error.message
          : error
      );
      mount.dataset.scBiochemistryProductionState =
        'error';
      return false;
    }

    if (!isRendered(mount)) {
      clearStaleMarker(mount);

      try {
        moduleApi.init(mount);
      } catch (error) {
        state.lastError = String(
          error && error.message
            ? error.message
            : error
        );
      }
    }

    const ready = isRendered(mount);

    mount.dataset.scBiochemistryProductionState =
      ready ? 'ready' : 'incomplete';
    mount.dataset.scBiochemistryProductionVersion =
      VERSION;

    if (ready) {
      state.initializedAt = new Date().toISOString();
      state.lastError = null;
    } else if (!state.lastError) {
      state.lastError =
        'Biochemistry controls did not finish rendering.';
    }

    return ready;
  }

  function schedule(reason) {
    RETRY_DELAYS.forEach((delay, index) => {
      rootWindow.setTimeout(
        () => initialize(
          `${reason}:retry-${index + 1}`
        ),
        delay
      );
    });
  }

  function triggerFrom(target) {
    if (!target || !target.closest) {
      return null;
    }

    const explicit = target.closest([
      `[data-module="${MODULE_ID}"]`,
      `[data-lab-module-button="${MODULE_ID}"]`,
      `[data-lab-target="${MODULE_ID}"]`,
      `[data-module-target="${MODULE_ID}"]`,
      `[href*="${MODULE_ID}"]`,
    ].join(','));

    if (explicit) {
      return explicit;
    }

    const candidate = target.closest(
      'button, a, [role="button"], [tabindex]'
    );

    if (!candidate) {
      return null;
    }

    const label = String(
      candidate.textContent
      || candidate.getAttribute('aria-label')
      || ''
    ).trim().toLowerCase();

    return (
      label.includes('biochemistry')
      && label.includes('molecular')
    )
      ? candidate
      : null;
  }

  function open() {
    const targetPanel = ensurePanel();

    if (!targetPanel) {
      return false;
    }

    const trigger = Array.from(
      document.querySelectorAll(
        'button, a, [role="button"], [tabindex]'
      )
    ).find((candidate) => (
      triggerFrom(candidate) === candidate
    ));

    if (trigger && typeof trigger.click === 'function') {
      trigger.click();
    }

    rootWindow.setTimeout(() => {
      if (targetPanel.hidden) {
        const parent = targetPanel.parentElement;

        if (parent) {
          Array.from(parent.children).forEach((sibling) => {
            if (
              sibling !== targetPanel
              && sibling.matches
              && sibling.matches(
                '[data-lab-module], [data-module-panel]'
              )
            ) {
              sibling.hidden = true;
              sibling.setAttribute(
                'aria-hidden',
                'true'
              );
            }
          });
        }

        targetPanel.hidden = false;
        targetPanel.removeAttribute('hidden');
        targetPanel.setAttribute(
          'aria-hidden',
          'false'
        );
      }

      schedule('open');
    }, 80);

    return true;
  }

  function status() {
    const targetPanel = panel();
    const mount = targetPanel
      ? targetPanel.querySelector(MOUNT_SELECTOR)
      : document.querySelector(MOUNT_SELECTOR);

    return {
      productionVersion: VERSION,
      configuredVersion: CONFIG.version || null,
      analysisModuleVersion:
        analysisModule()?.VERSION || null,
      panelFound: Boolean(targetPanel),
      panelHidden: targetPanel
        ? Boolean(targetPanel.hidden)
        : null,
      mountCount: document.querySelectorAll(
        MOUNT_SELECTOR
      ).length,
      renderedMounts: Array.from(
        document.querySelectorAll(MOUNT_SELECTOR)
      ).filter(isRendered).length,
      controls: controls(mount),
      attempts: state.attempts,
      initializedAt: state.initializedAt,
      lastReason: state.lastReason,
      lastError: state.lastError,
      observerActive: state.observerActive,
      health: state.lastHealth,
      scripts: Array.from(document.scripts || [])
        .map((script) => script.src)
        .filter((src) => (
          src.includes('biochemistry')
        )),
    };
  }

  async function health() {
    if (!CONFIG.healthUrl || typeof fetch !== 'function') {
      return null;
    }

    try {
      const response = await fetch(
        CONFIG.healthUrl,
        { credentials: 'same-origin' }
      );
      const payload = await response.json();

      state.lastHealth = {
        ok: response.ok && Boolean(payload.ok),
        status: payload.status || null,
        release: payload.release || null,
        methodCount: payload.methodCount || 0,
        benchmarkCount: payload.benchmarkCount || 0,
      };

      return payload;
    } catch (error) {
      state.lastHealth = {
        ok: false,
        error: String(
          error && error.message
            ? error.message
            : error
        ),
      };

      return state.lastHealth;
    }
  }

  function observe() {
    if (
      typeof MutationObserver === 'undefined'
      || state.observerActive
      || !document.documentElement
    ) {
      return;
    }

    const observer = new MutationObserver(
      (mutations) => {
        const relevant = mutations.some((mutation) => (
          Array.from(mutation.addedNodes || []).some(
            (node) => (
              node.nodeType === 1
              && (
                node.matches?.(PANEL_SELECTOR)
                || node.matches?.(MOUNT_SELECTOR)
                || node.querySelector?.(PANEL_SELECTOR)
                || node.querySelector?.(MOUNT_SELECTOR)
              )
            )
          )
        ));

        if (relevant) {
          schedule('mutation');
        }
      }
    );

    observer.observe(
      document.documentElement,
      {
        childList: true,
        subtree: true,
      }
    );

    state.observerActive = true;
  }

  function start() {
    schedule('startup');
    observe();
    health();

    document.addEventListener(
      'sc-lab:module-opened',
      (event) => {
        const detail = event?.detail || {};
        const id = detail.module
          || detail.moduleId
          || detail.id
          || '';

        if (!id || id === MODULE_ID) {
          schedule('module-opened');
        }
      }
    );

    document.addEventListener(
      'click',
      (event) => {
        if (triggerFrom(event.target)) {
          schedule('navigation-click');
        }
      },
      true
    );

    rootWindow.addEventListener?.(
      'pageshow',
      () => schedule('pageshow')
    );
  }

  Lab.BiochemistryProduction = {
    VERSION,
    initialize,
    repair: () => initialize('repair', true),
    open,
    status,
    health,
  };

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener(
        'DOMContentLoaded',
        start,
        { once: true }
      );
    } else {
      start();
    }
  }
})();
