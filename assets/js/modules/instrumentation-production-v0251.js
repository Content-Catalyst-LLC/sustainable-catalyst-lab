(() => {
  'use strict';

  const W = typeof window !== 'undefined' ? window : globalThis;
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.25.1';
  const ENGINE_VERSION = '0.25.0';
  const MODULE_ID = 'laboratory-data-instrumentation';
  const ROOT_SELECTOR = '[data-laboratory-instrumentation-root]';
  const PANEL_SELECTOR = [
    `[data-lab-module="${MODULE_ID}"]`,
    `[data-module-panel="${MODULE_ID}"]`,
  ].join(',');
  const NAV_SELECTOR = [
    `[data-lab-target="${MODULE_ID}"]`,
    `[data-module-target="${MODULE_ID}"]`,
    `[data-lab-module-button="${MODULE_ID}"]`,
    `[href="#${MODULE_ID}"]`,
  ].join(',');

  const state = {
    attempts: 0,
    repairs: 0,
    duplicateRootsRemoved: 0,
    staleMarkersCleared: 0,
    lastReason: null,
    lastError: null,
    initializedAt: null,
    lastRepairAt: null,
    observerActive: false,
  };

  let observer = null;
  let repairTimer = null;

  function core() {
    const candidate = Lab.LaboratoryDataInstrumentation;

    if (
      candidate
      && candidate.VERSION === ENGINE_VERSION
      && typeof candidate.init === 'function'
      && typeof candidate.status === 'function'
      && candidate.catalog
      && Array.isArray(candidate.catalog.methods)
      && Array.isArray(candidate.catalog.benchmarks)
      && Array.isArray(candidate.catalog.categories)
      && Array.isArray(candidate.catalog.recordTypes)
      && Array.isArray(candidate.catalog.connectionProfiles)
      && Array.isArray(candidate.catalog.qualityFlags)
      && typeof candidate.render === 'function'
    ) {
      return candidate;
    }

    return null;
  }

  function panels() {
    if (typeof document === 'undefined') {
      return [];
    }

    return Array.from(
      document.querySelectorAll(PANEL_SELECTOR)
    );
  }

  function roots() {
    if (typeof document === 'undefined') {
      return [];
    }

    return Array.from(
      document.querySelectorAll(ROOT_SELECTOR)
    );
  }

  function panelScore(panel) {
    let score = 0;

    if (
      panel.getAttribute('data-lab-module')
        === MODULE_ID
    ) {
      score += 8;
    }

    if (
      panel.getAttribute('data-module-panel')
        === MODULE_ID
    ) {
      score += 8;
    }

    if (panel.querySelector(ROOT_SELECTOR)) {
      score += 5;
    }

    if (panel.closest('main')) {
      score += 2;
    }

    if (!panel.hidden) {
      score += 1;
    }

    return score;
  }

  function canonicalPanel() {
    const candidates = panels();

    if (!candidates.length) {
      const existingRoot = roots()[0];

      if (existingRoot) {
        return existingRoot.closest(
          'section, article, main, div'
        );
      }

      if (typeof document === 'undefined') {
        return null;
      }

      const host = document.querySelector(
        'main, [role="main"], .site-main, #primary'
      );

      if (!host) {
        return null;
      }

      const panel = document.createElement('section');
      panel.className = 'sc-lab-panel sc-lab-module';
      panel.setAttribute('data-lab-module', MODULE_ID);
      panel.setAttribute('data-module-panel', MODULE_ID);
      panel.hidden = true;
      panel.innerHTML = [
        '<header class="sc-lab-module-header">',
        '<p class="sc-lab-kicker">LAB/DATA/INSTRUMENTATION</p>',
        '<h3>Laboratory data and instrumentation</h3>',
        '<p>Instrument, sensor, sample, calibration, measurement, maintenance, run, and custody records.</p>',
        '</header>',
        '<div data-laboratory-instrumentation-root></div>',
      ].join('');
      host.appendChild(panel);
      return panel;
    }

    return candidates
      .map((panel) => ({
        panel,
        score: panelScore(panel),
      }))
      .sort((a, b) => b.score - a.score)[0].panel;
  }

  function normalizePanel(panel) {
    if (!panel) {
      return false;
    }

    let changed = false;

    if (
      panel.getAttribute('data-lab-module')
        !== MODULE_ID
    ) {
      panel.setAttribute(
        'data-lab-module',
        MODULE_ID
      );
      changed = true;
    }

    if (
      panel.getAttribute('data-module-panel')
        !== MODULE_ID
    ) {
      panel.setAttribute(
        'data-module-panel',
        MODULE_ID
      );
      changed = true;
    }

    if (!panel.classList.contains('sc-lab-panel')) {
      panel.classList.add('sc-lab-panel');
      changed = true;
    }

    if (!panel.classList.contains('sc-lab-module')) {
      panel.classList.add('sc-lab-module');
      changed = true;
    }

    return changed;
  }

  function chooseCanonicalRoot(panel) {
    const allRoots = roots();

    let root = (
      panel
        ? allRoots.find(
            (candidate) => candidate.closest(PANEL_SELECTOR)
              === panel
          )
        : null
    );

    if (!root) {
      root = allRoots.find(
        (candidate) => (
          candidate.querySelector('.sc-inst-shell')
        )
      ) || allRoots[0] || null;
    }

    if (!root && panel) {
      root = document.createElement('div');
      root.setAttribute(
        'data-laboratory-instrumentation-root',
        ''
      );
      panel.appendChild(root);
    }

    if (!root) {
      return null;
    }

    if (
      panel
      && root.parentElement !== panel
      && !panel.contains(root)
    ) {
      panel.appendChild(root);
    }

    for (const duplicate of allRoots) {
      if (duplicate === root) {
        continue;
      }

      const duplicateRendered = Boolean(
        duplicate.querySelector('.sc-inst-shell')
      );
      const rootRendered = Boolean(
        root.querySelector('.sc-inst-shell')
      );

      if (duplicateRendered && !rootRendered) {
        root.replaceWith(duplicate);
        root = duplicate;
      } else {
        duplicate.remove();
      }

      state.duplicateRootsRemoved += 1;
    }

    return root;
  }

  function clearStaleRoot(root) {
    if (!root) {
      return false;
    }

    const hasShell = Boolean(
      root.querySelector('.sc-inst-shell')
    );
    const marker = root.dataset.scInstrumentationVersion || '';

    if (hasShell && marker === ENGINE_VERSION) {
      return false;
    }

    if (
      marker
      && (
        !hasShell
        || marker !== ENGINE_VERSION
      )
    ) {
      delete root.dataset.scInstrumentationVersion;
      state.staleMarkersCleared += 1;
    }

    if (
      root.children.length
      && !hasShell
    ) {
      root.replaceChildren();
      state.staleMarkersCleared += 1;
    }

    return true;
  }

  function revealPanel(panel) {
    if (!panel) {
      return false;
    }

    panel.hidden = false;
    panel.removeAttribute('hidden');
    panel.setAttribute('aria-hidden', 'false');
    panel.classList.add('is-active');
    panel.classList.add('sc-lab-panel-active');

    for (const other of panels()) {
      if (other === panel) {
        continue;
      }

      if (
        other.classList.contains('is-active')
        || other.classList.contains(
          'sc-lab-panel-active'
        )
      ) {
        other.classList.remove('is-active');
        other.classList.remove(
          'sc-lab-panel-active'
        );
      }
    }

    return true;
  }

  function rendered(root) {
    return Boolean(
      root?.querySelector('.sc-inst-shell')
    );
  }

  function repair(reason = 'manual') {
    state.attempts += 1;
    state.lastReason = reason;

    if (typeof document === 'undefined') {
      state.lastError = 'Document unavailable.';
      return false;
    }

    const engine = core();

    if (!engine) {
      state.lastError =
        'Instrumentation v0.25.0 engine unavailable.';
      return false;
    }

    try {
      const panel = canonicalPanel();

      if (!panel) {
        state.lastError =
          'Instrumentation panel unavailable.';
        return false;
      }

      normalizePanel(panel);
      const root = chooseCanonicalRoot(panel);

      if (!root) {
        state.lastError =
          'Instrumentation root unavailable.';
        return false;
      }

      clearStaleRoot(root);

      if (!rendered(root)) {
        engine.render();
      }

      if (!rendered(root)) {
        delete root.dataset.scInstrumentationVersion;
        root.replaceChildren();
        engine.render();
      }

      if (!rendered(root)) {
        state.lastError =
          'Instrumentation interface did not render.';
        return false;
      }

      root.dataset.scInstrumentationProductionVersion = VERSION;
      panel.dataset.scInstrumentationProductionVersion = VERSION;
      state.repairs += 1;
      state.lastRepairAt = new Date().toISOString();

      if (!state.initializedAt) {
        state.initializedAt = state.lastRepairAt;
      }

      state.lastError = null;
      return true;
    } catch (error) {
      state.lastError = String(
        error && error.message
          ? error.message
          : error
      );
      return false;
    }
  }

  function scheduleRepair(
    reason = 'scheduled',
    delays = [0, 80, 220, 600, 1400, 3000]
  ) {
    for (const delay of delays) {
      W.setTimeout(
        () => repair(`${reason}:${delay}`),
        delay
      );
    }
  }

  function open() {
    const panel = canonicalPanel();

    if (!panel) {
      scheduleRepair('open-missing-panel');
      return false;
    }

    revealPanel(panel);
    repair('open');

    try {
      panel.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    } catch (_error) {
      // Scrolling is optional.
    }

    return true;
  }

  function health() {
    const engine = core();
    const panel = canonicalPanel();
    const allRoots = roots();
    const root = (
      panel?.querySelector(ROOT_SELECTOR)
      || allRoots[0]
      || null
    );
    const engineStatus = engine
      ? engine.status()
      : null;

    return {
      ok: Boolean(
        engine
        && panel
        && root
        && rendered(root)
        && allRoots.length === 1
      ),
      status: (
        engine
        && panel
        && root
        && rendered(root)
        && allRoots.length === 1
      ) ? 'ready' : 'repair-required',
      release: VERSION,
      engineRelease: engine?.VERSION || null,
      methodCount:
        engine?.catalog?.methods?.length || 0,
      benchmarkCount:
        engine?.catalog?.benchmarks?.length || 0,
      categoryCount:
        engine?.catalog?.categories?.length || 0,
      recordTypeCount:
        engine?.catalog?.recordTypes?.length || 0,
      connectionProfileCount:
        engine?.catalog?.connectionProfiles?.length || 0,
      qualityFlagCount:
        engine?.catalog?.qualityFlags?.length || 0,
      panelFound: Boolean(panel),
      panelOpen: Boolean(
        panel
        && !panel.hidden
        && !panel.hasAttribute('hidden')
      ),
      rootCount: allRoots.length,
      renderedRootCount: allRoots.filter(
        (candidate) => rendered(candidate)
      ).length,
      productionMarker:
        root?.dataset.scInstrumentationProductionVersion || null,
      engineStatus,
      attempts: state.attempts,
      repairs: state.repairs,
      duplicateRootsRemoved:
        state.duplicateRootsRemoved,
      staleMarkersCleared:
        state.staleMarkersCleared,
      lastReason: state.lastReason,
      lastError: state.lastError,
      initializedAt: state.initializedAt,
      lastRepairAt: state.lastRepairAt,
      observerActive: state.observerActive,
      contractReady: Boolean(
        engine
        && engine?.catalog?.methods?.length === 48
        && engine?.catalog?.benchmarks?.length === 48
        && engine?.catalog?.categories?.length === 8
        && engine?.catalog?.recordTypes?.length === 9
        && engine?.catalog?.connectionProfiles?.length === 8
        && engine?.catalog?.qualityFlags?.length === 8
      ),
    };
  }

  function status() {
    return health();
  }

  function mutationNeedsRepair(mutations) {
    return mutations.some((mutation) => {
      if (mutation.type === 'attributes') {
        const target = mutation.target;

        return (
          target?.matches?.(PANEL_SELECTOR)
          || target?.matches?.(ROOT_SELECTOR)
        );
      }

      return Array.from(
        mutation.addedNodes || []
      ).some((node) => (
        node.nodeType === 1
        && (
          node.matches?.(PANEL_SELECTOR)
          || node.matches?.(ROOT_SELECTOR)
          || node.querySelector?.(PANEL_SELECTOR)
          || node.querySelector?.(ROOT_SELECTOR)
        )
      ));
    });
  }

  function observe() {
    if (
      observer
      || typeof MutationObserver === 'undefined'
      || typeof document === 'undefined'
    ) {
      return;
    }

    observer = new MutationObserver((mutations) => {
      if (!mutationNeedsRepair(mutations)) {
        return;
      }

      if (repairTimer) {
        W.clearTimeout(repairTimer);
      }

      repairTimer = W.setTimeout(
        () => repair('mutation'),
        40
      );
    });

    observer.observe(
      document.documentElement,
      {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: [
          'hidden',
          'class',
          'data-lab-module',
          'data-module-panel',
          'data-laboratory-instrumentation-root',
          'data-sc-instrumentation-version',
        ],
      }
    );

    state.observerActive = true;
  }

  function navigationClick(event) {
    const target = event.target?.closest?.(
      NAV_SELECTOR
    );

    if (!target) {
      return;
    }

    scheduleRepair('navigation-click');
  }

  function start() {
    scheduleRepair('startup');
    observe();

    document.addEventListener(
      'sc-lab:module-opened',
      (event) => {
        if (
          !event.detail
          || !event.detail.moduleId
          || event.detail.moduleId === MODULE_ID
        ) {
          scheduleRepair('module-opened');
        }
      }
    );

    document.addEventListener(
      'click',
      navigationClick,
      true
    );

    W.addEventListener(
      'pageshow',
      () => scheduleRepair('pageshow')
    );

    W.addEventListener(
      'focus',
      () => scheduleRepair('window-focus')
    );

    W.addEventListener(
      'popstate',
      () => scheduleRepair('popstate')
    );

    document.addEventListener(
      'visibilitychange',
      () => {
        if (!document.hidden) {
          scheduleRepair('visibility-restored');
        }
      }
    );

    W.addEventListener(
      'online',
      () => scheduleRepair('online')
    );

    W.addEventListener(
      'resize',
      () => scheduleRepair('resize', [80, 260])
    );

    W.addEventListener(
      'orientationchange',
      () => scheduleRepair('orientationchange', [100, 400])
    );

    W.addEventListener(
      'hashchange',
      () => {
        if (
          W.location?.hash
          && W.location.hash.includes(MODULE_ID)
        ) {
          open();
        } else {
          scheduleRepair('hashchange');
        }
      }
    );
  }

  Lab.InstrumentationProduction = {
    VERSION,
    ENGINE_VERSION,
    repair,
    open,
    health,
    status,
    scheduleRepair,
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
