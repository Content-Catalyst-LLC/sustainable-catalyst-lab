(() => {
  'use strict';

  const W = typeof window !== 'undefined' ? window : globalThis;
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.22.1';
  const ENGINE_VERSION = '0.22.0';
  const MODULE_ID = 'biotechnology-bioprocess-engineering';
  const ROOT_SELECTOR = '[data-biotechnology-bioprocess-root]';
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
    const candidate = Lab.BiotechnologyBioprocessEngineering;

    if (
      candidate
      && candidate.VERSION === ENGINE_VERSION
      && typeof candidate.init === 'function'
      && typeof candidate.status === 'function'
      && Array.isArray(candidate.definitions)
      && Array.isArray(candidate.benchmarks)
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

      return null;
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
          candidate.querySelector('.sc-bpe-shell')
        )
      ) || allRoots[0] || null;
    }

    if (!root && panel) {
      root = document.createElement('div');
      root.setAttribute(
        'data-biotechnology-bioprocess-root',
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
        duplicate.querySelector('.sc-bpe-shell')
      );
      const rootRendered = Boolean(
        root.querySelector('.sc-bpe-shell')
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
      root.querySelector('.sc-bpe-shell')
    );
    const marker = root.dataset.scBpeVersion || '';

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
      delete root.dataset.scBpeVersion;
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
      root?.querySelector('.sc-bpe-shell')
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
        'Bioprocess v0.22.0 engine unavailable.';
      return false;
    }

    try {
      const panel = canonicalPanel();

      if (!panel) {
        state.lastError =
          'Bioprocess panel unavailable.';
        return false;
      }

      normalizePanel(panel);
      const root = chooseCanonicalRoot(panel);

      if (!root) {
        state.lastError =
          'Bioprocess root unavailable.';
        return false;
      }

      clearStaleRoot(root);

      if (!rendered(root)) {
        engine.init();
      }

      if (!rendered(root)) {
        delete root.dataset.scBpeVersion;
        root.replaceChildren();
        engine.init();
      }

      if (!rendered(root)) {
        state.lastError =
          'Bioprocess interface did not render.';
        return false;
      }

      root.dataset.scBpeProductionVersion = VERSION;
      panel.dataset.scBpeProductionVersion = VERSION;
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
        engine?.definitions?.length || 0,
      benchmarkCount:
        engine?.benchmarks?.length || 0,
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
        root?.dataset.scBpeProductionVersion || null,
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
          'data-biotechnology-bioprocess-root',
          'data-sc-bpe-version',
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

  Lab.BioprocessProduction = {
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
